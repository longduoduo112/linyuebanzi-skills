#!/usr/bin/env bash
# Manim 教学动图 渲染管线
# 用法: ./render.sh <topic_py> <SceneClass> [quality]
#   quality: qm (720p30 默认) | qh (1080p60) | ql (480p15)
# 输出:
#   outputs/<scene-kebab>.mp4   (按 ClassName 自动转 kebab-case)
#   outputs/<scene-kebab>.gif   (720p, 20fps, 调色板优化)
#   preview/montage.png         (7 场景蒙太奇)

set -euo pipefail

# ---- 工具路径: 默认走 PATH, 特殊环境用环境变量覆盖 ----
MANIM=${MANIM:-manim}
FFMPEG=${FFMPEG:-ffmpeg}
FFPROBE=${FFPROBE:-ffprobe}
for tool in "$MANIM" "$FFMPEG" "$FFPROBE"; do
  command -v "$tool" >/dev/null || { echo "❌ 找不到 $tool (可用 MANIM=/path/to/manim 等环境变量指定)"; exit 1; }
done

# ---- 解析参数 ----
if [[ $# -lt 2 ]]; then
  echo "用法: $0 <topic_py> <SceneClass> [quality]"
  echo "  例: $0 light_phenomena.py LightPhenomena qm"
  exit 1
fi
TOPIC_PY=$1
SCENE_CLASS=$2
QUALITY=${3:-qm}

# 转 ClassName → kebab-case: LightPhenomena → light-phenomena
KEBAB=$(python3 -c "import re,sys; print(re.sub(r'(?<=[a-z])(?=[A-Z])', '-', sys.argv[1]).lower())" "$SCENE_CLASS")

# ---- 准备目录 ----
mkdir -p outputs preview

# ---- 1. 渲染 MP4 ----
echo "==> 渲染 $SCENE_CLASS ($QUALITY)..."
$MANIM -$QUALITY "$TOPIC_PY" "$SCENE_CLASS" 2>&1 | tail -3

# 找输出文件
if [[ "$QUALITY" == "qh" ]]; then
  RENDER_DIR="media/videos/$(basename ${TOPIC_PY%.py})/1080p60"
else
  RENDER_DIR="media/videos/$(basename ${TOPIC_PY%.py})/720p30"
fi
RENDERED="$RENDER_DIR/${SCENE_CLASS}.mp4"
if [[ ! -f "$RENDERED" ]]; then
  echo "❌ 渲染产物未找到: $RENDERED"
  exit 1
fi

mv "$RENDERED" "outputs/${KEBAB}.mp4"
echo "✅ MP4: outputs/${KEBAB}.mp4"

# ---- 2. 生成 GIF (固定 720p, 20fps, 调色板优化; >2MB 自动降级重编) ----
echo "==> 生成 GIF..."
$FFMPEG -y -i "outputs/${KEBAB}.mp4" \
  -vf "fps=20,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" \
  "outputs/${KEBAB}.gif" 2>&1 | tail -2

GIF_LIMIT=2097152   # 2MB, 公众号内嵌自动播放的硬约束
GIF_BYTES=$(wc -c < "outputs/${KEBAB}.gif" | tr -d ' ')
if [[ "$GIF_BYTES" -gt "$GIF_LIMIT" ]]; then
  echo "⚠ GIF $(($GIF_BYTES / 1024))KB 超 2MB, 降级重编 (15fps, 64 色, 640p)..."
  $FFMPEG -y -i "outputs/${KEBAB}.mp4" \
    -vf "fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=64[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" \
    "outputs/${KEBAB}.gif" 2>&1 | tail -2
  GIF_BYTES=$(wc -c < "outputs/${KEBAB}.gif" | tr -d ' ')
  if [[ "$GIF_BYTES" -gt "$GIF_LIMIT" ]]; then
    echo "❌ 降级后仍 $(($GIF_BYTES / 1024))KB > 2MB — 视频太长, 考虑压缩场景时长"
  fi
fi
echo "✅ GIF: outputs/${KEBAB}.gif ($(($GIF_BYTES / 1024))KB)"

# ---- 3. 抽帧 + 蒙太奇 (7 段各取中点, 避开段首清场/转场的空帧) ----
echo "==> 抽帧 + 蒙太奇..."
DUR=$($FFPROBE -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "outputs/${KEBAB}.mp4")
TIMES=$(python3 -c "
d = float('$DUR')
print(' '.join(f'{d / 7 * (i + 0.5):.2f}' for i in range(7)))")
mkdir -p preview/.frames && rm -f preview/.frames/*.png
i=1
for T in $TIMES; do
  $FFMPEG -y -loglevel error -ss "$T" -i "outputs/${KEBAB}.mp4" -frames:v 1 "preview/.frames/f-$i.png"
  i=$((i + 1))
done
$FFMPEG -y -loglevel error -framerate 1 -i "preview/.frames/f-%d.png" \
  -vf "scale=480:-1,tile=2x4:padding=12" -frames:v 1 -update 1 "preview/montage.png"
rm -rf preview/.frames
echo "✅ 蒙太奇: preview/montage.png"

# ---- 4. 打印元信息 ----
echo ""
echo "==> 输出元信息:"
$FFPROBE -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate \
  -of default=noprint_wrappers=1 "outputs/${KEBAB}.mp4"
echo ""
echo "完成。文件:"
ls -lh "outputs/${KEBAB}".{mp4,gif} "preview/montage.png"
