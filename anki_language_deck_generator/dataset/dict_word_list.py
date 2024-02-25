import pandas as pd

from typing import Iterator, List, Dict

from .interface import (
    WordList,
    WordType,
    WordListDF,
    WordListRow,
    NOUN_TYPE,
    VERB_TYPE,
    OTHER_TYPE,
)


class DictWordList(WordList):
    def __init__(self, entries: Dict) -> None:
        data = {
            "word": entries.keys(),
            "type": entries.values(),
        }
        self.df: WordListDF = pd.DataFrame(data)

    def __iter__(self) -> Iterator[WordListRow]:
        for _, row in self.df.iterrows():
            yield row

    def __len__(self) -> int:
        return len(self.df)

    def get_types(self) -> List[WordType]:
        return [NOUN_TYPE, VERB_TYPE, OTHER_TYPE]
