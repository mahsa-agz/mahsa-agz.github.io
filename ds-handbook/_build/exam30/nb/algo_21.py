"""Day 21 algorithms (mock exam, hard band): Unique Paths, Minimum Window Substring, Course Schedule II."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from _algo_hard_common import BIG, lc, compute, MOCK_INTRO

ex = Exam(21, "algorithms", intro=MOCK_INTRO + " Suggested split: 12 + 28 + 20 minutes.")
ex.setup(BIG)

# ---------------------------------------------------------------- Q1 Unique Paths (62)
SOL1 = '''import math

def unique_paths_brute(m, n):
    """Tries every route: exponential, about C(m+n-2, m-1) calls. Fine for tiny grids only."""
    if m == 1 or n == 1:
        return 1
    return unique_paths_brute(m - 1, n) + unique_paths_brute(m, n - 1)

def unique_paths(m, n):
    """Grid DP with one row: dp[c] = number of routes to column c of the current row."""
    dp = [1] * n                      # first row: exactly one route to each cell (all right moves)
    for _ in range(1, m):
        for c in range(1, n):
            dp[c] += dp[c - 1]        # from above (old dp[c]) + from the left (new dp[c - 1])
    return dp[-1]

# stress test: DP == brute force == formula C(m+n-2, m-1) on all small grids
for m in range(1, 9):
    for n in range(1, 9):
        assert unique_paths(m, n) == unique_paths_brute(m, n) == math.comb(m + n - 2, m - 1)
print("stress test vs brute force and formula: OK")   # prints: stress test vs brute force and formula: OK'''

ANS1 = compute(SOL1, expr="unique_paths(100, 100)")
TESTS1 = """check(unique_paths, [
    ((1, 1), 1),
    ((2, 3), 3),
    ((3, 3), 6),
    ((1, 9), 1),
    ((9, 1), 1),
    ((3, 7), 28),
    ((10, 10), 48620),
    ((12, 8), 31824),
])
check_big("100 x 100 grid", lambda: unique_paths(100, 100), @ANS@, limit=0.5)""".replace("@ANS@", repr(ANS1))

ex.q("Robot routes on a grid", minutes=12, level="medium",
     prompt="""A warehouse robot starts in the top-left cell of a grid with `m` rows and `n` columns and must reach
the bottom-right cell. Each step moves it one cell **right** or one cell **down**. Return the number of different
routes.

Examples:
- `m = 2, n = 3` -> `3` (the routes are RRD, RDR, DRR)
- `m = 3, n = 3` -> `6`
- `m = 1, n = 9` -> `1` (only right moves)

Constraints: `1 <= m, n <= 100`. The answer can be very large (Python integers are fine). The last test uses a
100 x 100 grid, so trying every route will not finish in time.""",
     stub="def unique_paths(m, n):\n    pass",
     tests=TESTS1,
     hint1="Signal: \"count the ways\" to reach a cell, and every cell can only be reached from its top or its "
           "left neighbour, so the same sub-counts are needed again and again. Pattern: **2D dynamic programming** "
           "(grid DP).",
     hint2="""1. Brute force first (say it out loud): recursion `paths(r, c) = paths(r-1, c) + paths(r, c-1)`.
   It is exponential because the same cells are recomputed.
2. Store the counts: `dp[r][c] = dp[r-1][c] + dp[r][c-1]`, with 1 for every cell in the first row and first column.
3. You only need the previous row, so keep one list `dp` of length `n` and update it left to right.
4. Bonus: a route is just `m-1` downs and `n-1` rights in some order, so the answer is `C(m+n-2, m-1)`.""",
     solution=SOL1,
     why="""Every route to a cell ends with a move from the cell above or the cell to the left, and those two sets of
routes never overlap. So the count for a cell is the sum of the two neighbour counts. The brute force recomputes the
same cells an exponential number of times; the table computes each cell once. Updating one row in place works
because, when you reach column `c`, `dp[c]` still holds the value from the row above and `dp[c-1]` already holds the
value of the current row.

**Follow-ups the examiner may ask:**
- Some cells are blocked (LeetCode 63): set `dp[c] = 0` for a blocked cell; the first row and column stop at the first block.
- Each cell has a cost, find the cheapest route (LeetCode 64): same table with `min` instead of `+`.
- The answer must be returned modulo `10**9 + 7`, or `m, n` are up to `10**6`: use the formula with factorials and
  modular inverses, O(m + n).
