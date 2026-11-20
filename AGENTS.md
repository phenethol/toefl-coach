# Instructions for AI coding agents (any provider)

This repository is a TOEFL iBT coach. It was built for Claude Code, but nothing in it depends on one provider: the behaviour lives in Markdown instructions and the work is done by local Python scripts.

1. **Read `CLAUDE.md` first.** Despite its name, it holds the learner's settings and the rules for every agent (language, logging, GitHub sync, ETS formats only).
2. **Use the skills in `.claude/skills/`.** Each is a folder with a `SKILL.md` (instructions), `references/` and `scripts/`:
   - `toefl-coach/SKILL.md` for every TOEFL request (tasks, tests, audio and videos, grading recordings, progress)
   - `toefl-writing-grader/SKILL.md` for grading Writing
   If your tool loads Agent Skills (`SKILL.md`) automatically, point it at `.claude/skills/`. Otherwise, open the matching `SKILL.md` and follow it.
3. **Run the scripts with the project's virtual environment** (`.venv/bin/python …`), created once with `bash .claude/skills/toefl-coach/scripts/setup_env.sh`. Transcription, speech synthesis, videos, measurements and test pages all run locally.
4. **Grading needs judgment, so the model matters.** The rules in `references/speaking-grading.md` and the writing grader's `references/ets-calibration.md` were calibrated with a Claude model. With another model, re-check them on ETS's rated samples before trusting the scores (procedure in `toefl-coach/references/ets-calibration-report.md`).
5. **Skill names in the instructions that are specific to Claude** (for example sending a file to the chat, or a sub-agent) have an equivalent in most agents; if yours has none, give the file path or do the step yourself.
