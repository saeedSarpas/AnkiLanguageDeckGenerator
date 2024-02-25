def remove_article(word: str) -> str:
    articles = ["the", "a", "an"]
    words = word.strip().split()

    if words and words[0].lower() in articles:
        return " ".join(words[1:])
    else:
        return " ".join(words)
