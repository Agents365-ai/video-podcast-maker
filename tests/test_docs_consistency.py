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
# when a backend gains or loses native word-boundary support.
NATIVE_BOUNDARY_PLATFORMS = "edge, azure"
# Files that state the native-boundary platform list.
NATIVE_BOUNDARY_DOCS = [
    SKILL_ROOT / "references" / "troubleshooting.md",
    SKILL_ROOT / "references" / "workflow-production.md",
    SKILL_ROOT / "scripts" / "tts" / "backends" / "native.py",
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
    missing = [backend for backend in BACKENDS if backend not in options_line]
    assert not missing, f".env.example TTS_BACKEND options line missing: {missing}"


def test_env_example_covers_required_env_vars():
    """Every env var the routing table validates must appear in .env.example."""
    env_example = (SKILL_ROOT / ".env.example").read_text(encoding="utf-8")
    missing = sorted(
        var
        for entry in BACKENDS.values()
        for var in entry["env"]
        if var not in env_example
    )
    assert not missing, f".env.example missing env vars: {missing}"


# Backends/component-skills removed in v5.3.0's local-TTS change. Any of these
# turning up in the docs is a stale reference to a deleted platform.
REMOVED_TTS_PLATFORMS = (
    "TTSCN_HOME", "doubao", "cosyvoice", "tencent", "baidu", "minimax",
    "xunfei", "elevenlabs", "openai", "google",
)


def test_env_example_has_no_removed_platforms():
    """.env.example must not name any TTS platform removed since v5.3.0.

    The prior .env.example still listed TTSCN_HOME and the doubao/cosyvoice/
    tencent/... backends long after they were removed, because only the
    "must include" direction was guarded. This is the inverse: the file must
    not carry removed platforms either."""
    env_example = (SKILL_ROOT / ".env.example").read_text(encoding="utf-8")
    hits = [p for p in REMOVED_TTS_PLATFORMS if p.lower() in env_example.lower()]
    assert not hits, f".env.example names removed TTS platform(s): {hits}"


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


# Canonical workflow step ids (single source of truth — keep in sync with
# the workflow table in SKILL.md, which folds the decimal sub-steps into its
# 12 rows). Docs, templates, and script comments must only reference these.
CANONICAL_STEPS = {
    "1",
    "2",
    "3",
    "4",
    "4.5",
    "5",
    "5.5",
    "6",
    "7",
    "8",
    "9",
    "9.5",
    "10",
    "10.1",
    "10.2",
    "10.3",
    "11",
}

# Scanned for 'Step N' references. CHANGELOG.md is intentionally excluded:
# old entries document retired numbering and are a historical record.
STEP_SCAN_FILES = (
    [SKILL_ROOT / "SKILL.md"]
    + sorted(SKILL_ROOT.glob("references/*.md"))
    + sorted(SKILL_ROOT.glob("templates/**/*.tsx"))
    + sorted(SKILL_ROOT.glob("templates/**/*.ts"))
    + sorted(SKILL_ROOT.glob("scripts/**/*.py"))
    + [REPO_ROOT / "README.md", REPO_ROOT / "README_CN.md"]
)

_STEP_START = re.compile(r"Steps?\s+(\d+(?:\.\d+)?)", re.IGNORECASE)
_STEP_RANGE = re.compile(r"\s*[-–—]\s*(\d+(?:\.\d+)?)")
_STEP_LIST = re.compile(r"\s*(?:,|/)\s*(?:and\s+)?(\d+(?:\.\d+)?)")
_STEP_WORD = re.compile(r"\s+(?:and|through)\s+(\d+(?:\.\d+)?)")


def _step_numbers(line):
    """Yield every step number mentioned in a line.

    Handles the shapes docs actually use: 'Step 9', 'Steps 5.5-9.5',
    'Steps 10.1-11', comma lists ('Steps 7, 9, 10, 13, and 15' — how the
    retired 13/15 refs survived a renumbering), slash lists, and word
    separators ('Steps 7 and 13', 'Steps 7 through 13').
    """
    for start in _STEP_START.finditer(line):
        yield start.group(1)
        rest = line[start.end() :]
        rm = _STEP_RANGE.match(rest)
        if rm:
            yield rm.group(1)
            rest = rest[rm.end() :]
        while True:
            cm = _STEP_LIST.match(rest)
            if cm:
                yield cm.group(1)
                rest = rest[cm.end() :]
                continue
            wm = _STEP_WORD.match(rest)
            if wm:
                yield wm.group(1)
                rest = rest[wm.end() :]
                continue
            break


def test_no_stale_skill_dir_state_paths():
    """Mutable state (user_prefs.json, phonemes.json) lives in
    ~/.video-podcast-maker/ — references/ must never point agents at
    ${SKILL_DIR} copies (they are wiped on every skill update)."""
    forbidden = ("${SKILL_DIR}/user_prefs.json", "${SKILL_DIR}/phonemes.json")
    hits = []
    for path in sorted((SKILL_ROOT / "references").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for pat in forbidden:
            if pat in text:
                hits.append(f"{path.name}: {pat}")
    assert not hits, f"stale skill-dir state paths: {hits}"


def test_step_references_resolve_to_canonical_workflow():
    """Every 'Step N' mention must be a canonical workflow step id.

    This is the drift class that produced 6 of the 25 findings in the
    dual-review round: retired steps 13/15 survived in platform-matrix.md,
    BGM mix was called 'Step 11' (shorts) in four templates, and SKILL.md
    contradicted itself on Step 8 vs 9 for design-guide.md. A renumbering
    must update CANONICAL_STEPS here and SKILL.md's table together.
    """
    violations = []
    for path in STEP_SCAN_FILES:
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for num in _step_numbers(line):
                if num not in CANONICAL_STEPS:
                    rel = path.relative_to(REPO_ROOT)
                    violations.append(
                        f"{rel}:{lineno}: 'Step {num}' not in {sorted(CANONICAL_STEPS)}"
                    )
    assert not violations, f"{len(violations)} stale step reference(s):\n" + "\n".join(
        violations
    )


def test_step_regex_catches_bypass_shapes():
    """The exact shapes that slipped through a renumbering must be caught,
    while legitimate canonical references pass."""
    bypasses = [
        "Reference during Steps 7, 9, 10, 13, and 15.",
        "Steps 7 and 13",
        "Steps 7/13",
        "Steps 7 through 13",
        "step 13.",
    ]
    for line in bypasses:
        bad = [n for n in _step_numbers(line) if n not in CANONICAL_STEPS]
        assert bad, f"bypass shape not caught: {line!r}"
    valid = [
        "Steps 5.5-9.5 (publish info draft -> BGM mix)",
        "Steps 10.1-11 (finalize -> shorts)",
        "Steps 1-4",
        "Step 9.5 mixes BGM via FFmpeg.",
    ]
    for line in valid:
        bad = [n for n in _step_numbers(line) if n not in CANONICAL_STEPS]
        assert not bad, f"valid shape falsely flagged: {line!r}"


def test_all_markdown_references_resolve():
    """Every references/*.md link in docs/templates must resolve to an existing file."""
    ref_pattern = re.compile(
        r"\]\(references/([a-z0-9_-]+\.md)(?:#[a-z0-9_-]+)?\)",
        re.IGNORECASE,
    )
    doc_files = (
        [SKILL_ROOT / "SKILL.md"]
        + list(SKILL_ROOT.glob("references/*.md"))
        + list(SKILL_ROOT.glob("templates/**/*.md"))
        + list(SKILL_ROOT.glob("templates/**/*.tsx"))
        + list(SKILL_ROOT.glob("templates/**/*.json"))
    )
    existing_refs = {p.name for p in (SKILL_ROOT / "references").glob("*.md")}
    missing = []
    for doc in doc_files:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8")
        for match in ref_pattern.finditer(text):
            ref_file = match.group(1)
            if ref_file not in existing_refs:
                missing.append(f"{doc.relative_to(REPO_ROOT)} → references/{ref_file}")
    assert not missing, (
        f"{len(missing)} stale reference(s) to deleted files:\n"
        + "\n".join(sorted(missing))
    )


def test_variant_skills_point_at_canonical_script_style_source():
    """lite + nano distill the script-style rules from the full skill's refs;
    each must name the canonical source so future edits route there instead of
    forking and drifting the rule in place (provenance, not a hard import)."""
    lite = (REPO_ROOT / "skills" / "video-podcast-maker-lite" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    nano = (REPO_ROOT / "skills" / "video-podcast-maker-nano" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    # lite distils the zh-CN rules; nano the language-agnostic ones. Both must
    # name natural-narration.md / script-polish.md as the canonical source.
    assert "natural-narration.md" in lite and "script-polish.md" in lite
    assert "canonical" in nano
