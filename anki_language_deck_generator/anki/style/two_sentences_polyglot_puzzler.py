from anki_language_deck_generator.anki.interface import AnkiFields, AnkiNote
from typing import TypedDict, Dict, List

from .interface import AnkiStyle, AnkiTemplate


class TwoSentencesPuzzlerNoteType(TypedDict):
    _1_pzl: str
    _1_pzl_hint: str
    _1_fil: str
    _1_ans: str
    _1_ans_trans: str
    _1_trans: str
    _1_pzl_vce: str
    _1_fil_vce: str
    _1_trans_vce: str
    _2_pzl: str
    _2_pzl_hint: str
    _2_fil: str
    _2_ans: str
    _2_ans_trans: str
    _2_trans: str
    _2_pzl_vce: str
    _2_fil_vce: str
    _2_trans_vce: str



class TwoSentencesPuzzlerFields(AnkiFields):
    def __init__(self) -> None:
        self.fields = [
            '1_pzl', # 1st sentence puzzle
            '1_pzl_hint', # 1st sentence puzzle with hint
            '1_fil', # 1st sentence filled
            '1_ans', # 1st sentence answer
            '1_ans_trans', # 1st sentence answer translation
            '1_trans', # 1st sentence translation
            '1_pzl_vce', # 1st sentence puzzle voice
            '1_fil_vce', # 1st sentence filled voice
            '1_trans_vce', # 1st sentence translation voice
            '2_pzl', # 2nd sentence puzzle
            '2_pzl_hint', # 2nd sentence puzzle with hint
            '2_fil', # 2nd sentence filled
            '2_ans', # 2nd sentence answer
            '2_ans_trans', # 2nd sentence answer translation
            '2_trans', # 2nd sentence translation
            '2_pzl_vce', # 2nd sentence puzzle voice
            '2_fil_vce', # 2nd sentence filled voice
            '2_trans_vce', # 1st sentence translation voice
            'expl_1', # Extra explanation
            'expl_2', # Extra explanation
        ]

    def to_genanki_fields(self) -> Dict[str, str]:
        return {'name': filed for filed in self.fields}


class TwoSentencesPuzzlerStyle(AnkiStyle):
    def get_fields(self) -> 'AnkiFields':
        return TwoSentencesPuzzlerFields()

    def get_templates(self) -> str:
        return TEMPLATES

    def get_css(self) -> str:
        return CSS


class TwoSentencesPuzzlerNote(AnkiNote):
    def __init__(self, note: TwoSentencesPuzzlerNoteType) -> None:
        super().__init__(note)

    def to_list(self) -> List[str]:
        return list(self.note.values())


TEMPLATES: List[AnkiTemplate] = [{
    'name': 'Two Sentence Puzzler Template',
    'qfmt': '''
<div class="card">
  <div id="puzzle-sentences">
    <p id="sentence1">{{1_pzl}}</p>
    <p id="sentence2">{{2_pzl}}</p>
  </div>
  <button id="show-hints-btn">Show Hints</button>
  [sound:{{1_pzl_vce}}]
  [sound:{{2_pzl_vce}}]
</div>

<script>
  document.getElementById('show-hints-btn').onclick = function() {
    document.getElementById('sentence1').innerHTML = '{{1_pzl_hint}}';
    document.getElementById('sentence2').innerHTML = '{{2_pzl_hint}}';
  };
</script>
    ''',
    'afmt': '''
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
'''
}]

CSS: str = '''
.card {
  font-family: Arial, sans-serif;
  text-align: center;
  color: #333;
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

p {
  margin: 15px 0;
  line-height: 1.6;
}

button {
  background-color: #007aff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 20px;
}

button:hover {
  background-color: #005ecb;
}

hr {
  margin: 20px 0;
  border: none;
  height: 1px;
  background-color: #ccc;
}
'''