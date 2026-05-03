import html
import random
import textwrap
import threading
from pathlib import Path
from typing import Callable, Optional, Tuple

from stablediffusion_dixit.image_generation.image_generator import ImageGenerator


BASE_DIR = Path(__file__).resolve().parents[2]
IMAGE_FOLDER = BASE_DIR / "images"


def random_anim_path() -> str:
    return f"premade_animations/{random.randrange(5)}.gif"


def write_mock_card(index: int, prompt: str) -> str:
    IMAGE_FOLDER.mkdir(exist_ok=True)
    palette = [
        ("#1d3557", "#f1faee", "#e63946"),
        ("#2a9d8f", "#fff3b0", "#264653"),
        ("#6d597a", "#f8edeb", "#b56576"),
        ("#003049", "#fdf0d5", "#f77f00"),
        ("#386641", "#f2e8cf", "#bc4749"),
    ]
    bg, fg, accent = palette[index % len(palette)]
    lines = textwrap.wrap(prompt.strip() or "Untitled dream", width=22)[:6]
    line_markup = "\n".join(
        f'<text x="192" y="{220 + (line_index * 34)}" text-anchor="middle">{html.escape(line)}</text>'
        for line_index, line in enumerate(lines)
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="384" height="512" viewBox="0 0 384 512">
  <rect width="384" height="512" rx="26" fill="{bg}"/>
  <circle cx="310" cy="88" r="64" fill="{accent}" opacity="0.9"/>
  <circle cx="76" cy="424" r="86" fill="{fg}" opacity="0.16"/>
  <path d="M55 148 C116 62, 237 72, 318 155 C254 130, 165 145, 55 148 Z" fill="{fg}" opacity="0.22"/>
  <rect x="44" y="178" width="296" height="184" rx="18" fill="{fg}" opacity="0.92"/>
  <g font-family="Georgia, serif" font-size="25" fill="{bg}">
    {line_markup}
  </g>
  <text x="192" y="450" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="{fg}" opacity="0.72">local playable card</text>
</svg>
"""
    file_name = f"{index}.svg"
    (IMAGE_FOLDER / file_name).write_text(svg, encoding="utf-8")
    return f"images/{file_name}"


class MockImageGenerator(ImageGenerator):
    def __init__(self):
        IMAGE_FOLDER.mkdir(exist_ok=True)
        self.generated_images = []

    def request_generation(self, prompt: str, callback: Optional[Callable[[int, str, str], None]] = None) -> int:
        index = len(self.generated_images)
        self.generated_images.append(None)

        def generate_card():
            image_path = write_mock_card(index, prompt)
            anim_path = random_anim_path()
            self.generated_images[index] = image_path, anim_path
            if callback is not None:
                callback(index, image_path, anim_path)

        threading.Thread(target=generate_card, daemon=True).start()
        return index

    def get_image_and_anim(self, image_num) -> Optional[Tuple[str, str]]:
        return self.generated_images[image_num]
