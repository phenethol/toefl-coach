# Logging: every graded answer goes into files

## Repo layout
```
CLAUDE.md                          learner settings and short rules; points to this skill (AGENTS.md does the same for other agents)
.claude/skills/toefl-coach/        this skill (scripts, references)
.claude/skills/toefl-writing-grader/  the writing grader
speaking/
  OVERVIEW.md                      all scores, averages, band, recurring errors, Focus (always ends with the summary)
  interview/<YYYY-MM-DD>-<topic>.md   one document per Take an Interview set
  listen-repeat/<YYYY-MM-DD>-<topic>.md  created when Listen and Repeat is practised
  recordings/<YYYY-MM-DD>-<topic>-q<N>.m4a   copies of the learner's recordings (-q2-q4 if one file holds several, -section<n> for a full section)
  sets/<topic>.txt                 interview-only sets for make_practice_set.py
  sets/speaking-section-<n>.json   full sections (Listen and Repeat + Interview) for make_speaking_section.py
  pending-sets.md                  sets given but not answered yet (texts hidden in <details>)
  formulas-and-stories.md          formulas per question type and the learner's story bank
  word-bank.md                     phrases and ready-made sentences per story
speaking-audio/<topic>-interview/  generated interview audio and timer video
speaking-audio/speaking-section-<n>/  generated full-section audio and video
listening/
  OVERVIEW.md                      all Listening results, band estimates, error types by task, Focus
  tests/<YYYY-MM-DD>-listening-<n>/   index.html (self-scoring, key embedded) + audio/
reading/
  OVERVIEW.md                      all Reading results, band estimates, errors by task and question type, Focus
  tests/<id>/index.html            interactive Reading tests (make_reading_test.py)
writing/
  OVERVIEW.md
  email/ · academic-discussion/ · build-a-sentence/   <YYYY-MM-DD>-<topic>.md
  pending-tasks.md                 writing prompts given but not answered yet
  tests/<id>/index.html            interactive Writing tests (make_writing_test.py)
.venv/ and .cache/                 local only (git-ignored)
```
The date is the day of the attempt, and the topic is a short English slug. One document per set (speaking) or per prompt (writing). Several attempts at the same prompt go in the same document as *Attempt 1, 2…*.

Write the documents in the feedback language set in `CLAUDE.md` (English by default). Task text, quotes, corrections and model answers are always in English.

## After every graded answer
1. Add the answer section to the set or prompt document, creating it from the template if needed.
2. Rewrite that document's closing **Summary** with the score table (both lenses), the most frequent errors in this document and the Focus for next time.
3. Update `OVERVIEW.md`:
   - add a row to the score history and recompute the averages, per set and overall, for both lenses
   - update the band estimate and the Progress notes
   - recount the error table, with how many answers show each error and examples
   - rewrite the Focus (3–4 points: first the ones that cost ETS points, then language)
4. **Sync with GitHub:** do it automatically if the repo's `CLAUDE.md` records the learner's standing approval, otherwise ask once. See the next section.
5. Give the same scores in chat, link the document, and say in one line that it was pushed (or why the push failed).

## Sync with GitHub
`origin` is the learner's own private repo. If there is no `origin`, skip the push and mention it once. Do the same after adding a new set, practice audio or prompt to the repo:
```bash
git pull --rebase --autostash   # bring in grades logged on another computer first
git add -A
git commit -m "Log <speaking|writing>: <set or task> <questions/attempt>"
git push
```
- Use one commit per grading turn. The subject line names what was logged, e.g. `Log speaking: environment set Q2-Q4` or `Log writing: academic discussion animal-testing attempt 3`.
- Never use `--force` and never rewrite history. If the rebase hits a conflict (both computers changed the same OVERVIEW section), merge both sides by hand so that no score row is lost, then continue.
- If there is no network or the push fails, keep the local commit, tell the learner in one line, and push at the next opportunity.
- If `git status` shows changes you did not make (for example another session logged a set), check that they are complete and commit them in their own commit, with a subject that says what they are.
- `.venv/`, `.cache/` and `dist/` are git-ignored and never get committed.

