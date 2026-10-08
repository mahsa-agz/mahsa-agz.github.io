"""Day 26 algorithms (hard): Max Consecutive Ones III, Word Ladder, Binary Tree Maximum Path Sum."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from _algo_hard_common import BIG, TREE, lc, compute

ex = Exam(26, "algorithms")
ex.setup(BIG + "\n\n" + TREE)

# ---------------------------------------------------------------- Q1 Max Consecutive Ones III (1004)
SOL1 = '''def longest_ones_brute(bits, k):
    """Every start, extend while at most k zeros are inside. O(n^2)."""
    best = 0
    for i in range(len(bits)):
        zeros = 0
        for j in range(i, len(bits)):
            zeros += bits[j] == 0
            if zeros > k:
                break
            best = max(best, j - i + 1)
    return best

def longest_ones(bits, k):
    """Sliding window that holds at most k zeros. O(n)."""
    left = zeros = best = 0
    for right, b in enumerate(bits):
        zeros += b == 0
        while zeros > k:                 # too many outages inside: shrink from the left
            zeros -= bits[left] == 0
            left += 1
        best = max(best, right - left + 1)
    return best

rng = random.Random(1004)
for _ in range(3000):
    bits = [rng.randint(0, 1) for _ in range(rng.randint(1, 14))]
    k = rng.randint(0, 4)
    assert longest_ones(bits, k) == longest_ones_brute(bits, k), (bits, k)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN1 = '''rng = random.Random(10040)
big_bits = [1 if rng.random() < 0.7 else 0 for _ in range(300000)]'''
ANS1 = compute(SOL1, GEN1, expr="longest_ones(big_bits, 1000)")
W1 = compute(SOL1, expr="longest_ones([0, 1, 0, 0, 1, 1, 0, 1], 2)")
TESTS1 = """check(longest_ones, [
    (([1, 1, 0, 0, 1, 1, 1, 0, 1], 1), 5),
    (([1, 1, 0, 0, 1, 1, 1, 0, 1], 2), 7),
    (([0, 0, 0], 0), 0),
    (([0, 0, 0], 2), 2),
    (([1, 1, 1], 0), 3),
    (([0], 1), 1),
    (([1, 0, 1, 0, 1], 5), 5),
    (([0, 1, 0, 0, 1, 1, 0, 1], 2), @W1@),
])
# big test: 300000 minutes, k = 1000
@GEN@
check_big("n = 300000, k = 1000", lambda: longest_ones(big_bits, 1000), @ANS@, limit=1.0)""".replace(
    "@W1@", repr(W1)).replace("@GEN@", GEN1).replace("@ANS@", repr(ANS1))

ex.q("Longest uptime after a few repairs", minutes=12, level="medium",
     prompt="""A monitoring log has one entry per minute: `1` if the service was up, `0` if it was down. You are
allowed to "repair" at most `k` down minutes (turn a `0` into a `1`). Return the length of the longest run of
consecutive up minutes you can get.

Examples:
- `bits = [1, 1, 0, 0, 1, 1, 1, 0, 1], k = 1` -> `5` (repair the `0` at index 7: indexes 4 to 8)
- same `bits`, `k = 2` -> `7` (repair indexes 2 and 3: indexes 0 to 6)
- `bits = [0, 0, 0], k = 0` -> `0`

Constraints: `1 <= len(bits) <= 3 * 10**5`, `0 <= k <= len(bits)`. Target: O(n). The big test has 300000 minutes.""",
     stub="def longest_ones(bits, k):\n    pass",
     tests=TESTS1,
     hint1="Signal: \"longest contiguous run\" with a budget (\"at most k\" bad items inside). Pattern: "
           "**variable-size sliding window**.",
     hint2="""1. Rephrase: find the longest window that contains at most `k` zeros.
2. Move `right` forward and count the zeros inside the window.
3. While the count is above `k`, move `left` forward (and decrease the count if a zero leaves).
4. After each step the window is valid: update the best length.""",
     solution=SOL1,
     why="""Repairing the zeros inside a window turns it into a run of ones, so the question is "longest window with
at most k zeros". If a window is valid, every smaller window inside it is valid too, so for each right end we only
need the leftmost valid start, and that start never moves backwards. Both pointers move at most n times.

**Follow-ups the examiner may ask:**
- The log is an endless stream and `k = 1`: remember only the index of the last zero (in general, a deque with the
  positions of the last `k + 1` zeros).
- Return the start and end minute of the best run, not just its length.
- Different repair costs per minute and a budget: the same window with a running cost sum (costs must be
  non-negative).
