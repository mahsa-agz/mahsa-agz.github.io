import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _algo_mid_common import BIG, TREE

ex = Exam(17, "algorithms")
ex.setup(BIG + "\n\n" + TREE)
ex.text("The setup cell also defines `TreeNode`, `build(level_order_list)` (LeetCode's tree format, `None` = no "
        "child) and `find(root, value)` for the tree question. Q4 is an optional bonus: do it only if you finished "
        "Q1 to Q3 within the time.")

# ---------------------------------------------------------------- Q1 spiral matrix (grid simulation)
ex.q("Read a matrix from the outside in", minutes=15,
     prompt="""Given a matrix with `m` rows and `n` columns (not necessarily square), return all its values in
**clockwise spiral** order: the top row left to right, the right column top to bottom, the bottom row right to left,
the left column bottom to top, then the same for the inner ring, and so on.

Example:
```
[[1,  2,  3,  4],
 [5,  6,  7,  8],
 [9, 10, 11, 12]]
```
gives `[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]`.

Single rows, single columns and an empty matrix (`[]`) must work too. The larger test is a 200 x 150 matrix; it
compares a checksum of your output.""",
     stub="""def spiral_order(matrix):
    pass""",
     tests="""check(spiral_order, [
    ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]], [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]),
    ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [1, 2, 3, 6, 9, 8, 7, 4, 5]),
    ([[7]], [7]),                                         # 1 x 1
    ([[1, 2, 3]], [1, 2, 3]),                             # one row
    ([[1], [2], [3]], [1, 2, 3]),                         # one column
    ([[1, 2], [3, 4], [5, 6], [7, 8]], [1, 2, 4, 6, 8, 7, 5, 3]),   # tall and thin
    ([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], [1, 2, 3, 4, 5, 10, 9, 8, 7, 6]),   # wide and short
    ([], []),                                             # empty matrix
])
# larger input: 200 x 150 matrix of 0..29,999; compares length and a position-weighted checksum
def checksum(order):
    return (len(order), sum((i + 1) * v for i, v in enumerate(order)) % 1_000_000_007)
big = [[r * 150 + c for c in range(150)] for r in range(200)]
check_big("200 x 150 matrix", lambda: checksum(spiral_order(big)), (30_000, 923745738))""",
     hint1="""Signal: walk a grid in a fixed geometric order; the difficulty is boundaries and off-by-one errors, not
an algorithm. Pattern: **grid simulation** with four shrinking boundaries (`top`, `bottom`, `left`, `right`).""",
     hint2="""1. Set `top, bottom, left, right = 0, m - 1, 0, n - 1`.
2. While `top <= bottom and left <= right`: read the top row (`left..right`), then `top += 1`; read the right column
   (`top..bottom`), then `right -= 1`.
3. **Only if** `top <= bottom`, read the bottom row right to left and `bottom -= 1`. **Only if** `left <= right`, read
   the left column bottom to top and `left += 1`.
4. The two checks in step 3 stop a single remaining row or column from being read twice.""",
     solution="""def spiral_order(matrix):
    if not matrix or not matrix[0]:
        return []
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    out = []
    while top <= bottom and left <= right:
        for c in range(left, right + 1):          # top row, left to right
            out.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):          # right column, top to bottom
            out.append(matrix[r][right])
        right -= 1
        if top <= bottom:                         # a bottom row still exists
            for c in range(right, left - 1, -1):
                out.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:                         # a left column still exists
            for r in range(bottom, top - 1, -1):
                out.append(matrix[r][left])
            left += 1
    return out""",
     why="""Each ring is four straight walks, and after each walk the matching boundary moves inward, so every cell is
read exactly once. When the remaining area is a single row or a single column, the first two walks already cover it;
the two `if` checks prevent reading it again backwards (the most common bug).

**Follow-ups (what if...):**
- *What if you must fill an n x n matrix with 1..n^2 in spiral order (LeetCode 59)?* Same four walks, writing instead
  of reading.
- *What if you need to rotate the matrix 90 degrees in place (LeetCode 48)?* Transpose, then reverse each row.
  A similar boundary-careful simulation, very common in Samsung-style tests.
- *What if you prefer a direction vector approach?* Keep `dr, dc` and turn right when the next cell is outside or
  already visited (needs a visited grid or a marker value). Easier to generalise, uses O(mn) extra memory.
- *What if the matrix is huge and stored row by row on disk?* Spiral order jumps between rows constantly; read ring
  by ring or load blocks, because random access dominates the cost.""",
     complexity="O(m x n) time, O(1) extra space besides the output.",
     mistakes="Reading the last row or column twice when m != n (missing the `if` checks). Off-by-one in the reverse "
              "ranges (`left - 1` and `top - 1` as stops). Crashing on `[]`.",
     learn=["algo-grid-simulation", "algo-arrays-strings"],
     source=("LeetCode 54", "https://leetcode.com/problems/spiral-matrix/"))

