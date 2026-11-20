"""Cut a recording of the full Speaking section video into one clip per answer.

Usage: split_section.py <recording> <section.json> <out_dir>

The learner plays the section video (make_speaking_section.py) and records with a phone, so the recording
contains the 880 Hz start beeps. Each answer window starts right after a start beep and lasts 8, 10 or 12 s
(Listen and Repeat: sentences 1-2, 3-5, 6-7) or 45 s (Take an Interview). Writes lr1..lr7.wav and iv1..iv4.wav and
prints the expected text of each Listen and Repeat sentence next to its clip.
"""
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _env import ffmpeg  # noqa: E402
from make_speaking_section import INTERVIEW_SECS, lr_seconds  # noqa: E402

RATE = 16000
FRAME = 0.02


def load(path):
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "r.wav"
        ffmpeg("-i", str(path), "-ac", "1", "-ar", str(RATE), "-c:a", "pcm_s16le", str(wav))
        with wave.open(str(wav)) as w:
            return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def beep_starts(x, freq=880.0, min_len=0.2):
    """Times where a pure tone at `freq` dominates for at least `min_len` seconds."""
    n = int(RATE * FRAME)
    frames = x[: len(x) // n * n].reshape(-1, n) * np.hanning(n)
    spec = np.abs(np.fft.rfft(frames, axis=1))
    freqs = np.fft.rfftfreq(n, 1 / RATE)
    band = (freqs > freq - 60) & (freqs < freq + 60)
    ratio = spec[:, band].sum(axis=1) / (spec.sum(axis=1) + 1e-9)
    on = ratio > 0.35
    starts, run = [], 0
    for i, flag in enumerate(on):
        run = run + 1 if flag else 0
        if run == int(min_len / FRAME):
            starts.append((i - run + 1) * FRAME)
    return starts


def main(recording, section_path, out_dir):
    section = json.loads(Path(section_path).read_text())
    parts = section.get("listen_repeat_parts") or [section["listen_repeat"]]
    windows = []
    for p_i, lr in enumerate(parts):     # a drill with several parts names its clips p1_lr1 … p2_lr7
        tag = f"p{p_i + 1}_" if len(parts) > 1 else ""
        windows += [(f"{tag}lr{i + 1}", lr_seconds(i), s["text"]) for i, s in enumerate(lr["sentences"])]
    windows += [(f"iv{i + 1}", INTERVIEW_SECS, q) for i, q in enumerate(section.get("interview", {}).get("questions", []))]
    x = load(recording)
    beeps = beep_starts(x)
    print(f"found {len(beeps)} start beeps (expected {len(windows)}) at: {', '.join(f'{b:.1f}' for b in beeps)}")
    if len(beeps) != len(windows):
        print("Beep count does not match. Check the recording (was the whole video recorded?) and cut by hand if needed.")
        if len(beeps) < len(windows):
            windows = windows[len(windows) - len(beeps):] if beeps and beeps[0] > 60 else windows[: len(beeps)]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for (name, secs, text), start in zip(windows, beeps):
        begin = start + 0.35
        clip = out / f"{name}.wav"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{begin:.2f}", "-t", str(secs),
                        "-i", str(recording), "-ac", "1", "-ar", "16000", str(clip)], check=True)
        label = f"  | {text}" if name.startswith("lr") else ""
        print(f"{name}: {begin:6.1f}-{begin + secs:6.1f} s -> {clip.name}{label}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
