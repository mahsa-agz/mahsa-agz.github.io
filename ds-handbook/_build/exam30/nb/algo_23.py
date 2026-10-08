"""Day 23 algorithms (hard): Edit Distance, Pacific Atlantic Water Flow, Merge k Sorted Lists."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from _algo_hard_common import BIG, LIST, lc, compute

ex = Exam(23, "algorithms")
ex.setup(BIG + "\n\n" + LIST)

# ---------------------------------------------------------------- Q1 Edit Distance (72)
SOL1 = '''def edit_distance_brute(a, b):
    """Plain recursion on the first characters: exponential (about 3^(m+n) calls)."""
    if not a or not b:
        return len(a) + len(b)
    if a[0] == b[0]:
        return edit_distance_brute(a[1:], b[1:])
    return 1 + min(edit_distance_brute(a[1:], b),       # delete a[0]
                   edit_distance_brute(a, b[1:]),       # insert b[0]
                   edit_distance_brute(a[1:], b[1:]))   # replace a[0] by b[0]

def edit_distance(a, b):
    """Bottom-up DP with two rows. prev[j] = distance between a[:i-1] and b[:j]."""
    m, n = len(a), len(b)
    prev = list(range(n + 1))                 # turning "" into b[:j] takes j inserts
    for i in range(1, m + 1):
        cur = [i] + [0] * n                   # turning a[:i] into "" takes i deletes
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1]          # last letters match: no cost
            else:
                cur[j] = 1 + min(prev[j],     # delete a[i-1]
                                 cur[j - 1],  # insert b[j-1]
                                 prev[j - 1]) # replace
        prev = cur
    return prev[n]

rng = random.Random(72)
for _ in range(1500):
    a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 6)))
    b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 6)))
    assert edit_distance(a, b) == edit_distance_brute(a, b), (a, b)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN1 = '''rng = random.Random(7272)
big_a = "".join(rng.choice("acgt") for _ in range(1000))
big_b = "".join(rng.choice("acgt") for _ in range(1000))'''
ANS1 = compute("import random", SOL1, GEN1, expr="edit_distance(big_a, big_b)")
TESTS1 = """check(edit_distance, [
    (("data", "date"), 1),
    (("", "abc"), 3),
    (("abc", ""), 3),
    (("same", "same"), 0),
    (("sunday", "saturday"), 3),
    (("kitten", "sitting"), 3),
    (("flaw", "lawn"), 2),
    (("ab", "ba"), 2),
])
# big test: two random DNA-like strings of length 1000
@GEN@
check_big("two strings of length 1000", lambda: edit_distance(big_a, big_b), @ANS@, limit=3.0)""".replace(
    "@GEN@", GEN1).replace("@ANS@", repr(ANS1))

ex.q("Fewest edits between two words", minutes=18, level="medium",
     prompt="""Given two strings `a` and `b`, return the smallest number of single-character edits that turn `a`
into `b`. An edit is one of: **insert** a character, **delete** a character, **replace** a character.

Examples:
- `"data"` -> `"date"`: `1` (replace the last `a` by `e`)
- `"sunday"` -> `"saturday"`: `3` (insert `a`, insert `t`, replace `n` by `r`)
- `""` -> `"abc"`: `3`

