# ETS format reference: what each task looks like and how it is scored

**Rule:** every task, set, test and video follows this file. Do not invent formats. If something is not covered here, check the ETS sources below, or tell the learner it is not specified.

**Sources**
- ETS, *Updated TOEFL iBT® Test Overview* (with sample questions), 28 pp.
  - Download it from ets.org (TOEFL iBT, *Test Overview with sample questions*) and keep it outside the repo, e.g. `~/Downloads/toefl-overview-with-sample_questions.pdf`. It is ETS material, so it is never committed.
- ETS, *TOEFL iBT Test: 2026 Update Test Blueprint and Specifications Document*: https://www.eu.ets.org/pdfs/toefl/toefl-ibt-test-specifications-2026.pdf
- ETS, ***The Official Guide to the TOEFL iBT® Test, Pocket Edition (2026)***, 362 pp. This is the most detailed source: scoring guides, rated sample responses with rater comments, a full practice test and section performance descriptors.
  - Buy it from ETS and keep it outside the repo, e.g. in `~/Downloads/`. It is never committed.
  - It embeds `Audio_Video Files.zip` with all 94 audio tracks and 4 videos. Extract it with pymupdf `doc.embfile_get(0)`.
  - Ten file names contain a narrow no-break space, so rename them when extracting.
  - The rated samples were used for the ETS-lens calibration (see `speaking-grading.md` and the writing grader's `references/ets-calibration.md`).

The facts below are summarized from those documents (page numbers without a source refer to the Overview). Instruction lines that the test shows on screen are quoted because the practice materials reuse them; everything else is paraphrased.

## Test structure (Overview p. 4)
Sections come in this order: Reading → Listening → Writing → Speaking. Reading and Listening are multistage adaptive: the first stage (router) decides whether the second stage is a lower or an upper module.

| Section | Task types | Items | Time |
|---|---|---|---|
| Reading | Complete the Words, Read in Daily Life, Read an Academic Passage | 35–48 | ~27 min |
| Listening | Listen and Choose a Response, Listen to a Conversation, Listen to an Announcement, Listen to an Academic Talk | 35–45 | ~27 min |
| Writing | Build a Sentence, Write an Email, Write for an Academic Discussion | 12 | ~23 min |
| Speaking | Listen and Repeat, Take an Interview | 11 | ~8 min |

Every test taker gets unscored pretest items in either Reading or Listening.

The Blueprint gives more detail for Listening: about 47 items (with pretest) and 35 raw points.
- Listen and Choose a Response: 15–19 items
- Listen to a Conversation: 10 items
- Listen to an Announcement: 6–10 items
- Listen to an Academic Talk: 8–16 items

For Speaking, the Blueprint gives 7 Listen and Repeat items and 4 Take an Interview items, 5 points each (55 raw).

## Reading (Official Guide 2026, ch. 2 pp. 50–55 and the ch. 6 Practice Test pp. 250–259, 292–295)
General rules for the section:
- **Multistage adaptive:** about 35 questions in Module 1 and about 15 in Module 2 (about 50 in all). The Module 1 result decides the difficulty of Module 2.
- **Practice Test timing:** Module 1 about 20 min, Module 2 about 9 min. Inside a module the learner may review and change answers while time remains.
- **Unscored items:** in the Practice Test, 15 of the 35 Module 1 questions are unscored (pretest), so the raw score is out of 35 (20 + 15). The test taker is not told which ones.
- **Texts** come from academic and everyday campus life: textbook-like passages, scientific articles, emails, schedules, posters and social media posts.

| Task | What the learner sees | Questions |
|---|---|---|
| **Complete the Words** | *"Fill in the missing letters in the paragraph."* An academic paragraph of **70–100 words**. The first sentence is complete; after it, as a rule, the **second half of every second word** is missing, **10 words** in all, content words and function words alike. One box per missing letter. | 10 items, one per word |
| **Read in Daily Life** | A label such as *"Read an email."* or *"Read a social media post."*, then a short practical text of **15–150 words** (email, poster, notice, schedule, social media post). | **2 or 3** multiple-choice questions: main idea or purpose, details, informal language, inference |
| **Read an Academic Passage** | A titled expository passage of **about 200 words** (history, science, the arts); no background knowledge needed. | **5** multiple-choice questions |

**The 8 question types** (Guide pp. 55–126; each has worked examples there):
- Basic comprehension: **Factual** and **Negative Factual** (*NOT*, *EXCEPT*), **Vocabulary** (a highlighted word, *"…is closest in meaning to"*), **Select the Sentence**, **Sentence Simplification**, **Reference**.
- Inferential comprehension: **Inference**, **Rhetorical Purpose** (*"Why does the author mention…?"*), **Insert Text** (*"There are four locations in the passage (marked with [A], [B], [C], and [D]) that indicate where the following sentence could be added."*, then the sentence and *"Where would the sentence best fit?"*).

The Practice Test's Module 1 has two Complete the Words paragraphs (items 1–20), an email (2 questions), a social media post (3) and two academic passages (5 each). Module 2 has one Complete the Words paragraph and one academic passage.

**Band:** the Guide gives its own conversion for the Practice Test, raw /35: 34–35 = 6 (C2), 32–33 = 5.5, 28–31 = 5 (C1), 25–27 = 4.5, 18–24 = 4 (B2), 12–17 = 3.5, 8–11 = 3 (B1), 7 = 2.5, 6 = 2 (A2), 0–5 = 1 (A1). Use it for any 35-item test of this shape, and say it is an estimate.

Our Reading tests (`make_reading_test.py`) follow this section; the test JSON is written by hand.

## Listening (Overview pp. 8–12; Blueprint pp. 10–12)
General rules for the section:
- **Audio plays once.** A picture of the speaker(s) is shown during the audio.
- **Questions come after the audio**, with printed stems and 4 options (A–D).
- **Accents:** North America, UK, Australia and New Zealand. The ETS audio is partly AI-generated.
- **Lengths:** single utterances can be as short as about six stressed syllables, mid-length audio is about 35–100 words, and monologues go up to 250 words.

| Task | What the learner hears | What the learner sees and answers |
|---|---|---|
| **Listen and Choose a Response** | One short question or statement, campus-life or social. **Heard only, never written on screen.** | *"Choose the best response."* and 4 written replies. Wrong options often echo a word or sound from the prompt, or answer a different question. Tests literal and implied meaning. |
| **Listen to a Conversation** | Narrator: *"Listen to a conversation."* Then two speakers in an everyday or campus situation (dining, services, housing, health, travel, and so on). | **2 questions**: main idea or context, detail, implied meaning, the purpose of a remark, or what a speaker will do next. |
| **Listen to an Announcement** | Narrator, e.g. *"Listen to an announcement in a classroom."* Then **40–85 words** in a classroom or at a school event: schedules, directions, rules, achievements. | Questions on the purpose, details, inferences and what will happen next. ETS does not state the number per announcement; use 2. |
| **Listen to an Academic Talk** | Narrator, e.g. *"Listen to a talk on a podcast about psychology."* Then a talk of **100–250 words** from history, art and music, life science, physical science, business and economics, or social science. No background knowledge is needed. | **4 questions**: main idea, supporting detail, inference, why the speaker mentions something (organization), and less common or idiomatic vocabulary. |

Our practice tests (`make_listening_test.py`) use 30 scored items, matching the raw score range of 0–30. They are split into a router stage and an upper stage:
- Stage 1: 5 Choose a Response, 1 conversation, 1 announcement, 1 talk
- Stage 2: 5 Choose a Response, 2 conversations, 2 announcements, 1 talk

## Speaking (Overview pp. 17–20, scoring pp. 26–28)
**Listen and Repeat**
- The narrator sets a scene with a role and a purpose, and ends with *"Repeat only once."* The ETS sample is *learning to welcome visitors to the zoo, listen to your manager and repeat what she says.*
- The setting is academic or campus life. An illustration of it stays on screen, and progress through the sentences moves through parts of the illustration.
- **7 sentences in a fixed pattern** (Official Guide 2026, pp. 226–234):
  - 2 short (9–11 syllables, one simple clause): **8 s** each
  - 3 medium (14–16 syllables, a prepositional phrase or a dependent clause): **10 s** each
  - 2 long (19–23 syllables, several modifiers, lists or dependent clauses): **12 s** each

  Example sentences from the Guide: *"Fill out the form to request your transcript."* (10 syllables) and *"If you need an unofficial transcript, which you can keep for your own records, check this box."* (22 syllables).
- After each sentence there is a **2-second pause, then a beep**, then the response window with an on-screen timer. The learner repeats it once, exactly.
- Scoring is holistic on **intelligibility** and **accuracy**, and partial credit is given for any part repeated accurately.
- On-screen line: *"Listen and repeat only once."*

**Take an Interview**
- The narrator says: *"You have agreed to take part in a research study about … You will have a short online interview with a researcher. The researcher will ask you some questions."* Other situations, such as a scholarship application, are possible.
- On-screen line: *"Please answer the interviewer's questions."*
- A prerecorded interviewer asks **4 questions**, with **45 s for each and no preparation time**.
- **Questions 1–2** are about facts and personal experience, for example the last city visited and why, or your reaction to cities and why.
- **Questions 3–4** ask for an opinion on broader issues, for example whether city people lead more interesting lives, or whether cities should build more parks. Both end with *Why or why not?*
- **How the interviewer talks:** there is a short reaction before each question (*Thank you for speaking with me today… / Great. … / OK. Next, I'd like to ask your opinion. … / Good points. Let me ask you one final question. …*). Each question has one or two sentences of context, then one or two questions.
- **Question types** (Official Guide p. 236):
  - personal: experiences, plans or goals, preferences or interests, observations about people close to you
  - abstract or speculative: opinions on current topics or trends, the future, hypotheticals (*If you were…*)
- **Timing:** the response time starts **immediately after the question**; on the real test there is no beep. The interviewer nods while the learner answers. Our practice videos add a start beep so `split_section.py` can find the answers; this is a known deviation.
- **Advice:** use the full 45 s. Memorized phrases lower the score. Relevant content earns partial credit.

**Scoring guides (0–5)**
- **Listen and Repeat**
  - 5: an exact, fully intelligible repetition.
  - 4: the meaning is kept, with minor changes: one or two function words, one content word in a long sentence, a tense, aspect or number marker, two transposed words, or one or two unclear words.
  - 3: an essentially full sentence, but the meaning is not captured accurately: several function words or a content word changed or missing.
  - 2: a large part is missing or wrong; fragments.
  - 1: a few words only, or mostly unintelligible.
  - 0: no response.
- **Take an Interview**
  - 5: fully addresses the question, well elaborated, a good conversational pace with natural pauses, easily intelligible, accurate range.
  - 4: addresses the question and is reasonably clear. Elaborated, but may lack sentence-level connectors; some pausing; minor effort needed to understand occasional words; grammar and vocabulary adequate for general meanings.
  - 3: limited elaboration or clarity, a choppy pace, frequent fillers, limited range.
  - 2–1: minimally connected or mostly unintelligible.
- Holistic scoring looks at **relevance, elaboration, delivery and language use**. The Guide (p. 225) says high-scoring responses can still contain occasional errors and minor problems in any of these areas.
- All rated samples (the Overview's urban-life interview and the Official Guide's 8 interview answers) have plenty of *um/uh*, self-corrections and grammar slips. See `speaking-grading.md` for the calibration.

## Writing (Overview pp. 13–16, scoring pp. 23–25)
- **Build a Sentence (10 items):** one intact sentence, then a reply whose words and phrases are scrambled. On screen: *"Make an appropriate sentence."* There may be a distractor; the ETS sample has an extra *was*.
- **Write an Email (7 min):**
  - The scenario, then *"Write an email to … In your email, do the following."* and three bullets.
  - Then *"Write as much as you can and in complete sentences."*, with pre-filled **To:** and **Subject:** lines.
- **Write for an Academic Discussion (10 min):**
  - *"Your professor is teaching a class on … Write a post responding to the professor's question. In your response, you should do the following. • Express and support your opinion. • Make a contribution to the discussion in your own words. An effective response will contain at least 100 words."*
  - Then the professor's post and two named student posts.
- Both written tasks are scored 0–5. The full rubrics are in the `toefl-writing-grader` skill.
- **What the Official Guide adds** (pp. 36, 207, 212–218):
  - Responses are treated as **first drafts**, and a high score is possible with some errors.
  - **Email:** every required point must be addressed. A concise email is fine if it is complete, relevant and organized.
  - **Academic Discussion:** responses under 100 words usually lack the development needed for a 5. One well-elaborated argument is enough for a 5.
  - **Language cap:** language that is hard to follow, overly simple sentences and limited vocabulary cap a response at about 3, whatever the content.
  - **Memorized material:** memorized or formulaic text (wordy openings and closings, canned examples or "polls") scores "considerably lower". Content-free wordiness gets "just 1 or 2".

## Score reporting (Overview pp. 21–22)
- Every section and the total get a band from 1 to 6 in half bands. The total is the mean of the four section bands, rounded to the nearest half band.
- Raw score ranges: Reading 0–30, Listening 0–30, Writing 0–20, Speaking 0–55.
- CEFR: 6 = C2, 5–5.5 = C1, 4–4.5 = B2, 3–3.5 = B1, 2–2.5 = A2, 1–1.5 = A1.

**Table 3: band ↔ old 0–30 section score and 0–120 total**

| Band | Reading | Listening | Writing | Speaking | Total 0–120 |
|---|---|---|---|---|---|
| 6 | 29–30 | 28–30 | 29–30 | 28–30 | 114 |
| 5.5 | 27–28 | 26–27 | 27–28 | 27 | 107+ |
| 5 | 24–26 | 22–25 | 24–26 | 25–26 | 95+ |
| 4.5 | 22–23 | 20–21 | 21–23 | 23–24 | 86+ |
| 4 | 18–21 | 17–19 | 17–20 | 20–22 | 72+ |
| 3.5 | 12–17 | 13–16 | 15–16 | 18–19 | 58+ |
| 3 | 6–11 | 9–12 | 13–14 | 16–17 | 44+ |
| 2.5 | 4–5 | 6–8 | 10–12 | 13–15 | 34+ |
| 2 | 3 | 4–5 | 5–9 | 11–12 | 24+ |
| 1.5 | 2 | 2–3 | 3–6 | 5–9 | 12+ |
| 1 | 0–1 | 0–1 | 0–4 | 0–2 | 0+ |

ETS does not publish how raw scores on the new test convert to bands (the test is adaptive). For our estimates, scale the raw score to 0–30 and read the section's column above. Always say it is an estimate.
- **Listening:** raw/30, read straight off the table.
- **Speaking:** (sum of 11 item scores)/55 × 30. L&R items are 7 of the 11, so the estimate leans on them.
- **Writing:** the chained method in `toefl-writing-grader`.
