"""Day 22 algorithms (hard): Kth Smallest Element in a BST, Trapping Rain Water, Word Search."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from _algo_hard_common import BIG, TREE, lc, compute

ex = Exam(22, "algorithms")
ex.setup(BIG + "\n\n" + TREE)

# ---------------------------------------------------------------- Q1 Kth Smallest Element in a BST (230)
SOL1 = '''def kth_smallest_brute(root, k):
    """Collect every value, sort, pick. O(n log n) time, O(n) space, ignores the BST order."""
    vals, stack = [], [root]
    while stack:
        node = stack.pop()
        if node:
            vals.append(node.val)
            stack += [node.left, node.right]
    return sorted(vals)[k - 1]

def kth_smallest(root, k):
    """Iterative in-order traversal that stops at the k-th node. O(h + k) time, O(h) space."""
    stack, node = [], root
    while stack or node:
        while node:                 # go as far left as possible
            stack.append(node)
            node = node.left
        node = stack.pop()          # next smallest value
        k -= 1
        if k == 0:
            return node.val
        node = node.right           # then the right subtree

# stress test against the brute force on random BSTs
def _insert(root, v):
    if root is None:
        return TreeNode(v)
    cur = root
    while True:
        side = "left" if v < cur.val else "right"
        if getattr(cur, side) is None:
            setattr(cur, side, TreeNode(v))
            return root
        cur = getattr(cur, side)

rng = random.Random(230)
for _ in range(500):
    vals = rng.sample(range(100), rng.randint(1, 30))
    root = None
    for v in vals:
        root = _insert(root, v)
    for k in range(1, len(vals) + 1):
        assert kth_smallest(root, k) == kth_smallest_brute(root, k)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

TESTS1 = """def kth_on(vals, k):
    return kth_smallest(build_tree(vals), k)

check(kth_on, [
    (([50, 30, 70, 20, 40, 60, 80], 1), 20),
    (([50, 30, 70, 20, 40, 60, 80], 4), 50),
    (([50, 30, 70, 20, 40, 60, 80], 7), 80),
    (([5], 1), 5),
    (([1, None, 2, None, 3], 2), 2),
    (([8, 3, 10, 1, 6, None, 14, None, None, 4, 7, 13], 5), 7),
    (([8, 3, 10, 1, 6, None, 14, None, None, 4, 7, 13], 9), 14),
])

# big tests: a balanced BST with 131071 nodes, and a chain 20000 nodes deep (each node is the left child of the previous)
def balanced_bst_values(n):
    \"\"\"Level-order list of a balanced BST holding 1..n.\"\"\"
    out, q = [], deque([(1, n)])
    while q:
        lo, hi = q.popleft()
        if lo > hi:
            out.append(None)
            continue
        mid = (lo + hi) // 2
        out.append(mid)
        q.append((lo, mid - 1))
        q.append((mid + 1, hi))
    while out[-1] is None:
        out.pop()
    return out

big_root = build_tree(balanced_bst_values(2**17 - 1))
deep_vals = [20000]
for v in range(19999, 0, -1):
    deep_vals += [v, None]
deep_root = build_tree(deep_vals)
check_big("balanced BST, 131071 nodes, k = 5", lambda: kth_smallest(big_root, 5), 5, limit=0.5)
check_big("chain 20000 deep, k = 3", lambda: kth_smallest(deep_root, 3), 3, limit=0.5)"""

ex.q("The k-th smallest value in a search tree", minutes=15, level="medium",
     prompt="""You get the root of a **binary search tree** (every value in a left subtree is smaller than the node,
every value in a right subtree is larger; values are unique) and an integer `k`. Return the `k`-th smallest value
(`k = 1` is the minimum).

The tests write a tree as a level-order list (LeetCode style, `None` = missing child). `build_tree(list)` from the
setup cell turns it into `TreeNode` objects with `.val`, `.left`, `.right`.

Examples:
- tree `[50, 30, 70, 20, 40, 60, 80]`, `k = 4` -> `50`
- tree `[1, None, 2, None, 3]` (a chain to the right), `k = 2` -> `2`

