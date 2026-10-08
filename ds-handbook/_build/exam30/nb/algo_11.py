import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _algo_mid_common import BIG

ex = Exam(11, "algorithms")
ex.setup(BIG)

# ---------------------------------------------------------------- Q1 daily temperatures (monotonic stack)
ex.q("Wait for a warmer day", minutes=15,
     prompt="""You get a list of daily temperatures. For every day, return how many days you must wait until a
**strictly** warmer day. If no warmer day comes later, write 0 for that day.

Example: `temps = [30, 40, 35, 32, 50]` gives `[1, 3, 2, 1, 0]`.
Day 0 (30) is beaten the next day (40). Day 1 (40) waits until day 4 (50), so 3 days. Day 4 has no warmer day after it.

Constraints: up to 100,000 days, integer temperatures. Aim for better than checking every pair.""",
     stub="""def daily_temperatures(temps):
    pass""",
     tests="""check(daily_temperatures, [
    ([30, 40, 35, 32, 50], [1, 3, 2, 1, 0]),
    ([73, 74, 75, 71, 69, 72, 76, 73], [1, 1, 4, 2, 1, 1, 0, 0]),
    ([50], [0]),                      # one day
    ([60, 50, 40], [0, 0, 0]),        # only colder days
    ([70, 70, 70], [0, 0, 0]),        # equal is NOT warmer
    ([30, 31, 32], [1, 1, 0]),
    ([40, 35, 35, 36, 41], [4, 2, 1, 1, 0]),
])
# larger input: 10,000 colder days in a row, then one hot day
n = 10_000
check_big("10,000 falling days then a hot day", lambda: daily_temperatures(list(range(n + 30, 30, -1)) + [n + 100]),
          [n - i for i in range(n)] + [0])""",
     hint1="""Signal: for each element you need the **next greater element** to its right. Every day is "waiting"
until something warmer pops up. Pattern: **monotonic stack** (a stack of indices whose temperatures are decreasing).""",
     hint2="""1. Keep a stack of indices of days that are still waiting for a warmer day.
2. Walk left to right. While today is warmer than the day on top of the stack, pop that index `j` and set
   `answer[j] = i - j`.
3. Push today's index. Days left in the stack at the end keep the default 0.""",
     solution="""def daily_temperatures(temps):
    answer = [0] * len(temps)
    stack = []                                   # indices; their temps are strictly decreasing from bottom to top
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:    # today resolves every colder day still waiting
            j = stack.pop()
            answer[j] = i - j
        stack.append(i)
    return answer""",
     why="""Each index is pushed once and popped at most once, so the total work is linear even though there is a
`while` inside the `for`. The stack only holds days that have not found a warmer day yet; they are in decreasing
order, so as soon as the top is not colder than today, nothing below it can be colder either.

**Follow-ups (what if...):**
- *What if temperatures arrive as a stream and you must output an answer as soon as it is known?* The same stack
  works online: when a day is popped, emit its answer at that moment. Days still in the stack are unresolved.
- *What if you need the previous warmer day instead?* Walk from right to left, or keep the same stack and read the
  top before pushing.
- *What if temperatures are known to lie in a tiny range, say 30 to 100?* You can walk from the right and keep `next_index[t]` for every
  temperature, then take the minimum over warmer values: O(n * 71). The stack is still simpler and fully general.
- *What if "warmer or equal" counts?* Change `<` to `<=` in the pop condition.""",
     complexity="O(n) time (each index is pushed and popped once), O(n) space for the stack in the worst case (falling temperatures).",
     mistakes="Using `<=` instead of `<` (equal days are not warmer). Storing temperatures instead of indices in the "
              "stack (you need the index to compute the distance). Writing the O(n^2) double loop, which fails the larger test.",
     learn=["algo-monotonic-stack", "algo-stack"],
     source=("LeetCode 739", "https://leetcode.com/problems/daily-temperatures/"))

