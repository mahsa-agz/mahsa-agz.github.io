import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _algo_mid_common import BIG

ex = Exam(18, "algorithms")
ex.setup(BIG)

# ---------------------------------------------------------------- Q1 LIS (dp 1d)
ex.q("Longest rising selection", minutes=18,
     prompt="""Given a list of integers, return the length of the longest **strictly increasing subsequence**. A
subsequence keeps the original order but may skip elements (it does not have to be contiguous).

Example: `nums = [3, 10, 2, 1, 20, 4, 6, 7]` gives `4`: for example `[2, 4, 6, 7]` or `[1, 4, 6, 7]`.
`[7, 7, 7]` gives `1` (equal values do not count as increasing).

Constraints: up to 2,500 numbers. O(n^2) is accepted; O(n log n) is the strong answer and the usual follow-up.""",
     stub="""def length_of_lis(nums):
    pass""",
     tests="""check(length_of_lis, [
    ([3, 10, 2, 1, 20, 4, 6, 7], 4),
    ([10, 9, 2, 5, 3, 7, 101, 18], 4),
    ([0, 1, 0, 3, 2, 3], 4),
    ([7, 7, 7], 1),                     # strictly increasing: duplicates do not chain
    ([5], 1),                           # one element
    ([], 0),                            # empty
    ([5, 4, 3, 2, 1], 1),               # decreasing
    ([4, 10, 4, 3, 8, 9], 3),
])
# larger input: 1500..2999 followed by 0..1499 (3,000 numbers, answer 1,500)
check_big("3,000 numbers", lambda: length_of_lis(list(range(1_500, 3_000)) + list(range(1_500))), 1_500, limit=5.0)""",
     hint1="""Signal: "longest subsequence with an order condition": the best answer ending at position i is built from
best answers ending earlier. Pattern: **1-D dynamic programming** (`dp[i] = 1 + max(dp[j])` for `j < i` with
`nums[j] < nums[i]`). Faster: patience sorting with binary search.""",
     hint2="""O(n^2): `dp[i]` = length of the longest increasing subsequence that **ends at i**. Start each at 1. For each
`i`, look at every `j < i` with `nums[j] < nums[i]` and set `dp[i] = max(dp[i], dp[j] + 1)`. Answer: `max(dp)`.

O(n log n): keep `tails`, where `tails[L]` is the smallest possible last value of an increasing subsequence of length
`L + 1`. For each `x`, find with `bisect_left` the first tail `>= x` and replace it with `x` (or append `x` if none).
The answer is `len(tails)`.""",
     solution="""from bisect import bisect_left

def length_of_lis(nums):
    tails = []                        # tails[L] = smallest tail of an increasing subsequence of length L + 1
    for x in nums:
        i = bisect_left(tails, x)     # first tail >= x (bisect_left keeps it STRICTLY increasing)
        if i == len(tails):
            tails.append(x)           # x extends the longest subsequence so far
        else:
            tails[i] = x              # x is a better (smaller) tail for length i + 1
    return len(tails)

# O(n^2) DP, the version to write first in an exam
def length_of_lis_dp(nums):
    if not nums:
        return 0
    dp = [1] * len(nums)              # dp[i] = longest increasing subsequence ending at i
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)""",
     why="""In the O(n^2) DP, any increasing subsequence ending at i has some previous element j, and the best one
through j is `dp[j]`, so trying all j is enough. The O(n log n) version keeps, for each length, the smallest possible
tail; a smaller tail is never worse because it leaves more room to extend. `tails` is always sorted, so binary search
finds where `x` belongs. Note: `tails` is not itself a valid subsequence, only its length is meaningful.

**Follow-ups (what if...):**
- *What if you must return the subsequence itself?* In the DP, store `parent[i] = j` when `dp[i]` improves and walk
  back from the argmax. In the fast version, store the index of each tail and a parent per element.
- *What if "non-decreasing" is allowed (equal values chain)?* Use `bisect_right` instead of `bisect_left`.
- *What if you need the number of longest increasing subsequences (LeetCode 673)?* Extend the O(n^2) DP with a count
  array next to `dp`.
- *What if the elements are pairs (envelopes that must fit inside each other, LeetCode 354)?* Sort by width ascending
  and height descending, then run LIS on heights.
- *Data-science angle:* the longest run of improving metrics over time, or the longest chain of user upgrades, are LIS
  in disguise.""",
     complexity="O(n log n) time and O(n) space with binary search; O(n^2) time and O(n) space for the plain DP.",
     mistakes="Treating it as a contiguous subarray. Using `bisect_right` (allows equal values). Returning `dp[-1]` "
              "instead of `max(dp)` (the best subsequence need not end at the last element). Thinking `tails` is the "
              "actual subsequence.",
     learn=["algo-dp-1d", "algo-binary-search"],
     source=("LeetCode 300", "https://leetcode.com/problems/longest-increasing-subsequence/"))

