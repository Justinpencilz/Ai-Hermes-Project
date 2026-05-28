"""
Video Ad Studio — Main Builder
Orchestrates ad creation with overlays, transitions, and audio.

Usage:
    from ad_builder import build_ad

    build_ad(
        video_path="input.mp4",
        output_path="output.mp4",
        preset="square",
        headline="Amazing Product",
        body=["Feature 1", "Feature 2"],
        cta_text="Shop Now",
        music_path="background.mp3",
    )
"""

import os
import sys
import yaml
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip, ColorClip
from moviepy.video.fx import FadeIn, FadeOut
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut, MultiplyVolume

from effects.kinetic_text import kinetic_title, kinetic_body
from effects.lower_thirds import lower_third_name, cta_button, promo_bar
from effects.transitions import crossfade, slide_transition, wipe

# ──────────────────────────────
# Load presets
# ──────────────────────────────

PRESETS_DIR = os.path.join(os.path.dirname(__file__), "presets")

def _load_presets():
    path = os.path.join(PRESETS_DIR, "facebook_ad.yaml")
    with open(path) as f:
        data = yaml.safe_load(f)
    return data["presets"], data["defaults"]

PRESETS, STYLE = _load_presets()


# ──────────────────────────────
# Audio mixing
# ──────────────────────────────


def _mix_audio(video_clip, music_path=None, music_volume=None, voiceover_path=None):
    """Add background music + optional voiceover to a video clip."""
    if not music_path and not voiceover_path:
        return video_clip

    if music_volume is None:
        music_volume = STYLE["music_volume"]

    audio_clips = [video_clip.audio] if video_clip.audio else []

    if music_path and os.path.exists(music_path):
        music = AudioFileClip(music_path)
        # Loop music to match video duration
        if music.duration < video_clip.duration:
            music = music.loop(duration=video_clip.duration)
        else:
            music = music.subclipped(0, video_clip.duration)
        music = music.with_effects([
            MultiplyVolume(music_volume),
            AudioFadeIn(1),
            AudioFadeOut(1),
        ])
        audio_clips.append(music)

    if voiceover_path and os.path.exists(voiceover_path):
        vo = AudioFileClip(voiceover_path).with_duration(video_clip.duration)
        audio_clips.append(vo)

    if len(audio_clips) > 1:
        mixed = CompositeAudioClip(audio_clips)
        return video_clip.with_audio(mixed)
    elif audio_clips:
        return video_clip.with_audio(audio_clips[0])
    return video_clip


# ──────────────────────────────
# Ad builder
# ──────────────────────────────


def build_ad(
    video_path,
    output_path="output.mp4",
    preset="square",
    headline=None,
    body=None,
    cta_text=None,
    music_path=None,
    voiceover_path=None,
    lower_third_name_text=None,
    lower_third_title=None,
):
    """
    Build a Facebook-ready ad video with overlays.

    Args:
        video_path: Path to source video
        output_path: Where to save final ad
        preset: "square", "story", or "landscape"
        headline: Big animated title text
        body: List of body text lines
        cta_text: Call-to-action button text
        music_path: Background music file
        voiceover_path: Voiceover audio file
        lower_third_name_text: Name for lower third
        lower_third_title: Title for lower third
    """
    cfg = PRESETS.get(preset)
    if not cfg:
        available = list(PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset}'. Options: {available}")

    # ── Load video ──
    video = VideoFileClip(video_path)
    target_w = cfg["width"]
    target_h = cfg["height"]
    fps = cfg["fps"]

    # Resize to target (maintain aspect, letterbox)
    if video.size != (target_w, target_h):
        video = video.resized(width=target_w)
        # Center crop if too tall
        if video.h > target_h:
            video = video.cropped(y_center=video.h / 2, height=target_h)
        # Pad if too short
        elif video.h < target_h:
            from moviepy import ColorClip
            _hc = STYLE["bg_color"].lstrip("#")
            _rgb = tuple(int(_hc[i:i+2], 16) for i in (0, 2, 4))
            bg = ColorClip(
                color=_rgb,
                size=(target_w, target_h),
                duration=video.duration,
            )
            video = CompositeVideoClip([bg, video.with_position(("center", "center"))],
                                        size=(target_w, target_h))

    video = video.with_fps(fps)

    # ── Build overlays ──
    overlays = []

    # Headline
    if headline:
        title_clip = kinetic_title(
            text=headline,
            font_size=72 if preset == "square" else 56,
            color=STYLE["primary_color"],
            duration=min(video.duration, 3.5),
            animation="slide_up",
            position=("center", 80),
        )
        overlays.append(title_clip)

    # Body text
    if body:
        body_clip = kinetic_body(
            lines=body,
            font_size=36,
            color=STYLE["text_color"],
            line_duration=min(video.duration, 3),
            stagger=0.3,
            animation="slide_up",
            position=("center", "center"),
        )
        overlays.append(body_clip)

    # CTA button
    if cta_text:
        cta = cta_button(
            text=cta_text,
            font_size=36,
            color=STYLE["text_color"],
            bg_color=STYLE["primary_color"],
            duration=min(video.duration, 4),
            position=("center", target_h - 150),
        )
        overlays.append(cta)

    # Lower third
    if lower_third_name_text:
        lower = lower_third_name(
            name=lower_third_name_text,
            title=lower_third_title or "",
            font_size=42,
            name_color=STYLE["text_color"],
            title_color=STYLE["primary_color"],
            duration=min(video.duration, 4),
        )
        overlays.append(lower)

    # Composite video + overlays
    if overlays:
        # Add fade-in/out to main video
        video = video.with_effects([
            FadeIn(0.5),
            FadeOut(0.5),
        ])
        final = CompositeVideoClip(
            [video] + overlays,
            size=(target_w, target_h),
        )
    else:
        final = video.with_effects([FadeIn(0.5), FadeOut(0.5)])

    # ── Mix audio ──
    final = _mix_audio(final, music_path, voiceover_path=voiceover_path)

    # ── Export ──
    final.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )
    print(f"\n✅ Ad saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    # Test with a simple sample if run directly
    import argparse
    parser = argparse.ArgumentParser(description="Build Facebook Ad Video")
    parser.add_argument("video", help="Path to input video")
    parser.add_argument("-o", "--output", default="output.mp4", help="Output path")
    parser.add_argument("-p", "--preset", default="square", choices=["square", "story", "landscape"])
    parser.add_argument("--headline", help="Animated title text")
    parser.add_argument("--body", nargs="*", help="Body text lines")
    parser.add_argument("--cta", help="CTA button text")
    parser.add_argument("--music", help="Background music file")
    parser.add_argument("--voiceover", help="Voiceover audio file")
    parser.add_argument("--name", help="Lower third name")
    parser.add_argument("--title", help="Lower third title")

    args = parser.parse_args()
    build_ad(
        video_path=args.video,
        output_path=args.output,
        preset=args.preset,
        headline=args.headline,
        body=args.body,
        cta_text=args.cta,
        music_path=args.music,
        voiceover_path=args.voiceover,
        lower_third_name_text=args.name,
        lower_third_title=args.title,
    )