import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _algo_mid_common import BIG

INTRO = """**Mock exam rules (exam conditions):**

1. Set **one timer for 60 minutes** for the whole notebook. Do not pause it.
2. Do **not** open any hint or solution until the timer rings. No notes, no handbook, no search.
3. For each question: say the pattern and the complexity out loud before you code, then run the tests.
4. If one question blocks you for more than about 20 minutes, move on and come back at the end.
5. When time is up, write down for each question: solved / partly / not solved, and the minutes it took. Then open
   the hints and solutions and log every question that was not fully solved in time."""

ex = Exam(14, "algorithms", intro=INTRO)
ex.setup(BIG)

# ---------------------------------------------------------------- Q1 rotting oranges (multi-source BFS)
ex.q("How long until everything spoils?", minutes=20,
     prompt="""A grid describes a crate of fruit: `0` = empty cell, `1` = fresh fruit, `2` = rotten fruit. Every
minute, each fresh fruit that touches a rotten fruit **up, down, left or right** becomes rotten. Return the number of
minutes until no fresh fruit is left, or `-1` if some fresh fruit can never rot.

Example:
```
[[2, 1, 0],
 [0, 1, 1],
 [1, 0, 1]]
```
gives `-1`: the fruit in the bottom-left corner has no neighbour that can rot it. Without that fruit
(`[[2, 1, 0], [0, 1, 1], [0, 0, 1]]`) the answer is `4`.

Constraints: up to 300 x 300 cells. The larger test is 300 x 300, so re-scanning the whole grid every minute is too
slow.""",
     stub="""def oranges_rotting(grid):
    pass""",
     tests="""check(oranges_rotting, [
    ([[2, 1, 0], [0, 1, 1], [1, 0, 1]], -1),
    ([[2, 1, 0], [0, 1, 1], [0, 0, 1]], 4),
    ([[2, 1, 1], [1, 1, 0], [0, 1, 1]], 4),
    ([[0, 2]], 0),                       # nothing fresh: 0 minutes
    ([[0]], 0),                          # empty crate
    ([[1]], -1),                         # fresh fruit, nothing rotten
    ([[2, 1, 1, 1, 2]], 2),              # two sources meet in the middle
    ([[2, 2], [1, 1], [0, 0], [2, 0]], 1),
])
# larger input: 300 x 300 fresh fruit with one rotten fruit in a corner
def big_grid():
    g = [[1] * 300 for _ in range(300)]
    g[0][0] = 2
    return g
check_big("300 x 300, one rotten corner", lambda: oranges_rotting(big_grid()), 598)""",
     hint1="""Signal: something spreads one step per time unit from **several starting cells at once**, and you need
the time when it reaches the last cell. Pattern: **multi-source BFS** on a grid (all rotten cells start in the queue
at minute 0).""",
     hint2="""1. Scan once: put every rotten cell in a queue and count the fresh cells.
2. Process the queue level by level; each level is one minute. For each cell, rot its fresh neighbours, decrease the
   fresh count and push them.
3. Count a minute only when the level actually rotted something (or count levels and subtract 1).
4. At the end return the minutes if the fresh count is 0, else -1.""",
     solution="""from collections import deque

def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue, fresh = deque(), 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while queue and fresh:
        for _ in range(len(queue)):                  # one level = one minute
            r, c = queue.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2                 # mark when pushed, so no cell is pushed twice
                    fresh -= 1
                    queue.append((nr, nc))
        minutes += 1
    return minutes if fresh == 0 else -1""",
     why="""BFS visits cells in order of distance from the start. Starting with **all** rotten cells in the queue gives
each fresh cell its distance to the nearest rotten one, and the last level is the answer. Every cell enters the queue
once, so the cost is linear in the grid size. Re-scanning the full grid every minute costs O((rows * cols) x minutes),
which is about 54 million cell visits on the 300 x 300 test.

**Follow-ups (what if...):**
- *What if you must not modify the input grid?* Copy it, or keep a `seen` set / a separate distance grid.
- *What if rot also spreads diagonally?* Use the 8 neighbour offsets; the BFS is unchanged.
- *What if some fruit rots after 2 minutes of contact (weighted spreading)?* Unequal step costs need Dijkstra (a heap
  ordered by time) instead of a plain BFS.
- *What if you want the distance from every cell to the nearest rotten one (LeetCode 542 style)?* The same
  multi-source BFS fills a distance grid.
- *What if the grid is huge and sparse (a few million cells, mostly empty)?* Store only non-empty cells in a dict or
  set keyed by `(r, c)`; BFS cost then depends on the fruit, not on the grid area.""",
     complexity="O(rows x cols) time and space.",
     mistakes="Starting a separate BFS from each rotten fruit (gives the wrong time and costs more). Counting one "
              "minute too many (the last level rots nothing). Forgetting the case with no fresh fruit (answer 0). "
              "Marking a cell rotten when popped instead of when pushed, which pushes duplicates.",
     learn=["algo-graphs-bfs-dfs", "algo-grid-simulation"],
     source=("LeetCode 994", "https://leetcode.com/problems/rotting-oranges/"))

