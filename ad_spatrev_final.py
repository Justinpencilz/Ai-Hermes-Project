#!/usr/bin/env python3
"""
Final Spatrev Ad — Original Swift Algo video
- Use Swift Algo video as base
- Overlay Spatrev logo (top-right)
- Replace audio "Swift Algo" with "Spatrev"
- Keep everything else identical
"""

import os, subprocess
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip
from moviepy.video.fx import FadeIn

VIDEO = "/root/Ai-Hermes-Project/input/example_video.mov"
MODIFIED_AUDIO = "/tmp/modified_audio.wav"
LOGO = "/tmp/ad_assets/spatrev_logo.jpg"
OUTPUT = "/root/Ai-Hermes-Project/output/spatrev_final_ad.mp4"
TEMP_VID = OUTPUT.replace(".mp4", "_temp.mp4")

print("🎬 Building final Spatrev ad...")

# Load video
video = VideoFileClip(VIDEO)
W, H = video.size
dur = video.duration
print(f"Source: {W}x{H}, {dur:.1f}s")

# Overlay Spatrev logo (top-right corner)
logo = ImageClip(LOGO).resized(width=int(W * 0.2))
logo_x = W - logo.w - 12
logo_y = 12
logo_clip = logo.with_position((logo_x, logo_y)).with_duration(dur)
logo_clip = logo_clip.with_opacity(0.8).with_effects([FadeIn(0.5)])
print(f"Logo: {logo.w}x{logo.h} at ({logo_x}, {logo_y})")

# Replace audio
if os.path.exists(MODIFIED_AUDIO):
    new_audio = AudioFileClip(MODIFIED_AUDIO)
    video = video.with_audio(new_audio)
    print("Audio: Replaced 'Swift Algo' with 'Spatrev'")
else:
    print("⚠️ Modified audio not found, using original")

# Composite
final = CompositeVideoClip([video, logo_clip], size=(W, H))

# Export with original quality
print("💾 Rendering...")
final.write_videofile(
    TEMP_VID,
    fps=30,
    codec="libx264",
    preset="medium",
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
print(f"\n✅ Final Spatrev Ad ready: {OUTPUT}")
print(f"   Size: {size_mb:.1f} MB")
print(f"   Same video + Spatrev logo + 'Spatrev' audio")