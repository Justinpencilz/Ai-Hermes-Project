#!/usr/bin/env python3
"""
Spatrev Ad — Fresh Build, Swift Algo Style
- Dark kinetic typography ad
- NO woman's video footage
- Spatrev logo + AI image as main visuals
- Woman's voiceover as audio
- Text captions synced to voice
- Sound effects matching transitions
"""

import os, subprocess, math, numpy as np
from moviepy import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    CompositeAudioClip, ColorClip, TextClip, AudioFileClip,
)
from moviepy.video.fx import FadeIn, FadeOut

AUDIO_ONLY = "/root/.hermes/cache/videos/video_9083bedea37d.mov"
OUTPUT = "/root/Ai-Hermes-Project/output/spatrev_fresh.mp4"
TEMP_VID = OUTPUT.replace(".mp4", "_temp.mp4")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ASSETS = "/tmp/ad_assets"

W, H = 592, 1280  # Same resolution as Swift Algo example
FPS = 30

if os.path.exists(TEMP_VID):
    os.remove(TEMP_VID)

print("🎬 Building fresh Spatrev ad — Swift Algo style...")

# ── Extract audio from woman's video ──
print("🔊 Extracting voiceover audio...")
vo = AudioFileClip(AUDIO_ONLY)
audio_dur = vo.duration
print(f"   Voiceover duration: {audio_dur:.1f}s")

# ── Segments with text + timing ──
SEGMENTS = [
    (0.0,  4.0,  "Stop using your smartphone\nonly for scrolling.",                          "spatrev_logo.jpg"),
    (4.0,  8.5,  "The internet has created\nmany opportunities\nfor willing learners.",      None),
    (8.5,  13.0, "Join our free WhatsApp\ncommunity to learn\ndigital skills every day.",     "spatrev_ai.jpg"),
    (13.0, 17.0, "No complicated setup.\nNo payment to join.",                                None),
    (17.0, 21.3, "Click the link below\nand get started with Spatrev!",                       "spatrev_logo.jpg"),
]

SFX_TIMING = [
    (0.0,  "whoosh.wav"),
    (4.0,  "swish.wav"),
    (6.0,  "ding.wav"),
    (8.5,  "whoosh.wav"),
    (10.5, "ding.wav"),
    (13.0, "swish.wav"),
    (15.0, "ding.wav"),
    (17.0, "whoosh.wav"),
    (19.0, "ding_high.wav"),
]

# ── Build base ──
# Dark background (Swift Algo dark navy)
bg = ColorClip(color=(8, 10, 22), size=(W, H), duration=audio_dur)
layers = [bg]

# ── Spatrev logo watermark (top-right, always visible) ──
logo_path = os.path.join(ASSETS, "spatrev_logo.jpg")
if os.path.exists(logo_path):
    logo = ImageClip(logo_path).resized(width=int(W * 0.2))
    logo_x = W - logo.w - 15
    logo_y = 15
    logo_clip = logo.with_position((logo_x, logo_y)).with_duration(audio_dur)
    logo_clip = logo_clip.with_opacity(0.6).with_effects([FadeIn(0.5)])
    layers.append(logo_clip)

