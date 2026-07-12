"""TTS backend registry."""
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


def resolve_azure_style():
    """Resolve Azure mstts:express-as style.

    Precedence: env TTS_STYLE > user_prefs.json > 'gentle'.
    Empty string ("") explicitly disables the express-as wrapper — useful when
    the chosen voice has poor style support (e.g. Multilingual variants) or
    when a style produces vocoder artifacts on certain phonetic transitions.

    Returns (style, source) where source is 'env', 'user_prefs', or 'default'.
    """
    env = os.environ.get('TTS_STYLE')
    if env is not None:  # honour empty string
        return env, 'env'
    pref = user_prefs_get('global', 'tts', 'azure_style')
    if pref is not None:
        return pref, 'user_prefs'
    return 'gentle', 'default'


def _resolve_voice(backend_name, env_var, default):
    """Resolve voice with precedence: env var > user_prefs.json > hardcoded default."""
    env_val = os.environ.get(env_var)
    pref_val = user_prefs_get('global', 'tts', 'voices', backend_name)
    voice = env_val or pref_val or default
    source = 'env' if env_val else 'user_prefs' if pref_val else 'default'
    print(f"  Voice ({backend_name}): {voice} [from {source}]")
    return voice


# `supports_ssml` is the suite-wide source of truth for whether a backend
# accepts inline SSML markup (<lang>, <phoneme>, <break>, etc.) in the
# synthesize input. Currently only Azure constructs an SSML doc; the rest
# pass plain text and would either escape or speak any markup aloud. This
# field drives:
#   - tts/ssml.py wrap_mode_for() — picks 'off' for non-SSML backends
#   - generate_tts.py phoneme warning — emits unified warning for all
#     non-SSML backends instead of hand-listing names
BACKENDS = {
    'azure': {
        'module': '.azure',
        'env': ['AZURE_SPEECH_KEY'],
        'import': ('azure.cognitiveservices.speech', 'azure-cognitiveservices-speech',
                    'pip install azure-cognitiveservices-speech'),
        # Bumped from 400 to 2000 so a typical 5–10 min podcast fits in 1 chunk
        # (zero concat seams). Azure SSML accepts up to ~10 min audio per call;
        # 2000 chars stays well under that envelope.
        'max_chars': 2000,
        'supports_ssml': True,
    },
    'cosyvoice': {
        'module': '.cosyvoice',
        'env': ['DASHSCOPE_API_KEY'],
        'import': ('dashscope', 'dashscope', 'pip install dashscope'),
        'max_chars': 400,
        'supports_ssml': False,
    },
    'edge': {
        'module': '.edge',
        'env': [],
        'import': ('edge_tts', 'edge-tts', 'pip install edge-tts'),
        # Bumped from 400 to 2000 — Edge's WebSocket reliably handles long
        # payloads (same Microsoft TTS as Azure under the hood).
        'max_chars': 2000,
        'supports_ssml': False,
    },
    'doubao': {
        'module': '.doubao',
        'env': ['VOLCENGINE_APPID', 'VOLCENGINE_ACCESS_TOKEN'],
        'import': ('requests', 'requests', 'pip install requests'),
        'max_chars': 280,
        'supports_ssml': False,
    },
    'elevenlabs': {
        'module': '.elevenlabs',
        'env': ['ELEVENLABS_API_KEY'],
        'import': ('requests', 'requests', 'pip install requests'),
        'max_chars': 400,
        'supports_ssml': False,
    },
    'openai': {
        'module': '.openai_tts',
        'env': ['OPENAI_API_KEY'],
        'import': ('requests', 'requests', 'pip install requests'),
        'max_chars': 400,
        'supports_ssml': False,
    },
    'google': {
        'module': '.google_tts',
        'env': ['GOOGLE_TTS_API_KEY'],
        'import': ('requests', 'requests', 'pip install requests'),
        'max_chars': 400,
        'supports_ssml': False,
    },
    # Bridge to the ttsCN component skill — adds its providers (tencent,
    # baidu, minimax, xunfei, ...) without duplicating adapters. Env vars are
    # validated by ttsCN itself for the platform actually chosen
    # (TTSCN_PLATFORM); install detection happens in _build_config.
    'ttscn': {
        'module': '.ttscn',
        'env': [],
        'import': ('subprocess', 'python3', ''),
        'max_chars': 2000,
        'supports_ssml': False,
    },
}


