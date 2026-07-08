# Manim 教学动图 避坑指南

> 5 个最常踩的坑, 都是实战中 debug 出来的。

## 坑 1: `section_chip()` 创建后不显示

**症状**: 调用了 `chip = section_chip(1, "标题")`, 但画面上没出现。

**原因**: `section_chip()` 只返回 VGroup, 不加到 scene。`Create` 也不行 (没被父 scene 接管)。

**修复**:
```python
chip = section_chip(1, "标题")
self.add(chip)         # ✅ 直接 add
# 或
self.play(FadeIn(chip)) # ✅ 或 play
```

---

## 坑 2: `Arc(...).set_opacity(0.85)` 变实心半圆

**症状**: 画声波/光波弧, 想半透明显示, 结果出来是一个实心的半圆饼。

**原因**: `set_opacity` 同时设置 stroke + fill opacity, 而 Arc 默认 fill_opacity=1。

**修复**: 构造时就分开设:
```python
# ❌ 错
a = Arc(radius=1, color=ACCENT, stroke_width=3).set_opacity(0.85)

# ✅ 对
a = Arc(radius=1, color=ACCENT, stroke_width=3,
        fill_opacity=0, stroke_opacity=0.85)
# 或者
a = Arc(...).set_stroke(opacity=0.85)  # 只动 stroke
```

模板里的 `wave_arcs()` 已经处理过, 直接用。

---

## 坑 3: `body.set_stroke(DASHED)` 报 NameError

**症状**: `NameError: name 'DASHED' is not defined`

**原因**: manim community 没有 `DASHED` 常量。

**修复**: 用 4 条 DashedLine 拼出虚线矩形:
```python
# ❌ 错
body = Rectangle(...)
body.set_stroke(DASHED)

# ✅ 对 (用模板里的 dashed_rect)
body = dashed_rect(w=0.28, h=0.7, color=LINE)
```

---

## 坑 4: 文字或线条挤到右边屏幕外

**症状**: 场景 4-5 写文字 "波长=频率×周期" 之类的长句, 被自动换行或挤出屏幕。

**原因**: manim 文字默认 1 行, 太长会溢出。

**修复**:
- 用 `\n` 显式换行: `Text("波长\n频率")`
- 右侧文字 `.move_to([3.0, 0.2, 0])` 而不是放到边缘
- 限制 `.scale(0.4)` 或更小, 全文 `width <= 4.0` units

---

## 坑 5: `BraceLabel` 在某些 manim 版本报错

**症状**: `TypeError: BraceLabel.__init__() got unexpected keyword argument`

**原因**: manim community 0.18 之前 BraceLabel 用法不一样, 0.20+ 才稳定。

**修复**: 自己写一个标签:
```python
# 简单替代: 文字 + Brace 手动定位
brace = Brace(obj, direction=DOWN)
lbl = Text("标签", font=CJK, color=INK).scale(0.3).next_to(brace, DOWN, buff=0.1)
group = VGroup(brace, lbl)
```

---

## 性能 / 渲染小贴士

- **`-qm` (720p30)**: 教学用足够, 28s 渲染 ~15s
- **`-qh` (1080p60)**: 教学分享高清版, ~30s
- **避免**: 单场景超过 80 个独立 play (超过 50s 节奏拖沓, 建议拆)
- **字体**: Heiti SC (macOS 自带), 跨平台可改 Noto Sans CJK
- **GIF 大小**: 720p, 20fps, 调色板 128 色, 单集 < 2MB 适合朋友圈

## 调试命令

```bash
# 渲染 + 跳到指定时间预览
manim -qm --start_at_animation=5 <file>.py SceneClass

# 只看某场景最后一帧
manim -qm --format=png <file>.py SceneClass

# 列出所有可用 Scene
manim -ql --list_scenes <file>.py
```

## CJK 字体备选 (跨平台)

