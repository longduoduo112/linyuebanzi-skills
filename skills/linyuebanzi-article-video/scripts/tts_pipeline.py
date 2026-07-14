#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文章解说视频配音管线: storyboard.json → 逐句 TTS 音频 + timeline.json

与 teaching-animation 的 minimax_tts.py 同源, 区别是 **按句分段**:
每章 narration 是一个句子数组, 每句单独 TTS, 得到句级时间轴 —— 字幕逐句同步、
要点卡条目可以锚定到某一句的开口时刻。

用法:
    python3 tts_pipeline.py <project_dir> [--provider minimax|say] [--voice <id>]
                            [--speed 1.0] [--model speech-02-hd] [--skip-existing]

    project_dir 需含 storyboard.json; 输出写入 project_dir/audio/

Provider:
    minimax  (默认) 需要 MINIMAX_API_KEY
             可选: MINIMAX_GROUP_ID / MINIMAX_API_HOST / MINIMAX_TTS_MODEL
    say      macOS 内置 TTS, 零依赖, 仅预览管线用

--skip-existing: 已存在的 mp3 不重新生成 (改了某句旁白就删掉对应文件重跑)

输出:
    audio/ch-01-s01.mp3 ...      每句一个音频
    audio/timeline.json          章节 + 句级时间轴 (scaffold.py 的输入)

时间轴规则:
    章节时长 = HEAD_PAD + Σ(句时长 + GAP) - GAP + TAIL_PAD, 不低于 MIN_CHAPTER
    第一句起点 = 章节起点 + HEAD_PAD
