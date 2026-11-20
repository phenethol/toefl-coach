#!/usr/bin/env python3
"""Rough estimate of the TOEFL iBT Writing band (1-6) for the 2026+ test.

NOT an official ETS conversion. ETS does not publish how Build a Sentence,
Write an Email and Academic Discussion scores combine into the section band.
This heuristic chains two published ETS tables:

  1. Legacy (pre-2026) Writing: mean task rubric score (0-5) -> 0-30 score
  2. ETS's 2026 concordance: legacy Writing 0-30 -> new 1-6 band

applied to the mean of the Email and Academic Discussion rubric scores (the
Academic Discussion task and rubric carried over unchanged).

Build a Sentence (10 of the section's 12 items, all-or-nothing) then lowers
the estimate only when it is out of line with the level the extended tasks
show, so weak writers are not penalised twice:

    expected minimum BAS:  band 5+ -> 8,  band 4-4.5 -> 6,  band 3-3.5 -> 4
    shortfall of 1-2 items: -0.5      shortfall of 3+: -1.0

BAS never raises the estimate: ETS's weighting is unknown, and a high BAS is
what every competent writer gets. Read the result as +/- 0.5 band, or +/- 1
when only one extended task is given.

Usage:
    python estimate_band.py --email 4 --discussion 5 --bas 9
    python estimate_band.py --discussion 4
"""

import argparse
import math

# Points of ETS's legacy "mean rubric score -> scaled Writing score" table.
# Values between points are interpolated linearly.
LEGACY_MEAN_TO_SCALED = [
    (0.0, 0), (1.0, 8), (1.25, 10), (1.5, 11), (2.0, 14), (2.25, 15),
    (2.5, 17), (2.75, 18), (3.0, 20), (3.25, 21), (3.5, 22), (4.0, 25),
    (4.25, 27), (4.5, 28), (5.0, 30),
]

# ETS Updated TOEFL iBT Test Overview, Table 3, Writing column: legacy 0-30 -> 1-6 band.
# ETS's rows overlap below band 2 (1.5 = 3-6, 1 = 0-4, 2 = 5-9); the 1.5 row is used for 3-6.
WRITING_SCALED_TO_BAND = {
    30: 6.0, 29: 6.0, 28: 5.5, 27: 5.5, 26: 5.0, 25: 5.0, 24: 5.0, 23: 4.5,
    22: 4.5, 21: 4.5, 20: 4.0, 19: 4.0, 18: 4.0, 17: 4.0, 16: 3.5, 15: 3.5,
    14: 3.0, 13: 3.0, 12: 2.5, 11: 2.5, 10: 2.5, 9: 2.0, 8: 2.0, 7: 2.0,
    6: 1.5, 5: 1.5, 4: 1.5, 3: 1.5, 2: 1.0, 1: 1.0, 0: 1.0,
}

CEFR = {6.0: "C2", 5.5: "C1", 5.0: "C1", 4.5: "B2", 4.0: "B2", 3.5: "B1",
        3.0: "B1", 2.5: "A2", 2.0: "A2", 1.5: "A1", 1.0: "A1"}


def legacy_scaled(mean):
    points = LEGACY_MEAN_TO_SCALED
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= mean <= x1:
            y = y0 + (y1 - y0) * (mean - x0) / (x1 - x0)
            return int(math.floor(y + 0.5))
    raise ValueError(f"mean rubric score out of range: {mean}")


def expected_bas(base_band):
    if base_band >= 5.0:
        return 8
    if base_band >= 4.0:
        return 6
    if base_band >= 3.0:
        return 4
    return 0


def bas_adjustment(bas, base_band):
    if bas is None:
        return 0.0
    shortfall = expected_bas(base_band) - bas
    if shortfall <= 0:
        return 0.0
    if shortfall <= 2:
        return -0.5
    return -1.0


def estimate(email=None, discussion=None, bas=None):
    scores = [s for s in (email, discussion) if s is not None]
    if not scores:
        raise ValueError("need at least one of email / discussion")
    mean = sum(scores) / len(scores)
    scaled = legacy_scaled(mean)
    base = WRITING_SCALED_TO_BAND[scaled]
    adjustment = bas_adjustment(bas, base)
    band = min(6.0, max(1.0, base + adjustment))
    spread = 0.5 if len(scores) == 2 else 1.0
    return {
        "mean_rubric": mean,
        "legacy_scaled": scaled,
        "base_band": base,
        "bas_adjustment": adjustment,
        "bas_expected": expected_bas(base),
        "band": band,
        "cefr": CEFR[band],
        "range": (max(1.0, band - spread), min(6.0, band + spread)),
    }


def main():
    parser = argparse.ArgumentParser(description="Heuristic TOEFL iBT Writing band estimate.")
    parser.add_argument("--email", type=float, help="Write an Email rubric score, 0-5")
    parser.add_argument("--discussion", type=float, help="Academic Discussion rubric score, 0-5")
    parser.add_argument("--bas", type=int, help="Build a Sentence items correct, 0-10")
    args = parser.parse_args()

    if args.email is None and args.discussion is None:
        parser.error("give at least one of --email / --discussion")
    for name, value in (("email", args.email), ("discussion", args.discussion)):
        if value is not None and not 0 <= value <= 5:
            parser.error(f"--{name} must be between 0 and 5")
    if args.bas is not None and not 0 <= args.bas <= 10:
        parser.error("--bas must be between 0 and 10")

    r = estimate(args.email, args.discussion, args.bas)
    lo, hi = r["range"]
    print(f"Mean of extended tasks: {r['mean_rubric']:.2f}/5")
    print(f"Legacy-anchored band:   {r['base_band']} (legacy Writing ~{r['legacy_scaled']}/30)")
    if args.bas is None:
        print("Build a Sentence:       not given, no adjustment")
    else:
        print(f"Build a Sentence:       {args.bas}/10 (expected at least {r['bas_expected']} "
              f"at this level), adjustment {r['bas_adjustment']:+.1f}")
    print(f"ESTIMATE:               {r['band']} ({r['cefr']}), plausible range {lo}-{hi}")
    if args.email is None or args.discussion is None:
        print("Only one extended task given: treat as a wide estimate.")
    print("Heuristic only: ETS does not publish how the tasks combine into the band.")


if __name__ == "__main__":
    main()
