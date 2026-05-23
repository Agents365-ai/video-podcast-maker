"""Volcengine Doubao TTS backend."""
import os
import re
import json
import time
import uuid
import base64
import subprocess
from .base import check_resume


def synthesize(chunks, config, output_dir, resume=False):
    """Synthesize using Volcengine Doubao TTS HTTP API.

    Note: Doubao does not support the phoneme system.
    config keys: appid, token, cluster, voice, endpoint, speech_rate
    """
    import requests

    appid = config['appid']
    token = config['token']
    cluster = config.get('cluster', 'volcano_tts')
    voice = config.get('voice', 'BV001_streaming')
    endpoint = config.get('endpoint', 'https://openspeech.bytedance.com/api/v1/tts')
    speech_rate = config.get('speech_rate', '+5%')

    uid = os.environ.get("VOLCENGINE_UID", "video-podcast-maker")
    timeout_sec = int(os.environ.get("VOLCENGINE_TIMEOUT_SEC", "60"))
    sample_rate = int(os.environ.get("VOLCENGINE_SAMPLE_RATE", "48000"))
    part_files = []
    word_boundaries = []
    accumulated_duration = 0

    rate_match = re.match(r'([+-]?\d+)%', speech_rate)
    speed_ratio = 1.0 + int(rate_match.group(1)) / 100.0 if rate_match else 1.0
    speed_ratio = max(0.2, min(3.0, speed_ratio))

    headers = {
        "Authorization": f"Bearer; {token}",
        "Content-Type": "application/json",
    }

    for i, chunk in enumerate(chunks):
        part_file = os.path.join(output_dir, f"part_{i}.wav")
        part_files.append(part_file)

        if resume:
            dur = check_resume(part_file)
            if dur is not None:
                print(f"  ⏭ Part {i + 1}/{len(chunks)} skipped (resume, {dur:.1f}s)")
                accumulated_duration += dur
                continue

        success = False
        for attempt in range(1, 4):
            try:
                req_id = str(uuid.uuid4())
                payload = {
                    "app": {
                        "appid": appid,
                        "token": token,
                        "cluster": cluster,
                    },
                    "user": {"uid": uid},
                    "audio": {
                        "voice_type": voice,
                        "encoding": "wav",
                        "rate": sample_rate,
                        "speed_ratio": speed_ratio,
                        "volume_ratio": 1.0,
                        "pitch_ratio": 1.0,
                    },
                    "request": {
                        "reqid": req_id,
                        "text": chunk,
                        "text_type": "plain",
                        "operation": "query",
                        "with_timestamp": 1,
                    },
                }

                resp = requests.post(endpoint, headers=headers, json=payload, timeout=timeout_sec)
                resp.raise_for_status()
                data = resp.json()

                code = data.get("code")
                if code != 3000:
                    raise RuntimeError(f"Doubao API error code={code}, message={data.get('message')}")

                audio_b64 = data.get("data")
                if not audio_b64:
                    raise RuntimeError("Doubao API returned empty audio data")
                audio_bytes = base64.b64decode(audio_b64)
                with open(part_file, "wb") as f:
                    f.write(audio_bytes)

                normalized_file = part_file + ".norm.wav"
                norm_result = subprocess.run(
                    ["ffmpeg", "-y", "-i", part_file, "-ar", "48000", "-ac", "1", normalized_file],
                    capture_output=True)
                if norm_result.returncode != 0:
                    raise RuntimeError(f"ffmpeg normalization failed: {norm_result.stderr.decode()[:200]}")
                os.replace(normalized_file, part_file)

                probe = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", part_file],
                    capture_output=True, text=True)
                chunk_duration = float(probe.stdout.strip()) if probe.stdout.strip() else 0

                added = data.get("addition", {}) or {}
                frontend = added.get("frontend")
                words = []
                if isinstance(frontend, str) and frontend.strip():
                    try:
                        frontend_obj = json.loads(frontend)
                        words = frontend_obj.get("words", []) or []
                    except json.JSONDecodeError:
                        words = []
                elif isinstance(frontend, dict):
                    words = frontend.get("words", []) or []

                chunk_words = []
                for w in words:
                    text = str(w.get("word", "")).strip()
                    st = float(w.get("start_time", 0))
                    et = float(w.get("end_time", st))
                    if not text:
                        continue
                    chunk_words.append({
                        "text": text,
                        "offset": accumulated_duration + st,
                        "duration": max(0.01, et - st),
                    })

                if not chunk_words and chunk_duration > 0:
                    chars = [c for c in chunk if c.strip()]
                    if chars:
                        per = chunk_duration / len(chars)
                        for idx, ch in enumerate(chars):
                            chunk_words.append({
                                "text": ch,
                                "offset": accumulated_duration + idx * per,
                                "duration": max(0.01, per),
                            })

                word_boundaries.extend(chunk_words)
                print(f"  ✓ Part {i + 1}/{len(chunks)} done ({len(chunk)} chars, {chunk_duration:.1f}s)")
                accumulated_duration += chunk_duration
                success = True
                break
            except Exception as e:
                print(f"  ✗ Part {i + 1} failed (attempt {attempt}/3): {e}")
                if attempt < 3:
                    time.sleep(attempt * 2)

        if not success:
            raise RuntimeError(f"Part {i + 1} synthesis failed")

    return part_files, word_boundaries, accumulated_duration
