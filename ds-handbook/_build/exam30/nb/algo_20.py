import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _algo_mid_common import BIG, TREE

ex = Exam(20, "algorithms")
ex.setup(BIG + "\n\n" + TREE)
ex.text("The setup cell also defines `TreeNode`, `build(level_order_list)` (LeetCode's tree format, `None` = no "
        "child) and `find(root, value)` for the tree question.")

# ---------------------------------------------------------------- Q1 right side view (trees)
ex.q("What you see from the right", minutes=15,
     prompt="""Imagine standing to the right of a binary tree. Return the values of the nodes you can see, from top
to bottom: on each level, the **rightmost** node.

Example: `[1, 2, 3, 4, None, None, None, 5]` is

```
      1
     / \\
    2   3
   /
  4
 /
5
```
and the answer is `[1, 3, 4, 5]`: on the third and fourth levels the only nodes are on the left side, but you still
see them because nothing blocks them.

The tests call your function through `right_view(values)`, which builds the tree. An empty tree gives `[]`.""",
     stub="""def right_side_view(root):
    pass""",
     tests="""def right_view(values):
    return right_side_view(build(values))

check(right_view, [
    ([1, 2, 3, 4, None, None, None, 5], [1, 3, 4, 5]),
    ([1, 2, 3, None, 5, None, 4], [1, 3, 4]),
    ([1, None, 3], [1, 3]),                     # right chain
    ([1, 2], [1, 2]),                           # only a left child: still visible
    ([], []),                                   # empty tree
    ([7], [7]),                                 # one node
    ([1, 2, 3, None, 5], [1, 3, 5]),            # deepest node is under the LEFT subtree
])
# larger inputs: complete tree with 65,535 nodes, and a 3,000-deep left chain
chain = [1]
for v in range(2, 3_001):
    chain += [v, None]
check_big("complete tree, 65,535 nodes", lambda: right_view(list(range(1, 2**16))), [2**d - 1 for d in range(1, 17)])
check_big("left chain of 3,000 nodes", lambda: right_view(chain), list(range(1, 3_001)))""",
     hint1="""Signal: "one value per level" (here the last one). Pattern: **tree BFS level by level** (take the last
node of each level). A DFS that visits the right child first and records the first node seen at each depth works too.""",
     hint2="""1. BFS with a queue; at the start of each level `size = len(queue)`.
2. Pop `size` nodes, pushing their children left then right.
3. The last node popped in the level is the visible one: append its value.""",
     solution="""from collections import deque

def right_side_view(root):
    if root is None:
        return []
    out, queue = [], deque([root])
    while queue:
        for _ in range(len(queue)):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        out.append(node.val)          # the last node popped in this level is the rightmost
    return out""",
     why="""BFS groups nodes by level and, pushing left before right, pops each level from left to right, so the last
one popped is the rightmost visible node. Following only right children is the classic bug: a deeper level may exist
only under the left subtree (third and fifth test). The iterative BFS also handles a 3,000-deep chain, where a
recursive DFS would exceed Python's recursion limit.

**Follow-ups (what if...):**
- *What if you want the left side view?* Take the first node of each level instead of the last.
- *What if you must use DFS?* Visit right before left and pass the depth; record a value when
  `depth == len(out)` (the first node reached at a new depth is the rightmost). Uses O(h) memory instead of O(width).
- *What if you need the view from the top or bottom (vertical order)?* Track horizontal positions (column = parent's
  column -1 / +1) and keep the first or last node per column.
- *What if the tree is stored as parent pointers in a table?* Compute depth for each node (recursive CTE in SQL or a
  BFS), then for each depth pick the node with the largest horizontal order.""",
     complexity="O(n) time, O(w) extra space (w = widest level).",
     mistakes="Walking only along right children. Taking the first node of each level (that is the left view). "
              "Recursive solutions that fail on deep trees.",
     learn=["algo-trees", "algo-graphs-bfs-dfs"],
     source=("LeetCode 199", "https://leetcode.com/problems/binary-tree-right-side-view/"))

