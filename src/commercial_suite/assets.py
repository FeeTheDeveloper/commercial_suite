"""Asset selection: resolve logos, images, and fonts from the brand kit."""

from __future__ import annotations

from pathlib import Path

from .models import BrandKit

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
FONT_EXTENSIONS = {".ttf", ".otf"}


def _list_files(directory: Path, extensions: set[str]) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.iterdir() if p.suffix.lower() in extensions)


def select_logo(brand: BrandKit, repo_root: Path) -> Path | None:
    """Pick the first available logo image, or None if the kit has none."""
    logos = _list_files(repo_root / brand.assets.logos_dir, IMAGE_EXTENSIONS)
    return logos[0] if logos else None


def select_images(brand: BrandKit, repo_root: Path, limit: int = 5) -> list[Path]:
    """Pick approved brand images to use as scene backdrops."""
    return _list_files(repo_root / brand.assets.images_dir, IMAGE_EXTENSIONS)[:limit]


def resolve_font(brand: BrandKit, repo_root: Path, heading: bool = True) -> Path | None:
    """Resolve the brand heading/body font, falling back to any font in the kit."""
    configured = brand.typography.heading_font if heading else brand.typography.body_font
    if configured:
        path = repo_root / configured
        if path.is_file():
            return path
    fonts = _list_files(repo_root / brand.assets.fonts_dir, FONT_EXTENSIONS)
    return fonts[0] if fonts else None
