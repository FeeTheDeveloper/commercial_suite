import pytest

from commercial_suite.ingestion import (
    ConfigError,
    list_campaigns,
    load_brand_kit,
    load_campaign,
    load_template,
)
from commercial_suite.models import Campaign, Palette


def test_load_brand_kit(repo_root):
    brand = load_brand_kit(repo_root)
    assert brand.company.name
    assert brand.palette.primary.startswith("#")


def test_load_campaign(repo_root):
    campaign = load_campaign(repo_root, "summer_sale")
    assert campaign.template == "product_promo"
    assert "youtube" in campaign.platforms


def test_load_template(repo_root):
    template = load_template(repo_root, "product_promo")
    assert template.scenes
    assert template.scenes[0].role == "intro"


def test_all_campaign_templates_exist(repo_root):
    for name in list_campaigns(repo_root):
        campaign = load_campaign(repo_root, name)
        load_template(repo_root, campaign.template)


def test_missing_campaign_raises(repo_root):
    with pytest.raises(ConfigError):
        load_campaign(repo_root, "does_not_exist")


def test_invalid_hex_color_rejected():
    with pytest.raises(ValueError):
        Palette(
            primary="notacolor",
            secondary="#000000",
            accent="#000000",
            background="#000000",
            text="#FFFFFF",
        )


def test_unknown_platform_rejected():
    with pytest.raises(ValueError):
        Campaign(
            name="x",
            goal="g",
            message="m",
            cta="c",
            template="product_promo",
            platforms=["myspace"],
        )


def test_duration_bounds_rejected():
    with pytest.raises(ValueError):
        Campaign(
            name="x",
            goal="g",
            message="m",
            cta="c",
            template="product_promo",
            platforms=["youtube"],
            duration_seconds=999,
        )
