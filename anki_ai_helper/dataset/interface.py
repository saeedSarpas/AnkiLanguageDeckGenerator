from abc import ABC, abstractmethod
from typing import Iterator, List
from typing_extensions import Protocol
import pandas as pd


class WordType:
    def __init__(self, name: str) -> None:
        self.name = name


NOUN_TYPE = WordType("Noun")
VERB_TYPE = WordType("Verb")
OTHER_TYPE = WordType("Other")


class WordListRow(Protocol):
    @property
    def word(self) -> str:
        ...

    @property
    def type(self) -> WordType:
        ...


class WordListDF(Protocol):
    @property
    def word(self) -> pd.Series:
        ...

    @property
    def type(self) -> pd.Series:
        ...


class WordList(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[WordListRow]:
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def get_types(self) -> List[WordType]:
        ...

    def to_list(self) -> List[WordListRow]:
        return [row for _, row in self.df.iterrows()]
