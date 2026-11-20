#!/usr/bin/env python3
"""Exact text statistics for a TOEFL iBT Email or Academic Discussion response.

Language models miscount words and sentences, and length is a real signal in
both tasks (Academic Discussion asks for 100+ words; the Email instructions say
to write as much as you can in 7 minutes). Run this instead of estimating.

Usage:
    python text_stats.py response.txt [--prompt prompt.txt] [--task email|discussion]
    python text_stats.py - --task email < response.txt

Prints JSON:
    words                   whitespace-separated tokens containing a letter or
                            digit (how on-screen word counters count)
    sentences               sentence-like segments; an email's greeting, closing
                            and signature lines count as their own segments
    mean_sentence_words     words per segment
    longest_sentence_words  the longest segment, in words
    mtld                    lexical diversity (McCarthy & Jarvis 2010). Steadier
                            than type-token ratio on short texts but still noisy
                            around 100 words; compare a writer's attempts with
                            each other rather than against a fixed norm.
                            null under 50 words.
    repeated_words          content words used 4+ times (words that also occur
                            in the prompt are excluded when --prompt is given)
    prompt_overlap          share of the response's distinct content words that
                            also occur in the prompt (with --prompt)
    longest_copied_run      longest word sequence copied verbatim from the
                            prompt (with --prompt)
    flags                   heuristic warnings in plain English
"""

import argparse
import json
import re
import sys
from collections import Counter

STOPWORDS = set(
    """a about above after again against all also am an and any are as at be
    because been before being below between both but by can could did do does
    doing down during each even few for from further had has have having he her
    here hers herself him himself his how i if in into is it its itself just
    let may me might more most must my myself no nor not now of off on once
    only or other our ours ourselves out over own same shall she should so
    some such than that the their theirs them themselves then there these they
    this those through to too under until up us very was we were what when
    where which while who whom whose why will with would you your yours
    yourself yourselves i'm i've i'd i'll you're you've you'd you'll he's
    she's it's we're we've they're they've that's there's what's let's don't
    doesn't didn't can't couldn't won't wouldn't shouldn't isn't aren't
    wasn't weren't hasn't haven't hadn't""".split()
)

# Titles are always followed by a name, so their period never ends a sentence.
TITLE_RE = re.compile(r"\b(?:dr|mr|mrs|ms|prof)\.", re.IGNORECASE)
# Other abbreviations end a sentence only when a capitalised word follows.
ABBR_RE = re.compile(
    r"\b(?:e\.g\.|i\.e\.|etc\.|vs\.|a\.m\.|p\.m\.|u\.s\.|u\.k\.|approx\.)(?=\s*[a-z0-9,(])",
    re.IGNORECASE,
)
DOT_PLACEHOLDER = "\u2024"  # one-dot leader; never appears in real responses


def read_text(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as f:
        return f.read()


def normalize_quotes(text):
    return text.replace("\u2019", "'").replace("\u2018", "'")


def count_words(text):
    return sum(1 for tok in text.split() if re.search(r"[A-Za-z0-9]", tok))


def split_sentences(text):
    def protect(match):
        return match.group(0).replace(".", DOT_PLACEHOLDER)

    protected = ABBR_RE.sub(protect, TITLE_RE.sub(protect, text))
    segments = []
    for line in protected.splitlines():
        line = line.strip()
        if not line:
            continue
        for part in re.split(r"(?<=[.!?])[\"')\]]*\s+", line):
            if re.search(r"[A-Za-z0-9]", part):
                segments.append(part.replace(DOT_PLACEHOLDER, "."))
    return segments


def lexical_tokens(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)?", normalize_quotes(text).lower())


def crude_lemma(word):
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def content_words(tokens):
    return [crude_lemma(t) for t in tokens if t not in STOPWORDS and len(t) > 2]


def _mtld_pass(tokens, threshold=0.72):
    factors = 0.0
    types, count = set(), 0
    for tok in tokens:
        count += 1
        types.add(tok)
        if len(types) / count <= threshold:
            factors += 1
            types, count = set(), 0
    if count:
        factors += (1 - len(types) / count) / (1 - threshold)
    return len(tokens) / factors if factors else None


def mtld(tokens):
    if len(tokens) < 50:
        return None
    forward, backward = _mtld_pass(tokens), _mtld_pass(tokens[::-1])
    if forward is None or backward is None:
        return None
    return round((forward + backward) / 2, 1)


def longest_common_run(a, b):
    """Longest contiguous token sequence shared by lists a and b."""
    best_len, best_end = 0, 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best_len:
                    best_len, best_end = cur[j], i
        prev = cur
    return best_len, a[best_end - best_len:best_end]


def analyse(response, prompt=None, task=None):
    words = count_words(response)
    sentences = split_sentences(response)
    lengths = [count_words(s) for s in sentences]
    tokens = lexical_tokens(response)
    content = content_words(tokens)

    prompt_content = set(content_words(lexical_tokens(prompt))) if prompt else set()
    counts = Counter(w for w in content if w not in prompt_content)
    repeated = [[w, n] for w, n in counts.most_common() if n >= 4]

    result = {
        "words": words,
        "sentences": len(sentences),
        "mean_sentence_words": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "longest_sentence_words": max(lengths) if lengths else 0,
        "mtld": mtld(tokens),
        "repeated_words": repeated,
    }

    flags = []
    if task == "discussion" and words < 100:
        flags.append(
            f"{words} words: below the 100 words the task asks for; "
            "elaboration will likely be judged limited."
        )
    if task == "email" and words < 80:
        flags.append(
            f"{words} words: short for a 7-minute email (the instructions say to "
            "write as much as you can); check that every bullet point is developed."
        )
    if lengths and max(lengths) >= 40:
        flags.append(
            f"Longest sentence is {max(lengths)} words: check for run-ons and comma splices."
        )
    if len(lengths) >= 4 and sum(lengths) / len(lengths) < 10:
        flags.append("Short average sentence length: may read as limited syntactic variety.")
    if repeated:
        listed = ", ".join(f"{w} ({n}x)" for w, n in repeated)
        flags.append(f"Repeated words not taken from the prompt: {listed}.")

    if prompt:
        distinct = set(content)
        overlap = len(distinct & prompt_content) / len(distinct) if distinct else 0.0
        run_len, run = longest_common_run(tokens, lexical_tokens(prompt))
        result["prompt_overlap"] = round(overlap, 2)
        result["longest_copied_run"] = {"words": run_len, "text": " ".join(run)}
        if run_len >= 8:
            flags.append(
                f"{run_len}-word stretch copied verbatim from the prompt: reusing key "
                "terms is fine, but long copied stretches don't count as your own language."
            )
        if distinct and overlap < 0.12:
            flags.append(
                "Little vocabulary shared with the prompt: check the response stays on "
                "the prompt's topic (automated relevance checks lean on this overlap)."
            )

    result["flags"] = flags
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("response", help="file with the response, or - for stdin")
    parser.add_argument("--prompt", help="file with the full task prompt")
    parser.add_argument("--task", choices=["email", "discussion"])
    args = parser.parse_args()

    response = read_text(args.response)
    prompt = read_text(args.prompt) if args.prompt else None
    print(json.dumps(analyse(response, prompt, args.task), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
