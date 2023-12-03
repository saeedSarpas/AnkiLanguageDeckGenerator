from setuptools import setup, find_packages

setup(
    name='anki_language_deck_generator',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        torch,
        transformers,
        sentencepiece,
        protobuf,
        accelerate,
    ],
)
