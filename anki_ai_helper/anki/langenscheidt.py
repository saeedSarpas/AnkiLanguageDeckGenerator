from tqdm import tqdm
import traceback
import random
import time
import json
import uuid
import os
from pydub import AudioSegment
import pandas as pd

from anki_ai_helper.dataset.langenscheidt_word_list import LangenscheidtWordList
from anki_ai_helper.dataset.interface import NOUN_TYPE, VERB_TYPE
from anki_ai_helper.anki.style.one_sentence_puzzler import (
    OneSentencePuzzlerDataFrame,
    OneSentencePuzzlerStyle,
    OneSentencePuzzlerFields,
    OneSentencePuzzlerNote,
)
from anki_ai_helper.T2S.tts_v2 import TTSV2
from anki_ai_helper.anki.deck import AnkiDeck

from anki_ai_helper.helper import string as str_helper
from anki_ai_helper.helper import english as eng_helper
from anki_ai_helper.helper import german as ger_helper
from anki_ai_helper.helper import io as io_helper


class Langenscheidt:
    def __init__(self, name: str) -> None:
        self.puzzler = OneSentencePuzzlerDataFrame()
        self.word_list = LangenscheidtWordList()
        self.filename = name
        self.puzzler.load_and_append(self.filename)
        self.puzzler.store(self.filename)

    def fill_sentences(self):
        try:
            for row in tqdm(self.word_list, desc="Filling sentences"):
                self.puzzler.upsert(
                    row.word,
                    {
                        "word_trans": row.word_trans,
                        "1_fil": row.sentence,
                        "1_pzl": ger_helper.obscure_closest_word(
                            row.sentence, ger_helper.remove_article(row.word)
                        ),
                        "1_trans": row.sentence_trans,
                    },
                )
        except Exception as e:
            print(f"Error occurred: {e}")
            traceback.print_exc()

        self.puzzler.store(self.filename)

    def fetch_extra_info(self):
        self._fetch_extra_noun_info()
        self._fetch_extra_verb_info()

    def to_voice(self):
        dir_path = io_helper.create_package_directory(self.filename)

        german_columns = [
            "word",
            "expl_1",
            "1_pzl",
            "1_pzl_vce",
            "1_fil",
            "1_fil_vce",
        ]

        def german_additional_texts(row, word_type):
            expl_1_processed = (
                _expl_to_string(row.get("expl_1"), word_type)
                if row.get("expl_1")
                else ""
            )
            return {
                "1_fil": f"{row['word'] + '.' if not expl_1_processed else ''}{expl_1_processed}",
            }

        self._generate_voices("de", dir_path, german_columns, german_additional_texts)

        english_columns = [
            "word",
            "word_trans",
            "1_trans",
            "1_trans_vce",
        ]

        def english_additional_texts(row, _):
            return {
                "1_trans": f"{row['word_trans']}. " if row.get("word_trans") else "",
            }

        self._generate_voices("en", dir_path, english_columns, english_additional_texts)

        self.puzzler.store(self.filename)

    def convert_to_mp3(self):
        try:
            dir_path = io_helper.create_package_directory(self.filename)

            for word in tqdm(self.word_list, desc="Converting to MP3"):
                w = word["word"]

                row = self.puzzler.get_values(
                    key=w,
                    columns=[
                        "1_pzl_vce",
                        "1_fil_vce",
                        "1_trans_vce",
                    ],
                )

                if not row:
                    print(f"Unknown word: {w}")
                    continue

                for vce_filename in filter(None, row.values()):
                    self._convert_single_wav_file_to_mp3(vce_filename, dir_path)

                self.puzzler.store(self.filename)
        except Exception as e:
            print("Something went wrong", e)

    def package_deck(self):
        dir_path = io_helper.create_package_directory(self.filename)
        deck_style = OneSentencePuzzlerStyle()
        deck_fields = OneSentencePuzzlerFields()

        columns = [
            "word",
            "word_trans",
            "1_pzl",
            "1_fil",
            "1_trans",
            "1_pzl_vce",
            "1_fil_vce",
            "1_trans_vce",
            "expl_1",
        ]

        deck_words = self.word_list.to_list()

        deck = AnkiDeck(
            deck_name=f"{self.filename}",
            style=deck_style,
            fields=deck_fields,
        )
        media = []

        for word in tqdm(deck_words, desc="Packaging the Deck"):
            w = word.word
            t = word.type
            row = self.puzzler.get_values(key=w, columns=columns)

            vce_keys = [key for key in columns if key.endswith("_vce") and row.get(key)]
            for vce_key in vce_keys:
                media.append(
                    os.path.join(dir_path, row[vce_key].replace(".wav", ".mp3"))
                )

            note_fields = {key: row.get(key, "") for key in columns}
            note_fields.update(
                {key: f"[sound:{row[key].replace('.wav', '.mp3')}]" for key in vce_keys}
            )
            note_fields["expl_1"] = (
                _expl_to_string(row.get("expl_1"), t) if row.get("expl_1") else ""
            )
            note_fields["expl_2"] = ""

            note = OneSentencePuzzlerNote(note_fields)
            deck.add_note(note)

        _ = deck.save(media)

    def _store_progress(self, index, interval: int = 25):
        if (index + 1) % interval == 0 or index + 1 == len(self.word_list):
            self.puzzler.store(self.filename)

    def _fetch_extra_verb_info(self):
        for word in tqdm(self.word_list, desc="Fetching extra verb info"):
            w = word.word
            t = word.type

            if t != VERB_TYPE.name:
                continue

            row = self.puzzler.get_values(key=w, columns=["expl_1"])

            if (
                row
                and "expl_1" in row
                and row["expl_1"] is not None
                and row["expl_1"].strip() != ""
                and row["expl_1"].strip() != "{}"
            ):
                continue

            if len(w) > 1:
                w_updated = w.replace("sich", "")
                w_updated_split = w_updated.split()
                if (
                    len(w_updated_split) > 1
                    and w_updated_split[-1] in ger_helper.VERB_PREFIXES
                ):
                    w_updated = "".join([w_updated_split[-1], w_updated_split[0]])
            else:
                w_updated = w

            expl_1 = ger_helper.get_conjugation_from_reverso(w_updated)

            self.puzzler.upsert(key_value=w, entries={"expl_1": expl_1})
            self.puzzler.store(self.filename)

            sleep_time = int(random.uniform(1, 5))
            time.sleep(sleep_time)

        self.puzzler.store(self.filename)

    def _fetch_extra_noun_info(self):
        for word in tqdm(self.word_list, desc="Fetching extra noun info"):
            w = word.word
            t = word.type

            if t != NOUN_TYPE.name:
                continue

            row = self.puzzler.get_values(key=w, columns=["expl_1"])

            if row and "expl_1" in row and row["expl_1"]:
                try:
                    extra_info = json.loads(row["expl_1"].strip())
                    if extra_info and "Nominative" in extra_info:
                        continue
                except Exception:
                    pass

            expl_1 = ger_helper.get_declension_info_from_collinsdictionary(w)
            if expl_1:
                self.puzzler.upsert(key_value=w, entries={"expl_1": expl_1})
                self.puzzler.store(self.filename)

                sleep_time = round(random.uniform(0.2, 3), 1)
                time.sleep(sleep_time)

        self.puzzler.store(self.filename)

    def _generate_voices(
        self, language, dir_path, columns, additional_text_callback=None
    ):
        with TTSV2(language, dir_path) as tts:
            for i, word in enumerate(tqdm(self.word_list, desc="Generating voices")):
                w = word.word
                t = word.type

                row = self.puzzler.get_values(
                    key=w,
                    columns=columns,
                )

                filenames = {
                    col: _gen_random_wav_filename(i) for col in columns if "vce" in col
                }
                additional_texts = (
                    additional_text_callback(row, t) if additional_text_callback else {}
                )
                self._handle_single_row_to_voice(
                    row, w, tts, filenames, additional_texts
                )

                self.puzzler.store(self.filename)

    def _handle_single_row_to_voice(self, row, w, tts, filenames, additional_texts={}):
        for key, filename in filenames.items():
            if row.get(key) and (
                row.get(key).endswith(".wav") or row.get(key).endswith(".mp3")
            ):
                continue

            text_key = key.replace("_vce", "")

            if row.get(text_key):
                text = row[text_key]
                if text_key in additional_texts:
                    text = additional_texts[text_key] + text

                _ = tts.shoot(text, filename)
                self.puzzler.upsert(key_value=w, entries={key: filename})

    def _convert_single_wav_file_to_mp3(self, vce_filename, dir_path):
        filepath = os.path.join(dir_path, vce_filename)
        mp3_path = filepath.replace(".wav", ".mp3")

        if os.path.exists(mp3_path):
            return

        try:
            mp3 = AudioSegment.from_wav(filepath)
            mp3.export(mp3_path, format="mp3", bitrate="32k")
        except Exception as e:
            print(f"Error converting {vce_filename} to mp3: {e}")


def _expl_to_string(expl_1_str: str, word_type: str) -> str:
    try:
        if word_type not in ["Noun", "Verb"]:
            return ""

        expl_1 = json.loads(expl_1_str)

        if word_type == "Noun":
            return f"{expl_1['Nominative']['Singular']}, {expl_1['Nominative']['Plural']}. "
        else:
            return f"{expl_1['Indikativ Präsens']['er/sie/es']}, {expl_1['Indikativ Präteritum']['er/sie/es']}, {expl_1['Indikativ Perfekt']['er/sie/es']}. "
    except Exception as e:
        return ""


def _gen_random_wav_filename(i: int) -> str:
    return f"{i:05}-{uuid.uuid4()}.wav"
