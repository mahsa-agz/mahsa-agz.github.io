"""Day 28 algorithms (mock exam, hard band): Partition Labels, Longest Increasing Path in a Matrix,
Serialize and Deserialize Binary Tree."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from _algo_hard_common import BIG, TREE, lc, compute, MOCK_INTRO

ex = Exam(28, "algorithms", intro=MOCK_INTRO + " Suggested split: 12 + 25 + 23 minutes. This is the last mock "
          "before the full exam round tomorrow: practise talking while you code.")
ex.setup(BIG + "\n\n" + TREE)

# ---------------------------------------------------------------- Q1 Partition Labels (763)
SOL1 = '''def partition_labels_brute(s):
    """Try every cut: a cut after i is allowed if no letter appears on both sides. O(n^2)."""
    sizes, start = [], 0
    for i in range(len(s)):
        if not set(s[start:i + 1]) & set(s[i + 1:]):
            sizes.append(i + 1 - start)
            start = i + 1
    return sizes

def partition_labels(s):
    """Greedy: extend the current part to the last occurrence of every letter inside it. O(n)."""
    last = {ch: i for i, ch in enumerate(s)}      # last index of each letter
    sizes, start, end = [], 0, 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])                  # this part must reach at least here
        if i == end:                              # nothing inside the part appears later: cut
            sizes.append(end - start + 1)
            start = i + 1
    return sizes

rng = random.Random(763)
for _ in range(3000):
    s = "".join(rng.choice("abcdef") for _ in range(rng.randint(1, 14)))
    assert partition_labels(s) == partition_labels_brute(s), s
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN1 = '''rng = random.Random(7630)
blocks = []
for i in range(13):                              # 13 blocks, block i uses only two letters
    pair = chr(97 + 2 * i) + chr(98 + 2 * i)
    blocks.append("".join(rng.choice(pair) for _ in range(rng.randint(5000, 20000))))
big_s = "".join(blocks)
big_want = [len(b) for b in blocks]'''
TESTS1 = """check(partition_labels, [
    ("abacdcdeffe", [3, 4, 4]),
    ("a", [1]),
    ("abc", [1, 1, 1]),
    ("aaaa", [4]),
    ("abca", [4]),
    ("xyxzyw", [5, 1]),
    ("qwertyq", [7]),
    ("abcdefabc", [9]),
])
# big test: about 150000 letters in 13 blocks
@GEN@
check_big(f"n = {len(big_s)}", lambda: partition_labels(big_s), big_want, limit=0.5)""".replace("@GEN@", GEN1)

ex.q("Cut a string so letters do not cross", minutes=12, level="medium",
     prompt="""Cut a string `s` of lowercase letters into as **many** pieces as possible so that every letter
appears in **at most one** piece (all copies of a letter end up in the same piece). Return the lengths of the pieces,
from left to right.

Examples:
- `"abacdcdeffe"` -> `[3, 4, 4]` (`"aba" | "cdcd" | "effe"`)
- `"xyxzyw"` -> `[5, 1]` (`"xyxzy" | "w"`)
- `"abc"` -> `[1, 1, 1]`

Constraints: `1 <= len(s) <= 2 * 10**5`. Target: O(n). The big test has about 150000 letters.""",
     stub="def partition_labels(s):\n    pass",
     tests=TESTS1,
     hint1="Signal: each letter defines a span from its first to its last position, and you want the most cuts. "
           "Pattern: **greedy** with the last occurrence of each letter (it is merge intervals in disguise).",
     hint2="""1. One pass to store `last[ch]`, the last index of every letter.
2. Walk the string keeping `end` = the furthest `last[ch]` of the letters in the current piece.
3. When `i == end`, no letter of the piece appears later: cut here, record the length, start a new piece.""",
     solution=SOL1,
     why="""A piece that contains letter `ch` must reach `last[ch]`, so the earliest possible cut is the furthest
last occurrence among the letters seen so far. Cutting as early as possible never hurts later cuts, which is why the
greedy choice gives the maximum number of pieces. Each index is visited twice (once to build `last`, once to cut).
Seen as intervals `[first, last]` per letter, the pieces are exactly the merged intervals.

**Follow-ups the examiner may ask:**
- Return the pieces as strings, or as `(start, end)` index pairs.
- The string is a stream you can read only once: you cannot know the last occurrence; you need two passes or a
  buffer of the open piece.
