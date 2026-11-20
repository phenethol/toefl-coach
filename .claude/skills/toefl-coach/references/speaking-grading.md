# Speaking grading: two scores per answer

Every Take an Interview answer gets two holistic scores on the 0–5 task scale, each with a one-sentence reason. The two lenses have **separate rules**:

- **ETS estimate:** what an ETS rater would most likely give. It was calibrated on 2026-10-24, blind, against ETS's own rated answers (see *ETS estimate* below and `ets-calibration-report.md`).
- **strict estimate:** the coach's strict view. Its rules are **frozen as they were on 2026-10-23** and were not touched by the calibration. It is the strict training target, while the ETS lens is the realistic prediction.

When the two scores are the same, the problem is real and ETS would punish it too. When the ETS score is higher, the strict score shows what still separates the answer from an excellent one. On ETS's own top-rated answers the strict estimate is typically 4, by design.

## ETS estimate (calibrated 2026-10-24)

**Sources:**
- *The Official Guide to the TOEFL iBT Test, Pocket Edition* (2026): the Take an Interview scoring guide (p. 240), the scoring notes (pp. 225, 235, 244–247) and 8 rated answers with audio and rater comments (pp. 241–243, 335–337).
- The urban-life sample in the *Updated TOEFL iBT Test Overview*.

ETS material is not reproduced here; the features below are summarized from it.

