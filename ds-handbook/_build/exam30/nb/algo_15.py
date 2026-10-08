import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _algo_mid_common import BIG, TREE

ex = Exam(15, "algorithms")
ex.setup(BIG + "\n\n" + TREE)
ex.text("The setup cell also defines `TreeNode`, `build(level_order_list)` (LeetCode's tree format, `None` = no "
        "child) and `find(root, value)` for the tree question.")

# ---------------------------------------------------------------- Q1 non-overlapping intervals (greedy)
ex.q("Fewest meetings to cancel", minutes=18,
     prompt="""You get a list of meetings as `[start, end]` pairs. Return the **minimum number of meetings to remove**
so that the remaining meetings do not overlap. Meetings that only touch (one ends at 5, the next starts at 5) do not
overlap.

Example: `[[1, 2], [2, 3], [3, 4], [1, 3]]` gives `1`: remove `[1, 3]` and the other three fit one after another.

Second example: `[[1, 4], [2, 3], [3, 6], [5, 7]]` gives `2`. At most two of these meetings can be kept together
(for example `[2, 3]` and `[3, 6]`), so two must go.

Constraints: up to 100,000 meetings, times between -50,000 and 50,000.""",
     stub="""def erase_overlap_intervals(intervals):
    pass""",
     tests="""check(erase_overlap_intervals, [
    ([[1, 4], [2, 3], [3, 6], [5, 7]], 2),
    ([[1, 2], [2, 3], [3, 4], [1, 3]], 1),
    ([[1, 2], [1, 2], [1, 2]], 2),                  # identical meetings
    ([[1, 2], [2, 3]], 0),                          # touching is fine
    ([], 0),                                        # no meetings
    ([[5, 9]], 0),                                  # one meeting
    ([[1, 100], [11, 22], [1, 11], [2, 12]], 2),     # one long meeting covers the rest
    ([[-5, -1], [-3, 0], [0, 4]], 1),               # negative times
])
# larger input: 100,000 meetings [i, i + 2], shuffled; keeping every second one is optimal
import random
big = [[i, i + 2] for i in range(100_000)]
random.Random(15).shuffle(big)
check_big("100,000 meetings", lambda: erase_overlap_intervals(big), 50_000)""",
     hint1="""Signal: choose the largest set of non-overlapping intervals (removals = total - kept). Keeping the
meeting that **ends earliest** always leaves the most room for the rest. Pattern: **greedy** (sort by end time).""",
     hint2="""1. Sort the meetings by their end time.
2. Keep the first one; remember `last_end`.
3. For each next meeting: if `start >= last_end`, keep it and set `last_end = end`; otherwise it overlaps, so count a
   removal.
4. Return the number of removals.""",
     solution="""def erase_overlap_intervals(intervals):
    removed = 0
    last_end = float("-inf")
    for start, end in sorted(intervals, key=lambda iv: iv[1]):   # earliest end first
        if start >= last_end:      # fits after the last kept meeting
            last_end = end
        else:                      # overlaps: drop this one (it ends later than the kept one)
            removed += 1
    return removed""",
     why="""Exchange argument: take any optimal plan. Its first meeting can be swapped for the meeting with the
earliest end time without creating an overlap, because that meeting ends no later. Repeating this argument shows the
greedy choice is never worse. Sorting by end, not by start, is what makes the greedy correct: sorting by start would
keep `[1, 100]` in the fifth test and block everything.

For the first test: sorted by end gives `[2, 3], [1, 4], [3, 6], [5, 7]`. Keep `[2, 3]`, drop `[1, 4]`, keep
`[3, 6]`, drop `[5, 7]`: 2 removals.

**Follow-ups (what if...):**
- *What if you need the minimum number of rooms so that no meeting is removed (LeetCode 253)?* Sort by start and keep
  a min-heap of end times (or sweep sorted starts and ends); the answer is the maximum overlap.
- *What if meetings have weights (value) and you maximise the kept value?* Greedy fails; use DP over meetings sorted
  by end plus binary search for the last compatible meeting (LeetCode 1235).
- *What if touching meetings count as overlapping?* Change `start >= last_end` to `start > last_end`.
- *What if you also sort by start instead?* It can be made to work (on overlap keep the one with the smaller end), but
  sorting by end is simpler to prove and explain.""",
     complexity="O(n log n) time for the sort, O(n) space for the sorted copy (O(1) extra if you sort in place).",
     mistakes="Sorting by start and keeping the first meeting of each overlap. Treating touching meetings as "
              "overlapping. Returning the number kept instead of the number removed. An O(n^2) DP over pairs.",
     learn=["algo-greedy", "algo-sorting-intervals"],
     source=("LeetCode 435", "https://leetcode.com/problems/non-overlapping-intervals/"))

