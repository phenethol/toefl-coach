"""Pronunciation and delivery signals for a Speaking answer. An extra signal for practice: it never changes a score.

Usage:
  pronunciation.py <audio> --text "Expected sentence."         Listen and Repeat: compare with the sentence
  pronunciation.py <audio> --transcript <transcribe.json>      Interview: compare with Whisper's words
  pronunciation.py --split <dir> --section <section.json>      a split full section: lr1..7.wav, iv1..4.wav (+ iv*.json)
  add --json <out.json> to save every number.

Pronunciation: a local wav2vec2 phoneme recognizer (facebook/wav2vec2-lv-60-espeak-cv-ft, about 1.2 GB) hears which
sounds were said; they are aligned with the expected US pronunciation from misaki. Only sound patterns common for many
learners are reported (th, æ, ʌ, ɪ/i, ʊ/u, w/v, h, final devoicing, ng), because an accent is not an error and the
recognizer also mishears native speech.
Read the counts against the baseline in references/pronunciation-signals.md (ETS recordings), not as absolutes.
Delivery: Praat (parselmouth) pitch range, articulation rate, mean length of run and pauses inside phrases.
"""
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _env import use_local_model_cache  # noqa: E402

MODEL = "facebook/wav2vec2-lv-60-espeak-cv-ft"
SR = 16000
FRAME = 0.02  # wav2vec2 output step in seconds

VOWELS = set("iɪɛæɑɔʊuʌəɜAIOWY")
VOICED_PAIRS = {"b": "p", "d": "t", "ɡ": "k", "v": "f", "ʒ": "ʃ", "ʤ": "ʧ"}  # not z: natives devoice plural -s too
# Recognizer (espeak IPA) and misaki symbols, reduced to one inventory. A I O W Y are misaki's diphthongs, T its flap.
PAIRS = (("eɪ", "A"), ("aɪ", "I"), ("oʊ", "O"), ("əʊ", "O"), ("aʊ", "W"), ("ɔɪ", "Y"), ("dʒ", "ʤ"), ("tʃ", "ʧ"))
SINGLE = {"ɚ": "əɹ", "ɝ": "ɜɹ", "ᵻ": "ɪ", "ᵊ": "ə", "ɐ": "ə", "ɒ": "ɑ", "a": "ɑ", "e": "ɛ", "o": "O", "ɾ": "T",
          "ʔ": "t", "ɫ": "l", "r": "ɹ", "g": "ɡ", "ɬ": "l"}


def canon(seq):
    """Phoneme string (any delimiter) -> list of symbols in the shared inventory."""
    s = unicodedata.normalize("NFD", seq.replace("ᵊ", "ə"))
    s = "".join(c for c in s if unicodedata.category(c) in ("Ll", "Lu", "Lo"))  # drops stress and length marks
    for k, v in PAIRS:
        s = s.replace(k, v)
    out = []
    for c in s:
        out += list(SINGLE.get(c, c))
    return out


def load_audio(path):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).copy()


class Recognizer:
    def __init__(self):
        use_local_model_cache()
        import torch
        from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC, Wav2Vec2PhonemeCTCTokenizer
        self.torch = torch
        self.fe = Wav2Vec2FeatureExtractor.from_pretrained(MODEL)
        self.tok = Wav2Vec2PhonemeCTCTokenizer.from_pretrained(MODEL, do_phonemize=False)
        self.model = Wav2Vec2ForCTC.from_pretrained(MODEL).eval()
        self.vocab = {v: k for k, v in self.tok.get_vocab().items()}
        self.blank = self.tok.pad_token_id

    def __call__(self, audio):
        """Recognized phonemes as [(symbol, time_s)], CTC-collapsed."""
        inp = self.fe(audio, sampling_rate=SR, return_tensors="pt")
        with self.torch.no_grad():
            ids = self.model(inp.input_values).logits.argmax(-1)[0].tolist()
        out, prev = [], None
        for f, i in enumerate(ids):
            if i != prev and i != self.blank:
                tok = self.vocab.get(i, "")
                if tok and not tok.startswith("<"):
                    out += [(p, f * FRAME) for p in canon(tok)]
            prev = i
        return out


def expected(text):
    """Expected pronunciation: [(word, [phonemes])] from misaki (US)."""
    from misaki import en
    g2p = expected.g2p = getattr(expected, "g2p", None) or en.G2P(trf=False, british=False, fallback=None)
    _, tokens = g2p(text)
    return [(t.text, canon(t.phonemes or "")) for t in tokens if t.phonemes and re.search(r"\w", t.text)]


# Differences that native US speech shows too (measured on the Guide's ETS recordings): reduced vowels, tour/tore.
SAME = {frozenset("əɪ"), frozenset("əʌ"), frozenset("ʊɔ"), frozenset("ɔɑ"), frozenset("ɔO")}


