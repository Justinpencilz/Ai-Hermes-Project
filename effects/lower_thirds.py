"""
Animated Lower Thirds for Facebook ads.
Branded name/title overlays, CTA buttons, and promo bars.
"""

from moviepy import TextClip, CompositeVideoClip, ColorClip
from moviepy.video.fx import FadeIn, FadeOut, SlideIn, SlideOut

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CANVAS_W = 1080
CANVAS_H = 1080


def _hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def lower_third_name(name, title="", font_size=48, name_color="#FFFFFF",
                     title_color="#FF6B35", bar_color="#1A1A2E",
                     duration=4, anim_duration=0.5):
    """
    Animated lower third with name + optional title.
    Slides in from bottom, stays, fades out.
    """
    padding = 20
    line_height = font_size + 6
    bar_height = (line_height * 2 + padding * 2) if title else (line_height + padding * 2)

    # Background bar
    bar = ColorClip(color=_hex_to_rgb(bar_color), size=(CANVAS_W, bar_height), duration=duration)
    bar = bar.with_opacity(0.85).with_position((0, CANVAS_H - bar_height))
    bar = bar.with_effects([
        SlideIn(anim_duration, "bottom"),
        FadeOut(0.3),
    ])

    # Name text
    name_txt = TextClip(
        font=FONT_BOLD, text=name, font_size=font_size,
        color=name_color, size=(CANVAS_W - padding * 2, None),
    ).with_duration(duration).with_position(
        (padding, CANVAS_H - bar_height + padding)
    ).with_effects([
        SlideIn(anim_duration, "right"),
        FadeOut(0.3),
    ])

    clips = [bar, name_txt]

    if title:
        title_txt = TextClip(
            font=FONT_PATH, text=title, font_size=font_size - 10,
            color=title_color, size=(CANVAS_W - padding * 2, None),
        ).with_duration(duration).with_position(
            (padding, CANVAS_H - bar_height + padding + line_height + 4)
        ).with_effects([
            FadeIn(anim_duration + 0.2),
            FadeOut(0.3),
        ])
        clips.append(title_txt)

    return CompositeVideoClip(clips, size=(CANVAS_W, CANVAS_H))


def cta_button(text="Shop Now", font_size=40, color="#FFFFFF",
               bg_color="#FF6B35", duration=3, position=("center", "center")):
    """
    Animated CTA button overlay. Slides in from bottom, pulses, fades out.
    """
    padding_x = 40
    padding_y = 16

    txt = TextClip(
        font=FONT_BOLD, text=text, font_size=font_size,
        color=color, size=(CANVAS_W, None),
    )
    txt_w, txt_h = txt.size

    btn_w = txt_w + padding_x * 2
    btn_h = txt_h + padding_y * 2

    # Resolve "center" strings to pixel positions
    if isinstance(position, tuple):
        px, py = position
        if px == "center":
            px = (CANVAS_W - btn_w) // 2
        if py == "center":
            py = (CANVAS_H - btn_h) // 2
    else:
        px = (CANVAS_W - btn_w) // 2
        py = (CANVAS_H - btn_h) // 2

    btn = ColorClip(color=_hex_to_rgb(bg_color), size=(btn_w, btn_h), duration=duration)
    btn = btn.with_opacity(0.95).with_position((px, py))
    btn = btn.with_effects([
        SlideIn(0.4, "bottom"),
        FadeOut(0.3),
    ])

    btn_txt = TextClip(
        font=FONT_BOLD, text=text, font_size=font_size,
        color=color, size=(CANVAS_W, None),
    ).with_duration(duration).with_position((px + padding_x, py + padding_y))
    btn_txt = btn_txt.with_effects([
        FadeIn(0.4),
        FadeOut(0.3),
    ])

    return CompositeVideoClip([btn, btn_txt], size=(CANVAS_W, CANVAS_H))


def promo_bar(text, font_size=44, color="#FFFFFF",
              bg_color="#E63946", duration=3, anim_duration=0.4):
    """
    Full-width promotional bar — good for '50% OFF' banners.
    Slides in from top, stays, slides out.
    """
    padding = 16
    bar_height = font_size + padding * 2

    bar = ColorClip(color=_hex_to_rgb(bg_color), size=(CANVAS_W, bar_height), duration=duration)
    bar = bar.with_opacity(0.9).with_position((0, 100))
    bar = bar.with_effects([
        SlideIn(anim_duration, "top"),
        SlideOut(anim_duration, "top"),
    ])

    txt = TextClip(
        font=FONT_BOLD, text=text, font_size=font_size,
        color=color, size=(CANVAS_W - padding * 2, None),
    ).with_duration(duration).with_position((padding, 100 + padding))
    txt = txt.with_effects([
        FadeIn(anim_duration),
        FadeOut(anim_duration),
    ])

    return CompositeVideoClip([bar, txt], size=(CANVAS_W, CANVAS_H))