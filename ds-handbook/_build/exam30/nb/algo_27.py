"""Day 27 algorithms (hard): Partition Equal Subset Sum, Sliding Window Maximum, Cheapest Flights Within K Stops."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from _algo_hard_common import BIG, lc, compute

ex = Exam(27, "algorithms")
ex.setup(BIG)

# ---------------------------------------------------------------- Q1 Partition Equal Subset Sum (416)
SOL1 = '''def can_split_brute(nums):
    """Try every subset (take or skip each number). O(2^n)."""
    total = sum(nums)
    if total % 2:
        return False
    def go(i, left):
        if left == 0:
            return True
        if i == len(nums) or left < 0:
            return False
        return go(i + 1, left - nums[i]) or go(i + 1, left)
    return go(0, total // 2)

def can_split(nums):
    """0/1 knapsack on reachable sums: reach[s] is True if some subset of the numbers seen so far sums to s."""
    total = sum(nums)
    if total % 2:
        return False                                  # an odd total can never be split evenly
    target = total // 2
    reach = [True] + [False] * target
    for x in nums:
        for s in range(target, x - 1, -1):            # go DOWN so each number is used at most once
            if reach[s - x]:
                reach[s] = True
        if reach[target]:
            return True
    return reach[target]

def can_split_bits(nums):
    """Same DP with one big integer as a bitset: bit s is set if sum s is reachable."""
    total = sum(nums)
    if total % 2:
        return False
    bits = 1
    for x in nums:
        bits |= bits << x
    return bool(bits >> (total // 2) & 1)

rng = random.Random(416)
for _ in range(2000):
    nums = [rng.randint(1, 12) for _ in range(rng.randint(1, 10))]
    assert can_split(nums) == can_split_bits(nums) == can_split_brute(nums), nums
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN1 = '''rng = random.Random(4160)
big_yes = [rng.randint(1, 100) for _ in range(199)]
big_yes.append(101 if sum(big_yes) % 2 else 100)                # make the total even
big_no = [2 * rng.randint(1, 50) for _ in range(199)]
big_no.append(4 if (sum(big_no) // 2) % 2 else 2)               # even total, odd half: impossible with even numbers'''
ANS1a = compute(SOL1, GEN1, expr="can_split(big_yes)")
ANS1b = compute(SOL1, GEN1, expr="can_split(big_no)")
assert ANS1b is False
TESTS1 = """check(can_split, [
    ([3, 1, 5, 9, 2], True),
    ([1, 2, 4], False),
    ([2, 2], True),
    ([5], False),
    ([1, 1, 1, 1], True),
    ([2, 3, 4, 6, 1], True),
    ([100, 1, 1], False),
    ([1, 2, 3, 8], False),
])
# big tests: 200 numbers between 1 and 100
@GEN@
check_big("n = 200, a split exists", lambda: can_split(big_yes), @A@, limit=1.5)
check_big("n = 200, no split exists", lambda: can_split(big_no), False, limit=1.5)""".replace(
    "@GEN@", GEN1).replace("@A@", repr(ANS1a))

ex.q("Two teams with the same total", minutes=15, level="medium",
     prompt="""You get a list of positive integers `nums` (for example the estimated hours of tasks). Return `True`
if you can split them into **two groups with the same sum** (every number goes to exactly one group).

Examples:
- `[3, 1, 5, 9, 2]` -> `True` (`9 + 1 = 10` and `3 + 5 + 2 = 10`)
- `[1, 2, 4]` -> `False` (the total 7 is odd)
- `[100, 1, 1]` -> `False`

Constraints: `1 <= len(nums) <= 200`, `1 <= nums[i] <= 100`. The big tests have 200 numbers, so trying every
subset (`2**200`) is impossible.""",
     stub="def can_split(nums):\n    pass",
     tests=TESTS1,
     hint1="Signal: choose a subset that hits an exact sum, and the sums are small (at most 200 * 100 / 2). "
           "Pattern: **1D dynamic programming** (0/1 knapsack on reachable sums).",
     hint2="""1. If the total is odd, return `False`. Otherwise the question is: does some subset sum to `total // 2`?
2. `reach[s]` = can some of the numbers seen so far sum to `s`. Start with `reach[0] = True`.
3. For each number `x`, for `s` from `target` **down** to `x`: `reach[s] |= reach[s - x]`.
4. Going down makes sure each number is used at most once in the same round.""",
     solution=SOL1,
     why="""Two equal groups exist exactly when one group sums to half the total. The brute force tries all `2^n`
