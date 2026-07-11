"""Command line interface for the commercial suite pipeline."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from .assembly import assemble_video
from .assets import resolve_font, select_logo
from .config import load_settings
from .ingestion import ConfigError, list_campaigns, load_brand_kit, load_campaign, load_template
from .render import PLATFORM_SPECS
from .scriptgen import generate_storyboard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="commercial-suite",
        description="Generate marketing/campaign videos from a brand kit and campaign configs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate videos for a campaign")
    generate.add_argument("--campaign", required=True, help="Campaign name (campaigns/<name>.yaml)")
    generate.add_argument(
        "--platforms",
        help="Comma-separated platforms (defaults to the campaign's configured platforms). "
        f"Supported: {', '.join(sorted(PLATFORM_SPECS))}",
    )
    generate.add_argument(
        "--dry-run",
        action="store_true",
        help="Write the storyboard for review without rendering video",
    )
    generate.add_argument(
        "--repo-root", default=".", help="Path to the repository root (default: cwd)"
    )
    generate.add_argument(
        "--output-dir", default="output", help="Base output directory (default: output/)"
    )

    subparsers.add_parser("list-campaigns", help="List available campaigns")
    return parser


def cmd_generate(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    brand = load_brand_kit(repo_root)
    campaign = load_campaign(repo_root, args.campaign)
    template = load_template(repo_root, campaign.template)

    platforms = (
        [p.strip() for p in args.platforms.split(",") if p.strip()]
        if args.platforms
        else campaign.platforms
    )
    unknown = [p for p in platforms if p not in PLATFORM_SPECS]
    if unknown:
        print(f"Unknown platform(s): {unknown}. Supported: {sorted(PLATFORM_SPECS)}")
        return 1

    settings = load_settings()
    storyboard = generate_storyboard(brand, campaign, template, settings)

    output_base = Path(args.output_dir) / campaign.name
    output_base.mkdir(parents=True, exist_ok=True)

    # Human-review checkpoint: always save the storyboard artifact.
    storyboard_path = output_base / "storyboard.json"
    storyboard_path.write_text(
        json.dumps(storyboard.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Storyboard written to {storyboard_path}")

    if args.dry_run:
        print("Dry run: skipping video rendering.")
        return 0

    heading_font = resolve_font(brand, repo_root, heading=True)
    body_font = resolve_font(brand, repo_root, heading=False)
    logo = select_logo(brand, repo_root)

    for platform in platforms:
        with tempfile.TemporaryDirectory(prefix="frames_") as frames_dir:
            out_path = assemble_video(
                storyboard,
                brand,
                platform,
                output_dir=output_base / platform,
                frames_dir=Path(frames_dir),
                heading_font_path=heading_font,
                body_font_path=body_font,
                logo_path=logo,
            )
        print(f"Rendered {platform}: {out_path}")
    return 0


def cmd_list_campaigns(args: argparse.Namespace) -> int:
    for name in list_campaigns(Path(".").resolve()):
        print(name)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            return cmd_generate(args)
        if args.command == "list-campaigns":
            return cmd_list_campaigns(args)
    except (ConfigError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
