"""Guard against doc drift: facts duplicated across docs must match the code.

Each test targets a drift class actually hit in the v4.0.2 review:
stale .env.example backend lists, stale native-boundary platform lists,
and version numbers diverging between SKILL.md and package.json.
"""
import json
import re
from pathlib import Path

from tts.backends import BACKENDS

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "video-podcast-maker"

# Single source of truth for the test suite; update together with the docs
# when a platform gains native word-boundary support in ttsCN.
NATIVE_BOUNDARY_PLATFORMS = "edge, azure, doubao, minimax, cosyvoice"

# Files that state the native-boundary platform list.
NATIVE_BOUNDARY_DOCS = [
    SKILL_ROOT / "references" / "troubleshooting.md",
    SKILL_ROOT / "references" / "workflow-production.md",
    SKILL_ROOT / "scripts" / "tts" / "backends" / "ttscn.py",
]


def _normalized(path):
    """File text with backticks stripped and whitespace collapsed."""
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8").replace("`", ""))


def test_env_example_lists_every_backend():
    """The TTS_BACKEND options comment must name every routable platform."""
    env_example = (SKILL_ROOT / ".env.example").read_text(encoding="utf-8")
    options_line = next(
        line for line in env_example.splitlines() if line.startswith("TTS_BACKEND=")
    )
    missing = [
        backend for backend in BACKENDS
        if backend != "ttscn" and backend not in options_line  # legacy alias excluded
    ]
    assert not missing, f".env.example TTS_BACKEND options line missing: {missing}"


def test_env_example_covers_required_env_vars():
    """Every env var the routing table validates must appear in .env.example."""
    env_example = (SKILL_ROOT / ".env.example").read_text(encoding="utf-8")
    missing = sorted(
        var for entry in BACKENDS.values() for var in entry["env"]
        if var not in env_example
    )
    assert not missing, f".env.example missing env vars: {missing}"


def test_native_boundary_platform_lists_match():
    """Docs stating the native word-boundary platforms must carry the full list.

    ponytail: only asserts the canonical list appears at least once per file;
    a file mentioning it twice with one stale copy passes. Tighten to
    per-occurrence matching if that drift recurs.
    """
    stale = [
        str(path.relative_to(REPO_ROOT))
        for path in NATIVE_BOUNDARY_DOCS
        if NATIVE_BOUNDARY_PLATFORMS not in _normalized(path)
    ]
    assert not stale, (
        f"files missing the native-boundary list '{NATIVE_BOUNDARY_PLATFORMS}': {stale}"
    )


def test_skill_and_package_versions_match():
    skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    skill_version = re.search(r"^version:\s*(\S+)", skill_md, re.MULTILINE).group(1)
    package_version = json.loads(
        (SKILL_ROOT / "package.json").read_text(encoding="utf-8")
    )["version"]
    assert skill_version == package_version, (
        f"SKILL.md version {skill_version} != package.json version {package_version}"
    )
