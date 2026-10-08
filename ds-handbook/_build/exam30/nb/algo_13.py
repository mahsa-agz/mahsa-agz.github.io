import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _algo_mid_common import BIG

ex = Exam(13, "algorithms")
ex.setup(BIG)

# ---------------------------------------------------------------- Q1 course schedule (topological sort)
ex.q("Can every course be finished?", minutes=18,
     prompt="""There are `num_courses` courses labelled `0` to `num_courses - 1`. Each pair `[a, b]` in `prereqs`
means "you must pass course `b` before course `a`". Return `True` if it is possible to finish all courses, `False`
otherwise.

Example: `num_courses = 3`, `prereqs = [[1, 0], [2, 1]]` gives `True` (take 0, then 1, then 2).
`num_courses = 3`, `prereqs = [[1, 0], [2, 1], [0, 2]]` gives `False`: 0 needs 2, 2 needs 1, 1 needs 0.

Constraints: up to 100,000 courses and 100,000 pairs. The larger test is a chain of 100,000 courses, so a recursive
solution may hit Python's recursion limit.""",
     stub="""def can_finish(num_courses, prereqs):
    pass""",
     tests="""check(can_finish, [
    ((3, [[1, 0], [2, 1]]), True),
    ((3, [[1, 0], [2, 1], [0, 2]]), False),
    ((1, []), True),                                  # no prerequisites
    ((1, [[0, 0]]), False),                           # a course that needs itself
    ((3, [[0, 1], [0, 2], [1, 2]]), True),            # two paths into course 0
    ((4, [[1, 0], [2, 1], [3, 2], [1, 3]]), False),   # cycle 1 -> 2 -> 3 -> 1 after a free start
    ((5, [[1, 0], [3, 2]]), True),                    # two separate groups plus a free course
    ((2, [[1, 0], [1, 0]]), True),                    # duplicate pair
])
# larger inputs: a chain of 100,000 courses, then the same chain with one edge closing a cycle
n = 100_000
chain = [[i + 1, i] for i in range(n - 1)]
check_big("chain of 100,000 courses", lambda: can_finish(n, chain), True)
check_big("same chain plus one back edge", lambda: can_finish(n, chain + [[0, n - 1]]), False)""",
     hint1="""Signal: tasks with "must happen before" rules; the question is whether an order exists, which is the
same as "does the directed graph have a cycle?". Pattern: **topological sort** (Kahn's algorithm: repeatedly take a
course with no remaining prerequisites).""",
     hint2="""1. Build an adjacency list `b -> [a, ...]` and an in-degree count for every course.
2. Put every course with in-degree 0 in a queue.
3. Pop a course, count it as taken, and lower the in-degree of each course that depends on it; push those that drop
   to 0.
4. All courses can be finished exactly when the taken count equals `num_courses`.""",
     solution="""from collections import deque

def can_finish(num_courses, prereqs):
    graph = [[] for _ in range(num_courses)]
    indegree = [0] * num_courses
    for a, b in prereqs:              # b must come before a
        graph[b].append(a)
        indegree[a] += 1
    queue = deque(c for c in range(num_courses) if indegree[c] == 0)
    taken = 0
    while queue:
        c = queue.popleft()
        taken += 1
        for nxt in graph[c]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return taken == num_courses       # courses on a cycle never reach in-degree 0""",
     why="""A course can be taken once all its prerequisites are taken, which is exactly "in-degree 0 in the remaining
graph". Courses on a cycle wait for each other forever, so their in-degree never reaches 0 and they are never taken.
Counting the taken courses detects that. Kahn's algorithm is iterative, so a 100,000-long chain is fine.

**Follow-ups (what if...):**
- *What if you must return an actual order (LeetCode 210)?* Append each popped course to a list; return it if its
  length is `num_courses`, else `[]`.
- *What if you want DFS instead?* Three colors (unvisited, in progress, done); finding an "in progress" node again
  means a cycle. Use an explicit stack or raise the recursion limit for deep graphs.
- *What if you want the minimum number of semesters when you can take any number of courses per semester?* Run Kahn
  level by level (like BFS levels); the number of levels is the answer.
- *What if prerequisites change over time (edges are added online)?* Recomputing is O(V + E) per change; incremental
  cycle detection exists but is rarely expected. In a data pipeline (DAG of jobs) this is exactly how schedulers such
  as Airflow check the graph.""",
     complexity="O(V + E) time and space (V courses, E pairs).",
     mistakes="Reversing the edge direction (it still detects cycles, but the order is wrong in the follow-up). "
              "Starting only from course 0 instead of all in-degree 0 courses. Recursive DFS without the "
              "\"in progress\" state, which cannot tell a cycle from a shared descendant. Recursion depth errors.",
     learn=["algo-topological-sort", "algo-graphs-bfs-dfs"],
     source=("LeetCode 207", "https://leetcode.com/problems/course-schedule/"))

