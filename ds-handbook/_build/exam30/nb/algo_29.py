"""Day 29 algorithms: one full exam round. Custom data-processing problem (sessionize a click log),
First Missing Positive, Maximum Profit in Job Scheduling."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from _algo_hard_common import BIG, lc, compute

INTRO = """**Full exam round (70 minutes, one timer).** Treat this notebook as the real coding exam.
For every question, work through the same five steps and say them out loud (record yourself if you can):

1. **Clarify** (2 to 3 min): restate the problem, ask about input size, edge cases, duplicates, sorted or not. Write
   your assumptions as a comment at the top of the cell.
2. **Examples**: work one small example by hand, including an edge case.
3. **Brute force first**: describe it and its complexity in one or two sentences, then say why it is too slow.
4. **Optimise and code**: name the pattern, code it cleanly, keep talking.
5. **Test**: run the given tests, add one test of your own, then state the final time and space complexity.

Do not open any hint until the 70 minutes are over. Afterwards, score yourself from 1 to 4 on each of: communication,
problem solving, code quality, testing. Anything below 3 goes into the mistake log with a note on what to change."""

ex = Exam(29, "algorithms", title="Day 29: Algorithms (full exam round)", intro=INTRO)

LOG = '''from datetime import datetime, timedelta

def make_click_log(seed=29, n_users=300):
    """MADE-UP click log of a video app: rows (user_id, ts, page), ts as "YYYY-MM-DD HH:MM:SS".
    Like real logs it is unsorted, has exact duplicate rows (client retries) and a few broken rows (None values)."""
    rng = random.Random(seed)
    pages = ["home", "search", "video", "profile", "upload", "settings", "live", "shop"]
    rows = []
    for u in range(1, n_users + 1):
        uid = f"u{u:04d}"
        t = datetime(2026, 10, 1) + timedelta(seconds=rng.randint(0, 6 * 3600))
        for _ in range(rng.randint(1, 8)):                    # visits of this user
            for _ in range(rng.randint(1, 15)):               # clicks inside one visit
                rows.append((uid, t.strftime("%Y-%m-%d %H:%M:%S"), rng.choice(pages)))
                if rng.random() < 0.02:
                    rows.append(rows[-1])                     # duplicate row (retry)
                t += timedelta(seconds=1800 if rng.random() < 0.03 else rng.randint(5, 600))
            t += timedelta(seconds=rng.randint(1801, 20 * 3600))   # a break of more than 30 minutes
    for _ in range(25):                                        # broken rows
        uid, ts, page = rng.choice(rows)
        rows.append((None, ts, page) if rng.random() < 0.5 else (uid, None, page))
    rng.shuffle(rows)
    return rows

click_log = make_click_log()
print(len(click_log), "rows, for example:", click_log[:3])'''

ex.setup(BIG + "\n\n" + LOG)

# ---------------------------------------------------------------- Q1 sessionize (custom)
SOL1 = '''from collections import defaultdict
from datetime import datetime, timedelta

def _clean(events):
    """Drops broken rows and exact duplicates."""
    return {row for row in events if row[0] and row[1]}

def sessionize_brute(events, gap_minutes=30):
    """For every event, scan ALL earlier events to find the previous event of the same user. O(n^2)."""
    rows = sorted(_clean(events))
    gap = timedelta(minutes=gap_minutes)
    out = []
    for i, (user, ts, page) in enumerate(rows):
        t, prev = datetime.fromisoformat(ts), None
        for j in range(i):                                    # the whole prefix, every time
            if rows[j][0] == user:
                prev = datetime.fromisoformat(rows[j][1])
        if prev is None or t - prev > gap:
            no = out[-1][1] + 1 if out and out[-1][0] == user else 1
            out.append([user, no, ts, ts, 1])
        else:
            out[-1][3] = ts
            out[-1][4] += 1
    return [tuple(x) for x in out]

def sessionize(events, gap_minutes=30):
    """Group by user, sort each user's events by time, one pass to cut sessions. O(n log n)."""
    by_user = defaultdict(list)
    for user, ts, page in _clean(events):
        by_user[user].append(datetime.fromisoformat(ts))
    gap = timedelta(minutes=gap_minutes)
    fmt = "%Y-%m-%d %H:%M:%S"
    out = []
    for user in sorted(by_user):
        times = sorted(by_user[user])
        no, start, count = 1, times[0], 1
        for prev, t in zip(times, times[1:]):
            if t - prev > gap:                    # strictly more than the gap: close the session
                out.append((user, no, start.strftime(fmt), prev.strftime(fmt), count))
                no, start, count = no + 1, t, 0
            count += 1
        out.append((user, no, start.strftime(fmt), times[-1].strftime(fmt), count))
    return out

