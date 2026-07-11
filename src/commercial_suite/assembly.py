"""Video assembly: render storyboard scenes into frames with Pillow."""

from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import BrandKit
from .render import PLATFORM_SPECS, PlatformSpec, encode_frames
from .scriptgen import Storyboard


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _load_font(font_path: Path | None, size: int) -> ImageFont.ImageFont:
    if font_path is not None and font_path.is_file():
        try:
            return ImageFont.truetype(str(font_path), size=size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    color: tuple[int, int, int],
    width: int,
    y: int,
    wrap_chars: int,
) -> int:
    """Draw wrapped, horizontally centered text starting at y; return next y."""
    for line in textwrap.wrap(text, width=wrap_chars) or [""]:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        draw.text(((width - line_width) / 2, y), line, font=font, fill=color)
        y += int(line_height * 1.4)
    return y


def render_scene_image(
    scene_heading: str,
    scene_body: str,
    background_hex: str,
    text_hex: str,
    spec: PlatformSpec,
    heading_font_path: Path | None = None,
    body_font_path: Path | None = None,
    logo_path: Path | None = None,
) -> Image.Image:
    """Compose a single scene as a still image sized for the platform."""
    image = Image.new("RGB", (spec.width, spec.height), _hex_to_rgb(background_hex))
    draw = ImageDraw.Draw(image)
    text_color = _hex_to_rgb(text_hex)

    heading_size = max(spec.width, spec.height) // 20
    body_size = heading_size // 2
    heading_font = _load_font(heading_font_path, heading_size)
    body_font = _load_font(body_font_path, body_size)

    y = int(spec.height * 0.35)
    y = _draw_centered_text(draw, scene_heading, heading_font, text_color, spec.width, y, 24)
    if scene_body:
        y += body_size
        _draw_centered_text(draw, scene_body, body_font, text_color, spec.width, y, 40)

    if logo_path is not None and logo_path.is_file():
        logo = Image.open(logo_path).convert("RGBA")
        logo_width = spec.width // 10
        ratio = logo_width / logo.width
        logo_height = int(logo.height * ratio)
        # Skip logos with extreme aspect ratios that would render unusably small.
        if logo_height >= 8:
            logo = logo.resize((logo_width, logo_height))
            margin = spec.width // 40
            image.paste(logo, (spec.width - logo.width - margin, margin), logo)

    return image


def assemble_video(
    storyboard: Storyboard,
    brand: BrandKit,
    platform: str,
    output_dir: Path,
    frames_dir: Path,
    heading_font_path: Path | None = None,
    body_font_path: Path | None = None,
    logo_path: Path | None = None,
) -> Path:
    """Render every storyboard scene to frames and encode the platform video."""
    spec = PLATFORM_SPECS[platform]
    frames_dir.mkdir(parents=True, exist_ok=True)

    total_seconds = sum(s.duration_seconds for s in storyboard.scenes)
    if total_seconds > spec.max_duration_seconds:
        raise ValueError(
            f"Storyboard runs {total_seconds:.1f}s but {platform} allows at most "
            f"{spec.max_duration_seconds}s"
        )

    palette = brand.palette.model_dump()
    frame_index = 0
    for scene in storyboard.scenes:
        image = render_scene_image(
            scene.heading,
            scene.body,
            palette[scene.background],
            brand.palette.text,
            spec,
            heading_font_path=heading_font_path,
            body_font_path=body_font_path,
            logo_path=logo_path,
        )
        frame_count = max(1, round(scene.duration_seconds * spec.fps))
        for _ in range(frame_count):
            image.save(frames_dir / f"frame_{frame_index:05d}.png")
            frame_index += 1

    out_path = output_dir / f"{storyboard.campaign}_{platform}.mp4"
    return encode_frames(frames_dir, spec, out_path)
