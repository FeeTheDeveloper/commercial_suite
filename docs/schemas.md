# Configuration Schemas

All configuration is YAML, validated with Pydantic at load time. Invalid
configs fail fast with a clear error before any rendering starts.

## Brand kit — `brand/brand.yaml`

| Key | Type | Required | Description |
| --- | --- | --- | --- |
| `company.name` | string | yes | Company name, used in intros/outros. |
| `company.tagline` | string | no | Short slogan. |
| `company.mission` | string | no | Mission statement, available to script generation. |
| `company.website` | string | no | Shown on CTA scenes. |
| `voice.tone` | list of strings | no | Tone descriptors passed to the LLM copywriter. |
| `voice.guidelines` | list of strings | no | Writing rules for generated copy. |
| `voice.banned_words` | list of strings | no | Copy containing these words is rejected. |
| `audiences` | list of `{name, description}` | no | Target audience definitions. |
| `palette.primary` / `secondary` / `accent` / `background` / `text` | hex color `#RRGGBB` | yes | Brand colors used for scene backgrounds and text. |
| `typography.heading_font` / `body_font` | path | no | TTF/OTF font paths; falls back to any font in `fonts_dir`, then a default font. |
| `assets.logos_dir` / `images_dir` / `fonts_dir` / `audio_dir` | path | no | Brand asset directories. |
| `legal.disclaimer` | string | no | Shown on outro scenes. |

### Brand assets

Drop files into the asset directories — no config changes needed:

- `brand/assets/logos/` — PNG/JPG/WebP logos. The first one (sorted) is used
  as a corner watermark on every scene.
- `brand/assets/images/` — approved photography/product shots.
- `brand/assets/fonts/` — licensed TTF/OTF fonts.
- `brand/assets/audio/` — music and voice assets.

## Campaign — `campaigns/<name>.yaml`

| Key | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | Campaign identifier (should match the filename). |
| `goal` | string | yes | What the campaign should achieve. |
| `message` | string | yes | Core message shown in the video. |
| `cta` | string | yes | Call to action. |
| `template` | string | yes | Template name (`templates/<template>.yaml`). |
| `audience` | string | no | Audience name from the brand kit. |
| `platforms` | list of strings | yes | Any of: `youtube`, `tiktok`, `instagram_reels`, `instagram_feed`, `shorts`. |
| `duration_seconds` | int (5–120) | no | Target video length; default 15. Must not exceed the platform maximum. |

## Template — `templates/<name>.yaml`

| Key | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | Template identifier. |
| `description` | string | no | Human-readable summary. |
| `scenes` | list | yes (≥1) | Ordered scene definitions. |
| `scenes[].role` | string | yes | Scene role, e.g. `intro`, `message`, `cta`, `outro`. |
| `scenes[].heading` | string | no | Headline text; supports placeholders (below). |
| `scenes[].body` | string | no | Supporting text; supports placeholders. |
| `scenes[].background` | string | no | Palette key: `primary`, `secondary`, `accent`, `background`, or `text`. |
| `scenes[].duration_weight` | number > 0 | no | Relative share of the campaign duration; default 1. |

### Placeholders

Headings and bodies may reference brand/campaign values:

`{company_name}`, `{tagline}`, `{mission}`, `{website}`, `{message}`,
`{goal}`, `{cta}`, `{disclaimer}`

## Platform specs

| Platform | Resolution | Aspect | FPS | Max duration |
| --- | --- | --- | --- | --- |
| `youtube` | 1920×1080 | 16:9 | 30 | 120s |
| `tiktok` | 1080×1920 | 9:16 | 30 | 60s |
| `instagram_reels` | 1080×1920 | 9:16 | 30 | 90s |
| `instagram_feed` | 1080×1080 | 1:1 | 30 | 60s |
| `shorts` | 1080×1920 | 9:16 | 30 | 60s |