**What ETS raters reward.** The scoring is holistic on four dimensions (Guide p. 235):
- **Relevance:** answer the question actually asked, every part of it ("the situation *and* how the advice helped", "agree or disagree *and* why"). A qualified position is fine: *both are valuable, but…*, *it depends, but maybe…*.
- **Elaboration:** support ideas with at least one personal example or concrete detail. Rated-5 answers do this with ordinary material: choosing a course versus picking a snack, being tired with no meal plan so making an omelet, a classmate who knows phones. Several short reasons are fine, and so is one developed example.
- **Delivery:** a good conversational pace with natural pauses.
  - ETS comments call fillers (*um, uh, like, you know, so yeah*), brief pauses and self-corrections (*I was… I mean, I was*; *he's, uh, he is*) "natural" or say they "do not interfere". They do not lower a 5.
  - What lowers the score is frequent or long pausing that makes the pace choppy, or fillers so frequent that they dominate (the 3 descriptor).
- **Language use:** minor slips that do not impede meaning are expected at 5.
  - The rated-5 answers contain *that's how I usually do*, *I chose omelet*, *like good camera*, *so I don't regret later*, *it make them feel better*, *It also depending on* and *they maybe miss*.
  - Plain, appropriate vocabulary is acceptable.

**Calibration evidence** (details in `ets-calibration-report.md`):
- All 8 rated Guide answers are top-level: 4 in ch. 5 rated "fully successful", and 4 in the practice test that are described in level-5 terms.
- By our own pipeline (Whisper + answer_stats) they run 92–130 words at 144–177 wpm. Each has 0–3 fillers in the Whisper transcript (ETS's own transcripts show more) and up to 5 pauses of 1 s or more.
- One ETS comment says a closing statement is "not necessary for a full score" (p. 336).
- Blind graders using these rules gave all 8 a 5, in the calibration set and in the held-out set. The low controls stayed at 2–3.

**Score descriptors (ETS lens):**
- **5:** answers every part of the question. Has at least one relevant personal example or concrete detail. The ideas connect and are easy to follow, the pace is conversational, and errors are minor and non-impeding. None of these prevents a 5:
  - fillers and self-corrections
  - plain vocabulary
  - a hedged position
  - the time limit cutting the answer after the main points have been made
- **4:** addresses the question and is reasonably clear, but has one clear limitation:
  - a part of the question is only touched
  - the elaboration is generic, with no example or detail
  - the ideas are weakly connected (no sentence-level connectors, or a collapsed sentence that takes effort to follow)
  - some pausing affects the flow
  - grammar and vocabulary are adequate only for general meanings
- **3:** generally on topic, but with limited elaboration and/or clarity. Any of these fits a 3:
  - the answer stays thin
  - frequent or long pauses make it choppy
  - fillers are frequent
  - errors noticeably restrict precision
  - it stops very early with little content
- **2:** minimally connected to the question, with little relevant elaboration and mostly the question's own language. Intelligibility is limited and the range is very limited.
- **1:** only vaguely connected, mostly unintelligible, or isolated words.
- **0:** no response, no English, off topic, or only "I don't know".

**Rules of thumb (ETS lens):**
- **The time limit cuts the recording.** Whatever is said after 45 s is lost, but being cut off is not itself penalized; the Guide says to prioritize clarity and coherence (FAQ, p. 247). Lower the score only if the cut removes something the answer needs, such as the answer to one part of the question or the only example.
- **A wrap-up sentence is not required for a 5.** An ETS rater says a conclusion is "not necessary for a full score" (p. 336). If time is running out, the Guide's advice is to move on and cover as much as possible (p. 244).
- **Length is not a criterion.** The Overview's high-level answers have only about 60–75 words, and the Guide's rated-5 answers about 90–130.
- **Memorized or formulaic language lowers the score** (pp. 235, 244).
- **On a tie**, give the lower score and mark it borderline (CLAUDE.md). Decide the tie by the descriptors above, not by counting fillers or slips.

## Strict estimate (frozen 2026-10-23, do not change)

**Guardrail:** the ETS calibration must not soften this lens. Grade it exactly as before 2026-10-24, with the table and descriptors below. Ignore the ETS section's tolerance for fillers, plain vocabulary, missing endings and running over time; for this lens those still cost points. On a tie, give the lower score. In the blind checks, an unguarded grader drifted up by +1 on 4 of 19 responses.

| | What it measures | Weighs heavily | Weighs lightly |
|---|---|---|---|
| **Strict estimate** | the stricter coach's view: what still separates the answer from an excellent one | relevance (every part of the exact question answered; a real choice on *would you rather / who should do more*), coherence (complete, followable sentences, no collapsed run-ons), a clear ending, finishing inside 45 s, plus fillers and restarts, basic or repeated vocabulary, no single deep concrete example, length outside 90–100 words | (nothing is ignored) |

**Score descriptors (strict lens):**
- **5:** fully relevant, every part answered, well elaborated (at least one specific detail or example), coherent and easy to follow, fluent with at most minor lapses, accurate language with only minor errors, a clear ending within the time.
- **4:** relevant and mostly well developed, but with one clear weakness: a part of the question thin or dodged, a run-on that takes effort to follow, noticeable lapses, or an ending that runs past the beep.
- **3:** addresses the question, but development is limited or unclear in places, coherence breaks down (a collapsed sentence, a drifting position), or errors are frequent enough to need effort.
- **2–1:** very limited, largely irrelevant or hard to understand. **0:** no response or off-topic.

**Reference point.** The strict lens grades ETS's own high-level answers at about 4: the Overview's urban-life sample gets 4 / 4 / 3 / 4, and the Guide's rated-5 answers get 4. That gap is intended. A Claude 5 means the answer is better than ETS's minimum for the top score.

## Pronunciation and delivery signal (pronunciation.py; never changes a score)
`scripts/pronunciation.py` reports which sounds were heard (a phoneme recognizer aligned with the expected pronunciation) and Praat delivery measures (pitch range, articulation rate, mean length of run, pauses inside phrases).
- It is a **separate signal**, reported after the scores under *Pronunciation and delivery (signal)*.
- It does **not** change the strict estimate, the ETS estimate or the Listen and Repeat scores.
- Read it against the ETS baseline in [pronunciation-signals.md](pronunciation-signals.md). Mention a sound pattern only when it recurs or changes a word.

## What to measure (answer_stats.py)
- **Speaking span, words and wpm.** Fillers are counted separately. The learner's typical range is 120–160 wpm.
- **Silent pauses of 0.5 s or more**, from ffmpeg silencedetect. Whisper's word timings absorb silence, so do not rely on them for pauses.
- **Words stretched over 1 s:** usually an elongation or a hidden *uhh*.
- **Over time:** anything spoken after the end beep is cut on the real test. For the ETS lens see the rule of thumb above; the strict lens counts it as before.
- Mark mid-phrase pauses in the transcript as **(…)**.

## The learner's recurring patterns (check every answer)
The learner's own patterns, with counts and examples, live in the repo's `speaking/OVERVIEW.md`. Read its error tables before grading, and update them afterwards.
Until there is data, check the patterns that are common for many learners (and, if `CLAUDE.md` names a first language, the ones typical for it):
1. Not answering the exact question or not choosing a side.
2. Long chained or collapsed sentences (*and… because… I think…*).
3. Running past the end beep, which is most common on questions 3 and 4.
4. Articles and countability (*the* where *a* belongs; *the* in general statements; *informations*, *legislations*). *The environment / the planet* do need *the*.
5. Calques from the first language: a dropped subject (*I think is…*), *prefer … than*, *enjoyed it really much*, *at <city>* for *in <city>*.
6. Repeating *I think*, *for example* or one adjective.
7. Restarts at the start of an answer (*I, I, I…*).

## Band estimate
TOEFL reports sections on a 1–6 scale in half bands (6 = C2, 5 = C1, 4 = B2, 3 = B1, 2 = A2, 1 = A1). ETS does not publish the conversion from task scores, so any band you give is an estimate. Give it for both lenses, and say that Listen and Repeat is part of the Speaking section score.
- **Full section** (7 Listen and Repeat + 4 interview items, raw 0–55): divide by 55, multiply by 30, and read the Speaking column of Table 3 in [ets-format.md](ets-format.md).
- **Listen and Repeat** is scored with the ETS guide in ets-format.md. 5 is an exact repetition; 4 has minor changes that keep the meaning, such as a function word, an ending or a transposition. Compare the transcript with the sentence word by word, but remember that Whisper may "correct" a slip the learner actually made. It can also drop a short, unstressed word that was said (*The library is* heard as *The library*). When a missing function word is the only difference, cut the clip, send it to the learner and confirm before lowering the score.
  - The Guide gives no rated learner repetitions, so this part is not empirically calibrated.
  - It does say that partial credit is given for any part repeated accurately (p. 226).

## Feedback format for each answer
1. Header line: recording (with the time range if it holds several answers), span, words, wpm, time status, longest pause.
2. Transcript.
3. Score table: strict estimate and ETS estimate, one line each.
4. **What works**: 1–3 points with the learner's own phrases.
5. **What costs points**: what costs points, the most important first. Say which lens each problem affects; many cost only the strict score.
6. **Corrections**: a table with what was said, the better version and why.
7. **Model answer (level 5)**: about 85–100 words that keep the learner's own ideas. Give it for answers below 5 or when asked. The learner may adjust the details to what is actually true for them.
