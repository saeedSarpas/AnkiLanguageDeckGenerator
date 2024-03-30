import os
import zipfile
import pandas as pd
from ankipandas import Collection

from typing import Iterator, List

from .interface import (
    WordList,
    WordType,
    WordListRow,
    NOUN_TYPE,
    VERB_TYPE,
    OTHER_TYPE,
)


class LangenscheidtWordListRow(WordListRow):
    @property
    def word_trans(self) -> str: ...

    @property
    def sentence(self) -> str: ...

    @property
    def sentence_trans(self) -> str: ...


class LangenscheidtWordList(WordList):
    def __init__(self, f: int = 0, t: int = -1) -> None:
        apkg_file = f"{os.path.dirname(os.path.dirname(__file__))}/asset/langenscheidt-2000.apkg"
        extract_folder = "/tmp/langenscheidt"

        with zipfile.ZipFile(apkg_file, "r") as zip_ref:
            zip_ref.extractall(extract_folder)

        collection_file = os.path.join(extract_folder, "collection.anki2")
        col = Collection(collection_file)
        notes = col.notes["nflds"].to_list()

        df_data = {
            "word": [n[0].split(",")[0] for n in notes],
            "word_trans": [n[1] for n in notes],
            "sentence": [n[2] for n in notes],
            "sentence_trans": [n[3] for n in notes],
        }

        self.df = pd.DataFrame(df_data)
        self.df["type"] = self.df.apply(self._assign_type, axis=1)

        if f != 0 or t != -1:
            self.df = self.df[f:t]

    def __iter__(self) -> Iterator[LangenscheidtWordListRow]:
        for _, row in self.df.iterrows():
            yield row

    def __len__(self) -> int:
        return len(self.df)

    def get_types(self) -> List[WordType]:
        return [NOUN_TYPE, VERB_TYPE, OTHER_TYPE]

    def _assign_type(self, row) -> str:
        if row["word_trans"].strip().startswith("to "):
            return VERB_TYPE.name
        elif row["word"].strip()[:3] in ["der", "die", "das"]:
            return NOUN_TYPE.name
        else:
            return OTHER_TYPE.name
