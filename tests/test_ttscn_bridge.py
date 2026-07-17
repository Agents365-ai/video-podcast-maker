"""Tests for the ttsCN routing table + bridge (tts/backends/)."""
import json
import os
import textwrap

import pytest

import tts.backends as backends
from tts.backends import (
    BACKENDS, init_backend, MissingEnvVarError, MissingPackageError,
)
from tts.backends.ttscn import synthesize

FAKE_TTSCN = textwrap.dedent("""\
    #!/usr/bin/env python3
    # Fake ttsCN entry: writes 0.3s of silence, echoes args as an envelope.
    # Emits native word_boundaries only for edge/azure (mirrors the contract).
    import json, sys, wave
    args = sys.argv[1:]
    text, output = args[0], args[1]
    platform = args[args.index("--platform") + 1]
    if "AUTHFAIL" in text:
        print(json.dumps({"ok": False, "error": {"code": "auth", "message": "no key"}}))
        sys.exit(3)
    if "FAIL" in text:
        print(json.dumps({"ok": False, "error": {"code": "backend", "message": "boom"}}))
        sys.exit(4)
    with wave.open(output, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes(b"\\x00\\x00" * int(24000 * 0.3))
    with open(output + ".args.json", "w") as f:
        json.dump(args, f)
    data = {"duration_seconds": 0.3, "output_file": output, "argv": args}
    if platform in ("edge", "azure"):
        step = 0.3 / max(len(text), 1)
        data["word_boundaries"] = [
            {"text": c, "offset_sec": i * step, "duration_sec": step}
            for i, c in enumerate(text)]
    print(json.dumps({"ok": True, "data": data}))
""")


@pytest.fixture
def fake_skill(tmp_path):
    """A fake ttsCN install (marketplace layout). Returns its entry path."""
    entry = tmp_path / "ttsCN" / "skills" / "ttsCN" / "scripts" / "tts.py"
    entry.parent.mkdir(parents=True)
    entry.write_text(FAKE_TTSCN)
    return entry


@pytest.fixture
def no_user_prefs(monkeypatch):
    """Isolate voice resolution from any real user_prefs.json on this machine."""
    monkeypatch.setattr(backends, "user_prefs_get", lambda *k: None)
    for var in ("TTS_VOICE", "AZURE_TTS_VOICE", "EDGE_TTS_VOICE", "TTSCN_VOICE"):
        monkeypatch.delenv(var, raising=False)


# --- routing table --------------------------------------------------------

def test_registry_routes_all_platforms():
    assert set(BACKENDS) == {
        "edge", "azure", "cosyvoice", "doubao", "tencent", "baidu",
        "minimax", "xunfei", "elevenlabs", "openai", "google", "ttscn",
    }
    assert BACKENDS["azure"]["env"] == ["AZURE_SPEECH_KEY"]
    assert BACKENDS["tencent"]["env"] == ["TENCENT_SECRET_ID", "TENCENT_SECRET_KEY"]
    assert BACKENDS["baidu"]["env"] == ["BAIDU_APP_ID", "BAIDU_API_KEY", "BAIDU_SECRET_KEY"]
    assert BACKENDS["minimax"]["env"] == ["MINIMAX_API_KEY"]
    assert BACKENDS["xunfei"]["env"] == ["XUNFEI_APP_ID", "XUNFEI_API_KEY", "XUNFEI_API_SECRET"]
    assert BACKENDS["ttscn"]["env"] == []


def test_init_backend_requires_ttscn_install_for_every_backend(monkeypatch, tmp_path):
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path / "empty"))
    monkeypatch.delenv("TTSCN_HOME", raising=False)
    import components
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path))
    with pytest.raises(MissingPackageError):
        init_backend("edge")


def test_init_backend_direct_id_sets_platform(monkeypatch, fake_skill, no_user_prefs):
    monkeypatch.setenv("TTSCN_HOME", str(fake_skill.parents[1]))
    monkeypatch.setenv("AZURE_SPEECH_KEY", "xxx")
    config = init_backend("azure")
    assert config["entry"] == str(fake_skill)
    assert config["platform"] == "azure"


