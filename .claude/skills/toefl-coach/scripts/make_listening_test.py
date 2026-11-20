"""Build a Listening practice test (audio + a self-scoring HTML page) in the 2026 TOEFL format.

Usage: make_listening_test.py <test.json> <out_dir>

test.json holds "id", "title", "narrator" (Kokoro voice) and "stages": [{"name", "blocks": [...]}]. Block types follow
the ETS Updated TOEFL iBT Test Overview. Optional "speed" (test-level or per block, e.g. 1.05-1.1 for a harder test) sets the speakers' pace; the narrator stays at 1.0.
  choose        {"id", "voice", "prompt", "options"[4], "key"}            prompt is heard only, options are shown
  conversation  {"id", "intro", "turns": [[label, voice, text], ...], "questions": [2 x {"stem", "options", "key"}]}
  announcement  {"id", "intro", "voice", "text" (40-85 words), "questions": [...]}
  talk          {"id", "intro", "voice", "text" (100-250 words), "questions": [4 x ...]}
Optional per stage: "minutes" (a module timer; when it runs out the rest of the stage is skipped). Optional per
question: "unscored", "qtype", "explanation" (shown after the test). Optional test keys: "conversion" ([[raw, band,
CEFR], ...], used instead of the Table 3 approximation), "numbering": "module" (numbers restart in each stage),
"source". With "ets_audio": true every block already has "audio" (and "transcript") and nothing is synthesized
(for official audio you own).
Writes <out_dir>/audio/<id>.m4a and <out_dir>/index.html (test data embedded base64-encoded, so the key and
transcripts are not readable at a glance).

Every spoken line (and every sentence of an announcement or talk) is synthesized and then checked with Whisper
on its own, because Kokoro can silently skip out-of-dictionary words, and Whisper on a whole file can drop
everything after a voice change. Lines that do not match are listed as CHECK; rewrite them and build again.
"""
import base64
import copy
import json
import re
import sys
import tempfile
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _env import ffmpeg  # noqa: E402
from transcribe import transcribe  # noqa: E402
from tts import synthesize  # noqa: E402

RATE = 24000
LEAD_IN, AFTER_NARRATOR, BETWEEN_TURNS, BETWEEN_SENTENCES = 0.3, 0.7, 0.35, 0.25
NUMBER_WORDS = set("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
                   "sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety "
                   "hundred thousand".split())


def tokens(text):
    """Words for comparison; numbers are dropped because Whisper writes them as digits."""
    words = re.findall(r"[a-z']+|\d+", text.lower().replace("’", "'"))
    return [w for w in words if not w.isdigit() and w not in NUMBER_WORDS]


def check(wav, expected):
    heard = tokens(transcribe(str(wav))[0])
    want = tokens(expected)
    sm = SequenceMatcher(a=want, b=heard, autojunk=False)
    diffs = [f"{' '.join(want[a1:a2]) or '∅'} -> {' '.join(heard[b1:b2]) or '∅'}"
             for op, a1, a2, b1, b2 in sm.get_opcodes() if op != "equal"]
    return sm.ratio(), diffs


def read_wav(path):
    import wave

    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


def silence(seconds):
    return np.zeros(int(RATE * seconds), dtype=np.int16)


def segments(block, narrator, speed):
    """The spoken pieces of one block, in order: [(voice, speed, text, pause_after), ...].
    Speakers use the block's "speed" (else the test's); the narrator always speaks at 1.0."""
    speed = block.get("speed", speed)
    if block["type"] == "choose":
        return [(block["voice"], speed, block["prompt"], 0)]
    out = [(narrator, 1.0, block["intro"], AFTER_NARRATOR)]
    if block["type"] == "conversation":
        out += [(voice, speed, text, BETWEEN_TURNS) for _, voice, text in block["turns"]]
    else:
        sentences = re.split(r"(?<=[.!?])\s+", block["text"].strip())
        out += [(block["voice"], speed, s, BETWEEN_SENTENCES) for s in sentences]
    return out


def write_page(test, out):
    encoded = base64.b64encode(json.dumps(test, ensure_ascii=False).encode()).decode()
    template = (Path(__file__).resolve().parent / "listening_test_template.html").read_text()
    (out / "index.html").write_text(template.replace("__DATA__", encoded).replace("__TITLE__", test.get("title", "Listening Practice Test")))


def main(test_path, out_dir):
    test = json.loads(Path(test_path).read_text())
    out = Path(out_dir)
    if test.get("ets_audio"):
        # Recorded audio (e.g. official tracks you own): no synthesis, just the page.
        out.mkdir(parents=True, exist_ok=True)
        write_page(test, out)
        print(f"wrote {out / 'index.html'} with recorded audio")
        return
    (out / "audio").mkdir(parents=True, exist_ok=True)
    blocks = [b for stage in test["stages"] for b in stage["blocks"]]

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        jobs = defaultdict(list)  # (voice, speed) -> [(wav, text)], so each voice's model loads once
        plan = {}
        for b in blocks:
            plan[b["id"]] = []
            for i, (voice, speed, text, pause) in enumerate(segments(b, test["narrator"], test.get("speed", 1.0))):
                wav = tmp / f"{b['id']}_{i}.wav"
                jobs[(voice, speed)].append((wav, text))
                plan[b["id"]].append((wav, pause))
        for (voice, speed), pairs in jobs.items():
            print(f"synthesizing {len(pairs)} lines with {voice} at speed {speed}")
            synthesize(voice, pairs, speed)

        problems = 0
        for (voice, _), pairs in jobs.items():
            for wav, text in pairs:
                ratio, diffs = check(wav, text)
                if diffs:
                    problems += 1
                    print(f"CHECK {wav.stem} ({voice}, {ratio:.2f}): {'; '.join(diffs)}  | {text}")
        print(f"verified {sum(map(len, jobs.values()))} lines, {problems} with differences")

        for b in blocks:
            pcm = [silence(LEAD_IN)]
            for wav, pause in plan[b["id"]]:
                pcm += [read_wav(wav), silence(pause)]
            raw = tmp / f"{b['id']}.pcm"
            np.concatenate(pcm + [silence(0.3)]).tofile(raw)
            ffmpeg("-f", "s16le", "-ar", str(RATE), "-ac", "1", "-i", str(raw),
                   "-c:a", "aac", "-b:a", "64k", str(out / "audio" / f"{b['id']}.m4a"))

    data = copy.deepcopy(test)
    for stage in data["stages"]:
        for b in stage["blocks"]:
            b["audio"] = f"audio/{b['id']}.m4a"
    write_page(data, out)
    print(f"wrote {out / 'index.html'} and {len(blocks)} audio files")


if __name__ == "__main__":
    main(*sys.argv[1:3])
