"""Platform output specs and video encoding via ffmpeg."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PlatformSpec:
    name: str
    width: int
    height: int
    fps: int
    max_duration_seconds: int
    bitrate: str


PLATFORM_SPECS: dict[str, PlatformSpec] = {
    "youtube": PlatformSpec("youtube", 1920, 1080, 30, 120, "8M"),
    "tiktok": PlatformSpec("tiktok", 1080, 1920, 30, 60, "6M"),
    "instagram_reels": PlatformSpec("instagram_reels", 1080, 1920, 30, 90, "6M"),
    "instagram_feed": PlatformSpec("instagram_feed", 1080, 1080, 30, 60, "5M"),
    "shorts": PlatformSpec("shorts", 1080, 1920, 30, 60, "6M"),
}


def get_ffmpeg_exe() -> str:
    """Locate an ffmpeg binary, preferring the bundled imageio-ffmpeg one."""
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def encode_frames(frames_dir: Path, spec: PlatformSpec, out_path: Path) -> Path:
    """Encode a directory of numbered PNG frames into an MP4 video."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        get_ffmpeg_exe(),
        "-y",
        "-framerate",
        str(spec.fps),
        "-i",
        str(frames_dir / "frame_%05d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-b:v",
        spec.bitrate,
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path
