from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
FRAMES = OUTPUT / "frames"
WIDTH, HEIGHT = 1280, 720


def font_path(bold: bool = False, mono: bool = False) -> str:
    candidates = []
    if mono:
        candidates.extend([
            Path(r"C:\Windows\Fonts\consola.ttf"),
            Path(r"C:\Windows\Fonts\CascadiaMono.ttf"),
        ])
    elif bold:
        candidates.extend([
            Path(r"C:\Windows\Fonts\msyhbd.ttc"),
            Path(r"C:\Windows\Fonts\simhei.ttf"),
        ])
    else:
        candidates.extend([
            Path(r"C:\Windows\Fonts\msyh.ttc"),
            Path(r"C:\Windows\Fonts\simsun.ttc"),
        ])
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    raise FileNotFoundError("未找到可用的中文字体")


def font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_path(bold=bold, mono=mono), size=size)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for char in paragraph:
            candidate = current + char
            if current and draw.textlength(candidate, font=fnt) > max_width:
                lines.append(current)
                current = char
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines


def gradient_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        for x in range(WIDTH):
            u = x / max(1, WIDTH - 1)
            pixels[x, y] = (
                int(7 + 5 * t),
                int(19 + 11 * t + 4 * u),
                int(42 + 22 * t + 10 * u),
            )
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(0, WIDTH, 64):
        draw.line((x, 0, x, HEIGHT), fill=(61, 144, 255, 18), width=1)
    for y in range(0, HEIGHT, 64):
        draw.line((0, y, WIDTH, y), fill=(61, 144, 255, 18), width=1)
    draw.ellipse((780, -300, 1420, 340), fill=(13, 170, 255, 28))
    return image


def render_frame(shot: dict, index: int, total: int) -> Image.Image:
    image = gradient_background()
    draw = ImageDraw.Draw(image, "RGBA")
    title_font = font(48, bold=True)
    body_font = font(27)
    label_font = font(18, bold=True)
    meta_font = font(21)
    mono_font = font(24, mono=True)

    rounded(draw, (66, 48, 350, 88), 20, (15, 122, 255, 45), (84, 189, 255, 110), 1)
    draw.text((88, 58), f"TUTORIAL TEMPLATE  ·  {index:02d}/{total:02d}", font=label_font, fill=(169, 224, 255, 255))

    draw.text((66, 130), shot["title"], font=title_font, fill=(245, 250, 255, 255))
    draw.line((66, 203, 280, 203), fill=(52, 203, 255, 230), width=4)

    rounded(draw, (66, 242, 764, 558), 28, (10, 27, 55, 205), (72, 153, 220, 95), 2)
    draw.text((100, 276), "旁白 / SUBTITLE", font=label_font, fill=(83, 202, 255, 255))
    y = 320
    for line in wrap_text(draw, shot["narration"], body_font, 620)[:4]:
        draw.text((100, y), line, font=body_font, fill=(231, 241, 250, 255))
        y += 45

    rounded(draw, (804, 242, 1214, 558), 28, (12, 36, 70, 210), (72, 153, 220, 95), 2)
    draw.text((840, 276), "画面类型", font=label_font, fill=(83, 202, 255, 255))
    rounded(draw, (840, 316, 1174, 364), 15, (24, 108, 179, 70), (67, 179, 255, 120), 1)
    draw.text((860, 326), shot["visual"], font=meta_font, fill=(224, 244, 255, 255))
    draw.text((840, 395), "来源 / 命令", font=label_font, fill=(83, 202, 255, 255))
    y2 = 434
    source_font = mono_font if shot["visual"] == "terminal" else meta_font
    for line in wrap_text(draw, shot["source"], source_font, 330)[:4]:
        draw.text((840, y2), line, font=source_font, fill=(226, 237, 247, 255))
        y2 += 34

    rounded(draw, (66, 610, 1214, 668), 20, (8, 21, 44, 210), (53, 121, 180, 70), 1)
    footer = "示例故事板 · 正式成片请替换为真实截图、命令输出或录屏"
    draw.text((92, 626), footer, font=meta_font, fill=(151, 181, 207, 255))
    draw.text((1090, 626), "2.0s", font=meta_font, fill=(80, 211, 255, 255))
    return image


def timestamp(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, rem = divmod(milliseconds, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(shots: Iterable[dict], seconds_per_shot: float) -> None:
    blocks = []
    for index, shot in enumerate(shots, start=1):
        start = (index - 1) * seconds_per_shot
        end = index * seconds_per_shot - 0.04
        blocks.append(
            f"{index}\n{timestamp(start)} --> {timestamp(end)}\n{shot['subtitle_text']}\n"
        )
    (OUTPUT / "template-preview.srt").write_text("\n".join(blocks), encoding="utf-8")


def write_manifest(shots: list[dict], seconds_per_shot: float) -> None:
    manifest = {
        "kind": "storyboard-preview",
        "audio": None,
        "note": "结构预览无旁白；正式成片须用实测音频重算时长。",
        "segments": [
            {
                **shot,
                "index": index,
                "start_seconds": (index - 1) * seconds_per_shot,
                "duration_seconds": seconds_per_shot,
                "frame": f"frames/frame-{index:02d}.png",
            }
            for index, shot in enumerate(shots, start=1)
        ],
    }
    (OUTPUT / "manifest.preview.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def make_contact_sheet(frames: list[Image.Image]) -> None:
    thumb_w, thumb_h = 384, 216
    gap, top = 32, 86
    sheet = Image.new("RGB", (1280, 1040), (6, 16, 34))
    draw = ImageDraw.Draw(sheet, "RGBA")
    draw.text((32, 24), "DeepSeek Harness · 12 镜头故事板模板", font=font(30, bold=True), fill=(240, 248, 255, 255))
    draw.text((1000, 30), "16:9 / 24 fps", font=font(18), fill=(104, 202, 255, 255))
    for i, frame in enumerate(frames):
        row, col = divmod(i, 3)
        x = gap + col * (thumb_w + gap)
        y = top + row * (thumb_h + 30)
        thumb = frame.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x, y))
        draw.text((x + 10, y + 188), f"{i + 1:02d}", font=font(18, bold=True), fill=(255, 255, 255, 255))
    sheet.save(OUTPUT / "storyboard-preview.png", quality=95)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    shots = json.loads((ROOT / "shot-list.json").read_text(encoding="utf-8"))
    project = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
    seconds_per_shot = float(project["preview"]["seconds_per_shot"])
    frames = []
    for index, shot in enumerate(shots, start=1):
        frame = render_frame(shot, index, len(shots))
        frame.save(FRAMES / f"frame-{index:02d}.png")
        frames.append(frame)
    make_contact_sheet(frames)
    write_srt(shots, seconds_per_shot)
    write_manifest(shots, seconds_per_shot)
    print(f"Rendered {len(shots)} frames to {OUTPUT}")


if __name__ == "__main__":
    main()
