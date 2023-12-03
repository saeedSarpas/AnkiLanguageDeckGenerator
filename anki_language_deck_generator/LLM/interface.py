from abc import ABC, abstractmethod


class LlmSingleShot(ABC):
    @abstractmethod
    def __init__(self, system_prompt: str):
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def __enter__(self) -> 'LlmSingleShot':
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def shoot(self, prompt: str) -> str:
        raise Exception("I haven't been implemented yet")