Constraints: `0 <= len(a), len(b) <= 1000`. The big test uses two strings of length 1000, so plain recursion is far
too slow, and a recursive memo can hit Python's recursion limit (depth up to `m + n`).""",
     stub="def edit_distance(a, b):\n    pass",
     tests=TESTS1,
     hint1="Signal: two strings, \"minimum number of operations\", and the choice at each step only depends on "
           "two prefixes. Pattern: **2D dynamic programming** on prefixes.",
     hint2="""1. Let `dp[i][j]` = edits to turn `a[:i]` into `b[:j]`. Base cases: `dp[i][0] = i`, `dp[0][j] = j`.
2. If `a[i-1] == b[j-1]`: `dp[i][j] = dp[i-1][j-1]`.
3. Else `1 + min(dp[i-1][j] (delete), dp[i][j-1] (insert), dp[i-1][j-1] (replace))`.
4. Fill row by row; keep only the previous row to get O(n) memory.""",
     solution=SOL1,
     why="""Look at the last characters of the two prefixes. If they match, they cost nothing and we are left with the
shorter prefixes. If not, the last operation was a delete, an insert or a replace, and each leaves a smaller
subproblem we already solved. The brute force solves the same pair of prefixes many times; the table solves each of
the `(m + 1) * (n + 1)` pairs once. Bottom-up filling also avoids recursion depth problems.

**Follow-ups the examiner may ask:**
- Return the list of edits, not just the count: keep the full table and walk back from `dp[m][n]`.
- Only answer "is the distance at most k?": fill only the band `|i - j| <= k`, O(n * k).
- Only inserts and deletes are allowed: the answer is `m + n - 2 * LCS(a, b)`.
- Different costs per operation (e.g. replace costs 2): same recurrence with weights.
- Spell suggestions over a dictionary of a million words: you cannot compare against all of them; use a BK-tree,
  or candidate generation with n-gram or deletion indexes, then rank by edit distance.""",
     complexity="Brute force: exponential. DP: O(m * n) time, O(min(m, n)) extra space with two rows "
                "(swap the strings so the shorter one is the row).",
     mistakes="Off by one between string indexes and table indexes (`a[i-1]` is the i-th character). Wrong base row "
              "(must be `0, 1, 2, ...`). Mixing up which neighbour is insert and which is delete (the count is the "
              "same, but explaining it wrong costs points). Recursive memo with depth 2000 (RecursionError).",
     learn=["algo-dp-2d"], source=("LeetCode 72", lc("edit-distance")))

# ---------------------------------------------------------------- Q2 Pacific Atlantic Water Flow (417)
SOL2 = '''from collections import deque

def two_coasts_brute(heights):
    """From every cell, search downhill and see which coasts it reaches. O((R*C)^2)."""
    R, C = len(heights), len(heights[0])
    out = []
    for r in range(R):
        for c in range(C):
            west = east = False
            seen, stack = {(r, c)}, [(r, c)]
            while stack:
                x, y = stack.pop()
                west |= x == 0 or y == 0
                east |= x == R - 1 or y == C - 1
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < R and 0 <= ny < C and (nx, ny) not in seen and heights[nx][ny] <= heights[x][y]:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            if west and east:
                out.append([r, c])
    return out

def two_coasts(heights):
    """Reverse thinking: walk UPHILL from each coast with BFS, then intersect the two reachable sets."""
    R, C = len(heights), len(heights[0])
    def climb(starts):
        seen = set(starts)
        queue = deque(starts)
        while queue:
            x, y = queue.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < R and 0 <= ny < C and (nx, ny) not in seen and heights[nx][ny] >= heights[x][y]:
                    seen.add((nx, ny))
                    queue.append((nx, ny))
        return seen
    west = climb([(r, 0) for r in range(R)] + [(0, c) for c in range(C)])
    east = climb([(r, C - 1) for r in range(R)] + [(R - 1, c) for c in range(C)])
    return sorted([r, c] for r, c in west & east)

rng = random.Random(417)
for _ in range(500):
    R, C = rng.randint(1, 6), rng.randint(1, 6)
    h = [[rng.randint(0, 4) for _ in range(C)] for _ in range(R)]
    assert two_coasts(h) == sorted(two_coasts_brute(h)), h
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

SMALL2 = {
    "spiral": [[1, 2, 3], [8, 9, 4], [7, 6, 5]],
    "one": [[7]],
    "row": [[1, 2, 3]],
    "flat": [[2, 2], [2, 2]],
    "valley": [[5, 5, 5], [5, 1, 5], [5, 5, 5]],
    "slope": [[1, 2], [3, 4]],
    "ridge": [[3, 3, 3, 3], [3, 1, 1, 3], [3, 3, 3, 0]],
}
WANT2 = {k: compute(SOL2, expr=f"two_coasts({v!r})") for k, v in SMALL2.items()}
GEN2 = '''rng = random.Random(4170)
big_h = [[9 if rng.random() < 0.1 else rng.choice((4, 5)) if rng.random() < 0.02 else 5 for _ in range(300)]
         for _ in range(300)]    # one huge plateau at height 5 with scattered walls and pits'''