## Template: speaking set document
```markdown
# Take an Interview: <Topic>

**Date:** YYYY-MM-DD; **Answered:** questions …; **Conditions:** (timer video / no timer, how it was recorded)

> **Situation:** You have agreed to take part in a research study about …

| # | Type | Question |
|---|---|---|
| 1 | personal | … |

---

## Question N: <short label>

**Recording:** [file](../recordings/…) (m:ss–m:ss if several answers); **Speaking time:** ~… s; **Words:** …; **Pace:** ~… wpm; **Time:** within the limit / **+X s past the beep**; **Longest pause:** …

### Transcript
> … **(…)** …

### Scores
| | Score | Reason |
|---|---|---|
| **Strict estimate** | | |
| **ETS estimate** | | |

### What works
### What costs points
### Corrections
| Said | Better | Why |
|---|---|---|
### Model answer (level 5)
> …

---

## Set summary: most frequent errors and what to focus on
| Question | Strict | ETS |
|---|---|---|
| **Average** | | |

**Most frequent errors** (numbered, with examples from this set)
**Focus for next time** (2–4 points)
```

## Template: Listen and Repeat document (`speaking/listen-repeat/<date>-<topic>.md`)
```markdown
# Listen and Repeat: <setting>

**Date:** YYYY-MM-DD; **Set:** [speaking-section-<n>](../sets/speaking-section-<n>.json); **Recording:** [file](../recordings/…)

> Narrator: … Repeat only once.

| # | Sentence | Repeated (transcript) | Score 0–5 | What is missing or wrong |
|---|---|---|---|---|
| 1 | Welcome to the main campus, everyone. | … | 5 | |

**Average:** … / 5

## Summary: most frequent errors and what to focus on
**Most frequent errors** (endings, articles, function words, word order, dropped clauses, with examples)
**Focus for next time** (2–3 points)
```
A full section also gets its interview answers in `speaking/interview/<date>-<topic>.md`, and the section
band estimate (11 items, raw/55 → 0–30 → Table 3) goes in `speaking/OVERVIEW.md`.

## Template: Listening result (in `listening/OVERVIEW.md`)
Add one row per test to the history table:
| Date | Test | Raw | Choose a Response | Conversation | Announcement | Talk | Band (estimate) | Time |
Then a short section per test listing the wrong items, each with:
- the item number and task type
- the question type (main idea, detail, inference, purpose, idiom or implied meaning, prediction)
- the correct answer and why the chosen distractor was tempting

Close with a Summary (error types with counts) and a Focus.

## Template: writing document (Email / Academic Discussion)
```markdown
# <Write an Email | Academic Discussion>: <Topic>

**Date:** …; **Task source:** (the coach / external, summarised); **Conditions:** 7/10 min, spellchecker yes/no

## Task
> prompt (verbatim if the coach wrote it; otherwise a faithful summary)

## Attempt N
**Words:** …; **Sentences:** … (avg …) (from text_stats.py)

### Your response (verbatim)
> … (every typo kept)

### Scores
| | Score | Reason |
|---|---|---|
| **Strict estimate** | | |
| **ETS estimate** | | |
**Engine flags:** …

### Errors
| Original | Correction | Type |
|---|---|---|
### Biggest wins
### Level-5 version
### Section estimate
band, CEFR, range, with the caveat

---

## Summary: most frequent errors and what to focus on
```
Build a Sentence: a table with item, answer, correct/incorrect and pattern, the score k/10, then the same summary.

## OVERVIEW.md structure (speaking and writing)
1. How answers are scored (two lenses, calibration in one paragraph)
2. Score history (one row per answer: date, set link, question, type, strict, ETS, pace, time), with averages per set and overall
3. Band estimate for both lenses, with the caveat
4. Progress
5. Practice materials (links)
6. **Summary** (always last):
   - errors that also cost the ETS score, as a table with counts and examples
   - recurring language errors, as a table with counts and examples
   - Focus, 3–4 points