# ---------------------------------------------------------------- Q2 validate BST (bst)
ex.q("Is this a proper search tree?", minutes=18,
     prompt="""Given the root of a binary tree, return `True` if it is a valid **binary search tree**: for every node,
**all** values in its left subtree are strictly smaller than the node and **all** values in its right subtree are
strictly larger. Duplicates are not allowed. An empty tree is valid.

Example: `[8, 4, 12, 2, 6, 10, 14]` is valid. `[8, 4, 12, None, None, 6, 14]` is **not** valid: 6 is the left child of
12 (fine locally) but it sits in the right subtree of 8 and 6 < 8.

The tests call your function through `valid_bst(values)`, which builds the tree. The larger test uses balanced trees
with 32,767 nodes.""",
     stub="""def is_valid_bst(root):
    pass""",
     tests="""def valid_bst(values):
    return is_valid_bst(build(values))

check(valid_bst, [
    ([8, 4, 12, 2, 6, 10, 14], True),
    ([8, 4, 12, None, None, 6, 14], False),      # only wrong compared with an ancestor
    ([2, 1, 3], True),
    ([5, 1, 4, None, None, 3, 6], False),        # right child smaller than the root
    ([2, 2, 2], False),                          # duplicates are not allowed
    ([1], True),                                 # one node
    ([], True),                                  # empty tree
    ([-2147483648, None, 2147483647], True),     # extreme values (no fake +/- infinity sentinels)
])
# larger inputs: a balanced BST with values 0, 2, 4, ... and the same tree with one deep value made invalid
def balanced(lo, hi):                            # BST over the even numbers 2*lo .. 2*hi
    if lo > hi:
        return None
    mid = (lo + hi) // 2
    return TreeNode(2 * mid, balanced(lo, mid - 1), balanced(mid + 1, hi))

good_tree = balanced(0, 2**15 - 2)
bad_tree = balanced(0, 2**15 - 2)
node = bad_tree.right
while node.left:
    node = node.left
node.val = bad_tree.val - 1                       # fine for its parent, smaller than the root
check_big("valid BST, 32,767 nodes", lambda: is_valid_bst(good_tree), True)
check_big("invalid deep inside, 32,767 nodes", lambda: is_valid_bst(bad_tree), False)""",
     hint1="""Signal: the rule is about **whole subtrees**, not just parent and child, so every node lives inside an
allowed range set by its ancestors. Pattern: **BST property**: DFS that passes down `(low, high)` bounds, or an
in-order traversal that must be strictly increasing.""",
     hint2="""1. Write `ok(node, low, high)`: an empty node is fine; otherwise the value must satisfy `low < val < high`.
2. Recurse: left child with `(low, val)`, right child with `(val, high)`.
3. Start with `low = -inf`, `high = +inf`.
4. In-order alternative: walk left, node, right with a stack; each value must be bigger than the previous one.""",
     solution="""def is_valid_bst(root):
    stack = [(root, float("-inf"), float("inf"))]     # iterative: no recursion limit issues
    while stack:
        node, low, high = stack.pop()
        if node is None:
            continue
        if not (low < node.val < high):
            return False
        stack.append((node.left, low, node.val))      # left subtree: smaller than this node
        stack.append((node.right, node.val, high))    # right subtree: larger than this node
    return True

# Recursive version (shorter, fine for balanced trees):
def is_valid_bst_rec(root, low=float("-inf"), high=float("inf")):
    if root is None:
        return True
    if not (low < root.val < high):
        return False
    return is_valid_bst_rec(root.left, low, root.val) and is_valid_bst_rec(root.right, root.val, high)""",
     why="""A node is constrained by every ancestor: going left sets a new upper bound, going right a new lower bound.
Passing the tightest bounds down checks the whole-subtree rule while visiting each node once. Comparing only a node
with its children misses cases like 6 under 12 under 8. Using real infinities (not `-2**31` sentinels) avoids bugs at
the extreme values.

**Follow-ups (what if...):**
- *What if duplicates are allowed on one side (for example left <= node < right)?* Change the comparisons accordingly;
  say which convention you use.
- *What if you want the in-order approach?* An in-order traversal of a BST is sorted, so check that each value is
  greater than the previous one. It also gives "k-th smallest" (LeetCode 230) for free.
- *What if exactly two nodes were swapped by mistake (LeetCode 99)?* In-order traversal finds the one or two places
  where the order drops; swap those values back.
- *What if the tree is very deep (a sorted insert sequence makes a chain)?* Recursion fails in Python; the iterative
  version above has no such limit. Also mention that a self-balancing tree avoids the chain in the first place.""",
     complexity="O(n) time, O(h) space (h = height; O(n) for a chain, O(log n) when balanced).",
     mistakes="Checking only `left.val < node.val < right.val`. Allowing equal values. Using `-2**31` and `2**31 - 1` "
              "as sentinels (fails when the tree contains them). Using `<=` in the in-order check.",
     learn=["algo-bst", "algo-trees"],
     source=("LeetCode 98", "https://leetcode.com/problems/validate-binary-search-tree/"))

