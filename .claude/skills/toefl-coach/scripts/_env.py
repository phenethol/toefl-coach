"""Shared helpers for the toefl-coach scripts."""
import os
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np


def repo_root() -> Path:
    """The TOEFL log folder: $TOEFL_HOME, else the nearest parent of the cwd that holds speaking/ or the skill."""
    if os.environ.get("TOEFL_HOME"):
        return Path(os.environ["TOEFL_HOME"]).expanduser()
    here = Path.cwd().resolve()
    for p in (here, *here.parents):
        if (p / "speaking").is_dir() or (p / ".claude" / "skills" / "toefl-coach").is_dir():
            return p
    return here


def use_local_model_cache():
    """Keep downloaded models in <repo>/.cache/hf (git-ignored) unless HF_HOME is already set."""
    os.environ.setdefault("HF_HOME", str(repo_root() / ".cache" / "hf"))
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")


def ffmpeg(*args, capture=False):
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg is required: brew install ffmpeg / apt install ffmpeg / winget install ffmpeg")
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-y", *args]
    if capture:
        return subprocess.run(cmd, capture_output=True, text=True).stderr
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def wav_seconds(path) -> float:
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def write_wav(path, samples, rate):
    pcm = (np.clip(np.asarray(samples, dtype=np.float32), -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
