"""TTS backend routing table.

Since v4.0.0 vpm ships no provider adapters of its own: every backend id
routes through the ttscn component skill via the single bridge adapter
(tts/backends/ttscn.py). vpm keeps orchestration (chunking, [SECTION:*]
parsing, SRT/timing.json, phonemes.json); ttscn owns synthesis, marker
rendering, and phoneme application per platform.

Each BACKENDS entry lists the env vars its ttscn platform needs — validated
here for fast-fail before any subprocess call (ttscn re-validates on its
side). max_chars is a flat 400 for all platforms: word-boundary estimation
error is bounded by chunk length, and ttscn sub-chunks internally per
provider limit.
"""

import json
import os

from _state import resolve_state_file


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


# Routing table: each backend id maps 1:1 to the ttscn platform of the
# same name.
BACKENDS = {
    "edge": {"env": []},
    "azure": {"env": ["AZURE_SPEECH_KEY"]},
    "cosyvoice": {"env": ["DASHSCOPE_API_KEY"]},
    "doubao": {"env": ["VOLCENGINE_APPID", "VOLCENGINE_ACCESS_TOKEN"]},
    "tencent": {"env": ["TENCENT_SECRET_ID", "TENCENT_SECRET_KEY"]},
    "baidu": {"env": ["BAIDU_APP_ID", "BAIDU_API_KEY", "BAIDU_SECRET_KEY"]},
    "minimax": {"env": ["MINIMAX_API_KEY"]},
    "xunfei": {"env": ["XUNFEI_APP_ID", "XUNFEI_API_KEY", "XUNFEI_API_SECRET"]},
    "elevenlabs": {"env": ["ELEVENLABS_API_KEY"]},
    "openai": {"env": ["OPENAI_API_KEY"]},
    "google": {"env": ["GOOGLE_TTS_API_KEY"]},
}

MAX_CHARS = 400


def _resolve_voice(name):
    """Voice precedence: env TTS_VOICE > user_prefs.json voices.<name> > None.

    Returns None when nothing is set — the bridge then omits --voice and
    ttscn resolves its own per-platform default (no default-voice table is
    duplicated here).
    """
    return (
        os.environ.get("TTS_VOICE")
        or user_prefs_get("global", "tts", "voices", name)
    )


def init_backend(name):
    """Validate the routing entry and build the bridge config dict.

    Raises:
        UnknownBackendError: name not in BACKENDS registry.
        MissingPackageError: the ttscn component skill is not installed.
        MissingEnvVarError: a required env var for the platform is unset.

    The caller (generate_tts.py main) routes these through cli_envelope so
    agents see a structured error envelope instead of a bare exit code.
    """
    if name not in BACKENDS:
        raise UnknownBackendError(
            f"Unknown backend '{name}'. Use: {', '.join(BACKENDS.keys())}"
        )

    import components

    _, entry = components.find_component("ttscn")
    if entry is None:
        raise MissingPackageError(
            "ttscn component skill not found (required for all TTS backends) "
            "— set TTSCN_HOME or install under ~/.claude/skills/ttscn "
            "(https://github.com/Agents365-ai/ttsCN)",
            package="ttscn",
            install_cmd="export TTSCN_HOME=<skill root>",
        )

    for var in BACKENDS[name]["env"]:
        if not os.environ.get(var):
            raise MissingEnvVarError(f"{var} not set", var=var)

    platform = name
    voice = _resolve_voice(name)
    print(f"  ttscn engine: platform={platform} entry={entry}")
    print(f"  Voice: {voice or f'(ttscn default for {platform})'}")
    config = {"entry": str(entry), "platform": platform, "voice": voice}
    if platform == "azure":
        # ttscn's azure adapter reads TTS_STYLE from env (mstts:express-as).
        # Preserve the pre-4.0 default: env TTS_STYLE > user_prefs > 'gentle',
        # where "" explicitly disables the wrapper.
        style = os.environ.get("TTS_STYLE")
        if style is None:
            pref = user_prefs_get("global", "tts", "style")
            style = pref if pref is not None else "gentle"
        config["style"] = style
    return config


def get_synthesize_func(name):
    """Return the synthesize function — always the ttscn bridge."""
    from . import ttscn

    return ttscn.synthesize


def get_max_chars(name):
    """Return max chunk size (flat 400 for all routed platforms)."""
    return MAX_CHARS
