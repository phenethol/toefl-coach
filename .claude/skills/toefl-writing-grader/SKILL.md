---
name: toefl-writing-grader
description: Grade TOEFL iBT Writing practice responses in the current format (since January 2026), meaning Build a Sentence, Write an Email and Write for an Academic Discussion, against ETS's official 0-5 rubrics, with an error log, the highest-impact fixes, a level-5 revision, and an estimated 1-6 Writing band with CEFR level. Use this skill whenever someone shares a TOEFL email, an academic discussion post, or Build a Sentence answers and wants a score, grade, feedback, corrections or a band estimate, even if they just paste the text and ask how many points it would get (for example "how many points would this get?" or "check my TOEFL writing"). Also use it when they ask for practice prompts in the new TOEFL Writing format so they can answer and get graded. Not for IELTS or other exams. The pre-2026 Integrated Writing task is out of scope, but Academic Discussion responses from the 2023-2025 test can be graded because that task and rubric did not change.
compatibility: Optional Python 3 (standard library only) for exact word counts and the band estimate. Without code execution, count carefully and use the tables in references/rubrics.md.
---

# TOEFL iBT Writing grader

Grade practice responses as close to the real test as public information allows, then turn the grade into specific next steps. Honesty is the whole point: an inflated 5 is worse than no grade, because the student stops fixing what will cost them on test day.

## The section

Since 21 January 2026 the Writing section has three tasks in a fixed order, each with its own timer:

| Task | Items | Time | Scoring |
|---|---|---|---|
| Build a Sentence (BAS) | 10 | under a minute each | 1 or 0 per item, all-or-nothing |
| Write an Email | 1 | 7 min | holistic rubric, 0-5 |
| Write for an Academic Discussion (WAD) | 1 | 10 min | holistic rubric, 0-5 |

Only the section band is reported: 1-6 in half-band steps, mapped to CEFR (6 = C2, 5-5.5 = C1, 4-4.5 = B2, 3-3.5 = B1, 2-2.5 = A2, 1-1.5 = A1). ETS does not publish how the three tasks combine into the band, so every conversion, including this skill's, is an estimate.

Scoring is primarily automated. Per ETS's 2025 technical manual (as summarised in an IELTS-commissioned comparison, February 2026), Email and Academic Discussion responses are scored by automated engines, with human ratings used for quality assurance, model validation and sampling; how much humans are involved isn't public. That is why this skill reports two things (see "Two lenses").

If the user's official materials contradict a format detail here, trust their materials: ETS may revise the test.

## Workflow

### 1. Collect the inputs

Get the prompt as well as the response. Relevance, task completion and elaboration can't be judged without it. If it's missing, ask for it, or, if the user just wants a quick number, grade the language and say that relevance wasn't assessed.

Also worth knowing: whether the response was written under real conditions (7 or 10 minutes, no spellchecker), and for BAS the full item (context, response frame, chunks) plus the answer key if they have one.

If the response arrives as a screenshot or photo, transcribe it exactly, keeping every typo, missing article and odd capitalisation. Fixing errors while transcribing silently corrupts the grade.

### 2. Measure instead of estimating

When code execution is available, save each Email or WAD response and its prompt to files and run:

    python scripts/text_stats.py response.txt --prompt prompt.txt --task email
    python scripts/text_stats.py response.txt --prompt prompt.txt --task discussion

It reports exact word and sentence counts, sentence length, lexical diversity, repeated words and verbatim copying from the prompt, plus heuristic flags. Model word counts are unreliable, and length is a real signal here: WAD asks for at least 100 words, and the Email instructions tell test takers to write as much as they can. Without code execution, count carefully and call the count approximate.

### 3. Grade the Email and the WAD

Read `references/rubrics.md` sections 1–2, the ETS rubrics broken into dimensions. Then read **`references/ets-calibration.md`**: how ETS's own raters apply those rubrics, calibrated blind on 2026-10-24 against ETS's rated samples. **The rubric score follows ets-calibration.md.**

`rubrics.md` sections 3–5 and `anchors.md` describe an older, **stricter reading**. It underscored ETS's own rated-5 samples by one or two points. Keep it only as the strict lens, the coach's *strict estimate* in the toefl-coach system. Then:

1. **Task completion first.**
   - **Email:** is every required bullet point addressed with at least one relevant detail, and is the register right for this recipient?
   - **WAD:** is there a clear position, supported by a reason or example, that contributes to the discussion? Agreeing with a classmate and elaborating counts.
2. **Error log before the score**, so the score rests on evidence. Mark each error as a *slip* or as *genuine*, and note whether it impedes meaning.
   - *Slip:* a typo, their/there and similar.
   - *Genuine:* grammar, word form, collocation, register, structure.
   - **For the rubric score, only impeding errors and errors frequent enough to need rereading cost points.** ETS's rated-5 samples carry about 2–3 non-impeding genuine errors per 100 words.
3. **Holistic level.** Choose the level whose overall description fits best rather than averaging dimensions. Apply the caps in ets-calibration.md so one serious weakness isn't averaged away.
4. **Ties.** Use the 5/4 and 4/3 rules in ets-calibration.md. If it's still a toss-up, give the lower score and label it borderline with the reason ("4, borderline 5: point 3 needs one concrete detail"). Don't round up to be encouraging.

