#!/usr/bin/env python3
"""Print resolved TTS backend name. Used by SKILL.md prereq snippet."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts.backends import resolve_backend  # noqa: E402

print(resolve_backend()[0])
