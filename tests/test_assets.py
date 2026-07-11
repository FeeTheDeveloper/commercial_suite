from pathlib import Path

from commercial_suite.assets import resolve_font, select_images, select_logo
from commercial_suite.ingestion import load_brand_kit


def test_select_logo_returns_none_when_empty(repo_root):
    brand = load_brand_kit(repo_root)
    assert select_logo(brand, repo_root) is None


def test_select_logo_finds_image(repo_root, tmp_path):
    brand = load_brand_kit(repo_root)
    logos_dir = tmp_path / brand.assets.logos_dir
    logos_dir.mkdir(parents=True)
    (logos_dir / "logo.png").write_bytes(b"fake")
    (logos_dir / "notes.txt").write_bytes(b"ignored")

    logo = select_logo(brand, tmp_path)
    assert logo is not None
    assert logo.name == "logo.png"


def test_select_images_respects_limit(repo_root, tmp_path):
    brand = load_brand_kit(repo_root)
    images_dir = tmp_path / brand.assets.images_dir
    images_dir.mkdir(parents=True)
    for i in range(10):
        (images_dir / f"photo_{i}.jpg").write_bytes(b"fake")

    assert len(select_images(brand, tmp_path, limit=3)) == 3


def test_resolve_font_falls_back_to_none(repo_root):
    brand = load_brand_kit(repo_root)
    font = resolve_font(brand, Path("/nonexistent"))
    assert font is None
