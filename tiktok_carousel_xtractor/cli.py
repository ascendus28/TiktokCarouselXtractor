from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .pipeline import CarouselPipeline, ExtractionConfig

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract TikTok carousel posts, download images, run OCR, and export Markdown."
    )
    parser.add_argument("profile_url", help="TikTok profile URL or @username")
    parser.add_argument(
        "--max-posts",
        type=int,
        default=None,
        help="Maximum number of posts to fetch from the profile.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory where downloaded images will be stored.",
    )
    parser.add_argument(
        "--exports-dir",
        type=Path,
        default=Path("exports"),
        help="Directory where the Markdown export will be saved.",
    )
    parser.add_argument(
        "--ocr-language",
        default="eng",
        help="Language code to pass to Tesseract for OCR.",
    )
    parser.add_argument(
        "--download-timeout",
        type=int,
        default=30,
        help="Timeout (in seconds) for image downloads.",
    )
    parser.add_argument(
        "--download-concurrency",
        type=int,
        default=10,
        help="Number of images to download concurrently.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = ExtractionConfig(
        profile_url=args.profile_url,
        data_dir=args.data_dir,
        exports_dir=args.exports_dir,
        max_posts=args.max_posts,
        download_concurrency=args.download_concurrency,
        download_timeout=args.download_timeout,
        ocr_language=args.ocr_language,
    )

    pipeline = CarouselPipeline(config)
    output_path = pipeline.run()
    print(f"Export written to {output_path}")


if __name__ == "__main__":
    main()