rng = random.Random(2929)
users = sorted({r[0] for r in click_log if r[0]})
for _ in range(100):
    chosen = set(rng.sample(users, 3))                       # all rows of 3 random users + the broken rows
    small = [r for r in click_log if r[0] in chosen or r[0] is None or r[1] is None]
    gap = rng.choice([5, 30, 60])
    assert sessionize(small, gap) == sessionize_brute(small, gap)
print("stress test vs brute force: OK")          # prints: stress test vs brute force: OK

# Use it like a data scientist: a few session metrics on the made-up log
sessions = sessionize(click_log)
bounce = sum(s[4] == 1 for s in sessions) / len(sessions)
minutes = sorted((datetime.fromisoformat(s[3]) - datetime.fromisoformat(s[2])).total_seconds() / 60 for s in sessions)
mid = len(minutes) // 2
median = minutes[mid] if len(minutes) % 2 else (minutes[mid - 1] + minutes[mid]) / 2
print("sessions:", len(sessions))                          # prints: sessions: @N@
print("bounce rate:", round(bounce, 3))                    # prints: bounce rate: @B@
print("median session length (min):", round(median, 1))    # prints: median session length (min): @M@'''

N1 = compute(BIG, LOG, SOL1.split("rng = random.Random(2929)")[0], expr="len(sessionize(click_log))")
B1 = compute(BIG, LOG, SOL1, expr="round(bounce, 3)")
M1 = compute(BIG, LOG, SOL1, expr="round(median, 1)")
SOL1 = SOL1.replace("@N@", str(N1)).replace("@B@", str(B1)).replace("@M@", str(M1))
SUM1 = compute(BIG, LOG, SOL1, expr="(lambda r: (len(r), sum(s[4] for s in r), sum(s[4] == 1 for s in r)))(sessionize(click_log))")

TESTS1 = """D = "2026-10-01 "
check(sessionize, [
    # one user, a 50-minute break splits the visit in two
    ([("u1", D + "10:00:00", "home"), ("u1", D + "10:10:00", "video"), ("u1", D + "11:00:00", "home")],
     [("u1", 1, D + "10:00:00", D + "10:10:00", 2), ("u1", 2, D + "11:00:00", D + "11:00:00", 1)]),
    # unsorted input, two users, output sorted by user then session
    ([("u2", D + "09:05:00", "home"), ("u1", D + "09:20:00", "shop"), ("u2", D + "09:00:00", "live")],
     [("u1", 1, D + "09:20:00", D + "09:20:00", 1), ("u2", 1, D + "09:00:00", D + "09:05:00", 2)]),
    # exactly 30 minutes stays in the session, 30 minutes and 1 second does not
    ([("u1", D + "08:00:00", "a"), ("u1", D + "08:30:00", "b"), ("u1", D + "09:00:01", "c")],
     [("u1", 1, D + "08:00:00", D + "08:30:00", 2), ("u1", 2, D + "09:00:01", D + "09:00:01", 1)]),
    # an exact duplicate row counts once; a different page in the same second counts
    ([("u1", D + "12:00:00", "home"), ("u1", D + "12:00:00", "home"), ("u1", D + "12:00:00", "search")],
     [("u1", 1, D + "12:00:00", D + "12:00:00", 2)]),
    # broken rows are skipped
    ([(None, D + "12:00:00", "home"), ("u7", None, "home"), ("u7", D + "13:00:00", "home")],
     [("u7", 1, D + "13:00:00", D + "13:00:00", 1)]),
    # empty log
    ([], []),
    # a visit that crosses midnight
    ([("u3", "2026-10-01 23:50:00", "video"), ("u3", "2026-10-02 00:10:00", "video")],
     [("u3", 1, "2026-10-01 23:50:00", "2026-10-02 00:10:00", 2)]),
    # a custom gap of 5 minutes
    (([("u1", D + "10:00:00", "a"), ("u1", D + "10:06:00", "b")], 5),
     [("u1", 1, D + "10:00:00", D + "10:00:00", 1), ("u1", 2, D + "10:06:00", D + "10:06:00", 1)]),
])
# big test: the made-up click log from the setup cell.
# The check compares (number of sessions, total events, number of one-event sessions).
summary = lambda r: (len(r), sum(s[4] for s in r), sum(s[4] == 1 for s in r))
check_big(f"click_log ({len(click_log)} rows)", lambda: sessionize(click_log), @SUM@, key=summary, limit=1.0)""".replace(
    "@SUM@", repr(SUM1))

