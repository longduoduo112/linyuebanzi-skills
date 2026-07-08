---
name: linyuebanzi-teaching-animation
description: 把单个学科概念(中文/英文都行,如"声现象""杠杆原理""光合作用")自动做成教学动图和/或带配音的教学视频。两条管线:① Manim 动图 → MP4(1080p60) + GIF(720p,<2MB,公众号内嵌) + 7 场景蒙太奇;② HyperFrames 教学视频 → 分镜脚本 + Minimax TTS 中文配音 + 字幕 + 完整 MP4。同一概念共用一份 7 段分镜和同一套主题配色(声/光/力/电/热/生物/数学各有色系),GIF 和视频风格统一。当用户提"教学动图""教学动画""教学视频""配音视频""manim""concept → animation"或给一个学科概念要做成动态内容时,使用本 skill。
---

# Teaching Animation (Manim 动图 + 配音教学视频)

## 概述

输入一个概念 (例 "声现象") → 按需求产出:

| 管线 | 产物 | 工具链 |
|---|---|---|
| **动图** | `<topic>.mp4` (1080p60) + `<topic>.gif` (720p 20fps <2MB) + 蒙太奇 | Manim Community |
| **视频** | 带中文配音 + 字幕的 MP4 (1920×1080 30fps) + 蒙太奇 | Minimax TTS + HyperFrames |

两条管线共用: **7 段结构** (1 标题 + 5 子概念 + 1 总结)、**同一套主题配色**
(`references/color-palettes.md`)、**同一份分镜脚本** (`references/storyboard-guide.md`)。

## 触发路由

| 用户说 | 做什么 |
|---|---|
| "做一个声现象的教学动图" | 只跑动图管线 |
| "做一个声现象的教学视频" / 提到配音、旁白 | 只跑视频管线 |
| "动图和视频都要" | 先写一份 storyboard, 两条管线都跑 |

不确定时, **先问清楚概念 + 适用学段 (默认初二物理)**, 其他别问。

## 第 0 步 (两条管线共用): 写分镜

按 `references/storyboard-guide.md` 把概念拆成 7 段, 写 `storyboard.json`:
每段含 title / narration (旁白 30-50 字, 口语化, 不读公式) / visual (画面描述) / transition。
拆解质量决定一切 — 对照教材知识点, 参考 `examples/sound_phenomena.py` 的拆法。
配色按主题族选 (`references/color-palettes.md`), **同一概念两条管线用同一套色值**。

## 管线 A: Manim 动图

```bash
# 1. 复制模板
cp assets/template.py /path/to/project/<topic>.py

# 2. 编辑 <topic>.py, 改 4 处:
#    a) class ExampleTopic → class <TopicName>
#    b) CHAPTER_TEXT = "初二物理·第X章"
#    c) THEME_ICON = "sound" / "light" / "mechanics" / "electricity"
#    d) 配色块 + 7 个 sceneN_xxx() 场景内容

# 3. 渲染 (mp4 + gif + 蒙太奇一条龙)
bash scripts/render.sh <topic>.py <TopicName> qh
```

**场景内容必须按 `references/scene-recipes.md` 的配方写** — 先判断子概念类型
(定义/对比/流程/结构/定量/分类), 再套对应布局。每个场景的合格线:
示意图 (≥3 个图形元素) + info_card + callout/对比标签 + 4-8 个 play。
只有 chip 和文字的场景 = 空壳, 返工。

每段标准骨架:
```python
def scene2_xxx(self):
    chip = section_chip(1, "子概念名")
    self.add(chip)                       # ⚠ 必须 add 才显示
    # 左侧示意图 (按配方) → callout 指哪讲哪 → 右侧 info_card
    self.wait(1.5)
    self.clear_stage()
```

Helper 一览 (都在 `assets/template.py`): `chapter_corner` `section_chip` `clear_stage`
`info_card` `callout` `icon_badge` `summary_bar` `styled_text` `wave_arcs` `wave_path`
`dashed_rect` `transition_wipe` + 4 个标题页图标 (TITLE_ICONS)。

