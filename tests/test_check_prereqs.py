"""Tests for scripts/check_prereqs.py — prereq state computation."""
from unittest.mock import patch

import pytest

# scripts/ is on sys.path via tests/conftest.py
import components  # noqa: E402
from check_prereqs import check_prereqs, REQUIRED_BINS  # noqa: E402


@pytest.fixture(autouse=True)
def ttscn_installed(monkeypatch):
    """Every backend now requires the ttsCN component — pretend it's
    installed so tests don't depend on this machine; tests that exercise
    the missing-component path override this."""
    monkeypatch.setattr(components, "find_component",
                        lambda name: ("/x", "/x/scripts/tts.py"))


def _all_bins_present(name):
    """shutil.which mock: every binary appears installed."""
    return f"/usr/bin/{name}"


def _no_bins_present(name):
    """shutil.which mock: no binary is installed."""
    return None


def _make_resolve_backend(name='azure', source='env'):
    return lambda: (name, source)


# --- happy path ----------------------------------------------------------

def test_all_clean_when_bins_present_and_env_set():
    env = {'TTS_BACKEND': 'azure', 'AZURE_SPEECH_KEY': 'xxx'}
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('azure', 'env')):
        state = check_prereqs(env=env)
    assert state['missing_bins'] == []
    assert state['missing_env_vars'] == []
    assert state['backend'] == 'azure'
    assert state['required_env_vars'] == ['AZURE_SPEECH_KEY']


def test_edge_backend_requires_no_env_var():
    env = {}
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('edge', 'default')):
        state = check_prereqs(env=env)
    assert state['missing_env_vars'] == []
    assert state['required_env_vars'] == []


# --- missing-tool path ---------------------------------------------------

def test_missing_all_bins_listed():
    env = {'AZURE_SPEECH_KEY': 'xxx'}
    with patch('check_prereqs.shutil.which', _no_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('azure', 'env')):
        state = check_prereqs(env=env)
    assert state['missing_bins'] == REQUIRED_BINS
    assert state['missing_env_vars'] == []


def test_missing_specific_bin_only():
    def only_ffmpeg_missing(name):
        return None if name == 'ffmpeg' else f"/usr/bin/{name}"
    env = {'AZURE_SPEECH_KEY': 'xxx'}
    with patch('check_prereqs.shutil.which', only_ffmpeg_missing), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('azure', 'env')):
        state = check_prereqs(env=env)
    assert state['missing_bins'] == ['ffmpeg']
    assert state['missing_env_vars'] == []


# --- missing-env-var path ------------------------------------------------

def test_missing_env_var_for_azure():
    env = {}  # no AZURE_SPEECH_KEY
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('azure', 'env')):
        state = check_prereqs(env=env)
    assert state['missing_bins'] == []
    assert state['missing_env_vars'] == ['AZURE_SPEECH_KEY']


def test_missing_multiple_env_vars_for_doubao():
    env = {}  # no VOLCENGINE_*
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('doubao', 'env')):
        state = check_prereqs(env=env)
    assert set(state['missing_env_vars']) == {'VOLCENGINE_APPID', 'VOLCENGINE_ACCESS_TOKEN'}


def test_partial_env_var_present():
    env = {'VOLCENGINE_APPID': 'xxx'}  # token still missing
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('doubao', 'env')):
        state = check_prereqs(env=env)
    assert state['missing_env_vars'] == ['VOLCENGINE_ACCESS_TOKEN']


# --- both-missing path ---------------------------------------------------

def test_both_bins_and_env_missing():
    env = {}
    with patch('check_prereqs.shutil.which', _no_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('azure', 'env')):
        state = check_prereqs(env=env)
    assert state['missing_bins'] == REQUIRED_BINS
    assert state['missing_env_vars'] == ['AZURE_SPEECH_KEY']


# --- backend resolution failure --------------------------------------------

def test_resolve_backend_exception_falls_back_to_env():
    def explode():
        raise RuntimeError("user_prefs.json is malformed")
    env = {'TTS_BACKEND': 'cosyvoice', 'DASHSCOPE_API_KEY': 'xxx'}
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', explode):
        state = check_prereqs(env=env)
    assert state['backend'] == 'cosyvoice'
    assert state['backend_source'] == 'env'
    assert state['missing_env_vars'] == []


def test_resolve_backend_exception_no_env_falls_back_to_edge_default():
    def explode():
        raise RuntimeError("user_prefs.json is malformed")
    env = {}  # no TTS_BACKEND
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', explode):
        state = check_prereqs(env=env)
    assert state['backend'] == 'edge'
    assert state['backend_source'] == 'default'
    assert state['required_env_vars'] == []


# --- unknown backend graceful degradation -------------------------------

def test_unknown_backend_flags_backend_known_false():
    # If BACKENDS doesn't list the backend (e.g. user typo'd TTS_BACKEND),
    # we shouldn't crash — we just can't know what env vars it needs, so the
    # caller emits validation_failed rather than silently passing.
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('mystery_backend', 'env')):
        state = check_prereqs(env={})
    assert state['backend'] == 'mystery_backend'
    assert state['backend_known'] is False
    assert state['required_env_vars'] == []
    assert state['missing_env_vars'] == []


def test_known_backend_flags_backend_known_true():
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('edge', 'default')):
        state = check_prereqs(env={})
    assert state['backend_known'] is True


# --- ttsCN component check (required for every backend) ------------------

@pytest.mark.parametrize('backend', ['ttscn', 'edge', 'azure'])
def test_missing_ttscn_component_reported_for_any_backend(monkeypatch, backend):
    monkeypatch.setattr(components, 'find_component', lambda name: (None, None))
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend(backend, 'env')):
        state = check_prereqs(env={})
    assert state['missing_components'] == ['ttsCN']


def test_installed_component_passes():
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('edge', 'default')):
        state = check_prereqs(env={})
    assert state['missing_components'] == []


def test_unknown_backend_skips_component_check(monkeypatch):
    monkeypatch.setattr(components, 'find_component', lambda name: (None, None))
    with patch('check_prereqs.shutil.which', _all_bins_present), \
         patch('check_prereqs.resolve_backend', _make_resolve_backend('mystery', 'env')):
        state = check_prereqs(env={})
    assert state['missing_components'] == []
