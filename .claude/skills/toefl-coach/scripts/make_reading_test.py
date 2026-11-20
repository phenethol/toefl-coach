"""Build an interactive Reading practice test (one self-contained HTML page) in the 2026 TOEFL format.

Usage: make_reading_test.py <test.json> <out_dir>

The page follows the Official Guide (2026, ch. 2 and the ch. 6 Practice Test): modules with their own timers
(Practice Test: Module 1 ~20 min, Module 2 ~9 min), review and changes allowed inside a module while time remains,
and the three task types:
- Complete the Words: a paragraph of ~70-100 words, first sentence intact, 10 words with the second half missing,
  one box per missing letter
- Read in Daily Life: a short text (15-150 words: email, notice, schedule, social media post), 2-3 questions
- Read an Academic Passage: ~200 words, 5 questions (factual, negative factual, vocabulary, rhetorical purpose,
  inference, insert text, ...); a vocabulary word is highlighted only while its question is shown, and the
  insert-text squares [A]-[D] appear only during an insert-text question
At the end the page scores the scored items, converts the raw score with the test's own conversion table (if any)
and shows a result block to paste back.

test.json:
  "id", "title", "source" (optional), "conversion" (optional: [[raw, band, "CEFR"], ...])
  "modules": [{"name", "minutes", "tasks": [...]}]
    {"type": "ctw", "first": 1, "text": "... Scientists {{bel|ieve}} its ...", "scored": [true x 10]}
    {"type": "daily", "label": "Read an email.", "paragraphs": ["Subject: ...", ...], "questions": [Q]}
    {"type": "academic", "title", "paragraphs": ["... ==feats== ... [A] ..."], "questions": [Q]}
    Q = {"n", "stem", "options"[4], "key": "A"-"D", "scored": true, "qtype", "insert" (insert-text sentence)}
Writes <out_dir>/index.html with the test data embedded base64-encoded, so the key is not readable at a glance.
"""
import base64
import json
import re
import sys
from pathlib import Path


def validate(test):
    for mod in test["modules"]:
        for task in mod["tasks"]:
            if task["type"] == "ctw":
                n = len(re.findall(r"\{\{\w*\|\w+\}\}", task["text"]))
                if n != 10:
                    raise SystemExit(f"{mod['name']}: Complete the Words {task.get('first')} has {n} words, ETS uses 10")
                continue
            if task["type"] not in ("daily", "academic"):
                raise SystemExit(f"unknown task type {task['type']}")
            for q in task["questions"]:
                if len(q["options"]) != 4 or q["key"] not in "ABCD":
                    raise SystemExit(f"{mod['name']}, question {q['n']}: needs 4 options and a key A-D")
                if q["stem"].startswith("There are four locations") and not q.get("insert"):
                    raise SystemExit(f"{mod['name']}, question {q['n']}: insert-text question without the sentence")


def main(src, out_dir):
    test = json.loads(Path(src).read_text())
    validate(test)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    encoded = base64.b64encode(json.dumps(test, ensure_ascii=False).encode()).decode()
    template = (Path(__file__).resolve().parent / "reading_test_template.html").read_text()
    (out / "index.html").write_text(template.replace("__DATA__", encoded).replace("__TITLE__", test["title"]))
    counts = [sum(10 if t["type"] == "ctw" else len(t["questions"]) for t in m["tasks"]) for m in test["modules"]]
    print(f"wrote {out / 'index.html'} ({' + '.join(map(str, counts))} items)")


if __name__ == "__main__":
    main(*sys.argv[1:3])