# ---------------------------------------------------------------- Q2 top k frequent (heap)
ex.q("The k most common values", minutes=15,
     prompt="""Given a list of integers `nums` and an integer `k`, return the `k` values that appear most often.
You may return them in any order. The tests guarantee the answer is unique (no ties at the cut-off).

Example: `nums = [4, 4, 4, 9, 9, 1]`, `k = 2` gives `[4, 9]` (4 appears 3 times, 9 twice, 1 once).

Constraints: up to 100,000 numbers, `1 <= k <=` number of distinct values. Try to beat sorting all distinct values
(O(m log m)) when `k` is small.""",
     stub="""def top_k_frequent(nums, k):
    pass""",
     tests="""check(top_k_frequent, [
    (([4, 4, 4, 9, 9, 1], 2), [4, 9]),
    (([1, 1, 1, 2, 2, 3], 2), [1, 2]),
    (([7], 1), [7]),                              # single element
    (([5, 5, 6, 6, 6, 7], 1), [6]),
    (([-1, -1, 2, 2, 2, 3], 2), [2, -1]),         # negative values
    (([1, 2, 3], 3), [1, 2, 3]),                  # k = number of distinct values
    (([0, 0, 0, 0], 1), [0]),
], key=any_order)
# larger input: value v appears v times for v = 1..400 (80,200 numbers), shuffled
import random
big = [v for v in range(1, 401) for _ in range(v)]
random.Random(11).shuffle(big)
check_big("80,200 numbers, k = 5", lambda: top_k_frequent(big, 5), [396, 397, 398, 399, 400], key=any_order)""",
     hint1="""Signal: "the k largest / most frequent" means keep only the best k candidates. Pattern: **heap**
(a min-heap of size k over the counts), after counting with a hash map. Bucket sort by count is the O(n) alternative.""",
     hint2="""1. Count each value with `collections.Counter`.
2. Push `(count, value)` pairs into a min-heap; when the heap grows past `k`, pop the smallest.
3. The heap now holds the k most frequent values. (Shortcut: `heapq.nlargest(k, counts, key=counts.get)`.)
4. Bucket alternative: `buckets[c]` = values seen exactly `c` times; read buckets from high `c` down until you have k.""",
     solution="""import heapq
from collections import Counter

def top_k_frequent(nums, k):
    counts = Counter(nums)
    heap = []                                   # min-heap of (count, value), never bigger than k
    for value, c in counts.items():
        heapq.heappush(heap, (c, value))
        if len(heap) > k:
            heapq.heappop(heap)                 # drop the least frequent of the k + 1
    return [value for c, value in heap]

# O(n) variant: bucket sort by count
def top_k_frequent_buckets(nums, k):
    counts = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, c in counts.items():
        buckets[c].append(value)
    out = []
    for c in range(len(buckets) - 1, 0, -1):
        out += buckets[c]
        if len(out) >= k:
            return out[:k]""",
     why="""Counting is O(n). The heap never holds more than k items, so each push/pop costs O(log k) and the whole
selection is O(m log k) for m distinct values, which beats sorting when k is small. The bucket version uses the fact
that a count is at most n, so you can index buckets by count and avoid comparisons entirely.

**Follow-ups (what if...):**
- *What if the data is a stream that never ends?* Keep exact counts in a hash map plus a size-k heap that you
  refresh, or, when memory is tight, use an approximate sketch (Count-Min Sketch or the Misra-Gries / Space-Saving
  heavy hitters algorithm) that keeps only O(k) counters.
- *What if ties are possible at the cut-off?* Define the rule (for example the smaller value wins) and push
  `(count, -value)` so the heap breaks ties the way you want.
- *What if the data does not fit on one machine?* Count per shard (map), merge counts by key (reduce), then take
  the top k. Note that the top k of each shard is not enough on its own.
- *What if you need the k most frequent words of a big text?* Same pattern; the follow-up is usually about sorting
  ties alphabetically (LeetCode 692).""",
     complexity="Heap: O(n + m log k) time, O(m + k) space (m = distinct values). Buckets: O(n) time and space.",
     mistakes="Sorting the whole list of numbers instead of the counts. Using a max-heap of all m items and popping k "
              "times (fine, but O(m + k log m)); keeping a min-heap bigger than k. Forgetting that `heapq` is a min-heap.",
     learn=["algo-heap", "algo-hashing"],
     source=("LeetCode 347", "https://leetcode.com/problems/top-k-frequent-elements/"))