- Same idea on intervals: "merge overlapping sessions" or "group log lines that share an ID".
- Uppercase and digits too: use a dict (as here), not an array of 26.""",
     complexity="Brute force: O(n^2) (set intersections at every cut). Greedy: O(n) time, O(A) space for the "
                "alphabet A.",
     mistakes="Cutting when a letter's last occurrence is reached instead of the maximum of all of them. Returning "
              "the end indexes instead of the lengths. Forgetting to update `start`.",
     learn=["algo-greedy", "algo-sorting-intervals"], source=("LeetCode 763", lc("partition-labels")))

# ---------------------------------------------------------------- Q2 Longest Increasing Path in a Matrix (329)
SOL2 = '''from collections import deque
from functools import lru_cache

def lip_brute(matrix):
    """DFS from every cell with no memory: exponential when many increasing paths share cells."""
    R, C = len(matrix), len(matrix[0])
    def longest_from(r, c):
        best = 1
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and matrix[nr][nc] > matrix[r][c]:
                best = max(best, 1 + longest_from(nr, nc))
        return best
    return max(longest_from(r, c) for r in range(R) for c in range(C))

def lip_memo(matrix):
    """The classic answer: DFS + memo. Each cell is solved once. Recursion depth = path length."""
    R, C = len(matrix), len(matrix[0])
    @lru_cache(maxsize=None)
    def longest_from(r, c):
        best = 1
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and matrix[nr][nc] > matrix[r][c]:
                best = max(best, 1 + longest_from(nr, nc))
        return best
    return max(longest_from(r, c) for r in range(R) for c in range(C))

def longest_increasing_path(matrix):
    """No recursion: topological sort by layers. Peel off cells with no larger neighbour (local maxima),
    then the cells that become maxima, and so on. The number of layers is the longest path."""
    R, C = len(matrix), len(matrix[0])
    def neighbours(r, c):
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C:
                yield nr, nc
    out = [[0] * C for _ in range(R)]             # number of larger neighbours (edges going "up")
    for r in range(R):
        for c in range(C):
            out[r][c] = sum(matrix[nr][nc] > matrix[r][c] for nr, nc in neighbours(r, c))
    layer = [(r, c) for r in range(R) for c in range(C) if out[r][c] == 0]
    layers = 0
    while layer:
        layers += 1
        nxt = []
        for r, c in layer:
            for nr, nc in neighbours(r, c):
                if matrix[nr][nc] < matrix[r][c]:    # (nr, nc) had an edge up to (r, c)
                    out[nr][nc] -= 1
                    if out[nr][nc] == 0:
                        nxt.append((nr, nc))
        layer = nxt
    return layers

rng = random.Random(329)
for _ in range(1000):
    R, C = rng.randint(1, 5), rng.randint(1, 5)
    m = [[rng.randint(0, 6) for _ in range(C)] for _ in range(R)]
    assert longest_increasing_path(m) == lip_memo(m) == lip_brute(m), m
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

SMALL2 = [[[1, 2, 3], [6, 5, 4], [7, 8, 9]], [[7]], [[1, 1], [1, 1]], [[5, 4], [2, 3]], [[1, 2], [2, 3]],
          [[3, 1, 4], [1, 5, 9], [2, 6, 5]], [[1, 10, 2], [9, 3, 8], [4, 7, 5]], [[0, 1, 2, 3, 4, 5]]]
WANT2 = [compute(SOL2, expr=f"longest_increasing_path({m!r})") for m in SMALL2]
assert WANT2[:5] == [9, 1, 1, 4, 3], WANT2
GEN2 = '''diag = [[r + c for c in range(60)] for r in range(60)]                 # millions of increasing paths
snake = [[r * 150 + (c if r % 2 == 0 else 149 - c) for c in range(150)] for r in range(150)]   # one path of 22500 cells'''
cases2 = ",\n".join(f"    ({m!r}, {w!r})" for m, w in zip(SMALL2, WANT2))
TESTS2 = """check(longest_increasing_path, [
@CASES@,
])
# big tests: a 60 x 60 grid with a huge number of increasing paths, and a 150 x 150 snake (path of 22500 cells)
@GEN@
check_big("60 x 60, value = row + col", lambda: longest_increasing_path(diag), 119, limit=1.0)
check_big("150 x 150 snake", lambda: longest_increasing_path(snake), 22500, limit=2.0)""".replace(
    "@CASES@", cases2).replace("@GEN@", GEN2)
assert compute(SOL2, GEN2, expr="(longest_increasing_path(diag), longest_increasing_path(snake))") == (119, 22500)

ex.q("Longest climb on a height map", minutes=25, level="hard",
     prompt="""You get a grid of integers `matrix`. From a cell you may move up, down, left or right (no diagonals,
no wrap-around). Return the length (number of cells) of the longest path whose values are **strictly increasing**.

Examples:
```
1 2 3
6 5 4
7 8 9
```
-> `9` (follow the snake 1, 2, ..., 9)
- `[[5, 4], [2, 3]]` -> `4` (2, 3, 4, 5)
- `[[1, 1], [1, 1]]` -> `1` (equal values do not count as increasing)

