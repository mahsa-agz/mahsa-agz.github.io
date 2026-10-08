"""Writes exam_prep/00_start_here.ipynb (how to use the plan). Run: python start_here.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbformat as nbf
from libx import ROOT, SITE, COLAB, BADGE
from plan import ALGO, LEVEL, MOCK_DAYS


def links(d):
    base = f"{COLAB}exam_prep/day_{d:02d}/"
    return " · ".join(f"[{name}]({base}{f}.ipynb)" for name, f in
                      (("Algorithms", "1_algorithms"), ("SQL", "2_sql"), ("Stats", "3_stats"), ("AI", "4_ai")))


rows = "\n".join(
    f"| {d} | {LEVEL[d]}{' (mock)' if d in MOCK_DAYS else ''} | {links(d)} | [flashcards]({SITE}#day-{d}) |"
    for d in range(1, 31))

TEXT = f"""[![Open in Colab]({BADGE})]({COLAB}exam_prep/00_start_here.ipynb)

# Start here: 30-day data science exam plan

**Handbook (explanations, cheat sheets, flashcards):** {SITE}

## How to open the notebooks
Click a link in the table below: the notebook opens in Google Colab straight from GitHub, nothing to upload.
Run the **Setup** cell first; it downloads the data files the notebook needs. To keep your answers, use
**File > Save a copy in Drive** in Colab (otherwise Colab does not keep your edits).

## Every day (about 2 hours 15 minutes)
| Order | What | Time |
|---|---|---|
| 1 | Redo the questions on your redo list that are due (3 and 7 days old) | 10 min |
| 2 | Algorithms notebook: 3 problems from different patterns | 50 to 55 min |
| 3 | SQL notebook: 5 queries | 20 to 25 min |
| 4 | Statistics notebook: 4 questions (compute + explain to a PM) | 20 to 25 min |
| 5 | AI notebook: 5 questions (concepts + hands-on) | 20 to 25 min |
| 6 | Theory flashcards for the day (handbook), out loud | 10 min |

## Rules that make it work
- **Mixed practice:** every day mixes patterns and topics. Name the pattern yourself before you open Hint 1:
  recognising the method is half of the exam.
- **Try before you look:** stuck 15 minutes, open Hint 1; stuck 25 minutes, open Hint 2 and then the solution.
  Re-type the solution from memory afterwards.
- **Redo list:** wrong answer, Hint 2 used, or over time: write it down and solve it again after 3 and 7 days.
- **Say it out loud:** complexity for code, one plain sentence for every statistic, 60 to 90 seconds for concepts.
- **Protect your energy:** algorithms first while you are fresh, short breaks between notebooks, stop at the time
  limits. Doing every day matters more than doing one long day.
- **Mock days** (7, 14, 21, 28): one timer per notebook, no hints until time is up. Day 29 is a full exam loop,
  day 30 is light: redo your list and rest.

## The 30 days
| Day | Level | Notebooks (open in Colab) | Theory |
|---|---|---|---|
{rows}
"""

nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_markdown_cell(TEXT)]
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
os.makedirs(ROOT, exist_ok=True)
nbf.write(nb, os.path.join(ROOT, "00_start_here.ipynb"))
print("wrote", os.path.join(ROOT, "00_start_here.ipynb"))