# ---------------------------------------------------------------- Q3 k closest points (heap)
ex.q("Nearest points to the origin", minutes=15,
     prompt="""Given a list of points `[x, y]` on a plane and an integer `k`, return the `k` points closest to the
origin `(0, 0)` by straight-line (Euclidean) distance. Any order is fine. The tests guarantee the answer is unique.

Example: `points = [[3, 3], [5, -1], [-2, 4]]`, `k = 2` gives `[[3, 3], [-2, 4]]` (squared distances 18, 26 and 20).

Constraints: up to 200,000 points, `k` can be much smaller than the number of points.""",
     stub="""def k_closest(points, k):
    pass""",
     tests="""check(k_closest, [
    (([[3, 3], [5, -1], [-2, 4]], 2), [[3, 3], [-2, 4]]),
    (([[1, 3], [-2, 2]], 1), [[-2, 2]]),
    (([[0, 0]], 1), [[0, 0]]),                              # one point at the origin
    (([[1, 1], [2, 2], [3, 3]], 3), [[1, 1], [2, 2], [3, 3]]),  # k = all points
    (([[0, 5], [3, 4], [1, 1]], 1), [[1, 1]]),
    (([[-1, 0], [0, 10], [2, 2]], 2), [[-1, 0], [2, 2]]),   # negative coordinates
    (([[10000, -10000], [-10000, 10000], [1, -1]], 1), [[1, -1]]),
], key=rows_any_order)
# larger input: 200,000 points on the x-axis, shuffled; k = 10
import random
big = [[x, 0] for x in range(1, 200_001)]
random.Random(17).shuffle(big)
check_big("200,000 points, k = 10", lambda: k_closest(big, 10), [[x, 0] for x in range(1, 11)], key=rows_any_order)""",
     hint1="""Signal: "the k smallest by some score" where k is much smaller than n. Pattern: **heap** (keep a max-heap
of size k on squared distance; drop the farthest when it grows past k). Quickselect is the average O(n) alternative.""",
     hint2="""1. Use the squared distance `x*x + y*y` (no square root needed; it keeps the same order).
2. Push `(-dist, x, y)` into a heap (negated, because `heapq` is a min-heap and you want to evict the farthest).
3. If the heap size exceeds k, pop. At the end the heap holds the k closest points.
4. Shortcut: `heapq.nsmallest(k, points, key=lambda p: p[0]**2 + p[1]**2)` does the same.""",
     solution="""import heapq

def k_closest(points, k):
    heap = []                                   # max-heap via negative distance, size <= k
    for x, y in points:
        d = x * x + y * y
        if len(heap) < k:
            heapq.heappush(heap, (-d, x, y))
        elif -heap[0][0] > d:                   # closer than the farthest kept point
            heapq.heapreplace(heap, (-d, x, y))
    return [[x, y] for _, x, y in heap]""",
     why="""The heap always holds the k best points seen so far, with the worst of them on top, so each new point is
compared with that worst one in O(1) and inserted in O(log k). Squared distance avoids floating-point square roots
and preserves the order. Sorting all points is O(n log n) and also passes, but the heap is better when k is small or
the points come as a stream.

**Follow-ups (what if...):**
- *What if points arrive as an endless stream?* The size-k heap works unchanged with O(k) memory; sorting is not
  possible.
- *What if you need average O(n)?* Quickselect (partition around a pivot distance like in quicksort, recurse only into
  one side). Worst case O(n^2) without a random pivot.
- *What if the reference point is not the origin, or you need the k nearest neighbours of many query points?*
  Subtract the reference point first. For many queries, build a spatial index (k-d tree, ball tree; in practice
  `sklearn.neighbors.NearestNeighbors` or an approximate index such as FAISS for embeddings).
- *What if ties at the k-th distance are possible?* Agree on a tie rule with the examiner (for example by x, then y)
  and include it in the heap key.""",
     complexity="O(n log k) time, O(k) extra space.",
     mistakes="Using a min-heap of all n points and popping k times (fine but O(n + k log n) and more memory). "
              "Pushing `(d, ...)` into a size-k heap and evicting the closest instead of the farthest. Taking square "
              "roots and comparing floats.",
     learn=["algo-heap"],
     source=("LeetCode 973", "https://leetcode.com/problems/k-closest-points-to-origin/"))

