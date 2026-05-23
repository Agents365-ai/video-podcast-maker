"""Shared utilities for TTS backends."""
import os
import subprocess


def check_resume(part_file):
    """Check if a part file exists and return its duration, or None."""
    if not os.path.exists(part_file):
        return None
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", part_file],
        capture_output=True, text=True)
    return float(probe.stdout.strip()) if probe.stdout.strip() else 0
