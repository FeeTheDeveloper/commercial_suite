# commercial_suite

Video content generation suite for marketing and campaigns. Everything is
driven by two sources of truth: a **brand kit** (company info, voice, colors,
fonts, logos, images) and per-campaign **config files** — adding a campaign is
just adding a YAML file.

## How it works

```
brand/brand.yaml ─┐
campaigns/*.yaml ─┼─▶ ingestion ─▶ script/copy generation ─▶ asset selection
templates/*.yaml ─┘                        │
                                           ▼
              output/<campaign>/  ◀─ per-platform rendering ◀─ video assembly
```

1. **Ingestion** loads and schema-validates the brand kit, campaign, and template.
2. **Script generation** builds a storyboard from the template, substituting
   brand and campaign copy. If `LLM_API_KEY` is set, an LLM refines the message
   and CTA within your brand voice guidelines; otherwise an offline fallback is
   used. Copy containing banned words is rejected.
3. **Asset selection** picks logos, fonts, and images from the brand kit.
4. **Video assembly** composes each scene (brand colors, fonts, logo watermark)
   into frames.
5. **Rendering** encodes platform-specific variants (16:9 YouTube, 9:16
   TikTok/Reels/Shorts, 1:1 feed) with the right resolution, fps, bitrate, and
   duration limits.

## Setup

```bash
pip install -e ".[dev]"
cp .env.example .env   # optional: add API keys for LLM copy refinement
```

Requires Python 3.10+. ffmpeg is bundled via `imageio-ffmpeg` — no system
install needed.

## Usage

```bash
# List campaigns
commercial-suite list-campaigns

# Review the generated script/storyboard before rendering (human checkpoint)
commercial-suite generate --campaign summer_sale --dry-run

# Render all platforms configured in the campaign
commercial-suite generate --campaign summer_sale

# Render specific platforms only
commercial-suite generate --campaign summer_sale --platforms tiktok,youtube
```

Outputs land in `output/<campaign>/<platform>/`, alongside a
`storyboard.json` artifact for marketing review.

## Adding content

- **Brand asset**: drop the file into `brand/assets/logos/`, `images/`,
  `fonts/`, or `audio/`. The first logo found is used as a watermark; brand
  fonts are picked up automatically.
- **Campaign**: add `campaigns/<name>.yaml` (see `campaigns/summer_sale.yaml`).
- **Template**: add `templates/<name>.yaml` defining scenes, placeholders, and
  duration weights.

Full schema reference: [docs/schemas.md](docs/schemas.md).

## Development

```bash
ruff check src tests   # lint
pytest -v              # tests (includes a video-render smoke test)
```

CI runs lint + tests on every PR. A manually-triggered workflow
(`workflow_dispatch`) renders every campaign and uploads the videos as
artifacts.
