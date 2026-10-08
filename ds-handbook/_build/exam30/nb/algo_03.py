"""Day 3 algorithms (easy): Reverse Linked List, Maximum Depth of Binary Tree, Valid Anagram
+ bonus Guess Number Higher or Lower."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from algo_common import LIST_CODE, TREE_CODE, lc

ex = Exam(3, "algorithms")
ex.setup(LIST_CODE + "\n\n" + TREE_CODE)
ex.text("""The setup cell gives you `ListNode`, `build_list([1, 2, 3])`, `list_values(head)`, `TreeNode`,
`build_tree([3, 9, 20, None, None, 15, 7])` (level order, `None` = no child) and `tree_values(root)`. The tests use
them to turn plain python lists into nodes and back.""")

ex.q("Turn the chain around", minutes=15, level="easy",
     prompt="""You get the head of a singly linked list. Reverse the list and return the new head. Do it in one pass
with O(1) extra space; then, if you have time, also write it recursively.

Examples (shown as values):
- `1 -> 2 -> 3 -> 4` becomes `4 -> 3 -> 2 -> 1`
- `7 -> 8` becomes `8 -> 7`
- an empty list stays empty""",
     stub="def reverse_list(head):\n    pass",
     tests="""def reversed_values(vals):
    return list_values(reverse_list(build_list(vals)))

check(reversed_values, [
    ([1, 2, 3, 4], [4, 3, 2, 1]),
    ([7, 8], [8, 7]),
    ([5], [5]),
    ([], []),
    ([1, 1, 2], [2, 1, 1]),
    ([1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1]),
])""",
     hint1="Signal: you must re-point every `next` arrow without losing the rest of the chain. Pattern: "
           "**linked list pointer manipulation** (prev / current / next).",
     hint2="""1. `prev = None`, `cur = head`.
2. While `cur`: save `nxt = cur.next`; set `cur.next = prev`; move `prev = cur`; move `cur = nxt`.
3. Return `prev` (the old tail).""",
     solution='''def reverse_list(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next        # 1. remember the rest
        cur.next = prev       # 2. flip the arrow
        prev, cur = cur, nxt  # 3. step forward
    return prev

# recursive version (O(n) stack space):
def reverse_list_rec(head):
    if head is None or head.next is None:
        return head
    new_head = reverse_list_rec(head.next)
    head.next.next = head
    head.next = None
    return new_head

print(list_values(reverse_list_rec(build_list([1, 2, 3]))))  # [3, 2, 1]''',
     why="Each node only needs its arrow flipped to point at the node before it. Saving `cur.next` first is the "
         "key step: once the arrow is flipped, it is the only way to reach the rest of the list.",
     complexity="Iterative: O(n) time, O(1) space. Recursive: O(n) time, O(n) call stack.",
     mistakes="Flipping `cur.next` before saving it (the rest of the list is lost). Returning `head` (now the "
              "tail). In the recursive version, forgetting `head.next = None`, which creates a cycle.",
     learn=["algo-linked-list"], source=("LeetCode 206", lc("reverse-linked-list")))

ex.q("How tall is the tree?", minutes=12, level="easy",
     prompt="""Return the depth of a binary tree: the number of nodes on the longest path from the root down to a
leaf. An empty tree has depth 0.

Examples (level order, `None` = missing child):
- `[3, 9, 20, None, None, 15, 7]` -> `3` (path 3, 20, 15)
- `[1, None, 2]` -> `2`
- `[]` -> `0`""",
     stub="def max_depth(root):\n    pass",
     tests="""def depth_of(vals):
    return max_depth(build_tree(vals))

check(depth_of, [
    ([3, 9, 20, None, None, 15, 7], 3),
    ([1, None, 2], 2),
    ([], 0),
    ([0], 1),
    ([1, 2, 3, 4, None, None, 5, 6], 4),
    ([1, 2, None, 3, None, 4, None, 5], 5),
])""",
     hint1="Signal: the answer for a node is built from the answers of its two children. Pattern: **tree "
           "recursion (DFS)**; BFS counting levels also works.",
     hint2="""1. Base case: `root is None` -> 0.
2. Otherwise: `1 + max(max_depth(root.left), max_depth(root.right))`.
3. (BFS version: count how many levels you pop from a queue.)""",
     solution='''def max_depth(root):
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

# iterative BFS version: count the levels
def max_depth_bfs(root):
    depth, level = 0, [root] if root else []
    while level:
        depth += 1
        level = [c for n in level for c in (n.left, n.right) if c]
    return depth

print(max_depth_bfs(build_tree([3, 9, 20, None, None, 15, 7])))  # 3''',
     why="The tallest path through a node goes into its taller subtree, plus the node itself. Recursion visits "
         "every node once. On a very deep, chain-like tree, Python recursion can hit the default limit of about "
         "1000 frames; the BFS version avoids that.",
     complexity="O(n) time; O(h) space for recursion (h = height, up to n), O(w) for BFS (w = widest level).",
     mistakes="Returning 1 for an empty tree. Counting edges instead of nodes. Using `min` logic from a "
              "different problem.",
     learn=["algo-trees"], source=("LeetCode 104", lc("maximum-depth-of-binary-tree")))

ex.q("Same letters, different order?", minutes=10, level="easy",
     prompt="""Return `True` if `t` uses exactly the same letters as `s`, each the same number of times (an anagram),
