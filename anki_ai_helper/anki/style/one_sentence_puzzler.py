from typing import ClassVar, Dict, List

from anki_ai_helper.anki.interface import AnkiTemplate, AnkiNote
from anki_ai_helper.helper.dataframe import GenericDataFrame


class OneSentencePuzzlerDataFrame(GenericDataFrame):
    COLUMNS: ClassVar[Dict[str, type]] = {
        "word": str,  # The German word
        "word_trans": str,  # The English translation of the word
        "1_pzl": str,  # 1st sentence puzzle
        "1_fil": str,  # 1st sentence filled
        "1_trans": str,  # 1st sentence translation
        "1_pzl_vce": str,  # 1st sentence puzzle voice
        "1_fil_vce": str,  # 1st sentence filled voice
        "1_trans_vce": str,  # 1st sentence translation voice
        "expl_1": str,  # Extra explanation
        "expl_2": str,  # Extra explanation
    }

    def __init__(self):
        super().__init__(self.COLUMNS, "word")


class OneSentencePuzzlerFields:
    def __init__(self) -> None:
        self.fields = OneSentencePuzzlerDataFrame.COLUMNS.keys()

    def to_genanki_fields(self) -> List[Dict[str, str]]:
        return [{"name": field} for field in self.fields]


class OneSentencePuzzlerStyle:
    def __init__(self) -> None:
        pass

    def get_fields(self) -> "OneSentencePuzzlerFields":
        fields = OneSentencePuzzlerFields()
        return fields

    def get_templates(self) -> List[AnkiTemplate]:
        return TEMPLATES

    def get_css(self) -> str:
        return CSS


class OneSentencePuzzlerNote:
    def __init__(self, note: AnkiNote):
        self.note = note

    def to_list(self) -> List[str]:
        return list(self.note.values())


TEMPLATES: List[AnkiTemplate] = [
    {
        "name": "One Sentence Puzzler Template",
        "qfmt": """
<div class="card">
  <div id="puzzle-sentences">
    <p id="sentence1">{{1_pzl}}</p>
  </div>
  {{1_pzl_vce}}
</div>
    """,
        "afmt": """
<div class="card">
  <div id="filled-sentences">
    <p>{{1_fil}}</p>
  </div>
  <hr>
  <div class="explanations">
    <p>{{word}} [{{word_trans}}]</p>
    <p>{{expl_1}}</p>
  </div>
  <div class="translations">
    <p>{{1_trans}}</p>
  </div>
  {{1_fil_vce}}
  {{1_trans_vce}}
</div>
""",
    }
]

CSS: str = """
.card {
  font-family: Arial, sans-serif;
  text-align: center;
  color: #333; /* Dark text color for light background */
  background-color: #fff; /* Light background color */
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Adjusted for light theme */
}

p {
  margin: 15px 0;
  line-height: 1.6;
}

hr {
  margin: 20px 0;
  border: none;
  height: 1px;
  background-color: #ccc; /* Adjusted for light theme */
}
"""