- Diagonal moves are also allowed: add `dp_prev[c-1]` as a third term (keep the previous row as a separate list).""",
     complexity="Brute force: exponential. DP: O(m * n) time, O(n) extra space. Formula: O(min(m, n)) multiplications.",
     mistakes="Starting the first row or column at 0 instead of 1. Swapping rows and columns in the 1D update. "
              "Using floating point (`factorial / factorial`) for the formula, which loses precision for big grids; "
              "use `math.comb` or integer arithmetic.",
     learn=["algo-dp-2d", "algo-dp-1d"], source=("LeetCode 62", lc("unique-paths")))

# ---------------------------------------------------------------- Q2 Minimum Window Substring (76)
SOL2 = '''from collections import Counter

def min_window_brute(s, t):
    """Every start i, grow the end until the window covers t. O(n^2) windows, each check O(alphabet)."""
    need, best = Counter(t), ""
    for i in range(len(s)):
        have = Counter()
        for j in range(i, len(s)):
            have[s[j]] += 1
            if all(have[c] >= k for c, k in need.items()):
                if not best or j - i + 1 < len(best):
                    best = s[i:j + 1]
                break
    return best

def min_window(s, t):
    """Variable-size sliding window: grow the right end, shrink the left end while the window still covers t."""
    if not t or len(t) > len(s):
        return ""
    need = Counter(t)            # need[c] > 0: still missing; need[c] < 0: extra copies inside the window
    missing = len(t)             # characters of t still missing, counted with repeats
    left, best_start, best_len = 0, 0, float("inf")
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:      # valid window: record it, then try to make it shorter
            if right - left + 1 < best_len:
                best_start, best_len = left, right - left + 1
            need[s[left]] += 1
            if need[s[left]] > 0:     # we just dropped a character we needed
                missing += 1
            left += 1
    return "" if best_len == float("inf") else s[best_start:best_start + best_len]

# stress test against the brute force on many small random strings
rng = random.Random(76)
for _ in range(3000):
    s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 12)))
    t = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
    assert min_window(s, t) == min_window_brute(s, t), (s, t)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN2 = '''rng = random.Random(2021)
big_s = [rng.choice("abcd") for _ in range(200000)]
for pos in rng.sample(range(200000), 8):
    big_s[pos] = "x"               # a rare character: only 8 of them in the whole text
big_s = "".join(big_s)'''

ANS2 = compute("import random", SOL2, GEN2, expr="min_window(big_s, 'xxabcd')")
TESTS2 = """check(min_window, [
    (("ZXAYBQCAB", "ABC"), "CAB"),
    (("ZXAYBQCAB", "AAB"), "AYBQCA"),
    (("cabwefgewcwaefgcf", "cae"), "cwae"),
    (("a", "a"), "a"),
    (("a", "aa"), ""),
    (("abc", "d"), ""),
    (("bba", "ab"), "ba"),
    (("abab", "ab"), "ab"),
])
# big test: 200000 characters, the pattern needs two copies of a rare character
@GEN@
check_big("n = 200000", lambda: min_window(big_s, "xxabcd"), @ANS@, limit=1.0)""".replace("@GEN@", GEN2).replace(
    "@ANS@", repr(ANS2))

ex.q("Shortest stretch that covers a pattern", minutes=28, level="hard",
     prompt="""You get a text `s` and a pattern `t`. Return the **shortest contiguous piece** of `s` that contains
every character of `t`, **including repeats** (if `t` has two `A`s, the piece needs at least two `A`s). Characters are
case-sensitive. If several pieces have the same shortest length, return the leftmost one. If no piece works, return
`""`.

Examples:
- `s = "ZXAYBQCAB", t = "ABC"` -> `"CAB"`
- `s = "ZXAYBQCAB", t = "AAB"` -> `"AYBQCA"` (it must hold two `A`s)
- `s = "a", t = "aa"` -> `""`

Constraints: `1 <= len(s), len(t) <= 2 * 10**5`. Target: one pass over `s`, O(n) time. The big test has 200000
characters.""",
     stub="def min_window(s, t):\n    pass",
     tests=TESTS2,
     hint1="Signal: \"shortest contiguous piece that satisfies a condition\", and the condition stays true when "
           "the piece grows. Pattern: **variable-size sliding window** with a character count map.",
     hint2="""1. Count what you need: `need = Counter(t)`, and `missing = len(t)`.
