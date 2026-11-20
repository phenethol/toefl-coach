"""Metrics for evaluation/results.json: python3 evaluation/analyze.py

For each model and rule set: items graded inside ETS's range, within one point of it, mean signed error
(negative = harsher than ETS) and mean absolute error, against the range bounds. With two runs: test-retest
exact agreement and quadratic weighted kappa (QWK, the agreement statistic used for automated essay scoring).
"""
import json
from pathlib import Path

data = json.load(open(Path(__file__).with_name("results.json")))
ref = {it["id"]: it["ref"] for it in data["items"]}


def error(i, s):
    lo, hi = ref[i]
    return 0 if lo <= s <= hi else (s - hi if s > hi else s - lo)


def qwk(a, b, n=6):
    ids = sorted(a)
    obs = [[0] * n for _ in range(n)]
    for i in ids:
        obs[a[i]][b[i]] += 1
    rows, cols = [sum(r) for r in obs], [sum(obs[i][j] for i in range(n)) for j in range(n)]
    w = lambda i, j: (i - j) ** 2 / (n - 1) ** 2
    num = sum(w(i, j) * obs[i][j] for i in range(n) for j in range(n))
    den = sum(w(i, j) * rows[i] * cols[j] / len(ids) for i in range(n) for j in range(n))
    return 1 - num / den if den else 1.0


print(f"{'model':7} {'rules':6} {'runs':>4} {'in range':>9} {'within 1':>9} {'bias':>6} {'MAE':>5}  test-retest")
for model in data["models"]:
    for cond in data["conditions"]:
        runs = [v for k, v in data["runs"].items() if k.startswith(f"{model}_{cond}_")]
        if not runs:
            continue
        errs = [[error(i, s) for i, s in r.items()] for r in runs]
        avg = lambda f: sum(f(e) for e in errs) / len(errs)
        line = (f"{model:7} {cond:6} {len(runs):>4} {avg(lambda e: sum(x == 0 for x in e)):>6.1f}/19 "
                f"{avg(lambda e: sum(abs(x) <= 1 for x in e)):>6.1f}/19 {avg(lambda e: sum(e) / len(e)):>+6.2f} {avg(lambda e: sum(map(abs, e)) / len(e)):>5.2f}")
        if len(runs) == 2:
            line += f"  {sum(runs[0][i] == runs[1][i] for i in ref)}/19 exact, QWK {qwk(runs[0], runs[1]):.2f}"
        print(line)
