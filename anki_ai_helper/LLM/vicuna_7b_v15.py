import gc
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from .interface import LlmSingleShot


MODEL_NAME = "lmsys/vicuna-7b-v1.5"


class Vicuna7Bv15(LlmSingleShot):
    _template: str = "{system} USER: {query} ASSISTANT:"
    _split_key: str = "ASSISTANT:"

    def __init__(self, system_prompt: str):
        self.model = None
        self.tokenizer = None
        self.system_prompt = system_prompt

    def __enter__(self) -> "Vicuna7Bv15":
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            use_fast=True,
            model_max_length=4096,
            do_sample=True,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="cuda",
            torch_dtype=torch.bfloat16,
            max_position_embeddings=4096,
            do_sample=True,
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
        filled_prompt = self._template.replace("{system}", self.system_prompt).replace(
            "query", prompt
        )

        inputs = self.tokenizer(filled_prompt, return_tensors="pt").to("cuda")

        outputs_gen = self.model.generate(
            **inputs,
            max_new_tokens=256,
            min_new_tokens=0,
            do_sample=True,
            temperature=0.2,
            top_k=50,
            top_p=0.3,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.bos_token_id,
        )

        response = self.tokenizer.batch_decode(outputs_gen)[0]
        pos = response.find(self._split_key)

        if pos != -1:
            return response[pos + len(self._split_key) :].replace("</s>", "").strip()
        else:
            return None
