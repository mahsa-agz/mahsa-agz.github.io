"""Day 25 algorithms (hard): Time Based Key-Value Store, N-Queens, Find Median from Data Stream."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from _algo_hard_common import BIG, OPS, lc, compute

ex = Exam(25, "algorithms")
ex.setup(BIG + "\n\n" + OPS)

# ---------------------------------------------------------------- Q1 Time Based Key-Value Store (981)
SOL1 = '''import bisect
from collections import defaultdict

class TimeMapBrute:
    """Keeps (timestamp, value) pairs per key and scans them backwards on every get. get is O(n)."""
    def __init__(self):
        self.data = defaultdict(list)

    def set(self, key, value, timestamp):
        self.data[key].append((timestamp, value))

    def get(self, key, timestamp):
        for t, v in reversed(self.data[key]):
            if t <= timestamp:
                return v
        return ""

class TimeMap:
    """Per key: two parallel lists, timestamps (sorted, because sets arrive in time order) and values.
    get = binary search for the last timestamp <= the query. set O(1), get O(log n)."""
    def __init__(self):
        self.times = defaultdict(list)
        self.values = defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)
        self.values[key].append(value)

    def get(self, key, timestamp):
        i = bisect.bisect_right(self.times[key], timestamp)   # number of versions with time <= timestamp
        return self.values[key][i - 1] if i else ""

rng = random.Random(981)
for _ in range(300):
    fast, slow = TimeMap(), TimeMapBrute()
    t = 0
    for _ in range(40):
        key = rng.choice("ab")
        if rng.random() < 0.5:
            t += rng.randint(1, 3)
            fast.set(key, str(t), t)
            slow.set(key, str(t), t)
        else:
            q = rng.randint(0, t + 2)
            assert fast.get(key, q) == slow.get(key, q)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN1 = '''def timemap_workload():
    """50000 versions of one key, then 50000 lookups at random times. Returns the sum of the values found."""
    rng = random.Random(9810)
    tm = TimeMap()
    for t in range(1, 50001):
        tm.set("model_threshold", str(t), 2 * t)          # versions at times 2, 4, 6, ...
    total = 0
    for _ in range(50000):
        v = tm.get("model_threshold", rng.randint(0, 100001))
        total += int(v) if v else 0
    return total'''
ANS1 = compute(SOL1, GEN1, expr="timemap_workload()")
TESTS1 = """check_ops(TimeMap,
    ["TimeMap", "set", "get", "get", "set", "get", "get", "get"],
    [[], ["price", "10", 5], ["price", 5], ["price", 7], ["price", "12", 9], ["price", 8], ["price", 9], ["price", 4]],
    [None, None, "10", "10", None, "10", "12", ""])
check_ops(TimeMap,
    ["TimeMap", "set", "set", "get", "get", "get"],
    [[], ["a", "x", 1], ["b", "y", 2], ["a", 2], ["b", 1], ["c", 5]],
    [None, None, None, "x", "", ""])
check_ops(TimeMap,
    ["TimeMap", "set", "set", "set", "get", "get", "get"],
    [[], ["cfg", "v1", 10], ["cfg", "v2", 20], ["cfg", "v3", 30], ["cfg", 29], ["cfg", 30], ["cfg", 10**9]],
    [None, None, None, None, "v2", "v3", "v3"])
# big test: 50000 versions of one key, 50000 lookups
@GEN@
check_big("50000 sets + 50000 gets", timemap_workload, @ANS@, limit=1.0)""".replace("@GEN@", GEN1).replace(
    "@ANS@", repr(ANS1))

ex.q("Values that change over time", minutes=15, level="medium",
     prompt="""Build a class `TimeMap` that stores several versions of a value per key:
- `set(key, value, timestamp)`: store `value` for `key` at time `timestamp`.
- `get(key, timestamp)`: return the value of `key` that was valid at time `timestamp`, that is the value whose
  stored timestamp is the **largest one that is `<= timestamp`**. Return `""` if there is none.

For every key, `set` is called with strictly increasing timestamps (think of a config or a price that gets new
versions).

