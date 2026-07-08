# -*- coding: utf-8 -*-
"""教学动图 通用模板 v2 (Manim Community)

## 更新 (v2)
  - 新增 info_card(): 圆角信息卡片, 替代纯文字堆砌
  - 新增 callout(): 标注线+箭头, "指哪讲哪"
  - 新增 icon_badge(): 图标+标签徽章, 适合底部总结栏
  - 新增 styled_text(): 带层级的文字 (title/body/label/formula)
  - 新增 transition_wipe(): 横扫过渡, 替代单调的 FadeOut
  - 新增 summary_bar(): 底部总结栏, 一行徽章
  - 优化 scene1_title: 支持主题图标装饰

## 使用方式
  1. 复制本文件为 `<topic>.py`
  2. 改 ClassName (默认 ExampleTopic)
  3. 改 "配色" 块 (见 references/color-palettes.md)
  4. 改 chapter_corner() 和 7 个 sceneN_xxx()
  5. 渲染: bash scripts/render.sh <topic>.py ClassName qh

## 保留的 helper (v1)
  - chapter_corner()         右上角章节标识
  - section_chip()           左上角小节标
  - clear_stage()            段间清场
  - wave_arcs()              多层弧 (声波/光波)
  - dashed_rect()            虚线矩形
  - wave_path()              正弦波路径

## 新增 helper (v2)
  - info_card()              圆角信息卡片
  - callout()                标注线+箭头
  - icon_badge()             图标徽章
  - summary_bar()            底部总结栏
  - styled_text()            层级文字
  - transition_wipe()        横扫过渡 (Scene 方法)

## 避坑 (见 references/manim-gotchas.md)
  - section_chip() 必须 self.add(chip)
  - Arc 用 fill_opacity=0, stroke_opacity=X
  - 虚线矩形用 dashed_rect(), 不要 set_stroke(DASHED)
  - MathTex 需要 LaTeX, 没装就用 Text + Unicode 符号
"""

from manim import *
import numpy as np


# =========================================================================
# 配色 v2 (按主题替换整块, 见 references/color-palettes.md)
# 60-30-10 分层: 背景 60% + 冷/暖中性结构 30% + 主色强调 10%
# 中性色 (INK/NEUTRAL/LINE/SERIES) 的色温与主色相反: 暖主色配冷灰, 冷主色配暖灰
# =========================================================================
PRIMARY   = "#E8631C"   # 主色 (10% 强调: 示意图主体/公式/编号)
ACCENT    = "#F4A24C"   # 次强调 (对比元素)
HIGHLIGHT = "#FFD166"   # 浅辅
INK       = "#22303C"   # 正文 (蓝黑, 与暖主色形成冷暖对比)
NEUTRAL   = "#5E7183"   # 冷灰青 (kicker/标签/副标题)
SOFT      = "#FFFDF6"   # 卡片底 (近白)
LINE      = "#9DAEBB"   # 结构线 (冷)
BG        = "#FFF6E5"   # 背景
WHITE     = "#FFFFFF"
SERIES    = "#5E7183"   # 章节标识 (冷)
# 主题专用 (按需启用):
RED       = "#E63946"
WATER     = "#9ED2EA"
WATER_DK  = "#5BA8D3"
RAINBOW   = ["#E63946", "#F77F00", "#FCBF49", "#06A77D",
             "#118AB2", "#264D8C", "#7209B7"]

CJK       = "Heiti SC"    # 正文/标签
CJK_SERIF = "Songti SC"   # 大标题/公式/大数字 (衬线, 教材质感)

# 文字层级
TITLE_SCALE   = 0.55   # 段内标题
BODY_SCALE    = 0.36   # 正文
LABEL_SCALE   = 0.28   # 标注/注释
FORMULA_SCALE = 0.48   # 公式


