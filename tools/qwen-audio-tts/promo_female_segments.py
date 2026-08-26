"""为 TabMind 宣传片生成逐功能对齐的阿里女声片段。"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import dashscope
from dashscope.audio.tts_v2 import AudioFormat, SpeechSynthesizer
from dotenv import load_dotenv


MODEL = "qwen-audio-3.0-tts-plus"
VOICE = "longanlingxin"
OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "tabmind-video" / "female-sync"

BASE_INSTRUCTION = (
    "年轻自然的女性科技产品讲解员，声音清晰温暖、有活力；"
    "功能介绍自信有节奏，重点适度重读，停顿自然，避免客服腔和机械播报。"
)

SEGMENTS = (
    {
        "id": "01",
        "title": "使用场景",
        "text": "[curious]每天打开几十个网页，重要资料很快就会挤在标签栏里。TabMind 帮你把它们重新整理清楚。",
    },
    {
        "id": "02",
        "title": "仪表盘",
        "text": "[excited]打开全屏管理页，今日记录、当前打开、待分类和重复页面，一次就能看清。",
    },
    {
        "id": "03",
        "title": "分类目录",
        "text": "[serious]左侧目录显示每个分类的数量。点击分类后，选中状态会清晰保留。",
    },
    {
        "id": "04",
        "title": "记录详情",
        "text": "[curious]打开记录详情，可以查看网址、AI 摘要、标签、访问次数和浏览器状态。",
    },
    {
        "id": "05",
        "title": "稍后阅读与归档",
        "text": "[empathetic]需要以后处理的内容放入稍后阅读，完成的资料进入已归档，查找更加直接。",
    },
    {
        "id": "06",
        "title": "导出记录",
        "text": "[excited]整理后的记录支持导出。HTML 保留搜索和筛选，CSV 可以直接使用 Excel 打开。",
    },
    {
        "id": "07",
        "title": "DeepSeek 设置",
        "text": "[serious]在设置页面配置 DeepSeek 的 API Key、接口地址和模型名称。密钥只保存在当前浏览器本地。",
    },
    {
        "id": "08",
        "title": "简约模式",
        "text": "[amazed]需要轻量操作时，一键切换简约模式，在右侧面板完成同步、分类、保存和整理。",
    },
    {
        "id": "09",
        "title": "结尾",
        "text": "[excited]TabMind，让每天打开的网页更容易整理、查找和再次使用。现在就开始整理吧！",
    },
)


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"缺少环境变量：{name}")
    return value


def srt_timestamp(seconds: float) -> str:
    total_ms = max(0, round(seconds * 1000))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def audio_duration(path: Path) -> float:
    ffprobe = os.getenv("FFPROBE_PATH", "").strip() or shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError(
            "找不到 ffprobe。请安装 FFmpeg 并加入 PATH，或设置 FFPROBE_PATH。"
        )
    result = subprocess.check_output(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    )
    return float(result.strip())


def main() -> None:
    load_dotenv(Path(__file__).resolve().parent / ".env")
    dashscope.api_key = require_env("DASHSCOPE_API_KEY")
    workspace_id = require_env("DASHSCOPE_WORKSPACE_ID")
    dashscope.base_websocket_api_url = (
        f"wss://{workspace_id}.cn-beijing.maas.aliyuncs.com/api-ws/v1/inference"
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, object]] = []
    for index, segment in enumerate(SEGMENTS, start=1):
        audio_path = OUTPUT_DIR / f"{segment['id']}.mp3"
        synthesizer = SpeechSynthesizer(
            model=MODEL,
            voice=VOICE,
            format=AudioFormat.MP3_22050HZ_MONO_256KBPS,
            volume=62,
            speech_rate=1.12,
            pitch_rate=1.04,
            instruction=BASE_INSTRUCTION,
        )
        print(f"[{index}/{len(SEGMENTS)}] {segment['title']}")
        audio = synthesizer.call(str(segment["text"]))
        if not audio:
            raise RuntimeError(f"{segment['title']} 合成失败：{synthesizer.get_response()}")
        audio_path.write_bytes(audio)
        duration = audio_duration(audio_path)

        subtitle_text = str(segment["text"]).split("]", 1)[-1]
        srt_path = OUTPUT_DIR / f"{segment['id']}.srt"
        srt_path.write_text(
            "1\n"
            f"00:00:00,200 --> {srt_timestamp(duration + 0.2)}\n"
            f"{subtitle_text}\n",
            encoding="utf-8",
        )
        manifest.append(
            {
                **segment,
                "subtitle": subtitle_text,
                "audio": str(audio_path),
                "srt": str(srt_path),
                "duration": duration,
                "segment_duration": duration + 0.6,
            }
        )

    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"完成：{OUTPUT_DIR}")


if __name__ == "__main__":
    main()

