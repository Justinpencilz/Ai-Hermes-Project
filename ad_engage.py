#!/usr/bin/env python3
"""
Engaging Facebook Ad Edit v2
- 3 animated images placed front/center
- Sound effects: ding, whoosh, swish
- Original resolution & audio preserved
- Captions synced to script with WhatsApp CTA
"""

import os, sys, subprocess, math
import numpy as np
from moviepy import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    CompositeAudioClip, ColorClip, TextClip, AudioFileClip,
)
from moviepy.video.fx import FadeIn, FadeOut

INPUT = "/root/.hermes/cache/videos/video_9083bedea37d.mov"
OUTPUT = "/root/Ai-Hermes-Project/output/ad_final.mp4"
TEMP_VID = OUTPUT.replace(".mp4", "_temp.mp4")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ASSETS = "/tmp/ad_assets"

# ── 3 Images only ──
# Format: (start, end, image_file, caption_text)
SEGMENTS = [
    (0.0,  6.5,  "scrolling.jpg",
     "Stop using your smartphone\nonly for scrolling.\n\nThe internet has created\nmany opportunities..."),
    (6.5,  13.0, "online_money.jpg",
     "Join our free WhatsApp\ncommunity to learn\ndigital skills every day.\n\nNo complicated setup.\nNo payment to join."),
    (13.0, 21.3, "community.jpg",
     "Click the WhatsApp link below\nand get started today!"),
]

# ── Sound effect placements ──
# (time, sfx_file)
SFX = [
    (0.0,  "whoosh.wav"),      # First image appears
    (2.5,  "ding.wav"),        # "Stop scrolling" emphasis
    (5.0,  "swish.wav"),       # "opportunities" emphasis
    (6.5,  "whoosh.wav"),      # Second image appears
    (9.0,  "ding.wav"),        # "WhatsApp community" emphasis
    (12.0, "swish.wav"),       # "No payment" emphasis
    (13.0, "whoosh.wav"),      # Third image appears
    (16.0, "ding.wav"),        # CTA emphasis
    (19.0, "ding_high.wav"),   # Final emphasis
]

print("🎬 Building enhanced ad v2...")
video = VideoFileClip(INPUT)
dur = video.duration
W, H = video.size
print(f"Source: {W}x{H}, {dur:.1f}s")

# ──────────────────────────────
# LAYERS: [video + image overlays + text + CTA + SFX]
# ──────────────────────────────
layers = [video]

for i, (start, end, img_file, caption) in enumerate(SEGMENTS):
    seg_dur = end - start

    # ── ANIMATED IMAGE ──
    img_path = os.path.join(ASSETS, img_file)
    if not os.path.exists(img_path):
        # Try alternate extensions
        for ext in ["jpg", "jpeg", "png", "webp"]:
            cand = os.path.join(ASSETS, img_file.rsplit(".", 1)[0] + "." + ext)
            if os.path.exists(cand):
                img_path = cand
                break

    if os.path.exists(img_path):
        img = ImageClip(img_path)

        # Responsive sizing - fit nicely in frame
        target_w = int(W * 0.75)
        img = img.resized(width=target_w)
        img_w, img_h = img.w, img.h

        # Position: centered horizontally, upper-middle vertically
        img_x = int((W - img_w) / 2)
        img_y = int(H * 0.12)  # Upper-middle, not at top

        # ── ANIMATION: scale-in effect ──
        # Use a lambda-based position animation for breathing/scale effect
        # But for simplicity, we'll create frames with time-varying scale

        # Create animated versions using with_effects approach
        # Start slightly scaled down, animate to full size
        def make_animated_img(clip, seg_dur, start_t):
            """Create an image with scale-in + subtle breathing animation"""
            frames = []

            # Phase 1: Scale in (0 to 0.4s)
            scale_in_frames = 12
            for fi in range(scale_in_frames):
                t = fi / scale_in_frames * 0.4
                scale = 0.6 + 0.4 * (t / 0.4)
                scaled = clip.resized(width=int(target_w * scale))
                # Center position
                sx = int((W - scaled.w) / 2)
                sy = int(H * 0.12)
                frame = scaled.with_position((sx, sy)).with_start(start_t + t).with_duration(0.03)
                frames.append(frame)

            # Phase 2: Hold at full with subtle pulse
            hold_end = seg_dur - 0.3
            t = 0.4
            while t < hold_end:
                # Subtle breathing: 0.98 to 1.02 every 2 seconds
                breath = 1.0 + 0.015 * math.sin(t * 2.5)
                sc = clip.resized(width=int(target_w * breath))
                sx = int((W - sc.w) / 2)
                sy = int(H * 0.12)
                frame = sc.with_position((sx, sy)).with_start(start_t + t).with_duration(0.1)
                frames.append(frame)
                t += 0.1

            # Phase 3: Fade out
            if seg_dur > 0.5:
                fade_start = start_t + seg_dur - 0.3
                fi = 0
                while fi < 6:
                    t = fi / 6 * 0.3
                    opacity = 1.0 - t / 0.3
                    sc = clip.resized(width=target_w).with_opacity(max(0.05, opacity))
                    sx = int((W - sc.w) / 2)
                    sy = int(H * 0.12)
                    frame = sc.with_position((sx, sy)).with_start(fade_start + t).with_duration(0.05)
                    frames.append(frame)
                    fi += 1

            return frames

        animated_frames = make_animated_img(img, seg_dur, start)
        layers.extend(animated_frames)

    # ── BOLD CAPTION TEXT ──
    # Semi-transparent background bar at bottom
    bar_h = int(H * 0.18)
    bar_y = H - bar_h - 10
    bar = ColorClip(color=(0, 0, 0), size=(W, bar_h), duration=seg_dur)
    bar = bar.with_opacity(0.75).with_position((0, bar_y))
    bar = bar.with_start(start)
    bar = bar.with_effects([FadeIn(0.2), FadeOut(0.2)])
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

