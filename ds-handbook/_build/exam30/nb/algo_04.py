"""Day 4 algorithms (easy): Running Sum, Merge Two Sorted Lists, Move Zeroes + bonus Diameter of Binary Tree."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from algo_common import LIST_CODE, TREE_CODE, lc

ex = Exam(4, "algorithms")
ex.setup(LIST_CODE + "\n\n" + TREE_CODE)
ex.text("""The setup cell gives you `ListNode`, `build_list`, `list_values`, `TreeNode`, `build_tree` (level order,
`None` = no child) and `tree_values`. The tests use them to convert plain lists to nodes and back.""")

ex.q("Totals so far", minutes=10, level="easy",
     prompt="""Given `nums`, return a list where position `i` holds `nums[0] + nums[1] + ... + nums[i]`. Then answer
out loud: once you have this list, how do you get the sum of `nums[i..j]` in O(1)?

Examples:
- `[3, 1, 2, 10, 1]` -> `[3, 4, 6, 16, 17]`
- `[1, 1, 1]` -> `[1, 2, 3]`
- `[]` -> `[]`""",
     stub="def running_sum(nums):\n    pass",
     tests="""check(running_sum, [
    ([1, 2, 3, 4], [1, 3, 6, 10]),
    ([1, 1, 1, 1, 1], [1, 2, 3, 4, 5]),
    ([3, 1, 2, 10, 1], [3, 4, 6, 16, 17]),
    ([], []),
    ([5], [5]),
    ([-2, 5, -1], [-2, 3, 2]),
])""",
     hint1="Signal: each answer is the previous answer plus one new number. Pattern: **prefix sum**.",
     hint2="""1. `total = 0`, `out = []`.
2. For each `x`: `total += x`, append `total`.
3. Follow-up: with `pre[0] = 0` and `pre[i+1] = nums[0] + ... + nums[i]`, the sum of `nums[i..j]` is
   `pre[j+1] - pre[i]`.""",
     solution='''def running_sum(nums):
    out, total = [], 0
    for x in nums:
        total += x
        out.append(total)
    return out

# same thing with the standard library
from itertools import accumulate
print(list(accumulate([3, 1, 2, 10, 1])))   # [3, 4, 6, 16, 17]''',
     why="Recomputing each total from scratch is O(n^2). Carrying the total forward makes it O(n). This list is "
         "the building block for O(1) range sums (`pre[j+1] - pre[i]`), which comes back on later days. In "
         "pandas the same idea is `df['x'].cumsum()`, and in SQL it is `SUM(x) OVER (ORDER BY t)`.",
     complexity="O(n) time, O(n) space for the output (O(1) extra if you overwrite `nums` in place).",
     mistakes="Off-by-one in the range-sum formula (forgetting the leading 0). Writing a nested loop.",
     learn=["algo-prefix-sum"], source=("LeetCode 1480", lc("running-sum-of-1d-array")))

ex.q("Zip two sorted chains", minutes=15, level="easy",
     prompt="""You get the heads of two linked lists, each sorted in increasing order. Splice their nodes together into
one sorted list (reuse the nodes, do not create new values) and return its head.

Examples (values):
- `1 -> 2 -> 4` and `1 -> 3 -> 4` -> `1 -> 1 -> 2 -> 3 -> 4 -> 4`
- empty and `0` -> `0`
- `5` and `1 -> 2 -> 3` -> `1 -> 2 -> 3 -> 5`""",
     stub="def merge_two_lists(l1, l2):\n    pass",
     tests="""def merged_values(a, b):
    return list_values(merge_two_lists(build_list(a), build_list(b)))

check(merged_values, [
    (([1, 2, 4], [1, 3, 4]), [1, 1, 2, 3, 4, 4]),
    (([], []), []),
    (([], [0]), [0]),
    (([5], [1, 2, 3]), [1, 2, 3, 5]),
    (([1, 1], [1]), [1, 1, 1]),
    (([-3, 0, 7], [-5, 8]), [-5, -3, 0, 7, 8]),
])""",
     hint1="Signal: two sorted sequences, always take the smaller front item. Pattern: **linked list merge with a "
           "dummy head** (the merge step of merge sort).",
     hint2="""1. Create `dummy = ListNode()` and `tail = dummy`.