"""

import argparse
import binascii
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# 绕过系统代理直连 (本地抓包代理的自签证书会让 TLS 校验失败; 需要走代理时
# 显式 export MINIMAX_USE_PROXY=1)
if not os.environ.get("MINIMAX_USE_PROXY"):
    urllib.request.install_opener(
        urllib.request.build_opener(urllib.request.ProxyHandler({})))

HEAD_PAD = 0.7      # 章节开头: 转场 + 标题入场喘口气
GAP = 0.18          # 句间停顿
TAIL_PAD = 0.75     # 末句结束后的画面停留
MIN_CHAPTER = 5.0
DEFAULT_VOICE = "male-qn-jingying"


def log(msg):
    print(msg, flush=True)


def die(msg):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)


def tts_minimax(text, out_path, voice_id, speed, model):
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        die("MINIMAX_API_KEY 未设置。导出后重试, 或先用 --provider say 走通管线预览。")

    host = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com").rstrip("/")
    url = f"{host}/v1/t2a_v2"
    group_id = os.environ.get("MINIMAX_GROUP_ID")
    if group_id:
        url += f"?GroupId={group_id}"

    payload = {
        "model": model,
        "text": text,
        "stream": False,
        "language_boost": "Chinese",
        "output_format": "hex",
        "voice_setting": {"voice_id": voice_id, "speed": speed, "vol": 1.0, "pitch": 0},
        "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    last_err = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            status = body.get("base_resp", {}).get("status_code")
            if status != 0:
                msg = body.get("base_resp", {}).get("status_msg", "unknown")
                if status in (1004, 2013):  # 鉴权失败 / 参数错误, 重试无意义
                    die(f"Minimax 返回错误 status_code={status}: {msg}")
                raise RuntimeError(f"status_code={status}: {msg}")
            audio_hex = body.get("data", {}).get("audio")
            if not audio_hex:
                raise RuntimeError("响应缺少 data.audio")
            out_path.write_bytes(binascii.unhexlify(audio_hex))
            return
        except (OSError, RuntimeError, ValueError) as e:  # OSError 含 URLError/连接重置
            last_err = e
            # 逐句管线请求数多, RPM 限流是常态: 限流要等满一个分钟窗口, 其他错误短退避
            wait = 21 if "1002" in str(e) else 2 * (attempt + 1)
            log(f"   ⚠ 第 {attempt + 1} 次调用失败 ({e}), {wait}s 后重试...")
            time.sleep(wait)
    die(f"Minimax TTS 连续失败: {last_err}")


def tts_say(text, out_path, voice_id, speed, model):
    voice = voice_id if voice_id and not voice_id.startswith(("male-", "female-", "presenter", "moss_")) else "Tingting"
    aiff = out_path.with_suffix(".aiff")
    rate = int(180 * speed)
    subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", str(aiff), text], check=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff),
         "-ar", "32000", "-b:a", "128k", str(out_path)],
        check=True,
    )
    aiff.unlink()


PROVIDERS = {"minimax": tts_minimax, "say": tts_say}


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir", help="含 storyboard.json 的项目目录")
    ap.add_argument("--provider", choices=list(PROVIDERS), default=None)
    ap.add_argument("--voice", default=None)
    ap.add_argument("--speed", type=float, default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--skip-existing", action="store_true",
                    help="已存在的 mp3 不重新生成 (改句子后删对应文件重跑)")
    args = ap.parse_args()

    project = Path(args.project_dir)
    sb_path = project / "storyboard.json"
    if not sb_path.exists():
        die(f"找不到 {sb_path}")
    sb = json.loads(sb_path.read_text(encoding="utf-8"))
    chapters = sb.get("chapters")
    if not chapters:
        die("storyboard.json 缺少 chapters 数组")

    voice_cfg = sb.get("voice", {})
    provider = args.provider or voice_cfg.get("provider", "minimax")
    voice_id = args.voice or voice_cfg.get("voice_id", DEFAULT_VOICE)
    speed = args.speed if args.speed is not None else float(voice_cfg.get("speed", 1.0))
    model = args.model or os.environ.get("MINIMAX_TTS_MODEL", "speech-02-hd")
    tts = PROVIDERS[provider]

    outdir = project / "audio"
    outdir.mkdir(parents=True, exist_ok=True)

    n_sent = sum(len(ch.get("narration", [])) for ch in chapters)
    log(f"==> TTS: provider={provider} voice={voice_id} speed={speed} "
        f"共 {len(chapters)} 章 {n_sent} 句"
        + (f" model={model}" if provider == "minimax" else ""))

    cursor = 0.0
    out_chapters = []
    for ch in chapters:
        cid = ch["id"]
        narration = ch.get("narration", [])
        if not narration:
            die(f"章节 {cid} 缺少 narration 句子数组")
        log(f"   [章 {cid}/{len(chapters)}] {ch.get('kicker', '')} ({len(narration)} 句)")

        sent_cursor = cursor + HEAD_PAD
        sentences = []
        for si, text in enumerate(narration, 1):
            text = text.strip()
            out_path = outdir / f"ch-{cid:02d}-s{si:02d}.mp3"
            if args.skip_existing and out_path.exists():
                log(f"      s{si:02d} 复用已有音频")
            else:
                tts(text, out_path, voice_id, speed, model)
            dur = round(probe_duration(out_path), 2)
            sentences.append({
                "text": text,
                "file": f"audio/{out_path.name}",
                "start": round(sent_cursor, 2),
                "duration": dur,
            })
            sent_cursor += dur + GAP

        content_end = sent_cursor - GAP + TAIL_PAD
        ch_dur = round(max(content_end - cursor, MIN_CHAPTER), 2)
        out_chapters.append({
            "id": cid,
            "start": round(cursor, 2),
            "duration": ch_dur,
            "sentences": sentences,
        })
        cursor += ch_dur

    timeline = {
        "topic": sb.get("topic", ""),
        "provider": provider,
        "voice_id": voice_id,
        "head_pad": HEAD_PAD,
        "gap": GAP,
        "tail_pad": TAIL_PAD,
        "total": round(cursor, 2),
        "chapters": out_chapters,
    }
    tl_path = outdir / "timeline.json"
    tl_path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")

    log(f"✅ {n_sent} 句音频 → {outdir}/  总时长 {timeline['total']}s")
    log(f"✅ 时间轴 → {tl_path}  (下一步: python3 scripts/scaffold.py {project})")


if __name__ == "__main__":
    main()
