from abc import ABC, abstractmethod
from PIL import Image


class T2IConfig:
    def __init__(
        self, model_id: str, default_negative_prompt: str, default_positive_prompt: str
    ):
        self.model_id = model_id
        self.default_negative_prompt = default_negative_prompt
        self.default_positive_prompt = default_positive_prompt


class T2I(ABC):
    @abstractmethod
    def __init__(self, config: T2IConfig):
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def __enter__(self) -> "T2I":
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def run(
        self, prompt: str, filename: str, negative_prompt: str = ""
    ) -> (Image, str):
        raise Exception("I haven't been implemented yet")
