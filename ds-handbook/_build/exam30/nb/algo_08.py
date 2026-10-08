"""Day 8 algorithms (easy band, first mediums): Same Tree, Group Anagrams, Min Stack + bonus Palindrome Linked List."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from algo_common import LIST_CODE, TREE_CODE, OPS_CODE, lc

ex = Exam(8, "algorithms")
ex.setup(LIST_CODE + "\n\n" + TREE_CODE + "\n\n" + OPS_CODE)
ex.text("""The setup cell gives you `build_tree` / `tree_values` (level order, `None` = no child), `build_list` /
`list_values`, and `check_ops(cls, ops, args, expected)`, which replays a list of method calls on a class (LeetCode
style) and prints PASS or FAIL for every returned value.""")

ex.q("Identical twins?", minutes=10, level="easy",
     prompt="""Given the roots of two binary trees, return `True` if they have exactly the same shape and the same value
in every position.

Examples (level order):
- `[1, 2, 3]` and `[1, 2, 3]` -> `True`
- `[1, 2]` and `[1, None, 2]` -> `False` (same values, different shape)
- `[1, 2, 1]` and `[1, 1, 2]` -> `False`""",
     stub="def is_same_tree(p, q):\n    pass",
     tests="""def same(a, b):
    return is_same_tree(build_tree(a), build_tree(b))

check(same, [
    (([1, 2, 3], [1, 2, 3]), True),
    (([1, 2], [1, None, 2]), False),
    (([1, 2, 1], [1, 1, 2]), False),
    (([], []), True),
    (([1], []), False),
    (([5, 4, 8, None, 3], [5, 4, 8, None, 3]), True),
    (([5, 4, 8, None, 3], [5, 4, 8, 3]), False),
])""",
     hint1="Signal: the answer for two nodes depends on the same question for their children. Pattern: **tree "
           "recursion (DFS on two trees at once)**.",
     hint2="""1. Both None: True. Exactly one None: False.
2. Values differ: False.
3. Otherwise: `same(p.left, q.left) and same(p.right, q.right)`.""",
     solution='''def is_same_tree(p, q):
    if p is None and q is None:
        return True
    if p is None or q is None or p.val != q.val:
        return False
    return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)''',
     why="Two trees are equal when the roots match and both pairs of subtrees are equal. Walking both trees in "
         "lock-step compares every position once and stops at the first difference.",
     complexity="O(min(n, m)) time (stops at the first difference), O(h) recursion space.",
     mistakes="Comparing only the in-order traversals: different shapes can give the same list (unless you also "
              "record the `None` gaps). Checking `p.val` before checking for None.",
     learn=["algo-trees"], source=("LeetCode 100", lc("same-tree")))

ex.q("Bucket the scrambled words", minutes=20, level="medium",
     prompt="""Group the words that are anagrams of each other (same letters, same counts). Return a list of groups;
the order of groups and the order inside a group do not matter (the test sorts them).

Example: `["eat", "tea", "tan", "ate", "nat", "bat"]` -> `[["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]`

Follow-ups to answer out loud:
1. Words are long (length k up to 10,000) but use only lowercase letters: can you avoid sorting each word?
2. The words arrive as a stream that does not fit in memory: what would you do?""",
     stub="def group_anagrams(words):\n    pass",
     tests="""def norm(groups):
    return sorted(sorted(g) for g in groups) if isinstance(groups, list) else groups

check(group_anagrams, [
    (["eat", "tea", "tan", "ate", "nat", "bat"], [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]),
    ([""], [[""]]),
    (["a"], [["a"]]),
    ([], []),
    (["abc", "bca", "cab", "xyz"], [["abc", "bca", "cab"], ["xyz"]]),
    (["ab", "ba", "ab"], [["ab", "ab", "ba"]]),
    (["aab", "abb"], [["aab"], ["abb"]]),
], key=norm)""",
     hint1="Signal: items that are \"the same\" under some rule must land together. Pattern: **hashing with a "
           "canonical key** (dict from key to list).",
     hint2="""1. For each word, compute a key that is identical for all its anagrams: `"".join(sorted(w))`, or a tuple of
   26 letter counts.
2. `groups[key].append(w)` with a `defaultdict(list)`.
3. Return `list(groups.values())`.""",
     solution='''from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    return list(groups.values())

# follow-up 1: count key, O(k) per word instead of O(k log k)
def group_anagrams_counts(words):
    groups = defaultdict(list)
    for w in words:
        counts = [0] * 26
        for ch in w:
            counts[ord(ch) - ord("a")] += 1
        groups[tuple(counts)].append(w)
    return list(groups.values())

print(len(group_anagrams_counts(["eat", "tea", "tan", "ate", "nat", "bat"])))   # 3''',
     why="All anagrams share the same sorted letters (or the same letter counts), so that key puts them in the "
         "same dict bucket in one pass. Lists cannot be dict keys, so the counts become a tuple. Follow-up 2: hash "
         "each word's key to one of many files or workers (a map-reduce style shuffle by key), then group each "
         "part on its own; this is the same idea as `GROUP BY key` in SQL.",
     complexity="Sorted key: O(n * k log k) time. Count key: O(n * k) time. Both O(n * k) space.",
     mistakes="Using a list as a dict key (TypeError). Using `set(w)` as the key (merges `\"aab\"` and "
              "`\"abb\"`). Comparing every pair of words (O(n^2 * k)).",
     learn=["algo-hashing"], source=("LeetCode 49", lc("group-anagrams")))

ex.q("A stack that knows its minimum", minutes=20, level="medium",
     prompt="""Design a class `MinStack` with these methods, each running in O(1) time:
- `push(val)`: add a value on top
- `pop()`: remove the top value
- `top()`: return the top value
- `getMin()`: return the smallest value currently in the stack

Calls are always valid (no `pop`, `top` or `getMin` on an empty stack).

Example: push -2, push 0, push -3, `getMin()` -> `-3`, pop, `top()` -> `0`, `getMin()` -> `-2`.

Follow-up to answer out loud: can you use less memory when many values are pushed but the minimum rarely changes?""",
     stub='''class MinStack:
    def __init__(self):
        pass

    def push(self, val):
        pass

    def pop(self):
        pass

    def top(self):
        pass

    def getMin(self):
        pass''',
     tests="""check_ops(MinStack,
    ["MinStack", "push", "push", "push", "getMin", "pop", "top", "getMin"],
    [[], [-2], [0], [-3], [], [], [], []],
    [None, None, None, None, -3, None, 0, -2])
# repeated minimum: popping one copy of 0 must keep 0 as the minimum
check_ops(MinStack,
    ["MinStack", "push", "push", "push", "push", "getMin", "pop", "getMin", "pop", "getMin", "pop", "getMin", "top"],
    [[], [2], [0], [3], [0], [], [], [], [], [], [], [], []],
    [None, None, None, None, None, 0, None, 0, None, 0, None, 2, 2])""",
     hint1="Signal: a stack plus a question about all its current values, answered in O(1). Pattern: **stack "
           "that stores extra state per element** (the minimum so far).",
     hint2="""1. Store pairs `(val, min_so_far)` on one stack, where `min_so_far = min(val, previous min)`.
2. `top()` is `stack[-1][0]`, `getMin()` is `stack[-1][1]`, `pop()` removes the pair.
3. When a value is popped, the minimum below it is already stored in the pair underneath.""",
     solution='''class MinStack:
    def __init__(self):
        self.stack = []                       # (value, minimum of the stack up to here)

    def push(self, val):
        low = val if not self.stack else min(val, self.stack[-1][1])
        self.stack.append((val, low))

    def pop(self):
        self.stack.pop()

    def top(self):
        return self.stack[-1][0]

    def getMin(self):
        return self.stack[-1][1]''',
     why="A stack only changes at the top, so the minimum of everything below a position never changes while "
         "that position exists. Saving it next to each value means a pop automatically restores the previous "
         "minimum. Follow-up: keep a second stack that only gets a push when `val <= current min`, and pop it when "
         "the popped value equals its top. The `<=` (not `<`) matters for repeated minimums.",
     complexity="O(1) time for every method, O(n) space.",
     mistakes="Keeping one `self.min` variable (after popping the minimum you cannot know the next one). Using "
              "`<` in the two-stack version, which breaks the second test with two zeros. Calling `min(self.stack)` "
              "in `getMin` (O(n)).",
     learn=["algo-stack", "algo-design"], source=("LeetCode 155", lc("min-stack")))

ex.q("Is the chain a palindrome? (bonus)", minutes=15, level="easy",
     prompt="""Optional. Return `True` if the values of a singly linked list read the same forwards and backwards.
First solve it any way you like, then the follow-up: O(n) time and O(1) extra space.

Examples (values):
- `1 -> 2 -> 2 -> 1` -> `True`
- `1 -> 2` -> `False`
- `1 -> 2 -> 3 -> 2 -> 1` -> `True`""",
     stub="def is_palindrome_list(head):\n    pass",
     tests="""def pal_list(vals):
    return is_palindrome_list(build_list(vals))

check(pal_list, [
    ([1, 2, 2, 1], True),
    ([1, 2], False),
    ([1], True),
    ([], True),
    ([1, 2, 3, 2, 1], True),
    ([1, 1, 2, 1], False),
])""",
     hint1="Signal: you need the second half in reverse order, but you can only walk forward. Pattern: **linked "
           "list: fast/slow pointers to find the middle, then reverse the second half**.",
     hint2="""1. Easy version: copy the values into a python list and compare with its reverse (O(n) space).
2. O(1) space: move `slow` one step and `fast` two steps until `fast` reaches the end; `slow` is at the middle.
3. Reverse the list from `slow` on (day 3), then compare it node by node with the first half.""",
     solution='''def is_palindrome_list(head):
    slow = fast = head
    while fast and fast.next:                 # 1. find the middle
        slow, fast = slow.next, fast.next.next
    prev = None                               # 2. reverse the second half
    while slow:
        slow.next, prev, slow = prev, slow, slow.next
    left, right = head, prev                  # 3. compare the halves
    while right:
        if left.val != right.val:
            return False
        left, right = left.next, right.next
    return True''',
     why="When `fast` reaches the end, `slow` has gone half as far, so it sits at the middle. After reversing the "
         "second half, both halves can be walked forward together. For an odd length the middle node ends up in "
         "the reversed half and is compared with itself, which is harmless. In real code, reverse the half back "
         "afterwards so the caller's list is not changed.",
     complexity="O(n) time, O(1) extra space (the simple copy version is O(n) space).",
     mistakes="Losing nodes while reversing (save `next` first). Comparing until `left` is None instead of "
              "`right`. Not mentioning that the input list is modified.",
     learn=["algo-linked-list"], source=("LeetCode 234", lc("palindrome-linked-list")))

ex.save()
