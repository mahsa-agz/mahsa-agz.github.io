"""Case 1 (The missing revenue), day 1: first look at the evidence. SELECT, LIMIT, ORDER BY, WHERE, LIKE, DISTINCT."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libcase import Case

SETUP = '''# Setup: loads the real sales data of a UK online gift shop (Dec 2010 to Dec 2011, 541,909 rows) into a
# small SQL database, and gives you run(query) to ask it questions. Run this cell once.
import os, sqlite3, urllib.request
import pandas as pd

URL = "https://raw.githubusercontent.com/mahsa-agz/mahsa-agz.github.io/main/ds-handbook/exam_prep/data/online_retail.csv.gz"
path = next((p for p in ["../../exam_prep/data/online_retail.csv.gz", "../data/online_retail.csv.gz",
                         "online_retail.csv.gz"] if os.path.exists(p)), None)
if path is None:
    print("downloading the data (about 7 MB)...")
    path = "online_retail.csv.gz"
    urllib.request.urlretrieve(URL, path)

df = pd.read_csv(path, dtype={"InvoiceNo": str, "StockCode": str})
df.columns = ["invoice_no", "stock_code", "description", "quantity", "invoice_date", "unit_price",
              "customer_id", "country"]
df["customer_id"] = df["customer_id"].astype("Int64")
db = sqlite3.connect(":memory:")
df.to_sql("sales", db, index=False)

def run(query):
    """Runs a SQL query on the database and shows the result as a table."""
    if not query.strip():
        print("Write your query between the triple quotes, then run the cell.")
        return None
    return pd.read_sql_query(query, db)

print("Ready: table sales with", len(df), "rows")'''

c = Case("case1_missing_revenue", 1, "Case 1, day 1: The missing revenue", 60)
c.setup(SETUP, "## Setup\n\nRun this cell once. It loads the data and gives you `run(...)`.")

# numbers for the story, computed from the real data
rev = c.query("""SELECT substr(invoice_date, 1, 7) AS month, ROUND(SUM(quantity * unit_price)) AS revenue
                 FROM sales GROUP BY month""").set_index("month")["revenue"]
nov, dec = int(rev["2011-11"]), int(rev["2011-12"])
drop = round(100 * (1 - dec / nov))

INTRO = f"""## The briefing

You just started as the data analyst at a small UK online shop that sells gifts and home decoration.
On Monday morning the CEO sends you this message:

> "I just saw the dashboard. **December revenue is {dec:,} pounds. November was {nov:,}.** That is a
> **{drop}% drop**. Is the business collapsing? I need an answer by Friday."

Your job this week: find out what really happened, using SQL on the shop's sales data. Every day you learn a few
new SQL tools and use them to follow the next clue. Today you only **look at the evidence**: what is in the data,
which period it covers, and what looks strange.

**How each step works:** read the short explanation, write your query in the empty cell, then open the Hint if you
are stuck and the Answer to check. Try first, look second."""

c.text(INTRO)

c.step("What does one row mean?",
       """`SELECT` chooses columns, `FROM` chooses the table, and `LIMIT` shows only the first few rows. `*` means
"all columns". This is always the first query on new data: you cannot analyse what you have not looked at.

```sql
SELECT * FROM sales LIMIT 3;
```""",
       "Show the first **10 rows** of the `sales` table. Then answer for yourself: what does **one row** describe? "
       "An order, a customer, or something else?",
       "`SELECT * FROM sales LIMIT 10`",
       "SELECT * FROM sales LIMIT 10",
       "Several rows share the same `invoice_no` (536365 appears many times). So one row is **one product line "
       "inside an invoice**, not one order. Counting rows would count product lines, not orders: an important "
       "detail for every number you report later.",
       clue="One row = one product line of an invoice. An invoice (order) has many rows.")

c.step("Which period does the data cover?",
       """`ORDER BY column` sorts the result: `ASC` (smallest first, the default) or `DESC` (largest first).
Together with `LIMIT 1` it finds the first or the last value. Dates stored as text in the form
`YYYY-MM-DD HH:MM:SS` sort correctly, because the biggest unit comes first.

```sql
SELECT invoice_date FROM sales ORDER BY invoice_date DESC LIMIT 1;  -- the latest date
```""",
       "Find the **first** and the **last** `invoice_date` in the data. Look closely at the last one. What does it "
       "mean for the CEO's December number?",
       "Two queries: `ORDER BY invoice_date ASC LIMIT 1` and `ORDER BY invoice_date DESC LIMIT 1`.",
       "SELECT invoice_date FROM sales ORDER BY invoice_date DESC LIMIT 1",
       "The first date is 2010-12-01 (run the ASC version too). The last is **2011-12-09**: the data stops on the 9th "
       "of December. So the dashboard compares a **full November** (30 days) with **only 9 days of December**. Part of "
       "the \"drop\" is simply missing days.",
       clue="The data ends on 2011-12-09. December has only 9 days of data, November has 30.")

c.step("Look only at the days that matter",
       """`WHERE` keeps only the rows that match a condition. With text dates you can compare ranges:
`invoice_date >= '2011-12-01'` keeps December. `AND` combines conditions, and `COUNT(*)` counts the rows that are
left (we use counting properly tomorrow).

