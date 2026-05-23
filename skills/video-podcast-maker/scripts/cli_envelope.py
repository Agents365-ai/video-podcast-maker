"""Standard JSON output envelope for the video-podcast-maker CLI suite.

Every CLI script in scripts/ should route final results and failures through
this module so agents and orchestrators see one stable contract on stdout:

    { "ok": true,  "data": {...}, "meta": {...} }
    { "ok": false, "error": { "code": "...", "message": "...", "retryable": false }, "meta": {...} }

Format selection
----------------
  --format auto  (default) JSON when stdout is not a TTY, prose otherwise
  --format json            always JSON
  --format prose           always legacy human output (no envelope)

Error code vocabulary (suite-wide; extend as needed)
----------------------------------------------------
  input_not_found        a required input file does not exist        (exit 1)
  input_invalid          a required input file is malformed          (exit 1)
  validation_failed      semantic validation rejected the input      (exit 1)
  auth_missing_env       a required env var for the backend is unset (exit 2)
  tool_missing           a required external binary is not on PATH   (exit 2)
  backend_failed         upstream API/backend returned an error      (exit 1, retryable)
  ffmpeg_failed          local ffmpeg subprocess failed              (exit 1)
  confirmation_required  destructive op invoked without --yes        (exit 3)
  internal_error         catch-all for unexpected exceptions         (exit 1)
"""
import json
import sys
import time
import uuid


ERROR_CODES = {
    "input_not_found":       {"retryable": False, "exit": 1},
    "input_invalid":         {"retryable": False, "exit": 1},
    "validation_failed":     {"retryable": False, "exit": 1},
    "auth_missing_env":      {"retryable": False, "exit": 2},
    "tool_missing":          {"retryable": False, "exit": 2},
    "backend_failed":        {"retryable": True,  "exit": 1},
    "ffmpeg_failed":         {"retryable": False, "exit": 1},
    "confirmation_required": {"retryable": False, "exit": 3},
    "internal_error":        {"retryable": False, "exit": 1},
}

SCHEMA_VERSION = "1.0.0"

# Capture the real stdout once, at import time, before any caller redirects it.
# Envelope writes always target this stream so JSON output cannot be swallowed
# by a `sys.stdout = sys.stderr` block used to silence verbose progress chatter.
_REAL_STDOUT = sys.stdout


def add_format_arg(parser):
    """Register --format on an argparse parser."""
    parser.add_argument(
        "--format",
        choices=("auto", "json", "prose"),
        default="auto",
        help="Output format: auto (JSON when stdout is not a TTY), json, or prose.",
    )


def use_json(args):
    """Return True if this run should emit a JSON envelope on stdout."""
    fmt = getattr(args, "format", "auto")
    if fmt == "json":
        return True
    if fmt == "prose":
        return False
    return not _REAL_STDOUT.isatty()


def emit_success(args, data, *, meta=None, started_at=None, exit_code=0):
    """Emit the success envelope. Returns ``exit_code`` (default 0).

    Caller pattern: ``sys.exit(emit_success(args, {...}))``.
    In prose mode this is a no-op — the script's existing prose is the human report.

    ``exit_code`` lets a caller signal a warned-but-publishable state without
    flipping ``ok`` to false. Use sparingly — agents should rely on the envelope
    body (e.g. a ``warnings`` list in ``data``), not on out-of-band exit codes.
    The current legitimate use is ``verify_output.py`` returning 2 for
    "warnings only, still publishable" to preserve a documented shell contract.
    """
    if not use_json(args):
        return exit_code
    envelope = {"ok": True, "data": data, "meta": _build_meta(meta, started_at)}
    print(json.dumps(envelope, ensure_ascii=False), file=_REAL_STDOUT)
    return exit_code


def emit_error(args, code, message, *, field=None, retryable=None,
               extra=None, started_at=None, meta=None):
    """Emit the failure envelope (JSON mode) or a prose error line (prose mode).

    Returns the exit code associated with `code`. Caller pattern:
    ``sys.exit(emit_error(args, "input_not_found", "..."))``.
    """
    spec = ERROR_CODES.get(code, ERROR_CODES["internal_error"])
    err = {
        "code": code,
        "message": message,
        "retryable": spec["retryable"] if retryable is None else retryable,
    }
    if field is not None:
        err["field"] = field
    if extra:
        err.update(extra)

    if use_json(args):
        envelope = {"ok": False, "error": err, "meta": _build_meta(meta, started_at)}
        print(json.dumps(envelope, ensure_ascii=False), file=_REAL_STDOUT)
    else:
        print(f"Error [{code}]: {message}", file=sys.stderr)
        if extra:
            for k, v in extra.items():
                print(f"  {k}: {v}", file=sys.stderr)
    return spec["exit"]


def _build_meta(extra, started_at):
    meta = {"request_id": uuid.uuid4().hex[:12], "schema_version": SCHEMA_VERSION}
    if started_at is not None:
        meta["latency_ms"] = int((time.time() - started_at) * 1000)
    if extra:
        meta.update(extra)
    return meta