# ── Subtle animated background particle/gradient ──
# Create a subtle moving highlight on the dark background
for i in range(0, int(audio_dur), 4):
    # Moving highlight dot
    t = float(i)
    x = int(W * (0.3 + 0.4 * (0.5 + 0.5 * math.sin(t * 0.5))))
    y = int(H * (0.2 + 0.6 * (0.5 + 0.5 * math.cos(t * 0.3))))
    glow = ColorClip(color=(255, 107, 53), size=(int(W*0.15), int(W*0.15)), duration=2.0)
    glow = glow.with_opacity(0.04).with_position((x - glow.w//2, y - glow.h//2)).with_start(t)
    layers.append(glow)

# ── Process each segment ──
for i, (start, end, caption, img_file) in enumerate(SEGMENTS):
    seg_dur = end - start

    # ── Brand Image Overlay ──
    if img_file:
        img_path = os.path.join(ASSETS, img_file)
        if os.path.exists(img_path):
            img = ImageClip(img_path)
            img_w = int(W * 0.7)
            img = img.resized(width=img_w)
            img_x = int((W - img.w) / 2)
            img_y = int(H * 0.1)

            # Scale-in animation (from 0.5 to 1.0)
            frames_n = 10
            for fi in range(frames_n):
                ft = fi / frames_n * 0.4
                scale = 0.5 + 0.5 * (ft / 0.4)
                sc = img.resized(width=int(img_w * scale))
                sx = int((W - sc.w) / 2)
                sy = int(H * 0.1)
                frame = sc.with_position((sx, sy)).with_start(start + ft).with_duration(0.04)
                layers.append(frame)

            # Hold with breathing
            hold_end = end - 0.3
            t = 0.4
            while t < (hold_end - start):
                breath = 1.0 + 0.01 * math.sin(t * 2.5)
                sc = img.resized(width=int(img_w * breath))
                sx = int((W - sc.w) / 2)
                sy = int(H * 0.1)
                frame = sc.with_position((sx, sy)).with_start(start + t).with_duration(0.08)
                layers.append(frame)
                t += 0.08

            # Fade out
            for fi in range(5):
                ft = fi / 5 * 0.3
                opacity = 1.0 - ft / 0.3
                sc = img.resized(width=img_w).with_opacity(max(0.05, opacity))
                sx = int((W - sc.w) / 2)
                sy = int(H * 0.1)
                frame = sc.with_position((sx, sy)).with_start(end - 0.3 + ft).with_duration(0.06)
                layers.append(frame)

    # ── Bold caption text ──
    font_sz = max(int(W * 0.06), 22)
    txt = TextClip(
        font=FONT_B,
        text=caption,
        font_size=font_sz,
        color="#FFFFFF",
        stroke_color="#FF6B35",
        stroke_width=3,
        size=(W - 40, None),
        text_align="center",
        method="caption",
    ).with_duration(seg_dur).with_position(("center", "center"))
    txt = txt.with_start(start)
    txt = txt.with_effects([FadeIn(0.35)])
    layers.append(txt)

# ── CTA Button (last 4 seconds) ──
cta_start = max(0, audio_dur - 4.5)
cta_dur = audio_dur - cta_start
btn_w = int(W * 0.78)
btn_h = int(H * 0.07)
btn_x = (W - btn_w) // 2
btn_y = H - btn_h - 70

btn = ColorClip(color=(255, 107, 53), size=(btn_w, btn_h), duration=cta_dur)
btn = btn.with_opacity(0.92).with_position((btn_x, btn_y))
btn = btn.with_start(cta_start)
btn = btn.with_effects([FadeIn(0.3)])
layers.append(btn)

btn_txt = TextClip(
    font=FONT_B,
    text="JOIN SPATREV FREE →",
    font_size=max(int(W * 0.055), 20),
    color="#FFFFFF",
    size=(W, None),
).with_duration(cta_dur).with_position(("center", btn_y + 6))
btn_txt = btn_txt.with_start(cta_start)
btn_txt = btn_txt.with_effects([FadeIn(0.3)])
layers.append(btn_txt)

# ── Sound effects ──
audio_clips = [vo]
for sfx_time, sfx_file in SFX_TIMING:
    sfx_path = os.path.join(ASSETS, sfx_file)
    if os.path.exists(sfx_path):
        try:
            sfx = AudioFileClip(sfx_path).with_start(sfx_time)
            audio_clips.append(sfx)
        except:
            pass

mixed_audio = CompositeAudioClip(audio_clips) if len(audio_clips) > 1 else audio_clips[0]

# ── Composite ──
print("🎬 Compositing...")
final = CompositeVideoClip(layers, size=(W, H)).with_audio(mixed_audio)

# ── Export ──
print("💾 Rendering (CRF 18)...")
final.write_videofile(
    TEMP_VID,
    fps=FPS,
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
print(f"\n✅ Spatrev Fresh Ad ready: {OUTPUT}")
print(f"   Size: {size_mb:.1f} MB")
print(f"   Resolution: {W}x{H}")
print(f"   Audio: Woman's original voiceover + SFX")
print(f"   Visuals: Dark theme, Spatrev logo + AI image, bold text")