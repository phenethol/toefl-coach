"""Text-to-speech for practice audio.

Usage: tts.py <voice> <out.wav> <text> [<out.wav> <text> ...]
voice: a Kokoro voice (af_heart = default female US, af_bella, am_michael, bm_george, ...)
       or "say:<macOS voice>" (e.g. say:Samantha) for the built-in macOS voice.
Kokoro runs through mlx-audio on Apple Silicon and through the kokoro package elsewhere.
Always check the result with transcribe.py: out-of-dictionary words can be skipped silently.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _env import ffmpeg, use_local_model_cache, write_wav  # noqa: E402


class _NoEspeak:
    # mlx-audio's bundled espeak-ng aborts the process on macOS ("Error processing file .../phontab").
    # It is only a fallback for out-of-dictionary words, so disable it.
    @staticmethod
    def EspeakFallback(**_):
        raise RuntimeError("espeak fallback disabled")


def _kokoro(voice, speed):
    use_local_model_cache()
    try:
        import mlx_audio.tts.models.kokoro.pipeline as kokoro_pipeline
        from mlx_audio.tts.utils import load_model
    except ImportError:
        kokoro_pipeline = None

    if kokoro_pipeline:
        kokoro_pipeline._get_misaki_espeak = lambda: _NoEspeak
        model = load_model("mlx-community/Kokoro-82M-bf16")
        return lambda text: [np.array(r.audio) for r in model.generate(text=text, voice=voice, speed=speed, lang_code=voice[0])]

    from kokoro import KPipeline

    pipe = KPipeline(lang_code=voice[0])
    return lambda text: [a.numpy() if hasattr(a, "numpy") else np.asarray(a) for _, _, a in pipe(text, voice=voice, speed=speed)]


def synthesize(voice, pairs, speed=1.0):
    """pairs: [(out_wav_path, text), ...]"""
    if voice.startswith("say:"):
        with tempfile.TemporaryDirectory() as tmp:
            for out, text in pairs:
                aiff = str(Path(tmp) / "x.aiff")
                subprocess.run(["say", "-v", voice[4:], "-r", "165", "-o", aiff, text], check=True)
                ffmpeg("-i", aiff, "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(out))
        return
    generate = _kokoro(voice, speed)
    for out, text in pairs:
        write_wav(out, np.concatenate(generate(text)), 24000)


if __name__ == "__main__":
    args = sys.argv[1:]
    synthesize(args[0], list(zip(args[1::2], args[2::2])))
    print("done")