Example:
```
set("price", "10", 5)
get("price", 5)  -> "10"
get("price", 7)  -> "10"
set("price", "12", 9)
get("price", 8)  -> "10"
get("price", 9)  -> "12"
get("price", 4)  -> ""     (nothing was set yet at time 4)
```
Constraints: up to `2 * 10**5` calls. Target: `get` in O(log n). The big test does 50000 sets and 50000 gets on
one key.""",
     stub="""class TimeMap:
    def __init__(self):
        pass

    def set(self, key, value, timestamp):
        pass

    def get(self, key, timestamp):
        pass""",
     tests=TESTS1,
     hint1="Signal: the timestamps of each key are already **sorted**, and you need \"the last one that is <= t\". "
           "Pattern: **binary search** (on the answer position, `bisect_right`).",
     hint2="""1. Store, for each key, a list of timestamps and a parallel list of values (append keeps them sorted).
2. `get`: `i = bisect.bisect_right(times[key], timestamp)` counts the versions with time `<= timestamp`.
3. If `i == 0` return `""`, else return `values[key][i - 1]`.
4. A missing key is just an empty list (use `defaultdict(list)`).""",
     solution=SOL1,
     why="""Because sets arrive in time order, each key's timestamps form a sorted list for free, and "latest version
at or before t" is a predecessor search, which binary search answers in O(log n). The brute force scans backwards
and is O(n) per get, which is 2.5 * 10^9 steps in the worst case of the big test. `bisect_right` (not
`bisect_left`) is what makes an exact timestamp match return that version.

**Follow-ups the examiner may ask:**
- `set` timestamps can arrive out of order: insert with `bisect.insort` (O(n) per insert because of shifting), or
  use a balanced tree / `sortedcontainers.SortedList` for O(log n).
- This is exactly a **point-in-time join** in a feature store: for each training example, take the feature value
  valid at the example's time (pandas `merge_asof`). Mention data leakage if you take a later value.
- Memory is limited: keep only the last N versions per key, or drop versions older than a TTL.
- Range query "all values between t1 and t2": two binary searches give a slice.""",
     complexity="Brute force: set O(1), get O(n). Binary search: set O(1), get O(log n), O(total sets) memory.",
     mistakes="Using `bisect_left` (misses the version stored exactly at `timestamp`). Storing `(timestamp, value)` "
              "tuples and bisecting with a bare integer (compare errors or wrong results; use a separate times list "
              "or `key=` in Python 3.10+). Returning `None` instead of `\"\"`. Sorting the list on every get.",
     learn=["algo-binary-search", "algo-design", "algo-hashing"],
     source=("LeetCode 981", lc("time-based-key-value-store")))

# ---------------------------------------------------------------- Q2 N-Queens (51)
SOL2 = '''from itertools import permutations

def _draw(cols):
    n = len(cols)
    return ["." * c + "Q" + "." * (n - c - 1) for c in cols]

def solve_n_queens_brute(n):
    """One queen per row and per column = a permutation of columns. Check the diagonals of every permutation.
    O(n! * n^2)."""
    out = []
    for cols in permutations(range(n)):
        if all(abs(cols[i] - cols[j]) != j - i for i in range(n) for j in range(i + 1, n)):
            out.append(_draw(cols))
    return out

def solve_n_queens(n):
    """Backtracking row by row; sets of used columns and diagonals make each check O(1)."""
    out, cols = [], []
    used_col, used_d1, used_d2 = set(), set(), set()     # d1: row - col is constant, d2: row + col is constant
    def place(r):
        if r == n:
            out.append(_draw(cols))
            return
        for c in range(n):
            if c in used_col or r - c in used_d1 or r + c in used_d2:
                continue                                  # attacked: prune this branch
            cols.append(c); used_col.add(c); used_d1.add(r - c); used_d2.add(r + c)
            place(r + 1)
            cols.pop(); used_col.remove(c); used_d1.remove(r - c); used_d2.remove(r + c)
    place(0)
    return out

for n in range(1, 8):
    assert sorted(solve_n_queens(n)) == sorted(solve_n_queens_brute(n))
print("stress test vs brute force (n = 1..7): OK")   # prints: stress test vs brute force (n = 1..7): OK'''

TESTS2 = """def any_order(res):
    try:
        return sorted(res)
    except TypeError:
        return res

def count_boards(n):
    return len(solve_n_queens(n))

check(solve_n_queens, [
    (1, [["Q"]]),
    (2, []),
    (3, []),
    (4, [[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]]),
], key=any_order)
check(count_boards, [
    (5, 10),
    (6, 4),
    (8, 92),
])
# big test: count the boards for n = 10
check_big("n = 10", lambda: count_boards(10), 724, limit=1.5)"""

ex.q("Peaceful queens", minutes=20, level="hard",
     prompt="""Place `n` chess queens on an `n x n` board so that no two attack each other (no two share a row, a
column or a diagonal). Return **all** such boards, in any order. Draw each board as a list of `n` strings, with `"Q"`
for a queen and `"."` for an empty square.