def cost(a, b):
    if a == b or (a == "T" and b in "tdT") or (b == "T" and a in "td") or frozenset((a, b)) in SAME:
        return 0.0
    if (a in VOWELS) == (b in VOWELS):
        return 0.7
    return 1.3


def align(exp, rec):
    """Needleman-Wunsch: list of (expected symbol or None, recognized symbol or None, word index or None)."""
    flat = [(p, w) for w, (_, ps) in enumerate(exp) for p in ps]
    n, m = len(flat), len(rec)
    d = np.zeros((n + 1, m + 1))
    d[:, 0], d[0, :] = np.arange(n + 1), np.arange(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i, j] = min(d[i - 1, j - 1] + cost(flat[i - 1][0], rec[j - 1][0]), d[i - 1, j] + 1, d[i, j - 1] + 1)
    i, j, path = n, m, []
    while i or j:
        if i and j and d[i, j] == d[i - 1, j - 1] + cost(flat[i - 1][0], rec[j - 1][0]):
            path.append((flat[i - 1][0], rec[j - 1][0], flat[i - 1][1])); i, j = i - 1, j - 1
        elif i and d[i, j] == d[i - 1, j] + 1:
            path.append((flat[i - 1][0], None, flat[i - 1][1])); i -= 1
        else:
            path.append((None, rec[j - 1][0], flat[i - 1][1] if i else None)); j -= 1
    return path[::-1]


def patterns(path, exp):
    """Sound patterns common for many learners of English: {pattern: [words]}."""
    found = {}

    def add(name, w):
        found.setdefault(name, []).append(exp[w][0] if w is not None else "?")

    last = {}
    for k, (e, r, w) in enumerate(path):
        if e is not None:
            last[w] = k
    for k, (e, r, w) in enumerate(path):
        if e == "θ" and r in ("t", "s", "f"):
            add(f"th /θ/ -> {r}", w)
        elif e == "ð" and r in ("d", "t", "z", "v"):
            add(f"th /ð/ -> {r}", w)
        elif e == "æ" and r == "ɛ":
            add("/æ/ -> e (bad = bed)", w)
        elif e == "ʌ" and r in ("ɑ", "O", "æ"):
            add("/ʌ/ -> a or o (buddy, but, cup)", w)
        elif (e, r) in (("ɪ", "i"), ("i", "ɪ")):
            add("/ɪ/ vs /i/ (ship = sheep)", w)
        elif (e, r) in (("ʊ", "u"), ("u", "ʊ")):
            add("/ʊ/ vs /u/ (full = fool)", w)
        elif e == "w" and r == "v":
            add("w -> v", w)
        elif e == "h" and r in ("x", None):
            add("h -> x or dropped", w)
        elif e in VOICED_PAIRS and r == VOICED_PAIRS[e] and last.get(w) == k:
            add("final b/d/g/v -> p/t/k/f (bad = bat)", w)
        elif e is None and r == "ɡ" and k and path[k - 1][1] == "ŋ":
            add("ng -> ng-g (sing = sing-g)", w)
    return found


def unclear_words(path, exp):
    """Words of 3+ sounds where at least half the expected sounds were not recognized as such."""
    stats = {}
    for e, r, w in path:
        if e is not None:
            ok, tot = stats.get(w, (0, 0))
            stats[w] = (ok + (cost(e, r) == 0 if r else 0), tot + 1)
    return [exp[w][0] for w, (ok, tot) in sorted(stats.items()) if tot >= 3 and ok / tot < 0.5]


