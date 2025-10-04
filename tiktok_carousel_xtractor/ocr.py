from __future__ import annotations

import logging
import re
from typing import Iterable

import pytesseract
from PIL import Image

from .models import CarouselImage

logger = logging.getLogger(__name__)


class OcrProcessor:
    """Run OCR on carousel images using pytesseract."""

    def __init__(self, language: str = "eng") -> None:
        self.language = language

    def process_images(self, images: Iterable[CarouselImage]) -> None:
        for image in images:
            if not image.local_path:
                logger.debug("Skipping OCR for image without a local path: %s", image.url)
                continue
            try:
                with Image.open(image.local_path) as img:
                    raw_text = pytesseract.image_to_string(img, lang=self.language)
                image.ocr_text = _clean_ocr_text(raw_text)
            except Exception as exc:  # noqa: BLE001 - OCR can fail for various reasons
                logger.warning("Failed to run OCR on %s: %s", image.local_path, exc)
                image.ocr_text = ""


def _clean_ocr_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned_lines = []
    for raw_line in text.split("\n"):
        normalized = re.sub(r"\s+", " ", raw_line).strip()
        if normalized:
            cleaned_lines.append(normalized)
    return "\n".join(cleaned_lines)