# ── CTA BUTTON (last 3 seconds) ──
cta_start = max(0, dur - 4.0)
cta_dur = dur - cta_start
btn_w = int(W * 0.75)
btn_h = int(H * 0.08)
btn_x = (W - btn_w) // 2
btn_y = H - btn_h - 60

btn = ColorClip(color=(37, 211, 102), size=(btn_w, btn_h), duration=cta_dur)
btn = btn.with_opacity(0.9).with_position((btn_x, btn_y))
btn = btn.with_start(cta_start)
layers.append(btn)

btn_txt = TextClip(
    font=FONT_B,
    text="JOIN FREE →",
    font_size=max(int(W * 0.06), 18),
    color="#FFFFFF",
    size=(W, None),
).with_duration(cta_dur).with_position(("center", btn_y + 5))
btn_txt = btn_txt.with_start(cta_start)
btn_txt = btn_txt.with_effects([FadeIn(0.3)])
layers.append(btn_txt)

# ── SOUND EFFECTS ──
print("🔊 Adding sound effects...")
# Load the original audio
original_audio = video.audio
audio_clips = [original_audio]

for sfx_time, sfx_file in SFX:
    sfx_path = os.path.join(ASSETS, sfx_file)
    if os.path.exists(sfx_path):
        try:
            sfx_clip = AudioFileClip(sfx_path)
            # Trim if longer than needed
            sfx_clip = sfx_clip.with_start(sfx_time)
            audio_clips.append(sfx_clip)
        except Exception as e:
            print(f"  ⚠️ Couldn't load {sfx_file}: {e}")

# Mix all audio
if len(audio_clips) > 1:
    mixed_audio = CompositeAudioClip(audio_clips)
    video_with_audio = video.with_audio(mixed_audio)
    # Replace in layers
    layers[0] = video_with_audio

# ── COMPOSITE ──
print("🎬 Compositing layers...")
final = CompositeVideoClip(layers, size=(W, H))

# ── EXPORT ──
print("💾 Rendering video (CRF 18)...")
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

# ── Mux with original audio (preserve original audio track) ──
# Since we mixed SFX with original audio above, we skip separate muxing
# Just rename
if os.path.exists(TEMP_VID):
    if os.path.exists(OUTPUT):
        os.remove(OUTPUT)
    os.rename(TEMP_VID, OUTPUT)

size_mb = os.path.getsize(OUTPUT) / (1024*1024)
print(f"\n✅ Ad v2 ready: {OUTPUT}")
print(f"   Size: {size_mb:.1f} MB")
print(f"   Resolution: {W}x{H} (original)")
print(f"   Images: 3 (scrolling → online_money → community)")
print(f"   Effects: scale-in + breathing animation, sound effects")