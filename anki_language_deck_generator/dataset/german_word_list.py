import os
import pandas as pd

from typing import Iterator

from .interface import WordList, WordTypeDF, WordTypeRow


class GermanWordList(WordList):
    pass
    def __init__(self) -> None:
        path =  f'{os.path.dirname(os.path.dirname(__file__))}/asset/german_words.csv'
        self.df: WordTypeDF = pd.read_csv(path)

    def __iter__(self) -> Iterator[WordTypeRow]:
        for _, row in self.df.iterrows():
            yield row
