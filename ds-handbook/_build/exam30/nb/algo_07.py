"""Day 7 algorithms (mock exam): Last Stone Weight, Majority Element, Merge Sorted Array."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from algo_common import lc

INTRO = """**Mock exam rules.**
- Start one 60 minute timer for the whole notebook and do not stop it between questions.
- Do not open any hint or solution until the timer ends. Then check, and read the solutions.
- For each problem, first say out loud: the pattern, the approach, and the time and space complexity. Then code.
- Run your own extra test (an edge case you chose) before you move on, like you would in a real exam.
- After the timer: score yourself (solved, solved after the timer, not solved) and log every miss."""

ex = Exam(7, "algorithms", intro=INTRO)
ex.setup()

ex.q("Smash the two heaviest", minutes=20, level="easy",
     prompt="""You have stones with positive integer weights. Each turn, take the two heaviest stones `x <= y` and smash
them: if `x == y` both are destroyed, otherwise only a stone of weight `y - x` remains. When at most one stone is
left, return its weight (or `0` if none is left).

Examples:
- `[2, 7, 4, 1, 8, 1]` -> `1` (8 and 7 leave 1, then 4 and 2 leave 2, then 2 and 1 leave 1, then 1 and 1 vanish,
  one stone of weight 1 remains)
- `[10, 4, 2, 10]` -> `2`
- `[2, 2]` -> `0`

Follow-up to answer out loud: what is the cost if you re-sort the list every turn instead?""",
     stub="def last_stone_weight(stones):\n    pass",
     tests="""check(last_stone_weight, [
    ([2, 7, 4, 1, 8, 1], 1),
    ([1], 1),
    ([2, 2], 0),
    ([10, 4, 2, 10], 2),
    ([3, 7, 2], 2),
    ([9, 3, 2, 10], 0),
    ([1, 3], 2),
])""",
     hint1="Signal: you repeatedly need the largest items of a collection that keeps changing. Pattern: **heap "
           "(priority queue)**; Python's `heapq` is a min-heap, so store negative weights.",
     hint2="""1. `heap = [-s for s in stones]`, then `heapq.heapify(heap)`.
2. While more than one stone: pop `y` (largest) and `x` (second largest), as positive numbers.
3. If `y != x`, push `-(y - x)` back.
4. Return `-heap[0]` if the heap is not empty, else 0.""",
     solution='''import heapq

def last_stone_weight(stones):
    heap = [-s for s in stones]          # negate: heapq is a min-heap
    heapq.heapify(heap)
    while len(heap) > 1:
        y = -heapq.heappop(heap)         # heaviest
        x = -heapq.heappop(heap)         # second heaviest
        if y != x:
            heapq.heappush(heap, -(y - x))
    return -heap[0] if heap else 0''',
     why="Each turn needs the two largest values of a set that changes. A heap gives the maximum in O(log n) per "
         "pop or push, so n turns cost O(n log n). Re-sorting every turn (the follow-up) costs O(n log n) per turn, "
         "so O(n^2 log n) in total.",
     complexity="O(n log n) time, O(n) space (O(1) extra if you heapify a negated copy in place).",
     mistakes="Forgetting to negate (pops the lightest stones). Pushing a 0 stone back when the two weights are "
              "equal. Returning `heap[0]` without flipping the sign.",
     learn=["algo-heap"], source=("LeetCode 1046", lc("last-stone-weight")))

ex.q("The value that wins the vote", minutes=20, level="easy",
     prompt="""`nums` has length `n` and one value appears more than `n / 2` times (it is guaranteed to exist). Return
that value. First give an O(n) time solution, then the follow-up: can you do it with O(1) extra space?

Examples:
- `[3, 2, 3]` -> `3`
- `[2, 2, 1, 1, 1, 2, 2]` -> `2`
- `[-1, -1, -1, 4]` -> `-1`""",
     stub="def majority_element(nums):\n    pass",
     tests="""check(majority_element, [
    ([3, 2, 3], 3),
    ([2, 2, 1, 1, 1, 2, 2], 2),
    ([1], 1),
    ([6, 5, 5], 5),
    ([-1, -1, -1, 4], -1),
    ([4, 4, 7, 7, 7, 4, 4], 4),
])""",
     hint1="Signal: count how often each value appears. Pattern: **hashing** (a count dict). Follow-up: "
           "Boyer-Moore voting, where different values cancel each other out.",
     hint2="""Count dict: count every value, return the one with count > n // 2.
