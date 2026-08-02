from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "video-podcast-maker"
    / "scripts"
    / "hermes_worker.py"
)


def load_worker():
    spec = importlib.util.spec_from_file_location("hermes_worker", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ffprobe_resolution_accepts_trailing_empty_csv_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worker = load_worker()
    monkeypatch.setattr(
        worker,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0], 0, "3840,2160,\n", ""
        ),
    )
    assert worker.ffprobe_resolution(Path("video.mp4")) == (3840, 2160)


def test_run_decodes_windows_cp950_output(monkeypatch: pytest.MonkeyPatch) -> None:
    worker = load_worker()

    def fake_run(*args, **kwargs):
        assert kwargs["text"] is False
        return subprocess.CompletedProcess(
            args[0],
            0,
            stdout="渲染完成".encode("cp950"),
            stderr=b"",
        )

    monkeypatch.setattr(worker.subprocess, "run", fake_run)

    completed = worker.run(["render"], timeout=30)

    assert completed.stdout == "渲染完成"
    assert completed.stderr == ""


def test_run_decodes_windows_cp950_error(monkeypatch: pytest.MonkeyPatch) -> None:
    worker = load_worker()

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0],
            1,
            stdout=b"",
            stderr="渲染失敗".encode("cp950"),
        )

    monkeypatch.setattr(worker.subprocess, "run", fake_run)

    with pytest.raises(worker.WorkerFailure, match="渲染失敗"):
        worker.run(["render"], timeout=30)


def test_capabilities_are_local_only_and_never_publish() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", ".", "--capabilities"],
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["local_only"] is True
    assert payload["publication"] is False
    assert "publish" not in payload["stages"]
    assert payload["image_gen"] == "comfyui-bridge-local"
    assert payload["render"] == "windows-native-remotion"


