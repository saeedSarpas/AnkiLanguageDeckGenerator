from abc import ABC, abstractmethod

from typing import TypedDict

from anki_language_deck_generator.anki.interface import AnkiFields, AnkiNote


class AnkiStyle(ABC):
    @abstractmethod
    def get_fields(self) -> 'AnkiFields':
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def get_template(self) -> str:
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def get_css(self) -> str:
        raise Exception("I haven't been implemented yet")


class AnkiTemplate(TypedDict):
    _name: str
    _qfmt: str
    _afmt: str
