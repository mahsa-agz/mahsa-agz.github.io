"""Day 1 algorithms (easy): Valid Parentheses, Two Sum, Valid Palindrome + bonus Longest Common Prefix."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from algo_common import lc

ex = Exam(1, "algorithms")
ex.setup()

ex.q("Do the brackets close?", minutes=15, level="easy",
     prompt="""You get a string that contains only the characters `( ) [ ] { }`. Return `True` if every opening
bracket is closed by the same type of bracket, and in the right order (the bracket opened last must close first).
Otherwise return `False`.

Examples:
- `"{[]}"` -> `True`
- `"()[]{}"` -> `True`
- `"([)]"` -> `False` (the `[` is still open when `)` arrives)
- `"(("` -> `False` (nothing closes them)""",
     stub="def is_valid(s):\n    pass",
     tests="""check(is_valid, [
    ("()", True),
    ("()[]{}", True),
    ("(]", False),
    ("([)]", False),
    ("{[]}", True),
    ("", True),
    ("((", False),
    ("))", False),
])""",
     hint1="Signal: the most recent unclosed item must be matched first (last in, first out). Pattern: **stack**.",
     hint2="""1. Map each closing bracket to its opening partner: `{')': '(', ...}`.
2. Walk the string. Opening bracket: push it.
3. Closing bracket: the stack must be non-empty and its top must be the partner; pop it. Otherwise return False.
4. At the end the stack must be empty.""",
     solution='''def is_valid(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:                       # closing bracket
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:                                 # opening bracket
            stack.append(ch)
    return not stack                          # leftovers are unclosed''',
     why="A closing bracket can only match the latest opening bracket that is still open. A stack keeps exactly "
         "that order: its top is always the bracket that must close next.",
     complexity="O(n) time, O(n) space (all openings in the worst case).",
     mistakes="Forgetting the final `return not stack` (fails on `\"((\"`). Popping from an empty stack on `\")\"`. "
              "Only counting brackets, which accepts `\"([)]\"`.",
     learn=["algo-stack"], source=("LeetCode 20", lc("valid-parentheses")))

ex.q("Pair that hits the target", minutes=15, level="easy",
     prompt="""Given a list of integers `nums` and an integer `target`, return the indexes `[i, j]` (with `i < j`) of
the two numbers that add up to `target`. Exactly one such pair exists, and you may not use the same position twice.
Aim for better than checking every pair.

Examples:
- `nums = [1, 5, 9, 14], target = 23` -> `[2, 3]` (9 + 14)
- `nums = [3, 3], target = 6` -> `[0, 1]`
- `nums = [3, 2, 4], target = 6` -> `[1, 2]` (not `[0, 0]`: one 3 cannot be used twice)""",
     stub="def two_sum(nums, target):\n    pass",
     tests="""check(two_sum, [
    (([2, 7, 11, 15], 9), [0, 1]),
    (([3, 2, 4], 6), [1, 2]),
    (([3, 3], 6), [0, 1]),
    (([-1, -2, -3, -4, -5], -8), [2, 4]),
    (([0, 4, 3, 0], 0), [0, 3]),
    (([1, 5, 9, 14], 23), [2, 3]),
])""",
     hint1="Signal: for each number you need to know at once whether its partner `target - x` appeared before. "
           "Pattern: **hashing** (a dict from value to index).",
     hint2="""1. Keep `seen = {}` mapping value -> index.
2. For each index `i` and value `x`: compute `need = target - x`.
3. If `need` is in `seen`, return `[seen[need], i]`.
4. Only then store `seen[x] = i` (look first, then add, so x never pairs with itself).""",
     solution='''def two_sum(nums, target):
    seen = {}                                 # value -> index
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    return []                                 # not reached when a pair is guaranteed''',
     why="Brute force tries all pairs in O(n^2). The dict answers \"have I seen the partner?\" in O(1) on average, "
         "so one pass is enough. Checking before inserting handles duplicates like `[3, 3]` and stops a number "
         "from pairing with itself.",
     complexity="O(n) time, O(n) space.",
     mistakes="Inserting before checking (returns `[0, 0]` for `[3, 2, 4], 6`). Sorting first, which loses the "
              "original indexes. Returning the values instead of the indexes.",
     learn=["algo-hashing"], source=("LeetCode 1", lc("two-sum")))

ex.q("Same forwards and backwards", minutes=15, level="easy",
     prompt="""A sentence counts as a palindrome if, after you lowercase it and drop everything that is not a letter