# ---------------------------------------------------------------- Q2 longest repeating char replacement (sliding window)
ex.q("Longest block after a few edits", minutes=18,
     prompt="""You get an uppercase string `s` and an integer `k`. You may change at most `k` characters into any
other uppercase letter. Return the length of the longest substring that consists of one repeated letter after your
changes.

Example: `s = "BAAABAC"`, `k = 1` gives `5`: change the `B` at index 4 to `A` and `"AAAAA"` (indices 1 to 5) appears.
`s = "ABCD"`, `k = 0` gives `1`.

Constraints: up to 100,000 characters.""",
     stub="""def character_replacement(s, k):
    pass""",
     tests="""check(character_replacement, [
    (("BAAABAC", 1), 5),
    (("ABAB", 2), 4),
    (("AABABBA", 1), 4),
    (("A", 0), 1),                  # one character
    (("ABCD", 0), 1),               # no edits allowed
    (("AAAA", 2), 4),               # already uniform
    (("ABCDE", 1), 2),
    (("ABBB", 5), 4),               # k larger than the string
])
# larger input: "AB" repeated 50,000 times, k = 100 (best window has 101 of one letter and 100 of the other)
check_big("100,000 characters, k = 100", lambda: character_replacement("AB" * 50_000, 100), 201)""",
     hint1="""Signal: "longest substring such that ..." with a condition you can check from counts inside the window:
`window_length - count_of_most_common_letter <= k`. Pattern: **sliding window** (grow right, shrink left when the
window becomes invalid).""",
     hint2="""1. Keep letter counts for the window `s[left..right]` and `best_count`, the highest count of one letter
seen in any window so far.
2. Extend `right` by one and update the counts and `best_count`.
3. If `window_length - best_count > k`, move `left` one step (decrease its count).
4. The answer is the largest window length seen (it equals the final window length, because the window never
   shrinks by more than one step).""",
     solution="""from collections import Counter

def character_replacement(s, k):
    counts = Counter()
    left = best_count = answer = 0
    for right, ch in enumerate(s):
        counts[ch] += 1
        best_count = max(best_count, counts[ch])
        while (right - left + 1) - best_count > k:   # more than k letters would need changing
            counts[s[left]] -= 1
            left += 1
        answer = max(answer, right - left + 1)
    return answer""",
     why="""A window can be made uniform when the letters that are not the most common one number at most k. The
window grows to the right and only shrinks when that rule breaks, so each index enters and leaves once. A subtle
point: `best_count` is not lowered when the left side moves. That is safe, because the answer can only improve when a
window with a higher `best_count` appears, so a stale (too high) value never produces a too-large answer that was
not achieved earlier.

**Follow-ups (what if...):**
- *What if the alphabet is all of Unicode?* Counts in a hash map still work; the trick with `best_count` avoids
  scanning the whole map at each step.
- *What if the string is binary and you may flip at most k zeros (LeetCode 1004)?* The same window with "number of
  zeros in the window <= k".
- *What if you must return the substring itself, not the length?* Remember `left` and `right` whenever `answer`
  improves.
- *What if you must recompute the true maximum count when shrinking?* That costs O(26) per step: still O(26n), fine
  for uppercase letters, and easier to explain if the stale-max trick feels risky.""",
     complexity="O(n) time, O(1) space (at most 26 counts).",
     mistakes="Checking every substring (O(n^2) or worse). Using `max(counts.values())` each step and believing it is "
              "required (it is correct but O(26n)). Forgetting that the changed letters are `length - max_count`, "
              "not `length - k`.",
     learn=["algo-sliding-window", "algo-hashing"],
     source=("LeetCode 424", "https://leetcode.com/problems/longest-repeating-character-replacement/"))

