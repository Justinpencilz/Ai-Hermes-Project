#!/usr/bin/env python3
"""
Spatrev Brand Video — Swift Algo Style Replica
- Dark aesthetic matching the example
- Spatrev logo + AI image overlays
- Bold captions synced to voice
- Sound effects: whoosh, ding, swish
- Original resolution & audio preserved
"""

import os, sys, subprocess, math
import numpy as np
from moviepy import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    CompositeAudioClip, ColorClip, TextClip, AudioFileClip,
)
from moviepy.video.fx import FadeIn, FadeOut

INPUT = "/root/.hermes/cache/videos/video_9083bedea37d.mov"
OUTPUT = "/root/Ai-Hermes-Project/output/spatrev_ad.mp4"
TEMP_VID = OUTPUT.replace(".mp4", "_temp.mp4")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ASSETS = "/tmp/ad_assets"

# Clean up old temp
if os.path.exists(TEMP_VID):
    os.remove(TEMP_VID)

# ── Timed segments (matching Swift Algo pacing) ──
# Swift Algo had 5 speech segments across 15.7s
# Our video is 21.3s, so we stretch to match
SEGMENTS = [
    (0.0,  3.5,
     "Most people only use\ntheir smartphone for scrolling.",
     "spatrev_logo.jpg"),          # Show logo
    (3.5,  8.0,
     "But Spatrev AI creates\nreal opportunities\nto earn online.",
     "spatrev_ai.jpg"),            # Show AI image
    (8.0,  13.0,
     "Join our free WhatsApp\ncommunity to learn\ndigital skills every day.",
     "spatrev_logo.jpg"),          # Show logo
    (13.0, 17.5,
     "No complicated setup.\nNo payment to join.\nStart learning today.",
     "spatrev_ai.jpg"),            # Show AI image
    (17.5, 21.3,
     "Click the link below\nand get started with Spatrev!",
     None),                        # No image - just CTA
]

# ── Sound effects ──
SFX = [
    (0.0,  "whoosh.wav"),
    (3.5,  "swish.wav"),
    (5.5,  "ding.wav"),
    (8.0,  "whoosh.wav"),
    (10.5, "ding.wav"),
    (13.0, "swish.wav"),
    (15.0, "ding.wav"),
    (17.5, "whoosh.wav"),
    (19.5, "ding_high.wav"),
]

print("🎬 Building Spatrev Brand Ad (Swift Algo style)...")
video = VideoFileClip(INPUT)
dur = video.duration
W, H = video.size
print(f"Source: {W}x{H}, {dur:.1f}s")

layers = [video]

# Dark overlay (moody like Swift Algo - very subtle)
dark_overlay = ColorClip(color=(8, 10, 20), size=(W, H), duration=dur)
dark_overlay = dark_overlay.with_opacity(0.15)  # Very subtle dark tint
layers.append(dark_overlay)

for i, (start, end, caption, img_file) in enumerate(SEGMENTS):
    seg_dur = end - start

    # ── BRAND IMAGE ──
    if img_file:
        img_path = os.path.join(ASSETS, img_file)
        if os.path.exists(img_path):
            img = ImageClip(img_path)
            
            # Size appropriately
            target_w = int(W * 0.65)
            img = img.resized(width=target_w)
            img_w, img_h = img.w, img.h
            
            # Position: center horizontally, lower-upper area
            img_x = int((W - img_w) / 2)
            img_y = int(H * 0.08)  # Upper area
            
            # Scale-in animation using manual frames
            frames_count = 8
            for fi in range(frames_count):
                t = fi / frames_count * 0.35
                scale = 0.5 + 0.5 * (t / 0.35)
                sc = img.resized(width=int(target_w * scale))
                sx = int((W - sc.w) / 2)
                sy = int(H * 0.08)
                frame = sc.with_position((sx, sy)).with_start(start + t).with_duration(0.05)
                layers.append(frame)
            
            # Hold at full size with slight pulse
            hold_end = end - 0.3
            t = 0.35
            while t < (hold_end - start):
                breath = 1.0 + 0.01 * math.sin(t * 3.0)
                sc = img.resized(width=int(target_w * breath))
                sx = int((W - sc.w) / 2)
                sy = int(H * 0.08)
                frame = sc.with_position((sx, sy)).with_start(start + t).with_duration(0.08)
                layers.append(frame)
                t += 0.08
            
            # Fade out
            for fi in range(5):
                t = fi / 5 * 0.3
                opacity = 1.0 - t / 0.3
                sc = img.resized(width=target_w).with_opacity(max(0.05, opacity))
                sx = int((W - sc.w) / 2)
                sy = int(H * 0.08)
                frame = sc.with_position((sx, sy)).with_start(end - 0.3 + t).with_duration(0.06)
                layers.append(frame)

    # ── CAPTION TEXT (bottom area, like Swift Algo style - clean, centered) ──
    # Semi-transparent dark bar
    bar_h = int(H * 0.18)
    bar_y = H - bar_h - 15
    bar = ColorClip(color=(0, 0, 0), size=(W, bar_h), duration=seg_dur)
    bar = bar.with_opacity(0.8).with_position((0, bar_y))
    bar = bar.with_start(start)
    bar = bar.with_effects([FadeIn(0.25), FadeOut(0.25)])
    layers.append(bar)

    # Bold white text
    font_sz = max(int(W * 0.055), 16)
    txt = TextClip(
        font=FONT_B,
        text=caption,
        font_size=font_sz,
        color="#FFFFFF",
        stroke_color="#FF6B35",
        stroke_width=2,
        size=(W - 20, None),
        text_align="center",
        method="caption",
    ).with_duration(seg_dur).with_position(("center", bar_y + 8))
    txt = txt.with_start(start)
    txt = txt.with_effects([FadeIn(0.3)])
    layers.append(txt)

# ── CTA BUTTON (last 4 seconds) ──
cta_start = max(0, dur - 4.5)
cta_dur = dur - cta_start
btn_w = int(W * 0.78)
btn_h = int(H * 0.08)
btn_x = (W - btn_w) // 2
btn_y = H - btn_h - 65

# Spatrev brand color - warm orange accent like Swift Algo
btn_color = (255, 107, 53)  # #FF6B35

btn = ColorClip(color=btn_color, size=(btn_w, btn_h), duration=cta_dur)
btn = btn.with_opacity(0.92).with_position((btn_x, btn_y))
btn = btn.with_start(cta_start)
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

# ── SOUND EFFECTS ──
print("🔊 Adding sound effects...")
original_audio = video.audio
audio_clips = [original_audio]

for sfx_time, sfx_file in SFX:
    sfx_path = os.path.join(ASSETS, sfx_file)
    if os.path.exists(sfx_path):
        try:
            sfx_clip = AudioFileClip(sfx_path)
            sfx_clip = sfx_clip.with_start(sfx_time)
            audio_clips.append(sfx_clip)
        except Exception as e:
            print(f"  ⚠️ Couldn't load {sfx_file}: {e}")

if len(audio_clips) > 1:
    mixed_audio = CompositeAudioClip(audio_clips)
    layers[0] = video.with_audio(mixed_audio)

# ── COMPOSITE ──
print("🎬 Compositing layers...")
final = CompositeVideoClip(layers, size=(W, H))

# ── EXPORT ──
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
print(f"\n✅ Spatrev Ad ready: {OUTPUT}")
print(f"   Size: {size_mb:.1f} MB")
print(f"   Resolution: {W}x{H} (original)")
print(f"   Brand: Spatrev logo + AI image overlay")
print(f"   Sound: whoosh, ding, swish effects")
print(f"   Style: Dark theme matching Swift Algo example")