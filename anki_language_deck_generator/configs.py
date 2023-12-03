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


VICUNA_7B_V15 = 'vicuna-7b-v1.5'

MODELS: Dict[str, LlmSetting] = {
    VICUNA_7B_V15: LlmSetting(
        name='lmsys/vicuna-7b-v1.5',
        device='cuda:0',
        context_len=4096,
        max_new_tokens=512,
        min_new_tokens=32,
        do_sample=True,
        temperature=0.9,
        top_k=0.0,
        top_p=None,
    )
}
