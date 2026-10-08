"""Day 24 algorithms (hard): Next Permutation, Largest Rectangle in Histogram, Network Delay Time."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from _algo_hard_common import BIG, lc, compute

ex = Exam(24, "algorithms")
ex.setup(BIG)

# ---------------------------------------------------------------- Q1 Next Permutation (31)
SOL1 = '''from itertools import permutations

def next_permutation_brute(nums):
    """List every distinct arrangement in sorted order and take the one after nums. O(n! * n)."""
    perms = sorted(set(permutations(nums)))
    i = perms.index(tuple(nums))
    nums[:] = perms[(i + 1) % len(perms)]          # after the last one, wrap to the first (sorted)

def next_permutation(nums):
    """In place, O(n): find the pivot, swap with the next larger value, reverse the tail."""
    i = len(nums) - 2
    while i >= 0 and nums[i] >= nums[i + 1]:       # 1. longest non-increasing tail starts at i + 1
        i -= 1
    if i >= 0:
        j = len(nums) - 1
        while nums[j] <= nums[i]:                  # 2. rightmost value in the tail that is larger than the pivot
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    lo, hi = i + 1, len(nums) - 1                  # 3. the tail is still non-increasing: reverse it to ascending
    while lo < hi:
        nums[lo], nums[hi] = nums[hi], nums[lo]
        lo, hi = lo + 1, hi - 1

rng = random.Random(31)
for _ in range(2000):
    a = [rng.randint(1, 4) for _ in range(rng.randint(1, 6))]
    b = a[:]
    next_permutation(a)
    next_permutation_brute(b)
    assert a == b
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN1 = '''big = list(range(100000)) + list(range(199999, 99999, -1))     # 200000 values, the second half descending'''
ANS1 = compute(SOL1, GEN1, "next_permutation(big)", expr="big")
TESTS1 = """def after_next(nums):
    next_permutation(nums)          # must change nums in place
    return nums

check(after_next, [
    ([2, 4, 3, 1], [3, 1, 2, 4]),
    ([3, 2, 1], [1, 2, 3]),
    ([1, 1, 5], [1, 5, 1]),
    ([1], [1]),
    ([1, 3, 2], [2, 1, 3]),
    ([2, 2, 2], [2, 2, 2]),
    ([5, 1, 1], [1, 1, 5]),
    ([1, 5, 8, 4, 7, 6, 5, 3, 1], [1, 5, 8, 5, 1, 3, 4, 6, 7]),
])
# big test: 200000 values
@GEN@
big_want = list(range(99999)) + [100000] + list(range(99999, 100000)) + list(range(100001, 200000))
check_big("n = 200000", lambda: after_next(big), big_want, limit=0.5)""".replace("@GEN@", GEN1)
assert compute(GEN1, "big_want = list(range(99999)) + [100000] + list(range(99999, 100000)) + list(range(100001, 200000))",
               expr="big_want") == ANS1

ex.q("The next arrangement in dictionary order", minutes=15, level="medium",
     prompt="""Think of all arrangements of a list of numbers, sorted like words in a dictionary. Change `nums`
**in place** into the arrangement that comes right after it. If `nums` is already the largest arrangement, change
it into the smallest one (ascending order). Use O(1) extra memory and return nothing.

Examples:
- `[2, 4, 3, 1]` -> `[3, 1, 2, 4]`
- `[1, 1, 5]` -> `[1, 5, 1]`
- `[3, 2, 1]` -> `[1, 2, 3]` (it was the last one, so wrap around)

Constraints: `1 <= len(nums) <= 2 * 10**5`, values may repeat. The big test has 200000 values, so listing
arrangements is impossible.""",
     stub="def next_permutation(nums):\n    pass",
     tests=TESTS1,
     hint1="Signal: \"next larger arrangement\" means you change as little as possible at the right end. Pattern: "
           "**array scan from the right** (find a pivot, swap, reverse the tail).",
     hint2="""1. From the right, find the first index `i` with `nums[i] < nums[i+1]` (the pivot). The part after it is
   non-increasing, so it is already the largest arrangement of those values.