# ---------------------------------------------------------------- Q2 LCA of binary tree (trees)
ex.q("Closest shared ancestor in a tree", minutes=18,
     prompt="""Given the root of a binary tree (not a search tree, values are not ordered) and two different nodes
`p` and `q` that are both in the tree, return the **lowest** node that has both `p` and `q` in its subtree. A node
counts as being in its own subtree, so if `p` is an ancestor of `q` the answer is `p`.

Example: `[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]` is

```
        3
      /   \\
     5     1
    / \\   / \\
   6   2 0   8
      / \\
     7   4
```
For `p = 7`, `q = 6` the answer is node `5`. For `p = 5`, `q = 4` the answer is `5`. For `p = 7`, `q = 8` it is `3`.

Your function receives and returns `TreeNode` objects. The tests call it through `lca_value(values, p, q)`, which
builds the tree, finds the nodes and returns the value of your answer.""",
     stub="""def lowest_common_ancestor(root, p, q):
    pass""",
     tests="""def lca_value(values, p, q):
    root = build(values)
    return lowest_common_ancestor(root, find(root, p), find(root, q)).val

example = [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]
check(lca_value, [
    ((example, 7, 6), 5),
    ((example, 5, 4), 5),                     # p is an ancestor of q
    ((example, 7, 8), 3),                     # opposite sides of the root
    ((example, 7, 4), 2),                     # siblings
    ((example, 0, 1), 1),
    (([1, 2], 1, 2), 1),                      # root and its child
    (([1, 2, 3, None, 4], 4, 3), 1),
    (([1, None, 2, None, 3, None, 4], 4, 2), 2),   # chain
])
# larger input: complete tree with 131,071 nodes (node v has children 2v and 2v + 1)
big_root = build(list(range(1, 2**17)))
pairs = [(2**16, 2**17 - 1), (2**16, 2**16 + 1), (2, 2**16), (40_000, 40_001)]
nodes = [(find(big_root, a), find(big_root, b)) for a, b in pairs]
check_big("131,071 nodes, 4 queries", lambda: [lowest_common_ancestor(big_root, a, b).val for a, b in nodes],
          [1, 2**15, 2, 20_000])""",
     hint1="""Signal: a question about two nodes and their relation inside a tree; information must flow **up** from
the subtrees to the parent. Pattern: **tree DFS (post-order)**: each call reports whether it found `p` or `q` below it.""",
     hint2="""1. If the node is `None`, `p` or `q`, return it.
2. Recurse into the left and right subtrees.
3. If both sides return a node, the current node is the split point: return it.
4. Otherwise return whichever side is not `None` (it carries `p`, `q` or an answer found deeper).""",
     solution="""def lowest_common_ancestor(root, p, q):
    if root is None or root is p or root is q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:          # p and q are on different sides: root is the split point
        return root
    return left or right        # pass up whatever was found (or None)""",
     why="""Each call returns "the interesting node found in this subtree": `None` if neither target is below,
the target itself if only one is below, or the answer once both were found. The first node where both sides report
something is the lowest common ancestor, because no lower node sees both. If `p` is an ancestor of `q`, the search
stops at `p` and returns it, which is correct because `p` counts as its own ancestor. Every node is visited at most
once.

**Follow-ups (what if...):**
- *What if the tree is a binary search tree (LeetCode 235)?* Walk down from the root: if both values are smaller go
  left, if both are larger go right, else the current node is the answer. O(h), no recursion needed.
- *What if nodes have parent pointers?* It becomes "intersection of two linked lists": walk up from `p` and `q` (or
  store `p`'s ancestors in a set) without touching the rest of the tree.
- *What if `p` or `q` might not be in the tree (LeetCode 1644)?* Count how many targets were really found; the simple
  version would wrongly return `p` when `q` is missing.
- *What if you get millions of LCA queries on the same tree?* Preprocess with binary lifting (O(n log n), then
  O(log n) per query) or an Euler tour plus a range-minimum structure.
- *What if the tree is very deep (a chain of 100,000 nodes)?* Recursion fails in Python; use an iterative DFS that
  records parents, then walk up from `p` and `q`.""",
     complexity="O(n) time, O(h) space for the recursion (h = tree height).",
     mistakes="Comparing values instead of nodes when values could repeat. Returning as soon as one target is found "
              "without checking the other side (it is fine here only because both are guaranteed to exist). "
              "Using the BST shortcut on a tree that is not a BST.",
     learn=["algo-trees"],
     source=("LeetCode 236", "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/"))