Constraints: up to `2 * 10**5` nodes, `1 <= k <= n`. One big test is a chain 20000 nodes deep, so think about
Python's recursion limit (about 1000 by default).""",
     stub="def kth_smallest(root, k):\n    pass",
     tests=TESTS1,
     hint1="Signal: a binary **search** tree and \"k-th smallest\": an in-order walk visits the values in sorted "
           "order. Pattern: **BST in-order traversal** (iterative, with a stack).",
     hint2="""1. Brute force: collect all values, sort, return index `k-1`. Correct but ignores the BST order.
2. Better: in-order walk (left, node, right) produces sorted values; stop at the k-th one.
3. Do it with an explicit stack: push the whole left spine, pop a node, count it, then move to its right child.
4. This also survives the 20000-deep chain because there is no recursion.""",
     solution=SOL1,
     why="""In a BST the in-order sequence is the sorted sequence, so the k-th node visited in order is the answer.
Stopping early means we only touch the left spine (height `h`) plus `k` nodes. The explicit stack replaces the call
stack, so a very deep (unbalanced) tree does not raise `RecursionError`.

**Follow-ups the examiner may ask:**
- The tree changes often (inserts and deletes) and you get many k-th queries: store `size` (number of nodes in the
  subtree) in each node. Then go left if `k <= size(left)`, return the node if `k == size(left) + 1`, else go right
  with `k - size(left) - 1`. That is O(h) per query.
- k-th **largest**: reverse in-order (right, node, left).
- Is the tree a valid BST? (in-order values must be strictly increasing).
- What is `h`? O(log n) for a balanced tree, O(n) for a chain. Mention self-balancing trees (AVL, red-black).""",
     complexity="Brute force: O(n log n) time, O(n) space. Iterative in-order: O(h + k) time, O(h) space.",
     mistakes="Recursive traversal on a very deep tree (RecursionError in Python). Off by one with `k` (1-based). "
              "Traversing the whole tree when you could stop at the k-th node. Using a global counter that is not "
              "reset between calls.",
     learn=["algo-bst", "algo-trees"], source=("LeetCode 230", lc("kth-smallest-element-in-a-bst")))

