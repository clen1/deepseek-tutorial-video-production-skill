# Production specification

## Segment record

Represent every narration/visual unit as a record. A Python dataclass or JSON object is preferred:

```json
{
  "slug": "female-08-launch",
  "title": "启动 Web UI",
  "narration": "记下官方命令……",
  "emotion": "confident",
  "instruction": "年轻自然的女性科技讲解员……",
  "speech_rate": 1.0,
  "visual": "terminal",
  "source": "npx @deepseek-ai/dsh web",
  "subtitle_policy": "clause",
  "duration_policy": "audio-plus-tail"
}
```

The slug is the cache key. Change it when the narration changes materially.

## Current Harness shot map

| # | Purpose | Preferred visual | Evidence |
|---:|---|---|---|
| 1 | Promise | title slide | tutorial scope |
| 2 | NVM concept | explanatory slide | Node Version Manager definition |
| 3 | NVM download | official screenshot | NVM homepage/download |
| 4 | Install NVM | terminal | `nvm version`, `nvm list`, `nvm install` |
| 5 | Switch Node | terminal | `nvm use`, `node --version`, `npm --version` |
| 6 | Harness concept | product intro slide | Agent/workspace/task relationship |
| 7 | Official entry | DeepSeek footer screenshot | Harness link |
| 8 | Official command | terminal | `npx @deepseek-ai/dsh web` |
| 9 | Open UI | browser capture/illustration | `127.0.0.1:3080` when real |
| 10 | Configure | real UI | workspace/model/key field; mask secrets |
| 11 | First task | real UI | create a file/task and show result |
| 12 | Close | end slide | “从自己的工作区开始探索，谢谢大家！” |

## Timing and subtitle heuristics

- Title: 3–5 seconds.
- Official screenshot: 4–7 seconds, enough time to identify the click target.
- Terminal command: 5–8 seconds, with a visible result.
- UI action: 5–10 seconds, split if there are more than two clicks.
- Closing slide: at least the complete final sentence plus 0.5–1 second of tail.

Generate SRT from the measured segment audio, not from guessed narration length. Split long segments into multiple subtitle events while keeping one segment MP3 if the narration itself is continuous. Use a separate final event for “谢谢大家！” when the visual needs a clean last beat.

## File and encoding rules on Windows

Use UTF-8 for `.py`, `.srt`, `.json`, `.html`, and text manifests. Set:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
```

Use a Chinese-capable font such as Microsoft YaHei (`msyh.ttc`/`msyhbd.ttc`) and a monospace font such as Consolas for commands. Avoid copying terminal output through a code page that turns Chinese into mojibake.

## Safety and publication rules

- Read API keys from a local `.env` only.
- Never put keys in a video, cover, SRT, HTML tutorial, manifest, or debug log.
- Mask keys in UI visuals, e.g. `sk-••••••••••••••••`.
- If a real key was exposed, revoke or rotate it before publication and regenerate all affected artifacts.
- Use official pages and commands where the video claims“官网”or“官方命令”.
- Do not claim a successful local Web UI run unless the URL and interaction were actually verified.
