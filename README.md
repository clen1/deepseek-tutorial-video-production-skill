# DeepSeek Tutorial Video Production Skill

面向 Codex 的中文软件教程视频制作 Skill。它把选题与素材整理为一套可复用的生产流程：分镜、旁白、分段 TTS、字幕、画面合成、FFmpeg 渲染、封面和质量检查。

## 适用场景

- 软件安装教程与产品功能演示
- 开发者工具、命令行和网页操作教学
- 横屏或竖屏的短视频教程
- 已有视频项目的配音、字幕、画面与发布资产修订

## 包含内容

- `SKILL.md`：完整工作流与执行规则
- `references/production-spec.md`：分镜字段、时长、字幕、编码和发布规范
- `scripts/validate_video_project.py`：视频、音频、字幕、封面和敏感信息检查器
- `examples/harness-windows-install-sample/`：可直接查看和重新渲染的轻量示例
- `agents/openai.yaml`：Skill 展示元数据

## 安装

将仓库克隆到 Codex 的个人 Skills 目录：

```powershell
git clone https://github.com/clen1/deepseek-tutorial-video-production-skill.git "$env:USERPROFILE\.codex\skills\deepseek-tutorial-video-production"
```

重新打开 Codex 后，可直接用自然语言调用，例如：

```text
请使用 deepseek-tutorial-video-production，制作一期 3 分钟的中文软件安装教程。
受众是第一次接触该工具的 Windows 用户，横屏 1280×720，需要旁白、字幕、封面和 QA 报告。
```

## 查看示例

示例目录已包含分镜、项目配置、SRT、QA 报告、故事板预览和短视频预览。重新生成故事板：

```powershell
python examples/harness-windows-install-sample/render_storyboard.py
```

## 校验项目

```powershell
python scripts/validate_video_project.py `
  --project-root D:\path\to\project `
  --video D:\path\to\final.mp4 `
  --srt D:\path\to\final.srt `
  --audio D:\path\to\narration.mp3 `
  --cover D:\path\to\cover.png
```

校验器依赖系统可执行的 `ffprobe`。根据实际渲染方式，你还可能需要 Python、Pillow、FFmpeg、Node.js、Remotion 或其他视频工具。

## 语音生成

本 Skill 不绑定某一家 TTS 服务。配套的阿里云 Qwen Audio 示例位于独立仓库：`clen1/qwen-audio-tts-examples`。真实 API Key 必须仅保存在本地 `.env`，不要提交到 Git。

## 发布安全

- 仓库不会包含本地 `projects/`、浏览器资料、虚拟环境、真实 `.env` 或生成的大型媒体。
- 在公开截图、旁白、字幕、日志和视频前，应再次检查令牌、个人路径、账号和隐私信息。
- 使用外部图片、音乐、字体和录屏前，请确认授权和署名要求。

## License

[MIT](LICENSE)

