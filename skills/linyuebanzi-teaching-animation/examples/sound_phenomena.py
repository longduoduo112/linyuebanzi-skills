# -*- coding: utf-8 -*-
"""声现象 · 教学动图 (基于 template v2)

渲染: bash scripts/render.sh sound_phenomena.py SoundPhenomena qh
"""

from manim import *
import numpy as np

# =========================================================================
# 配色: 声现象 (暖橙系)
# =========================================================================
PRIMARY   = "#E8631C"   # 主橙 (10% 强调: 示意图主体/公式/编号)
ACCENT    = "#F4A24C"   # 亮橙 (对比元素)
HIGHLIGHT = "#FFD166"   # 黄
INK       = "#22303C"   # 蓝黑正文 (与暖主色形成冷暖对比)
NEUTRAL   = "#5E7183"   # 冷灰青 (kicker/标签)
SOFT      = "#FFFDF6"   # 卡片底 (近白)
LINE      = "#9DAEBB"   # 结构线 (冷)
BG        = "#FFF6E5"   # cream 背景
WHITE     = "#FFFFFF"
SERIES    = "#5E7183"   # 章节标识 (冷)

CJK       = "Heiti SC"    # 正文/标签
CJK_SERIF = "Songti SC"   # 大标题/公式 (衬线)

# 文字层级
TITLE_SCALE   = 0.55
BODY_SCALE    = 0.36
LABEL_SCALE   = 0.28
FORMULA_SCALE = 0.48


# =========================================================================
# Helper (从 template v2 复制, 保持独立可运行)
# =========================================================================
def chapter_corner(text="初二物理·第2章", color=SERIES):
    label = Text(text, font=CJK, color=color).scale(0.28)
    label.to_corner(UR, buff=0.3)
    underline = Line(
        label.get_corner(DL) + DOWN * 0.08,
        label.get_corner(DR) + DOWN * 0.08,
        color=color, stroke_width=2, stroke_opacity=0.5,
    )
    return VGroup(label, underline)

def ghost_number(num, color=SERIES):
    ghost = Text(f"{num:02d}", font=CJK_SERIF, color=color, weight=BOLD)
    ghost.scale(3.2).set_opacity(0.14)
    ghost.to_corner(DR, buff=0).shift(DOWN * 0.55 + RIGHT * 0.15)
    return ghost

def section_chip(num, title, color=PRIMARY):
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
    arcs = VGroup()
    for r in radii:
        a = Arc(radius=r, start_angle=PI / 2, angle=-PI,
                color=color, stroke_width=stroke,
                fill_opacity=0, stroke_opacity=opacity)
        a.move_arc_center_to(center)
        arcs.add(a)
    return arcs

def wave_path(start, length, amplitude, freq, color=ACCENT, stroke=3, samples=200):
    xs = np.linspace(0, length, samples)
    ys = amplitude * np.sin(2 * np.pi * freq * xs / length)
    pts = [np.array([start[0] + x, start[1] + y, 0]) for x, y in zip(xs, ys)]
    return VMobject(stroke_color=color, stroke_width=stroke).set_points_as_corners(pts)

def styled_text(text, level="body", color=INK, font=None, **kwargs):
    scales = {"title": TITLE_SCALE, "body": BODY_SCALE,
              "label": LABEL_SCALE, "formula": FORMULA_SCALE}
    if font is None:
        font = CJK_SERIF if level == "formula" else CJK
    return Text(text, font=font, color=color, **kwargs).scale(scales.get(level, BODY_SCALE))