# ---------------------------------------------------------------- Q2 LCS (dp 2d)
ex.q("Longest shared subsequence of two strings", minutes=20,
     prompt="""Given two strings `a` and `b`, return the length of their longest **common subsequence**: the longest
string that can be obtained from both by deleting some characters (or none) without changing the order of the rest.
Return 0 if they share nothing.

Example: `a = "abcde"`, `b = "ace"` gives `3` (`"ace"`). `a = "AGGTAB"`, `b = "GXTXAYB"` gives `4` (`"GTAB"`).

Constraints: each string up to 1,000 characters. The larger test uses two 1,000-character strings, so a memoised
recursion would go up to 2,000 levels deep.""",
     stub="""def lcs(a, b):
    pass""",
     tests="""check(lcs, [
    (("abcde", "ace"), 3),
    (("AGGTAB", "GXTXAYB"), 4),
    (("abc", "abc"), 3),                     # identical
    (("abc", "def"), 0),                     # nothing shared
    (("", "abc"), 0),                        # empty string
    (("a", "a"), 1),
    (("abcba", "abcbcba"), 5),
    (("ezupkr", "ubmrapg"), 2),
])
# larger input: "ab" * 500 and "ba" * 500 (answer 999)
check_big("two strings of 1,000 characters", lambda: lcs("ab" * 500, "ba" * 500), 999, limit=4.0)""",
     hint1="""Signal: two sequences, and the answer for prefixes `a[:i]`, `b[:j]` depends on slightly shorter prefixes.
Pattern: **2-D dynamic programming** over `(i, j)`: match the last characters if they are equal, otherwise drop one
of them.""",
     hint2="""1. `dp[i][j]` = LCS length of `a[:i]` and `b[:j]`; row 0 and column 0 are 0.
2. If `a[i - 1] == b[j - 1]`: `dp[i][j] = dp[i - 1][j - 1] + 1`.
3. Else: `dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])`.
4. Answer: `dp[len(a)][len(b)]`. Only the previous row is needed, so you can keep two rows.""",
     solution="""def lcs(a, b):
    if len(a) < len(b):
        a, b = b, a                      # keep the rows short (memory O(min(m, n)))
    prev = [0] * (len(b) + 1)            # dp row for a[:i - 1]
    for ch in a:
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if ch == b[j - 1]:
                cur[j] = prev[j - 1] + 1                 # extend the LCS of both shorter prefixes
            else:
                cur[j] = max(prev[j], cur[j - 1])        # drop the last char of a or of b
        prev = cur
    return prev[-1]""",
     why="""Look at the last characters of the two prefixes. If they are equal, some LCS uses them as its last
character, so the answer is one more than for both prefixes without them. If they differ, at least one of them is not
in the LCS, so the answer is the better of dropping one or the other. Each cell is computed once from three
neighbours, giving O(m x n). Keeping only the previous row cuts memory to O(min(m, n)).

**Follow-ups (what if...):**
- *What if you need the subsequence itself, not just the length?* Keep the full table and walk back from
  `dp[m][n]`: on a match go diagonal and record the character, else move toward the larger neighbour.
- *What if you need the minimum number of insertions and deletions to turn a into b?* `len(a) + len(b) - 2 * LCS`.
  With substitutions too, it is edit distance (LeetCode 72), the same table with a different recurrence.
- *What if you want the longest common **substring** (contiguous)?* `dp[i][j] = dp[i - 1][j - 1] + 1` on a match and
  0 otherwise; the answer is the maximum cell.
- *What if the strings are 100,000 long?* O(mn) is 10^10, too slow. Practical tools (diff, git) use Myers' algorithm,
  which is fast when the strings are similar; for very different strings, no generally faster exact method is known.
- *Data angle:* comparing user event sequences (session paths) or fuzzy matching of names uses the same DP.""",
     complexity="O(m x n) time, O(min(m, n)) space with two rows (O(m x n) with the full table).",
     mistakes="Confusing it with the contiguous substring version. Off-by-one between `dp` indices and string indices "
              "(`a[i - 1]`). Memoised recursion that hits the recursion limit on long strings. Updating a single row in "
              "place and overwriting `prev[j - 1]` before it is used.",
     learn=["algo-dp-2d"],
     source=("LeetCode 1143", "https://leetcode.com/problems/longest-common-subsequence/"))