ANS2 = compute("import random", SOL2, GEN2, expr="len(two_coasts(big_h))")
cases2 = ",\n".join(f"    ({v!r}, {WANT2[k]!r})" for k, v in SMALL2.items())
TESTS2 = """def any_order(res):
    \"\"\"Compares the cells in any order.\"\"\"
    try:
        return sorted(tuple(x) for x in res)
    except TypeError:
        return res

check(two_coasts, [
@CASES@,
], key=any_order)
# big test: 300 x 300 grid, mostly one flat plateau (long paths, deep recursion if you use DFS)
@GEN@
check_big("300 x 300 grid (count of cells)", lambda: len(two_coasts(big_h)), @ANS@, limit=2.0)""".replace(
    "@CASES@", cases2).replace("@GEN@", GEN2).replace("@ANS@", repr(ANS2))

ex.q("Rain that reaches both coasts", minutes=17, level="medium",
     prompt="""An island is a grid `heights` of land heights. The **west sea** touches the top row and the left
column. The **east sea** touches the bottom row and the right column. Rain on a cell flows to any of its 4 neighbours
whose height is **lower or equal**, and from a border cell it flows into the sea next to that border.

Return all cells `[r, c]` from which rain can reach **both** seas (any order).

Example:
```
1 2 3
8 9 4
7 6 5
```
-> `[[0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]`. For example the `9` flows to `8` (west) and to `4`
(east). The `1` in the corner only reaches the west sea.

Constraints: grid up to 300 x 300. The big test has large flat areas, so searching from every cell is too slow, and
a recursive search can go 90000 levels deep.""",
     stub="def two_coasts(heights):\n    pass",
     tests=TESTS2,
     hint1="Signal: \"which cells can reach the border\" asked for every cell. Search **backwards** from the "
           "targets instead of forwards from every start. Pattern: **multi-source BFS/DFS on a grid** (reverse flow).",
     hint2="""1. Brute force: from every cell, walk downhill and check which seas you touch. O((R*C)^2).
2. Reverse it: water flows downhill from a cell to the sea exactly when you can walk **uphill** (to `>=`) from the
   sea to the cell.
3. BFS from all west border cells at once, walking to neighbours with height `>=` the current one. Same for east.
4. Answer = cells in both visited sets. Use an iterative BFS (deque), not recursion.""",
     solution=SOL2,
     why="""All cells share the same two targets, so instead of asking R*C questions ("does this cell reach the
sea?") we ask two ("which cells can the sea climb to?"). Each BFS visits every cell at most once, so the work is
O(R*C). Starting the BFS from all border cells at once is the multi-source idea also used in rotting oranges and
walls-and-gates problems.

**Follow-ups the examiner may ask:**
- Water flows only to strictly lower cells: change `>=` to `>` in the climb.
- Diagonal flow: 8 neighbours.
- The grid is 10^4 x 10^4 and does not fit in memory: process it in tiles, or use union-find over equal-height
  plateaus; mention external memory.
- Return the count only, or the cells that reach exactly one sea: set operations on the two visited sets.""",
     complexity="Brute force: O((R*C)^2). Reverse BFS: O(R*C) time and space.",
     mistakes="Walking downhill from the sea (wrong direction, must be `>=`). Forgetting the corner cells that "
              "touch both seas. Recursive DFS on a big flat grid (RecursionError). Marking cells visited when popped "
              "instead of when pushed (duplicates in the queue).",
     learn=["algo-graphs-bfs-dfs", "algo-grid-simulation"], source=("LeetCode 417", lc("pacific-atlantic-water-flow")))