def info_card(title, content_lines, color=PRIMARY, width=3.5, font=CJK, formula=None):
    inner_w = width - 0.5
    kicker_sq = Square(side_length=0.09, color=color, fill_opacity=1, stroke_width=0)
    kicker_text = Text(" ".join(title), font=font, color=NEUTRAL, weight=BOLD).scale(0.24)
    kicker = VGroup(kicker_sq, kicker_text).arrange(RIGHT, buff=0.12)
    rule = Line([0, 0, 0], [inner_w, 0, 0], color=NEUTRAL,
                stroke_width=1.2, stroke_opacity=0.45)
    lines = VGroup()
    for line in content_lines:
        t = Text(line, font=font, color=INK).scale(0.32)
        lines.add(t)
    if formula:
        lines.add(Text(formula, font=CJK_SERIF, color=color, weight=BOLD).scale(0.4))
    lines.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
    content = VGroup(kicker, rule, lines)
    content.arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    body_bg = RoundedRectangle(
        width=width, height=content.height + 0.5,
        corner_radius=0.12,
        color=SOFT, fill_opacity=0.92,
        stroke_color=NEUTRAL, stroke_width=1.2, stroke_opacity=0.4,
    )
    content.move_to(body_bg).align_to(body_bg.get_left() + RIGHT * 0.28, LEFT)
    edge = Rectangle(width=0.06, height=body_bg.height - 0.1,
                     color=color, fill_opacity=1, stroke_width=0)
    edge.move_to(body_bg.get_left() + RIGHT * 0.05)
    return VGroup(body_bg, edge, content)

def callout(target_pos, text, text_pos, color=PRIMARY, font=CJK):
    dot = Dot(target_pos, color=color, radius=0.06)
    arrow = Arrow(text_pos, target_pos, color=color, stroke_width=2,
                  tip_length=0.15, buff=0.15)
    label = Text(text, font=font, color=color).scale(LABEL_SCALE)
    label.move_to(text_pos)
    direction = np.array(text_pos) - np.array(target_pos)
    if np.linalg.norm(direction) > 0:
        direction = direction / np.linalg.norm(direction)
    label.shift(direction * 0.25)
    return VGroup(dot, arrow, label)

def icon_badge(icon_text, label, color=PRIMARY, font=CJK):
    icon = Text(icon_text, font=font, color=color).scale(0.45)
    bg = Circle(radius=0.28, color=color,
                fill_opacity=0.12, stroke_width=1.5, stroke_color=color)
    icon.move_to(bg)
    lbl = Text(label, font=font, color=INK).scale(LABEL_SCALE)
    lbl.next_to(bg, DOWN, buff=0.1)
    return VGroup(bg, icon, lbl)

def summary_bar(items, color=PRIMARY, font=CJK, y=-2.8):
    badges = VGroup()
    for icon_text, label in items:
        badges.add(icon_badge(icon_text, label, color=color, font=font))
    badges.arrange(RIGHT, buff=0.6)
    badges.move_to([0, y, 0])
    return badges


