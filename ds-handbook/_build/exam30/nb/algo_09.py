"""Day 9 algorithms (easy band): Linked List Cycle, Longest Substring Without Repeating Characters,
Kth Largest Element in a Stream + bonus Missing Number."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from algo_common import LIST_CODE, OPS_CODE, lc

ex = Exam(9, "algorithms")
ex.setup(LIST_CODE + "\n\n" + OPS_CODE)
ex.text("""The setup cell gives you `ListNode`, `build_list` / `list_values`, and `check_ops(cls, ops, args,
expected)`, which replays a list of method calls on a class (LeetCode style) and prints PASS or FAIL.""")

ex.q("Does the chain loop back?", minutes=15, level="easy",
     prompt="""You get the head of a linked list. Some node's `next` may point back to an earlier node, so walking the
list would never end. Return `True` if there is such a loop, `False` otherwise. Follow-up: use O(1) extra memory.

In the tests, `pos` is the index of the node the tail points back to (`-1` means no loop). Examples:
- values `[3, 2, 0, -4]`, `pos = 1` -> `True` (the tail `-4` points back to `2`)
- values `[1, 2]`, `pos = 0` -> `True`
- values `[1]`, `pos = -1` -> `False`""",
     stub="def has_cycle(head):\n    pass",
     tests="""def cycle_case(vals, pos):
    head = build_list(vals)
    if pos >= 0:
        nodes, node = [], head
        while node:
            nodes.append(node)
            node = node.next
        nodes[-1].next = nodes[pos]          # create the loop
    return has_cycle(head)

check(cycle_case, [
    (([3, 2, 0, -4], 1), True),
    (([1, 2], 0), True),
    (([1], -1), False),
    (([], -1), False),
    (([1], 0), True),
    (([1, 2, 3, 4, 5], -1), False),
    (([1, 2, 3, 4, 5], 4), True),
])""",
     hint1="Signal: detect a loop with constant memory. Pattern: **linked list, fast and slow pointers** "
           "(Floyd's tortoise and hare). With O(n) memory, a set of visited nodes also works.",
     hint2="""1. `slow = fast = head`.
2. While `fast` and `fast.next`: `slow` moves 1 step, `fast` moves 2 steps.
3. If they ever point to the same node, there is a loop: return True.
4. If `fast` reaches the end (None), there is no loop: return False.""",
     solution='''def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False''',
     why="Without a loop, `fast` falls off the end. With a loop, both pointers end up inside it, and each step "
         "the gap between them shrinks by one, so `fast` must land exactly on `slow` within one lap. No visited "
         "set is needed, so memory is O(1).",
     complexity="O(n) time, O(1) space (the visited-set version is O(n) space).",
     mistakes="Comparing values (`slow.val == fast.val`) instead of node identity: two different nodes can hold "
              "the same value. Checking `slow is fast` before moving (they start equal). Not checking "
              "`fast.next` before `fast.next.next`.",
     learn=["algo-linked-list"], source=("LeetCode 141", lc("linked-list-cycle")))

ex.q("Longest stretch with no repeated letter", minutes=20, level="medium",
     prompt="""Return the length of the longest contiguous piece of `s` in which no character appears twice. Aim for
O(n).

Examples:
- `"abcabcbb"` -> `3` (`"abc"`)
- `"pwwkew"` -> `3` (`"wke"`; `"pwke"` is not contiguous)
- `"abba"` -> `2`
- `""` -> `0`

Follow-ups to answer out loud:
1. The characters arrive one by one as a stream and you must report the current best after each one. Does your
   solution still work, and how much memory does it need?
2. What changes if each character may appear at most twice?""",
     stub="def length_of_longest_substring(s):\n    pass",
     tests="""check(length_of_longest_substring, [
    ("abcabcbb", 3),
    ("bbbbb", 1),
    ("pwwkew", 3),
    ("", 0),
    (" ", 1),
    ("dvdf", 3),
    ("abba", 2),
    ("tmmzuxt", 5),
])""",
     hint1="Signal: longest contiguous piece that satisfies a rule which breaks when a duplicate enters. Pattern: "
           "**variable-size sliding window** (with a dict of last positions).",
     hint2="""1. `last = {}` maps a character to the index where it was last seen; `left = 0` is the window start.
2. For each `right, ch`: if `ch` was seen at an index `>= left`, move `left` to `last[ch] + 1`.
3. Update `last[ch] = right` and `best = max(best, right - left + 1)`.""",
     solution='''def length_of_longest_substring(s):
    last = {}                         # char -> last index seen
    left = best = 0
    for right, ch in enumerate(s):
        if last.get(ch, -1) >= left:  # duplicate inside the current window
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best''',
     why="The window `s[left..right]` always has unique characters. When a duplicate enters, every window that "
         "starts at or before its earlier copy is invalid, so `left` can jump straight past it. Both ends only move "
         "forward, so the work is linear. The `>= left` check matters: in `\"abba\"`, the old `a` at index 0 is "
         "outside the window when the second `a` arrives, and `left` must not move back. Follow-up 1: yes, it is "
         "already a one-pass stream algorithm; memory is O(alphabet size). Follow-up 2: keep counts in the window "
         "and shrink from the left while some count is above 2.",
     complexity="O(n) time, O(min(n, alphabet)) space.",
     mistakes="Moving `left` backwards (`left = last[ch] + 1` without the `>= left` check, fails on `\"abba\"`). "
              "Checking all substrings (O(n^2) or worse). Off-by-one in `right - left + 1`.",
     learn=["algo-sliding-window"],
     source=("LeetCode 3", lc("longest-substring-without-repeating-characters")))

ex.q("Live leaderboard: the k-th best score", minutes=20, level="easy",
     prompt="""Design a class `KthLargest(k, nums)` for a stream of scores. `nums` is the starting list (it may have
fewer than k values). Each call `add(val)` inserts a new score and returns the k-th largest score seen so far
(counting duplicates). Each `add` will be called only when at least k scores exist after inserting.

