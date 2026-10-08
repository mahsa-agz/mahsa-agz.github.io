"""Day 10 algorithms (easy band, two mediums): Number of Islands, Merge Intervals, Range Sum Query
+ bonus Implement Queue using Stacks."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from algo_common import OPS_CODE, lc

ex = Exam(10, "algorithms")
ex.setup(OPS_CODE)
ex.text("""The setup cell gives you `check_ops(cls, ops, args, expected)`, which replays a list of method calls on a
class (LeetCode style) and prints PASS or FAIL for every returned value.""")

ex.q("Count the islands", minutes=20, level="medium",
     prompt="""`grid` is a map of `"1"` (land) and `"0"` (water). An island is a group of land cells connected up,
down, left or right (not diagonally). Return the number of islands.

Example:
```
["1", "1", "0", "0", "0"]
["1", "1", "0", "0", "0"]      ->  3
["0", "0", "1", "0", "0"]
["0", "0", "0", "1", "1"]
```
Follow-ups to answer out loud:
1. The grid is 10,000 x 10,000. What can go wrong with a recursive solution in Python?
2. You may not modify the input grid. What changes?
3. The grid is too big for memory and arrives one row at a time. How could you still count islands?""",
     stub="def num_islands(grid):\n    pass",
     tests="""G1 = [["1", "1", "1", "1", "0"],
      ["1", "1", "0", "1", "0"],
      ["1", "1", "0", "0", "0"],
      ["0", "0", "0", "0", "0"]]
G2 = [["1", "1", "0", "0", "0"],
      ["1", "1", "0", "0", "0"],
      ["0", "0", "1", "0", "0"],
      ["0", "0", "0", "1", "1"]]
check(num_islands, [
    (G1, 1),
    (G2, 3),
    ([["0"]], 0),
    ([["1"]], 1),
    ([["1", "0", "1"], ["0", "1", "0"], ["1", "0", "1"]], 5),
    ([["1", "1", "1"], ["0", "0", "1"], ["1", "1", "1"]], 1),
    ([], 0),
])""",
     hint1="Signal: count connected groups of cells on a grid. Pattern: **graph traversal on a grid (DFS or BFS), "
           "one traversal per island**.",
     hint2="""1. Loop over every cell. When you find a `"1"` that is not visited yet, add 1 to the count.
2. From that cell, run BFS or DFS and mark every connected land cell as visited (for example set it to `"0"`,
   or put it in a `seen` set).
3. Each cell is visited once, so the total is O(rows * cols).""",
     solution='''from collections import deque

def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    seen = set()                                   # keeps the input unchanged (follow-up 2)
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                count += 1
                seen.add((r, c))
                queue = deque([(r, c)])            # BFS: no recursion limit (follow-up 1)
                while queue:
                    i, j = queue.popleft()
                    for ni, nj in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                        if 0 <= ni < rows and 0 <= nj < cols and grid[ni][nj] == "1" and (ni, nj) not in seen:
                            seen.add((ni, nj))
                            queue.append((ni, nj))
    return count''',
     why="Each island is one connected component of the grid graph. Every time the outer loop meets an unvisited "
         "land cell, it is the first cell of a new island, and the BFS marks the whole island so it is never "
         "counted again. Follow-up 1: recursive DFS on a huge island goes deeper than Python's recursion limit "
         "(about 1000), so use BFS or an explicit stack. Follow-up 2: use a `seen` set (O(rows * cols) memory) "
         "instead of overwriting cells. Follow-up 3: keep only the previous row's labels and merge labels that "
         "touch with union-find, counting a component when it can no longer grow.",
     complexity="O(rows * cols) time and space.",
     mistakes="Marking a cell visited when it is popped instead of when it is pushed (the same cell enters the "
              "queue many times). Counting diagonal neighbours. Comparing with the integer `1` instead of the "
              "string `\"1\"`.",
     learn=["algo-graphs-bfs-dfs", "algo-union-find"], source=("LeetCode 200", lc("number-of-islands")))

ex.q("Combine overlapping time ranges", minutes=20, level="medium",
     prompt="""`intervals` is a list of `[start, end]` pairs in any order. Merge every group of overlapping intervals
