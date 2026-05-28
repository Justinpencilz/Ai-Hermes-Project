#!/usr/bin/env python3
"""
Spatrev Brand Ad — Exact Swift Algo Style Match
- NO text caption bars (just voiceover like Swift Algo)
- Dark aesthetic moody overlay
- Spatrev logo as subtle watermark
- AI image as product overlay at key moments
- Clean, professional, minimalist
- CTA button at end only
"""

import os, subprocess, math
from moviepy import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    CompositeAudioClip, ColorClip, TextClip, AudioFileClip,
)
from moviepy.video.fx import FadeIn, FadeOut

INPUT = "/root/.hermes/cache/videos/video_9083bedea37d.mov"
OUTPUT = "/root/Ai-Hermes-Project/output/spatrev_ad_v2.mp4"
TEMP_VID = OUTPUT.replace(".mp4", "_temp.mp4")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ASSETS = "/tmp/ad_assets"

if os.path.exists(TEMP_VID):
    os.remove(TEMP_VID)

print("🎬 Building Spatrev Ad — exact Swift Algo style...")
video = VideoFileClip(INPUT)
dur = video.duration
W, H = video.size
print(f"Source: {W}x{H}, {dur:.1f}s")

layers = [video]

# ── Subtle dark vignette overlay (moody like Swift Algo) ──
vignette = ColorClip(color=(5, 7, 15), size=(W, H), duration=dur)
vignette = vignette.with_opacity(0.12)  # Very subtle dark tint
layers.append(vignette)

# ── Spatrev Logo — corner watermark (always visible, subtle) ──
logo_path = os.path.join(ASSETS, "spatrev_logo.jpg")
if os.path.exists(logo_path):
    logo = ImageClip(logo_path)
    logo_w = int(W * 0.25)  # Small watermark
    logo = logo.resized(width=logo_w)
    # Position: top-right corner
    logo_x = W - logo_w - 12
    logo_y = 12
    logo_clip = logo.with_position((logo_x, logo_y)).with_duration(dur)
    logo_clip = logo_clip.with_opacity(0.7).with_effects([FadeIn(0.5)])
    layers.append(logo_clip)

# ── AI Image — appears in center like Swift Algo product demo ──
ai_path = os.path.join(ASSETS, "spatrev_ai.jpg")
if os.path.exists(ai_path):
    ai = ImageClip(ai_path)
    ai_w = int(W * 0.7)  # Prominent but not full width
    ai = ai.resized(width=ai_w)
    ai_x = int((W - ai.w) / 2)
    ai_y = int(H * 0.15)  # Center-upper area (product demo position)

    # Fade in at 3.5s, hold for ~8s, fade out
    ai_start = 3.5
    ai_dur = 10.0
    ai_clip = ai.with_position((ai_x, ai_y)).with_duration(ai_dur).with_start(ai_start)
    ai_clip = ai_clip.with_effects([FadeIn(0.8), FadeOut(0.6)])
    layers.append(ai_clip)

# ── CTA Button — last 4 seconds only ──
cta_start = max(0, dur - 4.5)
cta_dur = dur - cta_start
btn_w = int(W * 0.8)
btn_h = int(H * 0.08)
btn_x = (W - btn_w) // 2
btn_y = H - btn_h - 50

btn = ColorClip(color=(255, 107, 53), size=(btn_w, btn_h), duration=cta_dur)
btn = btn.with_opacity(0.92).with_position((btn_x, btn_y))
btn = btn.with_start(cta_start)
btn = btn.with_effects([FadeIn(0.3)])
layers.append(btn)

btn_txt = TextClip(
    font=FONT_B,
    text="JOIN SPATREV FREE →",
    font_size=max(int(W * 0.06), 18),
    color="#FFFFFF",
    size=(W, None),
).with_duration(cta_dur).with_position(("center", btn_y + 5))
btn_txt = btn_txt.with_start(cta_start)
btn_txt = btn_txt.with_effects([FadeIn(0.3)])
layers.append(btn_txt)

# ── Subtle sound effects ──
sfx_list = [
    (3.5,  "whoosh.wav"),    # AI image appears
    (8.0,  "ding.wav"),      # Mid-point emphasis
    (13.5, "swish.wav"),     # Transition
    (cta_start, "ding.wav"), # CTA appears
]

original_audio = video.audio
audio_clips = [original_audio]

for sfx_time, sfx_file in sfx_list:
    sfx_path = os.path.join(ASSETS, sfx_file)
    if os.path.exists(sfx_path):
        try:
            sfx = AudioFileClip(sfx_path).with_start(sfx_time)
            audio_clips.append(sfx)
        except:
            pass

if len(audio_clips) > 1:
    layers[0] = video.with_audio(CompositeAudioClip(audio_clips))

# ── Composite ──
print("🎬 Compositing...")
final = CompositeVideoClip(layers, size=(W, H))

# ── Export ──
print("💾 Rendering (CRF 18)...")
final.write_videofile(
    TEMP_VID,
    fps=30,
    codec="libx264",
    preset="slow",
    ffmpeg_params=["-crf", "18"],
    audio_codec="aac",
    audio_bitrate="192k",
    threads=4,
)

if os.path.exists(TEMP_VID):
    if os.path.exists(OUTPUT):
        os.remove(OUTPUT)
    os.rename(TEMP_VID, OUTPUT)

size_mb = os.path.getsize(OUTPUT) / (1024*1024)
print(f"\n✅ Spatrev v2 ready: {OUTPUT}")
print(f"   Size: {size_mb:.1f} MB")
print(f"   Style: Exact Swift Algo match — clean, dark, no text bars")