Examples:
- `n = 4` -> two boards:
```
.Q..      ..Q.
...Q      Q...
Q...      ...Q
..Q.      .Q..
```
- `n = 2` -> `[]` and `n = 3` -> `[]` (impossible)
- `n = 1` -> `[["Q"]]`

Constraints: `1 <= n <= 10`. The tests also count the boards for `n = 5, 6, 8` and, in the big test, for `n = 10`
(724 boards) within 1.5 seconds, so checking all `n!` column orders is too slow.""",
     stub="def solve_n_queens(n):\n    pass",
     tests=TESTS2,
     hint1="Signal: \"return all\" valid configurations, built one decision at a time with constraints you can "
           "check early. Pattern: **backtracking** with pruning.",
     hint2="""1. Place one queen per row, row by row; for the current row try every column.
2. A square `(r, c)` is attacked if column `c` is used, or diagonal `r - c` is used, or anti-diagonal `r + c` is used.
   Keep three sets so each check is O(1).
3. Place, recurse to the next row, then remove the queen (undo all three sets).
4. When `r == n`, draw the board from the list of chosen columns and save it.""",
     solution=SOL2,
     why="""Placing exactly one queen per row removes the row conflicts by construction, and the three sets remove
column and diagonal conflicts in O(1). The key gain over the brute force is **pruning**: as soon as a partial board
has a conflict, the whole subtree of completions is skipped, while the brute force builds and checks all `n!`
permutations. All squares on one diagonal share `r - c`, and on one anti-diagonal share `r + c`, which is why those
two numbers identify the diagonals.

**Follow-ups the examiner may ask:**
- Only count the boards (LeetCode 52): same search without drawing; use bitmasks for columns and diagonals, which
  is several times faster.
- Use symmetry: only try the first half of the columns in row 0 and double the count (careful with the middle
  column when `n` is odd).
- What is the complexity? The search tree is bounded by `n!`; in practice the pruning makes it much smaller, but it
  is still exponential.
- Return just one board quickly for large `n`: there are constructive formulas, or use a local search
  (min-conflicts heuristic).""",
     complexity="Brute force: O(n! * n^2). Backtracking: O(n!) in the worst case (much less in practice), O(n) "
                "extra space plus the output.",
     mistakes="Forgetting to undo one of the three sets when backtracking. Using `abs(r - c)` for the diagonal "
              "(merges two different diagonals). Building the board strings at every step instead of only at the "
              "end. Appending the same mutable list to the answer (copy it or draw it).",
     learn=["algo-backtracking"], source=("LeetCode 51", lc("n-queens")))

# ---------------------------------------------------------------- Q3 Find Median from Data Stream (295)
SOL3 = '''import heapq

class MedianFinderBrute:
    """Append, then sort the whole list at every query. find_median is O(n log n)."""
    def __init__(self):
        self.vals = []

    def add_num(self, x):
        self.vals.append(x)

    def find_median(self):
        s = sorted(self.vals)
        n = len(s)
        return float(s[n // 2]) if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2

class MedianFinder:
    """Two heaps: `low` is a max-heap (stored negated) with the smaller half, `high` a min-heap with the larger
    half. len(low) == len(high) or len(low) == len(high) + 1. add O(log n), median O(1)."""
    def __init__(self):
        self.low, self.high = [], []

    def add_num(self, x):
        heapq.heappush(self.low, -x)                              # 1. push into the lower half
        heapq.heappush(self.high, -heapq.heappop(self.low))       # 2. move the largest of low to high
        if len(self.high) > len(self.low):                       # 3. rebalance sizes
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def find_median(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2

rng = random.Random(295)
for _ in range(300):
    fast, slow = MedianFinder(), MedianFinderBrute()
    for _ in range(30):
        x = rng.randint(-20, 20)
        fast.add_num(x)
        slow.add_num(x)
        assert fast.find_median() == slow.find_median()
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN3 = '''def median_workload():
    """50000 random numbers, the median after each one. Returns the sum of all medians."""
    rng = random.Random(2950)
    mf = MedianFinder()
    total = 0.0
    for _ in range(50000):
        mf.add_num(rng.randint(0, 10**6))
        total += mf.find_median()
    return total'''
ANS3 = compute(SOL3, GEN3, expr="median_workload()")
TESTS3 = """check_ops(MedianFinder,
    ["MedianFinder", "add_num", "find_median", "add_num", "find_median", "add_num", "find_median"],
    [[], [5], [], [15], [], [1], []],
    [None, None, 5.0, None, 10.0, None, 5.0])