Example: `KthLargest(3, [4, 5, 8, 2])`, then `add(3)` -> `4`, `add(5)` -> `5`, `add(10)` -> `5`, `add(9)` -> `8`,
`add(4)` -> `8`.

Follow-up to answer out loud: millions of `add` calls with k = 100. Why is your solution better than sorting after
every insert?""",
     stub='''class KthLargest:
    def __init__(self, k, nums):
        pass

    def add(self, val):
        pass''',
     tests="""check_ops(KthLargest,
    ["KthLargest", "add", "add", "add", "add", "add"],
    [[3, [4, 5, 8, 2]], [3], [5], [10], [9], [4]],
    [None, 4, 5, 5, 8, 8])
check_ops(KthLargest,
    ["KthLargest", "add", "add", "add", "add", "add"],
    [[1, []], [-3], [-2], [-4], [0], [4]],
    [None, -3, -2, -2, 0, 4])
check_ops(KthLargest,
    ["KthLargest", "add", "add", "add", "add", "add"],
    [[2, [0]], [-1], [1], [-2], [-4], [3]],
    [None, -1, 0, 0, 0, 1])""",
     hint1="Signal: keep the top k of a stream and read the smallest of them quickly. Pattern: **heap** (a min-heap "
           "of size k).",
     hint2="""1. Keep a min-heap with at most k values: the k largest seen so far.
2. `add(val)`: push `val`; if the heap has more than k values, pop the smallest.
3. The k-th largest is the smallest value in the heap: `heap[0]`.""",
     solution='''import heapq

class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = []
        for x in nums:
            self.add(x)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)          # drop the smallest; it can never be in the top k again
        return self.heap[0]''',
     why="Once a score is below the current k-th largest, a new score can only push it further down, so it can be "
         "thrown away. The heap holds just the k survivors, and its root (the smallest survivor) is the answer. "
         "Follow-up: each add costs O(log k) with O(k) memory, while sorting costs O(n log n) per add and keeps all "
         "n scores.",
     complexity="O(log k) per `add`, O(n log k) to build, O(k) space.",
     mistakes="Using a max-heap of all values (O(n) memory, O(k log n) per query). Returning `heap[0]` before "
              "trimming. Forgetting that `nums` can be shorter than k.",
     learn=["algo-heap"], source=("LeetCode 703", lc("kth-largest-element-in-a-stream")))

ex.q("Which id is missing? (bonus)", minutes=10, level="easy",
     prompt="""Optional. `nums` holds `n` different numbers taken from `0..n`, so exactly one number of that range is
missing. Return it, in O(n) time and O(1) extra space.

Examples:
- `[3, 0, 1]` -> `2`
- `[0, 1]` -> `2`
- `[9, 6, 4, 2, 3, 5, 7, 0, 1]` -> `8`""",
     stub="def missing_number(nums):\n    pass",
     tests="""check(missing_number, [
    ([3, 0, 1], 2),
    ([0, 1], 2),
    ([9, 6, 4, 2, 3, 5, 7, 0, 1], 8),
    ([0], 1),
    ([1], 0),
    ([1, 2, 3], 0),
])""",
     hint1="Signal: you know exactly what the full set should be. Pattern: **math on the expected total** (the sum "
           "formula or XOR); a hash set also works but uses O(n) space.",
     hint2="""1. The numbers `0..n` add up to `n * (n + 1) // 2`, where `n = len(nums)`.
2. Subtract the actual sum; the difference is the missing number.
3. (XOR version: XOR all indexes `0..n` and all values; pairs cancel, the missing one is left.)""",
     solution='''def missing_number(nums):
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)

# XOR version (no large intermediate sums in fixed-size integer languages)
def missing_number_xor(nums):
    x = len(nums)
    for i, v in enumerate(nums):
        x ^= i ^ v
    return x

print(missing_number_xor([3, 0, 1]))   # 2''',
     why="Comparing the expected total with the actual total isolates the one value that is absent. XOR works "
         "the same way because `a ^ a = 0`. Both need one pass and two variables.",
     complexity="O(n) time, O(1) space.",
     mistakes="Using `range(n)` instead of `0..n` (forgets that n itself can be missing, as in `[0, 1]`). Sorting "
              "first (O(n log n)).",
     learn=["algo-hashing"], source=("LeetCode 268", lc("missing-number")))

ex.save()
