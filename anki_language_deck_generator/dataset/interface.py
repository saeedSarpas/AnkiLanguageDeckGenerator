from abc import ABC, abstractmethod
from typing import Iterator
from typing_extensions import Protocol
import pandas as pd


class WordTypeRow(Protocol):
    @property
    def word(self) -> str: ...
    @property
    def type(self) -> str: ...


class WordTypeDF(Protocol):
    @property
    def word(self) -> pd.Series: ...
    @property
    def type(self) -> pd.Series: ...


class WordList(ABC):
    @abstractmethod
    def __init__(self): ...
    @abstractmethod
    def __iter__(self) -> Iterator[WordTypeRow]: ...