check_ops(MedianFinder,
    ["MedianFinder", "add_num", "find_median", "add_num", "find_median", "add_num", "find_median",
     "add_num", "find_median", "add_num", "find_median"],
    [[], [-1], [], [-1], [], [3], [], [3], [], [2], []],
    [None, None, -1.0, None, -1.0, None, -1.0, None, 1.0, None, 2.0])
check_ops(MedianFinder,
    ["MedianFinder", "add_num", "find_median", "add_num", "find_median", "add_num", "find_median", "add_num", "find_median"],
    [[], [10], [], [9], [], [8], [], [7], []],
    [None, None, 10.0, None, 9.5, None, 9.0, None, 8.5])
# big test: 50000 numbers with a median query after each one
@GEN@
check_big("50000 adds, median after each", median_workload, @ANS@, limit=1.0)""".replace("@GEN@", GEN3).replace(
    "@ANS@", repr(ANS3))

ex.q("Running median of a live metric", minutes=20, level="hard",
     prompt="""Numbers arrive one by one (for example response times of a live service). Build a class
`MedianFinder` with:
- `add_num(x)`: add the integer `x`.
- `find_median()`: return the median of all numbers so far as a float. With an even count, the median is the
  average of the two middle values.

Example:
```
add_num(5)    find_median() -> 5.0
add_num(15)   find_median() -> 10.0
add_num(1)    find_median() -> 5.0
```
Constraints: up to `5 * 10**4` adds, a query may follow every add. Target: `add_num` in O(log n) and `find_median`
in O(1). The big test asks for the median after each of 50000 adds.""",
     stub="""class MedianFinder:
    def __init__(self):
        pass

    def add_num(self, x):
        pass

    def find_median(self):
        pass""",
     tests=TESTS3,
     hint1="Signal: a stream, and you repeatedly need the middle element (the max of the lower half and the min of "
           "the upper half). Pattern: **two heaps** (a max-heap and a min-heap).",
     hint2="""1. `low`: max-heap of the smaller half (Python: push `-x`). `high`: min-heap of the larger half.
2. Keep `len(low) == len(high)` or `len(low) == len(high) + 1`.
3. Add: push into `low`, move the top of `low` to `high` (so every value in low is `<=` every value in high), then if
   `high` is bigger, move its top back to `low`.
4. Median: `-low[0]` if `low` is bigger, else the average of `-low[0]` and `high[0]`.""",
     solution=SOL3,
     why="""The median only depends on the largest value of the lower half and the smallest value of the upper half,
and heaps give exactly those in O(1) while inserts cost O(log n). Routing every new value through `low` and then
`high` keeps the order invariant (all of `low` <= all of `high`) without any comparison logic. The brute force
sorts everything at every query: 50000 queries times a sort of up to 50000 values. Keeping a sorted list with
`bisect.insort` is a decent middle answer (O(n) per insert because of shifting, fast in practice for 5 * 10^4).

**Follow-ups the examiner may ask:**
- All values are integers in `[0, 100]`: keep a count array of size 101 and walk it, O(100) per query.
- 99% of values are in `[0, 100]`: count array plus two small heaps (or counters) for the outliers.
- Median of a **sliding window** of the last k values (LeetCode 480): two heaps with lazy deletion, or a sorted
  list.
- Billions of values across many machines: exact medians do not merge; use approximate quantile sketches
  (t-digest, KLL, Greenwald-Khanna) that do. Very relevant for p50 / p99 latency dashboards.
- Values can also be removed: lazy deletion with a "to delete" counter per heap.""",
     complexity="Brute force: add O(1), median O(n log n). Two heaps: add O(log n), median O(1), O(n) space.",
     mistakes="Forgetting that `heapq` is a min-heap (negate for the lower half). Returning an int instead of a float "
              "for odd counts (`5` vs `5.0` compare equal in Python, but say float in an exam). Letting the "
              "sizes drift by more than one. Integer division `//` for the even case.",
     learn=["algo-heap", "algo-design"], source=("LeetCode 295", lc("find-median-from-data-stream")))

ex.save()
