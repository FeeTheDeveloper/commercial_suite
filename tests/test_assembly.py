import pytest

from commercial_suite.assembly import _hex_to_rgb, assemble_video, render_scene_image
from commercial_suite.ingestion import load_brand_kit, load_campaign, load_template
from commercial_suite.render import PLATFORM_SPECS
from commercial_suite.scriptgen import generate_storyboard


def test_hex_to_rgb():
    assert _hex_to_rgb("#FFFFFF") == (255, 255, 255)
    assert _hex_to_rgb("#1F6FEB") == (31, 111, 235)


def test_render_scene_image_dimensions():
    spec = PLATFORM_SPECS["instagram_feed"]
    image = render_scene_image("Hello", "World", "#0D1117", "#FFFFFF", spec)
    assert image.size == (spec.width, spec.height)


def test_assemble_rejects_over_max_duration(repo_root, tmp_path):
    brand = load_brand_kit(repo_root)
    campaign = load_campaign(repo_root, "summer_sale")
    template = load_template(repo_root, campaign.template)
    campaign = campaign.model_copy(update={"duration_seconds": 120})
    storyboard = generate_storyboard(brand, campaign, template)

    with pytest.raises(ValueError, match="at most"):
        assemble_video(
            storyboard,
            brand,
            "tiktok",
            output_dir=tmp_path / "out",
            frames_dir=tmp_path / "frames",
        )


def test_smoke_render_short_video(repo_root, tmp_path):
    """End-to-end smoke test: render a 5s video at low cost via a small spec."""
    brand = load_brand_kit(repo_root)
    campaign = load_campaign(repo_root, "summer_sale")
    template = load_template(repo_root, campaign.template)
    campaign = campaign.model_copy(update={"duration_seconds": 5})
    storyboard = generate_storyboard(brand, campaign, template)

    out = assemble_video(
        storyboard,
        brand,
        "instagram_feed",
        output_dir=tmp_path / "out",
        frames_dir=tmp_path / "frames",
    )
    assert out.is_file()
    assert out.stat().st_size > 0