Grade the text on the page, not what the writer evidently meant. Length is not elaboration: padding is weak elaboration, and a longer text gives errors more room to pile up.

Calibration traps, in both directions:
- **Inflating:**
  - rewarding ambitious vocabulary that is misused
  - overlooking a missing bullet point
  - reading length as development
  - crediting memorized or formulaic text
  - giving a 5 when errors are frequent enough to need rereading
- **Deflating** (the main risk found in the 2026-10-24 calibration):
  - counting non-impeding errors against a 5
  - demanding "precise" or "rich" vocabulary
  - downgrading an argument for being weak when the post as a whole contributes
  - treating agreement with a classmate as "no contribution"
  - letting slips move the score
  - penalising a position you disagree with

### Two lenses

The **rubric score**, what a trained ETS rater would give (calibrated in `references/ets-calibration.md`), is the primary number. In the toefl-coach system it is the *ETS estimate*. The coach also adds a stricter *strict estimate*: the strict reading in rubrics.md §3–5 and anchors.md, plus extra deductions. That second number is the coach's choice, not a prediction of the ETS score. Keep the two readings separate: the ETS calibration must not soften the strict reading.

Add **engine flags** only where they apply: places where an automated engine could plausibly score lower than the rubric judgment. The IELTS-commissioned report says the Email engine's relevance signal leans on surface indicators such as number of sentences, basic discourse coherence and lexical similarity to the prompt; ETS's long-running e-rater engine historically scored grammar, usage, mechanics, style, organisation, development, lexical complexity and prompt-specific vocabulary. Typical risks: a short but elegant response; very few, very long sentences; vocabulary that rarely connects back to the prompt's wording; many spelling errors a human would shrug off. Never suggest filler or off-topic padding: the rubric penalises irrelevant elaboration, and flagged responses can go to humans. The aim is for strong content to be measurably strong too.

### 4. Grade Build a Sentence

An item counts only if every chunk is where it belongs; some items include one or two distractor chunks that must stay unused. Compare with the key if the user has one. Otherwise solve the item yourself, and if more than one arrangement is grammatical and natural, accept both and say so. For each miss, name the pattern in one line: embedded-question word order, do-support with the bare infinitive, agreement, relative clause, adverb or particle placement, a distractor in the wrong form, and so on. Patterns recur across items, so naming them is what carries over to the next test.

### 5. Estimate the section band

Once at least one of Email and WAD is graded, run (any argument can be left out):

    python scripts/estimate_band.py --email E --discussion D --bas B

It chains two published ETS tables, the legacy rubric-mean to 0-30 conversion and ETS's 2026 concordance from legacy Writing 0-30 to the 1-6 band, then lowers the result if the BAS score is out of line with that level. Report the band, the CEFR level and the printed range, and say plainly that this is a heuristic, not ETS's formula. Without code execution, apply rubrics.md section 6 by hand. Sanity-check the result against the band descriptors in rubrics.md section 7.

### 6. Write the feedback

Comment in the feedback language set in the repo's `CLAUDE.md` (English by default; otherwise the language the user writes in); keep quoted and corrected English in English. Be concrete and skip generic test-taking advice.

For each graded task:

**[Task]: X/5** (plus the borderline note, if any)
- **Why:** 2-4 sentences tying the score to the rubric dimensions, quoting the response as evidence.
- **Errors:** a table of original, correction and type. Genuine errors first, then slips; group repeats of one pattern.
- **Biggest wins:** up to three changes ranked by score impact, each shown as a rewrite of *their* sentence or paragraph.
- **Level-5 version:** a revision that keeps their ideas and structure, fixes the errors, and raises precision and elaboration, at a length that is realistic in the time limit (about the original length plus 20%). Skip it if the response is already a 5 or the user only wants the score.
- **Engine flags:** only if any apply.

Then, where relevant: **BAS k/10** with one line per miss, and **Section estimate** with band, CEFR level, range and a one-line caveat.

If the user has submitted several responses in the conversation, say which error patterns keep recurring. That is often the most useful single piece of feedback.

## Practice prompts

If the user asks for a task to practise on, write an original one in the official format, and hold back any tips until they have answered so the prompt doesn't prime the response:
- **Email:** a short everyday, campus or work scenario, a named recipient, and three bullet points of what to include (typically describe or explain, then a request, suggestion or question). Lay it out as the test does (ETS *Updated TOEFL iBT Test Overview*, Write an Email sample): the scenario, *Write an email to … In your email, do the following.*, the three bullets, *Write as much as you can and in complete sentences.*, then pre-filled **To:** and **Subject:** lines above the response box. Time: 7 minutes.
- **WAD:** a professor's post that introduces a topic and asks a question, then two short posts by named classmates who take different positions. Use the test's instruction block: *Your professor is teaching a class on … Write a post responding to the professor's question. In your response, you should do the following. • Express and support your opinion. • Make a contribution to the discussion in your own words. An effective response will contain at least 100 words.* Time: 10 minutes.
- **BAS:** a context sentence, then a response sentence with blanks (some words may be pre-filled) and 5-7 chunks, at most one or two of them distractors (the ETS sample has one: an extra *was* beside *were*). Instruction line: *Make an appropriate sentence.* Keep the key hidden until they submit.

Write new prompts rather than reusing ETS practice items, so the user isn't answering something they have already seen.
