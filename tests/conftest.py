"""Pytest configuration for tests/ — exposes the skill's scripts/ package
on sys.path.

After the 365-skills restructure, scripts live under
`skills/video-podcast-maker/scripts/`. This conftest is the single source
of truth for the import path so individual test files don't need to
hand-roll their own `sys.path.insert(...)` calls.
"""
import os
import sys

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "skills", "video-podcast-maker", "scripts",
    ),
)
