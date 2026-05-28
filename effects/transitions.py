"""
Custom video transitions for Facebook ads.
Fade, crossfade, slide, and wipe transitions between clips.
"""

from moviepy import VideoClip, concatenate_videoclips
from moviepy.video.fx import FadeIn, FadeOut
import numpy as np


def crossfade(clip1, clip2, duration=0.5):
    """
    Classic crossfade between two clips.
    clip1 fades out while clip2 fades in over the overlap.
    """
    fade_out = clip1.with_effects([FadeOut(duration)])
    fade_in = clip2.with_effects([FadeIn(duration)])
    return concatenate_videoclips(
        [fade_out, fade_in.with_start(0)],
        method="chain",
        padding=-duration,
    )


def slide_transition(clip1, clip2, duration=0.5, direction="left"):
    """
    Slide transition: clip1 slides out revealing clip2.
    direction: left, right, up, down
    """
    w, h = clip1.size if hasattr(clip1, 'size') else (1080, 720)
    if isinstance(w, tuple):
        w, h = w[0], w[1]

    def make_frame(t):
        progress = t / duration if duration > 0 else 1.0
        progress = min(max(progress, 0), 1)

        f1 = clip1.get_frame(t)
        f2 = clip2.get_frame(t)

        offset = int(progress * w)

        if direction == "left":
            result = np.zeros((h, w, 3), dtype=np.uint8)
            if offset < w:
                result[:, :w - offset] = f1[:, offset:]
            if offset > 0:
                result[:, w - offset:] = f2[:, :offset]
        elif direction == "right":
            result = np.zeros((h, w, 3), dtype=np.uint8)
            result[:, :offset] = f1[:, :offset]
            result[:, offset:] = f2[:, offset:]
        elif direction == "up":
            offset_v = int(progress * h)
            result = np.zeros((h, w, 3), dtype=np.uint8)
            if offset_v < h:
                result[:h - offset_v, :] = f1[offset_v:, :]
            if offset_v > 0:
                result[h - offset_v:, :] = f2[:offset_v, :]
        elif direction == "down":
            offset_v = int(progress * h)
            result = np.zeros((h, w, 3), dtype=np.uint8)
            result[:offset_v, :] = f1[:offset_v, :]
            result[offset_v:, :] = f2[offset_v:, :]
        else:
            result = f2
        return result.astype(np.uint8)

    return VideoClip(make_frame, duration=duration)


def wipe(clip1, clip2, duration=0.5, direction="left"):
    """
    Solid-color wipe transition revealing clip2 through clip1.
    """
    w, h = clip1.size if hasattr(clip1, 'size') else (1080, 1080)
    if isinstance(w, tuple):
        w, h = w[0], w[1]

    def make_frame(t):
        progress = t / duration if duration > 0 else 1.0
        progress = min(max(progress, 0), 1)
        f1 = clip1.get_frame(t)
        f2 = clip2.get_frame(t)

        if direction == "left":
            x = int(w * (1 - progress))
            mask = np.zeros((h, w, 3), dtype=np.uint8)
            mask[:, x:, :] = 1
        elif direction == "right":
            x = int(w * progress)
            mask = np.zeros((h, w, 3), dtype=np.uint8)
            mask[:, :x, :] = 1
        elif direction == "up":
            y = int(h * (1 - progress))
            mask = np.zeros((h, w, 3), dtype=np.uint8)
            mask[y:, :, :] = 1
        elif direction == "down":
            y = int(h * progress)
            mask = np.zeros((h, w, 3), dtype=np.uint8)
            mask[:y, :, :] = 1
        else:
            mask = np.ones((h, w, 3), dtype=np.uint8)

        result = np.where(mask > 0, f2, f1)
        return result.astype(np.uint8)

    return VideoClip(make_frame, duration=duration)