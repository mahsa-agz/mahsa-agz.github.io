"""Day 2 algorithms (easy): Best Time to Buy and Sell Stock, Contains Duplicate, Binary Search
+ bonus Valid Palindrome II."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from algo_common import lc

ex = Exam(2, "algorithms")
ex.setup()

ex.q("One buy, one sell", minutes=15, level="easy",
     prompt="""`prices[i]` is the price of a stock on day `i`. You may buy once and later sell once (the sell day must
come after the buy day). Return the largest possible profit, or `0` if no trade makes money.

Examples:
- `[7, 1, 5, 3, 6, 4]` -> `5` (buy at 1, sell at 6)
- `[7, 6, 4, 3, 1]` -> `0` (prices only fall)
- `[2, 4, 1]` -> `2` (the later low of 1 comes too late to help)""",
     stub="def max_profit(prices):\n    pass",
     tests="""check(max_profit, [
    ([7, 1, 5, 3, 6, 4], 5),
    ([7, 6, 4, 3, 1], 0),
    ([1], 0),
    ([2, 4, 1], 2),
    ([3, 3, 3], 0),
    ([2, 1, 2, 1, 0, 1, 2], 2),
])""",
     hint1="Signal: for every day you only need one fact about the past (the cheapest price so far). Pattern: "
           "**one pass over the array with a running minimum** (arrays and strings; a greedy idea).",
     hint2="""1. `lowest = infinity`, `best = 0`.
2. For each price: `lowest = min(lowest, price)`.
3. `best = max(best, price - lowest)` (selling today after buying at the lowest earlier price).
4. Return `best`.""",
     solution='''def max_profit(prices):
    lowest = float("inf")
    best = 0
    for p in prices:
        lowest = min(lowest, p)
        best = max(best, p - lowest)
    return best''',
     why="If you sell on day j, the best buy day is the minimum price before j. Keeping that minimum as you go "
         "turns the O(n^2) pair search into one pass. Updating `lowest` before `best` is safe because selling on "
         "the same day gives profit 0, never a fake gain.",
     complexity="O(n) time, O(1) space.",
     mistakes="Using `max(prices) - min(prices)`, which ignores the order (gives 3 instead of 2 for `[2, 4, 1]`). "
              "Returning a negative number when prices only fall.",
     learn=["algo-arrays-strings", "algo-greedy"], source=("LeetCode 121", lc("best-time-to-buy-and-sell-stock")))

ex.q("Any repeats?", minutes=10, level="easy",
     prompt="""Return `True` if some value appears at least twice in `nums`, and `False` if every value is different.
Then say out loud two other ways to solve it and their costs.

Examples:
- `[4, 1, 7, 4]` -> `True`
- `[1, 2, 3]` -> `False`
- `[]` -> `False`""",
     stub="def contains_duplicate(nums):\n    pass",
     tests="""check(contains_duplicate, [
    ([1, 2, 3, 1], True),
    ([1, 2, 3, 4], False),
    ([1, 1, 1, 3, 3, 4, 3, 2, 4, 2], True),
    ([], False),
    ([7], False),
    ([4, 1, 7, 4], True),
    ([-1, 1], False),
])""",
     hint1="Signal: \"have I seen this value before?\" asked for every item. Pattern: **hashing** (a set).",
     hint2="""1. `seen = set()`.
2. For each `x`: if `x in seen`, return True; otherwise add it.
3. Return False after the loop.
(Short version: `len(set(nums)) < len(nums)`, but it cannot stop early.)""",
     solution='''def contains_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False''',
     why="A set lookup is O(1) on average, so one pass answers the question and stops at the first repeat. "
         "The alternatives: compare all pairs (O(n^2) time, O(1) space) or sort and compare neighbours "
         "(O(n log n) time, O(1) extra space if sorting in place). Mentioning this time/space trade-off is what "
         "the examiner wants.",
     complexity="O(n) time, O(n) space.",
     mistakes="Using a list for `seen` (each `in` becomes O(n), total O(n^2)). Sorting the caller's list in place "
              "without saying so.",
     learn=["algo-hashing"], source=("LeetCode 217", lc("contains-duplicate")))

ex.q("Find it fast in a sorted list", minutes=12, level="easy",
     prompt="""`nums` is sorted in increasing order and has no repeated values. Return the index of `target`, or `-1`
