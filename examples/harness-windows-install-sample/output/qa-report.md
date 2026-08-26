# QA report — Harness Windows install sample

- Generated: 2026-08-19 (Asia/Shanghai)
- Scope: storyboard/template preview only; no narration was requested or synthesized.
- Python renderer compile: pass.
- Frames: pass — 12 PNG frames, 1280×720.
- Storyboard contact sheet: pass — all 12 shots visible; Chinese font rendering inspected.
- Preview video: pass — H.264, 1280×720, 24 fps, 24.00 seconds.
- Audio: intentionally absent; this is labeled as a silent structure preview.
- SRT: pass — 12 ordered UTF-8 blocks, monotonic and non-overlapping, ending at 23.960 seconds.
- Manifest: pass — 12 segments with slug, narration, visual type, source, timing policy and preview frame path.
- Secret scan: pass — no literal API key; only a masked placeholder is present.
- Mojibake scan: pass — no known garbled-Chinese markers found.
- Final-frame visual check: pass — closing frame remains visible through the end of the preview.
- Bundled validator: pass with zero errors and zero warnings.
- Note: the bundled validator did not report media duration because this sample directory does not contain its optional local ffmpeg bundle; independent `ffprobe` verification reported 24.000 seconds.

Publication status: **not publishable as an installation proof** until placeholder screenshots and UI cards are replaced with verified evidence, narration is generated, and audio-driven timing is rerendered.
