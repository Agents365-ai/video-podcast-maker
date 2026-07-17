"""Tests for verify_output.check_overlay_assets — overlay spec enforcement."""
import verify_output


def _manifest(**extra):
    entry = {
        "id": "chart", "section": "features", "type": "overlay",
        "role": "overlay", "source": "hyperframes", "status": "resolved",
        "path": "assets/chart.webm", "license": "self-rendered (Hyperframes)",
    }
    entry.update(extra)
    return {"schema_version": 1, "assets": [entry]}


def _probe(monkeypatch, info):
    monkeypatch.setattr(verify_output, "ffprobe_video", lambda path: info)


GOOD = {"width": 3840, "height": 2160, "duration": 8.2, "video_codec": "vp9",
        "audio_codec": None, "fps": 30.0, "pix_fmt": "yuva420p"}


def test_good_overlay_passes(monkeypatch, tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "chart.webm").write_bytes(b"x")
    _probe(monkeypatch, dict(GOOD))
    errors, warnings, details = verify_output.check_overlay_assets(
        tmp_path, _manifest(duration_s=8.2))
    assert errors == [] and warnings == []
    assert details["chart"]["pix_fmt"] == "yuva420p"


def test_no_alpha_is_error(monkeypatch, tmp_path):
    _probe(monkeypatch, dict(GOOD, pix_fmt="yuv420p"))
    errors, _, _ = verify_output.check_overlay_assets(tmp_path, _manifest())
    assert any("no alpha channel" in e for e in errors)


def test_wrong_fps_is_error(monkeypatch, tmp_path):
    _probe(monkeypatch, dict(GOOD, fps=25.0))
    errors, _, _ = verify_output.check_overlay_assets(tmp_path, _manifest())
    assert any("fps" in e for e in errors)


def test_duration_drift_warns(monkeypatch, tmp_path):
    _probe(monkeypatch, dict(GOOD, duration=7.0))
    errors, warnings, _ = verify_output.check_overlay_assets(
        tmp_path, _manifest(duration_s=8.2))
    assert errors == []
    assert any("realign" in w for w in warnings)


def test_non_4k_warns(monkeypatch, tmp_path):
    _probe(monkeypatch, dict(GOOD, width=1920, height=1080))
    errors, warnings, _ = verify_output.check_overlay_assets(tmp_path, _manifest())
    assert errors == []
    assert any("full-frame 4K" in w for w in warnings)


def test_ffprobe_failure_is_error(monkeypatch, tmp_path):
    _probe(monkeypatch, None)
    errors, _, _ = verify_output.check_overlay_assets(tmp_path, _manifest())
    assert any("ffprobe failed" in e for e in errors)


def test_unresolved_and_non_overlay_assets_skipped(monkeypatch, tmp_path):
    _probe(monkeypatch, None)  # would error if probed
    manifest = {"schema_version": 1, "assets": [
        {"id": "p", "type": "overlay", "status": "planned"},
        {"id": "img", "type": "image", "status": "resolved", "path": "a.png"},
    ]}
    errors, warnings, details = verify_output.check_overlay_assets(tmp_path, manifest)
    assert errors == [] and warnings == [] and details == {}
