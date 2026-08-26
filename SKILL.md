---
name: deepseek-tutorial-video-production
description: Produce polished Chinese software tutorial videos from a brief, local screenshots, browser recordings, terminal outputs, and narration assets; orchestrate script writing, segmented female TTS, timed subtitles, screen/slide composition, real command demos, ffmpeg rendering, QA, cover generation, and delivery. Use when Codex needs to make, revise, or batch-produce an installation guide, product walkthrough, developer tutorial, or short-form software demo video.
---

# Tutorial Video Production

Turn a software walkthrough into a reliable, watchable video package. Prefer a real, reproducible demonstration over decorative mockups; when a real integration cannot be run, label the visual honestly as an interface illustration or recorded product walkthrough.

## Deliverables

Produce these artifacts unless the user asks for fewer:

- final MP4, usually 1280×720 at 24 fps for landscape tutorials;
- UTF-8 SRT with short, timed subtitle blocks;
- concatenated narration MP3 and per-segment MP3 files;
- `manifest.json` containing segment text, voice, timing, and output paths;
- cover image when the user asks for publishing assets (usually 9:16 and/or 16:9);
- a compact QA report listing render, subtitle, audio, secret-scan, and visual checks.

Keep temporary frames and intermediate renders in a project output directory. Do not overwrite an existing final asset without an explicit replacement request; version the filename instead.

## Trigger and intake

When the request is a new video or a revision, extract:

1. subject, audience, platform, aspect ratio, target duration, and language;
2. required sites, commands, UI actions, and final call-to-action;
3. available screenshots, recordings, project files, fonts, and APIs;
4. narration preference. For Chinese tutorials, default to a warm, clear female voice unless the user specifies otherwise;
5. sensitive values. Ask the user to put keys in a local `.env`; never put a real key in narration, subtitles, HTML, screenshots, logs, prompts, or the final video.

If the workspace already contains a working renderer, inspect and reuse it before creating another pipeline. Typical reusable pieces are:

- an existing Pillow, Remotion, MoviePy, or ffmpeg renderer;
- a narration script that produces segmented audio, subtitles, scene timing, and QA frames;
- `assets/` for official screenshots and cover images;
- `video_frames/` for captured or prepared demonstration frames.

Use the browser-control skill when a live page must be opened, clicked, or captured. Use the image-generation skill for a brand-new raster cover; do not recreate a requested generated cover with HTML/CSS components.

## Standard production sequence

### 1. Build a shot list before coding

Use 8–12 segments for a 2–3 minute tutorial. Each segment should contain:

```text
slug, title, narration, emotion/instruction, speech_rate,
visual type, source asset or command, duration policy, subtitle text
```

Use this proven order for installation-and-first-use videos:

1. title and promise;
2. what the prerequisite tool does;
3. open the official download page;
4. install or verify the prerequisite;
5. switch the required runtime version and print real versions;
6. introduce the product and its role;
7. open the official product entry point;
8. show the official install/start command;
9. open the local Web UI or recorded product screen;
10. configure a provider/model with a masked example key;
11. send a real first task and show the result;
12. summarize, invite exploration, and close.

Keep one instructional idea per segment. Do not stuff all narration into the opening slide.

### 2. Capture evidence and real outputs

For official pages, use the official homepage and the specific download/install section. Capture the element that the narration names, not a random page. Prefer local screenshots with a visible browser frame only when it helps orientation.

For terminal steps, run the commands in the target environment and record their output. For the NVM/Node flow, verify at minimum:

```powershell
nvm version
nvm list
nvm use <version>
node --version
npm --version
```

For a product launch, use the official command from the product page and preserve the command exactly. If it opens a local UI, show the real URL and a real browser interaction. If the package or network cannot run, do not pretend it did: use a clearly labeled visual demonstration and state the limitation in the production notes, not as a fake terminal success.

### 3. Write narration for speech, not for a document

Use plain Chinese, short sentences, explicit pauses, and spoken descriptions of clicks. Read commands slowly and keep punctuation around them. For a female Aliyun voice, use `qwen-audio-3.0-tts-plus` with `longanlingxin` and an instruction equivalent to:

```text
年轻自然的女性科技讲解员，声音清晰温暖，有轻微活力；像在屏幕前带新手操作；重点词适度重读，停顿自然，避免客服腔和机械播报。
```

Use emotional tags only inside the TTS source text and strip them from subtitles. Reuse an existing segment MP3 when the slug and text are unchanged. If the text changes, change the slug or invalidate the old cache.