ex.q("Turn a raw click log into sessions", minutes=25, level="medium",
     prompt="""The setup cell created `click_log`, a **made-up** click log of a video app (about 11000 rows). Each row
is `(user_id, ts, page)` with `ts` a string like `"2026-10-01 14:03:59"`. Like a real log it is **unsorted**, has
**exact duplicate rows** (client retries) and a few **broken rows** where `user_id` or `ts` is `None`.

Write `sessionize(events, gap_minutes=30)` that groups each user's clicks into **sessions**:
1. Skip rows where `user_id` or `ts` is missing. Count exact duplicate rows once.
2. Within one user, events in time order belong to the same session while the time since the previous event is
   **at most** `gap_minutes`. A gap of **more than** `gap_minutes` starts a new session.
3. Return a list of tuples `(user_id, session_no, start_ts, end_ts, n_events)`, sorted by `user_id` then
   `session_no`. `session_no` starts at 1 for each user; `start_ts` and `end_ts` use the input format;
   `n_events` counts the (deduplicated) events in the session.

Example:
```
("u1", "2026-10-01 10:00:00", "home")
("u1", "2026-10-01 10:10:00", "video")
("u1", "2026-10-01 11:00:00", "home")
-> [("u1", 1, "2026-10-01 10:00:00", "2026-10-01 10:10:00", 2),
    ("u1", 2, "2026-10-01 11:00:00", "2026-10-01 11:00:00", 1)]
```
In a real exam, ask these questions first: Is the input sorted? What exactly is a duplicate? Is a gap of
exactly 30 minutes a new session? Can a session cross midnight? (Answers: no; same user, time and page; no; yes.)

After the tests pass, use your function: how many sessions are there, what share are one-click "bounces", and what
is the median session length in minutes?""",
     stub="def sessionize(events, gap_minutes=30):\n    pass",
     tests=TESTS1,
     hint1="Signal: per-entity event logs and \"cut when the gap is too large\". Pattern: **data processing: group "
           "by key, sort each group, one linear pass** (the same logic as SQL `LAG` + running `SUM` of a new-session "
           "flag).",
     hint2="""1. Clean: keep rows with both `user_id` and `ts`; put them in a set to drop exact duplicates.
2. Group: `by_user[user].append(datetime.fromisoformat(ts))`.
3. For each user (in sorted order), sort the times. Walk consecutive pairs: if `t - prev > gap`, close the current
   session (start, prev, count) and open a new one at `t`.
4. Do not forget to close the last session of each user. Format times back with `strftime`.""",
     solution=SOL1,
     why="""Sessions are defined per user and in time order, so the natural plan is group, sort, scan. Grouping is
O(n) with a dict, sorting all groups costs O(n log n) in total, and the scan is linear. The brute force looks for
each event's predecessor by scanning the whole log, which is O(n^2). Using a set for cleaning makes the duplicate
rule exact (same user, time and page) and keeps two different pages in the same second as two events. Parsing
timestamps into `datetime` makes the gap test and the midnight case correct; comparing the strings would also sort
correctly for this fixed format, but subtracting them would not work.

**Follow-ups the examiner may ask:**
- **SQL version**: `LAG(ts) OVER (PARTITION BY user_id ORDER BY ts)`, a flag `CASE WHEN ts - prev_ts > 30 min OR
  prev_ts IS NULL THEN 1 ELSE 0 END`, then `SUM(flag) OVER (PARTITION BY user_id ORDER BY ts)` as the session number.
- **pandas version**: `df.sort_values(["user_id", "ts"])`, `gap = df.groupby("user_id")["ts"].diff()`,
  `df["session_no"] = (gap.isna() | (gap > pd.Timedelta("30min"))).groupby(df["user_id"]).cumsum()`.
- **Streaming**: keep `last_seen[user]` and the open session per user; close a session when an event arrives more
  than 30 minutes later, or when a timer (watermark) passes `last_seen + 30 min`. Late events need a watermark delay.
- **Scale**: billions of rows: partition by `user_id` (map-reduce / Spark), then sort within each partition.
- Metric questions: bounce rate, median session length (why median and not mean?), sessions per user per day.""",
     complexity="Brute force: O(n^2). Group, sort, scan: O(n log n) time (the sorts), O(n) space.",
     mistakes="Sorting the whole log by time but forgetting to group by user (sessions of different users interleave). "
              "Using `>=` instead of `>` for the gap. Not closing the last session. Dropping the second event when two "
              "different pages share a second. Comparing times as strings with `-`. Counting duplicates twice.",
     learn=["algo-data-processing", "algo-hashing", "algo-sorting-intervals"])

