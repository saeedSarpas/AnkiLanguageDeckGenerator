from typing import Protocol

from typing import TypedDict, List, Dict


class AnkiTemplate(TypedDict):
    _name: str
    _qfmt: str
    _afmt: str


class AnkiStyle(Protocol):
    def get_templates(self) -> List[AnkiTemplate]:
        ...

    def get_css(self) -> str:
        ...


class AnkiFields(Protocol):
    def to_genanki_fields(self) -> List[Dict[str, str]]:
        ...


class AnkiNote(Protocol):
    def __init__(self, note: TypedDict) -> None:
        ...

    def to_list(self) -> List[str]:
        ...
