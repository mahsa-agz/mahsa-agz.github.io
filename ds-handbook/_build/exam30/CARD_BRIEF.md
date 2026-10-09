# Brief: short, question-first explanations (rewrite of the handbook tabs)

The learner found the long pages hard to follow. Goal: **learn the most with the least effort.** Every section becomes
one short "card": a concrete question first, then the method in plain words, then when to use it, then the next
question that leads to the next topic. Straight to the point. No filler, no history, no long introductions.

Folder: `C:\Users\USER\Desktop\personal\my_personal\mahsa-agz.github.io\ds-handbook\_build\exam30`.
Read `plan.py` (SECTIONS: the exact section ids and their order). Keep EVERY id exactly (links depend on them).

## Card format (markdown in the section "body"), 6 to 15 lines total
```
**Question:** one concrete everyday situation with small, obvious numbers.

- **Method A:** one plain line, with the result for the example.
- **Method B:** one plain line, with the result.

**Use:** when to choose which, in one or two lines.
**Watch out:** the one mistake people make (optional, one line).
**Next question:** a new situation this cannot handle -> [Next topic title](#next-section-id)
```
- "summary" field: one line, the question the card answers (e.g. "One number that describes a group").
- "title": short and plain (e.g. "Mean, median, mode").
- Example numbers must make the effect OBVIOUS: one huge value next to small ones (3, 3, 4, 5, 100), clearly
  different groups, round numbers. Never numbers close together. Compute every number with Python and check it.
- Plain everyday words. Say "affects the result a lot", not "pulls it" or "is sensitive to". Explain any term the
  first time in a few words. Short sentences.
- Formulas only if needed, one line, in inline code (`SE = sd / sqrt(n)`). No `$`. No em or en dashes. No emojis.
- One card per section id. If a section covers several methods (e.g. distributions), list each as one bullet; still
  keep the card short. A small markdown table is fine when it compresses (e.g. which test for which data).
- "Next question" follows a logical chain (usually the order in plan.py SECTIONS; skip around when the logic needs it).
  The last card of a tab ends with a link to the cheat sheet of that tab.

## Per tab
- **stats**: question, methods, use, watch out, next question. Tiny numeric examples (5 to 10 values). For tests,
  say what is compared ("are the averages of two groups different?") and give the scipy call in one inline code span.
- **ai**: the chain of WHY each model was invented: linear regression (predict a number) -> logistic (yes/no) ->
  the world is not a straight line (trees) -> one tree overfits (random forest) -> learn from mistakes (boosting)
  -> ... -> neural networks -> embeddings -> attention -> transformers -> LLMs -> RAG -> agents -> evaluation.
  Each card: the problem the previous method could not solve, the idea in 2 to 4 lines, a tiny example, limits.
- **algo**: one card per trick or pattern: **Problem:** (tiny example input and output), **Signal:** the words in a
  problem that point to this trick, **Trick:** 1 to 3 lines, a Python template of at most 10 lines (run it to check),
  **Cost:** time and space, **Practice:** 2 or 3 LeetCode links (https://leetcode.com/problems/<slug>/),
  **Next:**. The `algo-recognize` card is a compact table: signal -> trick -> link.
- **sql**: **Question:** on a tiny table shown in markdown (3 to 5 rows), the **Query** (short, in a ```sql block),
  the **Result** (small table; run it with Python sqlite3 to check), **Watch out:**, **Next question:**.

## Output
Overwrite `site/content/en/<tab>.json` with {"title": ..., "intro": "2 lines max", "sections": [...]} keeping all
section ids from plan.py in order. Validate the JSON, check every `#id` link exists in plan.py SECTIONS (any tab),
and report briefly.
