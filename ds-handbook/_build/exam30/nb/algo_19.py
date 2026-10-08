import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _algo_mid_common import BIG

ex = Exam(19, "algorithms")
ex.setup(BIG)

# ---------------------------------------------------------------- Q1 task scheduler (greedy)
ex.q("Shortest schedule with a cool-down", minutes=18,
     prompt="""A CPU must run a list of tasks, each labelled with a capital letter; every task takes one time unit.
Two runs of the **same** label must be at least `n` units apart (there must be `n` other units between them, which can
be other tasks or idle time). Tasks can run in any order. Return the minimum total number of time units, idle units
included.

Example: `tasks = ["A", "A", "A", "B", "B", "B"]`, `n = 2` gives `8`: `A B idle A B idle A B`.
With `n = 0` the same tasks need just `6` units.

Constraints: up to 100,000 tasks, `0 <= n <= 100`.""",
     stub="""def least_interval(tasks, n):
    pass""",
     tests="""check(least_interval, [
    ((["A", "A", "A", "B", "B", "B"], 2), 8),
    ((["A", "A", "A", "B", "B", "B"], 0), 6),               # no cool-down
    ((["A", "C", "A", "B", "D", "B"], 1), 6),
    ((["A", "A", "A", "B", "B", "B"], 3), 10),
    ((["A"], 5), 1),                                        # one task: no idle at the end
    ((["A", "A", "A"], 2), 7),                              # A idle idle A idle idle A
    ((["A", "A", "A", "A", "B", "C", "D"], 2), 10),
    ((list("ABCDEABCDE"), 4), 10),                          # enough variety: no idle at all
])
# larger input: 100,000 tasks cycling through 26 letters, n = 50
big = [chr(65 + i % 26) for i in range(100_000)]
check_big("100,000 tasks, n = 50", lambda: least_interval(big, 50), 196_150)""",
     hint1="""Signal: scheduling with a "same type must be spaced out" rule; the most frequent task decides the
shape of the schedule. Pattern: **greedy** (count the most frequent task and build frames around it; a max-heap
simulation is the other common answer).""",
     hint2="""1. Count each letter; let `f` = the highest count and `k` = how many letters have that count.
2. The most frequent letter needs `f - 1` full frames of length `n + 1`, plus a last frame holding the `k` letters
   with the top count: `(f - 1) * (n + 1) + k`.
3. If there are so many different tasks that the frames overflow, no idle time is needed and the answer is
   `len(tasks)`. Return the maximum of the two.""",
     solution="""from collections import Counter

def least_interval(tasks, n):
    counts = Counter(tasks)
    f = max(counts.values())                              # highest frequency
    k = sum(1 for c in counts.values() if c == f)         # letters that share it
    return max(len(tasks), (f - 1) * (n + 1) + k)""",
     why="""The most frequent letter appears `f` times and needs `n` units after each run except the last, so the
schedule is at least `(f - 1) * (n + 1) + 1` long, plus one unit for every other letter that is just as frequent (they
also need a slot in the last frame). The other tasks fit into the gaps of the frames; if they do not fit, you can widen
the frames and still have no idle time, so the answer is simply the number of tasks. The answer is the larger of the
two lower bounds, and both are achievable.

**Follow-ups (what if...):**
- *What if you must output an actual schedule, not just its length?* Simulate with a max-heap of counts and a queue
  of tasks that are cooling down: at each time unit run the most frequent available task. O(total time x log 26).
- *What if tasks must run in the given order (LeetCode 2365)?* Then it is a simulation: keep the last run time of each
  task in a hash map and jump ahead when needed.
- *What if there are several CPUs?* The counting formula no longer holds; simulate with heaps per time unit, or
  frame it as a scheduling problem and say that general versions are NP-hard.
- *Data angle:* rate limits per API key or "do not show the same creator twice within n videos" in a feed are the
  same constraint.""",
     complexity="O(T) time for counting T tasks, O(1) space (at most 26 letters).",
     mistakes="Forgetting the `k` letters that tie for the top count. Forgetting `max(len(tasks), ...)`, which gives too "
              "small an answer when there is enough variety. Simulating time step by step with a full scan of the "
              "remaining tasks (slow for large inputs).",
     learn=["algo-greedy", "algo-heap"],
     source=("LeetCode 621", "https://leetcode.com/problems/task-scheduler/"))