# ---------------------------------------------------------------- Q3 Merge k Sorted Lists (23)
SOL3 = '''import heapq

def merge_two(a, b):
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next

def merge_k_lists_brute(lists):
    """Merge the lists one after another: O(k * N) because the result is re-walked k times."""
    result = None
    for head in lists:
        result = merge_two(result, head)
    return result

def merge_k_lists(lists):
    """Min-heap of the current head of each list: always take the smallest. O(N log k)."""
    heap = [(head.val, i, head) for i, head in enumerate(lists) if head]
    heapq.heapify(heap)                       # i breaks ties, so ListNode objects are never compared
    dummy = tail = ListNode()
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next

rng = random.Random(23)
for _ in range(1000):
    data = [sorted(rng.randint(-5, 5) for _ in range(rng.randint(0, 5))) for _ in range(rng.randint(0, 6))]
    want = sorted(v for lst in data for v in lst)
    assert list_values(merge_k_lists([build_list(x) for x in data])) == want
    assert list_values(merge_k_lists_brute([build_list(x) for x in data])) == want
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

TESTS3 = """def merge_on(lists):
    return list_values(merge_k_lists([build_list(x) for x in lists]))

check(merge_on, [
    ([[1, 4, 9], [2, 3, 10], [5]], [1, 2, 3, 4, 5, 9, 10]),
    ([], []),
    ([[]], []),
    ([[], [0]], [0]),
    ([[1, 1, 2], [1, 3]], [1, 1, 1, 2, 3]),
    ([[-5, 0], [-3], [7, 8, 9]], [-5, -3, 0, 7, 8, 9]),
    ([[2], [1]], [1, 2]),
    ([[1, 2, 3]], [1, 2, 3]),
])
# big test: 2000 sorted lists, 100000 nodes in total
rng = random.Random(2323)
big_lists = [sorted(rng.randint(0, 10**6) for _ in range(rng.randint(0, 100))) for _ in range(2000)]
big_want = sorted(v for lst in big_lists for v in lst)
big_heads = [build_list(x) for x in big_lists]
check_big(f"k = 2000 lists, N = {len(big_want)} nodes", lambda: list_values(merge_k_lists(big_heads)), big_want, limit=1.5)"""

ex.q("Combine many sorted chains", minutes=20, level="hard",
     prompt="""You get a list of `k` linked lists, each sorted in ascending order. Merge them into **one** sorted
linked list and return its head. Reuse the existing nodes (do not just collect the values into a Python list).

The setup cell has `ListNode` (`.val`, `.next`), `build_list([...])` and `list_values(head)`. Tests show lists as
Python lists.

Examples:
- `[[1, 4, 9], [2, 3, 10], [5]]` -> `[1, 2, 3, 4, 5, 9, 10]`
- `[]` -> `[]`, and `[[], [0]]` -> `[0]`

Constraints: `0 <= k <= 10**4`, total number of nodes `N <= 10**5`, values may repeat and may be negative. Target:
O(N log k). The big test has 2000 lists.""",
     stub="def merge_k_lists(lists):\n    pass",
     tests=TESTS3,
     hint1="Signal: at every step you need the smallest of k candidates, and the candidates change by one each "
           "step. Pattern: **heap** (priority queue) of the k current heads. Divide and conquer also works.",
     hint2="""1. Brute force: merge list 1 with list 2, then the result with list 3, ... That is O(k * N).
2. Push `(head.val, i, head)` for every non-empty list into a min-heap (`i` breaks ties: nodes cannot be compared).
3. Pop the smallest, append it to the result, push its `next` if there is one.
4. Alternative: merge the lists in pairs, round after round (like merge sort): also O(N log k).""",
     solution=SOL3,
     why="""The next node of the result is always one of the k current heads, and the heap gives the smallest of
them in O(log k). Every node enters and leaves the heap once, so the total is O(N log k). The sequential merge is
slower because the growing result is walked again for every new list. Collecting all values and sorting is
O(N log N) and allocates new nodes; it is acceptable as a first answer, but the examiner wants the heap.

**Follow-ups the examiner may ask:**
- Divide and conquer: pair up lists and merge them in rounds; O(N log k) time and O(1) extra space (no heap).
- The lists are huge files on disk (external sort): the same k-way merge with a heap, reading each file in buffered
  chunks.
- The inputs are infinite sorted streams: the heap version works as a generator that yields one value at a time.
- Remove duplicates while merging: skip a node whose value equals the last value written.""",
     complexity="Brute force (one by one): O(k * N). Heap: O(N log k) time, O(k) extra space. Divide and conquer: "
                "O(N log k) time, O(1) extra space (iterative).",
     mistakes="Pushing `(val, node)` only: equal values then compare `ListNode` objects and raise `TypeError`. "
              "Forgetting empty lists (`None` heads). Creating new nodes for every value. Not linking the last node.",
     learn=["algo-heap", "algo-linked-list"], source=("LeetCode 23", lc("merge-k-sorted-lists")))

ex.save()
