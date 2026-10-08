"""Shared start for the SQL exam notebooks of days 1 to 10 (builders sql_01.py ... sql_10.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_product_tables import CHINOOK_DOC, CHINOOK_SETUP, PRODUCT_DOC, PRODUCT_SETUP

LIST_TABLES = ('print("tables:", ", ".join(r[0] for r in db.execute(\n'
               '    "SELECT name FROM sqlite_master WHERE type = \'table\' ORDER BY name")))')


def start(day, intro=""):
    ex = Exam(day, "sql", intro=intro)
    ex.text("## Tables\n\n" + CHINOOK_DOC + "\n\n" + PRODUCT_DOC +
            "\n\nThe notebook uses SQLite (built into Python and Colab). Write standard SQL; the solutions note "
            "where PostgreSQL differs. Run a query with `run(\"\"\"SELECT ...\"\"\")`.")
    ex.setup(CHINOOK_SETUP + "\n\n" + PRODUCT_SETUP + "\n\n" + LIST_TABLES, data=True)
    return ex


def nrows(ex, q):
    """Number of rows a query returns (used to write 'Expected: N rows' in prompts)."""
    return len(ex.db.execute(q).fetchall())


def val(ex, q):
    """First value of the first row."""
    return ex.db.execute(q).fetchone()[0]
