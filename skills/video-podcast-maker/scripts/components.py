#!/usr/bin/env python3
"""Capability probe for optional component skills.

video-podcast-maker delegates asset production to sibling skills (assetSeeker,
imagenCN, videogenCN, ttsCN) by invoking their CLI scripts as subprocesses.
This probe reports which components are installed and credentialed BEFORE the
workflow plans assets, so the agent knows which producers it can use and the
pipeline can degrade gracefully instead of failing mid-run.

Discovery order per component (first hit wins):
  1. <NAME>_HOME env var (e.g. IMAGENCN_HOME) pointing at the skill root
  2. Extra parent dirs from VPM_COMPONENT_ROOTS (colon-separated)
  3. ~/.claude/skills/<dirname>   (symlinks resolved)

A "skill root" may hold the runtime directly (scripts/...) or in the
marketplace repo layout (skills/<dirname>/scripts/...); both are handled.

Usage:
    components.py probe [--format auto|json|prose]
"""
import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cli_envelope  # noqa: E402

# Entry scripts are the components' public CLI surface; env_any lists the
# provider keys of which at least ONE must be set for the component to be
# usable ([] = usable with no key at all).
COMPONENTS = {
    "assetSeeker": {
        "entry": "scripts/seek_assets.py",
        "env_any": [],
        "env_optional": ["PEXELS_API_KEY", "UNSPLASH_ACCESS_KEY", "PIXABAY_API_KEY",
                         "FREESOUND_API_KEY", "GOOGLE_FONTS_API_KEY"],
        "provides": "stock photos/video/BGM/SFX/icons/fonts (Iconify needs no key)",
    },
    "imagenCN": {
        "entry": "scripts/generate_image.py",
        "env_any": ["DASHSCOPE_API_KEY", "ARK_API_KEY", "HUNYUAN_API_KEY",
                    "ZHIPUAI_API_KEY", "STEP_API_KEY"],
        "env_optional": [],
        "provides": "AI stills (scene illustrations, thumbnails)",
    },
    "videogenCN": {
        "entry": "scripts/generate_video.py",
        "env_any": ["DASHSCOPE_API_KEY", "ARK_API_KEY", "MINIMAX_API_KEY",
                    "HUNYUAN_API_KEY"],
        "env_optional": [],
        "provides": "AI video clips (B-roll, i2v)",
    },
    "ttsCN": {
        "entry": "scripts/tts.py",
        "env_any": [],
        "env_optional": ["VOLCENGINE_APPID", "DASHSCOPE_API_KEY", "AZURE_SPEECH_KEY",
                         "TENCENT_SECRET_ID", "BAIDU_APP_ID", "MINIMAX_API_KEY",
                         "XUNFEI_APP_ID"],
        "provides": "TTS bridge backends (P4; Edge works with no key)",
    },
}


def _candidate_roots(name):
    """Yield possible skill roots for a component, in priority order."""
    home_env = f"{name.upper()}_HOME"
    if os.environ.get(home_env):
        yield Path(os.environ[home_env])
    for parent in os.environ.get("VPM_COMPONENT_ROOTS", "").split(":"):
        if parent:
            yield Path(parent).expanduser() / name
    yield Path.home() / ".claude" / "skills" / name


def find_component(name):
    """Return (root, entry_path) for an installed component, or (None, None)."""
    entry = COMPONENTS[name]["entry"]
    for root in _candidate_roots(name):
        try:
            root = root.resolve()
        except OSError:
            continue
        for base in (root, root / "skills" / name):
            script = base / entry
            if script.is_file():
                return base, script
    return None, None


HYPERFRAMES_MIN_NODE = 22


def _node_major():
    """Return the installed Node.js major version, or None."""
    try:
        out = subprocess.check_output(["node", "--version"], text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.match(r"v(\d+)", out.strip())
    return int(m.group(1)) if m else None


def _probe_hyperframes():
    """Hyperframes is an npx tool, not a skill — only Node >= 22 is required."""
    major = _node_major()
    usable = major is not None and major >= HYPERFRAMES_MIN_NODE
    if major is None:
        hint = "node not found — install Node.js 22+"
    elif not usable:
        hint = f"node v{major} too old — Hyperframes needs Node {HYPERFRAMES_MIN_NODE}+"
    else:
        hint = None
    return {
        "installed": major is not None,
        "root": None,
        "entry": "npx hyperframes",
        "env_ready": True,
        "env_present": [],
        "usable": usable,
        "provides": "transparent overlay renders (WebM VP9 alpha; charts, transitions)",
        "hint": hint,
        "node_major": major,
    }


def probe():
    """Return the availability matrix for all components."""
    report = {"hyperframes": _probe_hyperframes()}
    for name, spec in COMPONENTS.items():
        base, script = find_component(name)
        env_any = spec["env_any"]
        present = [v for v in env_any + spec["env_optional"] if os.environ.get(v)]
        env_ready = not env_any or any(os.environ.get(v) for v in env_any)
        usable = script is not None and env_ready
        hint = None
        if script is None:
            hint = (f"not installed — set {name.upper()}_HOME or install under "
                    f"~/.claude/skills/{name}")
        elif not env_ready:
            hint = f"installed but no API key — set one of: {', '.join(env_any)}"
        report[name] = {
            "installed": script is not None,
            "root": str(base) if base else None,
            "entry": str(script) if script else None,
            "env_ready": env_ready,
            "env_present": present,
            "usable": usable,
            "provides": spec["provides"],
            "hint": hint,
        }
    return report


def main():
    started_at = time.time()
    parser = argparse.ArgumentParser(
        prog="components.py",
        description="Probe optional component skills (installed? credentialed?).")
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")
    sp = sub.add_parser("probe", help="Report the component availability matrix")
    cli_envelope.add_format_arg(sp)
    args = parser.parse_args()

    report = probe()
    if not cli_envelope.use_json(args):
        for name, r in report.items():
            mark = "✓" if r["usable"] else ("~" if r["installed"] else "✗")
            print(f"  {mark} {name:<12} {r['provides']}")
            if r["hint"]:
                print(f"      {r['hint']}")
            elif r["env_present"]:
                print(f"      keys: {', '.join(r['env_present'])}")
        usable = [n for n, r in report.items() if r["usable"]]
        print(f"{len(usable)}/{len(report)} components usable: {', '.join(usable) or '-'}")
    sys.exit(cli_envelope.emit_success(args, {
        "components": report,
        "usable": [n for n, r in report.items() if r["usable"]],
    }, started_at=started_at))


if __name__ == "__main__":
    main()