# ---------------------------------------------------------------- Q2 koko eating bananas (binary search on the answer)
ex.q("Slowest pace that still meets the deadline", minutes=20,
     prompt="""You must eat piles of snacks within `h` hours. `piles[i]` is the size of pile `i`. You choose a fixed
eating speed `s` (items per hour). Each hour you pick one pile and eat up to `s` items from it; if the pile has fewer
than `s` items you finish it and wait for the rest of that hour (you never switch piles within an hour). Return the
**smallest** integer speed that finishes everything within `h` hours. The tests guarantee `h >= len(piles)`.

Example: `piles = [3, 6, 7, 11]`, `h = 8` gives `4`: hours needed at speed 4 are 1 + 2 + 2 + 3 = 8. Speed 3 would need
1 + 2 + 3 + 4 = 10 hours.

Constraints: up to 10,000 piles, each pile up to 1,000,000,000 items.""",
     stub="""def min_eating_speed(piles, h):
    pass""",
     tests="""check(min_eating_speed, [
    (([3, 6, 7, 11], 8), 4),
    (([30, 11, 23, 4, 20], 5), 30),          # h = number of piles: speed = biggest pile
    (([30, 11, 23, 4, 20], 6), 23),
    (([1], 1), 1),                           # smallest case
    (([1_000_000_000], 2), 500_000_000),     # one huge pile
    (([5, 5, 5], 100), 1),                   # lots of time: speed 1
    (([2, 2], 2), 2),
    (([312884470], 312884469), 2),           # just one hour short of speed 1
])
# larger input: 2,000 piles of 100,000 items, 40,000 hours (answer 5,000); trying speeds 1, 2, 3, ... is too slow
check_big("2,000 piles, answer 5,000", lambda: min_eating_speed([100_000] * 2_000, 40_000), 5_000, limit=0.5)""",
     hint1="""Signal: "find the minimum value that still works", and if a speed works then every faster speed also
works (the check is monotone). Pattern: **binary search on the answer** over the speed range `1..max(piles)`.""",
     hint2="""1. Write `hours(s) = sum(ceil(p / s) for p in piles)`, computed as `(p + s - 1) // s`.
2. Search `lo = 1`, `hi = max(piles)` (at that speed every pile takes one hour).
3. While `lo < hi`: `mid = (lo + hi) // 2`. If `hours(mid) <= h`, `mid` works, so `hi = mid`; else `lo = mid + 1`.
4. Return `lo`.""",
     solution="""def min_eating_speed(piles, h):
    def hours(speed):
        return sum((p + speed - 1) // speed for p in piles)   # integer ceil(p / speed)

    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if hours(mid) <= h:      # fast enough: the answer is mid or smaller
            hi = mid
        else:                    # too slow: the answer is bigger than mid
            lo = mid + 1
    return lo""",
     why="""`hours(speed)` never increases when the speed increases, so the speeds split into "too slow" followed by
"fast enough". Binary search finds the first "fast enough" speed with about `log2(max_pile)` checks (at most 30 for
1e9), each O(n). Trying speeds one by one costs O(answer x n), which is 5 million pile divisions on the larger test.

**Follow-ups (what if...):**
- *What if piles are huge in number (10 million) and you need speed?* Each check is still one pass; NumPy
  (`np.ceil(piles / s).sum()`) vectorises it. A tighter start `lo = ceil(sum(piles) / h)` also cuts iterations.
- *What if you may switch to another pile within the same hour?* Then hours = `ceil(sum(piles) / s)` and the answer
  is simply `ceil(sum(piles) / h)`, no search needed.
- *Where else does this pattern appear?* "Capacity to ship packages within D days" (LeetCode 1011), "split array
  largest sum" (410), "minimum days to make bouquets" (1482): pick the answer, check feasibility greedily, binary
  search the boundary.
- *What if the answer can be a real number (for example a rate in items per second)?* Binary search on floats for a
  fixed number of iterations (about 60) or until `hi - lo` is below the precision you need.""",
     complexity="O(n log M) time where M = max(piles), O(1) extra space.",
     mistakes="Using `p // speed` (floor) instead of ceiling. Starting `lo` at 0 (division by zero). Mixing up the "
              "update rules and getting an infinite loop (`hi = mid` must pair with `lo < hi` and `lo = mid + 1`). "
              "Using floats for the ceiling with huge numbers.",
     learn=["algo-binary-search"],
     source=("LeetCode 875", "https://leetcode.com/problems/koko-eating-bananas/"))

