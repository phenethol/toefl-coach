"""Transcribe a speaking recording with word timings, locally.

Usage: transcribe.py <audio> <out.json>
Uses mlx-whisper (whisper-large-v3-turbo) on Apple Silicon and faster-whisper elsewhere.
Writes {"text", "words": [{word, start, end, probability}]} and prints the text plus a word table.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _env import use_local_model_cache  # noqa: E402

# Nudges Whisper to keep fillers and restarts instead of tidying them away.
FILLER_PROMPT = "Umm, let me think, like, hmm... Okay, so, uh, I usually, I mean, I study at home."


def transcribe(audio):
    use_local_model_cache()
    try:
        import mlx_whisper
    except ImportError:
        mlx_whisper = None

    if mlx_whisper:
        r = mlx_whisper.transcribe(
            audio, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="en",
            word_timestamps=True, condition_on_previous_text=False, initial_prompt=FILLER_PROMPT,
        )
        words = [
            {"word": w["word"], "start": float(w["start"]), "end": float(w["end"]), "probability": float(w["probability"])}
            for seg in r["segments"] for w in seg.get("words", [])
        ]
        return r["text"].strip(), words

    from faster_whisper import WhisperModel

    model = WhisperModel("large-v3-turbo", compute_type="int8")
    segments, _ = model.transcribe(
        audio, language="en", word_timestamps=True, condition_on_previous_text=False, initial_prompt=FILLER_PROMPT,
    )
    texts, words = [], []
    for seg in segments:
        texts.append(seg.text)
        words += [{"word": w.word, "start": w.start, "end": w.end, "probability": w.probability} for w in seg.words]
    return "".join(texts).strip(), words


def main():
    audio, out_path = sys.argv[1], sys.argv[2]
    text, words = transcribe(audio)
    with open(out_path, "w") as f:
        json.dump({"text": text, "words": words}, f, indent=1)

    print(text)
    print("\n--- words (start-end, probability) ---")
    prev_end = None
    for w in words:
        gap = w["start"] - prev_end if prev_end is not None else 0
        flags = (f"  [pause {gap:.2f}s]" if gap >= 0.5 else "") + ("  <-- low confidence" if w["probability"] < 0.6 else "")
        print(f"{w['start']:7.2f}-{w['end']:7.2f}  {w['word'].strip():<18} p={w['probability']:.2f}{flags}")
        prev_end = w["end"]


if __name__ == "__main__":
    main()
