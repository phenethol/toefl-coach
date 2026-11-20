# Pronunciation and delivery signals (added 2026-10-25)

**An extra signal for practice. It never changes a score:** not the strict estimate (frozen), not the ETS estimate, not Listen and Repeat. Report it in its own section after the scores.

Script: `scripts/pronunciation.py` (usage in its docstring). Everything runs locally; recordings never leave the computer.

## What it measures
**Sounds.**
- A wav2vec2 phoneme recognizer (`facebook/wav2vec2-lv-60-espeak-cv-ft`, about 1.2 GB in `.cache/hf`) hears which sounds were said.
- They are aligned with the expected US pronunciation from misaki: for Listen and Repeat, the sentence; for the interview, Whisper's transcript.
- **sound match** is the share of expected sounds heard as such.
- The report lists only patterns that are common for many learners (the default set fits Slavic and many other European first languages; extend `PATTERNS` in the script for others):
  - *th* /θ ð/ → t, d, s, f, z, v
  - /æ/ → e (*bad = bed*)
  - /ʌ/ → a or o (*buddy, but, cup*)
  - /ɪ/ vs /i/ (*ship = sheep*)
  - /ʊ/ vs /u/ (*full = fool*)
  - w → v
  - h → x or dropped
  - word-final b/d/g/v → p/t/k/f
  - *ng* → *ng-g*
- It also lists words of three or more sounds where under half the sounds matched ("hard to recognize").

**Delivery** (Praat via parselmouth):
- **pitch range:** the 10th–90th percentile spread of F0, in semitones. Low means flat intonation.
- **articulation rate:** syllables per second of actual speech, pauses excluded.
- **mean length of run:** syllables between silent pauses of 0.25 s or more.
- **pauses inside phrases:** silent pauses of 0.4 s or more between two words with no punctuation between them in Whisper's transcript.

## Validation (2026-10-25)
| Test | Result |
|---|---|
| ETS native recordings: 14 Listen and Repeat sentences from the Guide (ch. 5 and 6) | sound match 95.8%; 2 pattern hits in 14 sentences (no th, æ, ʌ, w or devoicing hits) |
| Planted errors: Kokoro forced to say *tink, dat, de, bed* (for *bad*), *body* (for *buddy*), *vants, vater, dis, ting, bik* | `af_heart` 9 of 10 caught, `am_michael` 7 of 10; the correct version of the sentence: 0 hits |

Before the fixes, misaki and espeak notation differed (stress and length marks, *tour/tore*, *cot/caught*, reduced vowels, *more*). These are now treated as equal (`SAME` in the script), and plural -s → s is not reported because natives do it too.

## Baseline: how to read the numbers
ETS's 8 rated-5 test-taker answers (Guide tracks 49–52 and 91–94), measured with this script:

| | ETS rated 5 (8 answers) |
|---|---|
| sound match | 89–96% |
| learner-type pattern hits per answer | 0–10 (track 94: 4× ɪ/i, 3× ð→z) |
| pitch range | **7.8–9.9 st** |
| articulation rate | 4.6–6.0 syl/s |
| mean length of run | 6.0–10.3 syl |
| pauses inside phrases (≥ 0.4 s) | 0–5 |

**Rules for using it:**
- **Accent is not an error.** ETS rated-5 answers have up to 10 pattern hits. Mention a sound pattern only when it **recurs** (in 2 or more answers or 3 or more times) or when it changes a word (*buddy → body*). Then give 3–4 practice words.
- **Compare with the baseline, not with 100%.** A sound match in the 89–96% range is normal for rated-5 speech.
- **Interview mode has a blind spot.** It compares with Whisper's words. If Whisper "corrects" a mispronounced word into another real word (*buddy → body*), the expected text is already wrong. Check suspicious words by cutting the clip and running `--text` with the intended words.
- **Recording conditions differ.** ETS's samples are studio audio; the learner records on a phone. Pitch range in semitones is robust to that; pause counts less so. Treat a difference as real only if it is large and repeats across answers.
- **Silent vs filled pauses.** ETS speakers often fill pauses with *um/uh*. Silent pauses inside a phrase sound more like searching for words. This is what the ETS descriptors call pausing that affects the flow; it is a practice target, not a score change.