subsets; the DP notices that only the **sum** of a subset matters, and there are at most `target + 1` different sums.
So we track the set of reachable sums, which costs O(n * target). The backwards loop is the classic 0/1 knapsack
trick: going forwards would let the same number be added twice. The big-integer bitset does the inner loop in C and
is the fastest version in Python.

**Follow-ups the examiner may ask:**
- Return the two groups: keep, for each sum, which number first reached it, then walk back from `target`.
- Split into `k` groups with equal sums (LeetCode 698): backtracking with pruning, or DP over bitmasks for small n.
- Make the two sums as close as possible (LeetCode 1049): same reachable set, take the largest reachable `s <= total / 2`.
- Numbers are huge (up to 10^9) but `n <= 40`: the DP table is too big; use meet in the middle (enumerate sums of
  each half, sort one side, binary search).""",
     complexity="Brute force: O(2^n). DP: O(n * S) time and O(S) space, where S = total / 2 (here at most 10^4). "
                "Bitset: same bound, but about 60 times faster in Python.",
     mistakes="Looping the sums upwards (uses a number twice). Forgetting the odd-total shortcut. Using a 2D table "
              "when one row is enough. Recursion with memo on `(i, left)` is fine, but without memo it is exponential.",
     learn=["algo-dp-1d"], source=("LeetCode 416", lc("partition-equal-subset-sum")))

# ---------------------------------------------------------------- Q2 Sliding Window Maximum (239)
SOL2 = '''from collections import deque

def window_max_brute(nums, k):
    """max() of every window. O(n * k)."""
    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]

def window_max(nums, k):
    """Monotonic deque of indexes whose values are decreasing; the front is the max of the window."""
    dq, out = deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:     # smaller values can never be a max again: drop them
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:                  # the front slid out of the window
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

rng = random.Random(239)
for _ in range(3000):
    nums = [rng.randint(-5, 5) for _ in range(rng.randint(1, 15))]
    k = rng.randint(1, len(nums))
    assert window_max(nums, k) == window_max_brute(nums, k), (nums, k)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN2 = '''rng = random.Random(2390)
big_nums = [rng.randint(-10**6, 10**6) for _ in range(200000)]
big_down = list(range(200000, 0, -1))           # decreasing: the deque holds a whole window'''
ANS2a = compute(SOL2, GEN2, expr="(lambda r: (len(r), sum(r)))(window_max(big_nums, 5000))")
ANS2b = compute(SOL2, GEN2, expr="(lambda r: (len(r), sum(r)))(window_max(big_down, 1000))")
TESTS2 = """check(window_max, [
    (([4, 2, 12, 3, 8, 1, 7], 3), [12, 12, 12, 8, 8]),
    (([5], 1), [5]),
    (([1, 2, 3, 4], 4), [4]),
    (([9, 8, 7, 6], 2), [9, 8, 7]),
    (([1, 3, 1, 2, 0, 5], 3), [3, 3, 2, 5]),
    (([-1, -3, -2], 1), [-1, -3, -2]),
    (([2, 2, 2, 2], 2), [2, 2, 2]),
    (([1, 5, 1, 5, 1], 2), [5, 5, 5, 5]),
])
# big tests: 200000 values; the check compares (number of windows, sum of the maxima)
@GEN@
summary = lambda r: (len(r), sum(r))
check_big("n = 200000, k = 5000", lambda: window_max(big_nums, 5000), @A@, key=summary, limit=1.0)
check_big("n = 200000 decreasing, k = 1000", lambda: window_max(big_down, 1000), @B@, key=summary, limit=1.0)""".replace(
    "@GEN@", GEN2).replace("@A@", repr(ANS2a)).replace("@B@", repr(ANS2b))

ex.q("Peak load in every time window", minutes=22, level="hard",
     prompt="""You get a list `nums` (for example requests per second) and a window size `k`. Slide a window of `k`
consecutive values from left to right, one step at a time, and return the **maximum** of each window, in order.

Examples:
- `nums = [4, 2, 12, 3, 8, 1, 7], k = 3` -> `[12, 12, 12, 8, 8]`
- `nums = [9, 8, 7, 6], k = 2` -> `[9, 8, 7]`
- `nums = [5], k = 1` -> `[5]`

Constraints: `1 <= k <= len(nums) <= 2 * 10**5`. Target: O(n). The big tests use `n = 200000` and `k` up to
5000, so computing `max` of every window (`n * k` steps) is too slow.""",
     stub="def window_max(nums, k):\n    pass",
     tests=TESTS2,
     hint1="Signal: maximum of a window that slides, where an old value can never matter again once a larger value "
           "arrives after it. Pattern: **monotonic deque** (a monotonic stack that also pops from the front).",
     hint2="""1. Keep a deque of **indexes** whose values are decreasing from front to back.
