"""Pytest configuration — add scripts/ to sys.path so tests can import the
tts package. Scripts now live under skills/video-podcast-maker/scripts/.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "skills", "video-podcast-maker", "scripts"))