# =========================================================================
# 复用组件 (v1 保留)
# =========================================================================
def chapter_corner(text="初二物理·第N章", color=SERIES):
    """右上角系列标识 (v2: 带下划线)。整集保留。"""
    label = Text(text, font=CJK, color=color).scale(0.28)
    label.to_corner(UR, buff=0.3)
    underline = Line(
        label.get_corner(DL) + DOWN * 0.08,
        label.get_corner(DR) + DOWN * 0.08,
        color=color, stroke_width=2, stroke_opacity=0.5,
    )
    return VGroup(label, underline)


def ghost_number(num, color=SERIES):
    """右下角巨型底纹编号 (v2)。每个场景 self.add() 一个, clear_stage 会清掉。"""
    ghost = Text(f"{num:02d}", font=CJK_SERIF, color=color, weight=BOLD)
    ghost.scale(3.2).set_opacity(0.14)
    ghost.to_corner(DR, buff=0).shift(DOWN * 0.55 + RIGHT * 0.15)
    return ghost


def section_chip(num, title, color=PRIMARY):
    """左上角小节标: 编号圆 + 标题胶囊。
    ⚠ 必须 self.add(chip) 才会出现。"""
    num_text = Text(str(num), font=CJK, color=WHITE, weight=BOLD).scale(0.42)
    num_bg = Circle(radius=0.18, color=color, fill_opacity=1, stroke_width=0)
    num_text.move_to(num_bg.get_center())
    num_group = VGroup(num_bg, num_text)

    title_text = Text(title, font=CJK, color=INK, weight=BOLD).scale(0.42)
    pad = 0.18
    title_bg = RoundedRectangle(
        width=title_text.width + pad * 2,
        height=title_text.height + pad,
        corner_radius=0.12,
        color=WHITE, fill_opacity=1,
        stroke_color=NEUTRAL, stroke_width=1.5, stroke_opacity=0.5,
    ).move_to(title_text.get_center())

    title_group = VGroup(title_bg, title_text)
    title_group.next_to(num_group, RIGHT, buff=0.15)
    chip = VGroup(num_group, title_group)
    chip.to_corner(UL, buff=0.3)
    return chip


def wave_arcs(center, radii, color=ACCENT, opacity=0.85, stroke=3):
    """多层弧 (声波/光波/水波)。fill_opacity 已设为 0。"""
    arcs = VGroup()
    for r in radii:
        a = Arc(radius=r, start_angle=PI / 2, angle=-PI,
                color=color, stroke_width=stroke,
                fill_opacity=0, stroke_opacity=opacity)
        a.move_arc_center_to(center)
        arcs.add(a)
    return arcs


def dashed_rect(w, h, color=LINE, stroke=2.5, dash=0.06, fill_opacity=0):
    """虚线矩形 (4 条 DashedLine 拼)。"""
    return VGroup(
        DashedLine([-w/2,  h/2, 0], [ w/2,  h/2, 0],
                   color=color, stroke_width=stroke, dash_length=dash),
        DashedLine([ w/2,  h/2, 0], [ w/2, -h/2, 0],
                   color=color, stroke_width=stroke, dash_length=dash),
        DashedLine([ w/2, -h/2, 0], [-w/2, -h/2, 0],
                   color=color, stroke_width=stroke, dash_length=dash),
        DashedLine([-w/2, -h/2, 0], [-w/2,  h/2, 0],
                   color=color, stroke_width=stroke, dash_length=dash),
    )


def wave_path(start, length, amplitude, freq, color=ACCENT, stroke=3, samples=200):
    """一段正弦波 (用于音调/响度演示)。"""
    xs = np.linspace(0, length, samples)
    ys = amplitude * np.sin(2 * np.pi * freq * xs / length)
    pts = [np.array([start[0] + x, start[1] + y, 0])
           for x, y in zip(xs, ys)]
    return VMobject(stroke_color=color, stroke_width=stroke).set_points_as_corners(pts)


