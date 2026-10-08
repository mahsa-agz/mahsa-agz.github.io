import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _algo_mid_common import BIG, TREE

ex = Exam(12, "algorithms")
ex.setup(BIG + "\n\n" + TREE)
ex.text("The setup cell also defines `TreeNode`, `build(level_order_list)` (LeetCode's tree format, `None` = no "
        "child) and `find(root, value)` for the tree question.")

# ---------------------------------------------------------------- Q1 search rotated sorted array (binary search)
ex.q("Find a value in a shifted sorted list", minutes=18,
     prompt="""A sorted list of **distinct** integers was rotated at some unknown point: a block from the front was
moved to the back. Example: `[2, 5, 8, 11, 13, 17]` rotated by 2 becomes `[8, 11, 13, 17, 2, 5]`.

Given the rotated list `nums` and a `target`, return the index of `target`, or `-1` if it is not there.
Your solution must run in O(log n).

Examples: `search([8, 11, 13, 17, 2, 5], 2)` gives `4`. `search([8, 11, 13, 17, 2, 5], 9)` gives `-1`.""",
     stub="""def search(nums, target):
    pass""",
     tests="""check(search, [
    (([8, 11, 13, 17, 2, 5], 2), 4),
    (([8, 11, 13, 17, 2, 5], 9), -1),
    (([4, 5, 6, 7, 0, 1, 2], 0), 4),
    (([1], 0), -1),                         # one element, missing
    (([1], 1), 0),                          # one element, found
    (([3, 1], 1), 1),                       # two elements, rotated
    (([1, 2, 3, 4, 5], 4), 3),              # not rotated at all
    (([6, 7, 1, 2, 3, 4, 5], 7), 1),        # target in the left (big) part
])
# larger input: 1,000,000 values rotated by half, 1,004 searches (a linear scan per search is too slow)
big = list(range(500_000, 1_000_000)) + list(range(500_000))
targets = list(range(0, 1_000_000, 997)) + [-5, 1_000_001]
want = [t + 500_000 if t < 500_000 else t - 500_000 for t in targets[:-2]] + [-1, -1]
check_big("1e6 rotated values, 1,004 searches", lambda: [search(big, t) for t in targets], want)""",
     hint1="""Signal: sorted data and an O(log n) requirement. Even after rotation, if you cut the list in the middle,
**one half is always sorted**. Pattern: **binary search** (modified: decide which half is sorted, then whether the
target lies inside it).""",
     hint2="""1. `lo, hi = 0, n - 1`. While `lo <= hi`: `mid = (lo + hi) // 2`; return `mid` on a hit.
2. If `nums[lo] <= nums[mid]`, the left half is sorted: if `nums[lo] <= target < nums[mid]` go left (`hi = mid - 1`),
   else go right.
3. Otherwise the right half is sorted: if `nums[mid] < target <= nums[hi]` go right (`lo = mid + 1`), else go left.
4. Return -1 when the range is empty.""",
     solution="""def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:                 # left half [lo..mid] is sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                     # right half [mid..hi] is sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1""",
     why="""The rotation point can be in at most one of the two halves, so the other half is a normal sorted range.
For the sorted half you can test "is the target inside?" with two comparisons; if yes you search there, if not the
target can only be in the other half. Each step halves the range, so O(log n).

**Follow-ups (what if...):**
- *What if the list can contain duplicates (LeetCode 81)?* When `nums[lo] == nums[mid] == nums[hi]` you cannot tell
  which half is sorted; shrink with `lo += 1, hi -= 1`. The worst case becomes O(n) (for example all values equal).
- *What if you need the rotation point or the minimum (LeetCode 153)?* Binary search comparing `nums[mid]` with
  `nums[hi]`: if bigger, the minimum is right of `mid`, else at `mid` or left of it.
- *What if you first find the rotation point, then do a normal binary search on the right part?* Also O(log n) and
  often easier to get right under pressure: two simple binary searches instead of one tricky one.
- *What if the data is on disk or remote and each read is expensive?* Binary search reads only O(log n) items, which
  is why it is the right tool for sorted files and sorted database indexes.""",
     complexity="O(log n) time, O(1) space.",
     mistakes="Using `<` instead of `<=` in `nums[lo] <= nums[mid]` (breaks when `lo == mid`, for example two elements). "
              "Using strict or non-strict bounds wrongly in the range checks so the target at an edge is missed. "
              "Calling `nums.index(target)` (O(n); fails the larger test).",
     learn=["algo-binary-search"],
     source=("LeetCode 33", "https://leetcode.com/problems/search-in-rotated-sorted-array/"))

