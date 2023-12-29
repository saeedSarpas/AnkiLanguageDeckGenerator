import gc
import torch
from PIL import Image
from diffusers import StableDiffusionPipeline

from .interfaces import T2I, T2IConfig


class StableDiffusionV15(T2I):
    default_config = T2IConfig(
        model_id="runwayml/stable-diffusion-v1-5",
        default_negative_prompt="nsfw, nudity, violent, disturbing, offensive, sensitive content, disrespectful, unethical, blurry, pixelated, noisy",
        default_positive_prompt="Ultra HD, sharp, soft, Aesthetic",
    )

    def __init__(self, config: T2IConfig = None):
        self.config = config if config is not None else self.default_config
        self.pipe = None

    def __enter__(self) -> "StableDiffusion":
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.config.model_id, torch_dtype=torch.float16
        )
        self.pipe.to("cuda")
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        try:
            del self.pipe
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            return True
        except Exception as e:
            print(f"Unable to gracefully stop the model. Error: {e}")
            return False

    def run(
        self,
        prompt: str,
        filename: str,
        negative_prompt: str = None,
        positive_prompot: str = None,
        prefix: str = ".",
    ) -> (Image, str):
        processed_negative_prompt = (
            negative_prompt
            if negative_prompt is not None
            else self.config.default_negative_prompt
        )
        processed_positive_prompt = (
            positive_prompot
            if positive_prompot is not None
            else self.config.default_positive_prompt
        )

        processed_prompt = prompt + processed_positive_prompt

        img = self.pipe(
            prompt=processed_prompt,
            negative_prompt=processed_negative_prompt,
            height=512,
            width=512,
        ).images[0]

        img_path = f"{prefix}/{filename.replace('.jpg', '')}.jpg"
        img.save(img_path)
        return (img, img_path)