2. While both lists are non-empty: attach the smaller head to `tail.next`, advance that list, advance `tail`.
3. Attach whatever is left (`l1 or l2`) to `tail.next`.
4. Return `dummy.next`.""",
     solution='''def merge_two_lists(l1, l2):
    dummy = tail = ListNode()
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next, l1 = l1, l1.next
        else:
            tail.next, l2 = l2, l2.next
        tail = tail.next
    tail.next = l1 or l2          # one list is empty; the other is already sorted
    return dummy.next''',
     why="The smallest remaining value is always at the front of one of the two lists, so one comparison decides "
         "each node. The dummy head removes the special case of choosing the first node. The leftover tail can be "
         "attached in one step because it is already sorted.",
     complexity="O(n + m) time, O(1) extra space (nodes are reused).",
     mistakes="Forgetting to attach the leftover list. Returning `dummy` instead of `dummy.next`. Creating new "
              "nodes (works, but uses O(n + m) space and is not what was asked).",
     learn=["algo-linked-list"], source=("LeetCode 21", lc("merge-two-sorted-lists")))

ex.q("Push the zeros to the back", minutes=12, level="easy",
     prompt="""Move all `0` values of `nums` to the end **in place**, keeping the other values in their original order.
Return nothing; the test reads `nums` afterwards. Do not make a copy of the list.

Examples:
- `[0, 1, 0, 3, 12]` -> `[1, 3, 12, 0, 0]`
- `[4, 0, 5]` -> `[4, 5, 0]`
- `[0]` -> `[0]`""",
     stub="def move_zeroes(nums):\n    pass",
     tests="""def after_move(nums):
    move_zeroes(nums)
    return nums

check(after_move, [
    ([0, 1, 0, 3, 12], [1, 3, 12, 0, 0]),
    ([0], [0]),
    ([4, 0, 5], [4, 5, 0]),
    ([1, 2, 3], [1, 2, 3]),
    ([0, 0, 1], [1, 0, 0]),
    ([2, 0, 0, -1, 0, 7], [2, -1, 7, 0, 0, 0]),
])""",
     hint1="Signal: rearrange in place while keeping relative order. Pattern: **two pointers** (a slow write "
           "pointer and a fast read pointer).",
     hint2="""1. `write = 0`.
2. For each `read` index: if `nums[read] != 0`, swap `nums[write]` and `nums[read]`, then `write += 1`.
3. Everything from `write` onward is now 0.""",
     solution='''def move_zeroes(nums):
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1''',
     why="`write` marks where the next non-zero value belongs. The read pointer finds non-zeros in their "
         "original order, so their order is kept, and the swap pushes zeros behind them. Every element is read "
         "once.",
     complexity="O(n) time, O(1) space.",
     mistakes="Removing zeros with `nums.remove(0)` inside a loop (O(n^2) and skips elements). Building a new list "
              "and assigning `nums = ...` (only rebinds the local name; use `nums[:] = ...` if you must).",
     learn=["algo-two-pointers"], source=("LeetCode 283", lc("move-zeroes")))

ex.q("Widest path in a tree (bonus)", minutes=15, level="easy",
     prompt="""Optional. Return the length, counted in edges, of the longest path between any two nodes of a binary
tree. The path does not have to pass through the root.

Examples (level order, `None` = missing child):
- `[1, 2, 3, 4, 5]` -> `3` (path 4, 2, 1, 3)
- `[1, 2]` -> `1`
- `[1, 2, None, 3, 4, 5, None, None, 6]` -> `4` (path 5, 3, 2, 4, 6, which skips the root)""",
     stub="def diameter(root):\n    pass",
     tests="""def diameter_of(vals):
    return diameter(build_tree(vals))

check(diameter_of, [
    ([1, 2, 3, 4, 5], 3),
    ([1, 2], 1),
    ([1], 0),
    ([], 0),
    ([1, 2, None, 3, 4, 5, None, None, 6], 4),
    ([1, 2, 3, 4, None, None, 5, 6, None, None, 7], 6),
])""",
     hint1="Signal: a value for every node (its height) plus a best answer that can be anywhere. Pattern: **tree "
           "DFS that returns height and updates a global best**.",
     hint2="""1. Write `height(node)`: 0 for None, else `1 + max(height(left), height(right))`.
2. Inside it, before returning, update `best = max(best, height(left) + height(right))`: the longest path that
   bends at this node.
3. Call it on the root and return `best`.""",
     solution='''def diameter(root):
    best = 0
    def height(node):
        nonlocal best
        if node is None:
            return 0
        left, right = height(node.left), height(node.right)
        best = max(best, left + right)       # path that bends at this node
        return 1 + max(left, right)
    height(root)
    return best''',
     why="Every path has one highest node where it bends; there it uses the left height plus the right height. "
         "Computing heights bottom-up visits each node once and checks every possible bend point. Calling a "
         "separate height function from every node would be O(n^2).",
     complexity="O(n) time, O(h) recursion space.",
     mistakes="Returning `left + right` at the root only (fails when the best path skips the root). Counting "
              "nodes instead of edges. Forgetting `nonlocal`.",
     learn=["algo-trees"], source=("LeetCode 543", lc("diameter-of-binary-tree")))

ex.save()