- A shorter trick: the window never needs to shrink by more than one step (`if` instead of `while`), because only a
  longer window can improve the answer. Be ready to explain why it still works.""",
     complexity="Brute force: O(n^2). Sliding window: O(n) time, O(1) space.",
     mistakes="Shrinking only once when the window can be invalid by more than one zero (with `while` logic). "
              "Updating the answer before the window is valid again. Flipping the input in place. Off by one in "
              "`right - left + 1`.",
     learn=["algo-sliding-window"], source=("LeetCode 1004", lc("max-consecutive-ones-iii")))

# ---------------------------------------------------------------- Q2 Word Ladder (127)
SOL2 = '''from collections import deque

def ladder_length_brute(begin, end, words):
    """BFS where neighbours are found by comparing with every word in the list. O(N^2 * L)."""
    words = list(dict.fromkeys(words))
    if end not in words:
        return 0
    queue, seen = deque([(begin, 1)]), {begin}
    while queue:
        w, d = queue.popleft()
        if w == end:
            return d
        for nw in words:
            if nw not in seen and sum(a != b for a, b in zip(w, nw)) == 1:
                seen.add(nw)
                queue.append((nw, d + 1))
    return 0

def ladder_length(begin, end, words):
    """BFS where neighbours are generated: change one letter at a time and look it up in a set. O(N * L * 26)."""
    words = set(words)
    if end not in words:
        return 0
    queue, seen = deque([(begin, 1)]), {begin}
    while queue:
        w, d = queue.popleft()
        if w == end:
            return d
        for i in range(len(w)):
            for ch in "abcdefghijklmnopqrstuvwxyz":
                nw = w[:i] + ch + w[i + 1:]
                if nw in words and nw not in seen:
                    seen.add(nw)                  # mark when pushed, not when popped
                    queue.append((nw, d + 1))
    return 0

rng = random.Random(127)
for _ in range(500):
    pool = ["".join(rng.choice("ab") for _ in range(3)) for _ in range(rng.randint(1, 8))]
    b, e = "".join(rng.choice("ab") for _ in range(3)), rng.choice(pool)
    assert ladder_length(b, e, pool) == ladder_length_brute(b, e, pool)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN2 = '''rng = random.Random(1270)
pool = set()
while len(pool) < 5000:
    pool.add("".join(rng.choice("abcd") for _ in range(7)))
big_words = sorted(pool)
rng.shuffle(big_words)
big_begin, big_end, big_list = big_words[0], big_words[1], big_words[1:]'''
ANS2 = compute(SOL2, GEN2, expr="ladder_length(big_begin, big_end, big_list)")
CW = '["cord", "card", "ward", "warm", "worm", "word", "corm", "wore"]'
TESTS2 = """check(ladder_length, [
    (("cold", "warm", @CW@), 5),
    (("cold", "warm", ["cord", "card", "ward"]), 0),
    (("hit", "hot", ["hot"]), 2),
    (("a", "c", ["a", "b", "c"]), 2),
    (("abc", "xyz", ["abz", "ayz", "xyz"]), 4),
    (("aaa", "bbb", ["aab", "abb", "bbb", "aba", "baa"]), 4),
    (("lost", "cost", ["most", "fost"]), 0),
    (("abc", "abd", ["xyz", "abd"]), 2),
])
# big test: 5000 random 7-letter words over a, b, c, d
@GEN@
check_big("5000 words of length 7", lambda: ladder_length(big_begin, big_end, big_list), @ANS@, limit=1.0)""".replace(
    "@CW@", CW).replace("@GEN@", GEN2).replace("@ANS@", repr(ANS2))

ex.q("From one word to another, one letter at a time", minutes=22, level="hard",
     prompt="""You get a start word `begin`, a target word `end` and a list `words`. In one step you may change
**exactly one letter**, and every word you pass through (including `end`, but not `begin`) must be in `words`.
Return the **number of words** in the shortest chain from `begin` to `end` (counting both), or `0` if no chain exists.
All words have the same length and use lowercase letters.

Example: `begin = "cold"`, `end = "warm"`,
`words = ["cord", "card", "ward", "warm", "worm", "word", "corm", "wore"]` -> `5`
(`cold -> cord -> card -> ward -> warm`; `cold -> cord -> word -> worm -> warm` is just as short).

More examples:
- same words without `"warm"` -> `0` (the target must be in the list)
- `begin = "hit"`, `end = "hot"`, `words = ["hot"]` -> `2`