Constraints: up to 200 x 200 cells. The big tests are a 60 x 60 grid where `value = row + col` (searching without
memory explodes) and a 150 x 150 "snake" whose longest path has 22500 cells (a recursive solution goes 22500 calls
deep).""",
     stub="def longest_increasing_path(matrix):\n    pass",
     tests=TESTS2,
     hint1="Signal: longest path in a grid where moves only go to larger values, so there are no cycles (a DAG) and "
           "the answer from a cell never changes. Pattern: **DP on a DAG**: DFS with memo, or topological sort by "
           "layers.",
     hint2="""1. Brute force: DFS from every cell, trying all increasing moves. Exponential.
2. `best(r, c) = 1 + max(best(neighbour))` over larger neighbours. It does not depend on how you arrived, so memoise
   it: each cell is solved once.
3. Deep paths break Python recursion. Iterative alternative: count for every cell how many neighbours are larger
   (its out-degree). Cells with 0 are the ends of paths. Remove them layer by layer (like Kahn's algorithm), lowering
   the counts of their smaller neighbours. The number of layers is the answer.""",
     solution=SOL2,
     why="""Moving only to strictly larger values means you can never come back to a cell, so the moves form a
directed acyclic graph and "longest path from a cell" is well defined and reusable. Memoisation turns the
exponential search into O(R * C) work. The layer version computes the same thing without recursion: a cell is removed
in layer `t` exactly when the longest increasing path starting at it has `t` cells, so the number of layers equals
the longest path.

**Follow-ups the examiner may ask:**
- Return the path itself: store the best next cell for each cell and follow it from the best start.
- Non-decreasing paths (equal values allowed): cycles appear between equal neighbours; you need to merge equal-valued
  plateaus first (strongly connected components).
- Diagonal moves: 8 neighbours, same algorithm.
- Why not BFS from every cell? It would be O((R * C)^2).""",
     complexity="Brute force: exponential. DFS + memo: O(R * C) time and space, recursion depth up to R * C. "
                "Topological layers: O(R * C) time and space, no recursion.",
     mistakes="Forgetting the memo (exponential). Allowing equal values. Using a global visited set like in "
              "flood fill (not needed: the strictly increasing rule already prevents cycles). Recursion depth on "
              "long paths (raise the limit with `sys.setrecursionlimit` or go iterative).",
     learn=["algo-dp-2d", "algo-topological-sort", "algo-graphs-bfs-dfs"],
     source=("LeetCode 329", lc("longest-increasing-path-in-a-matrix")))

# ---------------------------------------------------------------- Q3 Serialize and Deserialize Binary Tree (297)
SOL3 = '''from collections import deque

# Version 1 (first idea, recursive): pre-order with "#" for missing children.
def serialize_rec(root):
    out = []
    def walk(node):
        if node is None:
            out.append("#")
            return
        out.append(str(node.val))
        walk(node.left)
        walk(node.right)
    walk(root)
    return ",".join(out)

def deserialize_rec(data):
    tokens = iter(data.split(","))
    def build():
        t = next(tokens)
        if t == "#":
            return None
        node = TreeNode(int(t))
        node.left = build()
        node.right = build()
        return node
    return build()

# Version 2 (final): level order with BFS. Same O(n), but no recursion, so very deep trees work.
def serialize(root):
    out, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append("#")
            continue
        out.append(str(node.val))
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] == "#":          # trailing markers carry no information
        out.pop()
    return ",".join(out)

def deserialize(data):
    if not data:
        return None
    tokens = data.split(",")
    root = TreeNode(int(tokens[0]))
    queue, i = deque([root]), 1
    while queue and i < len(tokens):
        node = queue.popleft()
        for side in ("left", "right"):
            if i < len(tokens) and tokens[i] != "#":
                child = TreeNode(int(tokens[i]))
                setattr(node, side, child)
                queue.append(child)
            i += 1
    return root

rng = random.Random(297)
for _ in range(1000):
    vals = [rng.randint(-50, 50)] + [rng.choice([None, rng.randint(-50, 50)]) for _ in range(rng.randint(0, 20))]
    want = tree_values(build_tree(vals))
    assert tree_values(deserialize(serialize(build_tree(vals)))) == want
    assert tree_values(deserialize_rec(serialize_rec(build_tree(vals)))) == want
print("round-trip stress test: OK")   # prints: round-trip stress test: OK'''

GEN3 = '''rng = random.Random(2970)
big_vals = [rng.randint(-10**6, 10**6) for _ in range(2**17 - 1)]     # complete tree, 131071 nodes
deep_vals = [rng.randint(-99, 99)]
for _ in range(49999):
    deep_vals += [None, rng.randint(-99, 99)]                         # every node is the right child: depth 50000
big_root, deep_root = build_tree(big_vals), build_tree(deep_vals)
big_want, deep_want = tree_values(big_root), tree_values(deep_root)'''
TESTS3 = """def roundtrip(vals):
    \"\"\"Serializes the tree, checks that the result is a string, then rebuilds it.\"\"\"
    data = serialize(build_tree(vals))
    if not isinstance(data, str):
        return "serialize must return a string, got " + type(data).__name__
    return tree_values(deserialize(data))

def two_trees():
    \"\"\"No hidden state: serialize two trees, then decode them in the opposite order.\"\"\"
    a, b = serialize(build_tree([1, 2, 3])), serialize(build_tree([9, None, 8]))
    return tree_values(deserialize(b)), tree_values(deserialize(a))

check(roundtrip, [
    ([], []),
    ([1], [1]),
    ([1, 2, 3, None, None, 4, 5], [1, 2, 3, None, None, 4, 5]),
    ([-7, None, 12, None, -100], [-7, None, 12, None, -100]),
    ([5, 5, 5, 5], [5, 5, 5, 5]),
    ([100000, -100000], [100000, -100000]),
    ([1, None, 2, None, 3, None, 4], [1, None, 2, None, 3, None, 4]),
    ([0, 0, None, 0, None, 0], [0, 0, None, 0, None, 0]),
])
check(two_trees, [((), ([9, None, 8], [1, 2, 3]))])
# big tests: a complete tree with 131071 nodes, and a chain 50000 nodes deep
@GEN@
check_big("complete tree, 131071 nodes", lambda: tree_values(deserialize(serialize(big_root))), big_want, limit=2.0)
check_big("chain 50000 deep", lambda: tree_values(deserialize(serialize(deep_root))), deep_want, limit=2.0)""".replace(
    "@GEN@", GEN3)

ex.q("Save a tree as text and load it back", minutes=23, level="hard",
     prompt="""Write two functions:
- `serialize(root)`: turn a binary tree into a **string**.
- `deserialize(data)`: turn that string back into the same tree (same shape, same values).

You choose the format. Values are integers (negative values and duplicates allowed). The functions must not keep
any hidden state between calls: the tests serialize two trees and decode them in the other order.

Trees in the tests are level-order lists (`build_tree` and `tree_values` are in the setup cell); a test passes if
`tree_values(deserialize(serialize(tree)))` gives back the same list.

Examples (one possible format):
- tree `[1, 2, 3, None, None, 4, 5]` -> `"1,2,3,#,#,4,5"` -> the same tree
- empty tree -> `""` -> `None`

Constraints: up to `1.3 * 10**5` nodes. One big test is a chain 50000 nodes deep.""",
     stub="def serialize(root):\n    pass\n\n\ndef deserialize(data):\n    pass",
     tests=TESTS3,
     hint1="Signal: you must record the **shape** of the tree, not just the values, so missing children need a "
           "marker. Pattern: **tree traversal** (BFS level order or DFS pre-order) with null markers.",
     hint2="""1. A traversal alone (only in-order, for example) is ambiguous: many trees give the same sequence. Add a
   marker such as `#` for every missing child.
2. Level order: BFS, write the value of each node or `#` for `None`, join with commas, drop trailing `#`.
3. Rebuild with a queue: the first token is the root; then for each node taken from the queue, the next two tokens are
   its left and right child (create them and push them, or skip `#`).
4. Pre-order with `#` also works and is shorter to write, but it recurses: think about the 50000-deep chain.""",
     solution=SOL3,
     why="""With a marker for every missing child, a pre-order or level-order sequence describes exactly one tree,
because when we read the tokens back we always know which position the next token belongs to. Level order pairs
naturally with a queue on both sides, so it is iterative and handles any depth; it also matches the LeetCode format.
Every node and every `None` child is written once, so the string has O(n) tokens and both directions are O(n).

**Follow-ups the examiner may ask:**
- The tree is a **BST** (LeetCode 449): pre-order values alone are enough (rebuild with value bounds), no markers.
- Make the string smaller: binary encoding of the values, or a bitmap for the shape plus the values.
- N-ary tree: write each node's number of children after its value.
- Very large trees that do not fit in memory: stream the tokens (generator) instead of building one big string.
- Why does using only in-order fail? `[1, 2]` and `[2, None, 1]` both give `2, 1`.""",
     complexity="Both functions O(n) time and O(n) space. The recursive pre-order version also needs O(h) call "
                "stack, which fails for h = 50000 in Python unless the recursion limit is raised.",
     mistakes="Storing only values without null markers (shape is lost). Splitting on a separator that can appear "
              "in values (for example `-` as the separator breaks negative numbers). Global counters or lists that keep "
              "state between calls.",
     learn=["algo-trees", "algo-design", "algo-graphs-bfs-dfs"],
     source=("LeetCode 297", lc("serialize-and-deserialize-binary-tree")))

ex.save()
