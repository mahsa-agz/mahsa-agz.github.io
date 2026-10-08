"""Day 5 algorithms (easy): Climbing Stairs, Maximum Average Subarray I, Invert Binary Tree
+ bonus Remove Duplicates from Sorted Array."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from algo_common import TREE_CODE, lc

ex = Exam(5, "algorithms")
ex.setup(TREE_CODE)
ex.text("""The setup cell gives you `TreeNode`, `build_tree([4, 2, 7])` (level order, `None` = no child) and
`tree_values(root)`.""")

ex.q("Ways up the staircase", minutes=15, level="easy",
     prompt="""A staircase has `n` steps. Each move you climb either 1 or 2 steps. In how many different orders can you
reach the top? `n` can be up to 45, so trying every sequence one by one is too slow.

Examples:
- `n = 2` -> `2` (1+1, 2)
- `n = 3` -> `3` (1+1+1, 1+2, 2+1)
- `n = 5` -> `8`""",
     stub="def climb_stairs(n):\n    pass",
     tests="""check(climb_stairs, [
    (1, 1),
    (2, 2),
    (3, 3),
    (5, 8),
    (10, 89),
    (45, 1836311903),
])""",
     hint1="Signal: the count for `n` is built from the counts for smaller `n` (the last move was 1 or 2 steps). "
           "Pattern: **1-D dynamic programming**.",
     hint2="""1. State: `ways(i)` = number of ways to reach step `i`.
2. Transition: `ways(i) = ways(i-1) + ways(i-2)`; base cases `ways(1) = 1`, `ways(2) = 2`.
3. You only need the last two values: keep two variables and roll them forward.""",
     solution='''def climb_stairs(n):
    a, b = 1, 1               # ways to reach step 0 and step 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b''',
     why="Every route to step n ends with a 1-step from n-1 or a 2-step from n-2, and those two groups do not "
         "overlap, so the counts add (it is the Fibonacci sequence). Plain recursion recomputes the same "
         "sub-answers again and again (O(2^n)); storing them makes it linear.",
     complexity="O(n) time, O(1) space.",
     mistakes="Plain recursion without memo (times out at n = 45). Wrong base case (`ways(0)` = 1, not 0). "
              "Off-by-one in the loop count.",
     learn=["algo-dp-1d"], source=("LeetCode 70", lc("climbing-stairs")))

ex.q("Best stretch of k days", minutes=15, level="easy",
     prompt="""`nums` holds daily values and `k` is a window length. Among all blocks of exactly `k` consecutive
values, return the largest average (a float). Aim for O(n), not O(n * k).

Examples:
- `nums = [1, 12, -5, -6, 50, 3], k = 4` -> `12.75` (block `[12, -5, -6, 50]`, sum 51)
- `nums = [0, 4, 0, 3, 2], k = 1` -> `4.0`
- `nums = [-1, -2, -3], k = 2` -> `-1.5`""",
     stub="def find_max_average(nums, k):\n    pass",
     tests="""check(find_max_average, [
    (([1, 12, -5, -6, 50, 3], 4), 12.75),
    (([5], 1), 5.0),
    (([0, 4, 0, 3, 2], 1), 4.0),
    (([-1, -2, -3], 2), -1.5),
    (([4, 0, 4, 3, 3], 5), 2.8),
    (([7, 7, 1, 1, 9, 9], 2), 9.0),
])""",
     hint1="Signal: a block of fixed length that moves one step at a time. Pattern: **fixed-size sliding window**.",
     hint2="""1. Sum the first `k` values: `window`.
2. For `i` from `k` to the end: `window += nums[i] - nums[i - k]` (one value enters, one leaves).
3. Track the best sum; return `best / k` (divide once at the end).""",
     solution='''def find_max_average(nums, k):
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best / k''',
     why="Neighbouring windows share k-1 values, so you only add the new value and remove the old one. That is "
         "O(1) work per step instead of re-summing k values. Comparing sums is the same as comparing averages "
         "because k is fixed.",
     complexity="O(n) time, O(1) space.",
     mistakes="Starting `best` at 0 (wrong when every value is negative, as in `[-1, -2, -3]`). Re-summing each "
              "window with `sum(nums[i:i+k])` (O(n * k)). Integer division `//`.",
     learn=["algo-sliding-window"], source=("LeetCode 643", lc("maximum-average-subarray-i")))

ex.q("Mirror the tree", minutes=10, level="easy",
     prompt="""Turn a binary tree into its mirror image: for every node, the left and right children swap places.