# =========================================================================
# 新增组件 (v2)
# =========================================================================
def styled_text(text, level="body", color=INK, font=None, **kwargs):
    """带层级的文字。level: title / body / label / formula
    v2: formula 默认用宋体 (CJK_SERIF), 其余用黑体。"""
    scales = {
        "title": TITLE_SCALE,
        "body": BODY_SCALE,
        "label": LABEL_SCALE,
        "formula": FORMULA_SCALE,
    }
    if font is None:
        font = CJK_SERIF if level == "formula" else CJK
    return Text(text, font=font, color=color, **kwargs).scale(
        scales.get(level, BODY_SCALE)
    )


def info_card(title, content_lines, color=PRIMARY, width=3.5, font=CJK, formula=None):
    """信息卡片 v2: 去大色块, 白底 + 左侧主色细边 + kicker 小标 + 细规则线。

    参数:
        title: kicker 小标 (字距拉开的小字, 不是大色块)
        content_lines: list[str], 每行一条内容
        color: 强调色 (左边线/kicker 方块)
        width: 卡片宽度
        formula: 可选, 公式行 (宋体加粗, 主色, 排在内容行下方)
    返回:
        VGroup (可直接 self.play(FadeIn(card)))
    """
    inner_w = width - 0.5

    # kicker 行: 小方块 + 拉开字距的小标
    kicker_sq = Square(side_length=0.09, color=color, fill_opacity=1, stroke_width=0)
    kicker_text = Text(" ".join(title), font=font, color=NEUTRAL, weight=BOLD).scale(0.24)
    kicker = VGroup(kicker_sq, kicker_text).arrange(RIGHT, buff=0.12)
    rule = Line([0, 0, 0], [inner_w, 0, 0], color=NEUTRAL,
                stroke_width=1.2, stroke_opacity=0.45)

    # 内容行
    lines = VGroup()
    for line in content_lines:
        t = Text(line, font=font, color=INK).scale(0.32)
        lines.add(t)
    if formula:
        lines.add(Text(formula, font=CJK_SERIF, color=color, weight=BOLD).scale(0.4))
    lines.arrange(DOWN, buff=0.16, aligned_edge=LEFT)

    # 纵向组装 (左对齐)
    content = VGroup(kicker, rule, lines)
    content.arrange(DOWN, buff=0.14, aligned_edge=LEFT)

    # 卡片背景: 白底 + 冷灰细边
    body_bg = RoundedRectangle(
        width=width,
        height=content.height + 0.5,
        corner_radius=0.12,
        color=SOFT, fill_opacity=0.92,
        stroke_color=NEUTRAL, stroke_width=1.2, stroke_opacity=0.4,
    )
    content.move_to(body_bg).align_to(body_bg.get_left() + RIGHT * 0.28, LEFT)

    # 左侧主色细边
    edge = Rectangle(
        width=0.06, height=body_bg.height - 0.1,
        color=color, fill_opacity=1, stroke_width=0,
    )
    edge.move_to(body_bg.get_left() + RIGHT * 0.05)

    return VGroup(body_bg, edge, content)


def callout(target_pos, text, text_pos, color=PRIMARY, font=CJK):
    """标注线: 从文字指向目标位置。

    参数:
        target_pos: [x, y, 0] 被标注的点
        text: 标注文字
        text_pos: [x, y, 0] 文字位置
    返回:
        VGroup(dot, arrow, label)
    """
    dot = Dot(target_pos, color=color, radius=0.06)
    arrow = Arrow(
        text_pos, target_pos,
        color=color, stroke_width=2,
        tip_length=0.15, buff=0.15
    )
    label = Text(text, font=font, color=color).scale(LABEL_SCALE)
    label.move_to(text_pos)
    # 微调: 文字往箭头反方向偏移一点, 避免重叠
    direction = np.array(text_pos) - np.array(target_pos)
    if np.linalg.norm(direction) > 0:
        direction = direction / np.linalg.norm(direction)
    label.shift(direction * 0.25)
    return VGroup(dot, arrow, label)


