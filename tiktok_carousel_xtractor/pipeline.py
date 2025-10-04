from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .downloader import ImageDownloader
from .extractor import TikTokCarouselExtractor
from .markdown import MarkdownExporter
from .models import CarouselPost
from .ocr import OcrProcessor
from .utils import extract_username

logger = logging.getLogger(__name__)


@dataclass
class ExtractionConfig:
    profile_url: str
    data_dir: Path = Path("data")
    exports_dir: Path = Path("exports")
    max_posts: Optional[int] = None
    download_concurrency: int = 10
    download_timeout: int = 30
    ocr_language: str = "eng"


class CarouselPipeline:
    """End-to-end pipeline that orchestrates extraction, download, OCR and export."""

    def __init__(self, config: ExtractionConfig) -> None:
        self.config = config
        self.username = extract_username(config.profile_url)
        self.extractor = TikTokCarouselExtractor(
            username=self.username, max_posts=config.max_posts
        )
        self.downloader = ImageDownloader(
            base_dir=config.data_dir,
            concurrency=config.download_concurrency,
            timeout=config.download_timeout,
        )
        self.ocr = OcrProcessor(language=config.ocr_language)
        self.exporter = MarkdownExporter(exports_dir=config.exports_dir)

    def run(self) -> Path:
        logger.info("Fetching carousels for @%s", self.username)
        posts = self.extractor.fetch_carousels()
        if not posts:
            logger.warning("No carousel posts found for @%s", self.username)
        logger.info("Downloading %d carousel posts", len(posts))
        asyncio.run(self.downloader.download_for_posts(posts, self.username))

        logger.info("Running OCR on downloaded images")
        for post in posts:
            self.ocr.process_images(post.images)

        logger.info("Generating Markdown export")
        return self.exporter.export(self.username, posts)

    def fetch_only(self) -> List[CarouselPost]:
        return self.extractor.fetch_carousels()