2. If there is no pivot, reverse the whole list and stop.
3. Find the rightmost `j > i` with `nums[j] > nums[i]` and swap them.
4. Reverse the part after `i` (it is still non-increasing) so it becomes the smallest arrangement.""",
     solution=SOL1,
     why="""To get the very next arrangement we must keep the longest possible prefix. The non-increasing tail can
not get any larger by itself, so the first position that can grow is the pivot just before it. We raise the pivot by
the smallest possible amount (the smallest tail value larger than it, which is the rightmost such value), and then
make the tail as small as possible. After the swap the tail is still non-increasing, so a reverse (O(n)) sorts it;
no sort is needed.

**Follow-ups the examiner may ask:**
- Previous arrangement: the same steps with the comparisons flipped.
- The k-th arrangement of `1..n` (LeetCode 60): build it digit by digit with factorials, O(n^2) or O(n log n).
- Next larger number with the same digits (LeetCode 556): run this on the digits; return -1 if there is no pivot
  or if the result does not fit in 32 bits.
- Why does `>=` (not `>`) matter in step 1? With duplicates, `>` would stop at an equal pair and produce a wrong or
  repeated arrangement.""",
     complexity="Brute force: O(n! * n). Scan, swap, reverse: O(n) time, O(1) extra space.",
     mistakes="Using `>` instead of `>=` when looking for the pivot (breaks on duplicates). Swapping with the first "
              "larger value from the left of the tail instead of the rightmost. Sorting the tail (O(n log n), correct "
              "but misses the point). Returning a new list instead of changing `nums`.",
     learn=["algo-arrays-strings", "algo-two-pointers"], source=("LeetCode 31", lc("next-permutation")))

# ---------------------------------------------------------------- Q2 Largest Rectangle in Histogram (84)
SOL2 = '''def largest_rectangle_brute(heights):
    """Every bar range [i, j], keeping the running minimum. O(n^2)."""
    best = 0
    for i in range(len(heights)):
        low = float("inf")
        for j in range(i, len(heights)):
            low = min(low, heights[j])
            best = max(best, low * (j - i + 1))
    return best

def largest_rectangle(heights):
    """Monotonic stack of indexes with increasing heights. When a lower bar arrives, the bars it pops cannot
    extend further right, and their left limit is the index below them on the stack."""
    stack, best = [], 0                            # stack holds indexes, heights increasing
    for i, h in enumerate(heights + [0]):          # the extra 0 flushes the stack at the end
        while stack and heights[stack[-1]] >= h:
            top = heights[stack.pop()]
            left = stack[-1] + 1 if stack else 0   # first index the rectangle can start at
            best = max(best, top * (i - left))
        stack.append(i)
    return best

rng = random.Random(84)
for _ in range(3000):
    h = [rng.randint(0, 6) for _ in range(rng.randint(0, 12))]
    assert largest_rectangle(h) == largest_rectangle_brute(h), h
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN2 = '''rng = random.Random(8484)
big_random = [rng.randint(0, 10000) for _ in range(200000)]
big_up = list(range(1, 200001))                   # strictly increasing: the stack grows to 200000'''
ANS2a = compute(SOL2, GEN2, expr="largest_rectangle(big_random)")
ANS2b = compute(SOL2, GEN2, expr="largest_rectangle(big_up)")
TESTS2 = """check(largest_rectangle, [
    ([2, 4, 6, 5, 1], 12),
    ([], 0),
    ([7], 7),
    ([3, 3, 3], 9),
    ([1, 2, 3, 4, 5], 9),
    ([5, 4, 3, 2, 1], 9),
    ([2, 1, 2], 3),
    ([6, 2, 5, 4, 5, 1, 6], 12),
])
# big tests: 200000 random bars, and 200000 increasing bars
@GEN@
check_big("n = 200000, random", lambda: largest_rectangle(big_random), @A@, limit=1.0)
check_big("n = 200000, increasing", lambda: largest_rectangle(big_up), @B@, limit=1.0)""".replace(
    "@GEN@", GEN2).replace("@A@", repr(ANS2a)).replace("@B@", repr(ANS2b))

ex.q("Biggest poster on a bar chart", minutes=22, level="hard",
     prompt="""A bar chart has bars of width 1 with heights `heights`, standing side by side. You want to glue the
