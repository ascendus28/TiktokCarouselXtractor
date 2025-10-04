from __future__ import annotations

import asyncio
import logging
import mimetypes
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urlparse

import aiohttp

from .models import CarouselImage, CarouselPost
from .utils import ensure_directory

logger = logging.getLogger(__name__)


class ImageDownloader:
    """Download carousel images concurrently."""

    def __init__(self, base_dir: Path, concurrency: int = 10, timeout: int = 30) -> None:
        self.base_dir = base_dir
        self.concurrency = concurrency
        self.timeout = timeout

    async def download_for_posts(self, posts: Iterable[CarouselPost], username: str) -> None:
        """Download all images for the provided carousel posts."""

        ensure_directory(self.base_dir)
        semaphore = asyncio.Semaphore(self.concurrency)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            tasks: List[asyncio.Task] = []
            for carousel_index, post in enumerate(posts, start=1):
                carousel_dir = self.base_dir / username / f"carousel_{carousel_index}"
                ensure_directory(carousel_dir)
                for image in post.images:
                    dest_path = carousel_dir / _filename_for_image(image)
                    tasks.append(
                        asyncio.create_task(
                            self._download_image(semaphore, session, image, dest_path)
                        )
                    )
            if tasks:
                await asyncio.gather(*tasks)

    async def _download_image(
        self,
        semaphore: asyncio.Semaphore,
        session: aiohttp.ClientSession,
        image: CarouselImage,
        dest_path: Path,
    ) -> None:
        async with semaphore:
            try:
                async with session.get(image.url) as response:
                    response.raise_for_status()
                    data = await response.read()
                    if not dest_path.suffix:
                        content_type = response.headers.get("Content-Type")
                        extension = _extension_from_content_type(content_type)
                        dest_path = dest_path.with_suffix(extension)
                    dest_path.write_bytes(data)
                    image.local_path = dest_path
                    logger.debug("Downloaded %s to %s", image.url, dest_path)
            except Exception as exc:  # noqa: BLE001 - network errors can vary
                logger.warning("Failed to download %s: %s", image.url, exc)


def _filename_for_image(image: CarouselImage) -> str:
    parsed = urlparse(image.url)
    suffix = Path(parsed.path).suffix
    if suffix:
        return f"image_{image.index}{suffix}"
    return f"image_{image.index}"


def _extension_from_content_type(content_type: Optional[str]) -> str:
    if not content_type:
        return ".jpg"
    extension = mimetypes.guess_extension(content_type.split(";")[0].strip())
    return extension or ".jpg"
