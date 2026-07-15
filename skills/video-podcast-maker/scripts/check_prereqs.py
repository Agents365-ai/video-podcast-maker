#!/usr/bin/env python3
"""Pre-flight check: verify required CLIs exist and the resolved TTS backend has its env vars.

Backend is resolved with the same precedence as generate_tts.py:
    env TTS_BACKEND > user_prefs.json (global.tts.backend) > 'edge' default

Prose output (default for TTY; preserved for SKILL.md back-compat):
    ALL_OK (backend=<name>)
    MISSING:<space-separated items> (backend=<name>)

JSON output (default when stdout is piped; --format json forces it):
    success: { "ok": true,  "data": { backend, backend_source, required_bins, required_env_vars }, "meta": ... }
    failure: { "ok": false, "error": { code: tool_missing | auth_missing_env, message,
                                        retryable: false, missing_bins, missing_env_vars,
                                        backend, backend_source }, "meta": ... }

Exit codes:
    0 — all prerequisites satisfied
    2 — at least one required binary or env var is missing
        (was 'always 0' historically; SKILL.md only reads stdout so the
        change is additive — orchestrators can now use && chaining)
"""
import argparse
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cli_envelope  # noqa: E402
from tts.backends import BACKENDS, resolve_backend  # noqa: E402


REQUIRED_BINS = ["node", "python3", "ffmpeg"]


def check_prereqs(env=None):
    """Compute prereq state. Returns dict with backend, backend_source,
    backend_known, required_bins, required_env_vars, missing_bins, missing_env_vars.

    `env` overrides os.environ for testing (default: os.environ).
    Tool presence is checked via shutil.which and is not mockable through
    `env` — tests should monkeypatch shutil.which directly if needed.

    `backend_known` is False when the resolved name is not in the BACKENDS
    registry (typo in TTS_BACKEND or stale user_prefs.json). In that case
    required_env_vars is [] because we don't know what to ask for; the caller
    reports validation_failed instead of silently passing.
    """
    env = env if env is not None else os.environ
    try:
        backend, backend_source = resolve_backend()
    except Exception:
        backend = env.get("TTS_BACKEND", "edge")
        backend_source = "env" if env.get("TTS_BACKEND") else "default"

    backend_known = backend in BACKENDS
    required_env_vars = BACKENDS.get(backend, {}).get("env", [])
    missing_bins = [b for b in REQUIRED_BINS if not shutil.which(b)]
    missing_env_vars = [v for v in required_env_vars if not env.get(v)]

    # Since v4.0.0 every backend synthesizes through the ttsCN component
    # skill — validate the install here instead of letting generate_tts.py
    # fail at synthesis time.
    missing_components = []
    if backend_known:
        import components
        if components.find_component("ttsCN")[1] is None:
            missing_components.append("ttsCN")

    return {
        "backend": backend,
        "backend_source": backend_source,
        "backend_known": backend_known,
        "required_bins": REQUIRED_BINS,
        "required_env_vars": required_env_vars,
        "missing_bins": missing_bins,
        "missing_env_vars": missing_env_vars,
        "missing_components": missing_components,
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    cli_envelope.add_format_arg(parser)
    return parser


def main():
    args = build_parser().parse_args()
    started_at = time.time()

    state = check_prereqs()
    backend = state["backend"]
    missing_bins = state["missing_bins"]
    missing_env_vars = state["missing_env_vars"]
    missing_components = state["missing_components"]

    # Unknown backend wins over bin/env checks: we can't report missing env
    # vars for a backend we don't know, so flag the typo before anything else.
    if not state["backend_known"]:
        known = sorted(BACKENDS.keys())
        message = (
            f"Unknown TTS backend '{backend}' (resolved from {state['backend_source']}). "
            f"Known backends: {', '.join(known)}."
        )
        if cli_envelope.use_json(args):
            sys.exit(cli_envelope.emit_error(
                args, "validation_failed", message,
                extra={
                    "backend": backend,
                    "backend_source": state["backend_source"],
                    "known_backends": known,
                },
                started_at=started_at,
            ))
        print(f"UNKNOWN_BACKEND:{backend} (known: {','.join(known)})", file=sys.stderr)
        sys.exit(2)

    if not missing_bins and not missing_env_vars and not missing_components:
        if cli_envelope.use_json(args):
            sys.exit(cli_envelope.emit_success(args, {
                "backend": backend,
                "backend_source": state["backend_source"],
                "required_bins": state["required_bins"],
                "required_env_vars": state["required_env_vars"],
            }, started_at=started_at))
        print(f"ALL_OK (backend={backend})")
        sys.exit(0)

    # Some prereqs missing. Tool-missing dominates: a missing binary needs
    # an install; missing env vars only need export. Both map to exit 2 in
    # cli_envelope.ERROR_CODES so the orchestrator-side routing is the same,
    # but the code field tells the agent what kind of fix to suggest.
    code = "tool_missing" if missing_bins or missing_components else "auth_missing_env"
    all_missing = missing_bins + missing_env_vars + \
        [f"{c}(component)" for c in missing_components]

    hint = ""
    if missing_components:
        hint = (" The ttsCN component skill is required for all TTS backends — "
                "install it under ~/.claude/skills/ttsCN or set TTSCN_HOME "
                "(https://github.com/Agents365-ai/ttsCN).")

    if cli_envelope.use_json(args):
        sys.exit(cli_envelope.emit_error(
            args, code,
            f"{len(all_missing)} prereq(s) missing for backend '{backend}'.{hint}",
            extra={
                "backend": backend,
                "backend_source": state["backend_source"],
                "missing_bins": missing_bins,
                "missing_env_vars": missing_env_vars,
                "missing_components": missing_components,
            },
            started_at=started_at,
        ))
    print(f"MISSING:{' '.join(all_missing)} (backend={backend})")
    if hint:
        print(hint.strip(), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
