"""TTS backend routing table.

vpm ships two self-contained TTS backends: edge (free, no key) and azure
(Microsoft Speech SDK). Both synthesize in-house via `native.py`; no external
component skill is required. The former ttscn component skill dependency is
removed.

Each BACKENDS entry lists the env vars its backend needs, validated here for
fast-fail before any synthesize call. MAX_CHARS bounds chunk size so word
-boundary estimation error stays small.
"""

import json
import os

from _state import resolve_state_file

from .native import synthesize as _synthesize


class BackendError(Exception):
    """Base class for backend init failures.

    Carries a `code` matching cli_envelope.ERROR_CODES so the CLI layer can
    route the failure through emit_error() without inventing new codes inline.
    """

    code = "internal_error"


class UnknownBackendError(BackendError):
    code = "validation_failed"


class MissingPackageError(BackendError):
    code = "tool_missing"

    def __init__(self, message, package=None, install_cmd=None):
        super().__init__(message)
        self.package = package
        self.install_cmd = install_cmd


class MissingEnvVarError(BackendError):
    code = "auth_missing_env"

    def __init__(self, message, var=None):
        super().__init__(message)
        self.var = var


def user_prefs_get(*keys):
    """Read nested key from user_prefs.json in shared state dir."""
    prefs_path = resolve_state_file(
        "user_prefs.json", template_filename="user_prefs.template.json"
    )
    if not prefs_path.exists():
        return None
    try:
        with open(prefs_path) as f:
            obj = json.load(f)
        for k in keys:
            if not isinstance(obj, dict):
                return None
            obj = obj.get(k)
        return obj
    except (json.JSONDecodeError, OSError):
        return None


def resolve_backend():
    """Resolve TTS backend with precedence: env TTS_BACKEND > user_prefs.json > 'edge'.

    Returns (name, source) where source is 'env', 'user_prefs', or 'default'.
    """
    env = os.environ.get("TTS_BACKEND")
    if env:
        return env, "env"
    pref = user_prefs_get("global", "tts", "backend")
    if pref:
        return pref, "user_prefs"
    return "edge", "default"


def resolve_speech_rate():
    """Resolve TTS speech rate with precedence: env TTS_RATE > user_prefs.json > '+5%'.

    Returns (rate, source) where source is 'env', 'user_prefs', or 'default'.
    """
    env = os.environ.get("TTS_RATE")
    if env:
        return env, "env"
    pref = user_prefs_get("global", "tts", "rate")
    if pref:
        return pref, "user_prefs"
    return "+5%", "default"


# Routing table: the only backends are the two local the skill can synthesize.
BACKENDS = {
    "edge": {"env": []},
    "azure": {"env": ["AZURE_SPEECH_KEY"]},
}

MAX_CHARS = 400


def _resolve_voice(name):
    """Voice precedence: env TTS_VOICE > user_prefs.json voices.<name> > None.

    Returns None when nothing is set — the local backend then applies its
    per-platform default voice.
    """
    return os.environ.get("TTS_VOICE") or user_prefs_get(
        "global", "tts", "voices", name
    )


def init_backend(name):
    """Validate the routing entry and build the local backend config dict.

    Raises:
        UnknownBackendError: name not in BACKENDS registry.
        MissingEnvVarError: a required env var for the platform is unset.

    The caller (generate_tts.py main) routes these through cli_envelope so
    agents see a structured error envelope instead of a bare exit code.
    """
    if name not in BACKENDS:
        raise UnknownBackendError(
            f"Unknown backend '{name}'. Use: {', '.join(BACKENDS.keys())}"
        )

    for var in BACKENDS[name]["env"]:
        if not os.environ.get(var):
            raise MissingEnvVarError(f"{var} not set", var=var)

    platform = name
    voice = _resolve_voice(name)
    print(f"  Local engine: platform={platform}")
    print(f"  Voice: {voice or f'(default for {platform})'}")
    config = {"platform": platform, "voice": voice}
    if platform == "azure":
        # Env TTS_STYLE > user_prefs > 'gentle'; "" disables the wrapper.
        style = os.environ.get("TTS_STYLE")
        if style is None:
            pref = user_prefs_get("global", "tts", "style")
            style = pref if pref is not None else "gentle"
        config["style"] = style
    return config


def get_synthesize_func(name):
    """Return the synthesize function — always the local backend."""
    return _synthesize


def get_max_chars(name):
    """Return max chunk size (flat 400 for both local backends)."""
    return MAX_CHARS
