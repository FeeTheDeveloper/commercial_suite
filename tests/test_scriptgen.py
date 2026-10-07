import pytest

from commercial_suite.ingestion import load_brand_kit, load_campaign, load_template
from commercial_suite.scriptgen import generate_storyboard


def test_storyboard_durations_sum_to_campaign_duration(repo_root):
    brand = load_brand_kit(repo_root)
    campaign = load_campaign(repo_root, "summer_sale")
    template = load_template(repo_root, campaign.template)

    storyboard = generate_storyboard(brand, campaign, template)
    assert storyboard.campaign == "summer_sale"
    total = sum(s.duration_seconds for s in storyboard.scenes)
    assert total == pytest.approx(campaign.duration_seconds, abs=0.1)


def test_substitutions_applied(repo_root):
    brand = load_brand_kit(repo_root)
    campaign = load_campaign(repo_root, "summer_sale")
    template = load_template(repo_root, campaign.template)

    storyboard = generate_storyboard(brand, campaign, template)
    headings = [s.heading for s in storyboard.scenes]
    assert campaign.message in headings
    assert campaign.cta in headings
    assert all("{" not in h for h in headings)


def test_banned_words_rejected(repo_root):
    brand = load_brand_kit(repo_root)
    campaign = load_campaign(repo_root, "summer_sale")
    template = load_template(repo_root, campaign.template)
    campaign = campaign.model_copy(update={"message": "Everything is cheap now"})

    with pytest.raises(ValueError, match="banned"):
        generate_storyboard(brand, campaign, template)
