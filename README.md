# Ai-Hermes-Project — Facebook Ad Video Studio

Automated video editing for Facebook/Instagram ads. Animated titles, CTA buttons, lower thirds, transitions, and audio mixing.

## Quick Start

```bash
pip3 install moviepy pyyaml
python3 ad_builder.py your_video.mp4 \
  --headline "Big Sale" \
  --body "Limited Offer" "Shop Now" \
  --cta "Get Yours →"
```

## Presets

| Flag | Format | Resolution |
|------|--------|------------|
| `-p square` | Facebook Feed | 1080×1080 |
| `-p story` | Stories / Reels | 1080×1920 |
| `-p landscape` | Desktop Feed | 1920×1080 |

## Options

| Flag | Description |
|------|-------------|
| `--headline` | Animated title text |
| `--body` | Animated body lines (repeat for multiple) |
| `--cta` | Call-to-action button text |
| `--name` | Lower third name |
| `--title` | Lower third title |
| `--music` | Background music file |
| `--voiceover` | Voiceover audio file |
| `-o` | Output path (default: output.mp4) |

## Auto-Processing

New videos placed in `input/` are automatically detected, processed, and pushed to GitHub.

1. Drop a `.mp4` file into the `input/` folder
2. The system detects it, runs the ad builder
3. Output appears in `output/`
4. You get a Telegram notification

## Files

| File | Purpose |
|---|---|
| `ad_builder.py` | Main pipeline |
| `auto_process.py` | Watches input/, processes, pushes |
| `effects/kinetic_text.py` | Animated text effects |
| `effects/lower_thirds.py` | Lower thirds, CTA buttons |
| `effects/transitions.py` | Crossfade, slide, wipe |
| `presets/facebook_ad.yaml` | Color/font/size config |
