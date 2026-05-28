"""
Kinetic Typography Effects
Animated text entries for Facebook ad videos — fade, slide, scale, typewriter.
"""

from moviepy import TextClip, CompositeVideoClip
from moviepy.video.fx import FadeIn, FadeOut, SlideIn

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CANVAS_W = 1080


def _anim_clip(text, font_size, color, font_path, duration, position, animation):
    """Create a TextClip with the given animation."""
    clip = TextClip(
        font=font_path,
        text=text,
        font_size=font_size,
        color=color,
        size=(CANVAS_W, None),
    ).with_duration(duration).with_position(position)

    ad = min(duration * 0.3, 0.5)  # animation duration

    if animation == "fade_in":
        return clip.with_effects([FadeIn(ad)])
    elif animation == "fade_in_out":
        return clip.with_effects([FadeIn(ad), FadeOut(ad)])
    elif animation == "slide_up":
        return clip.with_effects([SlideIn(ad, "bottom")])
    elif animation == "slide_left":
        return clip.with_effects([SlideIn(ad, "right")])
    elif animation == "slide_right":
        return clip.with_effects([SlideIn(ad, "left")])
    else:
        return clip


def kinetic_title(text, font_size=80, color="#FFFFFF", duration=3,
                  animation="zoom_in", position="center"):
    """
    Animated title text with entrance effect.

    animation options: fade_in, fade_in_out, slide_up, slide_left, slide_right
    """
    return _anim_clip(text, font_size, color, FONT_BOLD, duration, position, animation)


def kinetic_body(lines, font_size=40, color="#CCCCCC", line_duration=2.5,
                 stagger=0.3, animation="slide_up", position=("center", "center")):
    """
    Multiple lines of animated body text, staggered.
    """
    clips = []
    for i, line in enumerate(lines):
        start = i * stagger
        clip = _anim_clip(line, font_size, color, FONT_PATH,
                          line_duration, position, animation)
        clip = clip.with_start(start).with_duration(line_duration)
        clips.append(clip)
    return CompositeVideoClip(clips, size=(CANVAS_W, CANVAS_W))


def kinetic_word_sequence(words, font_size=70, color="#FF6B35",
                          word_duration=2.0, stagger=0.4,
                          animation="slide_up", position="center",
                          highlight_color="#FFD700"):
    """
    Words appear one-by-one with kinetic energy.
    Last word gets highlight color.
    """
    clips = []
    for i, word in enumerate(words):
        start = i * stagger
        c = highlight_color if i == len(words) - 1 else color
        clip = _anim_clip(word, font_size, c, FONT_BOLD,
                          word_duration, position, animation)
        clip = clip.with_start(start).with_duration(word_duration)
        clips.append(clip)
    return CompositeVideoClip(clips, size=(CANVAS_W, CANVAS_W))