# ---------------------------------------------------------------- Q2 Trapping Rain Water (42)
SOL2 = '''def trap_brute(heights):
    """For each bar, scan left and right for the tallest walls. O(n^2)."""
    total = 0
    for i in range(len(heights)):
        left_max = max(heights[:i + 1])
        right_max = max(heights[i:])
        total += min(left_max, right_max) - heights[i]
    return total

def trap_prefix(heights):
    """Precompute the tallest wall on each side. O(n) time, O(n) space."""
    n = len(heights)
    if n == 0:
        return 0
    left, right = [0] * n, [0] * n
    left[0], right[-1] = heights[0], heights[-1]
    for i in range(1, n):
        left[i] = max(left[i - 1], heights[i])
    for i in range(n - 2, -1, -1):
        right[i] = max(right[i + 1], heights[i])
    return sum(min(left[i], right[i]) - heights[i] for i in range(n))

def trap(heights):
    """Two pointers: always move the side with the lower wall. O(n) time, O(1) space."""
    lo, hi = 0, len(heights) - 1
    left_max = right_max = total = 0
    while lo < hi:
        if heights[lo] < heights[hi]:
            left_max = max(left_max, heights[lo])     # the right side has a wall at least this high
            total += left_max - heights[lo]
            lo += 1
        else:
            right_max = max(right_max, heights[hi])
            total += right_max - heights[hi]
            hi -= 1
    return total

rng = random.Random(42)
for _ in range(3000):
    h = [rng.randint(0, 6) for _ in range(rng.randint(0, 15))]
    assert trap(h) == trap_prefix(h) == trap_brute(h), h
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN2 = '''rng = random.Random(4242)
big_h = [rng.randint(0, 10000) for _ in range(300000)]'''
ANS2 = compute("import random", SOL2, GEN2, expr="trap(big_h)")
TESTS2 = """check(trap, [
    ([3, 0, 2, 0, 4], 7),
    ([], 0),
    ([5], 0),
    ([1, 2, 3, 4], 0),
    ([4, 3, 2, 1], 0),
    ([2, 0, 2], 2),
    ([5, 1, 1, 1, 5], 12),
    ([0, 3, 0, 1, 0, 3, 0], 8),
])
# big test: 300000 random bars
@GEN@
check_big("n = 300000", lambda: trap(big_h), @ANS@, limit=1.0)""".replace("@GEN@", GEN2).replace("@ANS@", repr(ANS2))

ex.q("Rain between the bars", minutes=22, level="hard",
     prompt="""A list `heights` describes bars of width 1 standing next to each other. After heavy rain, water
collects in the dips between taller bars. Return the total amount of water held (in unit squares).

Water above a bar can rise to the lower of the tallest bar on its left and the tallest bar on its right.

Examples:
- `[3, 0, 2, 0, 4]` -> `7` (3 + 1 + 3 units above the three inner bars)
- `[5, 1, 1, 1, 5]` -> `12`
- `[1, 2, 3, 4]` -> `0` (nothing can hold the water on the left)

Constraints: `0 <= len(heights) <= 3 * 10**5`, heights between 0 and 10**4. Target: O(n) time; then try O(1) extra
space. The big test has 300000 bars.""",
     stub="def trap(heights):\n    pass",
     tests=TESTS2,
     hint1="Signal: the answer at each position depends on the maximum to its left and to its right. Pattern: "
           "**two pointers** from both ends (or prefix and suffix maxima first).",
     hint2="""1. Water above bar `i` is `min(max_left(i), max_right(i)) - heights[i]`.
2. O(n) with O(n) space: build `left_max` and `right_max` arrays in two passes, then sum.
3. O(1) space: pointers `lo` and `hi` at both ends, plus `left_max` and `right_max`.
4. If `heights[lo] < heights[hi]`, the right side already has a wall at least as high as anything that limits `lo`,
   so the water at `lo` is `left_max - heights[lo]`; move `lo`. Otherwise do the same on the right.""",
     solution=SOL2,
     why="""The water level above a bar is set by the shorter of the two tallest walls around it. The brute force
finds those walls with a scan per bar. The prefix arrays store them. The two-pointer version notices that you only
need the **smaller** of the two maxima. The pointer that moves is always the one on the lower side, so `left_max`
never exceeds the tallest bar still waiting on the right. The water at `lo` is therefore limited by `left_max`, a
value we already know (and the same holds for `hi` on the other side).

**Follow-ups the examiner may ask:**
- 2D version (LeetCode 407, a height map): start from all border cells in a min-heap and flood inward, always
  expanding the lowest wall first. O(mn log(mn)).
- Explain the monotonic stack solution: keep bars in decreasing height; when a taller bar arrives, pop and add the
  water trapped in the layer between the new bar and the bar below the popped one.
- Heights arrive as a stream from the left: you cannot finalize water until a taller wall appears on the right; the
  stack method only keeps the still-open bars.
- Bars have different widths: multiply each layer by its width in the stack method.""",
     complexity="Brute force: O(n^2). Prefix maxima: O(n) time, O(n) space. Two pointers: O(n) time, O(1) space.",
     mistakes="Using `max` of both sides instead of `min`. Moving the pointer of the taller side. Adding negative "
              "water (update the max before subtracting). Forgetting empty input.",
     learn=["algo-two-pointers", "algo-prefix-sum", "algo-monotonic-stack"],
     source=("LeetCode 42", lc("trapping-rain-water")))

# ---------------------------------------------------------------- Q3 Word Search (79)
SOL3 = '''from collections import Counter

def exists_plain(board, word):
    """Standard backtracking: try every start cell, walk to neighbours, mark cells in use."""
    R, C = len(board), len(board[0])
    def dfs(r, c, i):
        if i == len(word):
            return True
        if not (0 <= r < R and 0 <= c < C) or board[r][c] != word[i]:
            return False
        board[r][c] = "#"                                  # mark as used on this path
        found = (dfs(r + 1, c, i + 1) or dfs(r - 1, c, i + 1) or
                 dfs(r, c + 1, i + 1) or dfs(r, c - 1, i + 1))
        board[r][c] = word[i]                              # undo (backtrack)
        return found
    return any(dfs(r, c, 0) for r in range(R) for c in range(C))

def exists(board, word):
    """Same backtracking plus two cheap prunings that matter in exams."""
    R, C = len(board), len(board[0])
    if len(word) > R * C:
        return False
    have = Counter(ch for row in board for ch in row)
    need = Counter(word)
    if any(have[ch] < k for ch, k in need.items()):        # pruning 1: not enough letters at all
        return False
    if have[word[0]] > have[word[-1]]:                    # pruning 2: start from the rarer end
        word = word[::-1]
    def dfs(r, c, i):
        if board[r][c] != word[i]:
            return False
        if i == len(word) - 1:
            return True
        board[r][c] = "#"
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and dfs(nr, nc, i + 1):
                board[r][c] = word[i]
                return True
        board[r][c] = word[i]
        return False
    return any(dfs(r, c, 0) for r in range(R) for c in range(C))