largest possible rectangular poster **inside** the bars (the poster sits on the ground and may not stick out above
any bar it covers). Return its area.

Examples:
- `[2, 4, 6, 5, 1]` -> `12` (height 4 over the bars `4, 6, 5`)
- `[3, 3, 3]` -> `9`
- `[2, 1, 2]` -> `3` (height 1 over all three bars)

Constraints: `0 <= len(heights) <= 2 * 10**5`, heights between 0 and 10**4 in the random test. Target: O(n). One big
test is 200000 increasing bars.""",
     stub="def largest_rectangle(heights):\n    pass",
     tests=TESTS2,
     hint1="Signal: for each bar you need the nearest **smaller** bar on the left and on the right. Pattern: "
           "**monotonic stack** (increasing heights).",
     hint2="""1. Brute force: for every start `i`, extend `j` and keep the minimum height; area = `min * width`. O(n^2).
2. Idea: the best rectangle uses some bar as its height and spreads until a lower bar on each side.
3. Keep a stack of indexes with increasing heights. When bar `i` is lower than the top, pop the top: its right limit
   is `i`, its left limit is the new top + 1 (or 0 if the stack is empty). Area = `height * (i - left)`.
4. Append a 0 at the end so every bar is popped.""",
     solution=SOL2,
     why="""Every optimal rectangle is as tall as its lowest bar and cannot extend past the nearest lower bars on
either side. A bar is popped exactly when we meet the first lower bar on its right, and the bar under it in the
stack is the first lower (or equal) bar on its left, so at pop time we know its full width. Each index is pushed and
popped once, so the work is O(n) even for the increasing input where the stack holds every bar.

**Follow-ups the examiner may ask:**
- Largest rectangle of 1s in a binary matrix (LeetCode 85): for each row build the histogram of consecutive 1s
  above it and run this function. O(R * C).
- With equal heights, does `>=` or `>` matter? Both give the right maximum; with `>=` an equal bar is popped early,
  but the later equal bar covers that width.