# ---------------------------------------------------------------- Q3 house robber (dp 1d)
ex.q("Best total with no two neighbours", minutes=15,
     prompt="""Houses stand in a row and `nums[i]` is the cash in house `i`. You may pick any set of houses, but never
two **adjacent** houses. Return the maximum total cash. An empty street gives `0`.

Example: `nums = [6, 1, 2, 7]` gives `13` (houses 0 and 3). `nums = [2, 7, 9, 3, 1]` gives `12` (2 + 9 + 1).

Constraints: up to 100,000 houses, values from 0 to 400. The larger test has 100,000 houses, so an exponential search
or a deep recursion will fail.""",
     stub="""def rob(nums):
    pass""",
     tests="""check(rob, [
    ([6, 1, 2, 7], 13),
    ([2, 7, 9, 3, 1], 12),
    ([1, 2, 3, 1], 4),
    ([5], 5),                    # one house
    ([], 0),                     # no houses
    ([2, 1], 2),                 # two houses: take the larger
    ([2, 1, 1, 2], 4),           # skip two in a row
    ([0, 0, 0], 0),
])
# larger input: 100,000 houses alternating 1 and 100
check_big("100,000 houses", lambda: rob([1, 100] * 50_000), 5_000_000)""",
     hint1="""Signal: maximise a total with a "you cannot take both neighbours" rule; each choice only depends on the
previous one or two choices. Pattern: **1-D dynamic programming**: `best[i] = max(best[i - 1], best[i - 2] + nums[i])`.""",
     hint2="""1. Define `best[i]` = the best total using houses `0..i`.
2. For house `i` you either skip it (`best[i - 1]`) or take it (`best[i - 2] + nums[i]`).
3. You only need the last two values, so keep two variables `prev2, prev1` and roll them forward.""",
     solution="""def rob(nums):
    prev2 = prev1 = 0              # best total up to house i-2 and i-1
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1""",
     why="""The best plan for the first i houses either ignores house i (then it is the best plan for i - 1 houses) or
uses it (then house i - 1 is excluded, so it is the best plan for i - 2 houses plus `nums[i]`). Those two cases cover
everything, so the recurrence is correct, and it needs only the last two answers. Plain recursion would recompute the
same subproblems an exponential number of times; memoised recursion is O(n) but 100,000 levels deep.

**Follow-ups (what if...):**
- *What if the houses are in a circle (LeetCode 213)?* The first and last are neighbours: answer =
  `max(rob(nums[1:]), rob(nums[:-1]))`.
- *What if you must return which houses to take?* Keep the full `best` array and walk back from the end: if
  `best[i] == best[i - 1]` house i was skipped, else it was taken (jump to i - 2).
- *What if the houses form a tree (LeetCode 337)?* Return two values per node (best with the node taken, best with it
  skipped) from a post-order DFS.
- *What if values can be negative?* The recurrence still works (you can always skip), because `max` never forces you
  to take a house.""",
     complexity="O(n) time, O(1) space.",
     mistakes="Greedy choices such as \"take all even indices or all odd indices\" (fails on [2, 1, 1, 2]). Plain "
              "recursion without memo (exponential). Index errors for 0 or 1 houses.",
     learn=["algo-dp-1d"],
     source=("LeetCode 198", "https://leetcode.com/problems/house-robber/"))

ex.save()