def icon_badge(icon_text, label, color=PRIMARY, font=CJK):
    """小图标 + 标签徽章, 适合底部总结栏。

    参数:
        icon_text: 图标文字 (emoji 或单字符, 如 "🔊" "〰" "♫")
        label: 标签文字
    返回:
        VGroup
    """
    icon = Text(icon_text, font=font, color=color).scale(0.45)
    bg = Circle(
        radius=0.28, color=color,
        fill_opacity=0.12, stroke_width=1.5, stroke_color=color
    )
    icon.move_to(bg)
    lbl = Text(label, font=font, color=INK).scale(LABEL_SCALE)
    lbl.next_to(bg, DOWN, buff=0.1)
    return VGroup(bg, icon, lbl)


def summary_bar(items, color=PRIMARY, font=CJK, y=-2.8):
    """底部总结栏: 一行 icon_badge。

    参数:
        items: list[tuple(icon_text, label)], 如 [("🔊", "振动"), ("〰", "声波")]
        y: 纵坐标位置 (默认 -2.8, 画面底部)
    返回:
        VGroup
    """
    badges = VGroup()
    for icon_text, label in items:
        badges.add(icon_badge(icon_text, label, color=color, font=font))
    badges.arrange(RIGHT, buff=0.6)
    badges.move_to([0, y, 0])
    return badges


def title_icon_tuning_fork(color=PRIMARY):
    """标题页装饰: 音叉 + 声波 (声现象用)"""
    # 简化音叉: U 形
    left = Line([0, 0, 0], [0, 1.2, 0], color=color, stroke_width=4)
    right = Line([0.4, 0, 0], [0.4, 1.2, 0], color=color, stroke_width=4)
    bridge = ArcBetweenPoints([0, 1.2, 0], [0.4, 1.2, 0],
                              angle=-PI, color=color, stroke_width=4)
    handle = Line([0.2, 0, 0], [0.2, -0.6, 0], color=color, stroke_width=5)
    fork = VGroup(left, right, bridge, handle)

    # 声波弧
    arcs = wave_arcs([0.6, 0.6, 0], [0.4, 0.7, 1.0],
                     color=ACCENT, opacity=0.5, stroke=2)
    return VGroup(fork, arcs)


def title_icon_prism(color=PRIMARY):
    """标题页装饰: 三棱镜 + 光线 (光现象用)"""
    tri = Polygon(
        [-0.5, -0.4, 0], [0.5, -0.4, 0], [0, 0.5, 0],
        color=color, fill_opacity=0.15,
        stroke_color=color, stroke_width=3
    )
    ray_in = Arrow([-1.5, 0, 0], [-0.3, 0, 0],
                   color=WHITE, stroke_width=2, tip_length=0.12)
    # 彩色出射光
    rays_out = VGroup()
    angles = [-0.3, -0.15, 0, 0.15, 0.3]
    colors_list = ["#E63946", "#F77F00", "#FCBF49", "#06A77D", "#118AB2"]
    for angle, c in zip(angles, colors_list):
        ray = Line([0.3, 0, 0], [1.5, angle * 2, 0],
                   color=c, stroke_width=2)
        rays_out.add(ray)
    return VGroup(tri, ray_in, rays_out)


def title_icon_lever(color=PRIMARY):
    """标题页装饰: 杠杆 (力学用)"""
    # 支点三角
    tri = Polygon(
        [0, -0.3, 0], [-0.25, -0.6, 0], [0.25, -0.6, 0],
        color=color, fill_opacity=0.3,
        stroke_color=color, stroke_width=2
    )
    # 杠杆横梁
    beam = Line([-1.5, -0.3, 0], [1.5, -0.1, 0],
                color=INK, stroke_width=4)
    # 左侧重物
    weight = Square(side_length=0.3, color=ACCENT,
                    fill_opacity=0.8, stroke_width=0)
    weight.move_to([-1.2, -0.6, 0])
    # 右侧力箭头
    force = Arrow([1.2, -0.1, 0], [1.2, 0.6, 0],
                  color=RED if RED else "#E63946",
                  stroke_width=3, tip_length=0.15)
    return VGroup(tri, beam, weight, force)


