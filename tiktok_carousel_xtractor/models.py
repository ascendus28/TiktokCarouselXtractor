from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class CarouselImage:
    """Represents a single image inside a TikTok carousel."""

    index: int
    url: str
    local_path: Optional[Path] = None
    ocr_text: Optional[str] = None

    def word_count(self) -> int:
        """Return the number of words extracted by OCR for this image."""

        if not self.ocr_text:
            return 0
        return len(self.ocr_text.split())


@dataclass
class CarouselPost:
    """Represents a TikTok carousel post."""

    aweme_id: str
    caption: str
    images: List[CarouselImage] = field(default_factory=list)

    def total_word_count(self) -> int:
        """Return the total OCR word count across all images in the carousel."""

        return sum(image.word_count() for image in self.images)

    def image_count(self) -> int:
        """Return the number of images in this carousel."""

        return len(self.images)