# ---------------------------------------------------------------- Q2 product except self (prefix)
ex.q("Product of everything else", minutes=15,
     prompt="""Given a list of integers `nums`, return a list `out` where `out[i]` is the product of all numbers in
`nums` **except** `nums[i]`. Do it in O(n) time and **without using division** (the list may contain zeros).

Example: `nums = [2, 3, 4, 5]` gives `[60, 40, 30, 24]`. `nums = [3, 0, 4]` gives `[0, 12, 0]`.

Constraints: 2 to 100,000 numbers. The tests guarantee every product fits in a normal integer range (Python integers
do not overflow anyway).""",
     stub="""def product_except_self(nums):
    pass""",
     tests="""check(product_except_self, [
    ([2, 3, 4, 5], [60, 40, 30, 24]),
    ([1, 2, 3, 4], [24, 12, 8, 6]),
    ([3, 0, 4], [0, 12, 0]),                   # one zero
    ([0, 0], [0, 0]),                          # two zeros: everything is 0
    ([-1, 1, 0, -3, 3], [0, 0, 9, 0, 0]),
    ([2, 3], [3, 2]),                          # smallest input
    ([-2, -3, 4], [-12, -8, 6]),               # negative numbers
    ([1, 1, 1, 1], [1, 1, 1, 1]),
])
# larger input: 100,000 ones with a single 2 at index 5
big = [1] * 100_000
big[5] = 2
want = [2] * 100_000
want[5] = 1
check_big("100,000 numbers", lambda: product_except_self(big), want)""",
     hint1="""Signal: every position needs an aggregate of "everything to the left" and "everything to the right".
Pattern: **prefix and suffix products** (the multiplication version of prefix sums).""",
     hint2="""1. First pass left to right: `out[i]` = product of all numbers before `i` (start with 1).
2. Second pass right to left with a running `suffix` product (start with 1): `out[i] *= suffix`, then
   `suffix *= nums[i]`.
3. No extra arrays besides the output are needed.""",
     solution="""def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    prefix = 1
    for i in range(n):              # out[i] = product of nums[0..i-1]
        out[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):  # multiply in the product of nums[i+1..n-1]
        out[i] *= suffix
        suffix *= nums[i]
    return out""",
     why="""The product of everything except `nums[i]` splits into "everything left of i" times "everything right of
i". Both parts can be built incrementally in one pass each, so the whole thing is O(n). Division fails with zeros (and
is not allowed); the prefix/suffix approach does not care about zeros at all.

**Follow-ups (what if...):**
- *What if division were allowed?* Count zeros: two or more zeros give all zeros; exactly one zero gives the product of
  the others at that index and 0 elsewhere; no zeros gives `total // nums[i]`. Mention the zero cases explicitly.
- *What if the numbers are floats and the product underflows or overflows?* Work in log space: sum of logs (track
  signs and zeros separately), then exponentiate.
- *What if you need "sum of everything except i"?* Trivial with the total sum; the prefix idea matters for operations
  that have no inverse (max, min, gcd): prefix and suffix maxima give "max of everything except i".
- *What if O(1) extra space is required?* The solution above already uses only the output array plus two variables.""",
     complexity="O(n) time, O(1) extra space besides the output.",
     mistakes="Using division (wrong with zeros). The O(n^2) double loop. Off-by-one: including `nums[i]` itself in the "
              "prefix (update `prefix` after writing `out[i]`).",
     learn=["algo-prefix-sum", "algo-arrays-strings"],
     source=("LeetCode 238", "https://leetcode.com/problems/product-of-array-except-self/"))

