from abc import ABC, abstractmethod


class T2S(ABC):
    @abstractmethod
    def __init__(self, lang: str):
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def __enter__(self) -> 'T2S':
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def shoot(self, text: str, filename: str) -> str:
        raise Exception("I haven't been implemented yet")
