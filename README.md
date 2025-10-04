# TikTok Carousel Xtractor

TikTok Carousel Xtractor is a command-line utility that automates the extraction of carousel posts from a TikTok profile. It downloads every image in each carousel, runs OCR on the downloaded assets, and produces a single Markdown document with metadata, OCR output, and summary statistics.

## Features

- Validate a TikTok profile URL and extract the username automatically.
- Retrieve carousel (multi-image) posts while skipping videos or single-image posts.
- Download all carousel images to a structured directory under `data/`.
- Perform OCR using [pytesseract](https://github.com/madmaze/pytesseract) on each image.
- Generate a Markdown report summarizing the extracted content.

## Requirements

- Python 3.11+
- System installation of [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (required by `pytesseract`).
- The Python dependencies listed in `requirements.txt`.

Install the Python requirements with:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m tiktok_carousel_xtractor.cli "https://www.tiktok.com/@username"
```

### CLI options

| Option | Description |
| --- | --- |
| `profile_url` | TikTok profile URL or `@username`. |
| `--max-posts` | Optional limit on the number of posts to fetch. |
| `--data-dir` | Directory where images will be stored (default: `data/`). |
| `--exports-dir` | Directory where the Markdown report will be written (default: `exports/`). |
| `--ocr-language` | Language code passed to Tesseract (default: `eng`). |
| `--download-timeout` | Timeout in seconds for image downloads (default: `30`). |
| `--download-concurrency` | Number of concurrent image downloads (default: `10`). |

### Output structure

- Images are downloaded to `data/<username>/carousel_<index>/`.
- The Markdown report is saved to `exports/tiktok_<username>_carousels.md`.

## Development

This project uses `TikTokApi` for scraping carousel metadata and `aiohttp` for efficient concurrent downloads. OCR is performed locally with `pytesseract` and `Pillow`. The source code lives under the `tiktok_carousel_xtractor/` package and is orchestrated by the `CarouselPipeline` class.

## Disclaimer

TikTok's platform, API, and Terms of Service may change without notice. Ensure your use of this tool complies with TikTok's policies and local regulations.