# ---------------------------------------------------------------- Q2 subarray sum equals k (prefix sum + hash map)
ex.q("Count stretches with a given total", minutes=18,
     prompt="""Given a list of integers `nums` (it may contain **negative numbers and zeros**) and an integer `k`,
count how many contiguous non-empty subarrays have a sum of exactly `k`.

Example: `nums = [2, -1, 1, 2]`, `k = 2` gives `4`: the subarrays `[2]` (start), `[2, -1, 1]`, `[-1, 1, 2]` and
`[2]` (end).

Constraints: up to 20,000 numbers. O(n^2) is too slow for the larger test.""",
     stub="""def subarray_sum(nums, k):
    pass""",
     tests="""check(subarray_sum, [
    (([2, -1, 1, 2], 2), 4),
    (([1, 1, 1], 2), 2),
    (([1, 2, 3], 3), 2),
    (([3], 3), 1),                          # one element
    (([1, -1, 0], 0), 3),                   # zeros and negatives
    (([0, 0, 0], 0), 6),                    # every subarray counts
    (([1, 2, 1, 2, 1], 3), 4),
    (([5, 6], 4), 0),                       # none
])
# larger input: [1, -1] * 5,000 and k = 0 has 25,000,000 matching subarrays
check_big("10,000 numbers alternating 1, -1", lambda: subarray_sum([1, -1] * 5_000, 0), 25_000_000)""",
     hint1="""Signal: "count subarrays with sum k" and **negative numbers are allowed**, so a sliding window does not
work (the sum is not monotone). Pattern: **prefix sum + hash map**: the sum of `nums[i..j]` is
`prefix[j + 1] - prefix[i]`.""",
     hint2="""1. Keep a running sum `s` and a counter `seen` of how many times each prefix sum occurred; start with
`seen = {0: 1}` (the empty prefix).
2. For each number: `s += x`; every earlier prefix equal to `s - k` closes a subarray ending here, so
   `count += seen[s - k]`.
3. Then `seen[s] += 1`. Order matters: count first, then record.""",
     solution="""from collections import defaultdict

def subarray_sum(nums, k):
    seen = defaultdict(int)
    seen[0] = 1                    # empty prefix: lets a subarray start at index 0
    s = count = 0
    for x in nums:
        s += x
        count += seen[s - k]       # earlier prefixes p with s - p == k
        seen[s] += 1
    return count""",
     why="""A subarray ending at position j has sum k exactly when some earlier prefix sum equals
`current_prefix - k`. The hash map answers "how many earlier prefixes had that value" in O(1), so one pass is enough.
The `{0: 1}` start handles subarrays that begin at index 0.

**Follow-ups (what if...):**
- *What if all numbers are positive?* Then a sliding window works with O(1) extra space: grow right, shrink left while
  the sum is above k.
- *What if you need the longest subarray with sum k (not the count)?* Store the first index where each prefix sum
  appears and maximize `j - first[s - k]`.
- *What if the question is "sum divisible by k" (LeetCode 974)?* Key the map by `s % k` instead of `s`.
- *What if nums is a stream?* The same loop works online with O(distinct prefixes) memory; you can report the count
  so far at any time.
- *What if you get many queries "sum of nums[i..j]" on a fixed array?* Precompute the prefix array once; each query
  is then O(1).""",
     complexity="O(n) time, O(n) space for the map of prefix sums.",
     mistakes="Using a sliding window (wrong with negatives and zeros). Forgetting `seen[0] = 1`. Updating `seen[s]` "
              "before counting (counts an empty subarray when k = 0). Building all subarrays (O(n^2) or worse).",
     learn=["algo-prefix-sum", "algo-hashing"],
     source=("LeetCode 560", "https://leetcode.com/problems/subarray-sum-equals-k/"))

