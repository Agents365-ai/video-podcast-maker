"""TTS backend routing table.

Since v4.0.0 vpm ships no provider adapters of its own: every backend id
routes through the ttsCN component skill via the single bridge adapter
(tts/backends/ttscn.py). vpm keeps orchestration (chunking, [SECTION:*]
parsing, SRT/timing.json, phonemes.json); ttsCN owns synthesis, marker
rendering, and phoneme application per platform.

Each BACKENDS entry lists the env vars its ttsCN platform needs — validated
here for fast-fail before any subprocess call (ttsCN re-validates on its
side). max_chars is a flat 400 for all platforms: word-boundary estimation
error is bounded by chunk length, and ttsCN sub-chunks internally per
provider limit.
"""
import json
import os


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
    """Read nested key from user_prefs.json. Returns None if missing/unreadable."""
    # __file__ = scripts/tts/backends/__init__.py → skill root is four levels up
    skill_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    prefs_path = os.path.join(skill_dir, 'user_prefs.json')
    if not os.path.exists(prefs_path):
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
    env = os.environ.get('TTS_BACKEND')
    if env:
        return env, 'env'
    pref = user_prefs_get('global', 'tts', 'backend')
    if pref:
        return pref, 'user_prefs'
    return 'edge', 'default'


def resolve_speech_rate():
    """Resolve TTS speech rate with precedence: env TTS_RATE > user_prefs.json > '+5%'.

    Returns (rate, source) where source is 'env', 'user_prefs', or 'default'.
    """
    env = os.environ.get('TTS_RATE')
    if env:
        return env, 'env'
    pref = user_prefs_get('global', 'tts', 'rate')
    if pref:
        return pref, 'user_prefs'
    return '+5%', 'default'


# Routing table: each backend id maps 1:1 to the ttsCN platform of the same
# name, except the legacy 'ttscn' alias whose platform comes from the
# TTSCN_PLATFORM env var (default 'edge'), exactly as before v4.0.0.
BACKENDS = {
    'edge':       {'env': []},
    'azure':      {'env': ['AZURE_SPEECH_KEY']},
    'cosyvoice':  {'env': ['DASHSCOPE_API_KEY']},
    'doubao':     {'env': ['VOLCENGINE_APPID', 'VOLCENGINE_ACCESS_TOKEN']},
    'tencent':    {'env': ['TENCENT_SECRET_ID', 'TENCENT_SECRET_KEY']},
    'baidu':      {'env': ['BAIDU_APP_ID', 'BAIDU_API_KEY', 'BAIDU_SECRET_KEY']},
    'minimax':    {'env': ['MINIMAX_API_KEY']},
    'xunfei':     {'env': ['XUNFEI_APP_ID', 'XUNFEI_API_KEY', 'XUNFEI_API_SECRET']},
    'elevenlabs': {'env': ['ELEVENLABS_API_KEY']},
    'openai':     {'env': ['OPENAI_API_KEY']},
    'google':     {'env': ['GOOGLE_TTS_API_KEY']},
    'ttscn':      {'env': []},
}

MAX_CHARS = 400

# Legacy per-backend voice env vars (pre-4.0) — kept so existing setups keep
# working. The generic TTS_VOICE covers every id, including the new ones.
_VOICE_ENV = {
    'azure': 'AZURE_TTS_VOICE',
    'edge': 'EDGE_TTS_VOICE',
    'doubao': 'VOLCENGINE_VOICE_TYPE',
    'elevenlabs': 'ELEVENLABS_VOICE_ID',
    'openai': 'OPENAI_TTS_VOICE',
    'google': 'GOOGLE_TTS_VOICE',
    'ttscn': 'TTSCN_VOICE',
}


def _resolve_voice(name):
    """Voice precedence: TTS_VOICE > legacy per-backend env var > user_prefs.

    Returns None when nothing is set — the bridge then omits --voice and
    ttsCN resolves its own per-platform default (no default-voice table is
    duplicated here).
    """
    return (os.environ.get('TTS_VOICE')
            or os.environ.get(_VOICE_ENV.get(name, ''), '')
            or user_prefs_get('global', 'tts', 'voices', name))


def init_backend(name):
    """Validate the routing entry and build the bridge config dict.

    Raises:
        UnknownBackendError: name not in BACKENDS registry.
        MissingPackageError: the ttsCN component skill is not installed.
        MissingEnvVarError: a required env var for the platform is unset.

    The caller (generate_tts.py main) routes these through cli_envelope so
    agents see a structured error envelope instead of a bare exit code.
    """
    if name not in BACKENDS:
        raise UnknownBackendError(
            f"Unknown backend '{name}'. Use: {', '.join(BACKENDS.keys())}"
        )

    import components
    _, entry = components.find_component('ttsCN')
    if entry is None:
        raise MissingPackageError(
            "ttsCN component skill not found (required for all TTS backends) "
            "— set TTSCN_HOME or install under ~/.claude/skills/ttsCN "
            "(https://github.com/Agents365-ai/ttsCN)",
            package='ttsCN', install_cmd='export TTSCN_HOME=<skill root>',
        )

    for var in BACKENDS[name]['env']:
        if not os.environ.get(var):
            raise MissingEnvVarError(f"{var} not set", var=var)

    platform = name if name != 'ttscn' else os.environ.get('TTSCN_PLATFORM', 'edge')
    voice = _resolve_voice(name)
    print(f"  ttsCN engine: platform={platform} entry={entry}")
    print(f"  Voice: {voice or f'(ttsCN default for {platform})'}")
    config = {'entry': str(entry), 'platform': platform, 'voice': voice}
    if platform == 'azure':
        # ttsCN's azure adapter reads TTS_STYLE from env (mstts:express-as).
        # Preserve the pre-4.0 default: env TTS_STYLE > user_prefs > 'gentle',
        # where "" explicitly disables the wrapper.
        style = os.environ.get('TTS_STYLE')
        if style is None:
            pref = user_prefs_get('global', 'tts', 'style')
            style = pref if pref is not None else 'gentle'
        config['style'] = style
    return config


def get_synthesize_func(name):
    """Return the synthesize function — always the ttsCN bridge."""
    from . import ttscn
    return ttscn.synthesize


def get_max_chars(name):
    """Return max chunk size (flat 400 for all routed platforms)."""
    return MAX_CHARS