def init_backend(name):
    """Validate dependencies and env vars for a backend. Returns config dict.

    Raises:
        UnknownBackendError: name not in BACKENDS registry.
        MissingPackageError: required Python module is not installed.
        MissingEnvVarError: required env var is unset.

    The caller (generate_tts.py main) routes these through cli_envelope so
    agents see a structured error envelope instead of a bare exit code.
    """
    if name not in BACKENDS:
        raise UnknownBackendError(
            f"Unknown backend '{name}'. Use: {', '.join(BACKENDS.keys())}"
        )

    info = BACKENDS[name]

    mod_name, pkg_name, install_cmd = info['import']
    try:
        __import__(mod_name)
    except ImportError as e:
        raise MissingPackageError(
            f"'{pkg_name}' not installed. Run: {install_cmd}",
            package=pkg_name, install_cmd=install_cmd,
        ) from e

    for var in info['env']:
        if not os.environ.get(var):
            raise MissingEnvVarError(f"{var} not set", var=var)

    return _build_config(name)


def get_synthesize_func(name):
    """Import and return the synthesize function for a backend."""
    from importlib import import_module
    mod = import_module(BACKENDS[name]['module'], package='tts.backends')
    return mod.synthesize


def get_max_chars(name):
    """Return max chunk size for a backend."""
    return BACKENDS[name]['max_chars']


def _build_config(name):
    """Build backend-specific config dict from environment variables."""
    config = {}
    if name == 'azure':
        config['key'] = os.environ['AZURE_SPEECH_KEY']
        config['region'] = os.environ.get('AZURE_SPEECH_REGION', 'eastasia')
        # Default to standard XiaoxiaoNeural — Multilingual variant ignores SAPI phoneme tags for zh-CN
        config['voice'] = _resolve_voice('azure', 'AZURE_TTS_VOICE', 'zh-CN-XiaoxiaoNeural')
        style, src = resolve_azure_style()
        config['style'] = style
        if style:
            print(f"  Azure style: {style} [from {src}]")
        else:
            print(f"  Azure style: (none — express-as wrapper disabled) [from {src}]")
    elif name == 'edge':
        config['voice'] = _resolve_voice('edge', 'EDGE_TTS_VOICE', 'zh-CN-XiaoxiaoNeural')
    elif name == 'doubao':
        config['appid'] = os.environ['VOLCENGINE_APPID']
        config['token'] = os.environ['VOLCENGINE_ACCESS_TOKEN']
        config['cluster'] = os.environ.get('VOLCENGINE_CLUSTER', 'volcano_tts')
        config['voice'] = _resolve_voice('doubao', 'VOLCENGINE_VOICE_TYPE', 'BV001_streaming')
        config['endpoint'] = os.environ.get('VOLCENGINE_TTS_ENDPOINT', 'https://openspeech.bytedance.com/api/v1/tts')
    elif name == 'elevenlabs':
        config['key'] = os.environ['ELEVENLABS_API_KEY']
        config['voice'] = _resolve_voice('elevenlabs', 'ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')
        config['model'] = os.environ.get('ELEVENLABS_MODEL', 'eleven_multilingual_v2')
    elif name == 'openai':
        config['key'] = os.environ['OPENAI_API_KEY']
        config['voice'] = _resolve_voice('openai', 'OPENAI_TTS_VOICE', 'alloy')
        config['model'] = os.environ.get('OPENAI_TTS_MODEL', 'tts-1-hd')
    elif name == 'google':
        config['key'] = os.environ['GOOGLE_TTS_API_KEY']
        config['voice'] = _resolve_voice('google', 'GOOGLE_TTS_VOICE', 'en-US-Neural2-F')
        config['language'] = os.environ.get('GOOGLE_TTS_LANGUAGE', 'en-US')
    elif name == 'ttscn':
        import components
        _, entry = components.find_component('ttsCN')
        if entry is None:
            raise MissingPackageError(
                "ttsCN skill not found — set TTSCN_HOME or install under "
                "~/.claude/skills/ttsCN",
                package='ttsCN', install_cmd='export TTSCN_HOME=<skill root>',
            )
        config['entry'] = str(entry)
        config['platform'] = os.environ.get('TTSCN_PLATFORM', 'edge')
        # Empty default → omit --voice and let ttsCN resolve its own default
        config['voice'] = (os.environ.get('TTSCN_VOICE')
                           or user_prefs_get('global', 'tts', 'voices', 'ttscn'))
        print(f"  ttsCN bridge: platform={config['platform']} entry={config['entry']}")
    return config