Constraints: up to 5000 words of length up to 10. The big test has 5000 words, so comparing every pair of words is too
slow.""",
     stub="def ladder_length(begin, end, words):\n    pass",
     tests=TESTS2,
     hint1="Signal: \"shortest number of steps\" where every step costs the same, and the states are words. "
           "Pattern: **BFS on an implicit graph** (nodes = words, edges = one-letter changes).",
     hint2="""1. Put `words` in a set. If `end` is not in it, return 0.
2. BFS from `begin` with distance 1. For the word you pop, generate all neighbours: for each position try the 26
   letters, keep the ones in the set and not yet seen.
3. Mark a word as seen when you push it. Return the distance when you pop `end`.
4. Generating neighbours costs `L * 26` per word, instead of comparing with all N words.""",
     solution=SOL2,
     why="""Every step has the same cost, so BFS finds the shortest chain: it explores all chains of length d before
any chain of length d + 1. The graph is never built explicitly. The brute force finds neighbours by comparing a word
with all N others (O(N * L) per word, O(N^2 * L) in total); generating the `L * 25` possible one-letter changes and
checking a hash set is O(L * 26) lookups per word (each lookup hashes a string of length L).

**Follow-ups the examiner may ask:**
- **Bidirectional BFS**: grow from both ends and always expand the smaller frontier; it visits far fewer words.
- Pattern buckets: map `"c*ld"`, `"co*d"`, ... to the words that match; neighbours are the words in the same
  buckets. Good when the alphabet is large.
- Return all the shortest chains (LeetCode 126): BFS that records parents per level, then backtrack.
- Steps may also insert or delete a letter: the neighbour generator changes; BFS stays the same.""",
     complexity="Brute force: O(N^2 * L). Generated neighbours: O(N * L * 26) set lookups (each O(L) to hash), "
                "O(N) space.",
     mistakes="Counting edges instead of words (off by one). Marking words visited when popped (the same word is "
              "queued many times). Forgetting that `end` must be in the list. Using DFS (finds a chain, not the "
              "shortest).",
     learn=["algo-graphs-bfs-dfs", "algo-hashing"], source=("LeetCode 127", lc("word-ladder")))

# ---------------------------------------------------------------- Q3 Binary Tree Maximum Path Sum (124)
SOL3 = '''def max_path_sum_brute(root):
    """Try every node as the top of the path; recompute the best downward paths each time.
    O(n * h): O(n^2) on a chain."""
    def best_down(node):                     # best path that starts at node and goes down (may stop anywhere)
        if node is None:
            return 0
        return node.val + max(0, best_down(node.left), best_down(node.right))
    best, stack = float("-inf"), [root]
    while stack:
        node = stack.pop()
        if node:
            best = max(best, node.val + max(0, best_down(node.left)) + max(0, best_down(node.right)))
            stack += [node.left, node.right]
    return best

def max_path_sum_recursive(root):
    """One post-order pass. gain(node) = best downward path from node; the answer may bend at node."""
    best = float("-inf")
    def gain(node):
        nonlocal best
        if node is None:
            return 0
        left = max(gain(node.left), 0)       # a negative branch is dropped
        right = max(gain(node.right), 0)
        best = max(best, node.val + left + right)    # path that bends here
        return node.val + max(left, right)           # a parent can only use one side
    gain(root)
    return best

def max_path_sum(root):
    """Same idea, iterative (no recursion limit): visit children before parents using a reversed pre-order."""
    order, stack = [], [root]
    while stack:
        node = stack.pop()
        if node:
            order.append(node)
            stack += [node.left, node.right]
    best, gain = float("-inf"), {None: 0}
    for node in reversed(order):             # every child appears after its parent in `order`
        left, right = max(gain[node.left], 0), max(gain[node.right], 0)
        best = max(best, node.val + left + right)
        gain[node] = node.val + max(left, right)
    return best

rng = random.Random(124)
for _ in range(1000):
    vals = [rng.randint(-10, 10)] + [rng.choice([None, rng.randint(-10, 10)]) for _ in range(rng.randint(0, 14))]
    root = build_tree(vals)
    assert max_path_sum(root) == max_path_sum_recursive(root) == max_path_sum_brute(root), vals
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

SMALL3 = [[1, 2, 3], [-3], [-2, -1], [2, -1, 3], [-1, -2, -3],
          [10, 2, 10, 20, 1, None, -25, None, None, None, None, 3, 4],
          [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1],
          [1, -2, -3, 1, 3, -2, None, -1]]
WANT3 = [compute(TREEX, SOL3, expr=f"max_path_sum(build_tree({v!r}))") for TREEX in [TREE] for v in SMALL3]
GEN3 = '''rng = random.Random(1240)
big_vals = [rng.randint(-1000, 1000) for _ in range(2**17 - 1)]       # complete tree, 131071 nodes
deep_vals = [rng.randint(-50, 100)]
for _ in range(19999):
    deep_vals += [rng.randint(-50, 100), None]                          # every node is the left child: depth 20000
big_root, deep_root = build_tree(big_vals), build_tree(deep_vals)'''
ANS3a = compute(TREE, SOL3, GEN3, expr="max_path_sum(big_root)")
ANS3b = compute(TREE, SOL3, GEN3, expr="max_path_sum(deep_root)")
cases3 = ",\n".join(f"    ({v!r}, {w!r})" for v, w in zip(SMALL3, WANT3))
TESTS3 = """def max_path_on(vals):
    return max_path_sum(build_tree(vals))

