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
    assert not report["imagencn"]["installed"]
    assert not report["imagencn"]["usable"]
    assert "not installed" in report["imagencn"]["hint"]


def test_flat_layout_discovered_via_roots(monkeypatch, tmp_path):
    _fake_skill(tmp_path, "assetseeker", "scripts/seek_assets.py")
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    report = components.probe()
    a = report["assetseeker"]
    assert a["installed"] and a["usable"]  # no key required
    assert a["entry"].endswith("assetseeker/scripts/seek_assets.py")


def test_nested_marketplace_layout_discovered(monkeypatch, tmp_path):
    _fake_skill(tmp_path, "videogencn", "scripts/generate_video.py", nested=True)
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test")
    report = components.probe()
    v = report["videogencn"]
    assert v["installed"] and v["env_ready"] and v["usable"]
    assert "/skills/videogencn/" in v["entry"]


def test_installed_without_key_is_not_usable(monkeypatch, tmp_path):
    _fake_skill(tmp_path, "videogencn", "scripts/generate_video.py")
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    for var in ("DASHSCOPE_API_KEY", "ARK_API_KEY", "MINIMAX_API_KEY", "HUNYUAN_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    report = components.probe()
    v = report["videogencn"]
    assert v["installed"] and not v["env_ready"] and not v["usable"]
    assert "no API key" in v["hint"]


def test_home_env_override_wins(monkeypatch, tmp_path):
    decoy = _fake_skill(tmp_path / "roots", "ttscn", "scripts/tts.py")
    preferred = _fake_skill(tmp_path / "override", "ttscn", "scripts/tts.py")
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path / "roots"))
    monkeypatch.setenv("TTSCN_HOME", str(preferred))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    report = components.probe()
    assert report["ttscn"]["root"] == str(preferred.resolve())
    assert str(decoy) not in report["ttscn"]["root"]


def test_mixed_case_dirname_discovered_flat(monkeypatch, tmp_path):
    """Installs use mixed casing (assetSeeker vs assetseeker); discovery must
    still find them (assertion is FS-agnostic — APFS normalizes the returned
    spelling, a case-sensitive FS keeps the original)."""
    _fake_skill(tmp_path, "assetSeeker", "scripts/seek_assets.py")
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    root, entry = components.find_component("assetseeker")
    assert root is not None
    assert entry.is_file()


def test_mixed_case_dirname_discovered_nested(monkeypatch, tmp_path):
    """Both levels can differ in case: root ttsCN, nested dir ttscn — the real install layout."""
    script = tmp_path / "ttsCN" / "skills" / "ttscn" / "scripts" / "tts.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("#!/usr/bin/env python3\n")
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    root, entry = components.find_component("ttscn")
    assert root is not None
    assert entry.is_file()


def test_mixed_case_entry_script(monkeypatch, tmp_path):
    """Entry script casing may also differ (Generate_Image.py vs generate_image.py)."""
    base = tmp_path / "imagencn" / "skills" / "imagencn"
    script = base / "scripts" / "Generate_Image.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("#!/usr/bin/env python3\n")
    monkeypatch.setenv("VPM_COMPONENT_ROOTS", str(tmp_path))
    monkeypatch.setattr(components.Path, "home", staticmethod(lambda: tmp_path / "nohome"))
    root, entry = components.find_component("imagencn")
    assert root is not None
    assert entry.is_file()


def test_case_insensitive_fallback_fires(monkeypatch, tmp_path):
    """Deterministic check of the CI fallback on a case-sensitive filesystem:
    the exact-spelling probe misses, the directory scan must find the match.
    (APFS can't reproduce this — it resolves either spelling — so fake it.)"""
    (tmp_path / "assetSeeker").mkdir()
    original_exists = type(tmp_path).exists

    def cs_exists(self):
        if self.name == "assetseeker" and self.parent == tmp_path:
            return False
        return original_exists(self)

    monkeypatch.setattr(type(tmp_path), "exists", cs_exists)
    got = components._case_insensitive_path(tmp_path, "assetseeker")
    assert got.name == "assetSeeker"
    assert got.is_dir()
