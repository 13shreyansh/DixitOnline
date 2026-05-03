import base64
import os
import threading
import urllib.request
from pathlib import Path
from typing import Callable, Optional, Tuple

from openai import OpenAI

from stablediffusion_dixit.image_generation.image_generator import ImageGenerator
from stablediffusion_dixit.image_generation.mock_image_generator import (
    IMAGE_FOLDER,
    random_anim_path,
    write_mock_card,
)


class OpenAIImageGenerator(ImageGenerator):
    def __init__(self):
        self.client = OpenAI(timeout=float(os.environ.get("OPENAI_TIMEOUT_SECONDS", "45")))
        self.models = [
            model.strip()
            for model in os.environ.get("OPENAI_IMAGE_MODELS", "gpt-image-1-mini,gpt-image-1,dall-e-3").split(",")
            if model.strip()
        ]
        self.size = os.environ.get("OPENAI_IMAGE_SIZE", "1024x1536")
        self.quality = os.environ.get("OPENAI_IMAGE_QUALITY", "low")
        self.generated_images = []
        IMAGE_FOLDER.mkdir(exist_ok=True)

    def request_generation(self, prompt: str, callback: Optional[Callable[[int, str, str], None]] = None) -> int:
        index = len(self.generated_images)
        self.generated_images.append(None)

        def generate_card():
            image_path = self._generate_image(index, prompt)
            anim_path = random_anim_path()
            self.generated_images[index] = image_path, anim_path
            if callback is not None:
                callback(index, image_path, anim_path)

        threading.Thread(target=generate_card, daemon=True).start()
        return index

    def get_image_and_anim(self, image_num) -> Optional[Tuple[str, str]]:
        return self.generated_images[image_num]

    def _generate_image(self, index: int, prompt: str) -> str:
        IMAGE_FOLDER.mkdir(exist_ok=True)
        try:
            result = self._request_image(prompt)
            image = result.data[0]
            image_bytes = self._image_bytes(image)
            file_name = f"{index}.png"
            (IMAGE_FOLDER / file_name).write_bytes(image_bytes)
            return f"images/{file_name}"
        except Exception as exc:
            print(f"OpenAI image generation failed, using local fallback: {exc}")
            return write_mock_card(index, prompt)

    def _image_bytes(self, image) -> bytes:
        if getattr(image, "b64_json", None):
            return base64.b64decode(image.b64_json)
        if getattr(image, "url", None):
            with urllib.request.urlopen(image.url, timeout=60) as response:
                return response.read()
        raise RuntimeError("OpenAI image response did not include image bytes or a URL")

    def _request_image(self, prompt: str):
        prompt = self._card_prompt(prompt)
        last_error = None
        for model in self.models:
            try:
                return self.client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=self._size_for_model(model),
                    quality=self._quality_for_model(model),
                    n=1,
                )
            except Exception as exc:
                last_error = exc
                print(f"OpenAI image model {model} failed: {exc}")
        raise last_error or RuntimeError("No OpenAI image models configured")

    def _size_for_model(self, model: str) -> str:
        if model == "dall-e-3" and self.size == "1024x1536":
            return "1024x1792"
        return self.size

    def _quality_for_model(self, model: str) -> str:
        if model == "dall-e-3" and self.quality == "low":
            return "standard"
        return self.quality

    def _card_prompt(self, prompt: str) -> str:
        return (
            "Create a vertical Dixit-style illustrated game card. "
            "Make it whimsical, surreal, painterly, family-friendly, and suitable for a social guessing game. "
            "Do not include any readable text, logos, watermarks, UI, or borders inside the image. "
            f"Card concept: {prompt.strip() or 'a mysterious dream'}"
        )
