# DeepSeek Harness Windows 教程示例模板

这是 `deepseek-tutorial-video-production` skill 的最小可运行故事板模板。它展示 12 镜头结构、画面字段、字幕节奏、manifest 结构与可视化预览，但不冒充已经完成的安装实录。

## 文件

- `project.json`：项目级参数；
- `shot-list.json`：12 个镜头的可复用记录；
- `render_storyboard.py`：Pillow 故事板/预览帧渲染器；
- `output/storyboard-preview.png`：12 镜头总览；
- `output/template-preview.mp4`：24 秒无声结构预览；
- `output/template-preview.srt`：与预览视频同步的示例字幕；
- `output/manifest.preview.json`：预览片段 manifest；
- `output/qa-report.md`：本次样例生成检查。

## 重新生成

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python render_storyboard.py
ffmpeg -y -framerate 1/2 -start_number 1 -i output/frames/frame-%02d.png -r 24 -c:v libx264 -pix_fmt yuv420p -movflags +faststart output/template-preview.mp4
```

正式生产时，把 `shot-list.json` 中的 `source` 替换为真实截图、录屏或命令输出；根据实测分段音频时长重新生成字幕和场景持续时间。示例中的 API Key 始终使用掩码，不得替换成真实密钥。
