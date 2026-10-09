"""Builder for project ("case") notebooks: learn by solving one story, step by step.

Every step: a short concept (what and why, tiny example) -> your turn (empty cell) -> Hint -> Answer (query run on the
real data at build time, result table shown, plus why) -> optional clue for the case board.
Notebooks land in ds-handbook/projects/<case>/day_NN.ipynb and open in Colab from GitHub.
"""
import io
import contextlib
import os
import sqlite3
import sys
import nbformat as nbf
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
HANDBOOK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "exam30"))
from libx import details, _md_table, SITE, BADGE  # noqa: E402

COLAB = "https://colab.research.google.com/github/mahsa-agz/mahsa-agz.github.io/blob/main/ds-handbook/"
RAW = "https://raw.githubusercontent.com/mahsa-agz/mahsa-agz.github.io/main/ds-handbook/exam_prep/data/"


def md(s):
    return ("md", s.strip())


def code(s):
    return ("code", s.strip())


class Case:
    def __init__(self, folder, day, title, minutes):
        self.folder, self.day, self.title, self.minutes = folder, day, title, minutes
        self.cells, self.n, self.clues = [], 0, []
        self.db = None

    def text(self, s):
        self.cells.append(md(s))

    def setup(self, src, note):
        """Setup cell shown to the learner; the same code runs here so answers use identical data."""
        self.cells += [md(note), code(src)]
        ns = {}
        cwd = os.getcwd()
        os.chdir(os.path.join(HANDBOOK, "exam_prep", "day_01"))     # so ../data/ resolves like in the notebooks
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(src, ns)
        finally:
            os.chdir(cwd)
        self.db = ns["db"]

    def query(self, sql):
        return pd.read_sql_query(sql, self.db)

    def step(self, title, concept, task, hint, answer, why, clue=None, kind="sql"):
        self.n += 1
        self.cells.append(md(f"---\n## Step {self.n}: {title}\n\n{concept}"))
        self.cells.append(md(f"### Your turn\n\n{task}"))
        if kind == "sql":
            self.cells.append(code('run("""\n\n""")'))
        else:
            self.cells.append(md("*Your answer (double-click to write):*"))
        self.cells.append(md(details("Hint", hint)))
        if kind == "sql":
            cur = self.db.execute(answer)
            table = _md_table([d[0] for d in cur.description], cur.fetchall(), limit=10)
            body = f"```sql\n{answer.strip()}\n```\n\nResult:\n\n{table}\n\n**Why:** {why}"
        else:
            body = f"{answer.strip()}\n\n**Why:** {why}"
        if clue:
            body += f"\n\n> **Clue found:** {clue}"
            self.clues.append(clue)
        self.cells.append(md(details("Answer", body)))

    def save(self, intro_top, outro):
        rel = f"projects/{self.folder}/day_{self.day:02d}.ipynb"
        badge = f"[![Open in Colab]({BADGE})]({COLAB}{rel})"
        board = "\n".join(f"{i}. {c}" for i, c in enumerate(self.clues, 1))
        head = [md(f"{badge}\n\n# {self.title}\n\n*About {self.minutes} minutes.*\n\n{intro_top}")]
        tail = [md(f"---\n## Case board after day {self.day}\n\n{board}\n\n{outro}")]
        nb = nbf.v4.new_notebook()
        nb.cells = [nbf.v4.new_markdown_cell(t) if k == "md" else nbf.v4.new_code_cell(t)
                    for k, t in head + self.cells + tail]
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        path = os.path.join(HANDBOOK, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        nbf.write(nb, path)
        print("wrote", path)
        return path
