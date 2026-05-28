#!/usr/bin/env python3
"""
Build a Facebook ad from a YAML config file.
Reads input/ad_config.yaml, processes video + images + text.
"""

import os
import sys
import yaml
from pathlib import Path
from moviepy import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    AudioFileClip, CompositeAudioClip, ColorClip,
)
from moviepy.video.fx import FadeIn, FadeOut, SlideIn
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut, MultiplyVolume

from effects.kinetic_text import kinetic_title, kinetic_body
from effects.lower_thirds import lower_third_name, cta_button
from effects.transitions import crossfade, slide_transition

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

PROJECT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = PROJECT_DIR / "input"
OUTPUT_DIR = PROJECT_DIR / "output"


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _resolve_position(pos_str, canvas_w=1080, canvas_h=1080, obj_w=0, obj_h=0):
    """Convert named position to pixel coordinates."""
    if isinstance(pos_str, list):
        return tuple(pos_str)
    if pos_str == "center":
        return ((canvas_w - obj_w) // 2, (canvas_h - obj_h) // 2)
    if pos_str == "top-left":
        return (20, 20)
    if pos_str == "top-right":
        return (canvas_w - obj_w - 20, 20)
    if pos_str == "bottom-left":
        return (20, canvas_h - obj_h - 20)
    if pos_str == "bottom-right":
        return (canvas_w - obj_w - 20, canvas_h - obj_h - 20)
    if pos_str == "top":
        return ((canvas_w - obj_w) // 2, 20)
    if pos_str == "bottom":
        return ((canvas_w - obj_w) // 2, canvas_h - obj_h - 20)
    return ("center", "center")


def load_config(config_path):
    with open(config_path) as f:
        data = yaml.safe_load(f)
    return data.get("ad", data)


def build_from_config(config_path):
    """Build an ad from a YAML config file."""
    cfg = load_config(config_path)

    video_path = INPUT_DIR / cfg.get("video", "")
    preset = cfg.get("preset", "square")
    output_name = cfg.get("output", "output.mp4")
    output_path = OUTPUT_DIR / output_name

    # ── Preset dimensions ──
    presets = {
        "square": (1080, 1080),
        "story": (1080, 1920),
        "landscape": (1920, 1080),
    }
    canvas_w, canvas_h = presets.get(preset, (1080, 1080))

    # ── Load video ──
    print(f"📹 Loading video: {video_path.name}")
    video = VideoFileClip(str(video_path))
    video = video.resized(width=canvas_w)
    if video.h > canvas_h:
        video = video.cropped(y_center=video.h / 2, height=canvas_h)
    elif video.h < canvas_h:
        bg = ColorClip(color=(26, 26, 46), size=(canvas_w, canvas_h), duration=video.duration)
        video = CompositeVideoClip([bg, video.with_position(("center", "center"))],
                                    size=(canvas_w, canvas_h))
    video = video.with_fps(30)

    # ── Build layer stack ──
    layers = [video.with_effects([FadeIn(0.5), FadeOut(0.5)])]

    # ── Background image ──
    img_cfg = cfg.get("images", {})
    bg_path = img_cfg.get("background", "")
    if bg_path and (INPUT_DIR / bg_path).exists():
        print(f"🖼️ Background: {bg_path}")
        from effects.image_overlay import image_background
        bg_clip = image_background(
            str(INPUT_DIR / bg_path),
            duration=video.duration,
            darken=img_cfg.get("background_darken", 0.0),
        )
        layers.insert(0, bg_clip)  # Behind video

    # ── Logo image ──
    logo_path = img_cfg.get("logo", "")
    if logo_path and (INPUT_DIR / logo_path).exists():
        print(f"🏷️ Logo: {logo_path}")
        logo_size = img_cfg.get("logo_size", [120, 120])
        from effects.image_overlay import logo_overlay
        logo_pos = img_cfg.get("logo_position", "top-left")
        pos = _resolve_position(logo_pos, canvas_w, canvas_h, logo_size[0], logo_size[1])
        logo = logo_overlay(
            str(INPUT_DIR / logo_path),
            position=pos,
            size=tuple(logo_size),
            duration=video.duration,
        )
        layers.append(logo)

    # ── Product image ──
    prod_path = img_cfg.get("product", "")
    if prod_path and (INPUT_DIR / prod_path).exists():
        print(f"📦 Product shot: {prod_path}")
        prod_size = img_cfg.get("product_size", [400, 400])
        from effects.image_overlay import product_shot
        prod_pos = img_cfg.get("product_position", "center")
        pos = _resolve_position(prod_pos, canvas_w, canvas_h, prod_size[0], prod_size[1])
        prod = product_shot(
            str(INPUT_DIR / prod_path),
            position=pos,
            size=tuple(prod_size),
            duration=min(video.duration, 4),
            animation=img_cfg.get("product_animation", "zoom_in"),
        )
        layers.append(prod)

    # ── Headline ──
    headline = cfg.get("headline", "")
    if headline:
        print(f"📝 Headline: {headline}")
        title = kinetic_title(
            text=headline,
            font_size=72 if preset == "square" else 56,
            color="#FF6B35",
            duration=min(video.duration, 3.5),
            animation="slide_up",
            position=("center", 80),
        )
        layers.append(title)

    # ── Body text ──
    body = cfg.get("body", [])
    if body:
        print(f"📝 Body: {len(body)} line(s)")
        body_clip = kinetic_body(
            lines=body,
            font_size=36,
            color="#FFFFFF",
            line_duration=min(video.duration, 3),
            stagger=0.3,
        )
        layers.append(body_clip)

    # ── CTA button ──
    cta_text = cfg.get("cta", "")
    if cta_text:
        print(f"🔘 CTA: {cta_text}")
        cta = cta_button(
            text=cta_text,
            font_size=36,
            duration=min(video.duration, 4),
            position=("center", canvas_h - 150),
        )
        layers.append(cta)

    # ── Brand / lower third ──
    brand = cfg.get("brand", {})
    brand_name = brand.get("name", "")
    if brand_name:
        print(f"🏷️ Brand: {brand_name}")
        lower = lower_third_name(
            name=brand_name,
            title=brand.get("tagline", ""),
            duration=min(video.duration, 4),
        )
        layers.append(lower)

    # ── Composite ──
    print("🎬 Compositing...")
    final = CompositeVideoClip(layers, size=(canvas_w, canvas_h))

    # ── Audio ──
    audio_cfg = cfg.get("audio", {})
    music_path = audio_cfg.get("music", "")
    voiceover_path = audio_cfg.get("voiceover", "")

    audio_layers = [final.audio] if final.audio else []

    if music_path and (INPUT_DIR / music_path).exists():
        print(f"🎵 Music: {music_path}")
        music = AudioFileClip(str(INPUT_DIR / music_path))
        vol = audio_cfg.get("music_volume", 0.3)
        if music.duration < final.duration:
            music = music.loop(duration=final.duration)
        else:
            music = music.subclipped(0, final.duration)
        music = music.with_effects([
            MultiplyVolume(vol),
            AudioFadeIn(1),
            AudioFadeOut(1),
        ])
        audio_layers.append(music)

    if voiceover_path and (INPUT_DIR / voiceover_path).exists():
        print(f"🎤 Voiceover: {voiceover_path}")
        vo = AudioFileClip(str(INPUT_DIR / voiceover_path))
        vo = vo.with_duration(final.duration)
        audio_layers.append(vo)

    if len(audio_layers) > 1:
        final = final.with_audio(CompositeAudioClip(audio_layers))
    elif audio_layers:
        final = final.with_audio(audio_layers[0])

    # ── Export ──
    print(f"💾 Rendering...")
    final.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )

    print(f"\n✅ Ad saved: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    config = sys.argv[1] if len(sys.argv) > 1 else str(INPUT_DIR / "ad_config.yaml")
    build_from_config(config)