Never synthesize a literal secret. Use phrases such as“粘贴你自己的 API Key”，and show a masked placeholder in visuals.

### 4. Generate segmented subtitles

Split subtitles by clause and action, not by arbitrary time. A readable block should normally contain one sentence or one command/result pair. Keep each block short enough to fit the established video style; for the current renderer, use an approximate visual-width limit of 42 units, with Latin command tokens counted wider than a Chinese character.

Write SRT as UTF-8 with BOM only if the target editor requires it; otherwise plain UTF-8 is preferred. Validate sequence order, non-overlap, monotonic timestamps, and the final subtitle ending after the final spoken sentence. Never use one giant subtitle block for a whole scene.

### 5. Compose visuals in the established style

Use the current visual language unless the user asks for a new brand direction:

- dark blue gradient and restrained blueprint grid;
- white/cyan section titles and blue glass panels;
- official screenshots inside clean framed cards;
- terminal commands in a monospace font;
- one visual focus per slide;
- enough empty space for subtitles.

Use real screenshots for official sites and real command output for environment checks. Generated visuals are appropriate for cover art or an explicitly labeled product-interface illustration, not for falsifying a successful installation.

### 6. Render without cutting audio

Static scenes must produce at least the requested duration in frames. Use `ceil(seconds * FPS)` rather than `int(seconds * FPS)` and provide a helper like:

```python
def repeat_exact(image, seconds, fps=24):
    for _ in range(max(1, math.ceil(seconds * fps))):
        yield image.convert("RGB")
```

The final frame must remain on screen through the end of the closing narration. If a video is audio-driven, compare video duration with audio duration and add a small visual tail rather than relying on a truncated `-shortest` output. After rendering, extract an early, middle, command, UI, and final frame for inspection.

### 7. Validate encoding and visible text

Before delivery:

- compile Python renderers;
- verify every referenced image, font, audio, and output path;
- scan text sources for mojibake markers such as `锛`, `璇`, `瑙`, `瀹`, `娓`, `鐨`, `绔`, or replacement characters;
- explicitly set `PYTHONIOENCODING=utf-8` for Windows subprocesses;
- render or view representative frames, including the last 2–3 seconds;
- verify subtitles are legible, segmented, and not behind the player controls;
- ensure narration is female/clear if requested and no debugging labels such as“女声讲解” appear on screen;
- check that the final video duration is not shorter than the narration;
- run `scripts/validate_video_project.py` against the final package.

### 8. Generate publishing assets separately

For a cover, use the image-generation skill directly. Ask for the platform ratio and use the video’s actual subject, not generic AI imagery. For this workflow, useful copy is short and factual, such as `DeepSeek Harness`, `Windows 安装与首次使用`, or `从 NVM 到第一个任务`. Keep generated cover text minimal and inspect it for legibility. Save the selected output inside the project `assets/` directory.

## Fast revision rules

- Subtitle too dense: split the narration at a clause boundary and regenerate only affected TTS segments.
- Audio cut off: preserve cached audio, increase static-scene frame counts with `ceil`, rerender, and inspect the final frames.
- Garbled Chinese: fix source encoding and font selection; do not“repair” the rendered screenshot by adding more text layers.
- Generic or fake demo: replace it with a real command/output capture, or label the illustration honestly.
- Leaked key: stop publication, redact every artifact, rotate/revoke the key, and regenerate affected audio, subtitles, screenshots, and video.
- Cover looks generic: regenerate through image generation with a more specific composition based on the actual video workflow; do not fall back to component-built poster art when the user asked for a generated cover.

## Completion handoff

Report the final MP4, SRT, narration, manifest, cover, and QA result as clickable absolute paths. State what was actually demonstrated and clearly separate real local output from illustrative UI. Mention any unresolved network, account, or API dependency instead of hiding it.

For detailed segment fields, timing rules, and the current Harness example, read [production-spec.md](references/production-spec.md). Run the bundled validator with:

```powershell
python scripts/validate_video_project.py --project-root D:\path\to\project --video <final.mp4> --srt <final.srt> --audio <narration.mp3> --cover <cover.png>
```

## Bundled example template

For a runnable 12-shot Harness Windows tutorial storyboard, use [the sample template](examples/harness-windows-install-sample/README.md). It includes project settings, a complete shot list, a Pillow renderer, a 24-second silent structure preview, synchronized preview subtitles, a manifest, and a QA report. Treat the preview as a planning artifact: replace placeholders with verified screenshots, real command output, measured narration, and real UI recordings before publication.
