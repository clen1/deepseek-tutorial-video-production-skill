# Qwen Audio 3.0 TTS Plus 中文语音示例

该项目调用阿里云百炼北京地域的 `qwen-audio-3.0-tts-plus`，包含单段生成、八类情感对比和宣传片分段配音三套示例。

## 运行

1. 创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

2. 复制环境变量模板，在本地 `.env` 中填入华北 2（北京）地域的百炼 API Key 与 Workspace ID：

```powershell
Copy-Item .env.example .env
```

3. 生成默认试听文件：

```powershell
.\.venv\Scripts\python.exe tts_demo.py
```

成功后音频位于 `output/customer-service.mp3`。

## 切换音色或文本

Plus 版当前提供两个系统音色：

- `longanlingxin`：知心温暖音，适合客服、陪伴场景。
- `longanlufeng`：明亮开朗音，适合活动通知、产品介绍。

示例：

```powershell
.\.venv\Scripts\python.exe tts_demo.py --voice longanlufeng --text "会员日活动开始啦，今天下单可享八折优惠！"
```

可用 `--instruction` 调整情绪、角色、语速与风格，使用 `python tts_demo.py --help` 查看全部参数。

## 批量情感测试

运行以下命令，会生成八个情感对比场景：共情客服、兴奋促销、严肃预警、悲伤有声书、惊喜开箱、ASMR 睡前陪伴、愤怒对白和多情绪切换。

```powershell
.\.venv\Scripts\python.exe emotion_suite.py
```

音频与请求指标保存在 `output/emotion-suite/`，其中 `manifest.json` 记录每段音频的音色、指令、文本、文件大小、Request ID 和首包延迟。

## 宣传片分段配音

`promo_female_segments.py` 演示如何批量生成逐功能对齐的旁白、单段 SRT 和时间清单：

```powershell
.\.venv\Scripts\python.exe promo_female_segments.py
```

该脚本需要 `ffprobe` 计算时长。请将 FFmpeg 加入 `PATH`，或设置 `FFPROBE_PATH` 指向本机的 `ffprobe.exe`。

## 安全说明

- `.env`、`.venv/` 和 `output/` 已被 Git 忽略。
- 只提交 `.env.example`，不要把真实 API Key、Workspace ID、Request ID 或生成日志提交到公开仓库。
- 音频生成会调用阿里云服务并可能产生费用，请在使用前确认账号配额与计费规则。

## License

本目录随仓库根目录的 [MIT License](../../LICENSE) 发布。