if it is not there. Your solution must run in O(log n) time.

Examples:
- `nums = [-1, 0, 3, 5, 9, 12], target = 9` -> `4`
- `nums = [-1, 0, 3, 5, 9, 12], target = 2` -> `-1`
- `nums = [5], target = 5` -> `0`""",
     stub="def search(nums, target):\n    pass",
     tests="""check(search, [
    (([-1, 0, 3, 5, 9, 12], 9), 4),
    (([-1, 0, 3, 5, 9, 12], 2), -1),
    (([5], 5), 0),
    (([5], -5), -1),
    (([], 3), -1),
    (([1, 3, 5, 7, 9, 11, 13], 1), 0),
    (([1, 3, 5, 7, 9, 11, 13], 13), 6),
])""",
     hint1="Signal: sorted input plus an O(log n) requirement. Pattern: **binary search**.",
     hint2="""1. `lo, hi = 0, len(nums) - 1` (an inclusive range).
2. While `lo <= hi`: `mid = (lo + hi) // 2`.
3. Equal: return `mid`. `nums[mid] < target`: `lo = mid + 1`. Otherwise: `hi = mid - 1`.
4. Return -1 when the range is empty.""",
     solution='''def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1''',
     why="Each comparison with the middle element throws away half of the remaining range, because the order "
         "tells you on which side the target must be. After about log2(n) steps the range is empty.",
     complexity="O(log n) time, O(1) space.",
     mistakes="`while lo < hi` with an inclusive range (misses a one-element range like `[5]`). `lo = mid` instead "
              "of `mid + 1` (infinite loop). In languages with fixed-size ints, `(lo + hi)` can overflow; write "
              "`lo + (hi - lo) // 2`.",
     learn=["algo-binary-search"], source=("LeetCode 704", lc("binary-search")))

ex.q("Palindrome with one delete allowed (bonus)", minutes=12, level="easy",
     prompt="""Optional. Return `True` if the lowercase string `s` is a palindrome, or can become one by deleting at
most one character.

Examples:
- `"abca"` -> `True` (delete `b` or `c`)
- `"abc"` -> `False`
- `"deeee"` -> `True` (delete `d`)""",
     stub="def valid_palindrome(s):\n    pass",
     tests="""check(valid_palindrome, [
    ("aba", True),
    ("abca", True),
    ("abc", False),
    ("deeee", True),
    ("a", True),
    ("cbbcc", True),
    ("eeccccbebaeeabebccceea", False),
])""",
     hint1="Signal: compare characters from both ends; at the first mismatch you get one chance to skip. "
           "Pattern: **two pointers**.",
     hint2="""1. Move `i` from the left and `j` from the right while `s[i] == s[j]`.
2. At the first mismatch, try both options: is `s[i+1 .. j]` a palindrome, or is `s[i .. j-1]`?
3. If either is, return True; else False. If no mismatch appears, return True.""",
     solution='''def valid_palindrome(s):
    def is_pal(i, j):
        while i < j:
            if s[i] != s[j]:
                return False
            i += 1
            j -= 1
        return True

    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return is_pal(i + 1, j) or is_pal(i, j - 1)
        i += 1
        j -= 1
    return True''',
     why="Before the first mismatch, all pairs already match, so the only useful delete is one of the two "
         "mismatching characters. Each branch is one more linear check, so the total stays O(n).",
     complexity="O(n) time, O(1) space.",
     mistakes="Trying only one of the two deletions (fails on `\"cbbcc\"`-like cases). Trying every possible "
              "deletion, which is O(n^2). Allowing a second skip inside the helper.",
     learn=["algo-two-pointers"], source=("LeetCode 680", lc("valid-palindrome-ii")))

ex.save()
