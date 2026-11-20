#!/bin/bash
# Creates <repo>/.venv with the speech tools used by toefl-coach.
# Usage: bash .claude/skills/toefl-coach/scripts/setup_env.sh   (run from the repo root)
# Apple Silicon: mlx-whisper + mlx-audio (Kokoro). Other systems: faster-whisper + kokoro (PyTorch).
# Needs uv (https://docs.astral.sh/uv/) and ffmpeg. On Windows, run it inside WSL.
set -euo pipefail

root="$(pwd)"
command -v uv >/dev/null || { echo "uv is missing: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
command -v ffmpeg >/dev/null || echo "WARNING: ffmpeg is missing (brew install ffmpeg / apt install ffmpeg)"

uv venv -q --python 3.12 "$root/.venv"
py="$root/.venv/bin/python"
if [ "$(uname -s)" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]; then
  uv pip install -q --python "$py" mlx-whisper mlx-audio "misaki[en]" pillow numpy pymupdf torch transformers praat-parselmouth
else
  uv pip install -q --python "$py" faster-whisper kokoro soundfile pillow numpy pymupdf torch transformers praat-parselmouth
fi
mkdir -p "$root/.cache/hf"
echo "ready: $py (models download to $root/.cache/hf on first use, about 3 GB with the phoneme model)"