# ---------------------------------------------------------------- Q3 longest consecutive sequence (hashing)
ex.q("Longest run of consecutive integers", minutes=20,
     prompt="""Given an **unsorted** list of integers, return the length of the longest run of consecutive values
(`x, x + 1, x + 2, ...`) that all appear in the list. The values do not have to be next to each other in the list,
and duplicates count once. Aim for O(n) time.

Example: `nums = [10, 4, 20, 1, 3, 2, 11]` gives `4` (the run 1, 2, 3, 4). `[]` gives `0`.

Constraints: up to 100,000 numbers, values between -1e9 and 1e9.""",
     stub="""def longest_consecutive(nums):
    pass""",
     tests="""check(longest_consecutive, [
    ([10, 4, 20, 1, 3, 2, 11], 4),
    ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1], 9),
    ([], 0),                                  # empty
    ([5], 1),                                 # one value
    ([1, 2, 0, 1], 3),                        # duplicates count once
    ([-1, -2, -3, 10], 3),                    # negative values
    ([1, 3, 5, 7], 1),                        # no neighbours at all
    ([1_000_000_000, -1_000_000_000, 999_999_999], 2),
])
# larger input: 0..9,999 shuffled; walking forward from EVERY number (not only from run starts) is O(n^2) here
import random
big = list(range(10_000))
random.Random(14).shuffle(big)
check_big("10,000 shuffled values, one long run", lambda: longest_consecutive(big), 10_000)""",
     hint1="""Signal: "consecutive values" in an unsorted list with an O(n) target, so sorting (O(n log n)) is not the
intended path. Pattern: **hashing** (a set for O(1) membership; only start counting at a value whose predecessor
`x - 1` is missing).""",
     hint2="""1. Put all values in a set (this also removes duplicates).
2. For each value `x` in the set: if `x - 1` is in the set, skip it (it is not the start of a run).
3. Otherwise count upward while `x + 1, x + 2, ...` are in the set, and keep the longest length.""",
     solution="""def longest_consecutive(nums):
    values = set(nums)
    best = 0
    for x in values:
        if x - 1 in values:          # not the start of a run: it will be counted from its start
            continue
        length = 1
        while x + length in values:
            length += 1
        best = max(best, length)
    return best""",
     why="""Each run is counted exactly once, from its smallest value, so the inner `while` loops add up to at most n
steps in total across the whole function. Together with O(1) set lookups this gives O(n). Without the "start of run"
check, a run of length L is walked from each of its L values, which is O(n^2) for a single long run.

**Follow-ups (what if...):**
- *Is sorting acceptable?* Sorting and one pass is O(n log n), uses less memory and is fine to mention, but say that
  the hash-set version meets the O(n) requirement.
- *What if you must return the run itself?* Keep the start value of the best run and return
  `list(range(start, start + best))`.
- *What if numbers arrive as a stream and you need the current best after each one?* Use a hash map from the ends of
  runs to their lengths (merge left and right neighbours on insert), or union-find over values.
- *What if the data is too large for one machine?* Sort or range-partition by value so each run lives on one worker,
  then merge runs that cross partition boundaries.""",
     complexity="O(n) time, O(n) space for the set.",
     mistakes="Counting from every value (O(n^2) on long runs). Forgetting duplicates (sorting solutions must skip "
              "equal neighbours, not reset the run). Returning 1 for an empty list.",
     learn=["algo-hashing"],
     source=("LeetCode 128", "https://leetcode.com/problems/longest-consecutive-sequence/"))

ex.save()