# ---------------------------------------------------------------- Q2 First Missing Positive (41)
SOL2 = '''def first_missing_positive_brute(nums):
    """Try 1, 2, 3, ... and search the list each time. O(n^2)."""
    k = 1
    while k in nums:                      # `in` on a list is a linear scan
        k += 1
    return k

def first_missing_positive_set(nums):
    """O(n) time but O(n) extra space."""
    seen = set(nums)
    k = 1
    while k in seen:
        k += 1
    return k

def first_missing_positive(nums):
    """O(n) time, O(1) extra space: use the list itself as the hash table.
    Put every value v in 1..n at index v - 1 (cyclic placement), then the first index i with nums[i] != i + 1
    gives the answer."""
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            j = nums[i] - 1
            nums[i], nums[j] = nums[j], nums[i]      # each swap puts one value in its final place
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1                                     # 1..n are all present

rng = random.Random(41)
for _ in range(3000):
    nums = [rng.randint(-3, 9) for _ in range(rng.randint(0, 10))]
    want = first_missing_positive_brute(nums[:])
    assert first_missing_positive(nums[:]) == first_missing_positive_set(nums[:]) == want, nums
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN2 = '''rng = random.Random(4100)
big = list(range(1, 500001))
rng.shuffle(big)
big_missing = big[123456]
big[123456] = -7                                    # remove one ticket number and add a junk value
big += [0, 10**9, 3, 3]'''
ANS2 = compute(GEN2, expr="big_missing")
TESTS2 = """check(first_missing_positive, [
    ([2, 5, -3, 1], 3),
    ([1, 2, 3], 4),
    ([7, 8, 9], 1),
    ([0], 1),
    ([1, 1, 2, 2], 3),
    ([-5], 1),
    ([2], 1),
    ([5, 3, 2, 1, 4], 6),
])
# big test: a shuffled 1..500000 with one number replaced by junk
@GEN@
check_big("n = 500004", lambda: first_missing_positive(big), big_missing, limit=1.5)"""
TESTS2 = TESTS2.replace("@GEN@", GEN2)

ex.q("Smallest free ticket number", minutes=20, level="hard",
     prompt="""A list `nums` holds ticket numbers that are already used; it may contain duplicates, zeros, negative
numbers and huge numbers (junk from a bad import). Return the **smallest positive integer that is not in the
list**.

Examples:
- `[2, 5, -3, 1]` -> `3`
- `[1, 2, 3]` -> `4`
- `[7, 8, 9]` -> `1`

Constraints: `1 <= len(nums) <= 5 * 10**5`. Target: **O(n) time and O(1) extra space** (you may change `nums`).
The big test has 500004 numbers. Say what you would do if you were not allowed to change the input.""",
     stub="def first_missing_positive(nums):\n    pass",
     tests=TESTS2,
     hint1="Signal: the answer is always in `1..n+1`, and O(1) extra space is required, so the input array must "
           "act as your hash table. Pattern: **index as hash key** (cyclic placement / in-place hashing).",
     hint2="""1. Brute force: try `k = 1, 2, ...` with `k in nums`: O(n^2). A set makes it O(n) time but O(n) space.
   Sorting is O(n log n).
2. Key fact: with `n` numbers, the answer is at most `n + 1`. Only values in `1..n` matter.
3. Place each value `v` in `1..n` at index `v - 1` by swapping, and keep swapping at `i` until the value there is out
   of range or already in place (watch out for duplicates: stop if the target already holds `v`).
4. Scan: the first index `i` with `nums[i] != i + 1` gives `i + 1`; if none, return `n + 1`.""",
     solution=SOL2,
     why="""Among `n` numbers at most `n` distinct values of `1..n` can be present, so the answer is in `1..n+1`.
That bounded range means index `v - 1` can serve as "the slot for v", and swapping values into their slots uses no
extra memory. Every swap puts at least one value in its final slot, and a value in its slot is never moved again, so
there are at most `n` swaps in total and the nested loop is still O(n). The check `nums[nums[i] - 1] != nums[i]` is
what stops infinite swapping on duplicates.

**Follow-ups the examiner may ask:**
- You may not modify the input: use a set (O(n) space) or a bit array of size `n + 1` (n bits).
- The input is a huge stream: a bitset of size `n + 1` if you know `n`; otherwise the problem cannot be solved in
  O(1) memory.
- Sign-marking variant: first replace values outside `1..n` by `n + 1`, then mark presence of `v` by making
  `nums[v - 1]` negative.
- k-th missing positive in a **sorted** array (LeetCode 1539): binary search on `nums[i] - (i + 1)`.""",
     complexity="Brute force: O(n^2). Set: O(n) time, O(n) space. Sort: O(n log n). Cyclic placement: O(n) time, "
                "O(1) extra space.",
     mistakes="Infinite loop on duplicates (missing the `nums[target] != value` check). Swapping with a stale index "
              "(`nums[i], nums[nums[i] - 1] = ...` assigns `nums[i]` first, so the second target uses the new value; "
              "compute `j = nums[i] - 1` first). Returning `n` instead of `n + 1` when 1..n are all present. Forgetting that 0 is not "
              "positive.",
     learn=["algo-hashing", "algo-arrays-strings"], source=("LeetCode 41", lc("first-missing-positive")))

# ---------------------------------------------------------------- Q3 Maximum Profit in Job Scheduling (1235)
SOL3 = '''import bisect

