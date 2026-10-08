# Exam prep: 30-day exam plan (project spec)

Learner: preparing for a **big-tech data scientist exam in 30 days** (TikTok/ByteDance, Samsung, Google style).
Three tests: **algorithms (coding)**, **data analysis (SQL + statistics/A-B/product)**, **AI (ML, deep learning, LLMs)**.
Not a beginner: has background in all areas, needs speed, recall and pattern recognition. Uses **Google Colab**.
A colleague may translate; the website is in **English, Persian (fa, right-to-left) and Korean (ko)**.

The older 35-day course (`30_day_plan/`, builders in `_build/simple30/`) stays as deep reference material.

## Two deliverables
1. **Website (artifact)** "the handbook": tabs Plan, Algorithms, SQL, Statistics, AI, Cheat sheets, Daily theory Q&A,
   Resources. Explanations with many examples, intra links between sections, quick-lookup cheat sheets,
   three languages. Source: `_build/exam30/site/`.
2. **Exam notebooks**: `exam_prep/day_NN/1_algorithms.ipynb, 2_sql.ipynb, 3_stats.ipynb, 4_ai.ipynb`
   (Colab). Real datasets in `exam_prep/data/` (see `DATASETS.md`). Builders in `_build/exam30/`.

## Learning principles (apply everywhere)
- **Interleaving**: every day mixes patterns/topics. Never a whole day of one pattern. Recognizing *which* method to
  use is part of the skill, so exam questions do NOT print the pattern name; the first hint reveals it.
- **Retrieval first**: try before any hint. Theory Q&A on the website are flashcards (answer out loud, then reveal).
- **Spaced repetition**: wrong/slow questions go into the mistake log and are redone 3 and 7 days later.
  Each day's SQL/stats/AI notebook also has 1 to 2 interleaved review questions on earlier topics.
- **Time boxes** (energy matters): algorithms 15 min stuck -> hint 1, 25 min -> hint 2 / solution, then log it.
  Never spend 2 hours on one problem.
- **Elaboration**: every answer explains *why* (and complexity for code), plus a "learn more" link to the website.
- **Difficulty ramp**: days 1 to 10 easy (first mediums from day 8), days 11 to 20 medium, days 21 to 30
  medium-hard and hard. Mock exams on days 7, 14, 21, 28; day 29 full loop; day 30 light review.
- **Daily load** about 2h15: warm-up redo 10 min, algorithms 50 to 55 min (3 problems), SQL 20 to 25 min (5 queries),
  stats 20 to 25 min (4 questions), AI 20 to 25 min (5 questions), theory flashcards 10 min. Algorithms first, while fresh.

## Exam notebook rules (all four topics)
- English, plain sentences, no em/en dashes, no emojis. Formulas in plain text or inline code, never `$...$`.
- Top: title `Day N: Algorithms (easy)` etc., the day's rules in 3 lines, a table of the questions with suggested
  minutes and difficulty, and a link to the handbook.
- Setup cell first (self-contained, works in Colab and locally): helpers (`check()` for algorithms, `run()`/`show()`
  for SQL), and the data loader that finds `exam_prep/data` in Google Drive (mounts Drive in Colab) or falls back
  to downloading from the source URL in DATASETS.md.
- Each question: `### Q1 (easy, ~15 min)` + a short title that does NOT name the pattern, the prompt (own words; for
  LeetCode problems write the statement in your own words with your own example and add the LeetCode link),
  an empty or stub code cell with tests that print pass/fail, then three dropdowns: **Hint 1** (the signal and the
  pattern name), **Hint 2** (the approach in steps), **Solution** (code + why + time/space complexity + common
  mistakes + `Learn more:` handbook section ids). Text questions get an empty markdown answer cell.
- Every solution is executed at build time; expected outputs written in comments must match.
- End: "Log it" box: which questions to put in the mistake log (wrong, used hint 2, or over time).
- Real data wherever the topic allows (SQL on Chinook/real tables plus small exam-style tables; stats and ML on
  the real datasets). Small made-up tables are fine for classic exam SQL patterns, but say so.

## Handbook section ids (for links)
`algo-<slug>`, `sql-<slug>`, `stats-<slug>`, `ai-<slug>`, `cheat-<slug>`, `day-NN`. The content agents create the
exact list in `site/content/en/<tab>.json`; notebooks link with the website URL + `#<id>`.
