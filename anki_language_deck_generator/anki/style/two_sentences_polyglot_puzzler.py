from anki_language_deck_generator.anki.interface import (
    AnkiFields,
    AnkiStyle,
    AnkiTemplate,
    AnkiNote,
)
from typing import TypedDict, Dict, List


class TwoSentencesPuzzlerStyle(AnkiStyle):
    def __init__(self) -> None:
        super().__init__()

    def get_fields(self) -> "TwoSentencesPuzzlerFields":
        fields = TwoSentencesPuzzlerFields()
        return fields

    def get_templates(self) -> List[AnkiTemplate]:
        return TEMPLATES

    def get_css(self) -> str:
        return CSS


class TwoSentencesPuzzlerFields(AnkiFields):
    def __init__(self) -> None:
        self.fields = [
            "1_pzl",  # 1st sentence puzzle
            "1_fil",  # 1st sentence filled
            "1_ans",  # 1st sentence answer
            "1_ans_trans",  # 1st sentence answer translation
            "1_trans",  # 1st sentence translation
            "1_pzl_vce",  # 1st sentence puzzle voice
            "1_fil_vce",  # 1st sentence filled voice
            "1_trans_vce",  # 1st sentence translation voice
            "2_pzl",  # 2nd sentence puzzle
            "2_fil",  # 2nd sentence filled
            "2_ans",  # 2nd sentence answer
            "2_ans_trans",  # 2nd sentence answer translation
            "2_trans",  # 2nd sentence translation
            "2_pzl_vce",  # 2nd sentence puzzle voice
            "2_fil_vce",  # 2nd sentence filled voice
            "2_trans_vce",  # 1st sentence translation voice
            "expl_1",  # Extra explanation
            "expl_2",  # Extra explanation
        ]

    def to_genanki_fields(self) -> Dict[str, str]:
        return [{"name": field} for field in self.fields]


class TwoSentencesPuzzlerNoteType(TypedDict):
    _1_pzl: str
    _1_fil: str
    _1_ans: str
    _1_ans_trans: str
    _1_trans: str
    _1_pzl_vce: str
    _1_fil_vce: str
    _1_trans_vce: str
    _2_pzl: str
    _2_fil: str
    _2_ans: str
    _2_ans_trans: str
    _2_trans: str
    _2_pzl_vce: str
    _2_fil_vce: str
    _2_trans_vce: str


class TwoSentencesPuzzlerNote(AnkiNote):
    def __init__(self, note: AnkiNote):
        self.note = note

    def to_list(self) -> List[str]:
        return list(self.note.values())


TEMPLATES: List[AnkiTemplate] = [
    {
        "name": "Two Sentence Puzzler Template",
        "qfmt": """
<div class="card">
  <div id="puzzle-sentences">
    <p id="sentence1">{{1_pzl}}</p>
    <p id="sentence2">{{2_pzl}}</p>
  </div>
  [sound:{{1_pzl_vce}}]
  [sound:{{2_pzl_vce}}]
</div>
    """,
        "afmt": """
<div class="card">
  <div id="filled-sentences">
    <p>{{1_fil}}</p>
    <p>{{2_fil}}</p>
  </div>
  <hr>
  <div class="explanations">
    <p>{{expl_1}}</p>
    <p>{{expl_2}}</p>
  </div>
  <div class="translations">
    <p>{{1_trans}}</p>
    <p>{{2_trans}}</p>
  </div>
  [sound:{{1_fil_vce}}]
  [sound:{{2_fil_vce}}]
  [sound:{{1_trans_vce}}]
  [sound:{{2_trans_vce}}]
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