rng = random.Random(79)
for _ in range(2000):
    R, C = rng.randint(1, 4), rng.randint(1, 4)
    board = [[rng.choice("ab") for _ in range(C)] for _ in range(R)]
    word = "".join(rng.choice("ab") for _ in range(rng.randint(1, 7)))
    assert exists([row[:] for row in board], word) == exists_plain([row[:] for row in board], word)
print("stress test vs plain backtracking: OK")   # prints: stress test vs plain backtracking: OK'''

TESTS3 = """B = [["C", "A", "T", "S"],
     ["O", "R", "E", "D"],
     ["D", "O", "G", "S"]]
check(exists, [
    ((B, "CATS"), True),
    ((B, "COD"), True),
    ((B, "DOGS"), True),
    ((B, "SDS"), True),
    ((B, "CAC"), False),
    ((B, "GOOD"), False),
    (([["a"]], "a"), True),
    (([["a"]], "ab"), False),
])
# big test: a 6 x 6 board full of "a"; the word is 15 "a" then "b", so the answer is False
board_a = [["a"] * 6 for _ in range(6)]
check_big("6 x 6 board of a, word a*15 + b", lambda: exists(board_a, "a" * 15 + "b"), False, limit=1.0)"""

ex.q("Spell a word on the letter grid", minutes=18, level="medium",
     prompt="""You get a grid of letters `board` and a string `word`. Return `True` if you can spell `word` by
starting at any cell and stepping to horizontally or vertically adjacent cells, **using each cell at most once**.

Example board:
```
C A T S
O R E D
D O G S
```
- `"CATS"` -> `True` (top row)
- `"COD"` -> `True` (down the first column)
- `"CAC"` -> `False` (the same `C` cannot be used twice)
- `"GOOD"` -> `False`

Constraints: board up to 6 x 6, word length up to 15. The big test is a 6 x 6 board full of `a` with the word
`"aaaaaaaaaaaaaaab"`: plain search tries a huge number of paths, so add a cheap check that rules it out early.""",
     stub="def exists(board, word):\n    pass",
     tests=TESTS3,
     hint1="Signal: build a path step by step, each step has a few choices, and you must undo a choice that leads "
           "nowhere. Pattern: **backtracking** (DFS on the grid with a visited mark).",
     hint2="""1. For every cell, start a DFS `dfs(r, c, i)`: does the path starting here spell `word[i:]`?
2. Fail fast: out of the grid, or `board[r][c] != word[i]`.
3. Mark the cell (e.g. set it to `"#"`), try the 4 neighbours with `i + 1`, then restore the letter.
4. Pruning: if the board does not contain enough copies of some letter, return `False` before any search.
   Optional: if the last letter is rarer than the first, search for the reversed word.""",
     solution=SOL3,
     why="""Backtracking explores every path but cuts a path as soon as one letter does not match. Marking the cell in
place and restoring it after the recursion gives the "each cell once" rule with no extra memory. The worst case is
still exponential (`4 * 3^(L-1)` paths per start cell), which is why the letter-count check matters: on a board of
`a`s it turns a search of millions of paths into a count that takes microseconds. Starting from the rarer end of the
word shrinks the number of starting points.

**Follow-ups the examiner may ask:**
- Many words on the same board (LeetCode 212, Word Search II): put all words in a trie and run one DFS per cell
  that walks the trie; remove found words from the trie.
- Diagonal moves allowed: 8 neighbours, same code.
- Do not modify the input: use a `visited` set (or restore the board, as here).
- What is the complexity? O(R * C * 3^L) in the worst case, O(L) recursion depth.""",
     complexity="O(R * C * 3^L) time in the worst case (4 directions for the first step, then 3), O(L) recursion "
                "depth. The pruning is O(R * C + L).",
     mistakes="Forgetting to restore the cell after the recursion (later paths see `#`). Checking `visited` "
              "after recursing instead of before. Testing the bounds before `i == len(word)`: then a word whose last "
              "letter has no free neighbour (for example a 1 x 1 board) is never found. Copying the board on every call.",
     learn=["algo-backtracking", "algo-grid-simulation"], source=("LeetCode 79", lc("word-search")))

ex.save()