- Divide and conquer alternative: split at the minimum bar, O(n log n) on average, O(n^2) on sorted input.
- Nearest smaller element to the left and right for every index: the same stack, a common building block.""",
     complexity="Brute force: O(n^2). Monotonic stack: O(n) time, O(n) space.",
     mistakes="Wrong width after a pop (use the new stack top, not the popped index). Forgetting the bars left on "
              "the stack at the end (the 0 sentinel). Storing heights instead of indexes, so widths are unknown. "
              "Mutating the input by appending the sentinel to it (use `heights + [0]`).",
     learn=["algo-monotonic-stack", "algo-stack"], source=("LeetCode 84", lc("largest-rectangle-in-histogram")))

# ---------------------------------------------------------------- Q3 Network Delay Time (743)
SOL3 = '''import heapq

def network_delay_brute(times, n, k):
    """Bellman-Ford: relax every edge n - 1 times. O(n * E)."""
    INF = float("inf")
    dist = [INF] * (n + 1)
    dist[k] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in times:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break
    worst = max(dist[1:])
    return -1 if worst == INF else worst

def network_delay(times, n, k):
    """Dijkstra with a min-heap and lazy deletion. O(E log V)."""
    graph = [[] for _ in range(n + 1)]
    for u, v, w in times:
        graph[u].append((v, w))
    dist = {}
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue                      # an older, longer entry: skip it
        dist[u] = d                       # the first pop of u is its shortest time
        for v, w in graph[u]:
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return max(dist.values()) if len(dist) == n else -1

rng = random.Random(743)
for _ in range(1500):
    n = rng.randint(1, 7)
    times = [[rng.randint(1, n), rng.randint(1, n), rng.randint(0, 9)] for _ in range(rng.randint(0, 15))]
    k = rng.randint(1, n)
    assert network_delay(times, n, k) == network_delay_brute(times, n, k)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN3 = '''rng = random.Random(7430)
N = 20000
big_times = [[i, i + 1, 1000] for i in range(1, N)]                          # a slow chain so every server is reachable
big_times += [[rng.randint(1, N), rng.randint(1, N), rng.randint(1, 100)] for _ in range(200000)]'''
ANS3 = compute(SOL3, GEN3, expr="network_delay(big_times, N, 1)")
TESTS3 = """check(network_delay, [
    (([[1, 2, 4], [1, 3, 1], [3, 2, 2], [2, 4, 1]], 4, 1), 4),
    (([[1, 2, 1]], 2, 2), -1),
    (([], 1, 1), 0),
    (([[1, 2, 5], [1, 2, 3]], 2, 1), 3),
    (([[1, 2, 1], [2, 3, 1], [3, 1, 1]], 3, 2), 2),
    (([[1, 2, 0], [2, 3, 0]], 3, 1), 0),
    (([[1, 2, 2], [2, 3, 2], [1, 3, 5]], 3, 1), 4),
    (([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2), 2),
])
# big test: 20000 servers, about 220000 links
@GEN@
check_big("20000 servers, 219999 links", lambda: network_delay(big_times, N, 1), @ANS@, limit=2.5)""".replace(
    "@GEN@", GEN3).replace("@ANS@", repr(ANS3))

ex.q("How long until every server hears the alert?", minutes=18, level="medium",
     prompt="""There are `n` servers numbered `1` to `n`. `times` lists one-way links `[u, v, w]`: a message sent
from `u` reaches `v` after `w` milliseconds (`w >= 0`). Server `k` starts broadcasting an alert, and every server
forwards it on all its outgoing links as soon as it receives it. Return the time when the **last** server receives
the alert, or `-1` if some server never receives it.

Examples:
- `times = [[1, 2, 4], [1, 3, 1], [3, 2, 2], [2, 4, 1]], n = 4, k = 1` -> `4` (server 2 at time 3 via server 3,
  server 4 at time 4)
- `times = [[1, 2, 1]], n = 2, k = 2` -> `-1` (links are one-way)
- `times = [], n = 1, k = 1` -> `0`

Constraints: `1 <= n <= 2 * 10**4`, up to `2.2 * 10**5` links, parallel links allowed. The big test has 20000
servers.""",
     stub="def network_delay(times, n, k):\n    pass",
     tests=TESTS3,
     hint1="Signal: shortest travel time from one source in a graph with **non-negative weights**. Pattern: "
           "**shortest path, Dijkstra** with a min-heap.",
     hint2="""1. Brute force: Bellman-Ford, relax all edges `n - 1` times. O(n * E): too slow here.
2. Build an adjacency list `u -> [(v, w)]`.
3. Heap starts with `(0, k)`. Pop the smallest time; if the server is already final, skip it; else record its time
   and push `(time + w, v)` for each link.
4. Answer: the largest final time if all `n` servers are final, else `-1`.""",
     solution=SOL3,
     why="""With non-negative weights, the server with the smallest tentative time cannot be improved later (any
other route goes through servers that are at least as far), so the first time it is popped from the heap is final.
Lazy deletion (skip servers already final) is simpler than a decrease-key operation and keeps the bound O(E log E),
which is O(E log V). Bellman-Ford does not need that greedy argument, which is why it also works with negative
weights, but it pays O(n * E).

**Follow-ups the examiner may ask:**
- Negative link times: Dijkstra is wrong; use Bellman-Ford (and detect negative cycles with one extra round).
- All links take the same time: plain BFS, O(V + E). Weights only 0 or 1: 0-1 BFS with a deque.
- Return the route to the slowest server: store `parent[v]` when you push, then walk back.
- Dense graph (E close to V^2): the O(V^2) array version of Dijkstra beats the heap.
- Times between all pairs of servers: Floyd-Warshall, O(V^3), fine for a few hundred servers.""",
     complexity="Brute force (Bellman-Ford): O(n * E). Dijkstra with a heap: O(E log V) time, O(V + E) space.",
     mistakes="Marking a server final when it is pushed instead of when it is popped. Forgetting to skip stale heap "
              "entries (correct but slow). Returning the sum of times instead of the maximum. Servers are numbered "
              "from 1 (size the arrays `n + 1`). Treating links as two-way.",
     learn=["algo-shortest-path", "algo-heap"], source=("LeetCode 743", lc("network-delay-time")))

ex.save()