def title_icon_circuit(color=PRIMARY):
    """标题页装饰: 电路 (电学用)"""
    # 简化电路: 电池 + 灯泡符号
    wire_top = Line([-0.8, 0.4, 0], [0.8, 0.4, 0], color=color, stroke_width=2)
    wire_bot = Line([-0.8, -0.4, 0], [0.8, -0.4, 0], color=color, stroke_width=2)
    wire_l = Line([-0.8, 0.4, 0], [-0.8, -0.4, 0], color=color, stroke_width=2)
    wire_r = Line([0.8, 0.4, 0], [0.8, -0.4, 0], color=color, stroke_width=2)
    # 电池符号 (左侧)
    batt_l = Line([-0.9, 0.2, 0], [-0.9, -0.2, 0], color=color, stroke_width=3)
    batt_s = Line([-0.7, 0.1, 0], [-0.7, -0.1, 0], color=color, stroke_width=1.5)
    # 灯泡 (右侧圆)
    bulb = Circle(radius=0.15, color=ACCENT,
                  fill_opacity=0.3, stroke_color=ACCENT, stroke_width=2)
    bulb.move_to([0.8, 0, 0])
    return VGroup(wire_top, wire_bot, wire_l, wire_r, batt_l, batt_s, bulb)


# 主题图标注册表 (按主题族选)
TITLE_ICONS = {
    "sound": title_icon_tuning_fork,
    "light": title_icon_prism,
    "mechanics": title_icon_lever,
    "electricity": title_icon_circuit,
    # 扩展: "heat", "biology", "math" 按需添加
}


