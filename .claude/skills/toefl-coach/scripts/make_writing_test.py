"""Build an interactive Writing practice test (one self-contained HTML page) in the 2026 TOEFL format.

Usage: make_writing_test.py <test.json> <out_dir>

The page runs the three Writing tasks in the ETS order, each with its own timer, as in the Updated TOEFL iBT Test
Overview: Build a Sentence (10 items, ~6 min), Write an Email (7 min), Write for an Academic Discussion (10 min).
The response boxes have spellcheck and autocorrect off. Answers are saved in the browser while the learner works,
so a reload does not lose them. At the end the page scores Build a Sentence against the key and shows a result
block (all answers and both texts) to paste back for grading.

test.json:
  "id", "title", "source" (optional)
  "bas": {"minutes": 6, "items": [{"context", "parts", "chunks", "key"}]}
      parts: the response frame, fixed text as strings and each blank as null, e.g. ["I", null, "the event", null, "."]
      chunks: the word boxes on screen (may include a distractor); key: the chunks in blank order
      (optional "keys": a list of accepted orders when more than one is natural)
  "email": {"minutes": 7, "scenario", "instruction", "bullets"[3], "closing", "to", "subject"}
  "discussion": {"minutes": 10, "intro", "professor": {"name", "text"}, "students": [{"name", "text"} x 2]}
Any of the three tasks may be left out for a shorter set.
Writes <out_dir>/index.html with the test data embedded base64-encoded, so the key is not readable at a glance.
"""
import base64
import json
import sys
from pathlib import Path


def validate(test):
    for n, item in enumerate(test.get("bas", {}).get("items", []), 1):
        blanks = item["parts"].count(None)
        for key in item.get("keys", [item["key"]]):
            if len(key) != blanks or any(c not in item["chunks"] for c in key):
                raise SystemExit(f"Build a Sentence {n}: the key does not fit {blanks} blanks and the chunks")
    if "email" in test and len(test["email"]["bullets"]) != 3:
        raise SystemExit("email: ETS emails have three bullet points")
    if "discussion" in test and len(test["discussion"]["students"]) != 2:
        raise SystemExit("discussion: ETS discussions have two student posts")


def main(src, out_dir):
    test = json.loads(Path(src).read_text())
    validate(test)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    encoded = base64.b64encode(json.dumps(test, ensure_ascii=False).encode()).decode()
    template = (Path(__file__).resolve().parent / "writing_test_template.html").read_text()
    (out / "index.html").write_text(template.replace("__DATA__", encoded).replace("__TITLE__", test["title"]))
    tasks = [k for k in ("bas", "email", "discussion") if k in test]
    print(f"wrote {out / 'index.html'} ({', '.join(tasks)})")


if __name__ == "__main__":
    main(*sys.argv[1:3])