def max_profit_brute(start, end, profit):
    """Every job is taken or skipped: exponential (2^n subsets)."""
    jobs = sorted(zip(start, end, profit))
    def go(i, free_at):
        if i == len(jobs):
            return 0
        s, e, p = jobs[i]
        best = go(i + 1, free_at)                        # skip job i
        if s >= free_at:
            best = max(best, p + go(i + 1, e))           # take job i
        return best
    return go(0, float("-inf"))

def max_profit_quadratic(start, end, profit):
    """DP over jobs sorted by end; for each job scan all earlier jobs. O(n^2)."""
    jobs = sorted(zip(end, start, profit))
    best = [0] * len(jobs)
    for i, (e, s, p) in enumerate(jobs):
        take = p + max([best[j] for j in range(i) if jobs[j][0] <= s], default=0)
        best[i] = max(best[i - 1] if i else 0, take)
    return best[-1] if jobs else 0

def max_profit(start, end, profit):
    """Sort by end time. dp[i] = best profit using the first i jobs (by end).
    For job i, binary search the last job that ends at or before it starts. O(n log n)."""
    jobs = sorted(zip(end, start, profit))
    ends = [e for e, _, _ in jobs]
    dp = [0] * (len(jobs) + 1)
    for i, (e, s, p) in enumerate(jobs):
        k = bisect.bisect_right(ends, s, 0, i)          # jobs 0..k-1 end at or before s
        dp[i + 1] = max(dp[i], dp[k] + p)                # skip job i, or take it
    return dp[-1]

rng = random.Random(1235)
for _ in range(1500):
    n = rng.randint(1, 8)
    st = [rng.randint(0, 10) for _ in range(n)]
    en = [s + rng.randint(1, 6) for s in st]
    pr = [rng.randint(1, 20) for _ in range(n)]
    assert max_profit(st, en, pr) == max_profit_quadratic(st, en, pr) == max_profit_brute(st, en, pr)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

SMALL3 = [([1, 2, 4, 6], [3, 5, 7, 9], [20, 20, 100, 70]), ([1], [2], [5]), ([1, 1, 1], [2, 3, 4], [5, 6, 4]),
          ([1, 2, 3], [2, 3, 4], [1, 1, 1]), ([1, 3, 0], [5, 4, 10], [2, 2, 100]),
          ([0, 5, 5, 10], [5, 10, 10, 15], [10, 10, 30, 10]), ([4, 2, 1], [6, 4, 3], [5, 5, 5]),
          ([1, 2, 2, 3], [10, 3, 4, 10], [100, 30, 30, 50])]
