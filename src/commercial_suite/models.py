"""Pydantic schemas for the brand kit, campaigns, and templates."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class Company(BaseModel):
    name: str
    tagline: str = ""
    mission: str = ""
    website: str = ""


class Voice(BaseModel):
    tone: list[str] = Field(default_factory=list)
    guidelines: list[str] = Field(default_factory=list)
    banned_words: list[str] = Field(default_factory=list)


class Audience(BaseModel):
    name: str
    description: str = ""


class Palette(BaseModel):
    primary: str
    secondary: str
    accent: str
    background: str
    text: str

    @field_validator("primary", "secondary", "accent", "background", "text")
    @classmethod
    def validate_hex(cls, value: str) -> str:
        if not HEX_COLOR_RE.match(value):
            raise ValueError(f"{value!r} is not a valid hex color (expected #RRGGBB)")
        return value


class Typography(BaseModel):
    heading_font: str = ""
    body_font: str = ""


class AssetDirs(BaseModel):
    logos_dir: str = "brand/assets/logos"
    images_dir: str = "brand/assets/images"
    fonts_dir: str = "brand/assets/fonts"
    audio_dir: str = "brand/assets/audio"


class Legal(BaseModel):
    disclaimer: str = ""


class BrandKit(BaseModel):
    company: Company
    voice: Voice = Field(default_factory=Voice)
    audiences: list[Audience] = Field(default_factory=list)
    palette: Palette
    typography: Typography = Field(default_factory=Typography)
    assets: AssetDirs = Field(default_factory=AssetDirs)
    legal: Legal = Field(default_factory=Legal)


class Campaign(BaseModel):
    name: str
    goal: str
    message: str
    cta: str
    template: str
    audience: str = ""
    platforms: list[str]
    duration_seconds: int = Field(default=15, ge=5, le=120)

    @field_validator("platforms")
    @classmethod
    def validate_platforms(cls, value: list[str]) -> list[str]:
        from .render import PLATFORM_SPECS

        unknown = [p for p in value if p not in PLATFORM_SPECS]
        if unknown:
            raise ValueError(
                f"Unknown platform(s) {unknown}; supported: {sorted(PLATFORM_SPECS)}"
            )
        if not value:
            raise ValueError("At least one platform is required")
        return value


class Scene(BaseModel):
    role: str
    heading: str = ""
    body: str = ""
    background: str = "background"
    duration_weight: float = Field(default=1.0, gt=0)

    @field_validator("background")
    @classmethod
    def validate_background(cls, value: str) -> str:
        allowed = set(Palette.model_fields)
        if value not in allowed:
            raise ValueError(f"background must be one of {sorted(allowed)}")
        return value


class Template(BaseModel):
    name: str
    description: str = ""
    scenes: list[Scene] = Field(min_length=1)
