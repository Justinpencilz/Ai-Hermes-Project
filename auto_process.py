#!/usr/bin/env python3
"""
Auto-process videos in input/ through the Ad Studio pipeline.
Pushes results to GitHub and sends Telegram notification.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Paths
PROJECT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = PROJECT_DIR / "input"
OUTPUT_DIR = PROJECT_DIR / "output"
DONE_DIR = PROJECT_DIR / "done"
STATE_FILE = PROJECT_DIR / ".processed_state.json"
AD_BUILDER = PROJECT_DIR / "ad_builder.py"

# Ensure dirs
DONE_DIR.mkdir(exist_ok=True)

# Default settings for the auto-process
DEFAULT_PRESET = "square"
DEFAULT_HEADLINE = None
DEFAULT_BODY = []
DEFAULT_CTA = None

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"processed": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def find_new_videos(state):
    """Find .mp4 files in input/ not yet processed."""
    processed = set(state.get("processed", []))
    new_videos = []
    for f in sorted(INPUT_DIR.glob("*.mp4")):
        if f.name not in processed:
            new_videos.append(f)
    return new_videos

def process_video(video_path, state):
    """Run ad_builder on a single video."""
    input_name = video_path.stem
    output_path = OUTPUT_DIR / f"{input_name}_ad.mp4"

    print(f"\n🎬 Processing: {video_path.name}")

    cmd = [
        sys.executable, str(AD_BUILDER),
        str(video_path),
        "-o", str(output_path),
        "-p", DEFAULT_PRESET,
    ]

    if DEFAULT_HEADLINE:
        cmd += ["--headline", DEFAULT_HEADLINE]
    if DEFAULT_BODY:
        cmd += ["--body"] + DEFAULT_BODY
    if DEFAULT_CTA:
        cmd += ["--cta", DEFAULT_CTA]

    # Run via subprocess
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode == 0 and output_path.exists():
        print(f"✅ Processed: {output_path.name} ({output_path.stat().st_size / 1024:.0f} KB)")

        # Move input to done/
        done_path = DONE_DIR / video_path.name
        shutil.move(str(video_path), str(done_path))

        # Mark as processed
        state["processed"].append(video_path.name)
        save_state(state)

        return str(output_path)
    else:
        print(f"❌ Failed: {video_path.name}")
        if result.stderr:
            print(result.stderr[-500:])
        return None

def push_to_github():
    """Commit and push output changes to GitHub."""
    import subprocess
    try:
        # Git add output + done
        subprocess.run(["git", "add", "output/", "done/", ".processed_state.json"],
                       cwd=PROJECT_DIR, capture_output=True, text=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=PROJECT_DIR, capture_output=True, text=True
        )
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Auto: new ad output"],
                           cwd=PROJECT_DIR, capture_output=True, text=True)
            push = subprocess.run(["git", "push"],
                                  cwd=PROJECT_DIR, capture_output=True, text=True)
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
    """Print notification (cron job delivers to Telegram)."""
    if not output_paths:
        return
    print("\n📬 READY FOR DELIVERY")
    for p in output_paths:
        size = os.path.getsize(p) / 1024
        print(f"  ✅ {os.path.basename(p)} — {size:.0f} KB")
    print(f"  📂 github.com/Justinpencilz/Ai-Hermes-Project")

def main():
    print("═" * 50)
    print("Ad Studio Auto-Processor")
    print(f"Input:  {INPUT_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print("═" * 50)

    state = load_state()
    new_videos = find_new_videos(state)

    if not new_videos:
        print("No new videos to process.")
        return

    print(f"Found {len(new_videos)} new video(s)")
    output_paths = []

    for video in new_videos:
        result = process_video(video, state)
        if result:
            output_paths.append(result)

    if output_paths:
        push_to_github()
        notify(output_paths)
        print(f"\n✅ Done — {len(output_paths)} video(s) processed")

if __name__ == "__main__":
    main()