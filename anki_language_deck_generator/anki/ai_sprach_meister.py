import torch
from typing import Dict, Optional
from tqdm import tqdm
import traceback
import random
import time
import json
import uuid
import os
from pydub import AudioSegment
import pandas as pd

from anki_language_deck_generator.LLM.interface import LlmSingleShot
from anki_language_deck_generator.dataset.interface import (
    WordList,
    NOUN_TYPE,
    VERB_TYPE,
)
from anki_language_deck_generator.anki.style.two_sentence_puzzler import (
    TwoSentencePuzzlerDataFrame,
    TwoSentencePuzzlerStyle,
    TwoSentencePuzzlerFields,
    TwoSentencePuzzlerNote,
)
from anki_language_deck_generator.T2S.tts_v2 import TTSV2
from anki_language_deck_generator.anki.deck import AnkiDeck

from anki_language_deck_generator.helper import string as str_helper
from anki_language_deck_generator.helper import english as eng_helper
from anki_language_deck_generator.helper import german as ger_helper
from anki_language_deck_generator.helper import io as io_helper


class AiSprachMeisterPrompt:
    WORD_PLACEHOLDER = "[[word]]"
    TRANSLATION_PLACEHOLDER = "[[trans]]"

    SYSTEM_PROMPT = """
    You are now operating as a highly precise and structured language processing tool for a German to English language learning application. Your primary objectives are:

        Accuracy in Translation and Generation: Provide accurate translations and sentence generations. Precision in language use, grammar, and context is paramount. You must maintain fidelity to the meanings of words and sentences, ensuring that translations and sentence constructions are clear, direct, and correct.

        Strict Adherence to Response Format: All responses must strictly follow the JSON format specified in each prompt. Pay close attention to the keys and structure outlined in the prompts. Any deviation from the specified format is unacceptable and will result in the response being deemed incorrect.

        German Language Specifics: When handling German words, consider the nuances of the language, such as gender-specific articles for nouns, verb conjugations, and the intricacies of syntax. Your responses should reflect a thorough understanding of these aspects.

        Direct and Concise Responses: Provide responses that are directly aligned with the prompt requirements. Avoid unnecessary elaboration or deviation from the prompt. Your responses should be to the point, fulfilling exactly what is asked, nothing more, nothing less.

        Prompt-Based Response: Each of your responses should be directly based on the specific prompt you receive. Carefully analyze the prompt, understand the requirement, and generate a response that precisely fulfills the need outlined in the prompt.

        When generating sentences, please make sure to use simplest German words and sentences.

    Remember, your role is to assist in language learning by providing meticulously accurate and well-structured language content. Consistency, precision, and clarity are your guiding principles.
    """

    PROMPTS = {
        "translation": {
            "word": {
                "Noun": f"Strictly adhering to the JSON format, translate the German noun '{WORD_PLACEHOLDER}' to English. Ensure the response contains 'German' and 'English' keys, with the original and translated words respectively. Example in JSON: {{ \"German\": \"der Hund\", \"English\": \"dog\" }}. Translate '{WORD_PLACEHOLDER}' following this exact JSON structure.",
                "Verb": f"Using JSON format exclusively, translate the German verb '{WORD_PLACEHOLDER}' into English. Include 'German' and 'English' as keys in your response. Example in JSON: {{ \"German\": \"gehen\", \"English\": \"go\" }}. Translate '{WORD_PLACEHOLDER}', maintaining the specified JSON format.",
                "Other": f"In a strict JSON format, translate the German word '{WORD_PLACEHOLDER}' (adjective/adverb/other) to English. The response must have 'German' and 'English' keys. Example in JSON: {{ \"German\": \"schnell\", \"English\": \"fast\" }}. Translate '{WORD_PLACEHOLDER}', keeping the JSON format intact.",
            },
        },
        "generate": {
            "sentence": {
                "descriptive": {
                    "Noun": f"Generate a German sentence starting with 'Das Wort {WORD_PLACEHOLDER} bedeutet', accurately describing the noun '{WORD_PLACEHOLDER}' (English: '{TRANSLATION_PLACEHOLDER}'), and use '{WORD_PLACEHOLDER}' only once in the sentence. Translate it to English. Present both sentences in strict JSON format with 'German' and 'English' keys. Example in JSON: {{ \"German\": \"Das Wort der Hund bedeutet ein Haustier.\", \"English\": \"The word 'Hund' means a pet.\" }}. Create a descriptive sentence for '{WORD_PLACEHOLDER}' following this format. Please use simplest German words and sentneces.",
                    "Verb": f"Create a German sentence beginning with 'Das Verb {WORD_PLACEHOLDER} bedeutet', which precisely explains the verb '{WORD_PLACEHOLDER}' (English: '{TRANSLATION_PLACEHOLDER}'). Include '{WORD_PLACEHOLDER}' just once. Translate this to English. Format your response in JSON with 'German' and 'English' keys. Example in JSON: {{ \"German\": \"Das Verb gehen bedeutet, sich zu Fuß von einem Ort zum anderen zu bewegen.\", \"English\": \"The verb 'gehen' means to move from one place to another on foot.\" }}. Proceed with '{WORD_PLACEHOLDER}' in this format. Please use simplest German words and sentneces.",
                    "Other": f"Construct a German sentence starting with 'Das Wort {WORD_PLACEHOLDER} bedeutet', which clearly defines the word '{WORD_PLACEHOLDER}' (English: '{TRANSLATION_PLACEHOLDER}'). Use '{WORD_PLACEHOLDER}' only once. Translate it and provide both sentences in JSON format, using 'German' and 'English' keys. Example in JSON: {{ \"German\": \"Das Wort schnell bedeutet eine hohe Geschwindigkeit bei einer Bewegung oder Aktion.\", \"English\": \"The word 'schnell' means a high speed in movement or action.\" }}. Follow this format for '{WORD_PLACEHOLDER}'. Please use simplest German words and sentneces.",
                },
                "example": {
                    "Noun": f"Generate a German sentence using the noun '{WORD_PLACEHOLDER}' (English: '{TRANSLATION_PLACEHOLDER}') exactly once, demonstrating its use as a noun in a conversational context. Translate it to English. Format both sentences in JSON with 'German' and 'English' keys, ensuring that '{WORD_PLACEHOLDER}' is used correctly as a noun. Example in JSON: {{ \"German\": \"Der {WORD_PLACEHOLDER} steht auf dem Tisch.\", \"English\": \"The {TRANSLATION_PLACEHOLDER} is on the table.\" }}. Create a sentence for '{WORD_PLACEHOLDER}' adhering to this format. Please use simplest German words and sentneces.",
                    "Verb": f"Compose a German sentence featuring the verb '{WORD_PLACEHOLDER}' (English: '{TRANSLATION_PLACEHOLDER}') just once, illustrating its use as a verb in a daily conversation. Translate this sentence into English. Your response should be in JSON format with 'German' and 'English' keys, ensuring that '{WORD_PLACEHOLDER}' is correctly used as a verb. Example in JSON: {{ \"German\": \"Ich {WORD_PLACEHOLDER} zum Geschäft.\", \"English\": \"I {TRANSLATION_PLACEHOLDER} to the store.\" }}. Proceed with '{WORD_PLACEHOLDER}', maintaining this format. Please use simplest German words and sentneces.",
                    "Other": f"Create a German sentence that includes the word '{WORD_PLACEHOLDER}' (English: '{TRANSLATION_PLACEHOLDER}') only once, as it might be used in everyday speech. Translate it to English. Ensure the response is in a structured JSON format with 'German' and 'English' keys. Example in JSON: {{ \"German\": \"Das Buch ist {WORD_PLACEHOLDER}.\", \"English\": \"The book is {TRANSLATION_PLACEHOLDER}.\" }}. Generate a sentence for '{WORD_PLACEHOLDER}', following the JSON format. Please use simplest German words and sentneces.",
                },
            },
        },
    }

    def __init__(self) -> None:
        pass

    def translate(
        self, model: LlmSingleShot, word: str, word_type: str
    ) -> Optional[Dict]:
        if word_type in self.PROMPTS["translation"]["word"]:
            prompt = self.PROMPTS["translation"]["word"][word_type]
            response = (
                self._prompt_to_json(model, prompt, word, None) if prompt else None
            )

            return str_helper.find_and_parse_json(response, ["German", "English"])

        return None

    def describe(
        self, model: LlmSingleShot, word: str, word_type: str, translation: str
    ) -> Optional[Dict]:
        if word_type in self.PROMPTS["generate"]["sentence"]["descriptive"]:
            prompt = self.PROMPTS["generate"]["sentence"]["descriptive"][word_type]
            response = (
                self._prompt_to_json(model, prompt, word, translation)
                if prompt
                else None
            )

            return str_helper.find_and_parse_json(response, ["German", "English"])

        return None

    def example(
        self, model: LlmSingleShot, word: str, word_type: str, translation: str
    ) -> Optional[Dict]:
        if word_type in self.PROMPTS["generate"]["sentence"]["example"]:
            prompt = self.PROMPTS["generate"]["sentence"]["example"][word_type]
            response = (
                self._prompt_to_json(model, prompt, word, translation)
                if prompt
                else None
            )

            return str_helper.find_and_parse_json(response, ["German", "English"])

        return None

    def _prompt_to_json(
        self, model: LlmSingleShot, prompt_raw: str, word: str, translation: str
    ) -> str:
        prompt = self._prepare_prompt(prompt_raw, word, translation)
        return model.shoot(prompt)

    def _prepare_prompt(self, prompt_raw: str, word: str, translation: str) -> str:
        prompt = prompt_raw.replace(self.WORD_PLACEHOLDER, word)
        return (
            prompt.replace(self.TRANSLATION_PLACEHOLDER, translation)
            if translation
            else prompt
        )


