# TOEFL preparation

This folder is a log of preparation for the TOEFL iBT in its current format (since 21 January 2026) and a portable environment at the same time. All behaviour, scripts and templates live in the skill [`.claude/skills/toefl-coach/`](.claude/skills/toefl-coach/SKILL.md), so everything works the same on every computer where this folder is cloned. Other AI agents read the same rules through [`AGENTS.md`](AGENTS.md).

## Learner settings (edit these)
- **Feedback language:** English. Change it to any language you prefer; task text, quotes, corrections and model answers always stay in English.
- **First language:** not set. If you set it (for example *Spanish*, *Polish*), the coach also checks the error and pronunciation patterns typical for that language.
- **Commit and push to GitHub automatically after every grade:** NO. To turn it on, change it to *YES* and add your private repo, e.g. `your-name/toefl-prep`.
- **May the coach use its memory of you and your other conversations as material for your stories:** NO. Change it to *YES* if you want.

## Always
- For every TOEFL request, use the **toefl-coach** skill: a new task or set, a full Speaking section (Listen and Repeat + Interview), a Listening or Reading test, an interactive Writing test, grading a recording, a text or a result, audio and timer videos, structure and timing, progress. Writing is graded with the **toefl-writing-grader** skill in `.claude/skills/toefl-writing-grader/`.
- **Task formats always follow ETS, never an invented format.** The source of truth is `.claude/skills/toefl-coach/references/ets-format.md` (a summary of ETS's *Updated TOEFL iBT Test Overview* and the 2026 Blueprint).
- **Every grade is logged in files:** the set or task document, the summary at the end of that document, and the section's `OVERVIEW.md`. Until that is done, the task is not finished.
- **Commit and push** follow the setting above. If it is *NO*, ask once after logging. Never use `--force`.
- Every Speaking Interview, Email and Academic Discussion answer gets two scores: the **strict estimate** and the **ETS estimate** (calibrated).
  - The **ETS estimate** was calibrated blind on ETS's rated responses from the *Official Guide* (2026). The report is in `references/ets-calibration-report.md`, and the Writing rules are in `toefl-writing-grader/references/ets-calibration.md`.
  - The **strict estimate** is the strict lens, and the calibration must not soften it.
- Before giving feedback or a new task, read the "Focus" at the end of `speaking/OVERVIEW.md`, `listening/OVERVIEW.md`, `reading/OVERVIEW.md` or `writing/OVERVIEW.md`.
- Stories in `speaking/formulas-and-stories.md` are built **only from real details** in the learner's answers. They are never invented.
- Recordings from `~/Downloads` are copied into `speaking/recordings/`; the originals are never deleted.

## First time on a new computer
```bash
bash .claude/skills/toefl-coach/scripts/setup_env.sh
```
This needs `uv` and `ffmpeg`. The models (~4 GB) download to `.cache/hf` on first use. `.venv/` and `.cache/` are never committed.

## Where things are
| Path | Contents |
|---|---|
| `speaking/OVERVIEW.md`, `listening/OVERVIEW.md`, `reading/OVERVIEW.md`, `writing/OVERVIEW.md` | all scores and results, averages, band, most frequent errors, focus |
| `speaking/interview/`, `speaking/listen-repeat/`, `writing/<task>/` | one document per set or task, with a summary at the end |
| `speaking/recordings/` | answer recordings |
| `speaking/sets/` | set definitions: `.txt` for interview sets, `speaking-section-<n>.json` for full sections |
| `speaking-audio/` | generated audio and timer videos |
| `listening/tests/<id>/index.html` | Listening tests: open in a browser |
| `reading/tests/<id>/index.html` | Reading tests: two timed modules, then the score and band |
| `writing/tests/<id>/index.html` | interactive Writing tests: three tasks with the exam's timers; Build a Sentence scores itself |
| `speaking/pending-sets.md`, `writing/pending-tasks.md` | practice tasks not answered yet |
| `speaking/formulas-and-stories.md`, `speaking/word-bank.md` | formulas per question type, your stories and phrases |
| `.claude/skills/toefl-coach/references/ets-format.md` | the official ETS format of every task, the rubrics and the band tables |
| `.claude/skills/toefl-coach/references/strategies.md` | answer structures, timing, score scales |
