"""Script/copy generation: builds a storyboard from campaign + brand + template.

Uses an LLM when LLM_API_KEY is configured; otherwise falls back to an
offline template-substitution generator so the pipeline always works.
"""

from __future__ import annotations

import json
import logging
import urllib.request
from dataclasses import asdict, dataclass

from .config import Settings
from .models import BrandKit, Campaign, Template

logger = logging.getLogger(__name__)


@dataclass
class StoryboardScene:
    role: str
    heading: str
    body: str
    background: str
    duration_seconds: float


@dataclass
class Storyboard:
    campaign: str
    template: str
    scenes: list[StoryboardScene]

    def to_dict(self) -> dict:
        return asdict(self)


def _substitutions(brand: BrandKit, campaign: Campaign) -> dict[str, str]:
    return {
        "company_name": brand.company.name,
        "tagline": brand.company.tagline,
        "mission": brand.company.mission,
        "website": brand.company.website,
        "message": campaign.message,
        "goal": campaign.goal,
        "cta": campaign.cta,
        "disclaimer": brand.legal.disclaimer,
    }


def _apply_substitutions(text: str, subs: dict[str, str]) -> str:
    for key, value in subs.items():
        text = text.replace("{" + key + "}", value)
    return text


def _check_banned_words(text: str, banned: list[str]) -> None:
    lowered = text.lower()
    hits = [w for w in banned if w.lower() in lowered]
    if hits:
        raise ValueError(f"Generated copy contains banned words: {hits}")


def generate_storyboard(
    brand: BrandKit,
    campaign: Campaign,
    template: Template,
    settings: Settings | None = None,
) -> Storyboard:
    """Build a storyboard, optionally refining copy through an LLM."""
    subs = _substitutions(brand, campaign)
    if settings and settings.llm_api_key:
        refined = _refine_copy_with_llm(brand, campaign, settings)
        if refined:
            subs.update(refined)

    total_weight = sum(scene.duration_weight for scene in template.scenes)
    scenes: list[StoryboardScene] = []
    for scene in template.scenes:
        heading = _apply_substitutions(scene.heading, subs)
        body = _apply_substitutions(scene.body, subs)
        _check_banned_words(heading + " " + body, brand.voice.banned_words)
        duration = campaign.duration_seconds * scene.duration_weight / total_weight
        scenes.append(
            StoryboardScene(
                role=scene.role,
                heading=heading,
                body=body,
                background=scene.background,
                duration_seconds=round(duration, 2),
            )
        )
    return Storyboard(campaign=campaign.name, template=template.name, scenes=scenes)


def _refine_copy_with_llm(
    brand: BrandKit, campaign: Campaign, settings: Settings
) -> dict[str, str] | None:
    """Ask an OpenAI-compatible API to punch up the message and CTA.

    Returns a dict of substitution overrides, or None on any failure so the
    offline fallback copy is used instead.
    """
    prompt = (
        f"You are a marketing copywriter for {brand.company.name}.\n"
        f"Tone: {', '.join(brand.voice.tone)}.\n"
        f"Guidelines: {' '.join(brand.voice.guidelines)}\n"
        f"Never use these words: {', '.join(brand.voice.banned_words)}.\n"
        f"Campaign goal: {campaign.goal}\n"
        f"Draft message: {campaign.message}\n"
        f"Draft CTA: {campaign.cta}\n"
        'Respond with JSON: {"message": "...", "cta": "..."} — short, punchy, on-brand.'
    )
    payload = {
        "model": settings.llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        f"{settings.llm_api_base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + settings.llm_api_key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = json.loads(body["choices"][0]["message"]["content"])
        result = {}
        if isinstance(content.get("message"), str):
            result["message"] = content["message"]
        if isinstance(content.get("cta"), str):
            result["cta"] = content["cta"]
        return result or None
    except Exception as exc:
        logger.warning("LLM copy refinement failed, using draft copy: %s", exc)
        return None