# ---------------------------------------------------------------- Q2 number of provinces (union-find)
ex.q("How many friend groups?", minutes=15,
     prompt="""There are `n` people. You get an `n x n` matrix `is_connected` where `is_connected[i][j] == 1` means
person `i` and person `j` know each other directly (the matrix is symmetric and the diagonal is 1). Knowing is
transitive for groups: if A knows B and B knows C, all three are in one group. Return the number of groups.

Example:
```
[[1, 1, 0, 0],
 [1, 1, 0, 0],
 [0, 0, 1, 1],
 [0, 0, 1, 1]]
```
gives `2` (people 0 and 1 form one group, 2 and 3 another).

Constraints: `n` up to 1,000. In the larger test the groups are long chains, so a recursive DFS can go 1,000 levels
deep.""",
     stub="""def find_circle_num(is_connected):
    pass""",
     tests="""def chain_matrix(n, step):
    # person i knows person i + step: gives `step` long chains
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        m[i][i] = 1
        if i + step < n:
            m[i][i + step] = m[i + step][i] = 1
    return m

check(find_circle_num, [
    ([[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]], 2),
    ([[1, 1, 0], [1, 1, 0], [0, 0, 1]], 2),
    ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 3),          # nobody knows anybody
    ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], 1),          # everybody knows everybody
    ([[1]], 1),                                       # one person
    ([[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 1], [1, 0, 1, 1]], 1),   # connected only through a chain 0-3-2-1
    (chain_matrix(6, 2), 2),                          # 0-2-4 and 1-3-5
])
# larger inputs: 1,000 people in one chain, and in three interleaved chains
big1, big3 = chain_matrix(1_000, 1), chain_matrix(1_000, 3)
check_big("1,000 people, one chain", lambda: find_circle_num(big1), 1)
check_big("1,000 people, three chains", lambda: find_circle_num(big3), 3)""",
     hint1="""Signal: count **connected components** of an undirected graph, where the groups merge as you read
connections. Pattern: **union-find** (disjoint set union with path compression). An iterative DFS/BFS also works.""",
     hint2="""1. `parent = list(range(n))`; `find(x)` follows parents to the root (compress the path on the way).
2. For every pair `i < j` with `is_connected[i][j] == 1`: find both roots; if they differ, set one root's parent to
   the other and decrease the group count (start at `n`).
3. Return the count.""",
     solution="""def find_circle_num(is_connected):
    n = len(is_connected)
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]    # path halving: points x closer to the root
            x = parent[x]
        return x

    groups = n
    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j]:
                ri, rj = find(i), find(j)
                if ri != rj:                 # two different groups merge into one
                    if rank[ri] < rank[rj]:
                        ri, rj = rj, ri
                    parent[rj] = ri          # attach the shorter tree under the taller one
                    rank[ri] += rank[ri] == rank[rj]
                    groups -= 1
    return groups""",
     why="""Every successful union merges two groups, so the number of groups is `n` minus the number of successful
unions. Path compression plus union by rank keep the trees almost flat, so each `find` is close to O(1) (inverse
Ackermann). The loop over the matrix is O(n^2), which is the input size anyway. The `find` is iterative, so long
chains do not hit any recursion limit.

**Follow-ups (what if...):**
- *What if the input is an edge list instead of a matrix?* Same union-find over the edges: O(E alpha(n)), much better
  for sparse graphs.
- *What if edges arrive over time and you must report the group count after each one (online)?* Union-find shines
  here: each new edge is one union, while DFS would have to rerun.
- *What if edges can also be deleted?* Plain union-find cannot undo merges; process offline in reverse (deletions
  become additions) or use more advanced dynamic connectivity.
- *What if you want the size of the largest group?* Keep `size[root]` and update it on each union.
- *Data angle:* entity resolution (merging user accounts that share a device or email) is union-find at scale; in
  Spark it is the connected-components algorithm in GraphFrames.""",
     complexity="O(n^2 x alpha(n)) time (alpha is the inverse Ackermann function, effectively constant), O(n) space.",
     mistakes="Counting ones in the matrix instead of groups. Forgetting path compression (chains make `find` O(n)). "
              "A recursive DFS on a 1,000-long chain (Python's default recursion limit is 1,000). Not checking "
              "`ri != rj` before decreasing the count.",
     learn=["algo-union-find", "algo-graphs-bfs-dfs"],
     source=("LeetCode 547", "https://leetcode.com/problems/number-of-provinces/"))