def test_tts_backend_env_routes_to_bridge_platform(monkeypatch, fake_skill, no_user_prefs):
    # TTS_BACKEND=azure end-to-end: resolve_backend -> init_backend -> bridge config
    monkeypatch.setenv("TTS_BACKEND", "azure")
    monkeypatch.setenv("TTSCN_HOME", str(fake_skill.parents[1]))
    monkeypatch.setenv("AZURE_SPEECH_KEY", "xxx")
    name, source = backends.resolve_backend()
    assert (name, source) == ("azure", "env")
    assert init_backend(name)["platform"] == "azure"


def test_init_backend_env_fastfail(monkeypatch, fake_skill):
    monkeypatch.setenv("TTSCN_HOME", str(fake_skill.parents[1]))
    monkeypatch.delenv("TENCENT_SECRET_ID", raising=False)
    monkeypatch.delenv("TENCENT_SECRET_KEY", raising=False)
    with pytest.raises(MissingEnvVarError):
        init_backend("tencent")


def test_ttscn_alias_honors_platform_env(monkeypatch, fake_skill):
    monkeypatch.setenv("TTSCN_HOME", str(fake_skill.parents[1]))
    monkeypatch.setenv("TTSCN_PLATFORM", "tencent")
    config = init_backend("ttscn")
    assert config["entry"] == str(fake_skill)
    assert config["platform"] == "tencent"


def test_voice_omitted_by_default(monkeypatch, fake_skill, no_user_prefs):
    monkeypatch.setenv("TTSCN_HOME", str(fake_skill.parents[1]))
    assert init_backend("edge")["voice"] is None


def test_voice_env_resolution(monkeypatch, fake_skill, no_user_prefs):
    monkeypatch.setenv("TTSCN_HOME", str(fake_skill.parents[1]))
    monkeypatch.setenv("AZURE_SPEECH_KEY", "xxx")
    monkeypatch.setenv("AZURE_TTS_VOICE", "zh-CN-YunyangNeural")  # legacy var
    assert init_backend("azure")["voice"] == "zh-CN-YunyangNeural"
    monkeypatch.setenv("TTS_VOICE", "zh-CN-XiaoyiNeural")  # generic wins
    assert init_backend("azure")["voice"] == "zh-CN-XiaoyiNeural"


# --- bridge synthesis -----------------------------------------------------

def test_synthesize_estimation_fallback(fake_skill, tmp_path):
    # Platform without native boundaries -> per-char estimation.
    out = tmp_path / "out"
    out.mkdir()
    config = {"entry": str(fake_skill), "platform": "minimax",
              "voice": "female-shaonv", "speech_rate": "+5%"}
    parts, boundaries, duration = synthesize(["你好。", "世界。"], config, str(out))
    assert len(parts) == 2
    assert duration == pytest.approx(0.6, abs=0.01)
    for p in parts:
        assert os.path.exists(p)
    # raw intermediate files are cleaned up
    assert not list(out.glob("*_ttscn.wav"))
    # estimated word boundaries cover both chunks with increasing offsets
    assert len(boundaries) == 6  # "你好。" + "世界。" visible chars
    offsets = [b["offset"] for b in boundaries]
    assert offsets == sorted(offsets)
    assert boundaries[3]["offset"] >= 0.3  # second chunk starts after first


def test_native_boundaries_shifted_per_chunk(fake_skill, tmp_path):
    # edge/azure report native word_boundaries — offsets are absolute within
    # each chunk's file and must be shifted by prior chunks' durations.
    out = tmp_path / "out"
    out.mkdir()
    config = {"entry": str(fake_skill), "platform": "azure"}
    _, boundaries, duration = synthesize(["你好。", "世界。"], config, str(out))
    assert duration == pytest.approx(0.6, abs=0.01)
    assert len(boundaries) == 6  # fake emits one boundary per char
    assert boundaries[0]["offset"] == pytest.approx(0.0)
    # first boundary of chunk 2 == accumulated duration of chunk 1
    assert boundaries[3]["offset"] == pytest.approx(0.3, abs=0.01)
    offsets = [b["offset"] for b in boundaries]
    assert offsets == sorted(offsets)
    assert all(b["duration"] > 0 for b in boundaries)