```sql
SELECT COUNT(*) FROM sales WHERE country = 'France';
```""",
       "How many rows (product lines) are there in **December 2011**? And in the **first 9 days of November 2011**?",
       "`WHERE invoice_date >= '2011-12-01'` for December. For November use two conditions with `AND`: "
       "from `'2011-11-01'` and before `'2011-11-10'`.",
       """SELECT
  (SELECT COUNT(*) FROM sales WHERE invoice_date >= '2011-12-01') AS dec_rows,
  (SELECT COUNT(*) FROM sales WHERE invoice_date >= '2011-11-01' AND invoice_date < '2011-11-10') AS nov_1_to_9_rows""",
       "The first 9 days of December have even **more** product lines (25,525) than the first 9 days of November "
       "(22,170). That already hints that business did **not** collapse. (The answer combines two counts in one row with small subqueries; "
       "two separate queries are just as good.) Note `< '2011-11-10'`: \"before the 10th\" includes the whole 9th, "
       "even its afternoon.",
       clue="Comparing equal periods (1 to 9 November vs 1 to 9 December), December is even busier.")

c.step("Strange rows: negative quantities",
       """Real data is messy. `WHERE quantity < 0` finds lines with a negative quantity. `LIKE` matches text
patterns: `%` means "any characters", so `invoice_no LIKE 'C%'` finds invoice numbers that start with C.

```sql
SELECT * FROM sales WHERE description LIKE '%HEART%' LIMIT 5;
```""",
       "Show 10 rows with a **negative quantity**. What do their invoice numbers have in common? Then count how many "
       "rows have an `invoice_no` that **starts with 'C'**.",
       "`WHERE quantity < 0 LIMIT 10`, then `SELECT COUNT(*) ... WHERE invoice_no LIKE 'C%'`.",
       "SELECT COUNT(*) AS cancellation_rows FROM sales WHERE invoice_no LIKE 'C%'",
       "Most negative lines have invoice numbers starting with **C**: they are **cancellations** (returned or cancelled "
       "items). They are stored as separate rows with a negative quantity, so they reduce revenue when you sum. The "
       "CEO's dashboard mixes sales and cancellations; we will separate them later in the week.",
       clue="About 9,300 rows are cancellations (invoice_no starts with C, negative quantity).")

c.step("The biggest single line",
       """`ORDER BY` can sort by a calculation, not only by a column: `ORDER BY quantity * unit_price DESC` puts the most
valuable lines first. You can also give the calculation a name with `AS` and show it.""",
       "Find the **5 most valuable product lines** (`quantity * unit_price`) in the whole data set. Show "
       "`invoice_no`, `invoice_date`, `description`, `quantity` and the line value. Does anything look suspicious?",
       "`SELECT ..., quantity * unit_price AS line_value FROM sales ORDER BY line_value DESC LIMIT 5`",
       """SELECT invoice_no, invoice_date, description, quantity, unit_price,
       ROUND(quantity * unit_price, 2) AS line_value
FROM sales
ORDER BY line_value DESC
LIMIT 5""",
       "The most valuable line in the whole year is **80,995 \"PAPER CRAFT , LITTLE BIRDIE\" on 2011-12-09**, worth "
       "about 168,000 pounds: one line that is a big part of the 9 days of December. One order of 80,995 paper birds "
       "is unusual. Remember it: tomorrow we check whether it was really sold, or cancelled.",
       clue="The single biggest line of the year (80,995 paper birds, about 168,000 pounds) is on the last day, 2011-12-09.")

c.step("Where do customers come from?",
       """`DISTINCT` removes duplicate values: `SELECT DISTINCT country FROM sales` lists every country once.
`COUNT(DISTINCT column)` counts the different values.""",
       "How many **different countries** buy from the shop? List them in alphabetical order.",
       "`SELECT DISTINCT country ... ORDER BY country`, and `SELECT COUNT(DISTINCT country) FROM sales`.",
       "SELECT COUNT(DISTINCT country) AS n_countries FROM sales",
       "The shop sells to 38 countries (one value is \"Unspecified\", a data quality issue). Most rows are from the "
       "United Kingdom. When a total moves, a change in **one big segment** (one country, one customer) is often the "
       "cause: we will break revenue down by country later.")

c.step("Report to the CEO (in words)",
       """A good update is short: **what you found, what it means, what you do next.** No SQL in the message.""",
       "Write **two or three sentences** to the CEO about what you know after today.",
       "Use your clues: the period of the data, the fair comparison, and the strange rows.",
       "\"The 70% drop is mostly because the data for December only covers the first 9 days; compared with the same 9 "
       "days of November, the shop was even busier. The December figure also includes one unusually large order and "
       "some cancellations, which I am checking next. I will send a like-for-like revenue comparison tomorrow.\"",
       "It answers the panic first (not collapsing), says what is still unknown, and promises the next step. "
       "This is exactly what an examiner checks in a product or analytics case: a clear, calm conclusion, not just "
       "numbers.", kind="text")

OUTRO = """**Tomorrow (day 2):** you learn `GROUP BY` and `SUM` to compute revenue per day and per country, compare
equal periods properly, and find out what happened to the 80,995 paper birds.

**How it's tested:** examiners give you a table and a vague business question. They watch whether you first check
what one row means and which period the data covers, before computing anything. That habit alone avoids the most
common wrong answers.

**Optional practice (about 10 minutes, auto-graded):** LeetCode SQL problems that use only today's tools:
[595 Big Countries](https://leetcode.com/problems/big-countries/),
[1757 Recyclable and Low Fat Products](https://leetcode.com/problems/recyclable-and-low-fat-products/),
[584 Find Customer Referee](https://leetcode.com/problems/find-customer-referee/) (watch out for NULL).

**Just for fun:** [SQL Murder Mystery](https://mystery.knightlab.com/) is a free detective game in the browser that
uses the same tools."""

c.save("", OUTRO)
