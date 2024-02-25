import os
import pandas as pd

from typing import Iterator, List

from .interface import (
    WordList,
    WordType,
    WordListDF,
    WordListRow,
    NOUN_TYPE,
    VERB_TYPE,
    OTHER_TYPE,
)


class GermanWordList(WordList):
    def __init__(self, f: int = 0, t: int = -1) -> None:
        path = f"{os.path.dirname(os.path.dirname(__file__))}/asset/german_words.csv"
        self.df: WordListDF = pd.read_csv(path)

        if f != 0 or t != -1:
            self.df = self.df[f:t]

    def __iter__(self) -> Iterator[WordListRow]:
        for _, row in self.df.iterrows():
            yield row

    def __len__(self) -> int:
        return len(self.df)

    def get_types(self) -> List[WordType]:
        return [NOUN_TYPE, VERB_TYPE, OTHER_TYPE]
