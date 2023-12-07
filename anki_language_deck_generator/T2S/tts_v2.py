import gc
import nltk
import torch
from TTS.api import TTS

from anki_language_deck_generator.configs import T2S_MODELS, TTS_V2_NAME

from .interface import T2S

# Download Punkt tokenizer (divides a text into a list of sentences)
nltk.download('punkt')


class TTSV2(T2S):
    _device = "cuda" if torch.cuda.is_available() else "cpu"

    def __init__(self, lang: str, asset_dir_path: str):
        self.lang = lang
        self.asset_dir_path = asset_dir_path
        self.tts = None

        if lang not in T2S_MODELS[TTS_V2_NAME]:
            raise Exception(f"Language is not supported currently. Lang: {lang}")

        self.model = T2S_MODELS[TTS_V2_NAME][lang].model
        self.speaker = T2S_MODELS[TTS_V2_NAME][lang].speaker
        
    def __enter__(self) -> 'T2S':
        self.tts = TTS(self.model).to(self._device)

        return self
        
    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        try:
            del self.tts
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            return True
        except Exception as e:
            print(f"Unable to gracefully stop TTS. Error: {e}")
            return False

    
    def shoot(self, text: str, filename: str) -> str:
        self.tts.tts_to_file(
            text=text,
            speaker=self.speaker if self.speaker else None,
            lang=self.lang,
            file_path=f"{self.asset_dir_path}/{filename}.wav")
