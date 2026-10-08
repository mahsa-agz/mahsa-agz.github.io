"""Builder helpers for the exam notebooks (exam_prep/day_NN/{1_algorithms,2_sql,3_stats,4_ai}.ipynb).

Usage (one builder per area and day range, e.g. algo_01_10.py):

    from libx import Exam
    ex = Exam(day=3, area="algorithms")             # header, rules and handbook link are automatic
    ex.setup(extra_code)                            # optional; check()/run()/data loader are added automatically
    ex.q("Same letters?", minutes=10, level="easy",
         prompt="...", stub="def is_anagram(s, t):\\n    pass", tests="check(is_anagram, [(('ab','ba'), True)])",
         hint1="Signal: ... Pattern: hashing", hint2="1. ... 2. ...",
         solution="def is_anagram(s, t): ...", why="...", complexity="O(n) time, O(1) space",
         mistakes="...", learn=["algo-hashing"], source=("LeetCode 242", "https://leetcode.com/problems/valid-anagram/"))
    ex.save()

kind="python" (default): `solution` + `tests` are executed at build time and every line must print PASS.
kind="sql": `solution` is a query run on the notebook's sqlite db (`ex.db`); its result table is shown.
kind="text": the solution is markdown (model answer); the learner writes in an empty markdown cell.
Any python `solution` may print values: put the expected output in a comment; build output is checked by the agent.
"""
import base64
import contextlib
import copy
import io
import os
import re
import sqlite3
import sys
import nbformat as nbf

HERE = os.path.dirname(os.path.abspath(__file__))
LEARN = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.join(LEARN, "exam_prep")
IMAGES = [os.path.join(ROOT, "images"), os.path.join(LEARN, "30_day_plan", "images")]
AREAS = {"algorithms": "1_algorithms", "sql": "2_sql", "stats": "3_stats", "ai": "4_ai"}
TITLES = {"algorithms": "Algorithms", "sql": "SQL", "stats": "Statistics, A/B testing and product", "ai": "AI and ML"}
NEXT = {"algorithms": "sql", "sql": "stats", "stats": "ai"}
_URL_FILE = os.path.join(HERE, "site_url.txt")
SITE = open(_URL_FILE).read().strip() if os.path.exists(_URL_FILE) else "HANDBOOK_URL"
COLAB = "https://colab.research.google.com/github/mahsa-agz/mahsa-agz.github.io/blob/main/ds-handbook/"
BADGE = "https://colab.research.google.com/assets/colab-badge.svg"

RULES = {
    "algorithms": "Name the pattern before you code. Stuck 15 min: open Hint 1. Stuck 25 min: Hint 2, then the "
                  "solution. Say the time and space complexity out loud. Re-type the solution from memory if you "
                  "needed it.",
    "sql": "Read the tables first (columns, one row = what?). Write the query in your head in the order FROM, WHERE, "
           "GROUP BY, HAVING, SELECT, ORDER BY. Check the result for duplicates and NULLs before you open the solution.",
    "stats": "Answer in two layers: the number (code) and one plain sentence a product manager understands. "
             "Name the method and its assumptions before computing.",
    "ai": "Answer concept questions out loud in 60 to 90 seconds before opening the solution: definition, why it "
          "matters, one example, one trade-off.",
}

CHECK_CODE = '''import copy

def check(fn, cases, key=None):
    """Runs fn on each (args, expected) case and prints PASS or FAIL. key: normalise outputs (e.g. sorted)."""
    ok = 0
    for args, want in cases:
        args = args if isinstance(args, tuple) else (args,)
        try:
            got = fn(*copy.deepcopy(args))
        except Exception as e:
            got = "error: " + repr(e)
        good = (key(got) == key(want)) if (key and not isinstance(got, str)) else got == want
        ok += good
        shown = ", ".join(repr(a) for a in args)
        print(("PASS " if good else "FAIL ") + f"{fn.__name__}({shown}) -> {got!r}" + ("" if good else f"   expected {want!r}"))
    print(f"{ok}/{len(cases)} passed")'''

SQL_CODE = '''import sqlite3
import pandas as pd

def run(q, con=None):
    """Runs a query and shows the result as a table (SELECT / WITH); other statements just run."""
    con = con or db
    if not q.strip():
        print("Write your query between the triple quotes, then run the cell.")
        return None
    if q.strip().lower().startswith(("select", "with")):
        return pd.read_sql_query(q, con)
    con.executescript(q)
    print("done")'''

