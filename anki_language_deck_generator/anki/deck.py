import random
import genanki

from datetime import datetime
from typing import List

from .interface import AnkiStyle, AnkiFields, AnkiNote


class AnkiDeck:
    def __init__(self, deck_name: str, style: AnkiStyle, fields: AnkiFields) -> None:
        self.deck_name = deck_name
        self.style = style
        self.fields = fields
        
        self.model_id = random.randrange(1 << 30, 1 << 31)
        self.deck_id = random.randrange(1 << 30, 1 << 31)

        self.model = genanki.Model(
            self.model_id,
            deck_name,
            fields=fields.to_genanki_fields(),
            templates=style.get_templates(),
            css=style.get_css()
        )

        self.deck = genanki.Deck(self.deck_id, self.deck_name)


    def add_note(self, note: AnkiNote) -> None:
        anki_note = genanki.Note(
            model=self.model,
            fields=note.to_list()
        )

        self.deck.add_note(anki_note)

    def save(self, media: List[str], prefix: str = '.') -> str | None:
        deck = genanki.Package(self.deck)
        deck.media_files = media
        path = f"{prefix}/{self.deck_name}_{datetime.now().strftime('%y%m%d%H%M%S')}.apkg"
        try:
            deck.write_to_file(path)
            return path
        except Exception as e:
            print(f"Unable to save the deck on disk. message: {e}")
            return None
