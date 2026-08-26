"""批量生成 Qwen Audio 3.0 TTS Plus 情感测试音频。"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from threading import Event

import dashscope
from dashscope.audio.tts_v2 import AudioFormat, ResultCallback, SpeechSynthesizer
from dotenv import load_dotenv


MODEL = "qwen-audio-3.0-tts-plus"
OUTPUT_DIR = Path("output/emotion-suite")


@dataclass(frozen=True)
class Scenario:
    filename: str
    title: str
    emotion: str
    voice: str
    instruction: str
    text: str
    speech_rate: float = 1.0
    pitch_rate: float = 1.0
    volume: int = 55


SCENARIOS = (
    Scenario(
        filename="01-empathetic-refund.mp3",
        title="退款客服安抚",
        emotion="共情、耐心、安心",
        voice="longanlingxin",
        instruction="温柔耐心的年轻女性客服，先共情安抚，金额和时间读得清楚，结尾自然亲切。",
        text="[empathetic]您好，真的很抱歉让您久等了。退款申请已经处理完成，金额是二百九十九元，预计一到三个工作日原路到账。请您放心，我会继续帮您留意处理进度。",
        speech_rate=0.92,
    ),
    Scenario(
        filename="02-excited-promotion.mp3",
        title="促销活动播报",
        emotion="兴奋、热情、感染力",
        voice="longanlufeng",
        instruction="年轻活泼的活动主持人，情绪兴奋有感染力，节奏偏快，优惠数字要突出。",
        text="[excited]好消息！会员狂欢日正式开始！今天下单全场八折，前一百名顾客还有惊喜礼品！[laughing]快来参加吧，我们在直播间等你！",
        speech_rate=1.12,
        pitch_rate=1.06,
        volume=62,
    ),
    Scenario(
        filename="03-serious-alert.mp3",
        title="安全预警通知",
        emotion="严肃、冷静、权威",
        voice="longanlingxin",
        instruction="严肃冷静的公共安全播报，语速稳健，关键时间和动作要求加重并适当停顿。",
        text="[serious]请注意，今晚九点至明天早晨六点，本市将出现强降雨。低洼地区居民请提前转移车辆，远离河道，并密切关注最新预警信息。",
        speech_rate=0.9,
        pitch_rate=0.94,
        volume=60,
    ),
    Scenario(
        filename="04-sad-audiobook.mp3",
        title="悲伤有声书",
        emotion="悲伤、克制、怀念",
        voice="longanlingxin",
        instruction="有声书旁白，悲伤而克制，带一点怀念感，句间停顿较长，保持清晰。",
        text="[sad]列车缓缓离开站台，她望着越来越远的灯火，终于明白，这一次告别，也许要很多年以后才能重逢。",
        speech_rate=0.8,
        pitch_rate=0.95,
        volume=48,
    ),
    Scenario(
        filename="05-amazed-unboxing.mp3",
        title="惊喜开箱",
        emotion="好奇、惊讶、喜悦",
        voice="longanlufeng",
        instruction="开箱视频博主，先充满好奇，再突然惊喜，情绪转折要明显，表达自然。",
        text="[curious]这个小盒子里究竟装了什么？让我慢慢打开看看……[amazed]哇！居然是我找了很久的限定款！这个颜色也太漂亮了！",
        speech_rate=1.05,
        pitch_rate=1.08,
        volume=58,
    ),
    Scenario(
        filename="06-asmr-bedtime.mp3",
        title="睡前治愈陪伴",
        emotion="轻柔、耳语、治愈",
        voice="longanlingxin",
        instruction="轻柔治愈的睡前陪伴，接近耳语，语速缓慢，音量偏低，停顿自然。",
        text="[asmr]今天辛苦了。现在，慢慢放松肩膀，轻轻闭上眼睛。窗外的风很安静，你也可以安心地休息了。晚安。",
        speech_rate=0.72,
        pitch_rate=0.98,
        volume=38,
    ),
    Scenario(
        filename="07-angry-drama.mp3",
        title="愤怒剧情对白",
        emotion="愤怒、颤抖、压迫感",
        voice="longanlufeng",
        instruction="影视剧情对白，情绪强烈，从压抑的愤怒逐渐爆发，吐字仍需清楚。",
        text="[angry]你明明答应过我，会保护好这份资料！为什么到最后，所有人都要为你的决定承担后果？[trembling]告诉我，这究竟是为什么？",
        speech_rate=1.03,
        pitch_rate=0.94,
        volume=68,
    ),
    Scenario(
        filename="08-emotion-switch.mp3",
        title="多情绪快速切换",
        emotion="严肃转兴奋并加入笑声",
        voice="longanlufeng",
        instruction="同一段话内完成明显的情绪切换，前半段严肃克制，后半段兴奋轻快。",
        text="[serious]请大家保持安静，我现在要宣布本次比赛的最终结果。[excited]冠军已经产生，就是我们坚持到最后的蓝队！[laughing]恭喜你们！",
        speech_rate=1.0,
        pitch_rate=1.03,
        volume=60,
    ),
)


class FileCallback(ResultCallback):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.file = None
        self.error_message = ""
        self.done = Event()

    def on_open(self) -> None:
        self.file = self.path.open("wb")

    def on_complete(self) -> None:
        if self.file is not None:
            self.file.flush()
        self.done.set()

    def on_error(self, message: str) -> None:
        self.error_message = message
        self.done.set()

    def on_close(self) -> None:
        if self.file is not None:
            self.file.close()
            self.file = None

    def on_event(self, message: str) -> None:
        return None

    def on_data(self, data: bytes) -> None:
        if self.file is None:
            raise RuntimeError("音频输出文件尚未打开")
        self.file.write(data)


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith(("sk-your-", "llm-your-")):
        raise RuntimeError(f"请先在 .env 中填写 {name}")
    return value


def configure_dashscope() -> None:
    load_dotenv()
    dashscope.api_key = require_env("DASHSCOPE_API_KEY")
    workspace_id = require_env("DASHSCOPE_WORKSPACE_ID")
    dashscope.base_websocket_api_url = (
        f"wss://{workspace_id}.cn-beijing.maas.aliyuncs.com/api-ws/v1/inference"
    )


def generate_scenario(scenario: Scenario) -> dict[str, object]:
    path = (OUTPUT_DIR / scenario.filename).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    callback = FileCallback(path)
    synthesizer = SpeechSynthesizer(
        model=MODEL,
        voice=scenario.voice,
        format=AudioFormat.MP3_22050HZ_MONO_256KBPS,
        volume=scenario.volume,
        speech_rate=scenario.speech_rate,
        pitch_rate=scenario.pitch_rate,
        instruction=scenario.instruction,
        callback=callback,
    )

    synthesizer.call(scenario.text)
    if not callback.done.wait(timeout=90):
        raise RuntimeError("等待语音合成完成超时")
    if callback.error_message:
        raise RuntimeError(callback.error_message)
    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError("接口未生成有效音频文件")

    return {
        **asdict(scenario),
        "path": str(path),
        "bytes": path.stat().st_size,
        "request_id": synthesizer.get_last_request_id(),
        "first_package_delay_ms": synthesizer.get_first_package_delay(),
    }


def main() -> int:
    try:
        configure_dashscope()
        results = []
        for index, scenario in enumerate(SCENARIOS, start=1):
            print(f"[{index}/{len(SCENARIOS)}] 正在生成：{scenario.title}")
            result = generate_scenario(scenario)
            results.append(result)
            print(
                f"  完成：{scenario.filename}，{result['bytes']} bytes，"
                f"首包 {result['first_package_delay_ms']} ms"
            )

        manifest_path = (OUTPUT_DIR / "manifest.json").resolve()
        manifest_path.write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"全部完成：{OUTPUT_DIR.resolve()}")
        return 0
    except Exception as exc:
        print(f"生成失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

