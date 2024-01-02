from typing import Dict


class LlmSetting:
    def __init__(
        self,
        name: str,
        device: str,
        context_len: int,
        max_new_tokens: int,
        min_new_tokens: int,
        do_sample: bool,
        temperature: float,
        top_k: float,
        top_p: float | None,
    ):
        self.name = name
        self.device = device
        self.context_len = context_len
        self.max_new_tokens = max_new_tokens
        self.min_new_tokens = min_new_tokens
        self.do_sample = do_sample
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p


class T2SLangSetting:
    def __init__(self, model: str, speaker: str | None = None) -> None:
        self.model = model
        self.speaker = speaker


TTS_V2_NAME = "tts-v2"

T2S_MODELS: Dict[str, Dict[str, T2SLangSetting]] = {
    TTS_V2_NAME: {
        "en": T2SLangSetting(model="tts_models/en/vctk/vits", speaker="p270"),
        "de": T2SLangSetting(model="tts_models/de/thorsten/tacotron2-DDC"),
    }
}
