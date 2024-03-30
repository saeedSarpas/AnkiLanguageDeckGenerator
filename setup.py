from setuptools import setup, find_packages

setup(
    name="anki_ai_helper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "mypy",
        "pandas",
        "fastparquet",
        "torch",
        "transformers",
        "sentencepiece",
        "protobuf",
        "accelerate",
        "TTS",
        "nltk",
        "ankipandas",
        "genanki",
        "diffusers",
        "spacy",
        "beautifulsoup4",
        "pydub",
    ],
)
