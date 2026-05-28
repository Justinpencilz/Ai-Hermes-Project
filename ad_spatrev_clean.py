#!/usr/bin/env python3
"""
Spatrev Ad — Clean, matches Swift Algo style perfectly
- Dark canvas (same #0b0d19 as Swift Algo)
- Woman's voiceover as the ONLY audio
- Bold text captions synced to her speech
- Spatrev logo watermark (top-right, same position)
- AI image as product visual (center, like Swift Algo charts)
- CTA button at end
- NO audio patching, NO mismatched content
- 592x1280 same resolution as Swift Algo
"""

import os, math
from moviepy import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    CompositeAudioClip, ColorClip, TextClip, AudioFileClip,
)
from moviepy.video.fx import FadeIn, FadeOut

AUDIO_SOURCE = "/root/.hermes/cache/videos/video_9083bedea37d.mov"
OUTPUT = "/root/Ai-Hermes-Project/output/spatrev_clean.mp4"
TEMP_VID = OUTPUT.replace(".mp4", "_temp.mp4")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ASSETS = "/tmp/ad_assets"

W, H = 592, 1280
FPS = 30

if os.path.exists(TEMP_VID):
    os.remove(TEMP_VID)

print("🎬 Building clean Spatrev ad...")

# Extract woman's voiceover
vo = AudioFileClip(AUDIO_SOURCE)
dur = vo.duration
print(f"Voiceover: {dur:.1f}s")

# Segments timed to her speech
SEGMENTS = [
    (0.0,  3.8,  "Stop using your smartphone\nonly for scrolling."),
    (3.8,  8.5,  "The internet has created\nmany opportunities\nfor willing learners."),
    (8.5,  13.5, "Join our free WhatsApp\ncommunity to learn\ndigital skills every day."),
    (13.5, 17.5, "No complicated setup.\nNo payment to join."),
    (17.5, dur, "Click the link below\nand get started with Spatrev!"),
]

SFX = [
    (0.0,  "whoosh.wav"),
    (3.8,  "swish.wav"),
    (6.0,  "ding.wav"),
    (8.5,  "whoosh.wav"),
    (11.0, "ding.wav"),
    (13.5, "swish.wav"),
    (15.5, "ding.wav"),
    (17.5, "ding_high.wav"),
]

# ── Dark background (matches Swift Algo #0b0d19) ──
bg = ColorClip(color=(11, 13, 25), size=(W, H), duration=dur)
layers = [bg]

# ── Subtle ambient glow (adds depth like Swift Algo) ──
glow = ColorClip(color=(255, 107, 53), size=(W, int(H*0.3)), duration=dur)
glow = glow.with_opacity(0.03).with_position((0, 0))
layers.append(glow)

# ── Spatrev logo watermark (top-right) ──
logo_path = os.path.join(ASSETS, "spatrev_logo.jpg")
if os.path.exists(logo_path):
    logo = ImageClip(logo_path).resized(width=int(W * 0.18))
    logo_x = W - logo.w - 12
    logo_y = 12
    logo_clip = logo.with_position((logo_x, logo_y)).with_duration(dur)
    logo_clip = logo_clip.with_opacity(0.7).with_effects([FadeIn(0.5)])
    layers.append(logo_clip)

# ── AI Image — appears like product demo (Swift Algo style) ──
ai_path = os.path.join(ASSETS, "spatrev_ai.jpg")
if os.path.exists(ai_path):
    ai = ImageClip(ai_path)
    ai_w = int(W * 0.72)
    ai = ai.resized(width=ai_w)
    ai_x = int((W - ai.w) / 2)
    ai_y = int(H * 0.12)

    # Animate: scale-in + hold + fade
    for fi in range(10):
        t = fi / 10 * 0.4
        scale = 0.5 + 0.5 * (t / 0.4)
        sc = ai.resized(width=int(ai_w * scale))
        sx = int((W - sc.w) / 2)
        frame = sc.with_position((sx, ai_y)).with_start(3.8 + t).with_duration(0.04)
        layers.append(frame)

    # Hold with breathing (8.5s to 17.5s)
    for t_s in range(0, int((17.5 - 3.8 - 0.4) * 10)):
        t = 0.4 + t_s / 10
        breath = 1.0 + 0.008 * math.sin(t * 2.5)
        sc = ai.resized(width=int(ai_w * breath))
        sx = int((W - sc.w) / 2)
        frame = sc.with_position((sx, ai_y)).with_start(3.8 + t).with_duration(0.1)
        layers.append(frame)

    # Fade out
    for fi in range(5):
        t = fi / 5 * 0.3
        opacity = 1.0 - t / 0.3
        sc = ai.resized(width=ai_w).with_opacity(max(0.05, opacity))
        sx = int((W - sc.w) / 2)
        frame = sc.with_position((sx, ai_y)).with_start(17.5 - 0.3 + t).with_duration(0.06)
        layers.append(frame)

# ── Text captions ──
for i, (start, end, caption) in enumerate(SEGMENTS):
    seg_dur = end - start
    font_sz = max(int(W * 0.055), 20)
    
    # Semi-transparent bottom bar (moody, like Swift Algo)
    bar_h = int(H * 0.16)
    bar_y = H - bar_h - 15
    bar = ColorClip(color=(5, 7, 15), size=(W, bar_h), duration=seg_dur)
    bar = bar.with_opacity(0.85).with_position((0, bar_y))
    bar = bar.with_start(start)
    bar = bar.with_effects([FadeIn(0.25), FadeOut(0.25)])
    layers.append(bar)
    
    txt = TextClip(
        font=FONT_B,
        text=caption,
        font_size=font_sz,
        color="#FFFFFF",
        stroke_color="#FF6B35",
        stroke_width=2,
        size=(W - 30, None),
        text_align="center",
        method="caption",
    ).with_duration(seg_dur).with_position(("center", bar_y + 6))
    txt = txt.with_start(start)
    txt = txt.with_effects([FadeIn(0.3)])
    layers.append(txt)

# ── CTA button ──
cta_start = max(0, dur - 4.5)
cta_dur = dur - cta_start
btn_w = int(W * 0.78)
btn_h = int(H * 0.07)
btn_x = (W - btn_w) // 2
btn_y = H - btn_h - 60

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

# ── Audio: woman's voice + SFX ──
audio_clips = [vo]
for sfx_time, sfx_file in SFX:
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
print(f"\n✅ Clean Spatrev Ad ready: {OUTPUT}")
print(f"   Size: {size_mb:.1f} MB")
print(f"   Resolution: {W}x{H} (same as Swift Algo)")
print(f"   Audio: Woman's voiceover + sound effects")
print(f"   Visuals: Dark aesthetic, Spatrev logo + AI image, captions")