WANT3 = [compute(SOL3, expr=f"max_profit(*{c!r})") for c in SMALL3]
assert WANT3[:4] == [120, 5, 6, 3], WANT3
GEN3 = '''rng = random.Random(12350)
big_start = [rng.randint(0, 10**6) for _ in range(50000)]
big_end = [s + rng.randint(1, 50000) for s in big_start]
big_profit = [rng.randint(1, 10**4) for _ in range(50000)]'''
ANS3 = compute(SOL3, GEN3, expr="max_profit(big_start, big_end, big_profit)")
cases3 = ",\n".join(f"    ({c!r}, {w!r})" for c, w in zip(SMALL3, WANT3))
TESTS3 = """check(max_profit, [
@CASES@,
])
# big test: 50000 jobs
@GEN@
check_big("n = 50000", lambda: max_profit(big_start, big_end, big_profit), @ANS@, limit=1.0)""".replace(
    "@CASES@", cases3).replace("@GEN@", GEN3).replace("@ANS@", repr(ANS3))

ex.q("Pick the most profitable set of gigs", minutes=25, level="hard",
     prompt="""A freelancer gets `n` job offers. Job `i` runs from `start[i]` to `end[i]` and pays `profit[i]`. She can
work on one job at a time; a job that ends at time `t` is compatible with a job that starts at time `t`. Return the
**maximum total profit**.

Examples:
- `start = [1, 2, 4, 6], end = [3, 5, 7, 9], profit = [20, 20, 100, 70]` -> `120` (jobs `[1, 3)` and `[4, 7)`)
- `start = [1, 2, 3], end = [2, 3, 4], profit = [1, 1, 1]` -> `3` (touching jobs are fine)
- `start = [1, 1, 1], end = [2, 3, 4], profit = [5, 6, 4]` -> `6`

Constraints: `1 <= n <= 5 * 10**4`, times up to about 10**6. Target: O(n log n). The big test has 50000 jobs, so the
O(n^2) DP is too slow.""",
     stub="def max_profit(start, end, profit):\n    pass",
     tests=TESTS3,
     hint1="Signal: choose non-overlapping intervals with **weights** (greedy by end time only works without "
           "weights). Pattern: **1D DP over jobs sorted by end time + binary search** (weighted interval scheduling).",
     hint2="""1. Sort the jobs by end time. Let `dp[i]` = best profit using only the first `i` jobs.
2. For job `i` (start `s`, profit `p`): skip it -> `dp[i]`; take it -> `p + dp[k]`, where `k` = number of jobs that
   end at or before `s`.
3. Find `k` with `bisect_right(ends, s)` on the sorted end times (O(log n) instead of a scan).
4. `dp[i + 1] = max(skip, take)`; the answer is `dp[n]`.""",
     solution=SOL3,
     why="""In the best schedule, the job with the latest end is either used or not. If it is not used, the answer is
the best schedule of the other jobs. If it is used, all other chosen jobs must end by its start, which is a prefix of
the jobs sorted by end. So `dp` over sorted prefixes captures every choice, and binary search finds the compatible
prefix in O(log n). Greedy (earliest end first) maximises the **number** of jobs, not the profit, so it fails here:
one long job can pay more than three short ones.

**Follow-ups the examiner may ask:**
- Return the chosen jobs: remember for each `i` whether you took job `i`, then walk back from `dp[n]`.
- All profits are equal: plain greedy by earliest end time (LeetCode 435 / activity selection), O(n log n).
- Two workers instead of one: the DP state must include two "free at" times; much harder, often solved as min-cost flow.
- Jobs arrive online: keep `(end, best)` pairs sorted by end with increasing `best` and binary search them.
- Times are huge or floats: nothing changes, only the order matters.""",
     complexity="Brute force: O(2^n). DP with a scan: O(n^2). DP with binary search: O(n log n) time, O(n) space.",
     mistakes="Sorting by start but searching by end (or the reverse). `bisect_left` instead of `bisect_right` (a job "
              "ending exactly at `s` must count as compatible). Greedy by profit or by end time. Searching over all "
              "jobs instead of only the ones before `i` (fine after sorting by end, but know why).",
     learn=["algo-dp-1d", "algo-binary-search", "algo-sorting-intervals"],
     source=("LeetCode 1235", lc("maximum-profit-in-job-scheduling")))

ex.save()
