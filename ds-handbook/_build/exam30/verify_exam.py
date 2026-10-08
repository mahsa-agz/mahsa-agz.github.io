"""Checks exam notebooks: python verify_exam.py [filter]   e.g. day_03   or   2_sql
- runs every notebook as the learner gets it (stubs): no cell may raise an error
- structure: each question has Hint 1, Hint 2, Solution; no em/en dashes, no emojis, no $...$ math
- every handbook link points at an id that exists in plan.py SECTIONS"""
import glob
import os
import re
import sys
import nbformat
from nbclient import NotebookClient

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plan import SECTIONS
from libx import ROOT

sys.stdout.reconfigure(encoding="utf-8")
IDS = {f"{tab}-{s}" for tab, ss in SECTIONS.items() for s in ss} | {"plan", "algo", "sql", "stats", "ai", "cheat", "qa", "resources"} | {f"day-{d}" for d in range(1, 31)}
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
pat = sys.argv[1] if len(sys.argv) > 1 else ""
bad = 0
for path in sorted(glob.glob(os.path.join(ROOT, "day_*", "*.ipynb"))):
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    if pat not in rel:
        continue
    nb = nbformat.read(path, 4)
    issues = []
    text = "\n".join(c.source for c in nb.cells)
    nq = len(re.findall(r"^### Q\d+\.", text, re.M))
    for k in ("Hint 1", "Hint 2", "Solution"):
        if text.count(f"<summary><b>{k}</b></summary>") != nq:
            issues.append(f"{k} count != {nq} questions")
    if "—" in text or "–" in text:
        issues.append("em/en dash")
    if EMOJI.search(text):
        issues.append("emoji")
    for c in nb.cells:
        if c.cell_type == "markdown" and re.search(r"(?<![\\\w])\$[^$\n]+\$", re.sub(r"data:image[^)]*\)", "", c.source)):
            issues.append("$...$ math in markdown")
            break
    for ref in re.findall(r"artifact/[A-Za-z0-9]+#([a-z0-9-]+)\)", text):
        if ref not in IDS:
            issues.append(f"bad handbook id #{ref}")
    try:
        NotebookClient(nb, timeout=300, kernel_name="python3",
                       resources={"metadata": {"path": os.path.dirname(path)}}).execute()
    except Exception as e:
        issues.append("EXEC: " + str(e).strip().splitlines()[-1][:200])
    status = "OK " if not issues else "BAD"
    bad += bool(issues)
    print(f"{status} {rel}: {nq} questions")
    for i in issues:
        print("     ", i)
print("ALL GOOD" if not bad else f"{bad} notebook(s) need fixing")