or a digit, it reads the same from both ends. Return `True` or `False`. Try to use O(1) extra space (no cleaned copy
of the string).

Examples:
- `"No 'x' in Nixon"` -> `True` (cleaned: `noxinnixon`)
- `"race a car"` -> `False` (cleaned: `raceacar`)
- `" "` -> `True` (cleaned string is empty)
- `"0P"` -> `False` (digits count as characters)""",
     stub="def is_palindrome(s):\n    pass",
     tests="""check(is_palindrome, [
    ("A man, a plan, a canal: Panama", True),
    ("race a car", False),
    (" ", True),
    ("0P", False),
    ("ab_a", True),
    ("No 'x' in Nixon", True),
    ("Was it a car or a cat I saw?", True),
])""",
     hint1="Signal: compare the two ends and move inward. Pattern: **two pointers** (one at each end).",
     hint2="""1. `i = 0`, `j = len(s) - 1`.
2. While `i < j`: move `i` right while `s[i]` is not alphanumeric; move `j` left the same way.
3. Compare `s[i].lower()` with `s[j].lower()`; if different return False.
4. Step both pointers inward. Return True at the end.""",
     solution='''def is_palindrome(s):
    i, j = 0, len(s) - 1
    while i < j:
        if not s[i].isalnum():
            i += 1
        elif not s[j].isalnum():
            j -= 1
        elif s[i].lower() != s[j].lower():
            return False
        else:
            i += 1
            j -= 1
    return True''',
     why="A palindrome mirrors around its centre, so each character only needs to be compared with its mirror "
         "partner. Two pointers do that in one pass and skip the junk characters in place, without building a "
         "cleaned copy. (The one-liner `t == t[::-1]` on a cleaned `t` is also fine to mention: O(n) space.)",
     complexity="O(n) time, O(1) extra space.",
     mistakes="Treating `_` as a letter (`isalnum` is False for it). Forgetting digits. Skipping a junk character "
              "and comparing in the same step without re-checking `i < j`.",
     learn=["algo-two-pointers"], source=("LeetCode 125", lc("valid-palindrome")))

ex.q("Shared start of words (bonus)", minutes=10, level="easy",
     prompt="""Optional. Given a list of words, return the longest string that every word starts with. Return `""`
if they share nothing.

Examples:
- `["interact", "internet", "interval"]` -> `"inter"`
- `["dog", "racecar", "car"]` -> `""`
- `["ab", "a"]` -> `"a"` (the prefix can never be longer than the shortest word)""",
     stub="def longest_common_prefix(words):\n    pass",
     tests="""check(longest_common_prefix, [
    (["flower", "flow", "flight"], "fl"),
    (["dog", "racecar", "car"], ""),
    (["alone"], "alone"),
    (["", "b"], ""),
    (["interact", "internet", "interval"], "inter"),
    (["ab", "a"], "a"),
])""",
     hint1="Signal: compare the words column by column (character position by position). Pattern: **string "
           "scanning** (arrays and strings).",
     hint2="""1. Take the first word as the candidate.
2. For each position `i` of the candidate, check every other word: if the word is too short or its `i`-th
   character differs, return `candidate[:i]`.
3. If no column fails, the whole first word is the prefix.""",
     solution='''def longest_common_prefix(words):
    if not words:
        return ""
    first = words[0]
    for i, ch in enumerate(first):
        for w in words[1:]:
            if i == len(w) or w[i] != ch:
                return first[:i]
    return first''',
     why="The prefix ends at the first column where any word disagrees or runs out. Scanning column by column "
         "stops as early as possible. An alternative: sort the words and compare only the first and last.",
     complexity="O(S) time where S is the total number of characters, O(1) extra space.",
     mistakes="Index error when a later word is shorter than the first. Returning the shortest word without "
              "checking the characters.",
     learn=["algo-arrays-strings"], source=("LeetCode 14", lc("longest-common-prefix")))

ex.save()