Voting (O(1) space):
1. `candidate = None`, `votes = 0`.
2. For each `x`: if `votes == 0`, set `candidate = x`. Then `votes += 1` if `x == candidate` else `votes -= 1`.
3. Return `candidate` (valid because a majority is guaranteed).""",
     solution='''from collections import Counter

def majority_element(nums):              # O(n) time, O(n) space
    count = Counter(nums)
    return max(count, key=count.get)

def majority_element_vote(nums):         # follow-up: O(n) time, O(1) space
    candidate, votes = None, 0
    for x in nums:
        if votes == 0:
            candidate = x
        votes += 1 if x == candidate else -1
    return candidate

print(majority_element_vote([2, 2, 1, 1, 1, 2, 2]))   # 2''',
     why="The dict answer is the direct one. For the vote: pair each majority copy with a different value and "
         "cancel them; because the majority has more than half of the items, some copies always survive, so the "
         "final candidate is the majority. If the majority were not guaranteed, you would need a second pass to "
         "count the candidate.",
     complexity="Count dict: O(n) time, O(n) space. Voting: O(n) time, O(1) space. (Sorting and taking "
                "`nums[n // 2]` is O(n log n).)",
     mistakes="Returning the candidate without a verification pass when the majority is not guaranteed. "
              "Using `nums.count(x)` for every x (O(n^2)).",
     learn=["algo-hashing"], source=("LeetCode 169", lc("majority-element")))

ex.q("Merge into the bigger array", minutes=20, level="easy",
     prompt="""`nums1` has length `m + n`: its first `m` values are sorted, and the last `n` slots are zeros (free
space). `nums2` has `n` sorted values. Merge `nums2` into `nums1` **in place** so that `nums1` is fully sorted.
Return nothing. Target: O(m + n) time and O(1) extra space.

Examples:
- `nums1 = [1, 2, 3, 0, 0, 0], m = 3, nums2 = [2, 5, 6], n = 3` -> `nums1 = [1, 2, 2, 3, 5, 6]`
- `nums1 = [0], m = 0, nums2 = [1], n = 1` -> `nums1 = [1]`
- `nums1 = [4, 5, 0, 0], m = 2, nums2 = [1, 2], n = 2` -> `nums1 = [1, 2, 4, 5]`""",
     stub="def merge(nums1, m, nums2, n):\n    pass",
     tests="""def merged(nums1, m, nums2, n):
    merge(nums1, m, nums2, n)
    return nums1

check(merged, [
    (([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3), [1, 2, 2, 3, 5, 6]),
    (([1], 1, [], 0), [1]),
    (([0], 0, [1], 1), [1]),
    (([4, 5, 0, 0], 2, [1, 2], 2), [1, 2, 4, 5]),
    (([2, 0], 1, [1], 1), [1, 2]),
    (([1, 3, 5, 0, 0], 3, [3, 4], 2), [1, 3, 3, 4, 5]),
])""",
     hint1="Signal: two sorted arrays and free space only at the end of one of them. Pattern: **two pointers, "
           "filling from the back**.",
     hint2="""1. `i = m - 1` (last real value in nums1), `j = n - 1` (last in nums2), `w = m + n - 1` (write slot).
2. While `j >= 0`: if `i >= 0` and `nums1[i] > nums2[j]`, write `nums1[i]` and move `i`; else write `nums2[j]`
   and move `j`. Move `w` each time.
3. When `nums2` is used up, the rest of `nums1` is already in place.""",
     solution='''def merge(nums1, m, nums2, n):
    i, j, w = m - 1, n - 1, m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[w] = nums1[i]
            i -= 1
        else:
            nums1[w] = nums2[j]
            j -= 1
        w -= 1''',
     why="Filling from the front would overwrite values of `nums1` that are not merged yet. The back of `nums1` "
         "is free, and the largest remaining value always goes there, so writing from the back never destroys "
         "unread data. The loop can stop when `nums2` is empty because the left part of `nums1` is already sorted "
         "in place.",
     complexity="O(m + n) time, O(1) space.",
     mistakes="Merging from the front (overwrites data). Looping `while i >= 0` instead of `while j >= 0` "
              "(leftover `nums2` values never get copied). `nums1 = sorted(...)` rebinds the name and does not "
              "change the caller's list (and is O((m + n) log(m + n))).",
     learn=["algo-two-pointers"], source=("LeetCode 88", lc("merge-sorted-array")))

ex.save()