# ---------------------------------------------------------------- Q3 3Sum (two pointers)
ex.q("Three numbers that cancel out", minutes=20,
     prompt="""Given a list of integers, return every **distinct** triple of values `[a, b, c]` taken from three
different positions with `a + b + c == 0`. The same triple of values must appear only once, even if the list has
repeated numbers. Order of the triples and order inside a triple do not matter.

Example: `nums = [-2, 0, 1, 1, 2]` gives `[[-2, 0, 2], [-2, 1, 1]]`.
`nums = [0, 0, 0, 0]` gives `[[0, 0, 0]]` (once, not four times).

Constraints: up to 3,000 numbers. O(n^3) is too slow; aim for O(n^2).""",
     stub="""def three_sum(nums):
    pass""",
     tests="""check(three_sum, [
    ([-2, 0, 1, 1, 2], [[-2, 0, 2], [-2, 1, 1]]),
    ([-1, 0, 1, 2, -1, -4], [[-1, -1, 2], [-1, 0, 1]]),
    ([0, 1, 1], []),
    ([0, 0, 0, 0], [[0, 0, 0]]),                 # duplicates: one triple only
    ([], []),                                    # empty
    ([1, -1], []),                               # fewer than 3 numbers
    ([-4, -1, -1, 0, 1, 2, 2], [[-4, 2, 2], [-1, -1, 2], [-1, 0, 1]]),
], key=any_order)
# larger input: 1,000 odd numbers (three odd numbers never sum to 0)
check_big("1,000 odd numbers", lambda: three_sum(list(range(-999, 1000, 2))), [], key=any_order, limit=2.0)""",
     hint1="""Signal: find pairs/triples with a target sum, and duplicates must be skipped cleanly. After sorting,
fix one number and the problem becomes "two numbers with a given sum in a sorted array". Pattern: **two pointers**
(sort first).""",
     hint2="""1. Sort `nums`.
2. For each index `i` (skip it if `nums[i] == nums[i - 1]`; stop early if `nums[i] > 0`), set `lo = i + 1`,
   `hi = len - 1`.
3. While `lo < hi`: if the sum is too small move `lo` right, too big move `hi` left.
4. On a hit, record it, then move both pointers and skip equal values so the same triple is not added again.""",
     solution="""def three_sum(nums):
    nums = sorted(nums)
    n, out = len(nums), []
    for i in range(n - 2):
        if nums[i] > 0:                      # smallest value positive: no triple can reach 0
            break
        if i > 0 and nums[i] == nums[i - 1]: # same first value as before: same triples
            continue
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s < 0:
                lo += 1
            elif s > 0:
                hi -= 1
            else:
                out.append([nums[i], nums[lo], nums[hi]])
                lo += 1
                hi -= 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
    return out""",
     why="""Sorting makes two things easy: the inner search becomes a two-pointer sweep (a sum that is too small can
only grow by moving `lo` right), and duplicates sit next to each other so you skip them by comparing with the previous
value. There are n choices for the first number and an O(n) sweep for each, so O(n^2) overall.

**Follow-ups (what if...):**
- *What if the target is not 0 but `t`?* Compare the sum with `t` instead of 0; remove the `nums[i] > 0` early stop
  (it only holds for `t = 0`).
- *What if you need 4Sum (or kSum)?* Add one more outer loop per extra number (O(n^3) for 4Sum) and keep the
  two-pointer core; write it recursively for general k.
- *What if you may not sort (you must keep the order or the data is read-only)?* Use a hash set per `i` for the
  inner two-sum: still O(n^2), but deduplication needs a set of sorted tuples.
- *What if you only need the count of triples (with duplicates by position)?* Count pairs with a hash map instead of
  listing them; listing can be O(n^2) items by itself.
- *What if you need the triple whose sum is closest to the target (LeetCode 16)?* Same sweep, track the best
  `abs(s - t)`.""",
     complexity="O(n^2) time (sort O(n log n) plus n two-pointer sweeps), O(1) extra space besides the output (sorting may use O(n)).",
     mistakes="Using a set of tuples to remove duplicates after an O(n^3) search (correct but too slow). Skipping "
              "duplicates of `nums[i]` with `nums[i] == nums[i + 1]` (that skips valid triples like [-1, -1, 2]). "
              "Forgetting to move both pointers after a hit, which loops forever.",
     learn=["algo-two-pointers", "algo-sorting-intervals"],
     source=("LeetCode 15", "https://leetcode.com/problems/3sum/"))

ex.save()
