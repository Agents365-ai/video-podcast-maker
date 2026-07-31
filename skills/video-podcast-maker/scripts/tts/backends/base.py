"""Shared utilities for TTS backends."""
import os
import subprocess


def check_resume(part_file):
    """Check if a part file exists and return its duration, or None.

    Returns None for a missing, unprobeable, or zero-length file so resume
    re-synthesizes it instead of silently skipping a corrupt part. OSError
    (missing ffprobe, permissions) also yields None so callers can fall
    back to the envelope's reported duration.
    """
    if not os.path.exists(part_file):
        return None
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", part_file],
            capture_output=True, text=True)
    except OSError:
        return None
    try:
        duration = float(probe.stdout.strip())
    except ValueError:
        return None
    return duration if duration > 0 else None