# ---------------------------------------------------------------- Q3 level order traversal (trees, BFS)
ex.q("A tree, one row at a time", minutes=15,
     prompt="""Given the root of a binary tree, return its values row by row: the first list is the root, the next
list holds its children from left to right, and so on. An empty tree gives `[]`.

Example (level-order input format, `None` = no child): `[3, 9, 20, None, None, 15, 7]` is

```
    3
   / \\
  9   20
     /  \\
    15   7
```
and the answer is `[[3], [9, 20], [15, 7]]`.

The tests call your function through `rows_of(values)`, which builds the tree with `build()`. The larger test uses a
5,000-level deep tree (a chain), so watch out for recursion depth.""",
     stub="""def level_order(root):
    pass""",
     tests="""def rows_of(values):
    return level_order(build(values))

check(rows_of, [
    ([3, 9, 20, None, None, 15, 7], [[3], [9, 20], [15, 7]]),
    ([1], [[1]]),                                           # one node
    ([], []),                                               # empty tree
    ([1, 2, None, 3], [[1], [2], [3]]),                      # left chain
    ([1, None, 2, None, 3], [[1], [2], [3]]),                # right chain
    ([1, 2, 3, 4, 5, 6, 7], [[1], [2, 3], [4, 5, 6, 7]]),    # full tree
    ([1, 2, 3, None, 4, None, 5], [[1], [2, 3], [4, 5]]),    # gaps in the middle
])
# larger inputs: a 5,000-deep chain and a complete tree with 65,535 nodes
chain = [1]
for v in range(2, 5_001):
    chain += [None, v]
check_big("chain of 5,000 nodes", lambda: rows_of(chain), [[v] for v in range(1, 5_001)])
check_big("complete tree, 65,535 nodes", lambda: rows_of(list(range(1, 2**16))),
          [list(range(2**d, 2**(d + 1))) for d in range(16)])""",
     hint1="""Signal: "level by level" or "row by row" in a tree. Pattern: **tree BFS** with a queue, processing one
level at a time (the queue length at the start of a level is the number of nodes in that level).""",
     hint2="""1. If the root is `None`, return `[]`. Put the root in a `deque`.
2. While the queue is not empty: `size = len(queue)`; pop exactly `size` nodes, collect their values, and push
   their non-empty children.
3. Append the collected row to the answer.""",
     solution="""from collections import deque

def level_order(root):
    if root is None:
        return []
    out, queue = [], deque([root])
    while queue:
        row = []
        for _ in range(len(queue)):        # exactly the nodes of the current level
            node = queue.popleft()
            row.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        out.append(row)
    return out""",
     why="""A queue releases nodes in the order they were discovered, which is level order. Freezing `len(queue)` at
the start of each round separates one level from the next without storing depths. It is iterative, so a 5,000-deep
tree is no problem, unlike a recursive DFS that hits Python's recursion limit (about 1,000 by default).

**Follow-ups (what if...):**
- *What if you want zigzag order (LeetCode 103)?* Same BFS; reverse every second row (or append to a deque from the
  other side).
- *What if you only need the rightmost value of each row, the row averages or the row maxima?* Same loop, different
  aggregation per row.
- *What if you must use DFS?* Pass the depth down: `out[depth].append(val)`, creating the row when `depth == len(out)`.
  Same O(n), but recursion depth equals the tree height.
- *What if the tree is huge and very wide?* BFS memory is the widest level (up to about n/2 for a complete tree); DFS
  memory is the height. Pick based on the tree's shape.""",
     complexity="O(n) time, O(w) extra space where w is the maximum width of a level (up to about n/2).",
     mistakes="Using `queue.pop(0)` on a list (O(n) per pop). Reading `len(queue)` inside the loop condition while "
              "pushing children, which mixes levels. Forgetting the empty tree. Recursion that fails on deep trees.",
     learn=["algo-trees", "algo-graphs-bfs-dfs"],
     source=("LeetCode 102", "https://leetcode.com/problems/binary-tree-level-order-traversal/"))

ex.save()