# ---------------------------------------------------------------- Q3 find all anagrams (sliding window)
ex.q("Where are the scrambled copies?", minutes=18,
     prompt="""Given a string `s` and a shorter pattern `p` (lowercase letters only), return every start index `i`
such that `s[i : i + len(p)]` is a rearrangement of `p` (same letters, same counts). Return the indices in increasing
order.

Example: `s = "cbaebabacd"`, `p = "abc"` gives `[0, 6]` (`"cba"` at 0 and `"bac"` at 6).
`s = "abab"`, `p = "ab"` gives `[0, 1, 2]`.

Constraints: `s` and `p` up to 100,000 characters. Sorting or counting every window from scratch is too slow for the
larger test.""",
     stub="""def find_anagrams(s, p):
    pass""",
     tests="""check(find_anagrams, [
    (("cbaebabacd", "abc"), [0, 6]),
    (("abab", "ab"), [0, 1, 2]),             # overlapping matches
    (("a", "ab"), []),                       # pattern longer than s
    (("aaaa", "a"), [0, 1, 2, 3]),
    (("abc", "abc"), [0]),                   # whole string
    (("baa", "aa"), [1]),                    # counts matter, not just the set of letters
    (("af", "be"), []),
    (("ababab", "aab"), [0, 2]),
])
# larger input: s = "ab" * 50,000, p = "ab" * 500 (every one of the 99,001 windows matches)
check_big("s of 100,000, p of 1,000", lambda: find_anagrams("ab" * 50_000, "ab" * 500), list(range(99_001)))""",
     hint1="""Signal: every window of a **fixed length** `len(p)` must be compared by letter counts; consecutive windows
differ by one letter in and one letter out. Pattern: **fixed-size sliding window** with a count array (26 letters).""",
     hint2="""1. Build `need` = letter counts of `p` and `have` = counts of the first `len(p)` letters of `s`.
2. If they are equal, record index 0.
3. Slide: add `s[i]`, remove `s[i - len(p)]`, and compare again; record `i - len(p) + 1` on a match.
4. To make each step O(1) instead of O(26), track `matches` = how many of the 26 letters currently have equal counts.""",
     solution="""def find_anagrams(s, p):
    m = len(p)
    if m > len(s):
        return []
    need, have = [0] * 26, [0] * 26
    for ch in p:
        need[ord(ch) - 97] += 1
    out = []
    for i, ch in enumerate(s):
        have[ord(ch) - 97] += 1                   # letter enters the window
        if i >= m:
            have[ord(s[i - m]) - 97] -= 1         # letter leaves the window
        if i >= m - 1 and have == need:           # comparing two 26-long lists is O(26) = O(1)
            out.append(i - m + 1)
    return out""",
     why="""Two strings are anagrams exactly when their letter counts are equal. Moving the window by one changes only
two counts, so you never recount the window. Comparing two 26-long lists costs a constant, so the total is O(n) for
`s` of length n, instead of O(n x m) (recount each window) or O(n x m log m) (sort each window).

**Follow-ups (what if...):**
- *What if the alphabet is Unicode (huge)?* Use dictionaries and keep a `matches` counter of letters whose counts are
  equal, updating it only for the two letters that changed, so each step is O(1) regardless of the alphabet.
- *What if you only need to know whether any anagram exists (LeetCode 567)?* Return on the first match.
- *What if the window is not fixed (smallest window containing all letters of p, LeetCode 76)?* Variable-size window:
  grow until valid, then shrink from the left while it stays valid.
- *What if s is a stream?* Keep the last `m` characters in a deque plus the counts; each new character is one O(1)
  update.
- *What if you must group many words by anagram class instead?* Use the sorted word or the count tuple as a hash key
  (LeetCode 49).""",
     complexity="O(n x 26) = O(n) time, O(1) extra space (two arrays of 26) plus the output.",
     mistakes="Recounting or sorting every window (too slow). Recording the end index instead of the start. Forgetting "
              "the case `len(p) > len(s)`. Comparing sets of letters instead of counts (fails on \"baa\" / \"aa\").",
     learn=["algo-sliding-window", "algo-hashing"],
     source=("LeetCode 438", "https://leetcode.com/problems/find-all-anagrams-in-a-string/"))

ex.save()
