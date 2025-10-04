from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from .models import CarouselPost
from .utils import sanitize_caption


class MarkdownExporter:
    """Generate the Markdown export for carousel posts."""

    def __init__(self, exports_dir: Path) -> None:
        self.exports_dir = exports_dir

    def export(self, username: str, posts: Iterable[CarouselPost]) -> Path:
        posts_list = list(posts)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.exports_dir / f"tiktok_{username}_carousels.md"
        lines: List[str] = [f"# TikTok Profile: @{username}", ""]

        total_images = 0
        total_words = 0

        for carousel_index, post in enumerate(posts_list, start=1):
            caption = sanitize_caption(post.caption)
            lines.append(f"## Carousel {carousel_index}: \"{caption}\"")
            for image in post.images:
                total_images += 1
                if image.ocr_text:
                    total_words += image.word_count()
                local_path = image.local_path or Path("(download failed)")
                lines.append(f"- Image {image.index}: `{local_path}`")
                lines.append("  - **Extracted text:**")
                lines.append("    ```")
                if image.ocr_text:
                    for text_line in image.ocr_text.split("\n"):
                        lines.append(f"    {text_line}")
                else:
                    lines.append("    (no text detected)")
                lines.append("    ```")
            lines.append("\n---\n")

        total_carousels = len(posts_list)
        avg_words = (total_words / total_images) if total_images else 0
        lines.append("### Summary")
        lines.append(f"- Total carousels: {total_carousels}")
        lines.append(f"- Total images: {total_images}")
        lines.append(f"- Average OCR text length: {avg_words:.0f} words/image")
        lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path