class AiSprachMeister:
    def __init__(self, model: LlmSingleShot, word_list: WordList, name: str) -> None:
        self.word_list = word_list
        self.puzzler = TwoSentencePuzzlerDataFrame()
        self.model = model
        self.prompt = AiSprachMeisterPrompt()

        self.filename = name
        self.puzzler.load_and_append(self.filename)
        self.puzzler.store(self.filename)

    def generate_sentences(self, force: bool = False):
        with torch.cuda.amp.autocast(dtype=torch.bfloat16), self.model(
            self.prompt.SYSTEM_PROMPT
        ) as self.llm:
            try:
                for i, word in enumerate(tqdm(self.word_list)):
                    processed_word = (
                        self._generate_descriptive_and_example_senteces_for_word(
                            word, force
                        )
                    )
                    if processed_word:
                        try:
                            self.puzzler.upsert(
                                processed_word["word"], processed_word["entries"]
                            )
                        except Exception as e:
                            print(
                                f"Unable to upsert the new entry. word: {processed_word['word']}",
                                e,
                            )
                    self._store_progress(i)
            except Exception as e:
                print(f"Error occurred: {e}")
                traceback.print_exc()

        self.puzzler.store(self.filename)

    def fetch_extra_info(self):
        self._fetch_extra_noun_info()
        self._fetch_extra_verb_info()

    def to_voice(self, force=False):
        dir_path = io_helper.create_package_directory(self.filename)

        german_columns = [
            "word",
            "expl_1",
            "1_pzl",
            "1_pzl_vce",
            "1_fil",
            "1_fil_vce",
            "2_pzl",
            "2_pzl_vce",
            "2_fil",
            "2_fil_vce",
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

        self._generate_voices(
            "de", dir_path, german_columns, force, german_additional_texts
        )

        english_columns = [
            "word",
            "word_trans",
            "1_trans",
            "1_trans_vce",
            "2_trans",
            "2_trans_vce",
        ]

        def english_additional_texts(row, _):
            return {
                "1_trans": f"{row['word_trans']}. " if row.get("word_trans") else "",
            }

        self._generate_voices(
            "en", dir_path, english_columns, force, english_additional_texts
        )

        self.puzzler.store(self.filename)

    def convert_to_mp3(self):
        dir_path = io_helper.create_package_directory(self.filename)

        for word in tqdm(self.word_list):
            w = word["word"]

            row = self.puzzler.get_values(
                key=w,
                columns=[
                    "1_pzl_vce",
                    "1_fil_vce",
                    "2_pzl_vce",
                    "2_fil_vce",
                    "1_trans_vce",
                    "2_trans_vce",
                ],
            )

            if not row:
                continue

            for vce_filename in filter(None, row.values()):
                self._convert_single_wav_file_to_mp3(vce_filename, dir_path)

            self.puzzler.store(self.filename)

    def package_deck(
        self, cards_per_deck: int, n_decks: int = None, force_all: bool = False
    ):
        dir_path = io_helper.create_package_directory(self.filename)
        deck_style = TwoSentencePuzzlerStyle()
        deck_fields = TwoSentencePuzzlerFields()

        total_words = len(self.word_list)
        n_decks_calc = (
            n_decks
            if n_decks
            else (total_words // cards_per_deck) + bool(total_words % cards_per_deck)
        )

        columns = [
            "word",
            "word_trans",
            "1_pzl",
            "1_fil",
            "1_trans",
            "1_pzl_vce",
            "1_fil_vce",
            "1_trans_vce",
            "2_pzl",
            "2_fil",
            "2_trans",
            "2_pzl_vce",
            "2_fil_vce",
            "2_trans_vce",
            "expl_1",
        ]

        for deck_n in range(1, n_decks_calc + 1):
            l = (deck_n - 1) * cards_per_deck
            u = min(deck_n * cards_per_deck, total_words)
            deck_words = self.word_list.to_list()[l:u]

            deck = AnkiDeck(
                deck_name=f"{self.filename} - {deck_n}",
                style=deck_style,
                fields=deck_fields,
            )
            media = []

            for word in tqdm(deck_words):
                w = word.word
                t = word.type
                row = self.puzzler.get_values(key=w, columns=columns)

                if not force_all and (
                    not row or not all(row.get(key) for key in columns[:-1])
                ):
                    continue

                vce_keys = [
                    key for key in columns if key.endswith("_vce") and row.get(key)
                ]
                for vce_key in vce_keys:
                    media.append(
                        os.path.join(dir_path, row[vce_key].replace(".wav", ".mp3"))
                    )

                note_fields = {key: row.get(key, "") for key in columns}
                note_fields.update(
                    {
                        key: f"[sound:{row[key].replace('.wav', '.mp3')}]"
                        for key in vce_keys
                    }
                )
                note_fields["expl_1"] = (
                    _expl_to_string(row.get("expl_1"), t) if row.get("expl_1") else ""
                )
                note_fields["expl_2"] = ""

                note = TwoSentencePuzzlerNote(note_fields)
                deck.add_note(note)

            _ = deck.save(media)

    def _generate_descriptive_and_example_senteces_for_word(
        self, word: str, force: bool
    ):
        w = word.word
        t = word.type
        if not force and self.puzzler.is_duplicate(w):
            return None

        trans = self.prompt.translate(self.llm, w, t)
        if not trans:
            return None

        w_en = trans["English"]
        descriptive = self.prompt.describe(self.llm, w, t, w_en)
        example = self.prompt.example(self.llm, w, t, w_en)
        if not descriptive or not example:
            return None

        return {
            "word": w,
            "entries": {
                "word_trans": eng_helper.remove_article(w_en),
                "1_fil": descriptive["German"],
                "1_pzl": ger_helper.obscure_closest_word(
                    descriptive["German"], ger_helper.remove_article(w)
                ),
                "1_trans": descriptive["English"],
                "2_fil": example["German"],
                "2_pzl": ger_helper.obscure_closest_word(
                    example["German"], ger_helper.remove_article(w)
                ),
                "2_trans": example["English"],
            },
        }

    def _store_progress(self, index, interval: int = 25):
        if (index + 1) % interval == 0 or index + 1 == len(self.word_list):
            self.puzzler.store(self.filename)

    def _fetch_extra_verb_info(self):
        for word in tqdm(self.word_list):
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
        for word in tqdm(self.word_list):
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
        self, language, dir_path, columns, force, additional_text_callback=None
    ):
        with TTSV2(language, dir_path) as tts:
            for i, word in enumerate(tqdm(self.word_list)):
                w = word.word
                t = word.type

                row = self.puzzler.get_values(
                    key=w,
                    columns=columns,
                )

                voice_needed = any(not row.get(col) for col in columns if "vce" in col)
                if not force and row and not voice_needed:
                    continue

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

    def _handle_single_row_to_voice(
        self, row, w, tts, filenames, additional_texts=None
    ):
        if additional_texts is None:
            additional_texts = {}
        for key, filename in filenames.items():
            text_key = key.split("_")[0]
            if row.get(text_key):
                text = row[text_key]
                if text_key in additional_texts:
                    text = additional_texts[text_key] + text
                if not row.get(filename):
                    _ = tts.shoot(text, filename)
                    self.puzzler.upsert(key_value=w, entries={filename: filename})

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