# ---------------------------------------------------------------- Q4 bonus: longest palindromic substring
ex.q("Longest substring that reads the same backwards (bonus)", minutes=15,
     prompt="""Optional bonus (a very frequent question at TikTok, ByteDance, Samsung and Google).

Given a string `s`, return the longest **contiguous** substring that reads the same forwards and backwards. If there
are several of the same maximum length, return any of them.

Example: `s = "forgeeksskeegfor"` gives `"geeksskeeg"`. `s = "abacdfgdcaba"` gives `"aba"` (or the other `"aba"`).
`s = "cbbd"` gives `"bb"`.

The tests call your function through `palindrome_length(s)`, which checks that your answer is a palindrome and a
substring of `s`, and then returns its length (or a message if it is not). Constraints: up to 1,000 characters.""",
     stub="""def longest_palindrome(s):
    pass""",
     tests="""def palindrome_length(s):
    r = longest_palindrome(s)
    if not isinstance(r, str) or r not in s or r != r[::-1]:
        return f"not a palindromic substring: {r!r}"
    return len(r)

check(palindrome_length, [
    ("forgeeksskeegfor", 10),
    ("abacdfgdcaba", 3),
    ("cbbd", 2),             # even length centre
    ("babad", 3),            # two valid answers: "bab" or "aba"
    ("a", 1),                # one character
    ("ac", 1),               # no palindrome longer than 1
    ("aaaa", 4),             # the whole string
    ("racecarxyz", 7),
])
# larger input: "ab" * 500 (1,000 characters); the best is 999 characters long
check_big("1,000 characters", lambda: palindrome_length("ab" * 500), 999, limit=2.0)""",
     hint1="""Signal: palindromes grow outward from a middle point, and there are only `2n - 1` possible middles (a
character, or the gap between two characters). Pattern: **expand around center** (a two-pointer walk outward from each
center). The 2-D DP table `is_pal[i][j]` is the other classic answer, with O(n^2) memory.""",
     hint2="""1. Write `expand(lo, hi)`: while `lo >= 0`, `hi < n` and `s[lo] == s[hi]`, move `lo -= 1`, `hi += 1`;
return the palindrome bounds `lo + 1, hi`.
2. For every index `i`, try `expand(i, i)` (odd length) and `expand(i, i + 1)` (even length).
3. Keep the longest bounds and return `s[start:end]`.""",
     solution="""def longest_palindrome(s):
    def expand(lo, hi):
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            lo -= 1
            hi += 1
        return lo + 1, hi                           # s[lo + 1:hi] is a palindrome

    best_lo, best_hi = 0, 0
    for i in range(len(s)):
        for lo, hi in (expand(i, i), expand(i, i + 1)):   # odd and even centres
            if hi - lo > best_hi - best_lo:
                best_lo, best_hi = lo, hi
    return s[best_lo:best_hi]""",
     why="""Every palindrome has a centre, and growing outward from the centre checks each palindrome around it in one
walk, stopping at the first mismatch. Trying all `2n - 1` centres covers every palindrome, so the longest is found.
Each expansion is O(n), so O(n^2) in total with O(1) extra memory, compared with O(n^3) for "check every substring".

**Follow-ups (what if...):**
- *What if you need the DP version?* `is_pal[i][j] = s[i] == s[j] and (j - i < 2 or is_pal[i + 1][j - 1])`, filled by
  increasing length. Same O(n^2) time but O(n^2) memory; it is a good warm-up for interval DP.
- *What if n is 1,000,000?* Manacher's algorithm finds it in O(n) by reusing mirror information inside the current
  longest palindrome. Mention it by name; implementing it is rarely required.
- *What if you need the number of palindromic substrings (LeetCode 647)?* Same expansion; add 1 for every successful
  step instead of tracking the longest.
- *What if you may delete characters (subsequence, not substring; LeetCode 516)?* That is the longest common
  subsequence of `s` and `reversed(s)`, a 2-D DP.""",
     complexity="O(n^2) time, O(1) extra space.",
     mistakes="Forgetting even-length palindromes (`expand(i, i + 1)`). Off-by-one when converting the stopped pointers "
              "back to bounds. Confusing substring (contiguous) with subsequence. Checking all substrings with "
              "`t == t[::-1]` (O(n^3)).",
     learn=["algo-two-pointers", "algo-dp-2d"],
     source=("LeetCode 5", "https://leetcode.com/problems/longest-palindromic-substring/"))

ex.save()
