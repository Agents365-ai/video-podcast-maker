#!/usr/bin/env python3
"""Machine-readable local Worker adapter for Hermes Video Production.

Input: one WorkerRequest JSON object on stdin.
Output: one WorkerResult-compatible JSON object on stdout.

The adapter reuses the existing video-podcast-maker tools. It never mutates
Hermes Production State, never publishes, and never falls back to cloud
services. Chinese TTS and branded rendering use Windows-native local tools.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

STAGES = {"tts", "scene_plan", "image_gen", "render", "package", "qa"}
SECTION_RE = re.compile(
    r"\[SECTION:([A-Za-z0-9_-]+)(?:\|([^\]]+))?\]"
)
SENTENCE_RE = re.compile(r"[^。！？!?\n]+[。！？!?]?|[^\n]+")


class WorkerFailure(RuntimeError):
    pass


class NeedsHuman(WorkerFailure):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def emit(status: str, *, outputs: Mapping[str, Any] | None = None, error: str | None = None) -> int:
    print(
        json.dumps(
            {"status": status, "outputs": dict(outputs or {}), "error": error},
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def read_request() -> dict[str, Any]:
    value = json.load(sys.stdin)
    if not isinstance(value, dict):
        raise WorkerFailure("WorkerRequest must be a JSON object")
    required = (
        "production_id",
        "deliverable_id",
        "stage",
        "run_id",
        "artifact_root",
        "inputs",
    )
    missing = [name for name in required if name not in value]
    if missing:
        raise WorkerFailure(f"WorkerRequest missing fields: {', '.join(missing)}")
    if str(value["stage"]) not in STAGES:
        raise WorkerFailure(f"unsupported stage: {value['stage']}")
    if not isinstance(value["inputs"], dict):
        raise WorkerFailure("WorkerRequest.inputs must be an object")
    return value


def allowed_artifact_root(request: Mapping[str, Any]) -> Path:
    root = Path(str(request["artifact_root"])).expanduser().resolve()
    configured = Path(
        os.environ.get(
            "HERMES_VIDEO_ARTIFACT_BASE",
            str(Path.home() / ".local/share/hermes/video-productions"),
        )
    ).expanduser().resolve()
    try:
        root.relative_to(configured)
    except ValueError as exc:
        raise WorkerFailure(
            f"artifact_root escapes HERMES_VIDEO_ARTIFACT_BASE: {root}"
        ) from exc
    root.mkdir(parents=True, exist_ok=True)
    return root


def tool(project_root: Path, *relative_candidates: str) -> Path:
    for relative in relative_candidates:
        candidate = project_root / relative
        if candidate.is_file():
            return candidate
    raise NeedsHuman(
        "local_dependency_unavailable: none of " + ", ".join(relative_candidates)
    )


def decode_subprocess_output(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    for encoding in ("utf-8", "cp950"):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            continue
    return value.decode("utf-8", errors="replace")


def run(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    timeout: int,
    environment: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(environment or {})
    raw = subprocess.run(
        list(command),
        cwd=str(cwd) if cwd else None,
        env=env,
        text=False,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    completed = subprocess.CompletedProcess(
        args=raw.args,
        returncode=raw.returncode,
        stdout=decode_subprocess_output(raw.stdout),
        stderr=decode_subprocess_output(raw.stderr),
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise WorkerFailure(
            f"command failed ({completed.returncode}): {detail[-4000:]}"
        )
    return completed


def collect_paths(root: Path, names: Sequence[str]) -> dict[str, str]:
    paths: dict[str, str] = {}
    for name in names:
        path = root / name
        if path.is_file():
            paths[name.replace("/", "_")] = str(path.resolve())
    return paths


def outputs_for(root: Path, names: Sequence[str], **extra: Any) -> dict[str, Any]:
    paths = collect_paths(root, names)
    hashes = {name: sha256_file(Path(path)) for name, path in sorted(paths.items())}
    return {
        "artifact_paths": paths,
        "artifact_hashes": hashes,
        **extra,
    }


def clean_script(text: str) -> str:
    without_headers = SECTION_RE.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", without_headers).strip()


def normalize_script_for_pipeline(text: str) -> str:
    """Canonicalize inline/labeled markers for the existing pipeline parser."""

    def replace(match: re.Match[str]) -> str:
        return f"\n[SECTION:{match.group(1)}]\n"

    normalized = SECTION_RE.sub(replace, text)
    normalized = re.sub(r"[ \t]+\n", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def parse_sections(text: str) -> list[dict[str, str]]:
    matches = list(SECTION_RE.finditer(text))
    if not matches:
        return [{"name": "content", "label": "Content", "text": clean_script(text)}]
    sections: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append(
            {
                "name": match.group(1),
                "label": (match.group(2) or match.group(1)).strip(),
                "text": clean_script(text[start:end]),
            }
        )
    return [section for section in sections if section["text"]]


def wsl_to_windows(path: Path) -> str:
    completed = run(
        ["wslpath", "-w", str(path)], cwd=None, timeout=30
    )
    return completed.stdout.strip()


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def ffprobe_duration(path: Path) -> float:
    completed = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        timeout=60,
    )
    return float(completed.stdout.strip())


def srt_time(seconds: float) -> str:
    milliseconds = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def sentence_cues(text: str, duration: float, max_chars: int = 28) -> list[dict[str, Any]]:
    raw_sentences = [value.strip() for value in SENTENCE_RE.findall(text) if value.strip()]
    chunks: list[str] = []
    for sentence in raw_sentences:
        while len(sentence) > max_chars:
            split_at = max(
                sentence.rfind(mark, 0, max_chars + 1)
                for mark in ("，", "、", "；", "：", ",", ";", " ")
            )
            if split_at <= 0:
                split_at = max_chars
            chunks.append(sentence[:split_at].strip(" ，、；：,;"))
            sentence = sentence[split_at:].strip()
        if sentence:
            chunks.append(sentence)
    if not chunks:
        chunks = [text.strip() or "（無旁白）"]
    weights = [max(1, len(chunk)) for chunk in chunks]
    total_weight = sum(weights)
    cues: list[dict[str, Any]] = []
    cursor = 0.0
    for index, (chunk, weight) in enumerate(zip(chunks, weights), 1):
        end = duration if index == len(chunks) else cursor + duration * weight / total_weight
        cues.append(
            {
                "index": index,
                "text": chunk,
                "start_time": round(cursor, 3),
                "end_time": round(end, 3),
            }
        )
        cursor = end
    return cues


def stage_tts(request: Mapping[str, Any], root: Path, project_root: Path) -> dict[str, Any]:
    del project_root
    inputs = request["inputs"]
    source_text = str(inputs.get("source_text", "")).strip()
    if not source_text:
        source_path = root / "podcast.txt"
        if not source_path.is_file():
            raise WorkerFailure("source_text and podcast.txt are both missing")
        source_text = source_path.read_text(encoding="utf-8")
    script_path = root / "podcast.txt"
    pipeline_script = normalize_script_for_pipeline(source_text)
    script_path.write_text(pipeline_script.rstrip() + "\n", encoding="utf-8")
    speech_path = root / "speech.txt"
    spoken_text = clean_script(source_text)
    speech_path.write_text(spoken_text + "\n", encoding="utf-8")
    audio_path = root / "podcast_audio.wav"

    powershell = Path(
        "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    if not powershell.is_file():
        raise NeedsHuman("local_dependency_unavailable: Windows PowerShell TTS")
    voice = os.environ.get("HERMES_VIDEO_TTS_VOICE", "Microsoft Hanhan Desktop")
    rate = int(os.environ.get("HERMES_VIDEO_TTS_RATE", "1"))
    command = (
        "Add-Type -AssemblyName System.Speech; "
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.SelectVoice({ps_quote(voice)}); "
        f"$s.Rate={rate}; "
        f"$s.SetOutputToWaveFile({ps_quote(wsl_to_windows(audio_path))}); "
        "$t=[IO.File]::ReadAllText("
        f"{ps_quote(wsl_to_windows(speech_path))},[Text.Encoding]::UTF8); "
        "$s.Speak($t); $s.Dispose()"
    )
    run([str(powershell), "-NoProfile", "-Command", command], timeout=1800)
    if not audio_path.is_file() or audio_path.stat().st_size < 1024:
        raise WorkerFailure("Windows TTS did not produce a valid WAV")
    duration = ffprobe_duration(audio_path)
    cues = sentence_cues(spoken_text, duration)

    srt_path = root / "podcast_audio.srt"
    srt_path.write_text(
        "".join(
            f"{cue['index']}\n{srt_time(cue['start_time'])} --> "
            f"{srt_time(cue['end_time'])}\n{cue['text']}\n\n"
            for cue in cues
        ),
        encoding="utf-8",
    )

    sections = parse_sections(source_text)
    total_chars = sum(max(1, len(section["text"])) for section in sections)
    cursor = 0.0
    timing_sections: list[dict[str, Any]] = []
    for index, section in enumerate(sections):
        weight = max(1, len(section["text"]))
        end = duration if index == len(sections) - 1 else cursor + duration * weight / total_chars
        timing_sections.append(
            {
                "name": section["name"],
                "label": section["label"],
                "start_time": round(cursor, 3),
                "end_time": round(end, 3),
                "duration": round(end - cursor, 3),
                "start_frame": int(round(cursor * 30)),
                "duration_frames": max(1, int(round((end - cursor) * 30))),
            }
        )
        cursor = end
    timing_path = root / "timing.json"
    timing_path.write_text(
        json.dumps(
            {
                "schema_version": "cloudsea35-timing-v2",
                "total_duration": round(duration, 3),
                "fps": 30,
                "total_frames": int(round(duration * 30)),
                "method": "windows_system_speech_local_char_proportional",
                "sections": timing_sections,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return outputs_for(
        root,
        ["podcast.txt", "podcast_audio.wav", "podcast_audio.srt", "timing.json"],
        duration_seconds=round(duration, 3),
        tts_backend="windows-system-speech-local",
        voice=voice,
    )


def title_from_source(text: str) -> str:
    for line in text.splitlines():
        value = line.strip()
        if value and not value.startswith("[SECTION:"):
            return value[:80]
    return "Hermes Video Production"


def _scene_text_items(scene: Mapping[str, Any]) -> list[str]:
    raw_items = scene.get("items")
    values: list[str] = []
    if isinstance(raw_items, list):
        for item in raw_items:
            if isinstance(item, str):
                value = item.strip()
            elif isinstance(item, Mapping):
                value = str(
                    item.get("description")
                    or item.get("title")
                    or item.get("label")
                    or ""
                ).strip()
            else:
                value = str(item).strip()
            if value:
                values.append(value)
    if not values:
        for key in ("key_text", "title", "subtitle"):
            value = str(scene.get(key) or "").strip()
            if value and value not in values:
                values.append(value)
    return values[:6]


def _short_title(value: str, *, limit: int = 18) -> tuple[str, str]:
    normalized = re.sub(r"\s+", " ", value).strip()
    for separator in ("：", ":", "—", "－", "，", ","):
        if separator in normalized:
            head, tail = normalized.split(separator, 1)
            if 2 <= len(head.strip()) <= limit:
                return head.strip(), tail.strip() or normalized
    if len(normalized) <= limit:
        return normalized, normalized
    return normalized[:limit].rstrip(), normalized


def _feature_items(scene: Mapping[str, Any]) -> list[dict[str, str]]:
    icons = ("Workflow", "Database", "Target", "Gauge", "Layers", "CheckCircle")
    result: list[dict[str, str]] = []
    for index, value in enumerate(_scene_text_items(scene)):
        title, description = _short_title(value)
        result.append(
            {
                "icon": icons[index % len(icons)],
                "title": title,
                "description": description,
            }
        )
    return result


def _timeline_items(scene: Mapping[str, Any]) -> list[dict[str, str]]:
    return [
        {"label": f"{index:02d}", "description": value}
        for index, value in enumerate(_scene_text_items(scene), 1)
    ]


def _visual_design(
    *, title: str, visual_structure: str, primary: str, duration_frames: int
) -> dict[str, Any]:
    duration = max(1, duration_frames)
    first_end = max(1, duration // 3)
    second_end = max(first_end + 1, (duration * 2) // 3)
    return {
        "visual_goal": f"用{primary}呈現「{title}」的可執行結構",
        "composition": visual_structure,
        "focal_point": f"{title} 的核心{primary}",
        "visual_layers": {
            "background": "dark_navy_industrial_grid",
            "primary": primary,
            "secondary": "supporting_labels",
            "accent": "highlight_path",
            "subtitle_zone": "bottom_safe_zone",
        },
        "motion_plan": {
            "entrance": "staggered_reveal",
            "reveal": "reveal_primary_visual",
            "emphasis": "highlight_focal_point",
            "transition_out": "fade_out",
        },
        "text_layout": {
            "title_zone": "top_safe_zone",
            "body_zone": "center_safe_zone",
            "max_lines": 4,
        },
        "visual_density": "high" if duration >= 900 else "medium",
        "visual_beats": [
            {
                "start_frame": 0,
                "end_frame": first_end,
                "visual_event": "建立主要視覺結構",
            },
            {
                "start_frame": first_end,
                "end_frame": second_end,
                "visual_event": "依序揭示關鍵節點",
            },
            {
                "start_frame": second_end,
                "end_frame": duration,
                "visual_event": "聚焦結論與下一步",
            },
        ],
    }


def repair_scene_plan(plan: Mapping[str, Any], timing: Mapping[str, Any]) -> dict[str, Any]:
    """Repair shallow generator output into a monotonic publishable scene plan."""
    repaired = json.loads(json.dumps(plan, ensure_ascii=False))
    scenes = repaired.get("scenes")
    timing_sections = timing.get("sections")
    if not isinstance(scenes, list) or not isinstance(timing_sections, list):
        raise WorkerFailure("scene plan and timing must both contain section lists")
    if len(scenes) != len(timing_sections):
        raise WorkerFailure(
            "scene/timing count mismatch: "
            f"{len(scenes)} scenes != {len(timing_sections)} timing sections"
        )

    framework_index = 0
    for index, (scene, timing_section) in enumerate(
        zip(scenes, timing_sections, strict=True)
    ):
        if not isinstance(scene, dict) or not isinstance(timing_section, dict):
            raise WorkerFailure(f"scene {index} or timing section is not an object")
        section = str(timing_section.get("name") or scene.get("section") or "").lower()
        start_frame = int(timing_section.get("start_frame", 0))
        duration_frames = int(timing_section.get("duration_frames", 0))
        if duration_frames <= 0:
            raise WorkerFailure(f"scene {index} has non-positive duration")
        scene["section"] = section
        scene["start_frame"] = start_frame
        scene["duration_frames"] = duration_frames
        scene["end_frame"] = start_frame + duration_frames
        title = str(scene.get("title") or scene.get("key_text") or section).strip()

        if section == "hook":
            component, structure, primary = "QuoteBlock", "single_statement", "quote_block"
        elif section in {"problem", "case"}:
            component = "FeatureGrid"
            structure = "case_flow" if section == "case" else "checklist"
            primary = "card_grid"
        elif section == "takeaway":
            component, structure, primary = "QuoteBlock", "single_statement", "quote_block"
        elif section == "framework":
            framework_index += 1
            if framework_index <= 2:
                structure = "timeline" if framework_index == 1 else "roadmap"
                component, primary = "Timeline", "timeline"
            else:
                component, structure, primary = "FeatureGrid", "checklist", "card_grid"
        elif section == "cta":
            component, structure, primary = "DailyInsight", "cta", "checklist"
            if title.strip().lower() in {
                "下集見",
                "下期見",
                "謝謝觀看",
                "thanks for watching",
            }:
                title = "你會先工程化哪個流程？"
                scene["title"] = title
            text_items = _scene_text_items(scene)
            scene["detail"] = " ".join(text_items[:2])
            scene["category"] = "行銷工程化"
        else:
            component = str(scene.get("component") or "FeatureGrid")
            if component == "Timeline":
                structure, primary = "timeline", "timeline"
            elif component == "QuoteBlock":
                structure, primary = "single_statement", "quote_block"
            elif component == "DailyInsight":
                structure, primary = "cta", "checklist"
            else:
                component, structure, primary = "FeatureGrid", "checklist", "card_grid"

        scene["component"] = component
        scene["visual_structure"] = structure
        if component == "FeatureGrid":
            scene["items"] = _feature_items(scene)
        elif component == "Timeline":
            scene["items"] = _timeline_items(scene)
        scene["visual_design"] = _visual_design(
            title=title,
            visual_structure=structure,
            primary=primary,
            duration_frames=duration_frames,
        )
        scene["visual_beats"] = scene["visual_design"]["visual_beats"]

    expected_start = 0
    for index, scene in enumerate(scenes):
        if int(scene["start_frame"]) != expected_start:
            raise WorkerFailure(
                f"scene {index} timing is not contiguous: "
                f"expected {expected_start}, got {scene['start_frame']}"
            )
        expected_start = int(scene["end_frame"])
    total_frames = int(timing.get("total_frames", expected_start))
    if expected_start != total_frames:
        raise WorkerFailure(
            f"scene plan ends at {expected_start}, timing ends at {total_frames}"
        )
    repaired["repair_contract"] = "hermes-scene-plan-repair-v1"
    repaired["total_frames"] = total_frames
    return repaired


def persist_design_audit(root: Path, raw_json: str) -> dict[str, Any]:
    try:
        audit_result = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise WorkerFailure(f"design audit returned invalid JSON: {exc}") from exc
    if not isinstance(audit_result, dict):
        raise WorkerFailure("design audit result must be an object")
    qa_dir = root / "qa"
    qa_dir.mkdir(exist_ok=True)
    audit_path = qa_dir / "audit-report.json"
    audit_path.write_text(
        json.dumps(audit_result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    blockers = [
        issue
        for issue in audit_result.get("issues", [])
        if isinstance(issue, Mapping) and issue.get("type") == "BLOCKER"
    ]
    if blockers:
        messages = [str(issue.get("message", "design blocker")) for issue in blockers]
        raise WorkerFailure("design_audit_blocked: " + " | ".join(messages))
    return audit_result


def stage_scene_plan(request: Mapping[str, Any], root: Path, project_root: Path) -> dict[str, Any]:
    inputs = request["inputs"]
    prepare = tool(
        project_root,
        "prepare_branded_assets.py",
        "skills/video-podcast-maker/scripts/prepare_branded_assets.py",
    )
    source_text = str(inputs.get("source_text", ""))
    run(
        [
            sys.executable,
            str(prepare),
            "--podcast",
            str(root / "podcast.txt"),
            "--audio",
            str(root / "podcast_audio.wav"),
            "--video-name",
            str(request["production_id"]),
            "--title",
            title_from_source(source_text),
            "--output-dir",
            str(root),
        ],
        cwd=project_root,
        timeout=600,
    )
    required = root / "scene-plan.json"
    timing_path = root / "timing.json"
    if not required.is_file() or not timing_path.is_file():
        raise WorkerFailure("scene-plan.json and timing.json must be produced")
    plan = json.loads(required.read_text(encoding="utf-8"))
    timing = json.loads(timing_path.read_text(encoding="utf-8"))
    repaired = repair_scene_plan(plan, timing)
    required.write_text(
        json.dumps(repaired, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    storyboard = None
    try:
        storyboard = tool(
            project_root,
            "generate_storyboard.py",
            "skills/video-podcast-maker/scripts/generate_storyboard.py",
        )
    except NeedsHuman:
        storyboard = None
    if storyboard is not None:
        run(
            [sys.executable, str(storyboard), str(root)],
            cwd=project_root,
            timeout=180,
        )

    design_audit = tool(
        project_root,
        "design_audit.py",
        "skills/video-podcast-maker/scripts/design_audit.py",
    )
    audit_completed = run(
        [sys.executable, str(design_audit), str(root), "--json"],
        cwd=project_root,
        timeout=180,
    )
    persist_design_audit(root, audit_completed.stdout)
    return outputs_for(
        root,
        [
            "scene-plan.json",
            "storyboard.html",
            "subtitles.json",
            "timing.json",
            "podcast_audio.srt",
            "qa/audit-report.json",
        ],
        scene_plan_repair_contract="hermes-scene-plan-repair-v1",
    )


def bridge_generate(payload: Mapping[str, Any], timeout: int = 1200) -> dict[str, Any]:
    request = urllib.request.Request(
        "http://127.0.0.1:8190/generate",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        raise NeedsHuman(f"capability_unavailable: ComfyUI Bridge: {exc}") from exc
    if not isinstance(value, dict) or value.get("status") != "success":
        raise WorkerFailure(f"ComfyUI Bridge generation failed: {value}")
    return value


def stage_image_gen(request: Mapping[str, Any], root: Path, project_root: Path) -> dict[str, Any]:
    del project_root
    plan_path = root / "scene-plan.json"
    if not plan_path.is_file():
        raise WorkerFailure("scene-plan.json is required before image_gen")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    scenes = plan.get("scenes", []) if isinstance(plan, dict) else []
    scene_titles = [str(scene.get("title", "")) for scene in scenes[:6] if isinstance(scene, dict)]
    prompt = {
        "purpose": "primary visual for a CloudSea35 knowledge video",
        "title": title_from_source(str(request["inputs"].get("source_text", ""))),
        "scene_context": scene_titles,
        "requirements": [
            "16:9 cinematic composition",
            "dark navy industrial technology aesthetic",
            "no text, no logos, no watermark, no human face",
            "clear primary visual suitable for a branded Remotion video",
        ],
    }
    request_id = re.sub(
        r"[^A-Za-z0-9_-]", "_", f"{request['run_id']}_primary_visual"
    )
    result = bridge_generate(
        {
            "request_id": request_id,
            "prompt": prompt,
            "preset": "official",
            "width": 1536,
            "height": 864,
            "seed": int(hashlib.sha256(request_id.encode()).hexdigest()[:8], 16),
            "filename_prefix": request_id[:80],
            "timeout": 1200,
        }
    )
    source = Path(str(result.get("output_path", ""))).expanduser()
    if not source.is_file():
        raise WorkerFailure("ComfyUI result output_path is missing")
    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    destination = assets / "primary_visual.png"
    shutil.copy2(source, destination)
    if isinstance(plan, dict):
        plan["primary_visual"] = "assets/primary_visual.png"
        plan["primary_visual_request_id"] = request_id
        plan_path.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return outputs_for(
        root,
        ["scene-plan.json", "assets/primary_visual.png"],
        comfyui_request_id=request_id,
        prompt_id=result.get("prompt_id"),
    )


def windows_render_paths(production_id: str) -> tuple[Path, Path, str, str]:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", production_id)
    windows_wsl_root = Path("/mnt/c/Users/User/video-podcast-maker")
    windows_video = windows_wsl_root / "videos" / safe
    output_wsl = windows_video / "branded-output.mp4"
    output_win = f"C:\\Users\\User\\video-podcast-maker\\videos\\{safe}\\branded-output.mp4"
    public_win = "C:\\Users\\User\\video-podcast-maker\\poc-project\\src\\remotion\\public"
    return windows_video, output_wsl, output_win, public_win


def stage_render(request: Mapping[str, Any], root: Path, project_root: Path) -> dict[str, Any]:
    cmd = Path("/mnt/c/Windows/System32/cmd.exe")
    windows_project = Path("/mnt/c/Users/User/video-podcast-maker/poc-project")
    if not cmd.is_file() or not windows_project.is_dir():
        raise NeedsHuman("capability_unavailable: Windows-native Remotion render")
    sync = tool(project_root, "sync-components-to-windows.sh")
    run(["bash", str(sync), str(project_root / "poc-project")], cwd=project_root, timeout=300)

    windows_video, output_wsl, output_win, public_win = windows_render_paths(
        str(request["production_id"])
    )
    windows_video.mkdir(parents=True, exist_ok=True)
    public_wsl = Path("/mnt/c/Users/User/video-podcast-maker/poc-project/src/remotion/public")
    public_wsl.mkdir(parents=True, exist_ok=True)
    required = [
        "timing.json",
        "scene-plan.json",
        "podcast_audio.wav",
        "podcast_audio.srt",
        "subtitles.json",
    ]
    for name in required:
        source = root / name
        if not source.is_file():
            raise WorkerFailure(f"render input is missing: {name}")
        shutil.copy2(source, windows_video / name)
        shutil.copy2(source, public_wsl / name)
    primary_visual = root / "assets/primary_visual.png"
    if primary_visual.is_file():
        assets_dir = public_wsl / "assets"
        assets_dir.mkdir(exist_ok=True)
        shutil.copy2(primary_visual, assets_dir / primary_visual.name)

    command = (
        "cd /d C:\\Users\\User\\video-podcast-maker\\poc-project && "
        "npx remotion render src\\remotion\\index.ts BrandedPodcastVideo "
        f"{output_win} --props-file={public_win}\\timing.json "
        f"--public-dir={public_win} --concurrency=8 --video-bitrate=10M"
    )
    run([str(cmd), "/C", command], timeout=3600)
    if not output_wsl.is_file() or output_wsl.stat().st_size < 1024 * 1024:
        raise WorkerFailure("Windows render did not produce a valid MP4")
    destination = root / "branded-output.mp4"
    shutil.copy2(output_wsl, destination)
    return outputs_for(
        root,
        ["branded-output.mp4", "timing.json", "scene-plan.json"],
        render_platform="windows-native",
    )


def stage_package(request: Mapping[str, Any], root: Path, project_root: Path) -> dict[str, Any]:
    del request, project_root
    source = root / "branded-output.mp4"
    if not source.is_file():
        raise WorkerFailure("branded-output.mp4 is required before package")
    destination = root / "final-video.mp4"
    run(
        ["ffmpeg", "-y", "-i", str(source), "-c", "copy", str(destination)],
        timeout=900,
    )
    if ffprobe_duration(destination) <= 0:
        raise WorkerFailure("packaged video duration is invalid")
    return outputs_for(
        root,
        ["branded-output.mp4", "final-video.mp4"],
        packaged=True,
    )


def blocker_count_from_json(path: Path) -> int:
    if not path.is_file():
        return 0
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 0
    if isinstance(value, dict):
        for key in ("blocker_count", "blockers"):
            item = value.get(key)
            if isinstance(item, int):
                return item
            if isinstance(item, list):
                return len(item)
    return 0


def visual_publishable_from_json(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if not isinstance(value, dict):
        return False
    for key in ("visual_publishable", "publishable", "passed"):
        if key in value:
            return bool(value[key])
    return False


def stage_qa(request: Mapping[str, Any], root: Path, project_root: Path) -> dict[str, Any]:
    del request
    verify = tool(
        project_root,
        "scripts/verify.sh",
        "skills/video-podcast-maker/scripts/verify_output.py",
    )
    if verify.suffix == ".sh":
        run(["bash", str(verify), str(root)], cwd=project_root, timeout=1200)
    else:
        run(
            [sys.executable, str(verify), str(root), "--strict", "--no-fix"],
            cwd=project_root,
            timeout=1200,
        )
    visual_path = root / "qa/visual-publishability.json"
    audit_path = root / "qa/audit-report.json"
    visual_publishable = visual_publishable_from_json(visual_path)
    blockers = blocker_count_from_json(audit_path)
    if not visual_publishable:
        raise WorkerFailure("QA passed command but visual_publishable is not true")
    if blockers:
        raise WorkerFailure(f"QA contains {blockers} blocker(s)")
    names = [
        "final-video.mp4",
        "branded-output.mp4",
        "qa/audit-report.json",
        "qa/render-checkpoints.json",
        "qa/visual-publishability.json",
        "qa/qa_report.html",
    ]
    return outputs_for(
        root,
        names,
        visual_publishable=True,
        blocker_count=0,
    )


HANDLERS: dict[str, Callable[[Mapping[str, Any], Path, Path], dict[str, Any]]] = {
    "tts": stage_tts,
    "scene_plan": stage_scene_plan,
    "image_gen": stage_image_gen,
    "render": stage_render,
    "package": stage_package,
    "qa": stage_qa,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hermes video Worker adapter")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--capabilities", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = Path(args.project_root).expanduser().resolve()
    if args.capabilities:
        print(
            json.dumps(
                {
                    "stages": sorted(STAGES),
                    "local_only": True,
                    "publication": False,
                    "tts": "windows-system-speech-local",
                    "image_gen": "comfyui-bridge-local",
                    "render": "windows-native-remotion",
                },
                sort_keys=True,
            )
        )
        return 0
    try:
        request = read_request()
        root = allowed_artifact_root(request)
        outputs = HANDLERS[str(request["stage"])](request, root, project_root)
        return emit("succeeded", outputs=outputs)
    except NeedsHuman as exc:
        return emit("needs_human", error=str(exc))
    except (WorkerFailure, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return emit("failed", error=str(exc))
    except Exception as exc:
        return emit("failed", error=f"worker_exception: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
