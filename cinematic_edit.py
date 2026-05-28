#!/usr/bin/env python3
"""
Cinematic Ad Editor
Upscales, color grades, adds zoom effects, text overlays, and music.
"""

import os, sys, subprocess, json
from pathlib import Path
from moviepy import (
    VideoFileClip, AudioFileClip, CompositeVideoClip,
    CompositeAudioClip, ColorClip, ImageClip, TextClip,
    concatenate_videoclips
)
from moviepy.video.fx import FadeIn, FadeOut, SlideIn

# ── Paths ──
INPUT = "/root/.hermes/cache/videos/video_9083bedea37d.mov"
MUSIC = "/tmp/bg_music.mp3"
OUTPUT = "/root/Ai-Hermes-Project/output/fernando_ad.mp4"
TEMP_PROCESSED = "/tmp/ad_processed.mp4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CANVAS_W, CANVAS_H = 1080, 1920

# ══════════════════════════════════════
# STEP 1: Upscale + Color Grade + Zoom (ffmpeg)
# ══════════════════════════════════════

print("🎬 Step 1: Upscaling, color grading, zoom effect...")

# Slow push-in zoom + cinematic color grade
# Using ffmpeg filters for speed
ffmpeg_cmd = (
    f"ffmpeg -y -i {INPUT} "
    f"-vf 'scale=1920:3408:flags=lanczos,crop=1080:1920,"
    f"eq=contrast=1.2:brightness=0.05:saturation=1.3,"
    f"colorbalance=rs=-0.1:gs=0.05:bs=0.15,"
    f"unsharp=5:5:0.8:3:3:0.4' "
    f"-c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p -an "
    f"{TEMP_PROCESSED}"
)
result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, shell=True)
if result.returncode != 0:
    print("❌ ffmpeg error:", result.stderr[-300:])
    sys.exit(1)

print("✅ Video processed — cinematic grade applied")

# ══════════════════════════════════════
# STEP 2: Build text overlays with MoviePy
# ══════════════════════════════════════

print("🎬 Step 2: Adding text overlays...")

video = VideoFileClip(TEMP_PROCESSED)
duration = video.duration
video = video.with_fps(30)

# Slow zoom-in effect (simulated via keyframes)
def zoom_in(get_frame, t):
    import numpy as np
    progress = t / duration
    zoom = 1.0 + 0.06 * (t / duration)  # 6% zoom over duration
    frame = get_frame(t)
    h, w, _ = frame.shape
    new_w = int(w / zoom)
    new_h = int(h / zoom)
    x = (w - new_w) // 2
    y = (h - new_h) // 2
    cropped = frame[y:y+new_h, x:x+new_w]
    from PIL import Image
    pil_img = Image.fromarray(cropped)
    pil_img = pil_img.resize((w, h), Image.LANCZOS)
    return np.array(pil_img)

video = video.transform(zoom_in)

# Cinematic black bars (2.35:1 aspect)
bar_height = int(CANVAS_H * 0.12)  # 12% top and bottom
top_bar = ColorClip(color=(0, 0, 0), size=(CANVAS_W, bar_height), duration=duration)
bottom_bar = ColorClip(color=(0, 0, 0), size=(CANVAS_W, bar_height), duration=duration)
top_bar = top_bar.with_position((0, 0)).with_opacity(0.7)
bottom_bar = bottom_bar.with_position((0, CANVAS_H - bar_height)).with_opacity(0.7)

layers = [video, top_bar, bottom_bar]

# ── Neon title (appears first 3s) ──
title = TextClip(
    font=FONT_BOLD, text="CINEMATIC\nMOMENTS",
    font_size=80, color="#00E5FF",
    size=(CANVAS_W, None), text_align="center",
).with_duration(min(3.5, duration)).with_position(("center", CANVAS_H // 3))
title = title.with_effects([FadeIn(0.5), FadeOut(0.5)])
layers.append(title)

# ── Subtitle ──
subtitle = TextClip(
    font=FONT, text="Captured in Motion",
    font_size=36, color="#FFFFFF", size=(CANVAS_W, None),
).with_duration(min(3.5, duration)).with_position(("center", CANVAS_H // 3 + 140))
subtitle = subtitle.with_effects([FadeIn(0.8), FadeOut(0.5)])
layers.append(subtitle)

# ── Brand bar (lower third) ──
brand_bar = ColorClip(color=(0, 229, 255), size=(CANVAS_W, 60), duration=min(4, duration))
brand_bar = brand_bar.with_opacity(0.85).with_position((0, CANVAS_H - bar_height - 60))
brand_bar = brand_bar.with_effects([SlideIn(0.5, "right"), FadeOut(0.3)])
layers.append(brand_bar)

brand_text = TextClip(
    font=FONT_BOLD, text="FERNANDO SHILOH HART",
    font_size=28, color="#FFFFFF", size=(CANVAS_W, None),
).with_duration(min(4, duration)).with_position((30, CANVAS_H - bar_height - 52))
brand_text = brand_text.with_effects([FadeIn(0.5), FadeOut(0.3)])
layers.append(brand_text)

# ── CTA (appears near end) ──
cta_start = max(duration - 5, 2)
cta = TextClip(
    font=FONT_BOLD, text="FOLLOW FOR MORE",
    font_size=50, color="#FFD700",
    size=(CANVAS_W, None),
).with_duration(min(3, duration)).with_position(("center", CANVAS_H - bar_height - 160))
cta = cta.with_start(cta_start)
cta = cta.with_effects([FadeIn(0.4)])
layers.append(cta)

# ── Bottom tagline ──
tagline = TextClip(
    font=FONT, text="Content Creator | Visual Storyteller",
    font_size=24, color="#AAAAAA", size=(CANVAS_W, None),
).with_duration(min(4, duration)).with_position(("center", CANVAS_H - bar_height - 110))
tagline = tagline.with_start(cta_start)
layers.append(tagline)

# ── Top left timestamp / watermark ──
watermark = TextClip(
    font=FONT, text="@fernando",
    font_size=20, color="#00E5FF", size=(CANVAS_W, None),
).with_duration(duration).with_position((20, bar_height + 10))
watermark = watermark.with_effects([FadeIn(0.5)])
layers.append(watermark)

# ── Fade in/out on whole video ──

# Composite
print("🎬 Compositing layers...")
final = CompositeVideoClip(layers, size=(CANVAS_W, CANVAS_H))

# ── Audio mixing ──
print("🎵 Mixing audio...")
audio_layers = []

# Original audio from video
if video.audio:
    audio_layers.append(video.audio)

# Background music
music = AudioFileClip(MUSIC)
if music.duration < duration:
    music = music.loop(duration=duration)
else:
    music = music.subclipped(0, duration)
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut, MultiplyVolume
music = music.with_effects([MultiplyVolume(0.25), AudioFadeIn(1), AudioFadeOut(2)])
audio_layers.append(music)

if len(audio_layers) > 1:
    from moviepy import CompositeAudioClip as CAC
    final = final.with_audio(CAC(audio_layers))

# ── Export ──
print("💾 Rendering final ad...")
final.write_videofile(
    OUTPUT, fps=30,
    codec="libx264", audio_codec="aac",
    threads=4, preset="medium",
)

print(f"\n✅ Ad ready: {OUTPUT}")
print(f"   Size: {os.path.getsize(OUTPUT) / 1024:.0f} KB")
print(f"   Duration: {duration:.1f}s")
print(f"   Format: {CANVAS_W}x{CANVAS_H} Story")