# ---------------------------------------------------------------- Q3 shortest path in binary matrix (BFS)
ex.q("Fewest cells from corner to corner", minutes=18,
     prompt="""You get an `n x n` grid of `0` (open) and `1` (blocked). Find the length of the shortest path from the
top-left cell to the bottom-right cell that only uses open cells. From a cell you may move to any of its **8
neighbours** (including diagonals). The length counts the cells on the path, including the start and the end. Return
`-1` if there is no such path (also when the start or the end is blocked).

Example:
```
[[0, 0, 0],
 [1, 1, 0],
 [1, 1, 0]]
```
gives `4`: (0,0) -> (0,1) -> (1,2) -> (2,2).

Constraints: `n` up to 100. The larger tests use a 100 x 100 open grid and a 41 x 41 zig-zag maze.""",
     stub="""def shortest_path_binary_matrix(grid):
    pass""",
     tests="""check(shortest_path_binary_matrix, [
    ([[0, 0, 0], [1, 1, 0], [1, 1, 0]], 4),
    ([[0, 1], [1, 0]], 2),                          # one diagonal step
    ([[1, 0, 0], [1, 1, 0], [1, 1, 0]], -1),        # start blocked
    ([[0, 0], [0, 1]], -1),                         # end blocked
    ([[0]], 1),                                     # start is the end
    ([[1]], -1),
    ([[0, 0, 0], [0, 0, 0], [0, 0, 0]], 3),         # straight down the diagonal
    ([[0, 1, 1], [1, 1, 1], [1, 1, 0]], -1),        # no way through
])
# larger inputs: an open 100 x 100 grid, and a zig-zag maze (walls on every odd row with one gap at alternating ends)
def maze(n):
    g = [[0] * n for _ in range(n)]
    for r in range(1, n, 2):
        g[r] = [1] * n
        g[r][n - 1 if (r // 2) % 2 == 0 else 0] = 0
    return g
check_big("open 100 x 100 grid", lambda: shortest_path_binary_matrix([[0] * 100 for _ in range(100)]), 100)
check_big("41 x 41 zig-zag maze", lambda: shortest_path_binary_matrix(maze(41)), 841)""",
     hint1="""Signal: **shortest** path, every move costs the same (one cell), on a grid. Pattern: **BFS** on the grid
graph with 8 directions. DFS does not give shortest paths without exploring everything.""",
     hint2="""1. If the start or end cell is 1, return -1.
2. Put `(0, 0)` in a queue with distance 1 and mark it visited.
3. Pop a cell; if it is the target return its distance; else push every open, unvisited neighbour among the 8
   directions with distance + 1 and mark it visited **when pushing**.
4. If the queue empties, return -1.""",
     solution="""from collections import deque

def shortest_path_binary_matrix(grid):
    n = len(grid)
    if grid[0][0] or grid[n - 1][n - 1]:
        return -1
    steps = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]   # 8 neighbours
    queue = deque([(0, 0, 1)])
    seen = {(0, 0)}
    while queue:
        r, c, d = queue.popleft()
        if r == n - 1 and c == n - 1:
            return d
        for dr, dc in steps:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not grid[nr][nc] and (nr, nc) not in seen:
                seen.add((nr, nc))                 # mark when pushed: each cell enters the queue once
                queue.append((nr, nc, d + 1))
    return -1""",
     why="""BFS explores cells in order of their distance from the start, so the first time it reaches the target that
distance is the minimum. Each cell is pushed at most once and has 8 neighbours, so the work is linear in the number of
cells. A DFS finds *a* path, not the shortest, unless it explores every path (exponential).

**Follow-ups (what if...):**
- *What if moves have different costs (diagonal costs 1.4, or cells have weights)?* Use Dijkstra with a heap. With a
  good distance heuristic (Chebyshev distance here) use A* to explore fewer cells.
- *What if you need the path itself?* Store `parent[(nr, nc)] = (r, c)` when pushing, then walk back from the target.
- *What if the grid is huge (10,000 x 10,000)?* Bidirectional BFS from both ends roughly square-roots the explored
  area in open grids; also avoid a Python set of tuples (use a flat bytearray for visited).
- *What if you may remove up to k walls (LeetCode 1293)?* Add the number of removals used to the BFS state:
  `(r, c, used)`.
- *What if only 4 directions are allowed?* Use 4 offsets; the open-grid answer becomes `2n - 1`.""",
     complexity="O(n^2) time and space (8 neighbours per cell is a constant factor).",
     mistakes="Forgetting to check that the start and end are open. Marking visited when popping (cells get pushed many "
              "times). Using 4 directions. Counting moves instead of cells (off by one).",
     learn=["algo-graphs-bfs-dfs", "algo-grid-simulation"],
     source=("LeetCode 1091", "https://leetcode.com/problems/shortest-path-in-binary-matrix/"))

ex.save()
