# ETS-lens calibration report (2026-10-23/24)

**Why:** to align the **ETS estimate** with ETS's own rating practice in the *Official Guide to the TOEFL iBT Test, Pocket Edition* (2026). Two conditions:
- calibrate blind, with a grader that never sees the official score or comment before giving its own
- keep the **Strict estimate** (the strict lens) unchanged

**Result in one line:**
- **Writing** ETS lens was too strict (ETS's rated-5 samples got 3–4) and is now calibrated.
- **Speaking** ETS lens was already accurate on ETS's top answers; it was re-weighted slightly, so time and wrap-ups count less, and examples and answering every part count more.
- The **strict lens is frozen**, with a guardrail against drift.

## Material
ETS text is not reproduced; items are identified by source.

| ID | Set | Task | Source | Reference level |
|---|---|---|---|---|
| Y7L | A | Interview | Guide ch. 5, track 49 (p. 241) | 5 (stated: "fully successful") |
| H7G | A | Interview | Guide ch. 5, track 50 (pp. 241–242) | 5 (stated) |
| E8N | A | Interview | Guide ch. 5, track 51 (p. 242) | 5 (stated) |
| Q7B | A | Interview | Guide ch. 5, track 52 (p. 243) | 5 (stated) |
| P9R | A | Email | Guide p. 209 (food truck) | 5 (stated) |
| D8F | A | Academic Discussion | Guide p. 218 (boarding schools) | 5 (level-5 wording: "consistent facility") |
| C7T | A | AD fragment | Guide p. 216 (content-free wordiness) | 1–2 (stated) |
| V9U | A | Interview | synthetic control (weak, choppy, 30 words) | 2–3 (from the scoring guide) |
| T9Z | B | Interview | Guide practice test, track 91 (pp. 335–336) | 5 (level-5 wording) |
| Z8K | B | Interview | Guide practice test, track 92 (p. 336) | 5 (level-5 wording) |
| K7Y | B | Interview | Guide practice test, track 93 (pp. 336–337) | 5 (level-5 wording) |
| M8V | B | Interview | Guide practice test, track 94 (p. 337) | 5 (level-5 wording) |
| J7M | B | Email | Guide p. 333 (workshop) | 5 (stated) |
| W7X | B | Academic Discussion | Guide p. 334 (history) | 5 (stated) |
| N9J | B | Email | Overview "Sample High-Level Response" (poetry magazine) | high (4–5) |
| L7H | B | Academic Discussion | Overview "Sample High-Level Response" (volunteering, ~80 words) | high (4–5) |
| G7W | B | AD fragment | Guide p. 216 (memorized "honesty" text) | 1–2 (stated: low) |
| F9C | B | Interview | synthetic control (frequent basic errors, 70 words) | 3–4 (from the scoring guide) |
| R9E | B | Email | synthetic control (one bullet missing, errors pile up) | 2–3 (from the scoring guide) |

The book's speaking samples are audio: tracks 49–52 and 91–94 in the PDF's embedded `Audio_Video Files.zip`. They went through **our own pipeline** (`transcribe.py`, `answer_stats.py`), exactly like the learner's answers. The book has **no rated learner repetitions for Listen and Repeat**, so that task could not be calibrated empirically.

## Procedure (blinding)
1. **Server agent.** It read the book and the Overview, ran the audio and texts through our tools, and wrote two blinded packets with random IDs. The packets contain the prompt, the response, and our transcript and stats only. The official scores and rater comments went into a separate key file. The server added 3 synthetic controls whose expected ranges come from the scoring guides.
2. **Grader agents.** Every round used a fresh agent that read exactly one packet: the rules plus the responses. They read nothing else (verified: 2–3 Read calls on the packet path, plus the agent's own list of files read).
3. **Round 1:** the current rules (v0) on calibration set A. **Baseline:** v0 on held-out set B.
4. **Recalibration (v1).** The main agent compared round 1 with the key and rewrote **only the ETS lens**, from set A and the book's general guidance text. The strict lens was copied verbatim. Set B details were kept out of v1 (checked by searching v1 for every set B item feature).
5. **Validation:** a fresh grader applied v1 to set B. **Refit check:** v1 on set A.
6. **v2:**
   - Set B evidence was added to the rules: the "synthesis counts" clause for Academic Discussion, more examples of rated-5 slips, and the rater's note that a conclusion is "not necessary for a full score".
   - A guardrail was added to the strict lens.
   - v2 is **not independently validated**; no unseen ETS samples are left.

## Results: ETS lens vs ETS's reference levels
| Run | Set | In range | Within ±1 | Mean signed error |
|---|---|---|---|---|
| v0 (old rules) | A, calibration | 6/8 | 7/8 | −0.38 |
| v0 (old rules) | B, held out | 8/11 | 10/11 | −0.36 |
| **v1** | **B, held out** | **10/11** | **11/11** | **−0.09** |
| v1 (refit) | A | 8/8 | 8/8 | 0.00 |
| v2 (final re-check, refit) | A + B | 19/19 | 19/19 | 0.00 |

Per item (ETS lens; reference in brackets):

| ID | Ref | v0 | v1 | Claude v0 | Claude v1 |
|---|---|---|---|---|---|
| Y7L, H7G, E8N, Q7B (Guide interviews) | 5 | 5, 5, 5, 5 | 5, 5, 5, 5 | 4, 4, 4, 4 | 4, 4, 4, 4 |
| T9Z, Z8K, K7Y, M8V (practice-test interviews) | 5 | 5, 5, 5, 5 | 5, 5, 5, 5 | 4, 4, 4, 4 | 5, 4, 4, 4 |
| P9R (email) | 5 | **4** | 5 | 3 | 4 |
| D8F (AD) | 5 | **3** | 5 | 3 | 3 |
| J7M (email) | 5 | **4** | 5 | 3 | 4 |
| W7X (AD) | 5 | **3** | **4** | 3 | 3 |
| N9J (email) | 4–5 | 4 | 5 | 4 | 4 |
| L7H (AD, 80 words) | 4–5 | **3** | 4 | 3 | 3 |
| C7T, G7W (low fragments) | 1–2 | 2, 2 | 1, 2 | 1, 1 | 1, 1 |
| V9U, F9C, R9E (controls) | 2–3, 3–4, 2–3 | 2, 3, 2 | 2, 3, 3 | 1, 2, 2 | 2, 2, 2 |

**What it means:**
- **Speaking:** the old ETS lens already matched ETS on all 8 top answers.
- **Writing:** the old lens under-scored every rated-5 response, by 1 to 2 points. The new lens fixes all but one, the history Academic Discussion, which led to the v2 synthesis clause.
- **Discrimination:** low fragments and controls stayed low. That check rests on synthetic controls and two fragments, because the book has no rated 3s or 4s.

## strict lens stability (must not change)
The Claude rules were copied verbatim. Three independent blind runs measured how well the strict lens repeats:

| Runs compared | Same Claude score |
|---|---|
| v0 vs v1 | 15/19 |
| v0 vs v2 | 15/19 |
| v1 vs v2 | 17/19 |

- Every difference is ±1. On the 14 real ETS-rated responses the Claude mean is 3.64 / 3.86 / 3.79, around 4 by design, while ETS gives them 5.
- **Systematic:** on two emails (P9R, J7M), v0 gave 3 and both later runs gave 4. In v0 the writing Claude score was read as "stricter than the rubric score", which was itself the strict reading, so the deductions were sometimes counted twice. Now the strict reading is the explicit baseline.
- **Noise:** the other differences are on synthetic controls.
- **Guardrail:** v2 adds one: grade the strict lens exactly as before, ignore the ETS tolerances, and give the lower score on a tie. It did not remove the ±1 noise. Treat a Claude score as ±1, like any single human or AI rating.

## What changed in the ETS lens
- **Speaking** (`speaking-grading.md`):
  - Same core: relevance, at least one concrete example or detail, coherence, conversational pace.
  - **Lighter:** fillers and self-corrections ("natural" in ETS comments), plain vocabulary, a missing wrap-up, and running over time unless the cut removes needed content.
  - **Explicit 4-triggers:** a part of the question only touched, generic elaboration, a collapsed sentence, pausing that affects flow.
- **Writing** (`toefl-writing-grader/references/ets-calibration.md`):
  - Non-impeding errors (about 2–3 genuine per 100 words plus typos) and plain vocabulary are compatible with 5.
  - No error-count or "precision" tiebreaker.
  - Agreement or synthesis with classmates counts as a contribution.
  - One elaborated argument is enough.
  - Caps from the Guide: a missing email point, language hard to follow plus overly simple, an AD under 100 words, memorized or formulaic text, content-free wordiness.


## Limitations
- **Top-heavy reference data.** All official samples are top-level (5) or very low (1–2 fragments). The 3/4 boundary was checked only with synthetic controls, so the system is best calibrated at the 5/4 line.
- **Small n:** 8 interview answers, 6 writing responses and 2 fragments.
- **Inferred levels.** Some reference levels come from the comment's wording, because no number is printed: the practice-test interviews, the boarding-school AD and the Overview's high-level samples.
- **Transcript gaps.** Our Whisper transcripts drop some fillers and differ slightly from ETS's transcripts, and pronunciation cannot be assessed.
- **Grader variance.** LLM graders vary by about ±1 on borderline responses, and a single grade is one sample of that.

## Re-running the calibration (any computer with the Guide PDF)
1. Extract the media: pymupdf `doc.embfile_get(0)` gives `Audio_Video Files.zip`. Rename the files; some names contain U+202F.
2. Build blinded packets: the items in the table above, plus our transcribe/answer_stats/text_stats output, with random IDs and the key in a separate file.
3. Run a fresh grader per packet: Read tool only, one file. Compare its scores with the key, change only the ETS rules, and validate on items the rules never saw.