otherwise `False`. Follow-up to answer out loud: what changes if the strings may contain any Unicode character?

Examples:
- `s = "listen", t = "silent"` -> `True`
- `s = "rat", t = "car"` -> `False`
- `s = "aab", t = "abb"` -> `False` (same letters, different counts)""",
     stub="def is_anagram(s, t):\n    pass",
     tests="""check(is_anagram, [
    (("anagram", "nagaram"), True),
    (("rat", "car"), False),
    (("listen", "silent"), True),
    (("aab", "abb"), False),
    (("", ""), True),
    (("a", "ab"), False),
    (("abc", "cba"), True),
])""",
     hint1="Signal: order does not matter, only how many of each letter. Pattern: **hashing** (count with a dict "
           "or Counter).",
     hint2="""1. If the lengths differ, return False.
2. Count the letters of `s` (+1 each) and of `t` (-1 each) in one dict.
3. Return True if every count is 0. (Or simply `Counter(s) == Counter(t)`.)""",
     solution='''def is_anagram(s, t):
    if len(s) != len(t):
        return False
    count = {}
    for a, b in zip(s, t):
        count[a] = count.get(a, 0) + 1
        count[b] = count.get(b, 0) - 1
    return all(v == 0 for v in count.values())''',
     why="Two strings are anagrams exactly when their letter counts match. Counting is one pass; sorting both "
         "strings also works but costs O(n log n). The dict version works for any Unicode character; a fixed "
         "array of 26 counts only works for lowercase English letters, which answers the follow-up.",
     complexity="O(n) time, O(k) space where k is the number of distinct characters (O(1) for 26 letters).",
     mistakes="Comparing `set(s) == set(t)` (ignores counts, says `\"aab\"` and `\"abb\"` match). Skipping the "
              "length check and then missing extra letters in `t`.",
     learn=["algo-hashing"], source=("LeetCode 242", lc("valid-anagram")))

ex.q("Guess the secret number (bonus)", minutes=10, level="easy",
     prompt="""Optional. A secret number was picked from `1..n`. You can call `guess(x)`, which returns `-1` if the
secret is smaller than `x`, `1` if it is larger, and `0` if `x` is the secret. Return the secret. `n` can be as
large as `2**31 - 1`, and the test fails if you call `guess` more than 40 times.

Example: `n = 10`, secret 6: `guess(5)` -> `1`, `guess(8)` -> `-1`, `guess(6)` -> `0`, so return 6.""",
     stub="def guess_number(n, guess):\n    pass",
     tests="""def play(n, secret):
    calls = [0]
    def guess(x):
        calls[0] += 1
        return 0 if x == secret else (-1 if secret < x else 1)
    answer = guess_number(n, guess)
    return answer if calls[0] <= 40 else "too many guesses"

check(play, [
    ((10, 6), 6),
    ((1, 1), 1),
    ((2, 1), 1),
    ((2, 2), 2),
    ((100, 1), 1),
    ((2**31 - 1, 1702766719), 1702766719),
    ((2**31 - 1, 2**31 - 1), 2**31 - 1),
])""",
     hint1="Signal: every answer tells you on which side the target is. Pattern: **binary search** on the range "
           "`1..n`.",
     hint2="""1. `lo, hi = 1, n`.
2. While `lo <= hi`: `mid = (lo + hi) // 2`, `r = guess(mid)`.
3. `r == 0`: return mid. `r == 1` (secret is larger): `lo = mid + 1`. `r == -1`: `hi = mid - 1`.""",
     solution='''def guess_number(n, guess):
    lo, hi = 1, n
    while lo <= hi:
        mid = (lo + hi) // 2
        r = guess(mid)
        if r == 0:
            return mid
        if r == 1:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1''',
     why="The range halves with every call, so even `n = 2**31 - 1` needs at most 31 guesses. A linear scan "
         "would need up to two billion calls.",
     complexity="O(log n) time, O(1) space.",
     mistakes="Mixing up the sign of the API answer (`-1` means guess lower). `while lo < hi` that never tests "
              "the last remaining value.",
     learn=["algo-binary-search"], source=("LeetCode 374", lc("guess-number-higher-or-lower")))

ex.save()
