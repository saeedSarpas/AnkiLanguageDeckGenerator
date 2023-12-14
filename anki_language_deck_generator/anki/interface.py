from abc import ABC, abstractmethod

from typing import TypedDict, List, Dict


class AnkiFields(ABC):
    @abstractmethod
    def to_genanki_fields(self) -> Dict[str, str]:
        raise Exception("I haven't been implemented yet")


class AnkiNote(ABC):
    @abstractmethod
    def __init__(self, note: TypedDict) -> None:
        self.note = note

    @abstractmethod
    def to_list(self) -> List[str]:
        raise Exception("I haven't been implemented yet")