2. Move `right` over `s`. If `need[ch] > 0`, this character was missing, so `missing -= 1`. Always do `need[ch] -= 1`
   (negative values mean extra copies inside the window).
3. While `missing == 0` the window is valid: record it if it is shorter, then remove `s[left]`
   (`need[s[left]] += 1`; if it becomes positive, `missing += 1`) and move `left` right.
4. Each index enters and leaves the window once, so the whole thing is O(n).""",
     solution=SOL2,
     why="""If the window `[left, right]` covers `t`, every longer window with the same `left` also covers it, so
for each `right` we only care about the largest `left` that still works. Both pointers only move forward, so the
work is linear. The single counter `missing` avoids comparing two whole count maps at every step, which is what
makes the brute force slow. Recording the window only when it is strictly shorter keeps the leftmost answer on ties.

**Follow-ups the examiner may ask:**
- Only the set of distinct characters matters (no repeats): set `need[c] = 1` for each distinct `c` and count
  distinct characters covered instead.
- The characters of `t` must appear in order (LeetCode 727, minimum window subsequence): the window trick no
  longer works; use DP or a forward then backward scan.
- Return the length of the shortest window that contains at least `k` distinct characters: same template, different
  validity counter.
- `s` is a huge log file read as a stream: the window still works with a deque of the current window, but memory
  can grow to the window size; say so.""",
     complexity="Brute force: O(n^2 * A) where A is the alphabet size. Sliding window: O(len(s) + len(t)) time, "
                "O(A) space for the counts.",
     mistakes="Ignoring repeats in `t` (using a set). Updating `missing` for characters that are already in surplus. "
               "Building the answer string inside the loop (copies, O(n^2)); keep `best_start` and `best_len` instead. "
               "Forgetting the `len(t) > len(s)` case.",
     learn=["algo-sliding-window", "algo-hashing"], source=("LeetCode 76", lc("minimum-window-substring")))

# ---------------------------------------------------------------- Q3 Course Schedule II (210)
SOL3 = '''from collections import deque

def job_order_brute(n, deps):
    """Repeatedly scan for a job whose prerequisites are all done. O(n * (n + E))."""
    before = [set() for _ in range(n)]
    for a, b in deps:
        before[a].add(b)
    done, order = set(), []
    while len(order) < n:
        ready = [j for j in range(n) if j not in done and before[j] <= done]
        if not ready:
            return []                     # every remaining job waits on another remaining job: a cycle
        done.add(ready[0])
        order.append(ready[0])
    return order

def job_order(n, deps):
    """Kahn's algorithm: start with jobs that wait on nothing, remove them, repeat."""
    after = [[] for _ in range(n)]        # b -> jobs that need b first
    indeg = [0] * n                       # number of prerequisites not yet done
    for a, b in deps:
        after[b].append(a)
        indeg[a] += 1
    queue = deque(j for j in range(n) if indeg[j] == 0)
    order = []
    while queue:
        j = queue.popleft()
        order.append(j)
        for nxt in after[j]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)
    return order if len(order) == n else []   # jobs left over sit on a cycle

# stress test: both agree on "possible or not" on random small graphs, and Kahn's order is always valid
rng = random.Random(210)
for _ in range(2000):
    n = rng.randint(1, 7)
    deps = [[rng.randrange(n), rng.randrange(n)] for _ in range(rng.randint(0, 9))]
    fast, slow = job_order(n, deps), job_order_brute(n, deps)
    assert (fast == []) == (slow == [])
    if fast:
        pos = {j: i for i, j in enumerate(fast)}
        assert all(pos[b] < pos[a] for a, b in deps)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN3 = '''rng = random.Random(2100)
N = 100000
perm = list(range(N))
rng.shuffle(perm)                                      # hide the order behind random job ids
big_deps = [[perm[i], perm[i - 1]] for i in range(1, N)]          # one long chain (depth 100000)
for _ in range(100000):
    a = rng.randrange(1, N)
    big_deps.append([perm[a], perm[rng.randrange(a)]])            # extra forward dependencies
cyclic_deps = big_deps + [[perm[0], perm[N - 1]]]                  # closes the chain into a cycle'''