2. New value `x`: pop from the back while the back value is `<= x` (they can never be a maximum again), then
   append `i`.
3. If the front index is out of the window (`<= i - k`), pop it from the front.
4. From `i = k - 1` on, the front of the deque is the maximum of the current window.""",
     solution=SOL2,
     why="""A value that has a larger value to its right inside the window can never be the maximum of this or any
later window, so we drop it. What remains is decreasing, so the maximum is at the front. Each index enters and leaves
the deque at most once, which makes the whole scan O(n) even though a single step may pop many items. Storing
indexes (not values) is what lets us detect that the front has left the window.

**Follow-ups the examiner may ask:**
- A max-heap of `(-value, index)` with lazy removal of out-of-window tops: O(n log n), a fine first answer.
- Window minimum: the same deque with the comparison flipped. Both together give the range (max - min) per window.
- Values arrive as a stream: the deque works online and uses O(k) memory.
- Longest subarray where max - min <= limit (LeetCode 1438): two deques plus a variable window.
- Block decomposition: prefix maxima and suffix maxima per block of size k give O(n) with no deque.""",
     complexity="Brute force: O(n * k). Heap: O(n log n). Monotonic deque: O(n) time, O(k) space.",
     mistakes="Storing values instead of indexes (cannot tell when the front expires). Using `<` instead of `<=` is "
              "still correct but keeps duplicates; know why. Popping the front before appending with an off by one "
              "(`< i - k + 1` vs `<= i - k`). Using a list with `pop(0)` (O(k) each).",
     learn=["algo-monotonic-stack", "algo-sliding-window"], source=("LeetCode 239", lc("sliding-window-maximum")))

# ---------------------------------------------------------------- Q3 Cheapest Flights Within K Stops (787)
SOL3 = '''import heapq

def cheapest_price_brute(n, flights, src, dst, k):
    """Depth-first search over every route with at most k + 1 flights. Exponential."""
    graph = [[] for _ in range(n)]
    for u, v, w in flights:
        graph[u].append((v, w))
    best = float("inf")
    def go(city, cost, flights_left):
        nonlocal best
        if city == dst:
            best = min(best, cost)
            return
        if flights_left == 0:
            return
        for v, w in graph[city]:
            go(v, cost + w, flights_left - 1)
    go(src, 0, k + 1)
    return -1 if best == float("inf") else best

def cheapest_price(n, flights, src, dst, k):
    """Bellman-Ford limited to k + 1 rounds: after round r, cost[v] = cheapest price using at most r flights."""
    INF = float("inf")
    cost = [INF] * n
    cost[src] = 0
    for _ in range(k + 1):
        new = cost[:]                       # copy: one round may only add ONE more flight
        for u, v, w in flights:
            if cost[u] + w < new[v]:
                new[v] = cost[u] + w
        cost = new
    return -1 if cost[dst] == INF else cost[dst]

def cheapest_price_dijkstra(n, flights, src, dst, k):
    """Alternative: Dijkstra on states (city, flights used); prune a state if we already reached the city
    with fewer flights for less money."""
    graph = [[] for _ in range(n)]
    for u, v, w in flights:
        graph[u].append((v, w))
    best_flights = [float("inf")] * n         # fewest flights seen when a city was popped
    heap = [(0, src, 0)]
    while heap:
        price, city, used = heapq.heappop(heap)
        if city == dst:
            return price
        if used >= best_flights[city] or used == k + 1:
            continue
        best_flights[city] = used
        for v, w in graph[city]:
            heapq.heappush(heap, (price + w, v, used + 1))
    return -1

rng = random.Random(787)
for _ in range(1500):
    n = rng.randint(2, 6)
    flights = [[rng.randrange(n), rng.randrange(n), rng.randint(1, 20)] for _ in range(rng.randint(0, 12))]
    flights = [f for f in flights if f[0] != f[1]]
    src, dst, k = rng.randrange(n), rng.randrange(n), rng.randint(0, 3)
    if src == dst:
        continue
    want = cheapest_price_brute(n, flights, src, dst, k)
    assert cheapest_price(n, flights, src, dst, k) == cheapest_price_dijkstra(n, flights, src, dst, k) == want
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN3 = '''rng = random.Random(7870)
big_n = 100
pairs = set()
while len(pairs) < 3000:
    u, v = rng.randrange(big_n), rng.randrange(big_n)
    if u != v:
        pairs.add((u, v))
big_flights = [[u, v, rng.randint(50, 1000)] for u, v in sorted(pairs)]'''
ANS3 = compute(SOL3, GEN3, expr="cheapest_price(big_n, big_flights, 0, 99, 30)")
TESTS3 = """F = [[0, 1, 100], [1, 2, 100], [2, 3, 100], [0, 3, 500], [0, 2, 250]]
check(cheapest_price, [
    ((4, F, 0, 3, 1), 350),
    ((4, F, 0, 3, 2), 300),
    ((4, F, 0, 3, 0), 500),
    ((3, [[0, 1, 5]], 0, 2, 5), -1),
    ((2, [[0, 1, 7]], 0, 1, 0), 7),
    ((5, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [0, 4, 10]], 0, 4, 2), 10),
    ((4, [[0, 1, 1], [0, 2, 5], [1, 2, 1], [2, 3, 1]], 0, 3, 1), 6),
    ((3, [[0, 1, 2], [1, 0, 2], [1, 2, 9]], 0, 2, 3), 11),
])
# big test: 100 cities, 3000 flights, at most 30 stops
@GEN@
check_big("100 cities, 3000 flights, k = 30", lambda: cheapest_price(big_n, big_flights, 0, 99, 30), @ANS@, limit=1.0)""".replace(
    "@GEN@", GEN3).replace("@ANS@", repr(ANS3))

ex.q("Cheapest trip with a limit on stops", minutes=18, level="medium",
     prompt="""There are `n` cities `0 .. n-1` and one-way flights `[u, v, price]`. Return the cheapest total price