# ---------------------------------------------------------------- Q3 combination sum (backtracking)
ex.q("All ways to hit a total with reusable numbers", minutes=18,
     prompt="""Given a list of **distinct positive** integers `candidates` and a `target`, return every unique
combination of candidates that sums to `target`. Each candidate may be used **any number of times**. Two combinations
are the same if they use the same numbers the same number of times (order does not matter). Return them in any order.

Example: `candidates = [3, 4, 5]`, `target = 8` gives `[[3, 5], [4, 4]]`.
`candidates = [2, 3, 6, 7]`, `target = 7` gives `[[2, 2, 3], [7]]`.

Constraints: up to 30 candidates, values from 2 to 40, target up to 40.""",
     stub="""def combination_sum(candidates, target):
    pass""",
     tests="""check(combination_sum, [
    (([3, 4, 5], 8), [[3, 5], [4, 4]]),
    (([2, 3, 6, 7], 7), [[2, 2, 3], [7]]),
    (([2, 3, 5], 8), [[2, 2, 2, 2], [2, 3, 3], [3, 5]]),
    (([2], 1), []),                          # impossible
    (([1], 2), [[1, 1]]),                    # same number reused
    (([7, 3, 2], 7), [[2, 2, 3], [7]]),      # unsorted input
    (([5, 10], 3), []),                      # every candidate is too big
], key=any_order)
# larger input: candidates [2, 3, 5, 7], target 40 has 90 combinations; checks count and that none repeats
def count_unique(result):
    return len(result), len({tuple(sorted(c)) for c in result}), all(sum(c) == 40 for c in result)
check_big("target 40, 90 combinations", lambda: count_unique(combination_sum([2, 3, 5, 7], 40)), (90, 90, True))""",
     hint1="""Signal: "return **all** combinations" that satisfy a sum, with reuse allowed: you must enumerate, and you
can prune a branch as soon as the running sum is too big. Pattern: **backtracking** with a start index (to avoid
permutations of the same combination).""",
     hint2="""1. Sort the candidates (lets you stop the loop early).
2. `dfs(start, remaining)`: if `remaining == 0`, record a copy of `path`.
3. For `i` from `start` to the end: if `candidates[i] > remaining`, break (sorted). Otherwise append it, call
   `dfs(i, remaining - candidates[i])` (pass `i`, not `i + 1`, because reuse is allowed), then pop.""",
     solution="""def combination_sum(candidates, target):
    candidates = sorted(candidates)
    out, path = [], []

    def dfs(start, remaining):
        if remaining == 0:
            out.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:          # sorted: every later candidate is too big as well
                break
            path.append(c)
            dfs(i, remaining - c)      # i, not i + 1: the same number may be used again
            path.pop()

    dfs(0, target)
    return out""",
     why="""Starting each loop at `start` makes every combination appear in non-decreasing index order, so `[2, 3]` and
`[3, 2]` cannot both be produced. Passing `i` (not `i + 1`) allows reuse. Sorting allows `break` instead of
`continue`, which prunes whole branches. Recursion depth is at most `target / min(candidates)`, which is small here.

**Follow-ups (what if...):**
- *What if each candidate may be used once and the list has duplicates (LeetCode 40)?* Recurse with `i + 1` and skip
  `candidates[i] == candidates[i - 1]` when `i > start`.
- *What if you only need the number of combinations, not the list?* Use DP (coin change II):
  `ways[a] += ways[a - c]`, loop coins outside. Much faster when the count is huge.
- *What if the target is large (1,000) and the output would be enormous?* Say so: listing is output-bound
  (exponential); ask whether a count or one example is enough.
- *What if negative numbers were allowed?* Then reuse can loop forever (`+1, -1, +1, ...`); you need a bound on the
  length, so clarify the constraints first.""",
     complexity="Exponential in general: roughly O(N^(T/M + 1)) time for N candidates, target T and smallest value M; "
                "O(T/M) recursion depth.",
     mistakes="Starting the loop at 0 (creates permutations as duplicates). Passing `i + 1` (forbids reuse). Appending "
              "`path` instead of `path[:]`. Not pruning, which explores many dead branches.",
     learn=["algo-backtracking"],
     source=("LeetCode 39", "https://leetcode.com/problems/combination-sum/"))

ex.save()
