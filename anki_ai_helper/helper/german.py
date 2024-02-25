import re
import spacy
import requests
import json
from bs4 import BeautifulSoup
from typing import Dict
import unicodedata

VERB_PREFIXES = [
    "ab",
    "an",
    "auf",
    "aus",
    "bei",
    "ein",
    "mit",
    "nach",
    "vor",
    "zu",
    "ent",
    "er",
    "ge",
    "miss",
    "ver",
    "zer",
    "be",
    "emp",
    "entgegen",
    "gegenüber",
    "hinter",
    "über",
    "um",
    "unter",
    "voll",
    "wider",
    "los",
]

# Run `python -m spacy download de_core_news_lg` to install the model

_german_nlp = spacy.load("de_core_news_lg")


def remove_article(word: str) -> str:
    articles = ["der", "die", "das", "ein", "eine", "einen", "einem"]
    words = word.strip().split()

    if words and words[0].lower() in articles:
        return " ".join(words[1:])
    else:
        return " ".join(words)


def obscure_closest_word(sentence: str, word: str) -> str | None:
    sentence_nlp = _german_nlp(sentence)
    word_nlp = _german_nlp(word)[0]

    target_is_verb = word_nlp.pos_ == "VERB"
    target_is_noun = word_nlp.pos_ == "NOUN"

    # Check and replace all exact matches of the word
    modified_sentence = ""
    for w in sentence_nlp:
        if any(w.text.lower() == single_word.lower() for single_word in word.split()):
            modified_sentence += "." * len(w.text) + w.whitespace_
        else:
            modified_sentence += w.text_with_ws

    # Check and replace all similar matches of the word
    closest_word = None
    highest_similarity = 0

    for w in sentence_nlp:
        if (target_is_verb and w.pos_ != "VERB") or (
            target_is_noun and w.pos_ != "NOUN"
        ):
            continue

        similarity = w.similarity(word_nlp)
        if similarity > highest_similarity:
            highest_similarity = similarity
            closest_word = w

    if closest_word:
        sentence = "".join(
            [
                "." * len(w.text) + w.whitespace_
                if w.lemma_ == closest_word.lemma_
                else w.text_with_ws
                for w in sentence_nlp
            ]
        )

    return (
        sentence
        if _count_dots_islands(sentence) > _count_dots_islands(modified_sentence)
        else modified_sentence
    )


def get_conjugation_from_reverso(verb: str) -> str:
    URL = f"https://conjugator.reverso.net/conjugation-german-verb-{verb}.html"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    }

    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    divs = soup.select("div.wrap-three-col > div.blue-box-wrap[mobile-title]")

    forms = {}

    for div in divs:
        mobile_title = div.get("mobile-title")
        div = soup.find("div", attrs={"mobile-title": mobile_title})
        ul = div.find("ul", class_="wrap-verbs-listing")
        li_tags = ul.find_all("li")

        result_dict = {}

        for li in li_tags:
            i_tags = li.find_all("i")
            key = i_tags[0].text.strip()
            value = "".join([i_tag.text for i_tag in i_tags[1:]]).strip()
            result_dict[key] = value

        forms[mobile_title] = result_dict

    return json.dumps(forms)


def get_declension_info_from_collinsdictionary(word: str) -> str | None:
    _word = remove_article(word)

    URL = f"https://www.collinsdictionary.com/dictionary/german-english/{_convert_umlauts(_word)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    }

    try:
        response = requests.get(URL, headers=headers)

        if response and response.text:
            declensions = _extract_declension_info(response.text, word)
            return json.dumps(declensions).strip() if declensions else None
        else:
            return None
    except Exception as e:
        print(f"Unable to process the response from collinsdictionary. word: {word}")
        return None


def _count_dots_islands(sentence: str) -> int:
    dot_islands = re.findall(r"\.{2,}", sentence)
    return len(dot_islands)


def _extract_declension_info(html: str, word: str) -> Dict[str, str] | None:
    declension_dict = {}

    try:
        soup = BeautifulSoup(html, "html.parser")

        # Attempt to get all noun forms from the declension table
        declension_table = soup.find("div", class_="short_noun_table decl")
        if declension_table:
            rows = declension_table.find_all("span", class_="tr")
            if rows:
                for row in rows[1:]:
                    cells = row.find_all("span", class_="td")

                    if len(cells) >= 3:
                        declension_dict[cells[0].text.strip()] = {
                            "Singular": cells[1].text.strip(),
                            "Plural": cells[2].text.strip(),
                        }

                if declension_dict:
                    return declension_dict

        # Attempt to get the Nominative plural form the word forms span
        word_fomrs = soup.find("span", class_="form inflected_forms type-infl")
        if word_fomrs:
            cells = word_fomrs.find_all("span", class_="orth")

            if cells and len(cells) > 0:
                plural = cells[-1].text.strip()

                declension_dict = {
                    "Nominative": {"Singular": word, "Plural": "die " + plural},
                    "Accusative": {"Singular": "", "Plural": ""},
                    "Genitive": {"Singular": "", "Plural": ""},
                    "Dative": {"Singular": "", "Plural": ""},
                }

                return declension_dict

        return None
    except Exception:
        return None


def _convert_umlauts(text):
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ASCII", "ignore").decode("ASCII")
    return ascii_text
