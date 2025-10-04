from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List, Optional

from TikTokApi import TikTokApi

from .models import CarouselImage, CarouselPost

logger = logging.getLogger(__name__)


@dataclass
class TikTokCarouselExtractor:
    """Handle retrieval of carousel posts from TikTok."""

    username: str
    max_posts: Optional[int] = None

    def fetch_carousels(self) -> List[CarouselPost]:
        """Fetch carousel posts for the configured user."""

        posts: List[CarouselPost] = []
        with TikTokApi() as api:
            user = api.user(username=self.username)
            kwargs = {}
            if self.max_posts is not None:
                kwargs["count"] = self.max_posts
            videos: Iterable = user.videos(**kwargs)
            for video in videos:
                aweme = getattr(video, "as_dict", None)
                if callable(aweme):
                    aweme = aweme()
                if aweme is None:
                    aweme = getattr(video, "info", None)
                if callable(aweme):
                    aweme = aweme()
                if not isinstance(aweme, dict):
                    logger.debug("Skipping video without dictionary representation: %s", video)
                    continue

                image_post_info = aweme.get("image_post_info") or {}
                images_data = image_post_info.get("images") or []
                if not images_data:
                    logger.debug("Skipping non-carousel post %s", aweme.get("aweme_id"))
                    continue

                images: List[CarouselImage] = []
                for index, image_data in enumerate(images_data, start=1):
                    url = _extract_image_url(image_data)
                    if not url:
                        logger.debug("Skipping image without URL in post %s", aweme.get("aweme_id"))
                        continue
                    images.append(CarouselImage(index=index, url=url))

                if not images:
                    continue

                caption = aweme.get("desc") or aweme.get("title") or ""
                aweme_id = aweme.get("aweme_id") or aweme.get("id") or f"{self.username}_{len(posts)+1}"
                posts.append(CarouselPost(aweme_id=aweme_id, caption=caption, images=images))

        return posts


def _extract_image_url(image_data: dict) -> Optional[str]:
    """Best-effort extraction of an image URL from TikTok image data."""

    display = image_data.get("display_image") or image_data.get("image") or {}
    url_list = display.get("url_list") or display.get("urls")
    if isinstance(url_list, list) and url_list:
        return url_list[0]

    # Some responses embed the URL directly.
    if isinstance(display, str):
        return display

    # Fallback to other potential keys.
    for key in ("url", "uri"):
        value = image_data.get(key)
        if isinstance(value, str) and value:
            return value
    return None