| 平台 | 字体名 |
|---|---|
| macOS | `Heiti SC` / `PingFang SC` |
| Linux | `Noto Sans CJK SC` / `WenQuanYi Zen Hei` |
| Windows | `Microsoft YaHei` / `SimHei` |

manim 找不到字体会 fallback 到默认, 导致中文变方块。打包前确认环境。

## 坑 6: `MathTex` 报 `FileNotFoundError: 'latex'`

**症状**: 用 `MathTex("F_1", "\\cdot", "L_1")` 渲染时:
```
FileNotFoundError: [Errno 2] No such file or directory: 'latex'
```

**原因**: manim 的 `MathTex` 调外部 LaTeX (`latex` / `pdflatex`) 编译公式, 没装就没法用。

**修复**: 默认用 `Text`, 用 Unicode 符号:
```python
# ❌ 错 (没装 LaTeX 就炸)
formula = MathTex("F_1", "\\cdot", "L_1", "=", "F_2", "\\cdot", "L_2")

# ✅ 对
formula = Text("F_1 · L_1 = F_2 · L_2", color=PRIMARY).scale(1.6)
# 也可用: × ÷ ± ≠ ≤ ≥ ∑ ∫ π ° 等 Unicode 数学符号
```

只有装好 LaTeX (`brew install --cask mactex-no-gui` ~5GB) 才能用 `MathTex`。教学场景够用就别装。

---

## 坑 7: `Text("F_1", color=...)` 误传多参数

**症状**:
```python
Text("F_1", "L_1")  # → ValueError: could not convert string to float: 'L_1'
MathTex("F_1", "L_1")  # → TypeError: takes 2 positional arguments but 3 were given
```

**原因**: `Text` / `MathTex` 只接 **一个字符串**, 其它位置参数会被当 `slant` 等数值。

**修复**: 多段文字必须拼成一个串, 或用 `VGroup` 拼多个 Text:
```python
# ✅ 拼成单串
formula = Text("F_1 · L_1 = F_2 · L_2")

# ✅ 多段 VGroup
group = VGroup(
    Text("F_1", color=PRIMARY),
    Text("=", color=INK),
    Text("F_2", color=ACCENT),
).arrange(RIGHT, buff=0.2)
```

---

## 坑 8: ClassName 转文件名 `LeverPrinciple` → `LLever-LPrinciple`

**症状**: `render.sh lever_principle.py LeverPrinciple qm` 输出 `LLever-LPrinciple.mp4`

**原因**: 老版 sed `s/\([A-Z]\)/-\L\1/g` 在 **每个** 大写前加 dash, 连续大写字母会重复拆。

**修复**: 用 Python 正则, 只在 `[a-z][A-Z]` 边界拆:
```bash
KEBAB=$(python3 -c "import re,sys; print(re.sub(r'(?<=[a-z])(?=[A-Z])', '-', sys.argv[1]).lower())" "$SCENE_CLASS")
# LeverPrinciple → lever-principle ✅
# LightPhenomena → light-phenomena ✅
# XMLParser → xml-parser ✅
```

`render.sh` 已用新版本, 直接跑就行。

---

## 坑 9: 蒙太奇抽帧时间写死, 视频短了后面几格空白

**症状**: 视频 34s, 蒙太奇抽 `n=1430` 帧 (47.7s), 后几格全黑。

**原因**: `render.sh` 的 ffmpeg 抽帧时间写死成 7 个等距点 (120, 340, 540, 740, 980, 1220, 1430)。

**修复**: 抽帧前用 ffprobe 算总帧数, 7 等分:
```bash
TOTAL_FRAMES=$($FFPROBE -v error -count_frames -select_streams v:0 \
  -show_entries stream=nb_read_frames -of default=noprint_wrappers=1:nokey=1 \
  "outputs/${KEBAB}.mp4")
# 然后用 TOTAL_FRAMES/6 算每帧间隔
```
(目前 `render.sh` 还没改, 可手动改或等下一版。视频总长 30-50s 时影响不大, 7 格蒙太奇肉眼能看就行。)
