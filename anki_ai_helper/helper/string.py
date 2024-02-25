import json
import re


def find_and_parse_json(text: str, keys: list) -> dict | None:
    try:
        start_index = text.find("{")
        if start_index == -1:
            return None

        open_braces = 0
        for i in range(start_index, len(text)):
            if text[i] == "{":
                open_braces += 1
            elif text[i] == "}":
                open_braces -= 1
                if open_braces == 0:
                    end_index = i
                    break
        else:
            return None

        json_str = text[start_index : end_index + 1]
        json_obj = json.loads(json_str)

        if all(key in json_obj for key in keys):
            return {key: json_obj[key] for key in keys}
        else:
            return None
    except json.JSONDecodeError:
        return None


def count_dots_islands(sentence: str) -> int:
    dot_islands = re.findall(r"\.{2,}", sentence)
    return len(dot_islands)


def replace_dot_islands(sentence: str, replacement: str) -> str:
    dot_islands_pattern = r"\.{2,}"
    replaced_sentence = re.sub(dot_islands_pattern, replacement, sentence)
    return replaced_sentence
