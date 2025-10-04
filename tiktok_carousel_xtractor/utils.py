from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

USERNAME_PATTERN = re.compile(r"@?(?P<username>[A-Za-z0-9._]+)")


def extract_username(profile_url: str) -> str:
    """Extract the username from a TikTok profile URL or raw handle."""

    if not profile_url:
        raise ValueError("A TikTok profile URL or username must be provided.")

    profile_url = profile_url.strip()
    if not profile_url:
        raise ValueError("A TikTok profile URL or username must be provided.")

    # If the user already provided a plain username or @username, return it.
    if "/" not in profile_url:
        return profile_url.lstrip("@")

    match = USERNAME_PATTERN.search(profile_url.split("?")[0].rstrip("/"))
    if not match:
        raise ValueError(f"Unable to extract username from '{profile_url}'.")
    return match.group("username")


def ensure_directory(path: Path) -> None:
    """Create a directory (and parents) if it does not already exist."""

    path.mkdir(parents=True, exist_ok=True)


def sanitize_caption(caption: Optional[str]) -> str:
    """Return a safe caption string for Markdown output."""

    if not caption:
        return "No caption"
    caption = caption.strip()
    return caption or "No caption"