TESTS3 = """def order_status(n, deps):
    \"\"\"'valid' if job_order returns a correct full order, 'empty' if it returns [], else 'invalid'.\"\"\"
    order = job_order(n, deps)
    if order == []:
        return "empty"
    if order is None or sorted(order) != list(range(n)):
        return "invalid"
    pos = {job: i for i, job in enumerate(order)}
    return "valid" if all(pos[b] < pos[a] for a, b in deps) else "invalid"

check(order_status, [
    ((2, [[1, 0]]), "valid"),
    ((2, [[1, 0], [0, 1]]), "empty"),
    ((1, []), "valid"),
    ((3, []), "valid"),
    ((4, [[1, 0], [2, 0], [3, 1], [3, 2]]), "valid"),
    ((3, [[0, 0]]), "empty"),
    ((5, [[1, 0], [2, 1], [0, 2], [4, 3]]), "empty"),
    ((6, [[5, 4], [4, 3], [3, 2], [2, 1], [1, 0], [5, 0], [5, 0]]), "valid"),
])
# big tests: 100000 jobs, about 200000 dependencies, one chain of depth 100000
@GEN@
check_big("100000 jobs, no cycle", lambda: order_status(N, big_deps), "valid", limit=1.5)
check_big("100000 jobs, one long cycle", lambda: order_status(N, cyclic_deps), "empty", limit=1.5)""".replace(
    "@GEN@", GEN3)

ex.q("Order the pipeline jobs", minutes=20, level="medium",
     prompt="""A data pipeline has `n` jobs numbered `0` to `n-1`. Each pair `[a, b]` in `deps` means job `b` must
finish **before** job `a` starts. Return any order that runs all `n` jobs and respects every pair. If no such order
exists, return an empty list `[]`.

Examples:
- `n = 4, deps = [[1, 0], [2, 0], [3, 1], [3, 2]]` -> `[0, 1, 2, 3]` (or `[0, 2, 1, 3]`; both are fine)
- `n = 2, deps = [[1, 0], [0, 1]]` -> `[]` (each job waits on the other)
- `n = 3, deps = []` -> any order of `0, 1, 2`

Constraints: `1 <= n <= 10**5`, up to `2 * 10**5` pairs, pairs may repeat, a job may even list itself. The tests
accept any valid order. The big tests contain a dependency chain 100000 jobs deep.""",
     stub="def job_order(n, deps):\n    pass",
     tests=TESTS3,
     hint1="Signal: tasks with \"must happen before\" rules, and you need an order (or to detect that none "
           "exists). Pattern: **topological sort** (Kahn's algorithm, BFS on in-degrees).",
     hint2="""1. Build the graph `b -> a` for every pair and count `indeg[a]` (how many jobs `a` waits on).
2. Put every job with `indeg == 0` in a queue.
3. Pop a job, append it to the order, and decrease `indeg` of the jobs that wait on it; push any that reach 0.
4. If the order has fewer than `n` jobs, the rest are stuck on a cycle: return `[]`.
5. Avoid recursive DFS here: a chain 100000 deep breaks Python's recursion limit.""",
     solution=SOL3,
     why="""A job with no unfinished prerequisites can always run next, and running it can only make other jobs
ready. If at some point no job is ready but jobs remain, every remaining job waits on another remaining job, which
means there is a cycle. Kahn's algorithm touches each job and each pair once. It is iterative, so it does not hit the
recursion limit that a DFS-based topological sort hits on long chains.

**Follow-ups the examiner may ask:**
- Return the smallest order in dictionary order: use a min-heap instead of the queue (O((n + E) log n)).
- Jobs can run in parallel, each takes one time unit: the minimum number of rounds is the number of BFS layers
  (process the queue level by level).
- Jobs have durations: the total time is the longest path in the DAG (the critical path); do a DP in topological order.
- Print the cycle: use DFS with three colours (unseen, on stack, done) and keep the parent of each node.""",
     complexity="Brute force: O(n * (n + E)). Kahn's algorithm: O(n + E) time and space.",
     mistakes="Reversing the edge direction (pair `[a, b]` means `b` first). Returning a partial order instead of `[]` "
              "when there is a cycle. Counting a repeated pair twice in `indeg` but adding the edge once (keep both "
              "consistent). Recursive DFS on a 100000-deep chain (RecursionError).",
     learn=["algo-topological-sort", "algo-graphs-bfs-dfs"], source=("LeetCode 210", lc("course-schedule-ii")))

ex.save()