# ---------------------------------------------------------------- Q3 subsets (backtracking)
ex.q("Every possible selection", minutes=15,
     prompt="""Given a list of **distinct** integers, return all possible subsets (the power set), including the
empty one and the full list. Order of the subsets and order inside a subset do not matter, but there must be no
duplicates.

Example: `nums = [4, 7]` gives `[[], [4], [7], [4, 7]]`.
`nums = [1, 2, 3]` gives 8 subsets.

Constraints: up to 15 numbers (2^15 = 32,768 subsets).""",
     stub="""def subsets(nums):
    pass""",
     tests="""from itertools import combinations

def all_subsets(nums):     # reference for the tests (a library shortcut you should NOT use in the exam)
    return [list(c) for r in range(len(nums) + 1) for c in combinations(nums, r)]

check(subsets, [
    ([4, 7], [[], [4], [7], [4, 7]]),
    ([1, 2, 3], [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]),
    ([0], [[], [0]]),                 # one element
    ([], [[]]),                       # empty input: only the empty subset
    ([-1, 5], [[], [-1], [5], [-1, 5]]),
    ([9, 8, 7, 6], all_subsets([9, 8, 7, 6])),
], key=any_order)
# larger input: 15 numbers, 32,768 subsets
nums15 = list(range(15))
check_big("15 numbers, 32,768 subsets", lambda: subsets(nums15), all_subsets(nums15), key=any_order, limit=2.0)""",
     hint1="""Signal: "return **all** subsets / combinations": the output itself is exponential, so you enumerate
choices. For every element you decide "take it or not". Pattern: **backtracking** (DFS over choices with an undo
step). Iterative doubling and bitmasks are equivalent alternatives.""",
     hint2="""1. Keep a `path` list and a start index `i`.
2. In `dfs(i)`: record a copy of `path` (every node of the search tree is a subset).
3. For `j` from `i` to the end: append `nums[j]`, call `dfs(j + 1)`, then pop it (undo).
4. Call `dfs(0)` and return the collected list.""",
     solution="""def subsets(nums):
    out, path = [], []

    def dfs(start):
        out.append(path[:])                 # copy: path keeps changing
        for j in range(start, len(nums)):
            path.append(nums[j])            # choose
            dfs(j + 1)                      # explore with later elements only
            path.pop()                      # undo

    dfs(0)
    return out

# Iterative alternative: every new number doubles the list
def subsets_iterative(nums):
    out = [[]]
    for x in nums:
        out += [s + [x] for s in out]
    return out""",
     why="""Each subset is built exactly once, because `dfs(j + 1)` only adds elements after position `j`, so the
elements of a path always appear in index order and the same set cannot be produced in two orders. The search tree
has 2^n nodes, one per subset. Appending `path[:]` (a copy) matters: appending `path` itself would store the same
list object 2^n times, and it ends up empty.

**Follow-ups (what if...):**
- *What if the input has duplicates (LeetCode 90)?* Sort first and, inside the loop, skip `nums[j]` when `j > start`
  and `nums[j] == nums[j - 1]`.
- *What if you only need subsets of size k (combinations, LeetCode 77)?* Record only when `len(path) == k` and stop
  going deeper at that point.
- *What if n is 40 and you need a subset with a given sum?* 2^40 is too many; use meet-in-the-middle (two halves of
  2^20 each) or DP over sums if the values are small.
- *What if you must stream subsets instead of storing them all (memory)?* Make `subsets` a generator with `yield` or
  iterate masks `0..2^n - 1` and decode each mask with bit operations.""",
     complexity="O(n x 2^n) time (2^n subsets, copying each costs up to n), O(n x 2^n) for the output, O(n) recursion depth.",
     mistakes="Appending `path` instead of a copy. Looping from 0 instead of `start` (creates duplicates like [1, 2] "
              "and [2, 1]). Forgetting the empty subset.",
     learn=["algo-backtracking"],
     source=("LeetCode 78", "https://leetcode.com/problems/subsets/"))

ex.save()