to fly from `src` to `dst` using **at most `k` stops** (a stop is a city strictly between `src` and `dst`, so at most
`k + 1` flights). Return `-1` if there is no such trip.

Example with `flights = [[0, 1, 100], [1, 2, 100], [2, 3, 100], [0, 3, 500], [0, 2, 250]]`, `src = 0`, `dst = 3`:
- `k = 0` -> `500` (direct flight only)
- `k = 1` -> `350` (`0 -> 2 -> 3`)
- `k = 2` -> `300` (`0 -> 1 -> 2 -> 3`)

Constraints: `n <= 100`, up to `n * (n - 1)` flights, prices between 1 and 10**4, `0 <= k < n`. Watch out: the
cheapest way to reach a middle city may use too many stops. The big test has 3000 flights and `k = 30`.""",
     stub="def cheapest_price(n, flights, src, dst, k):\n    pass",
     tests=TESTS3,
     hint1="Signal: shortest path, but with a limit on the **number of edges**. Plain Dijkstra on price alone is "
           "wrong. Pattern: **shortest path with a hop limit** (Bellman-Ford for k + 1 rounds, or BFS by levels, or "
           "Dijkstra on (city, stops) states).",
     hint2="""1. `cost[v]` = cheapest price to reach `v` with at most `r` flights. Start: `cost[src] = 0`, others inf.
2. Repeat `k + 1` times: make a copy `new = cost[:]`; for every flight `(u, v, w)`, `new[v] = min(new[v], cost[u] + w)`.
   Read from `cost` (last round), write to `new`.
3. The copy is essential: without it, one round could chain several flights.
4. Answer `cost[dst]`, or `-1` if it is still inf.""",
     solution=SOL3,
     why="""Round `r` of Bellman-Ford extends every best `r - 1`-flight route by exactly one flight, so after `k + 1`
rounds we have the cheapest route with at most `k + 1` flights. Reading from the previous round's array is what
enforces the limit. Dijkstra by price alone fails: it may settle a middle city through a cheap route with many stops
and then refuse a more expensive route with fewer stops that is the only one that can still reach `dst` in time
(see the test `[[0, 1, 1], [0, 2, 5], [1, 2, 1], [2, 3, 1]]`, `k = 1`). Dijkstra works again if the state is
`(city, flights used)`.

**Follow-ups the examiner may ask:**
- Return the route itself: keep `parent[r][v]` per round.
- Minimise the number of stops first, then the price: BFS by levels with a tie-break on price.
- Large graph with a small `k`: Dijkstra on `(city, stops)` with pruning explores much less than `k * E`.
- Negative prices (refunds)? Bellman-Ford still works with the round limit, Dijkstra does not.""",
     complexity="Brute force: exponential (all routes with up to k + 1 flights). Bellman-Ford with k + 1 rounds: "
                "O(k * E) time, O(n) space. Dijkstra on states: O(k * E * log(k * E)) worst case, usually faster.",
     mistakes="Updating `cost` in place inside a round (allows more than k + 1 flights). Using k rounds instead of "
              "k + 1. Plain Dijkstra with a visited set per city. Returning `inf` instead of `-1`.",
     learn=["algo-shortest-path", "algo-graphs-bfs-dfs"],
     source=("LeetCode 787", lc("cheapest-flights-within-k-stops")))

ex.save()
