from abc import ABC, abstractmethod


class LlmSingleShot(ABC):
    @abstractmethod
    def start(self) -> bool:
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def stop(self) -> bool:
        raise Exception("I haven't been implemented yet")

    @abstractmethod
    def shoot(self, prompt: str) -> str:
        raise Exception("I haven't been implemented yet")