check(max_path_on, [
@CASES@,
])
# big tests: a complete tree with 131071 nodes, and a chain 20000 nodes deep
@GEN@
check_big("complete tree, 131071 nodes", lambda: max_path_sum(big_root), @A@, limit=1.0)
check_big("chain 20000 deep", lambda: max_path_sum(deep_root), @B@, limit=1.0)""".replace(
    "@CASES@", cases3).replace("@GEN@", GEN3).replace("@A@", repr(ANS3a)).replace("@B@", repr(ANS3b))

ex.q("Best-scoring path anywhere in a tree", minutes=20, level="hard",
     prompt="""Each node of a binary tree holds an integer (it may be negative). A **path** is a sequence of nodes
where neighbours in the sequence are parent and child, and no node appears twice. It does not have to pass through
the root and it may "bend" at one node (go up the left side and down the right side). It has at least one node.
Return the largest possible sum of the values on a path.

Trees are given as level-order lists (`None` = missing child); `build_tree` is in the setup cell.

Examples:
- `[1, 2, 3]` -> `6` (path 2 - 1 - 3)
- `[2, -1, 3]` -> `5` (path 2 - 3; the -1 is skipped)
- `[-2, -1]` -> `-1` (a single node; at least one node is required)

Constraints: up to `1.3 * 10**5` nodes. Target: O(n). One big test is a chain 20000 nodes deep: a recursive
solution needs `sys.setrecursionlimit` or an iterative traversal.""",
     stub="def max_path_sum(root):\n    pass",
     tests=TESTS3,
     hint1="Signal: an answer that can start and end anywhere in a tree, built from what each subtree returns. "
           "Pattern: **tree DP with post-order DFS** (return one value up, update a global answer on the side).",
     hint2="""1. Define `gain(node)` = the best sum of a path that **starts** at `node` and goes **down** one side.
   `gain(node) = node.val + max(0, gain(left), gain(right))` (a negative branch is not taken).
2. The best path that **bends** at `node` is `node.val + max(0, gain(left)) + max(0, gain(right))`. Update a global
   `best` with it at every node.
3. Return `gain` to the parent (only one side, because a path cannot fork).
4. Start `best` at minus infinity (all values may be negative). For the deep chain, process nodes in reversed
   pre-order instead of recursing.""",
     solution=SOL3,
     why="""Every path has exactly one highest node, where it bends (or stops). For that node, the best path is its
value plus the best non-negative downward extension on each side, which is exactly what `gain` of the children gives.
So one post-order pass computes every candidate in O(1) per node. The value returned upward must be a single branch,
since a parent cannot use both of a child's sides. The brute force recomputes `best_down` for every node, which costs
O(n^2) on a chain. The iterative version uses the fact that in a pre-order list every child comes after its parent,
so walking it backwards visits children first.

**Follow-ups the examiner may ask:**
- Return the path itself, not only the sum: also return the best branch choice from `gain` and rebuild it at the
  bending node.
- Path must go from root to a leaf (LeetCode 112/113): simpler, no bending.
- Longest path by number of edges (diameter, LeetCode 543): the same template with `1 + max(...)`.
- The same idea on a general tree (graph with no cycles): keep the two best child gains at each node.""",
     complexity="Brute force: O(n * h), O(n^2) on a chain. Post-order DP: O(n) time, O(h) stack (recursive) or O(n) "
                "memory (iterative).",
     mistakes="Starting `best` at 0 (wrong when all values are negative). Returning `node.val + left + right` to the "
              "parent (that path forks). Not clamping negative child gains to 0. Recursion depth on a 20000-deep "
              "chain (RecursionError).",
     learn=["algo-trees", "algo-dp-1d"], source=("LeetCode 124", lc("binary-tree-maximum-path-sum")))

ex.save()