渲染完看蒙太奇 `preview/montage.png` 自检 7 格。避坑见 `references/manim-gotchas.md`
(9 个坑: chip 不显示 / Arc 变实心 / 无 DASHED 常量 / MathTex 要 LaTeX / …)。

## 管线 B: 配音教学视频

**顺序不能乱** — 时间轴由音频实际长度决定:

```bash
# 1. 建项目目录, 放入 storyboard.json

# 2. TTS 配音 (需要 MINIMAX_API_KEY; 没有时 --provider say 先走通预览)
export MINIMAX_API_KEY=...           # 可选: MINIMAX_GROUP_ID / MINIMAX_API_HOST / MINIMAX_TTS_MODEL
python3 scripts/minimax_tts.py storyboard.json --outdir audio/
# → audio/seg-0N.mp3 + audio/durations.json (时间轴唯一来源)

# 3. 生成骨架 (时间轴/配色/audio/SEGMENTS 全部自动填好, 不要手搭)
python3 scripts/scaffold_video.py <project_dir>

# 4. 填场景内容: s2-s6 的 SVG 示意图 (零件拷 references/svg-parts.md) + 卡片文案
#    + scene2()-scene6() 入场编排。规则见 references/video-authoring.md — GSAP 硬规则违反必坏

# 5. 检查 + 渲染 (lint + validate 对比度审计 + render + 场景中点蒙太奇)
bash scripts/build_video.sh <project_dir>
# → renders/<name>.mp4 + preview/montage.png

# 换音色/改旁白后重跑 TTS, 用脚本同步时间轴 (不要手抄数字), 再重新渲染:
python3 scripts/sync_timeline.py <project_dir>
```

场景内容要求与 Manim 版对齐: section-chip + SVG 示意图 + info-card + callout +
字幕条 (自动生成)。视频尺寸规范、SVG 画法、动效编排、实测 lint 坑都在
`references/video-authoring.md`。

环境: Node.js ≥22 + ffmpeg (`npx hyperframes doctor` 自检); Minimax TTS 走 HTTP API,
无额外 Python 依赖。

## 输出文件规范

```
<topic>/
├── <topic>.py               # 管线 A
├── storyboard.json          # 共用分镜
├── outputs/
│   ├── <topic>.mp4          # 动图高清版
│   └── <topic>.gif          # 公众号内嵌版
├── audio/                   # 管线 B: TTS 产物
│   ├── seg-01..07.mp3
│   └── durations.json
├── index.html               # 管线 B: HyperFrames 组合
├── renders/<topic>.mp4      # 带配音成片
└── preview/montage.png      # 蒙太奇 (两条管线各一张)
```

## 资源

- `assets/template.py` — Manim v2 模板 (全部 helper + 示例场景)
- `assets/video-template/index.html` — HyperFrames 模板 (组件 + 转场/字幕/波形引擎)
- `examples/sound_phenomena.py` — 声现象动图完整示例 (可直接渲染)
- `examples/sound-video/` — 声现象视频完整示例 (storyboard → 音频 → index.html → 成片)
- `scripts/render.sh` — 动图渲染 (GIF>2MB 自动降级) | `scripts/minimax_tts.py` — 配音
- `scripts/scaffold_video.py` — 视频骨架生成 (第 3 步) | `scripts/sync_timeline.py` — 重配音后同步时间轴
- `scripts/build_video.sh` — 视频渲染 (lint + validate + render + 场景中点蒙太奇)
- `references/storyboard-guide.md` — 分镜拆解 + 旁白规范 (第 0 步必读)
- `references/scene-recipes.md` — Manim 场景配方 (管线 A 必读)
- `references/video-authoring.md` — 视频编写硬规则 (管线 B 必读)
- `references/svg-parts.md` — SVG 符号库 (电学/波形/图线/力学/光学, 画示意图先来这拷)
- `references/color-palettes.md` — 7 套主题调色板 (v2) + CSS 变量映射
- `references/manim-gotchas.md` — Manim 避坑 9 条
