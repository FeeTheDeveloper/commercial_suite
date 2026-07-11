"""Ingestion layer: load and validate brand kit, campaigns, and templates."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from .models import BrandKit, Campaign, Template


class ConfigError(Exception):
    """Raised when a configuration file is missing or invalid."""


def _load_yaml(path: Path) -> dict:
    if not path.is_file():
        raise ConfigError(f"Config file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"Expected a mapping at the top level of {path}")
    return data


def load_brand_kit(repo_root: Path) -> BrandKit:
    path = repo_root / "brand" / "brand.yaml"
    try:
        return BrandKit.model_validate(_load_yaml(path))
    except ValidationError as exc:
        raise ConfigError(f"Invalid brand kit {path}:\n{exc}") from exc


def load_campaign(repo_root: Path, name: str) -> Campaign:
    path = repo_root / "campaigns" / f"{name}.yaml"
    try:
        return Campaign.model_validate(_load_yaml(path))
    except ValidationError as exc:
        raise ConfigError(f"Invalid campaign {path}:\n{exc}") from exc


def load_template(repo_root: Path, name: str) -> Template:
    path = repo_root / "templates" / f"{name}.yaml"
    try:
        return Template.model_validate(_load_yaml(path))
    except ValidationError as exc:
        raise ConfigError(f"Invalid template {path}:\n{exc}") from exc


def list_campaigns(repo_root: Path) -> list[str]:
    campaigns_dir = repo_root / "campaigns"
    if not campaigns_dir.is_dir():
        return []
    return sorted(p.stem for p in campaigns_dir.glob("*.yaml"))
