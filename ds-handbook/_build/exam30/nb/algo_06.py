"""Day 6 algorithms (easy): Flood Fill, Search Insert Position, First Unique Character + bonus Palindrome Number."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from algo_common import lc

ex = Exam(6, "algorithms")
ex.setup()

ex.q("Paint bucket", minutes=15, level="easy",
     prompt="""`image` is a grid of integers (colours). Starting at cell `(sr, sc)`, repaint that cell and every cell
connected to it through up/down/left/right neighbours **of the same original colour** with `color`. Return the
grid. Diagonal cells are not connected.

Example:
```
image = [[1, 1, 1],        sr = 1, sc = 1, color = 2     result: [[2, 2, 2],
         [1, 1, 0],                                                [2, 2, 0],
         [1, 0, 1]]                                                [2, 0, 1]]
```
The bottom-right `1` stays: it only touches the start region diagonally.""",
     stub="def flood_fill(image, sr, sc, color):\n    pass",
     tests="""check(flood_fill, [
    (([[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2), [[2, 2, 2], [2, 2, 0], [2, 0, 1]]),
    (([[0, 0, 0], [0, 0, 0]], 0, 0, 0), [[0, 0, 0], [0, 0, 0]]),
    (([[5]], 0, 0, 9), [[9]]),
    (([[1, 0], [0, 1]], 0, 0, 3), [[3, 0], [0, 1]]),
    (([[0, 0, 0], [0, 1, 1]], 1, 1, 1), [[0, 0, 0], [0, 1, 1]]),
    (([[2, 2, 3], [3, 2, 3], [2, 2, 2]], 2, 0, 7), [[7, 7, 3], [3, 7, 3], [7, 7, 7]]),
])""",
     hint1="Signal: spread from a cell to its matching neighbours on a grid. Pattern: **graph traversal on a grid "
           "(DFS or BFS)**.",
     hint2="""1. `old = image[sr][sc]`. If `old == color`, return the image unchanged (otherwise you loop forever).
2. Push `(sr, sc)` on a stack. Pop a cell; if it is inside the grid and has colour `old`, paint it and push its 4
   neighbours.
3. Return the image.""",
     solution='''def flood_fill(image, sr, sc, color):
    old = image[sr][sc]
    if old == color:
        return image
    rows, cols = len(image), len(image[0])
    stack = [(sr, sc)]
    while stack:
        r, c = stack.pop()
        if 0 <= r < rows and 0 <= c < cols and image[r][c] == old:
            image[r][c] = color                    # painting also marks it visited
            stack += [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]
    return image''',
     why="The grid is a graph: cells are nodes, same-colour neighbours are edges. DFS from the start visits the "
         "whole connected region once. Repainting a cell doubles as the \"visited\" mark, so no extra set is "
         "needed, which is exactly why the `old == color` case must return early.",
     complexity="O(rows * cols) time and space in the worst case (the stack).",
     mistakes="Missing the `old == color` early return (infinite loop). Checking bounds after indexing. Including "
              "diagonal neighbours. Deep recursion on a big grid can hit Python's recursion limit; the explicit "
              "stack avoids it.",
     learn=["algo-graphs-bfs-dfs"], source=("LeetCode 733", lc("flood-fill")))

ex.q("Where would it go?", minutes=12, level="easy",
     prompt="""`nums` is sorted in increasing order with distinct values. Return the index of `target` if it is present;
otherwise return the index where it would be inserted to keep the list sorted. Required: O(log n).

Examples:
- `nums = [1, 3, 5, 6], target = 5` -> `2`
- `nums = [1, 3, 5, 6], target = 2` -> `1`
- `nums = [1, 3, 5, 6], target = 7` -> `4` (after the last element)""",
     stub="def search_insert(nums, target):\n    pass",
     tests="""check(search_insert, [
    (([1, 3, 5, 6], 5), 2),
    (([1, 3, 5, 6], 2), 1),
    (([1, 3, 5, 6], 7), 4),
    (([1, 3, 5, 6], 0), 0),
    (([1], 1), 0),
    (([1, 3], 2), 1),
    (([], 4), 0),
])""",
     hint1="Signal: sorted input, O(log n), and the answer is a position (the first index with value >= target). "
           "Pattern: **binary search (lower bound)**.",
     hint2="""1. Half-open range: `lo, hi = 0, len(nums)`.
2. While `lo < hi`: `mid = (lo + hi) // 2`. If `nums[mid] < target`: `lo = mid + 1`, else `hi = mid`.
3. Return `lo`: the first index whose value is >= target (it is `len(nums)` if none is).""",
     solution='''def search_insert(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

# the standard library does exactly this:
import bisect
print(bisect.bisect_left([1, 3, 5, 6], 2))   # 1''',
     why="\"First index with value >= target\" is a yes/no question that is False then True along the sorted "
         "list, so binary search can find the boundary. The same template answers found and not found in one "
         "go. Knowing `bisect_left` is a plus in exams; still be ready to write the loop.",
     complexity="O(log n) time, O(1) space.",
     mistakes="Starting `hi` at `len(nums) - 1`, which can never return `len(nums)` (fails for target 7). "
              "Mixing the inclusive and half-open templates (`hi = mid - 1` with `lo < hi`).",
     learn=["algo-binary-search"], source=("LeetCode 35", lc("search-insert-position")))

ex.q("First letter that appears once", minutes=10, level="easy",
     prompt="""Return the index of the first character in `s` that occurs exactly once in the whole string, or `-1` if
every character repeats.

Examples:
- `"leetcode"` -> `0` (`l`)
- `"loveleetcode"` -> `2` (`v`)
- `"aabb"` -> `-1`""",
     stub="def first_uniq_char(s):\n    pass",
     tests="""check(first_uniq_char, [
    ("leetcode", 0),
    ("loveleetcode", 2),
    ("aabb", -1),
    ("z", 0),
    ("", -1),
    ("dddccdbba", 8),
])""",
     hint1="Signal: you need the total count of each character before you can judge the first one. Pattern: "
           "**hashing** (count, then a second pass).",
     hint2="""1. Count every character: `Counter(s)`.
2. Walk `s` again with indexes; return the first index whose count is 1.
3. Return -1 if none.""",
     solution='''from collections import Counter

def first_uniq_char(s):
    count = Counter(s)
    for i, ch in enumerate(s):
        if count[ch] == 1:
            return i
    return -1''',
     why="Whether a character is unique depends on the whole string, so one pass to count is needed first. The "
         "second pass keeps the original order, so the first hit is the answer. Two O(n) passes are still O(n).",
     complexity="O(n) time, O(k) space with k distinct characters (O(1) for 26 letters).",
     mistakes="Returning the character instead of the index. Using `s.count(ch)` inside the loop (O(n^2)). "
              "Walking the dict instead of the string (dict order is first-insertion order, which happens to work "
              "in Python 3.7+, but say why if you rely on it).",
     learn=["algo-hashing"], source=("LeetCode 387", lc("first-unique-character-in-a-string")))

ex.q("Number that reads the same both ways (bonus)", minutes=10, level="easy",
     prompt="""Optional. Return `True` if the integer `x` reads the same left to right and right to left. Do it without
converting the number to a string.

Examples:
- `121` -> `True`
- `-121` -> `False` (reads `121-` backwards)
- `10` -> `False` (reads `01`)""",
     stub="def is_palindrome_number(x):\n    pass",
     tests="""check(is_palindrome_number, [
    (121, True),
    (-121, False),
    (10, False),
    (0, True),
    (7, True),
    (12321, True),
    (1000021, False),
    (1221, True),
])""",
     hint1="Signal: digits can be peeled off with `% 10` and `// 10`. Pattern: **digit math** (reverse half of the "
           "number), from the arrays and strings toolkit.",
     hint2="""1. Negative numbers, and numbers that end in 0 (except 0 itself), are never palindromes.
2. Build `rev` from the last digits: `rev = rev * 10 + x % 10`, `x //= 10`, while `x > rev`.
3. Even digit count: `x == rev`. Odd digit count: `x == rev // 10` (drop the middle digit).""",
     solution='''def is_palindrome_number(x):
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    rev = 0
    while x > rev:
        rev = rev * 10 + x % 10
        x //= 10
    return x == rev or x == rev // 10''',
     why="Reversing only half of the digits avoids building the full reversed number (which can overflow in "
         "fixed-size integer languages) and stops early. When `x <= rev`, you have reached the middle.",
     complexity="O(d) time where d is the number of digits (that is O(log x)), O(1) space.",
     mistakes="Forgetting the trailing-zero case (`10` would wrongly pass the half check). Treating negative "
              "numbers as palindromes. Using `str(x)` when the examiner asked not to.",
     learn=["algo-arrays-strings"], source=("LeetCode 9", lc("palindrome-number")))

ex.save()