DATA_CODE = '''# Finds the data folder (local copy of the repository, or /content/data in Colab) and downloads a missing file
# from the ds-handbook repository on GitHub (or from its original source).
import os, sys, urllib.request

RAW = "https://raw.githubusercontent.com/mahsa-agz/mahsa-agz.github.io/main/ds-handbook/exam_prep/data/"

def _find_data():
    if "google.colab" in sys.modules:
        os.makedirs("/content/data", exist_ok=True)
        return "/content/data"
    for p in ("../data", "data", "exam_prep/data"):
        if os.path.isdir(p):
            return p
    os.makedirs("data", exist_ok=True)
    return "data"

DATA = _find_data()
print("data folder:", DATA)

def data_path(name, url=None):
    """Local path of a data file; downloads it from the repository (or from url) if it is not there yet."""
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        for source in (RAW + name, url):
            if not source:
                continue
            try:
                print("downloading", name)
                urllib.request.urlretrieve(source, path)
                break
            except Exception as e:
                print("  could not download from", source, "->", e)
    return path'''

_IMG = re.compile(r'!\[([^\]]*)\]\(img:([\w.-]+\.png)\)')


def md(s):
    return ("md", s.strip())


def code(s):
    return ("code", s.strip())


def details(summary, body):
    return f"<details><summary><b>{summary}</b></summary>\n\n{body.strip()}\n\n</details>"


def learn_links(ids):
    if not ids:
        return ""
    return "**Learn more:** " + ", ".join(f"[{i}]({SITE}#{i})" for i in ids)


def _md_table(cols, rows, limit=12):
    rows = list(rows)
    head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols)
    body = "".join("\n| " + " | ".join("NULL" if v is None else str(v) for v in r) + " |" for r in rows[:limit])
    more = f"\n\n({len(rows)} rows, first {limit} shown)" if len(rows) > limit else ""
    return head + body + more


def _embed(text):
    """img:name.png references -> inline base64 (Colab shows data URIs, not attachments)."""
    def sub(m):
        for folder in IMAGES:
            p = os.path.join(folder, m.group(2))
            if os.path.exists(p):
                data = base64.b64encode(open(p, "rb").read()).decode()
                return f"![{m.group(1)}](data:image/png;base64,{data})"
        raise FileNotFoundError(m.group(2))
    return _IMG.sub(sub, text)