Return the root.

Examples (level order):
- `[4, 2, 7, 1, 3, 6, 9]` -> `[4, 7, 2, 9, 6, 3, 1]`
- `[2, 1, 3]` -> `[2, 3, 1]`
- `[1, 2]` -> `[1, None, 2]`""",
     stub="def invert_tree(root):\n    pass",
     tests="""def mirrored(vals):
    return tree_values(invert_tree(build_tree(vals)))

check(mirrored, [
    ([4, 2, 7, 1, 3, 6, 9], [4, 7, 2, 9, 6, 3, 1]),
    ([2, 1, 3], [2, 3, 1]),
    ([], []),
    ([1], [1]),
    ([1, 2], [1, None, 2]),
    ([1, 2, None, 3], [1, None, 2, None, 3]),
])""",
     hint1="Signal: do the same small action at every node of the tree. Pattern: **tree traversal (DFS or BFS)**.",
     hint2="""1. Base case: `None` -> return `None`.
2. Swap: `root.left, root.right = root.right, root.left`.
3. Recurse into both children (or push them on a stack / queue). Return `root`.""",
     solution='''def invert_tree(root):
    if root is None:
        return None
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root

# iterative version (no recursion limit):
def invert_tree_iter(root):
    stack = [root]
    while stack:
        node = stack.pop()
        if node:
            node.left, node.right = node.right, node.left
            stack += [node.left, node.right]
    return root

print(tree_values(invert_tree_iter(build_tree([2, 1, 3]))))  # [2, 3, 1]''',
     why="A mirror image is just \"swap the children\" applied at every node; the order of visiting does not "
         "matter, so any traversal works. Each node is touched once.",
     complexity="O(n) time; O(h) space for recursion or the stack.",
     mistakes="Swapping only the root's children. Writing `root.left = invert_tree(root.right)` and then "
              "`root.right = invert_tree(root.left)` on two lines: the second line reads the already changed "
              "left child. Use one tuple assignment or a temp variable.",
     learn=["algo-trees"], source=("LeetCode 226", lc("invert-binary-tree")))

ex.q("Squeeze out repeats in a sorted list (bonus)", minutes=10, level="easy",
     prompt="""Optional. `nums` is sorted. Rearrange it in place so that its first `k` positions hold each distinct
value once, in order, and return `k`. What is left after position `k` does not matter.

Examples:
- `[1, 1, 2]` -> `k = 2`, first two values `[1, 2]`
- `[0, 0, 1, 1, 1, 2, 2, 3, 3, 4]` -> `k = 5`, first five values `[0, 1, 2, 3, 4]`""",
     stub="def remove_duplicates(nums):\n    pass",
     tests="""def dedup(nums):
    k = remove_duplicates(nums)
    return (k, nums[:k]) if isinstance(k, int) else k

check(dedup, [
    ([1, 1, 2], (2, [1, 2])),
    ([0, 0, 1, 1, 1, 2, 2, 3, 3, 4], (5, [0, 1, 2, 3, 4])),
    ([7], (1, [7])),
    ([2, 2, 2], (1, [2])),
    ([-3, -1, 0, 5], (4, [-3, -1, 0, 5])),
])""",
     hint1="Signal: sorted input, in-place rewrite, keep order. Pattern: **two pointers** (slow write, fast read).",
     hint2="""1. `k = 1` (the first value is always kept; handle an empty list separately).
2. For `i` from 1: if `nums[i] != nums[k - 1]`, write `nums[k] = nums[i]` and `k += 1`.
3. Return `k`.""",
     solution='''def remove_duplicates(nums):
    if not nums:
        return 0
    k = 1
    for i in range(1, len(nums)):
        if nums[i] != nums[k - 1]:
            nums[k] = nums[i]
            k += 1
    return k''',
     why="Because the list is sorted, equal values sit next to each other, so a value is new exactly when it "
         "differs from the last kept value. The write pointer never passes the read pointer, so nothing is "
         "overwritten before it is read.",
     complexity="O(n) time, O(1) space.",
     mistakes="Using `set(nums)` (loses the in-place requirement and the order guarantee). Deleting from the list "
              "while looping over it.",
     learn=["algo-two-pointers"], source=("LeetCode 26", lc("remove-duplicates-from-sorted-array")))

ex.save()