and return the merged list sorted by start. Intervals that only touch (`[1, 4]` and `[4, 5]`) count as overlapping.

Examples:
- `[[1, 3], [2, 6], [8, 10], [15, 18]]` -> `[[1, 6], [8, 10], [15, 18]]`
- `[[1, 4], [4, 5]]` -> `[[1, 5]]`
- `[[8, 9], [1, 2], [2, 3], [10, 12], [9, 10]]` -> `[[1, 3], [8, 12]]`

Follow-ups to answer out loud:
1. The input is already sorted by start. What is the cost now?
2. Intervals arrive one at a time (a stream of user sessions) and you must keep the merged list up to date. Which
   data structure would you use?""",
     stub="def merge(intervals):\n    pass",
     tests="""check(merge, [
    ([[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
    ([[1, 4], [4, 5]], [[1, 5]]),
    ([[1, 4], [0, 4]], [[0, 4]]),
    ([[1, 4], [2, 3]], [[1, 4]]),
    ([[5, 6]], [[5, 6]]),
    ([[8, 9], [1, 2], [2, 3], [10, 12], [9, 10]], [[1, 3], [8, 12]]),
    ([], []),
])""",
     hint1="Signal: ranges that may overlap, in random order. Pattern: **sort by start, then sweep** (intervals).",
     hint2="""1. Sort the intervals by start.
2. Keep a result list. For each interval: if the result is empty or the interval starts after the last merged end,
   append a copy of it.
3. Otherwise extend: `last[1] = max(last[1], end)`.""",
     solution='''def merge(intervals):
    out = []
    for start, end in sorted(intervals):          # sort by start
        if out and start <= out[-1][1]:           # overlaps (or touches) the last merged range
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return out''',
     why="After sorting by start, an interval can only overlap the most recent merged range: every earlier range "
         "ends before that one starts. So one sweep with one comparison per interval is enough. The `max` matters "
         "when an interval is fully inside the last one (`[1, 4]` then `[2, 3]`). Follow-up 1: no sort needed, "
         "O(n). Follow-up 2: keep merged ranges in a balanced tree or sorted list keyed by start (for example "
         "`sortedcontainers.SortedList`), find the neighbours of the new interval with binary search and merge "
         "only those, O(log n) plus the merged ones per insert. In SQL this is a gaps-and-islands question.",
     complexity="O(n log n) time for the sort, O(n) space for the output.",
     mistakes="Forgetting to sort. `out[-1][1] = end` without `max` (shrinks `[1, 4]` to `[1, 3]` when `[2, 3]` "
              "follows). Using `<` and missing touching intervals. Appending the caller's inner list and then "
              "mutating it.",
     learn=["algo-sorting-intervals"], source=("LeetCode 56", lc("merge-intervals")))

ex.q("Many range-sum questions on one list", minutes=15, level="easy",
     prompt="""Design a class `NumArray(nums)` with one method `sumRange(left, right)` that returns
`nums[left] + ... + nums[right]` (both ends included). The list never changes, but `sumRange` will be called a very
large number of times, so each call should be O(1).

Example: `NumArray([-2, 0, 3, -5, 2, -1])`, then `sumRange(0, 2)` -> `1`, `sumRange(2, 5)` -> `-1`,
`sumRange(0, 5)` -> `-3`.

Follow-up to answer out loud: what if values can also be updated between queries?""",
     stub='''class NumArray:
    def __init__(self, nums):
        pass

    def sumRange(self, left, right):
        pass''',
     tests="""check_ops(NumArray,
    ["NumArray", "sumRange", "sumRange", "sumRange"],
    [[[-2, 0, 3, -5, 2, -1]], [0, 2], [2, 5], [0, 5]],
    [None, 1, -1, -3])
check_ops(NumArray, ["NumArray", "sumRange"], [[[5]], [0, 0]], [None, 5])
check_ops(NumArray,
    ["NumArray", "sumRange", "sumRange", "sumRange"],
    [[[1, 2, 3, 4]], [1, 3], [3, 3], [0, 3]],
    [None, 9, 4, 10])""",
     hint1="Signal: many sum queries over ranges of a fixed list. Pattern: **prefix sum** (precompute once, answer "
           "each query with one subtraction).",
     hint2="""1. In `__init__`, build `pre` with `pre[0] = 0` and `pre[i + 1] = pre[i] + nums[i]`.
2. `sumRange(left, right)` is `pre[right + 1] - pre[left]`.""",
     solution='''class NumArray:
    def __init__(self, nums):
        self.pre = [0]
        for x in nums:
            self.pre.append(self.pre[-1] + x)

    def sumRange(self, left, right):
        return self.pre[right + 1] - self.pre[left]''',
     why="`pre[right + 1]` is the sum of everything up to `right`, and `pre[left]` is the sum of everything before "
         "`left`; the difference is exactly the range. Paying O(n) once makes every query O(1). The leading 0 "
         "removes the special case `left = 0`. Follow-up: with updates, one update would change O(n) prefix "
         "values; a Fenwick tree (binary indexed tree) or segment tree gives O(log n) updates and queries.",
     complexity="O(n) to build, O(1) per query, O(n) space.",
     mistakes="Summing the slice in every call (O(n) per query). Off-by-one: `pre[right] - pre[left - 1]` breaks "
              "for `left = 0` without the leading 0.",
     learn=["algo-prefix-sum"], source=("LeetCode 303", lc("range-sum-query-immutable")))

ex.q("A queue built from two stacks (bonus)", minutes=12, level="easy",
     prompt="""Optional. Build a first-in, first-out queue `MyQueue` using only stack operations (python list `append`,
`pop()` from the end, `[-1]`, `len`). Methods: `push(x)`, `pop()` (remove and return the front), `peek()` (return
the front), `empty()`. Each operation should be O(1) amortized.

Example: push 1, push 2, `peek()` -> `1`, `pop()` -> `1`, `empty()` -> `False`.""",
     stub='''class MyQueue:
    def __init__(self):
        pass

    def push(self, x):
        pass

    def pop(self):
        pass

    def peek(self):
        pass

    def empty(self):
        pass''',
     tests="""check_ops(MyQueue,
    ["MyQueue", "push", "push", "peek", "pop", "empty"],
    [[], [1], [2], [], [], []],
    [None, None, None, 1, 1, False])
check_ops(MyQueue,
    ["MyQueue", "push", "push", "pop", "push", "pop", "peek", "pop", "empty"],
    [[], [1], [2], [], [3], [], [], [], []],
    [None, None, None, 1, None, 2, 3, 3, True])""",
     hint1="Signal: reverse the order twice to get first-in, first-out. Pattern: **stack** (two stacks, lazy "
           "transfer) as a small **design** problem.",
     hint2="""1. `inbox` receives every push. `outbox` serves pops and peeks.
2. When `outbox` is empty and you need the front, move everything from `inbox` to `outbox` (this reverses the
   order, so the oldest item ends on top).
3. Never move items while `outbox` still has some: they are older than everything in `inbox`.""",
     solution='''class MyQueue:
    def __init__(self):
        self.inbox, self.outbox = [], []

    def push(self, x):
        self.inbox.append(x)

    def _shift(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())

    def pop(self):
        self._shift()
        return self.outbox.pop()

    def peek(self):
        self._shift()
        return self.outbox[-1]

    def empty(self):
        return not self.inbox and not self.outbox''',
     why="Pouring one stack into another reverses it, so the oldest element comes out first. Each element is "
         "moved from `inbox` to `outbox` at most once, so n operations cost O(n) in total: O(1) amortized, even "
         "though a single `pop` can take O(n).",
     complexity="O(1) amortized per operation, O(n) space.",
     mistakes="Moving items back and forth on every call (O(n) per operation). Refilling `outbox` while it still "
              "has items (breaks the order in the second test). `empty()` checking only one stack.",
     learn=["algo-stack", "algo-design"], source=("LeetCode 232", lc("implement-queue-using-stacks")))

ex.save()
