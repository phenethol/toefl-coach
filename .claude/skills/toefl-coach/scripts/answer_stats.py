"""Split a transcribed recording into answers and measure each one.

Usage: answer_stats.py <audio> <transcript.json> [--questions set.txt] [--answer-secs 45]

--questions  a set file (line 1 = intro, one question per line, optional "OUTRO: ..." line). Use it when the
             recording contains the interviewer's voice (practice video): each answer is the speech between
             the end of its question and the start of the next one. The recording may start mid-question.
Without --questions the whole recording is one answer.

Per answer it prints: time span, words, fillers, words per minute, silent pauses (ffmpeg silencedetect,
because Whisper's word timings swallow silence), words stretched over 1 s (usually a hidden "uhh"),
and, with --questions, how far the answer ran past the 45 s window of the practice audio.
"""
import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _env import ffmpeg  # noqa: E402

FILLERS = {"uh", "um", "umm", "uhh", "uhm", "hmm", "er", "erm", "ah", "mm"}
# make_practice_set.py plays 0.6 s of silence and a 0.35 s beep between the question and the answer window.
QUESTION_TO_WINDOW = 0.95
TAIL_TOKENS = 8


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def silences(audio):
    log = ffmpeg("-i", audio, "-af", "silencedetect=noise=-35dB:d=0.35", "-f", "null", "-", capture=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
    return list(zip(starts, ends))


def find_phrase(flat, phrase_tokens, start, from_end=True):
    """Best fuzzy match of the phrase's last (or first) TAIL_TOKENS tokens in flat[start:]. Returns (i, j) or None."""
    probe = phrase_tokens[-TAIL_TOKENS:] if from_end else phrase_tokens[:TAIL_TOKENS]
    best, best_at = 0.0, None
    for i in range(start, len(flat) - len(probe) + 1):
        ratio = SequenceMatcher(None, [t for _, t in flat[i:i + len(probe)]], probe).ratio()
        if ratio > best:
            best, best_at = ratio, i
    if best_at is None or best < 0.7:
        return None
    return best_at, best_at + len(probe) - 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("transcript")
    ap.add_argument("--questions")
    ap.add_argument("--answer-secs", type=float, default=45.0)
    args = ap.parse_args()

    words = json.load(open(args.transcript))["words"]
    flat = [(i, t) for i, w in enumerate(words) for t in tokens(w["word"])]

    answers = []  # (label, first_word_index, last_word_index, question_end_time or None)
    if args.questions:
        lines = [l.strip() for l in open(args.questions) if l.strip()]
        questions = [l for l in lines[1:] if not l.startswith("OUTRO:")]
        outro = next((l[6:].strip() for l in lines if l.startswith("OUTRO:")), None)
        found, pos = [], 0
        for n, q in enumerate(questions, 1):
            hit = find_phrase(flat, tokens(q), pos)
            if hit:
                found.append((n, q, hit))
                pos = hit[1] + 1
        for k, (n, q, (_, end_tok)) in enumerate(found):
            first = flat[end_tok][0] + 1
            if k + 1 < len(found):
                nxt = found[k + 1]
                stop_tok = max(end_tok + 1, nxt[2][1] - len(tokens(nxt[1])) + 1)
            else:
                out = find_phrase(flat, tokens(outro), end_tok + 1, from_end=False) if outro else None
                stop_tok = out[0] if out else len(flat)
            last = flat[stop_tok - 1][0] if stop_tok <= len(flat) and stop_tok > end_tok + 1 else first - 1
            answers.append((f"Q{n}: {q}", first, last, words[flat[end_tok][0]]["end"]))
        missing = [n for n in range(1, len(questions) + 1) if n not in {f[0] for f in found}]
        if missing:
            print(f"(questions not heard in this recording: {missing})\n")
    else:
        answers.append(("whole recording", 0, len(words) - 1, None))

    gaps = silences(args.audio)
    for label, a, b, q_end in answers:
        ans = words[a:b + 1]
        if not ans:
            print(f"## {label}\n(no answer found)\n")
            continue
        t0, t1 = ans[0]["start"], ans[-1]["end"]
        dur = max(t1 - t0, 0.01)
        toks = [t for w in ans for t in tokens(w["word"])]
        n_fill = sum(t in FILLERS for t in toks)
        n_words = sum(1 for w in ans if tokens(w["word"]) and not set(tokens(w["word"])) <= FILLERS)
        pauses = [(s, e - s) for s, e in gaps if s >= t0 and e <= t1 and e - s >= 0.5]
        stretched = [(w["start"], w["word"].strip(), w["end"] - w["start"]) for w in ans if w["end"] - w["start"] > 1.0]

        print(f"## {label}")
        line = f"time {t0:.1f}-{t1:.1f} s ({dur:.1f} s) | words {n_words} (+{n_fill} fillers) | {n_words / dur * 60:.0f} wpm"
        if q_end is not None:
            window_end = q_end + QUESTION_TO_WINDOW + args.answer_secs
            over = t1 - window_end
            line += f" | {'OVER TIME by ' + format(over, '.1f') + ' s' if over > 0.3 else 'within time'}"
        print(line)
        print("pauses >=0.5 s: " + (", ".join(f"{s:.1f}s ({d:.2f})" for s, d in pauses) or "none")
              + f" | longest: {max((d for _, d in pauses), default=0):.2f} s")
        print("stretched words >1 s: " + (", ".join(f"{s:.1f}s '{w}' ({d:.1f})" for s, w, d in stretched) or "none"))
        print("text: " + " ".join(w["word"].strip() for w in ans) + "\n")


if __name__ == "__main__":
    main()
