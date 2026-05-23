#!/usr/bin/env python3
"""Resolve user_prefs.bgm.track logical name to the absolute BGM file path.

Reads `global.bgm.track` (e.g. "calm-piano") and looks up the actual filename
in `global.bgm.tracks`. Prints the absolute path under <skill_dir>/assets/.
Falls back to the first track in `tracks` if `track` is unset or unknown.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts.backends import user_prefs_get  # noqa: E402


def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    track_name = user_prefs_get('global', 'bgm', 'track')
    tracks = user_prefs_get('global', 'bgm', 'tracks') or {}

    if not tracks:
        print('Error: no BGM tracks configured in user_prefs.bgm.tracks', file=sys.stderr)
        sys.exit(1)

    if track_name and track_name in tracks:
        filename = tracks[track_name]
    else:
        filename = next(iter(tracks.values()))
        if track_name:
            print(f"Warning: track '{track_name}' not in tracks map, using {filename}", file=sys.stderr)

    bgm_path = os.path.join(skill_dir, 'assets', filename)
    if not os.path.exists(bgm_path):
        print(f"Error: BGM file not found: {bgm_path}", file=sys.stderr)
        sys.exit(1)

    print(bgm_path)


if __name__ == '__main__':
    main()
