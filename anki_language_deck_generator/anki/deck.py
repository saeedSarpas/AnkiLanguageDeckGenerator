import random
import genanki

from datetime import datetime
from typing import List

from .interface import AnkiNote, AnkiFields
from .style.interface import AnkiStyle


class AnkiDeck:
    def __init__(self, deck_name: str, style: AnkiStyle) -> None:
        self.deck_name = deck_name
        self.style = style
        
        self.model_id = random.randrange(1 << 30, 1 << 31)
        self.deck_id = random.randrange(1 << 30, 1 << 31)

        self.model = genanki.Model(
            self.model_id,
            deck_name,
            fields=style.get_fields.to_genanki_fields(),
            template=style.get_template,
            css=style.get_css
        )

        self.deck = genanki.Deck(self.deck_id, self.model)


    def add_note(self, note: AnkiNote) -> None:
        anki_note = genanki.Note(
            model=self.model,
            fields=note.to_list()
        )

        self.deck.add_note(anki_note)

    def save(self, media: List[str]):
        deck = genanki.Package(self.deck)
        deck.media_files = media
        deck.write_to_file(f"{self.deck_name}_{datetime.now().strftime('%y%m%d%H%M%S')}.apkg")