def test_raw_text_passthrough(fake_skill, tmp_path):
    # ttsCN owns marker rendering — the bridge must send the chunk verbatim,
    # while estimated boundary text stays marker-free.
    out = tmp_path / "out"
    out.mkdir()
    chunk = "你好。[PAUSE:0.8]这是重庆。(chuckle)"
    _, boundaries, _ = synthesize([chunk], {"entry": str(fake_skill),
                                            "platform": "minimax"}, str(out))
    sent = json.loads((out / "part_0_ttscn.wav.args.json").read_text())[0]
    assert sent == chunk
    joined = "".join(b["text"] for b in boundaries)
    assert "PAUSE" not in joined and "chuckle" not in joined and "重" in joined


def test_synthesize_forwards_flags(fake_skill, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    phonemes = tmp_path / "phonemes_resolved.json"
    phonemes.write_text('{"重庆": "chóng qìng"}')
    config = {"entry": str(fake_skill), "platform": "baidu",
              "voice": "du-xiaomei", "speech_rate": "-10%",
              "phonemes_path": str(phonemes)}
    synthesize(["测试。"], config, str(out))
    argv = json.loads((out / "part_0_ttscn.wav.args.json").read_text())
    assert argv[2:4] == ["--platform", "baidu"]
    assert argv[argv.index("--voice") + 1] == "du-xiaomei"
    assert argv[argv.index("--rate") + 1] == "-10%"
    assert argv[argv.index("--phonemes") + 1] == str(phonemes)


def test_synthesize_backend_error_raises(fake_skill, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(RuntimeError, match="synthesis failed"):
        synthesize(["FAIL。"], {"entry": str(fake_skill)}, str(out))


def test_synthesize_auth_error_no_retry(fake_skill, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(RuntimeError, match="auth"):
        synthesize(["AUTHFAIL。"], {"entry": str(fake_skill)}, str(out))


def test_resume_skips_existing_parts(fake_skill, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    config = {"entry": str(fake_skill), "platform": "tencent"}
    parts, _, d1 = synthesize(["你好。"], config, str(out))
    parts2, _, d2 = synthesize(["你好。"], config, str(out), resume=True)
    assert parts == parts2
    assert d2 == pytest.approx(d1, abs=0.05)


def test_merge_native_boundaries_reinserts_punctuation():
    from tts.backends.ttscn import _merge_native_boundaries
    chunk = "大家好,欢迎。重庆[PAUSE:0.5]很美。"
    native = [
        {"text": "大家", "offset_sec": 0.0, "duration_sec": 0.4},
        {"text": "好", "offset_sec": 0.4, "duration_sec": 0.2},
        {"text": "欢迎", "offset_sec": 0.7, "duration_sec": 0.4},
        {"text": "重庆", "offset_sec": 1.3, "duration_sec": 0.5},
        {"text": "很美", "offset_sec": 2.4, "duration_sec": 0.5},
    ]
    merged = _merge_native_boundaries(chunk, native, 10.0)
    texts = [m["text"] for m in merged]
    # Punctuation from the script (ASCII and Chinese) is reinserted in order;
    # the [PAUSE:0.5] marker is not.
    assert texts == ["大家", "好", ",", "欢迎", "。", "重庆", "很美", "。"]
    # Word offsets are shifted by base_offset; punctuation anchors to the
    # preceding word's end.
    assert merged[0]["offset"] == 10.0
    assert merged[2]["offset"] == 10.0 + 0.4 + 0.2
    offsets = [m["offset"] for m in merged]
    assert offsets == sorted(offsets)