def delivery(audio, words):
    """Praat measures. `words` is [(text, start, end, syllables)]; start/end are None without word timings."""
    import parselmouth
    snd = parselmouth.Sound(audio.astype(np.float64), SR)
    pitch = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=500)
    f0 = pitch.selected_array["frequency"]
    f0 = f0[f0 > 0]
    res = {}
    if len(f0) > 20:
        st = 12 * np.log2(f0 / np.median(f0))
        res["pitch_range_st"] = round(float(np.percentile(st, 90) - np.percentile(st, 10)), 1)
    inten = snd.to_intensity(time_step=0.01)
    db = inten.values[0]
    times = np.array([inten.get_time_from_frame_number(i + 1) for i in range(len(db))])
    voiced = db > db.max() - 25
    if not voiced.any():
        return res
    start, end = times[voiced][0], times[voiced][-1]
    pauses, run_start, sil_start = [], None, None
    for t, v in zip(times, voiced):
        if start <= t <= end and not v:
            sil_start = t if sil_start is None else sil_start
        elif sil_start is not None:
            if t - sil_start >= 0.25:
                pauses.append((round(sil_start, 2), round(t - sil_start, 2)))
            sil_start = None
    phonation = (end - start) - sum(p[1] for p in pauses)
    res.update(speech_s=round(end - start, 1), pauses_025=len(pauses))
    if words:
        syl = sum(w[3] for w in words)
        res["articulation_rate_syl_s"] = round(syl / phonation, 2) if phonation > 0 else None
        res["mean_length_of_run_syl"] = round(syl / (len(pauses) + 1), 1)
        inside = {}  # (word before, word after) -> longest pause; Whisper's word times are rough, so merge duplicates
        for p_start, p_len in pauses if words[0][1] is not None else []:
            if p_len < 0.4:
                continue
            b = max((i for i, w in enumerate(words) if w[2] <= p_start + 0.15), default=None)
            if b is None or b + 1 >= len(words) or re.search(r"[.,?!;:]$", words[b][0].strip()):
                continue
            inside[b] = max(inside.get(b, 0), p_len)
        res["pauses_inside_phrases"] = [f"{words[b][0].strip()} (…{s:.1f} s) {words[b + 1][0].strip()}"
                                        for b, s in sorted(inside.items())]
    return res


def syllables(word_phonemes):
    return max(1, sum(p in VOWELS for p in word_phonemes))


def analyze(rec, audio_path, text=None, transcript=None):
    audio = load_audio(audio_path)
    if transcript:
        data = json.loads(Path(transcript).read_text())
        text = data.get("text", "")
        wt = [(w["word"], w["start"], w["end"]) for w in data.get("words", [])]
    else:
        wt = None
    exp = expected(text)
    heard = rec(audio)
    path = align(exp, heard)
    n_exp = sum(len(p) for _, p in exp)
    matched = sum(1 for e, r, _ in path if e is not None and r is not None and cost(e, r) == 0)
    if wt:
        words = [(w, s, e, syllables(expected(w)[0][1]) if expected(w) else 1) for w, s, e in wt]
    else:  # no word timings: rates only, no pause locations
        words = [(w, None, None, syllables(p)) for w, p in exp]
    deliv = delivery(audio, words)
    return {"audio": str(audio_path), "text": text, "sound_match": round(matched / n_exp, 3) if n_exp else None,
            "patterns": patterns(path, exp), "unclear_words": unclear_words(path, exp), "delivery": deliv}


def show(name, r):
    d = r["delivery"]
    print(f"## {name}  sound match {r['sound_match']:.0%}" + (f" | pitch range {d['pitch_range_st']} st" if "pitch_range_st" in d else "")
          + (f" | articulation {d['articulation_rate_syl_s']} syl/s" if d.get("articulation_rate_syl_s") else "")
          + (f" | run {d['mean_length_of_run_syl']} syl" if "mean_length_of_run_syl" in d else ""))
    for p, ws in sorted(r["patterns"].items(), key=lambda kv: -len(kv[1])):
        print(f"  {p}: {len(ws)}x  ({', '.join(ws[:6])})")
    if r["unclear_words"]:
        print(f"  hard to recognize: {', '.join(r['unclear_words'][:10])}")
    if d.get("pauses_inside_phrases"):
        print(f"  pauses inside phrases: {'; '.join(d['pauses_inside_phrases'][:6])}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("audio", nargs="?")
    ap.add_argument("--text")
    ap.add_argument("--transcript")
    ap.add_argument("--split")
    ap.add_argument("--section")
    ap.add_argument("--json")
    a = ap.parse_args()
    rec = Recognizer()
    results = {}
    if a.split:
        sec = json.loads(Path(a.section).read_text())
        d = Path(a.split)
        for i, s in enumerate(sec["listen_repeat"]["sentences"], 1):
            results[f"lr{i}"] = analyze(rec, d / f"lr{i}.wav", text=s["text"])
        for i in range(1, len(sec["interview"]["questions"]) + 1):
            if (d / f"iv{i}.json").exists():
                results[f"iv{i}"] = analyze(rec, d / f"iv{i}.wav", transcript=d / f"iv{i}.json")
    else:
        results[Path(a.audio).stem] = analyze(rec, a.audio, text=a.text, transcript=a.transcript)
    for name, r in results.items():
        show(name, r)
    if len(results) > 1:
        total = {}
        for r in results.values():
            for p, ws in r["patterns"].items():
                total.setdefault(p, []).extend(ws)
        print("## all items: " + ("; ".join(f"{p} {len(ws)}x" for p, ws in sorted(total.items(), key=lambda kv: -len(kv[1])))
                                  or "no recurring patterns"))
    if a.json:
        Path(a.json).write_text(json.dumps(results, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