# =========================================================================
# 主场景
# =========================================================================
class ExampleTopic(Scene):
    # 按主题改这两个
    CHAPTER_TEXT = "初二物理·第N章"
    THEME_ICON = "light"  # sound / light / mechanics / electricity

    def construct(self):
        self.camera.background_color = BG
        self.chapter = chapter_corner(self.CHAPTER_TEXT)
        self.add(self.chapter)

        self.scene1_title()
        self.scene2_xxx()
        self.scene3_xxx()
        self.scene4_xxx()
        self.scene5_xxx()
        self.scene6_xxx()
        self.scene7_xxx()

    def clear_stage(self):
        """段间清场: 保留 chapter, 其余 fade out"""
        rest = [m for m in self.mobjects if m is not self.chapter]
        if rest:
            self.play(*[FadeOut(m) for m in rest], run_time=0.4)

    def transition_wipe(self, direction=RIGHT):
        """横扫过渡, 比 clear_stage 更有动感。关键转折段用。"""
        rest = [m for m in self.mobjects if m is not self.chapter]
        if rest:
            self.play(
                *[m.animate.shift(direction * 8).set_opacity(0) for m in rest],
                run_time=0.5
            )
            for m in rest:
                self.remove(m)

    # -----------------------------------------------------------------
    # 场景 1: 标题 (v2: 带主题图标)
    def scene1_title(self):
        chip = section_chip(0, "引入")
        self.add(chip)
        # 标题页不放 ghost 编号 (ghost 与 chip 同号, 从场景 2 的 ghost_number(1) 开始)

        # v2: 大标题用宋体 (CJK_SERIF)
        title = Text("主题名", font=CJK_SERIF, color=PRIMARY, weight=BOLD).scale(2.2)
        title.move_to([0, 0.5, 0])

        # 主题图标装饰 (按 THEME_ICON 自动选)
        icon_fn = TITLE_ICONS.get(self.THEME_ICON)
        icon = None
        if icon_fn:
            icon = icon_fn(color=PRIMARY)
            icon.scale(0.8).next_to(title, LEFT, buff=0.8)

        sub = styled_text(
            "子概念 1 · 子概念 2 · 子概念 3",
            level="title", color=INK, weight=BOLD
        )
        sub.next_to(title, DOWN, buff=0.7)

        sub2 = styled_text("—— 副标题 ——", level="body", color=LINE)
        sub2.next_to(sub, DOWN, buff=0.4)

        self.play(Write(title), run_time=1.2)
        if icon:
            self.play(FadeIn(icon, shift=LEFT * 0.3), run_time=0.6)
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.6)
        self.play(FadeIn(sub2, shift=UP * 0.2), run_time=0.5)
        self.wait(1.5)
        self.clear_stage()

    # -----------------------------------------------------------------
    # 场景 2: 子概念 1 (示例: 用 info_card + callout)
    def scene2_xxx(self):
        chip = section_chip(1, "子概念 1", color=PRIMARY)
        self.add(chip)
        self.add(ghost_number(1))   # ghost 与 chip 同号

        # 左侧: 示意图 (按主题画)
        # 例: 一根杠杆
        beam = Line([-2, 0, 0], [2, 0, 0], color=INK, stroke_width=4)
        pivot = Polygon(
            [0, 0, 0], [-0.2, -0.35, 0], [0.2, -0.35, 0],
            color=PRIMARY, fill_opacity=0.4, stroke_width=2
        )
        demo = VGroup(beam, pivot).move_to([-2, 0, 0])
        self.play(Create(demo), run_time=0.8)

        # 标注线
        c1 = callout(
            target_pos=[-2, 0, 0],
            text="支点 O",
            text_pos=[-2, -1.2, 0],
            color=ACCENT
        )
        self.play(FadeIn(c1), run_time=0.5)

        # 右侧: 信息卡片 (公式走 formula 参数, 自动宋体+主色)
        card = info_card("核心要点", [
            "要点 1: 简洁表述",
            "要点 2: 简洁表述",
        ], color=PRIMARY, width=3.2, formula="F₁·L₁ = F₂·L₂")
        card.move_to([3.0, 0, 0])
        self.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)

        self.wait(1.5)
        self.clear_stage()

    # -----------------------------------------------------------------
    # 场景 3-6: 占位
    def scene3_xxx(self):
        chip = section_chip(2, "子概念 2", color=PRIMARY)
        self.add(chip)
        self.wait(1.0)
        self.clear_stage()

    def scene4_xxx(self):
        chip = section_chip(3, "子概念 3", color=PRIMARY)
        self.add(chip)
        self.wait(1.0)
        self.clear_stage()

    def scene5_xxx(self):
        chip = section_chip(4, "子概念 4", color=PRIMARY)
        self.add(chip)
        self.wait(1.0)
        self.clear_stage()

    def scene6_xxx(self):
        chip = section_chip(5, "子概念 5", color=PRIMARY)
        self.add(chip)
        self.wait(1.0)
        self.clear_stage()

    # -----------------------------------------------------------------
    # 场景 7: 收尾 (用 summary_bar)
    def scene7_xxx(self):
        chip = section_chip(6, "总结", color=PRIMARY)
        self.add(chip)

        # 总结卡片
        card = info_card("本章小结", [
            "核心概念 1",
            "核心概念 2",
            "核心公式",
        ], color=PRIMARY, width=5.0)
        card.move_to([0, 0.5, 0])
        self.play(FadeIn(card, shift=UP * 0.3), run_time=0.8)

        # 底部总结栏
        bar = summary_bar([
            ("⚡", "概念1"),
            ("📐", "概念2"),
            ("🔬", "概念3"),
            ("📊", "公式"),
        ], color=PRIMARY)
        self.play(FadeIn(bar, shift=UP * 0.2), run_time=0.6)

        self.wait(2.0)
        # 最后一段不清场