# =========================================================================
# 主场景
# =========================================================================
class SoundPhenomena(Scene):
    CHAPTER_TEXT = "初二物理·第2章"

    def construct(self):
        self.camera.background_color = BG
        self.chapter = chapter_corner(self.CHAPTER_TEXT)
        self.add(self.chapter)

        self.scene1_title()
        self.scene2_vibration()
        self.scene3_propagation()
        self.scene4_pitch()
        self.scene5_loudness()
        self.scene6_timbre()
        self.scene7_summary()

    def clear_stage(self):
        rest = [m for m in self.mobjects if m is not self.chapter]
        if rest:
            self.play(*[FadeOut(m) for m in rest], run_time=0.4)

    # -----------------------------------------------------------------
    # 场景 1: 标题
    # -----------------------------------------------------------------
    def scene1_title(self):
        chip = section_chip(0, "引入")
        self.add(chip)

        title = Text("声现象", font=CJK_SERIF, color=PRIMARY, weight=BOLD).scale(2.2)
        title.move_to([0, 0.8, 0])

        # 音叉图标
        fork_l = Line([0, 0, 0], [0, 0.9, 0], color=PRIMARY, stroke_width=4)
        fork_r = Line([0.35, 0, 0], [0.35, 0.9, 0], color=PRIMARY, stroke_width=4)
        fork_arc = ArcBetweenPoints([0, 0.9, 0], [0.35, 0.9, 0],
                                    angle=-PI, color=PRIMARY, stroke_width=4)
        fork_handle = Line([0.175, 0, 0], [0.175, -0.5, 0], color=PRIMARY, stroke_width=5)
        fork = VGroup(fork_l, fork_r, fork_arc, fork_handle).scale(0.7)
        arcs = wave_arcs([0.6, 0.5, 0], [0.3, 0.5, 0.7],
                         color=ACCENT, opacity=0.4, stroke=2)
        icon = VGroup(fork, arcs).next_to(title, LEFT, buff=0.8)

        sub = styled_text(
            "振动发声 · 声波传播 · 音调 · 响度 · 音色 · 声速",
            level="title", color=INK, weight=BOLD
        )
        sub.next_to(title, DOWN, buff=0.6)

        sub2 = styled_text("—— 声音的产生与特性 ——", level="body", color=LINE)
        sub2.next_to(sub, DOWN, buff=0.35)

        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(icon, shift=LEFT * 0.3), run_time=0.5)
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.5)
        self.play(FadeIn(sub2, shift=UP * 0.2), run_time=0.4)
        self.wait(1.5)
        self.clear_stage()

    # -----------------------------------------------------------------
    # 场景 2: 振动发声
    # -----------------------------------------------------------------
    def scene2_vibration(self):
        chip = section_chip(1, "振动发声")
        self.add(chip)
        self.add(ghost_number(1))

        # 左侧: 音叉动画
        fork_l = Line([0, 0, 0], [0, 1.5, 0], color=INK, stroke_width=5)
        fork_r = Line([0.5, 0, 0], [0.5, 1.5, 0], color=INK, stroke_width=5)
        fork_arc = ArcBetweenPoints([0, 1.5, 0], [0.5, 1.5, 0],
                                    angle=-PI, color=INK, stroke_width=5)
        fork_handle = Line([0.25, 0, 0], [0.25, -0.8, 0], color=INK, stroke_width=6)
        base = RoundedRectangle(width=0.8, height=0.2, corner_radius=0.05,
                                color=LINE, fill_opacity=0.5, stroke_width=1)
        base.move_to([0.25, -0.9, 0])
        fork_group = VGroup(fork_l, fork_r, fork_arc, fork_handle, base)
        fork_group.move_to([-3.5, -0.3, 0])

        self.play(FadeIn(fork_group), run_time=0.5)

        # 振动箭头
        arr_l = Arrow([-3.7, 0.5, 0], [-4.2, 0.5, 0], color=PRIMARY,
                      stroke_width=3, tip_length=0.12)
        arr_r = Arrow([-3.0, 0.5, 0], [-2.5, 0.5, 0], color=PRIMARY,
                      stroke_width=3, tip_length=0.12)
        self.play(FadeIn(arr_l), FadeIn(arr_r), run_time=0.3)

        # 声波弧线
        arcs = wave_arcs([-2.3, 0.3, 0], [0.5, 0.8, 1.1, 1.4],
                         color=ACCENT, opacity=0.6, stroke=2.5)
        self.play(Create(arcs), run_time=0.8)

        # 标注
        c1 = callout(
            target_pos=[-3.5, -0.9, 0],
            text="振动源",
            text_pos=[-3.5, -1.8, 0],
            color=PRIMARY
        )
        self.play(FadeIn(c1), run_time=0.4)

        # 右侧信息卡片
        card = info_card("振动发声", [
            "声音由物体振动产生",
            "振动停止，声音也停止",
            "一切发声体都在振动",
        ], color=PRIMARY, width=3.2)
        card.move_to([3.0, 0, 0])
        self.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)

        self.wait(1.5)
        self.clear_stage()

    # -----------------------------------------------------------------
    # 场景 3: 声波传播
    # -----------------------------------------------------------------
    def scene3_propagation(self):
        chip = section_chip(2, "声波传播")
        self.add(chip)
        self.add(ghost_number(2))

        # 左侧: 鼓 + 声波
        drum_body = RoundedRectangle(width=1.2, height=0.7, corner_radius=0.08,
                                     color="#C0392B", fill_opacity=0.7, stroke_width=2)
        drum_top = Ellipse(width=1.2, height=0.3, color=SOFT,
                           fill_opacity=0.9, stroke_color=INK, stroke_width=2)
        drum_top.next_to(drum_body, UP, buff=-0.05)
        drum = VGroup(drum_body, drum_top).move_to([-3.5, 0, 0])

        # 鼓槌
        stick = Line([-3.0, 0.8, 0], [-3.3, 0.2, 0], color=LINE, stroke_width=4)
        stick_head = Dot([-3.0, 0.8, 0], color=ACCENT, radius=0.08)

        self.play(FadeIn(drum), FadeIn(stick), FadeIn(stick_head), run_time=0.5)

        # 同心圆声波
        circles = VGroup()
        for r in [0.5, 0.9, 1.3, 1.7]:
            c = Circle(radius=r, color=ACCENT, stroke_width=2,
                       fill_opacity=0, stroke_opacity=0.7 - r * 0.2)
            c.move_to([-3.5, 0.2, 0])
            circles.add(c)
        self.play(Create(circles), run_time=1.0)

        # 右侧信息卡片
        card = info_card("声波传播", [
            "声音以波的形式传播",
            "声波需要介质（固/液/气）",
            "真空不能传声",
        ], color=PRIMARY, width=3.2)
        card.move_to([3.0, 0, 0])
        self.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)

        # 标注
        c1 = callout(
            target_pos=[-3.5, 0.2, 0],
            text="声源",
            text_pos=[-3.5, -1.5, 0],
            color=PRIMARY
        )
        self.play(FadeIn(c1), run_time=0.4)

        self.wait(1.5)
        self.clear_stage()

    # -----------------------------------------------------------------
    # 场景 4: 音调
    # -----------------------------------------------------------------
    def scene4_pitch(self):
        chip = section_chip(3, "音调")
        self.add(chip)
        self.add(ghost_number(3))

        # 两条波形对比: 高频 vs 低频
        wave_low = wave_path([-5.5, 1.0, 0], 4.5, 0.4, 2,
                             color=ACCENT, stroke=3)
        wave_high = wave_path([-5.5, -0.8, 0], 4.5, 0.4, 6,
                              color=PRIMARY, stroke=3)

        label_low = styled_text("低音调（频率低）", level="label", color=ACCENT)
        label_low.next_to(wave_low, LEFT, buff=0.15)
        label_high = styled_text("高音调（频率高）", level="label", color=PRIMARY)
        label_high.next_to(wave_high, LEFT, buff=0.15)

        self.play(Create(wave_low), FadeIn(label_low), run_time=0.6)
        self.play(Create(wave_high), FadeIn(label_high), run_time=0.6)

        # 右侧信息卡片
        card = info_card("音调", [
            "音调高低由频率决定",
            "频率：每秒振动次数",
            "单位：赫兹（Hz）",
        ], color=PRIMARY, width=3.2, formula="频率越高 → 音调越高")
        card.move_to([3.5, 0, 0])
        self.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)

        self.wait(1.5)
        self.clear_stage()

    # -----------------------------------------------------------------
    # 场景 5: 响度
    # -----------------------------------------------------------------
    def scene5_loudness(self):
        chip = section_chip(4, "响度")
        self.add(chip)
        self.add(ghost_number(4))

        # 两条波形对比: 大振幅 vs 小振幅
        wave_small = wave_path([-5.5, 1.0, 0], 4.5, 0.2, 4,
                               color=ACCENT, stroke=3)
        wave_big = wave_path([-5.5, -0.8, 0], 4.5, 0.6, 4,
                             color=PRIMARY, stroke=3)

        label_small = styled_text("响度小（振幅小）", level="label", color=ACCENT)
        label_small.next_to(wave_small, LEFT, buff=0.15)
        label_big = styled_text("响度大（振幅大）", level="label", color=PRIMARY)
        label_big.next_to(wave_big, LEFT, buff=0.15)

        self.play(Create(wave_small), FadeIn(label_small), run_time=0.6)
        self.play(Create(wave_big), FadeIn(label_big), run_time=0.6)

        # 右侧信息卡片
        card = info_card("响度", [
            "响度大小由振幅决定",
            "振幅：偏离平衡位置的距离",
            "还与距离声源远近有关",
        ], color=PRIMARY, width=3.2, formula="振幅越大 → 响度越大")
        card.move_to([3.5, 0, 0])
        self.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)

        self.wait(1.5)
        self.clear_stage()

    # -----------------------------------------------------------------
    # 场景 6: 音色
    # -----------------------------------------------------------------
    def scene6_timbre(self):
        chip = section_chip(5, "音色")
        self.add(chip)
        self.add(ghost_number(5))

        # 两条不同波形: 简单正弦 vs 复杂波
        wave_simple = wave_path([-5.5, 1.0, 0], 4.5, 0.4, 4,
                                color=ACCENT, stroke=3)

        # 复杂波形 (叠加两个频率)
        xs = np.linspace(0, 4.5, 200)
        ys = 0.3 * np.sin(2 * np.pi * 4 * xs / 4.5) + \
             0.15 * np.sin(2 * np.pi * 12 * xs / 4.5) + \
             0.1 * np.sin(2 * np.pi * 20 * xs / 4.5)
        pts = [np.array([-5.5 + x, -0.8 + y, 0]) for x, y in zip(xs, ys)]
        wave_complex = VMobject(stroke_color=PRIMARY, stroke_width=3).set_points_as_corners(pts)

        label_s = styled_text("笛子（波形简单）", level="label", color=ACCENT)
        label_s.next_to(wave_simple, LEFT, buff=0.15)
        label_c = styled_text("小提琴（波形复杂）", level="label", color=PRIMARY)
        label_c.next_to(wave_complex, LEFT, buff=0.15)

        self.play(Create(wave_simple), FadeIn(label_s), run_time=0.6)
        self.play(Create(wave_complex), FadeIn(label_c), run_time=0.6)

        # 右侧信息卡片
        card = info_card("音色", [
            "音色由材料和结构决定",
            "不同乐器 → 不同波形",
            "同一音调和响度下",
            "仍可区分不同乐器",
        ], color=PRIMARY, width=3.2)
        card.move_to([3.5, 0, 0])
        self.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)

        self.wait(1.5)
        self.clear_stage()

    # -----------------------------------------------------------------
    # 场景 7: 总结 + 声速
    # -----------------------------------------------------------------
    def scene7_summary(self):
        chip = section_chip(6, "声速与总结")
        self.add(chip)
        self.add(ghost_number(6))

        # 声速大字
        speed = Text("340 m/s", font=CJK_SERIF, color=PRIMARY, weight=BOLD).scale(1.8)
        speed.move_to([0, 1.2, 0])
        speed_label = styled_text("声音在空气中的传播速度（15°C）",
                                  level="body", color=INK)
        speed_label.next_to(speed, DOWN, buff=0.3)

        self.play(Write(speed), run_time=0.8)
        self.play(FadeIn(speed_label), run_time=0.4)

        # 总结卡片
        card = info_card("本章小结", [
            "声音由振动产生，通过介质传播",
            "音调 ← 频率 | 响度 ← 振幅",
            "音色 ← 材料和结构",
            "真空不能传声",
        ], color=PRIMARY, width=5.0)
        card.move_to([0, -0.8, 0])
        self.play(FadeIn(card, shift=UP * 0.3), run_time=0.6)

        # 底部总结栏
        bar = summary_bar([
            ("∿", "振动"),
            ("◎", "声波"),
            ("♪", "频率"),
            ("↕", "振幅"),
        ], color=PRIMARY)
        self.play(FadeIn(bar, shift=UP * 0.2), run_time=0.5)

        self.wait(2.0)
