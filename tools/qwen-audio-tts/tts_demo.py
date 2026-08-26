"""Qwen Audio 3.0 TTS Plus 场景试听脚本。"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import dashscope
from dashscope.audio.tts_v2 import AudioFormat, SpeechSynthesizer
from dotenv import load_dotenv


MODEL = "qwen-audio-3.0-tts-plus"
DEFAULT_VOICE = "longanlingxin"
DEFAULT_TEXT = (
    "您好，您的退款申请我已经核对完成。订单金额是二百九十九元，"
    "预计在一到三个工作日内原路退回。处理成功后，我们会第一时间通知您。"
    "感谢您的耐心等待！"
)
DEFAULT_INSTRUCTION = (
    "请使用温柔、耐心、专业的年轻女性客服语气，语速略慢；"
    "金额和时间范围读得清楚，先共情安抚，结尾轻快自然。"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="调用百炼 Qwen Audio 3.0 TTS Plus 生成 MP3")
    parser.add_argument("--text", default=DEFAULT_TEXT, help="待合成文本")
    parser.add_argument("--instruction", default=DEFAULT_INSTRUCTION, help="声音表现指令")
    parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        choices=("longanlingxin", "longanlufeng"),
        help="Plus 版系统音色",
    )
    parser.add_argument("--output", type=Path, default=Path("output/customer-service.mp3"))
    parser.add_argument("--speech-rate", type=float, default=0.95, help="语速，范围 0.5-2.0")
    parser.add_argument("--pitch-rate", type=float, default=1.0, help="音调，范围 0.5-2.0")
    parser.add_argument("--volume", type=int, default=55, help="音量，范围 0-100")
    return parser.parse_args()


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith(("sk-your-", "llm-your-")):
        raise RuntimeError(f"请先在 .env 中填写 {name}")
    return value


def validate_args(args: argparse.Namespace) -> None:
    if not 0.5 <= args.speech_rate <= 2.0:
        raise ValueError("--speech-rate 必须在 0.5 到 2.0 之间")
    if not 0.5 <= args.pitch_rate <= 2.0:
        raise ValueError("--pitch-rate 必须在 0.5 到 2.0 之间")
    if not 0 <= args.volume <= 100:
        raise ValueError("--volume 必须在 0 到 100 之间")
    if not args.text.strip():
        raise ValueError("--text 不能为空")


def synthesize(args: argparse.Namespace) -> Path:
    load_dotenv()
    validate_args(args)

    dashscope.api_key = require_env("DASHSCOPE_API_KEY")
    workspace_id = require_env("DASHSCOPE_WORKSPACE_ID")
    dashscope.base_websocket_api_url = (
        f"wss://{workspace_id}.cn-beijing.maas.aliyuncs.com/api-ws/v1/inference"
    )

    synthesizer = SpeechSynthesizer(
        model=MODEL,
        voice=args.voice,
        format=AudioFormat.MP3_22050HZ_MONO_256KBPS,
        volume=args.volume,
        speech_rate=args.speech_rate,
        pitch_rate=args.pitch_rate,
        instruction=args.instruction,
    )
    audio = synthesizer.call(args.text)
    if not audio:
        raise RuntimeError(f"接口未返回音频：{synthesizer.get_response()}")

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(audio)
    print(f"生成完成：{output}")
    print(f"Request ID：{synthesizer.get_last_request_id()}")
    print(f"首包延迟：{synthesizer.get_first_package_delay()} ms")
    return output


def main() -> int:
    try:
        synthesize(parse_args())
        return 0
    except (RuntimeError, ValueError) as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # DashScope SDK 会返回不同类型的网络/API 异常。
        print(f"合成失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


