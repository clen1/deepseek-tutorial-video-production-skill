"""Validate a rendered tutorial-video package on Windows.

This is deliberately dependency-light. It checks paths, UTF-8 text, SRT
ordering, likely secret leakage, common mojibake, and optional media durations
through a local ffmpeg binary. It does not modify project files.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


MOJIBAKE_MARKERS = ("锛", "璇", "瑙", "瀹", "娓", "鐨", "绔", "�")
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(
        r"(?i)(?:DASHSCOPE|OPENAI|ANTHROPIC|DEEPSEEK)_API_KEY\s*=\s*"
        r"(?![<`'\"]|$)[A-Za-z0-9_-]{20,}"
    ),
)
TIMESTAMP = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2}),(\d{3})$"
)


def parse_time(value: str) -> tuple[float, float]:
    match = TIMESTAMP.match(value.strip())
    if not match:
        raise ValueError(f"invalid SRT timestamp: {value}")
    h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
    start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
    end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000
    return start, end


def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def check_srt(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = read_utf8(path)
    except UnicodeDecodeError as exc:
        return [f"{path}: not valid UTF-8 ({exc})"]
    blocks = re.split(r"\n\s*\n", text.strip()) if text.strip() else []
    previous_end = -1.0
    previous_index = 0
    for block_no, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) < 3:
            errors.append(f"{path}: block {block_no} is incomplete")
            continue
        try:
            index = int(lines[0].strip())
            start, end = parse_time(lines[1])
        except (ValueError, IndexError) as exc:
            errors.append(f"{path}: block {block_no}: {exc}")
            continue
        if index != previous_index + 1:
            errors.append(f"{path}: block {block_no}: sequence is {index}, expected {previous_index + 1}")
        if start < previous_end:
            errors.append(f"{path}: block {block_no}: overlaps the previous subtitle")
        if end <= start:
            errors.append(f"{path}: block {block_no}: end is not after start")
        if not "".join(lines[2:]).strip():
            errors.append(f"{path}: block {block_no}: empty text")
        previous_index = index
        previous_end = end
    return errors


def find_ffmpeg(project_root: Path) -> Path | None:
    candidates = list(project_root.glob(".video_tools/imageio_ffmpeg/binaries/ffmpeg*.exe"))
    return candidates[0] if candidates else None


def media_duration(ffmpeg: Path | None, media: Path) -> float | None:
    if not ffmpeg:
        return None
    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(media)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    match = re.search(r"Duration:\s+(\d+):(\d+):(\d+\.\d+)", result.stderr)
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def scan_text(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    suffixes = {".py", ".srt", ".json", ".html", ".txt", ".md", ".yaml", ".yml"}
    ignored_parts = {".git", "node_modules", ".venv", "__pycache__", "segments"}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if any(part in ignored_parts for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            warnings.append(f"not UTF-8 text: {path}")
            continue
        if any(marker in text for marker in MOJIBAKE_MARKERS):
            warnings.append(f"possible mojibake: {path}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret in text file: {path}")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--audio", type=Path)
    parser.add_argument("--cover", type=Path)
    args = parser.parse_args()

    root = args.project_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    required = [args.video, args.srt]
    if args.audio:
        required.append(args.audio)
    if args.cover:
        required.append(args.cover)
    for raw in required:
        path = raw if raw.is_absolute() else root / raw
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing or empty artifact: {path}")

    srt = args.srt if args.srt.is_absolute() else root / args.srt
    if srt.exists():
        errors.extend(check_srt(srt))

    scan_errors, scan_warnings = scan_text(root)
    errors.extend(scan_errors)
    warnings.extend(scan_warnings)

    ffmpeg = find_ffmpeg(root)
    video = args.video if args.video.is_absolute() else root / args.video
    audio = args.audio if args.audio and args.audio.is_absolute() else (root / args.audio if args.audio else None)
    video_seconds = media_duration(ffmpeg, video) if video.exists() else None
    audio_seconds = media_duration(ffmpeg, audio) if audio and audio.exists() else None
    if video_seconds is not None and audio_seconds is not None and video_seconds + 0.05 < audio_seconds:
        errors.append(f"video is shorter than narration: video={video_seconds:.2f}s audio={audio_seconds:.2f}s")

    print(json.dumps({
        "project_root": str(root),
        "video_seconds": video_seconds,
        "audio_seconds": audio_seconds,
        "errors": errors,
        "warnings": warnings,
        "status": "fail" if errors else "pass",
    }, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
