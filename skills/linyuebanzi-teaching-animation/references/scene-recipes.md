# 场景配方 (Manim)

> 解决"空壳场景"问题: 拿到一个子概念, 先判断它属于哪类知识点, 再套对应配方。
> 每个配方都规定了最少画面元素, 只有 chip + 文字的场景不合格。

## 合格线 (每个子概念场景必须全有)

- [ ] `section_chip` 编号小节标 (记得 `self.add(chip)`)
- [ ] **示意图**: ≥3 个图形元素组成的主体 (线/圆/多边形/波形), 放左侧或上方
- [ ] **info_card**: 2-4 行要点, 放右侧 (x ≈ 3.0-3.5)
- [ ] **callout 或对比标签**: 至少一条"指哪讲哪"
- [ ] 4-8 个 `self.play`, 结尾 `self.wait(1.5)` + `self.clear_stage()`

写完用蒙太奇自检: 7 格里任何一格"只有字没有图" = 返工。

## 配方 1: 定义/原理型 — "X 是什么"

适用: 振动发声、光的直线传播、分子热运动
布局: 左侧示意图 (主体 + 运动指示) + callout + 右侧 info_card

```python
# 主体 (音叉/光源/分子): 3-6 个基本图形拼
fork = VGroup(fork_l, fork_r, fork_arc, fork_handle).move_to([-3.5, -0.3, 0])
self.play(FadeIn(fork), run_time=0.5)
# 运动指示: 箭头对 / wave_arcs / 虚影
self.play(FadeIn(arr_l), FadeIn(arr_r), run_time=0.3)
self.play(Create(wave_arcs([-2.3, 0.3, 0], [0.5, 0.8, 1.1])), run_time=0.8)
# 指哪讲哪 + 要点卡
self.play(FadeIn(callout([-3.5, -0.9, 0], "振动源", [-3.5, -1.8, 0])), run_time=0.4)
self.play(FadeIn(info_card("振动发声", [...]).move_to([3.0, 0, 0]), shift=UP*0.2))
```

## 配方 2: 对比型 — "A 高 B 低 / A 大 B 小"

适用: 音调(频率)、响度(振幅)、音色(波形)、串联并联、晶体非晶体
布局: 左侧上下两条对比图 + 各自标签 + 右侧 info_card

```python
wave_low  = wave_path([-5.5,  1.0, 0], 4.5, 0.4, 2, color=ACCENT)   # 参照物
wave_high = wave_path([-5.5, -0.8, 0], 4.5, 0.4, 6, color=PRIMARY)  # 强调项
label_low  = styled_text("低音调（频率低）", "label", ACCENT).next_to(wave_low, LEFT)
# 先画参照, 再画强调项, 最后卡片
```

关键: 两条只变**一个变量** (只变频率/只变振幅), 颜色用 ACCENT(弱) vs PRIMARY(强)。

## 配方 3: 过程/流程型 — "先怎样再怎样"

适用: 光合作用、水循环、声音传到人耳、四冲程
布局: 横向 3-4 节点链 (图标 + 名称), 箭头逐个点亮, 底部或右侧 info_card

```python
nodes = VGroup(*[icon_badge(ic, name) for ic, name in [("☀","阳光"),("🍃","叶绿体"),("○","氧气")]])
nodes.arrange(RIGHT, buff=1.4).move_to([-1.0, 0.3, 0])
for i, node in enumerate(nodes):
    self.play(FadeIn(node, shift=UP*0.2), run_time=0.4)
    if i < len(nodes) - 1:
        arrow = Arrow(nodes[i].get_right(), nodes[i+1].get_left(), color=PRIMARY, buff=0.15)
        self.play(GrowArrow(arrow), run_time=0.3)
```

## 配方 4: 结构/组成型 — "由什么组成"

适用: 电路组成、眼球结构、花的结构、原子结构
布局: 中央主体图 + 3-4 条 callout 从四周指入, 不放 info_card (标注本身就是要点)

```python
circuit = VGroup(wire_top, wire_bot, wire_l, wire_r, batt, bulb).move_to([-1.5, 0, 0])
self.play(Create(circuit), run_time=1.0)
for pos, name, tpos in [([−2.4, 0, 0], "电源", [−4.2, 1.2, 0]), ...]:
    self.play(FadeIn(callout(pos, name, tpos)), run_time=0.4)   # 逐条点亮
```

## 配方 5: 定量关系型 — "公式怎么来"

适用: 杠杆原理、欧姆定律、密度、速度
布局: 左侧示意图 (变量都标在图上) + 下方公式大字 + 右侧 info_card

```python
# 图上每个变量都有 callout: F₁、L₁、F₂、L₂ 指到杠杆对应位置
formula = Text("F₁ · L₁ = F₂ · L₂", font=CJK, color=PRIMARY, weight=BOLD).scale(0.9)
formula.move_to([-2.0, -2.2, 0])
self.play(Write(formula), run_time=0.8)   # 公式最后出, 是场景的高潮
```

注意: 没装 LaTeX 就用 Text + Unicode 下标 (₁₂₃ ×·÷ ⁸), 见 manim-gotchas 坑 6。

## 配方 6: 条件/分类型 — "分几种情况"

适用: 声音传播的介质 (固/液/气)、物态变化、力的三要素
布局: 2-3 张窄 info_card 横排, 逐张滑入, 上方一行示意小图

```python
cards = [info_card(t, lines, width=2.6) for t, lines in [("固体", [...]), ("液体", [...]), ("气体", [...])]]
for i, card in enumerate(cards):
    card.move_to([-3.5 + i * 3.5, -0.5, 0])
    self.play(FadeIn(card, shift=UP * 0.25), run_time=0.45)
```

## 配方 7: 收尾型 (场景 7 固定用)

大数字/核心公式 (scale 1.6-1.8, 居中偏上) → 本章小结 info_card (width 5.0) → summary_bar 4 枚徽章。
参考 `examples/sound_phenomena.py` 的 `scene7_summary`。

## 主题图标扩展

`TITLE_ICONS` 目前有 sound/light/mechanics/electricity 四个。遇到热学/生物/数学主题,
按 `title_icon_*` 的写法现画一个 (5-8 个基本图形拼), 注册进字典, 不要留空标题页。