class Exam:
    def __init__(self, day, area, title=None, intro=""):
        assert area in AREAS, area
        sys.path.insert(0, HERE)
        from plan import LEVEL, MOCK_DAYS
        self.day, self.area = day, area
        self.level = LEVEL[day]
        self.mock = day in MOCK_DAYS
        self.title = title or (f"Day {day}: {TITLES[area]}" + (" (mock exam)" if self.mock else f" ({self.level})"))
        self.intro = intro
        self.cells, self.rows, self.n = [], [], 0
        self.ns = {}
        self.db = sqlite3.connect(":memory:")
        self.ns["db"] = self.db
        self.workdir = os.path.join(ROOT, f"day_{day:02d}")
        os.makedirs(self.workdir, exist_ok=True)
        self._setup_done = False

    # ------------------------------------------------------------------ setup
    def setup(self, extra="", data=False):
        """Adds the setup cell (check / run helpers, data loader when data=True) and runs it at build time."""
        parts = [CHECK_CODE] if self.area == "algorithms" else []
        if self.area == "sql":
            parts.append(SQL_CODE)
        if data:
            parts.append(DATA_CODE)
        if self.area == "sql":
            parts.append("db = sqlite3.connect(':memory:')")
        if extra:
            parts.append(extra.strip())
        src = "\n\n".join(parts)
        self.cells.append(md("## Setup\n\nRun this cell once before the questions."))
        self.cells.append(code(src))
        cwd = os.getcwd()
        os.chdir(self.workdir)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(src, self.ns)
        finally:
            os.chdir(cwd)
        if "db" in self.ns:
            self.db = self.ns["db"]
        self._setup_done = True

    def text(self, s):
        self.cells.append(md(s))

    def figure(self, name, caption=""):
        self.cells.append(md(f"![{name}](img:{name})" + (f"\n\n*{caption}*" if caption else "")))

    # ------------------------------------------------------------------ questions
    def q(self, title, prompt, hint1, hint2, solution, why, minutes=10, level=None, kind="python",
          stub=None, tests="", complexity="", mistakes="", learn=(), source=None, figure=None, review=False):
        if not self._setup_done:
            self.setup()
        self.n += 1
        level = level or self.level
        tag = " (review)" if review else ""
        src_line = f"\n\n*Source: [{source[0]}]({source[1]})*" if source else ""
        self.rows.append((self.n, title + tag, level, minutes))
        self.cells.append(md(f"---\n### Q{self.n}. {title}{tag}\n\n*{level}, about {minutes} min*\n\n{prompt}{src_line}"))
        if figure:
            self.figure(figure)
        if kind == "python":
            cell = (stub or "# your code here\n").rstrip()
            if tests:
                cell += "\n\n# tests\n" + tests.strip()
            self.cells.append(code(cell))
        elif kind == "sql":
            self.cells.append(code(stub or 'run("""\n\n""")'))
        else:
            self.cells.append(md("*Your answer (double-click to write):*"))
        self.cells.append(md(details("Hint 1", hint1)))
        self.cells.append(md(details("Hint 2", hint2)))
        body = self._run_solution(kind, solution, tests)
        extra = []
        if complexity:
            extra.append(f"**Complexity:** {complexity}")
        if mistakes:
            extra.append(f"**Common mistakes:** {mistakes}")
        links = learn_links(list(learn))
        if links:
            extra.append(links)
        self.cells.append(md(details("Solution", body + f"\n\n**Why:** {why}\n\n" + "\n\n".join(extra))))

    def _run_solution(self, kind, solution, tests):
        if kind == "text":
            return solution.strip()
        cwd = os.getcwd()
        os.chdir(self.workdir)
        try:
            if kind == "sql":
                q = solution.strip()
                if q.lower().startswith(("select", "with")):
                    cur = self.db.execute(q)
                    result = _md_table([d[0] for d in cur.description], cur.fetchall())
                    return f"```sql\n{q}\n```\n\nResult:\n\n{result}"
                self.db.executescript(q)
                return f"```sql\n{q}\n```"
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                exec(solution, self.ns)
                if tests:
                    exec(tests, self.ns)
            printed = out.getvalue()
            if tests and ("FAIL" in printed or "PASS" not in printed):
                raise AssertionError(f"Day {self.day} {self.area} Q{self.n}: tests do not pass:\n{printed}")
            self.last_output = printed
            return f"```python\n{solution.strip()}\n```"
        finally:
            os.chdir(cwd)

    # ------------------------------------------------------------------ save
    def save(self):
        table = "| # | Question | Level | Minutes |\n|---|---|---|---|\n" + "\n".join(
            f"| Q{n} | {t} | {lvl} | {m} |" for n, t, lvl, m in self.rows)
        total = sum(r[3] for r in self.rows)
        tab = {"algorithms": "algo", "sql": "sql", "stats": "stats", "ai": "ai"}[self.area]
        intro = f"{self.intro}\n\n" if self.intro else ""
        here = f"exam_prep/day_{self.day:02d}/"
        badge = f"[![Open in Colab]({BADGE})]({COLAB}{here}{AREAS[self.area]}.ipynb)"
        head = [md(f"{badge}\n\n# {self.title}\n\n{intro}**How to work:** {RULES[self.area]}\n\n"
                   f"**Today ({total} min):**\n\n{table}\n\n**Handbook:** [{TITLES[self.area]}]({SITE}#{tab}), "
                   f"[cheat sheets]({SITE}#cheat)")]
        nxt = NEXT.get(self.area)
        foot = ("---\n## Redo list\n\nWrite down every question you got wrong, solved only after Hint 2, or finished "
                "over time. Solve it again from scratch 3 days and 7 days later.\n\n" +
                (f"**Next:** [{TITLES[nxt]}]({COLAB}{here}{AREAS[nxt]}.ipynb)" if nxt else "**Done for today.** "
                 f"Finish with the [theory flashcards for day {self.day}]({SITE}#day-{self.day})."))
        cells = head + self.cells + [md(foot)]
        nb = nbf.v4.new_notebook()
        nb.cells = [nbf.v4.new_markdown_cell(_embed(t)) if k == "md" else nbf.v4.new_code_cell(t) for k, t in cells]
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        nb.metadata["colab"] = {"provenance": []}
        path = os.path.join(self.workdir, AREAS[self.area] + ".ipynb")
        nbf.write(nb, path)
        print("wrote", path)
        return path
