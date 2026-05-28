#!/usr/bin/env python3
"""
Auto-process videos and configs in input/ through the Ad Studio pipeline.
Now supports Remotion (preferred) and MoviePy (legacy) renderers.
Pushes results to GitHub and notifies via Telegram.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

PROJECT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = PROJECT_DIR / "input"
OUTPUT_DIR = PROJECT_DIR / "output"
DONE_DIR = PROJECT_DIR / "done"
STATE_FILE = PROJECT_DIR / ".processed_state.json"

# Renderer options
REMOTION_DIR = PROJECT_DIR / "remotion"
REMOTION_CLI = REMOTION_DIR / "render-cli.js"
MOVIEPY_BUILDER = PROJECT_DIR / "ad_from_config.py"

DONE_DIR.mkdir(exist_ok=True)

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"processed_videos": [], "processed_configs": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def find_new_videos(state):
    """Find .mp4 files in input/ not yet processed."""
    processed = set(state.get("processed_videos", []))
    return [f for f in sorted(INPUT_DIR.glob("*.mp4")) if f.name not in processed]

def find_new_configs(state):
    """Find YAML config files in input/ not yet processed."""
    processed = set(state.get("processed_configs", []))
    return [f for f in sorted(INPUT_DIR.glob("*.yaml")) if f.name not in processed]

def use_remotion(config_path):
    """Check if Remotion is available and should be used."""
    return REMOTION_CLI.exists() and (
        REMOTION_DIR / "node_modules" / "@remotion" / "bundler"
    ).exists()

def process_with_remotion(config_path):
    """Render ad using Remotion (Node.js/React)."""
    output_name = f"ad_{config_path.stem}_{int(os.path.getmtime(config_path))}.mp4"
    output_path = OUTPUT_DIR / output_name
    print(f"\n🎬 Rendering with Remotion: {config_path.name}")

    cmd = [
        "node", str(REMOTION_CLI),
        str(config_path),
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode == 0:
        print(result.stdout[-500:])
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"✅ Remotion output: {output_path.name} ({size_mb:.1f} MB)")
            return output_path
    else:
        print(f"❌ Remotion failed: {config_path.name}")
        if result.stderr:
            print(result.stderr[-500:])
    return None

def process_with_moviepy(config_path):
    """Legacy renderer using MoviePy."""
    print(f"\n📋 Processing with MoviePy: {config_path.name}")
    cmd = [sys.executable, str(MOVIEPY_BUILDER), str(config_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode == 0:
        print(result.stdout[-500:])
        # Find latest output
        output_candidates = sorted(OUTPUT_DIR.glob("*.mp4"))
        return output_candidates[-1] if output_candidates else None
    else:
        print(f"❌ MoviePy failed: {config_path.name}")
        if result.stderr:
            print(result.stderr[-500:])
        return None

def process_config(config_path, state):
    """Process a YAML config. Uses Remotion if available, falls back to MoviePy."""
    output_path = None

    if use_remotion(config_path):
        output_path = process_with_remotion(config_path)
    else:
        # Fallback to legacy MoviePy
        output_path = process_with_moviepy(config_path)

    if output_path:
        state["processed_configs"].append(config_path.name)
        save_state(state)
        done_path = DONE_DIR / config_path.name
        shutil.move(str(config_path), str(done_path))
        return str(output_path)

    return None

def process_video(video_path, state):
    """Legacy: process raw video with MoviePy (no config)."""
    input_name = video_path.stem
    output_path = OUTPUT_DIR / f"{input_name}_ad.mp4"
    print(f"\n🎬 Processing video (legacy): {video_path.name}")

    cmd = [
        sys.executable, str(MOVIEPY_BUILDER),
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode == 0:
        print(result.stdout[-300:])
        state["processed_videos"].append(video_path.name)
        save_state(state)
        done_path = DONE_DIR / video_path.name
        shutil.move(str(video_path), str(done_path))
        return str(output_path) if output_path.exists() else None
    else:
        print(f"❌ Failed: {video_path.name}")
        if result.stderr:
            print(result.stderr[-500:])
        return None

def push_to_github():
    try:
        subprocess.run(
            ["git", "add", "output/", "done/", "input/", ".processed_state.json", "remotion/src/", "remotion/render-cli.js"],
            cwd=PROJECT_DIR, capture_output=True, text=True,
        )
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=PROJECT_DIR, capture_output=True, text=True,
        )
        if result.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", "Auto: new ad output [remotion]"],
                cwd=PROJECT_DIR, capture_output=True, text=True,
            )
            push = subprocess.run(
                ["git", "push"],
                cwd=PROJECT_DIR, capture_output=True, text=True,
            )
            if push.returncode == 0:
                print("✅ Pushed to GitHub")
                return True
            else:
                print(f"⚠️ Push failed: {push.stderr}")
        else:
            print("ℹ️ No new changes to push")
        return False
    except Exception as e:
        print(f"⚠️ Git error: {e}")
        return False

def notify(output_paths):
    if not output_paths:
        return
    print("\n📬 READY FOR DELIVERY")
    for p in output_paths:
        if os.path.exists(p):
            size = os.path.getsize(p) / 1024
            print(f"  ✅ {os.path.basename(p)} — {size:.0f} KB")
    print("  📂 github.com/Justinpencilz/Ai-Hermes-Project")

def main():
    print("═" * 50)
    print("Ad Studio Auto-Processor")
    print(f"Renderer:  {'Remotion' if use_remotion(None) else 'MoviePy (legacy)'}")
    print(f"Input:     {INPUT_DIR}")
    print(f"Output:    {OUTPUT_DIR}")
    print("═" * 50)

    state = load_state()
    new_configs = find_new_configs(state)
    output_paths = []

    # Process YAML configs first
    for cfg in new_configs:
        result = process_config(cfg, state)
        if result:
            output_paths.append(result)

    # Also check for orphaned videos (legacy)
    new_videos = find_new_videos(state)
    for vid in new_videos:
        result = process_video(vid, state)
        if result:
            output_paths.append(result)

    if output_paths:
        pushed = push_to_github()
        notify(output_paths)
        print(f"\n✅ Done — {len(output_paths)} item(s) processed")
    else:
        print("No new items to process.")

if __name__ == "__main__":
    main()