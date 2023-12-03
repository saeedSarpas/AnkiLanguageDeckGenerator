import gc
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from .interface import LlmSingleShot

from anki_language_deck_generator.configs import MODELS, VICUNA_7B_V15

VICUNA_MODEL = MODELS[VICUNA_7B_V15]


class Vicuna(LlmSingleShot):
    _template: str = "{system} USER: {query} ASSISTANT:"

    def __init__(self, system_prompt: str):
        self.model = None
        self.tokenizer = None
        self.system_prompt = system_prompt

    def __enter__(self) -> 'Vicuna':
        self.tokenizer = AutoTokenizer.from_pretrained(
            VICUNA_MODEL.name,
            use_fast=True,
            model_max_length=VICUNA_MODEL.context_len,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            VICUNA_MODEL.name,
            device_map=VICUNA_MODEL.device,
            torch_dtype=torch.bfloat16,
            max_position_embeddings=VICUNA_MODEL.context_len
        )

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        try:
            del self.model
            del self.tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            return True
        except Exception as e:
            print(f"Unable to gracefully stop the model. Error: {e}")
            return False

    def shoot(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(VICUNA_MODEL.device)
        outputs_gen = self.model.generate(
            **inputs,
            max_new_tokens=VICUNA_MODEL.max_new_tokens,
            min_new_tokens=VICUNA_MODEL.min_new_tokens,
            do_sample=VICUNA_MODEL.do_sample,
            temperature=VICUNA_MODEL.temperature,
            top_k=VICUNA_MODEL.top_k,
            top_p=VICUNA_MODEL.top_p,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        return self.tokenizer.batch_decode(outputs_gen)[0]