def test_artifact_root_must_stay_under_configured_base(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    worker = load_worker()
    allowed = tmp_path / "allowed"
    monkeypatch.setenv("HERMES_VIDEO_ARTIFACT_BASE", str(allowed))
    request = {
        "artifact_root": str(tmp_path / "escape"),
    }
    with pytest.raises(worker.WorkerFailure, match="escapes"):
        worker.allowed_artifact_root(request)

    valid = allowed / "vp_1" / "youtube_long_16x9"
    request["artifact_root"] = str(valid)
    assert worker.allowed_artifact_root(request) == valid.resolve()
    assert valid.is_dir()


def test_parse_sections_and_sentence_cues_are_deterministic() -> None:
    worker = load_worker()
    text = (
        "[SECTION:hook|開場]行銷正在工程化嗎？\n\n"
        "[SECTION:takeaway|結論]不要先學工具，先設計系統。"
    )
    sections = worker.parse_sections(text)
    assert sections == [
        {"name": "hook", "label": "開場", "text": "行銷正在工程化嗎？"},
        {
            "name": "takeaway",
            "label": "結論",
            "text": "不要先學工具，先設計系統。",
        },
    ]
    cleaned = worker.clean_script(text)
    assert "SECTION" not in cleaned
    normalized = worker.normalize_script_for_pipeline(text)
    assert normalized.startswith("[SECTION:hook]\n")
    assert "[SECTION:takeaway]\n" in normalized
    assert "|開場" not in normalized
    cues = worker.sentence_cues(cleaned, 12.0, max_chars=12)
    assert cues[0]["start_time"] == 0.0
    assert cues[-1]["end_time"] == 12.0
    assert all(cue["text"] for cue in cues)
    assert cues == worker.sentence_cues(worker.clean_script(text), 12.0, max_chars=12)


def test_outputs_include_only_existing_files_and_hashes(tmp_path: Path) -> None:
    worker = load_worker()
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested/b.txt").write_text("beta", encoding="utf-8")
    outputs = worker.outputs_for(
        tmp_path,
        ["a.txt", "nested/b.txt", "missing.txt"],
        marker=True,
    )
    assert outputs["marker"] is True
    assert set(outputs["artifact_paths"]) == {"a.txt", "nested_b.txt"}
    assert set(outputs["artifact_hashes"]) == {"a.txt", "nested_b.txt"}
    assert all(len(value) == 64 for value in outputs["artifact_hashes"].values())


def test_scene_plan_repair_uses_positional_timing_and_deep_components() -> None:
    worker = load_worker()
    sections = [
        "hook",
        "problem",
        "framework",
        "case",
        "framework",
        "framework",
        "takeaway",
        "cta",
    ]
    scenes = [
        {
            "id": f"scene-{index}",
            "section": section,
            "component": "ChapterCard" if section in {"case", "takeaway"} else "Timeline",
            "title": "下集見" if section == "cta" else f"{section} title",
            "key_text": f"{section} key text",
            "items": [
                f"{section} point one",
                f"{section} point two with a concrete explanation",
                f"{section} point three",
            ],
            "start_frame": 9999,
            "end_frame": 10000,
        }
        for index, section in enumerate(sections)
    ]
    cursor = 0
    timing_sections = []
    for index, section in enumerate(sections):
        duration = 300 + index * 10
        timing_sections.append(
            {
                "name": section,
                "start_frame": cursor,
                "duration_frames": duration,
            }
        )
        cursor += duration
    repaired = worker.repair_scene_plan(
        {"schema_version": "cloudsea35-video-scene-plan-v1", "scenes": scenes},
        {"total_frames": cursor, "sections": timing_sections},
    )

    assert repaired["repair_contract"] == "hermes-scene-plan-repair-v1"
    assert repaired["total_frames"] == cursor
    repaired_scenes = repaired["scenes"]
    assert [scene["component"] for scene in repaired_scenes] == [
        "QuoteBlock",
        "FeatureGrid",
        "Timeline",
        "FeatureGrid",
        "Timeline",
        "FeatureGrid",
        "QuoteBlock",
        "DailyInsight",
    ]
    assert [scene["start_frame"] for scene in repaired_scenes] == [
        section["start_frame"] for section in timing_sections
    ]
    assert [scene["end_frame"] for scene in repaired_scenes] == [
        section["start_frame"] + section["duration_frames"]
        for section in timing_sections
    ]
    for scene in repaired_scenes:
        assert scene["visual_design"]["focal_point"]
        assert scene["visual_design"]["visual_layers"]["primary"]
        assert len(scene["visual_beats"]) == 3
    for index in (1, 3, 5):
        assert repaired_scenes[index]["items"]
        assert set(repaired_scenes[index]["items"][0]) == {
            "icon",
            "title",
            "description",
        }
    for index in (2, 4):
        assert set(repaired_scenes[index]["items"][0]) == {
            "label",
            "description",
        }
    assert repaired_scenes[-1]["title"] == "你會先工程化哪個流程？"
    assert repaired_scenes[-1]["visual_structure"] == "cta"


def test_scene_plan_repair_rejects_ambiguous_timing() -> None:
    worker = load_worker()
    with pytest.raises(worker.WorkerFailure, match="count mismatch"):
        worker.repair_scene_plan(
            {"scenes": [{"section": "hook"}, {"section": "cta"}]},
            {
                "total_frames": 30,
                "sections": [
                    {"name": "hook", "start_frame": 0, "duration_frames": 30}
                ],
            },
        )


def test_design_audit_json_is_persisted_and_blockers_fail(tmp_path: Path) -> None:
    worker = load_worker()
    passed = {
        "score": 92,
        "issues": [],
        "warnings": [{"type": "WARNING", "message": "review this"}],
    }
    result = worker.persist_design_audit(
        tmp_path, json.dumps(passed, ensure_ascii=False)
    )
    assert result == passed
    persisted = json.loads(
        (tmp_path / "qa/audit-report.json").read_text(encoding="utf-8")
    )
    assert persisted == passed

    blocked = {
        "score": 70,
        "issues": [
            {
                "type": "BLOCKER",
                "check": "chapter_card_duration",
                "message": "ChapterCard is too long",
            }
        ],
    }
    with pytest.raises(worker.WorkerFailure, match="ChapterCard is too long"):
        worker.persist_design_audit(
            tmp_path, json.dumps(blocked, ensure_ascii=False)
        )
    persisted_blocked = json.loads(
        (tmp_path / "qa/audit-report.json").read_text(encoding="utf-8")
    )
    assert persisted_blocked == blocked


def test_image_generation_uses_local_bridge_and_copies_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    worker = load_worker()
    root = tmp_path / "artifacts"
    root.mkdir()
    plan = {
        "schema_version": "cloudsea35-video-scene-plan-v1",
        "scenes": [{"id": "s1", "title": "開場", "component": "BrandIntro"}],
    }
    (root / "scene-plan.json").write_text(
        json.dumps(plan, ensure_ascii=False), encoding="utf-8"
    )
    generated = tmp_path / "generated.png"
    generated.write_bytes(b"\x89PNG\r\n\x1a\n" + b"image-data")
    captured: dict = {}

    def fake_bridge(payload, timeout=1200):
        captured.update(payload)
        assert timeout == 1200
        return {
            "status": "success",
            "output_path": str(generated),
            "prompt_id": "prompt-1",
        }

    monkeypatch.setattr(worker, "bridge_generate", fake_bridge)
    request = {
        "production_id": "vp_test",
        "deliverable_id": "vd_test",
        "run_id": "vr_test",
        "stage": "image_gen",
        "artifact_root": str(root),
        "inputs": {"source_text": "Hermes 影片開場"},
    }
    outputs = worker.stage_image_gen(request, root, tmp_path)
    assert captured["width"] == 1536
    assert captured["height"] == 864
    assert captured["preset"] == "official"
    assert Path(outputs["artifact_paths"]["assets_primary_visual.png"]).is_file()
    updated = json.loads((root / "scene-plan.json").read_text(encoding="utf-8"))
    assert updated["primary_visual"] == "assets/primary_visual.png"
    assert updated["primary_visual_request_id"].startswith("vr_test")


def test_qa_generates_evidence_and_requires_all_gates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    worker = load_worker()
    project = tmp_path / "project"
    root = tmp_path / "artifacts"
    project.mkdir()
    (project / "poc-project").mkdir()
    (project / "generate_qa_report.py").write_text("# qa generator\n", encoding="utf-8")
    root.mkdir()
    for name in (
        "final-video.mp4",
        "branded-output.mp4",
        "podcast_audio.wav",
        "scene-plan.json",
        "timing.json",
    ):
        (root / name).write_bytes(b"artifact")
    (root / "qa").mkdir()
    for name in ("render-checkpoints.json", "qa_report.html"):
        (root / "qa" / name).write_text("{}", encoding="utf-8")

    calls: list[tuple[list[str], Path | None]] = []

    def fake_run(command, *, cwd=None, **kwargs):
        calls.append((list(command), cwd))
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(worker, "run", fake_run)
    monkeypatch.setattr(worker, "ffprobe_duration", lambda path: 47.0)
    monkeypatch.setattr(worker, "ffprobe_resolution", lambda path: (3840, 2160))
    monkeypatch.setattr(worker, "ffmpeg_black_duration", lambda path: 0.0)
    request = {"inputs": {}}
    (root / "qa/visual-publishability.json").write_text(
        json.dumps({"visual_publishable": False}), encoding="utf-8"
    )
    (root / "qa/audit-report.json").write_text(
        json.dumps({"blockers": []}), encoding="utf-8"
    )
    with pytest.raises(worker.WorkerFailure, match="visual_publishable"):
        worker.stage_qa(request, root, project)

    (root / "qa/visual-publishability.json").write_text(
        json.dumps({"visual_publishable": True}), encoding="utf-8"
    )
    (root / "qa/audit-report.json").write_text(
        json.dumps({"blockers": ["black frames"]}), encoding="utf-8"
    )
    with pytest.raises(worker.WorkerFailure, match="1 blocker"):
        worker.stage_qa(request, root, project)

    (root / "qa/audit-report.json").write_text(
        json.dumps({"blockers": []}), encoding="utf-8"
    )
    outputs = worker.stage_qa(request, root, project)
    assert outputs["visual_publishable"] is True
    assert outputs["blocker_count"] == 0
    assert outputs["resolution"] == "3840x2160"
    assert outputs["video_duration_seconds"] == 47.0
    assert [sys.executable, str(project / "generate_qa_report.py"), str(root), "--json-only"] in [
        command for command, _ in calls
    ]
    assert (["npx", "tsc", "--noEmit"], project / "poc-project") in calls


def test_main_rejects_publish_stage_without_side_effects(tmp_path: Path) -> None:
    request = {
        "production_id": "vp_test",
        "deliverable_id": "vd_test",
        "stage": "publish",
        "run_id": "vr_test",
        "attempt": 1,
        "artifact_root": str(tmp_path / "artifacts"),
        "inputs": {},
    }
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", str(tmp_path)],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] == "failed"
    assert "unsupported stage" in payload["error"]
    assert not (tmp_path / "artifacts").exists()
