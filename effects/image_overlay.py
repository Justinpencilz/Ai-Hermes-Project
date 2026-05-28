"""
Image overlay effects for Facebook ads.
Logo placement, product shots, full-bleed backgrounds.
"""

from moviepy import ImageClip, CompositeVideoClip
from moviepy.video.fx import FadeIn, FadeOut, SlideIn

CANVAS_W = 1080
CANVAS_H = 1080


def logo_overlay(image_path, position=("left", "top"), size=(120, 120),
                 duration=5, opacity=0.9, fade_duration=0.3):
    """
    Place a logo image in a corner of the ad.

    position: ("left"/"right", "top"/"bottom") or (x, y) in pixels
    size: (width, height) to resize the logo
    """
    img = ImageClip(image_path).resized(size)
    img = img.with_duration(duration).with_opacity(opacity)
    img = img.with_effects([FadeIn(fade_duration), FadeOut(fade_duration)])

    # Resolve named positions
    px, py = position
    if px == "left":
        px = 20
    elif px == "right":
        px = CANVAS_W - size[0] - 20
    if py == "top":
        py = 20
    elif py == "bottom":
        py = CANVAS_H - size[1] - 20

    img = img.with_position((px, py))
    return img


def product_shot(image_path, position=("center", "center"),
                 size=(400, 400), duration=4, animation="zoom_in",
                 border_radius=0):
    """
    Animated product image shot.
    """
    img = ImageClip(image_path).resized(size)
    img = img.with_duration(duration)

    if animation == "zoom_in":
        img = img.with_effects([img.effxn.FadeIn(0.4)])
    elif animation == "slide_up":
        img = img.with_effects([SlideIn(0.5, "bottom"), FadeOut(0.3)])

    px, py = position
    if px == "center":
        px = (CANVAS_W - size[0]) // 2
    if py == "center":
        py = (CANVAS_H - size[1]) // 2

    img = img.with_position((px, py))

    return img


def image_background(image_path, duration=5, blur=False, darken=0.0):
    """
    Use an image as a full-frame background.
    darken: 0.0 (none) to 1.0 (fully black)
    """
    img = ImageClip(image_path)
    img = img.resized(width=CANVAS_W)

    if img.h < CANVAS_H:
        img = img.resized(height=CANVAS_H)
    # Center crop if needed
    if img.h > CANVAS_H:
        img = img.cropped(y_center=img.h / 2, height=CANVAS_H)

    img = img.with_duration(duration)

    if darken > 0:
        # Darken overlay
        from moviepy import ColorClip
        overlay = ColorClip(
            color=(0, 0, 0),
            size=(CANVAS_W, CANVAS_H),
            duration=duration,
        ).with_opacity(darken)
        img = CompositeVideoClip([img, overlay], size=(CANVAS_W, CANVAS_H))

    return img.with_effects([FadeIn(0.5), FadeOut(0.5)])