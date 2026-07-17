"""Tests for components.py — the component-skill capability probe."""
import components


def _fake_skill(root, name, entry_rel, nested=False):
    """Create a fake component install; returns the skill root."""
    base = root / name / "skills" / name if nested else root / name
    script = base / entry_rel
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("#!/usr/bin/env python3\n")
    return base


def test_not_installed_reports_hint(monkeypatch, tmp_path):
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path / "empty"))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path))
    for var in ("IMAGENCN_HOME", "DASHSCOPE_API_KEY", "ARK_API_KEY",
                "HUNYUAN_API_KEY", "ZHIPUAI_API_KEY", "STEP_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    report = components.probe()
    assert not report["imagenCN"]["installed"]
    assert not report["imagenCN"]["usable"]
    assert "not installed" in report["imagenCN"]["hint"]


def test_flat_layout_discovered_via_roots(monkeypatch, tmp_path):
    _fake_skill(tmp_path, "assetSeeker", "scripts/seek_assets.py")
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    report = components.probe()
    a = report["assetSeeker"]
    assert a["installed"] and a["usable"]  # no key required
    assert a["entry"].endswith("assetSeeker/scripts/seek_assets.py")


def test_nested_marketplace_layout_discovered(monkeypatch, tmp_path):
    _fake_skill(tmp_path, "videogenCN", "scripts/generate_video.py", nested=True)
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test")
    report = components.probe()
    v = report["videogenCN"]
    assert v["installed"] and v["env_ready"] and v["usable"]
    assert "/skills/videogenCN/" in v["entry"]


def test_installed_without_key_is_not_usable(monkeypatch, tmp_path):
    _fake_skill(tmp_path, "videogenCN", "scripts/generate_video.py")
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    for var in ("DASHSCOPE_API_KEY", "ARK_API_KEY", "MINIMAX_API_KEY", "HUNYUAN_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    report = components.probe()
    v = report["videogenCN"]
    assert v["installed"] and not v["env_ready"] and not v["usable"]
    assert "no API key" in v["hint"]


def test_home_env_override_wins(monkeypatch, tmp_path):
    decoy = _fake_skill(tmp_path / "roots", "ttsCN", "scripts/tts.py")
    preferred = _fake_skill(tmp_path / "override", "ttsCN", "scripts/tts.py")
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path / "roots"))
    monkeypatch.setenv("TTSCN_HOME", str(preferred))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    report = components.probe()
    assert report["ttsCN"]["root"] == str(preferred.resolve())
    assert str(decoy) not in report["ttsCN"]["root"]
