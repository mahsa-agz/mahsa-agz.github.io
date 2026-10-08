import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _algo_mid_common import BIG

ex = Exam(16, "algorithms")
ex.setup(BIG)

# ---------------------------------------------------------------- Q1 container with most water (two pointers)
ex.q("Two walls that hold the most water", minutes=15,
     prompt="""`height[i]` is the height of a vertical wall at position `i`. Pick two walls; together with the floor
they form a container that holds `min(height[i], height[j]) * (j - i)` units of water. Return the largest amount any
pair can hold.

Example: `height = [2, 5, 4, 1, 6, 3]` gives `15`: walls at positions 1 (height 5) and 4 (height 6) hold
`min(5, 6) * 3 = 15`; walls 1 and 5 hold only `3 * 4 = 12`.

Constraints: up to 100,000 walls. Checking every pair is too slow.""",
     stub="""def max_area(height):
    pass""",
     tests="""check(max_area, [
    ([2, 5, 4, 1, 6, 3], 15),
    ([1, 8, 6, 2, 5, 4, 8, 3, 7], 49),
    ([1, 1], 1),                      # two walls only
    ([0, 0], 0),                      # zero height
    ([4, 3, 2, 1, 4], 16),            # the two ends win
    ([1, 2, 1], 2),
    ([1, 2, 4, 3], 4),
    ([10, 1, 1, 1, 1, 1, 1, 1, 1, 10], 90),
])
# larger input: heights 1..10,000 (best pair is near the middle)
n = 10_000
check_big("10,000 increasing walls", lambda: max_area(list(range(1, n + 1))), max((i + 1) * (n - 1 - i) for i in range(n)))""",
     hint1="""Signal: the best pair in an array where moving inward trades width for possible height. Start with the
widest pair and only move the **shorter** wall, because keeping it can never give a bigger container. Pattern:
**two pointers** from both ends.""",
     hint2="""1. `left = 0`, `right = n - 1`, `best = 0`.
2. While `left < right`: compute the area and update `best`.
3. Move the pointer at the shorter wall one step inward (if equal, move either).
4. Return `best`.""",
     solution="""def max_area(height):
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        h = min(height[left], height[right])
        best = max(best, h * (right - left))
        if height[left] < height[right]:   # the shorter wall limits every container that keeps it
            left += 1
        else:
            right -= 1
    return best""",
     why="""Suppose `height[left] < height[right]`. Every other container that uses `left` with a wall inside the
range is narrower and is still capped by `height[left]`, so none can beat the current one. That means `left` can be
discarded safely. Each step discards one wall, so one pass is enough.

**Follow-ups (what if...):**
- *What if you need the total water trapped between all bars (LeetCode 42, Trapping Rain Water)?* Different
  question: water above each bar is `min(max_left, max_right) - height`; also solvable with two pointers.
- *What if walls have widths (they are not one unit apart)?* Use positions `x[i]` instead of indices; the same
  argument holds as long as positions are sorted.
- *What if you must return the pair of indices?* Store `left, right` whenever `best` improves.
- *Why is moving the taller wall wrong?* Moving it keeps the shorter wall as the cap and reduces the width, so the
  area can only fall; you may skip the optimal pair.""",
     complexity="O(n) time, O(1) space.",
     mistakes="Moving the taller wall. Using `max` instead of `min` for the water level. The O(n^2) double loop, which "
              "fails the larger test.",
     learn=["algo-two-pointers", "algo-greedy"],
     source=("LeetCode 11", "https://leetcode.com/problems/container-with-most-water/"))

# ---------------------------------------------------------------- Q2 coin change (dp 1d)
ex.q("Fewest coins for an amount", minutes=18,
     prompt="""You get coin values `coins` (unlimited coins of each value) and a target `amount`. Return the smallest
number of coins that add up exactly to `amount`, or `-1` if it is impossible. An amount of 0 needs 0 coins.

Example: `coins = [1, 3, 4]`, `amount = 6` gives `2` (3 + 3). Taking the largest coin first gives 4 + 1 + 1 = 3 coins,
so "always take the biggest coin" is wrong here.
`coins = [2]`, `amount = 3` gives `-1`.

Constraints: up to 12 coin values, amount up to 10,000.""",
     stub="""def coin_change(coins, amount):
    pass""",
     tests="""check(coin_change, [
    (([1, 3, 4], 6), 2),              # greedy would give 3
    (([1, 2, 5], 11), 3),
    (([2], 3), -1),                   # impossible
    (([1], 0), 0),                    # amount 0
    (([1], 2), 2),
    (([3, 7], 1), -1),                # every coin is too big
    (([186, 419, 83, 408], 6249), 20),
    (([2, 5, 10, 1], 27), 4),
])
# larger input: amount 10,000 (a memoised recursion 10,000 levels deep hits the recursion limit)
check_big("amount 10,000", lambda: coin_change([7, 13, 29, 53, 97, 101], 10_000), 100, limit=2.0)""",
     hint1="""Signal: "minimum number of items to reach an exact total", items reusable, and greedy fails on some coin
sets. The best answer for an amount depends on best answers for smaller amounts. Pattern: **1-D dynamic programming**
(unbounded knapsack): `dp[a] = 1 + min(dp[a - c])` over coins `c`.""",
     hint2="""1. `dp = [0] + [inf] * amount`: `dp[a]` = fewest coins for amount `a`.
2. For `a` from 1 to `amount`, for each coin `c <= a`: `dp[a] = min(dp[a], dp[a - c] + 1)`.
3. Return `dp[amount]`, or -1 if it is still infinity.
(Alternative view: BFS from 0, each coin is an edge; the first time you reach `amount` is the answer.)""",
     solution="""def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount            # dp[a] = fewest coins that make a
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1    # last coin is c
    return dp[amount] if dp[amount] != INF else -1""",
     why="""Any optimal way to pay `a` ends with some coin `c`; the coins before it pay `a - c`, and they must be an
optimal way to pay `a - c` (otherwise you could improve the whole thing). So trying every last coin and reusing the
smaller answers is correct. Bottom-up filling avoids recursion depth problems and computes each amount once.

**Follow-ups (what if...):**
- *What if you need the number of different ways to pay (LeetCode 518)?* Loop coins on the outside and amounts on the
  inside, and add instead of taking the minimum (`ways[a] += ways[a - c]`); the loop order prevents counting the same
  set of coins in different orders.
- *What if each coin can be used at most once?* 0/1 knapsack: loop amounts **downward** for each coin.
- *What if you must return the coins, not only the count?* Store `last[a] = c` when `dp[a]` improves, then follow
  `a -= last[a]` back to 0.
- *When is greedy safe?* For "canonical" coin systems such as 1, 5, 10, 25. In an exam, say that greedy is a
  heuristic unless the coin system is known to be canonical.
- *What if the amount is huge (1e9) but coins are few?* The O(amount) table is too big; look for structure (for
  example BFS with pruning, or math on the largest coin), or ask whether an approximation is acceptable.""",
     complexity="O(amount x len(coins)) time, O(amount) space.",
     mistakes="Greedy (largest coin first). Initialising `dp` with 0 instead of infinity. Returning `inf` instead of -1. "
              "Recursion without memo (exponential) or with memo but 10,000 levels deep.",
     learn=["algo-dp-1d"],
     source=("LeetCode 322", "https://leetcode.com/problems/coin-change/"))

# ---------------------------------------------------------------- Q3 LRU cache (design)
ex.q("A cache that forgets the stalest entry", minutes=22,
     prompt="""Design a class `LRUCache` for a key-value cache with a fixed `capacity`:

- `LRUCache(capacity)` creates an empty cache.
- `get(key)` returns the value for `key`, or `-1` if the key is not in the cache. A successful `get` counts as a
  **use** of that key.
- `put(key, value)` inserts or updates the key (this also counts as a use). If the cache is now over capacity, remove
  the key that was **used least recently**.

Both operations must run in **O(1)** average time.

Example with capacity 2: `put(1, 10)`, `put(2, 20)`, `get(1)` returns `10` (key 1 is now the most recent),
`put(3, 30)` removes key 2 (least recent), so `get(2)` returns `-1`, while `get(1)` returns `10` and `get(3)` returns
`30`.

The tests run scripted sequences: each `get` result is collected and compared with the expected list.""",
     stub="""class LRUCache:
    def __init__(self, capacity):
        pass

    def get(self, key):
        pass

    def put(self, key, value):
        pass""",
     tests="""def run_lru(label, capacity, ops, want):
    try:
        cache, got = LRUCache(capacity), []
        for op in ops:
            if op[0] == "put":
                cache.put(op[1], op[2])
            else:
                got.append(cache.get(op[1]))
    except Exception as e:
        got = "error: " + repr(e)
    print(("PASS " if got == want else "FAIL ") + label + ("" if got == want else f"   got {got}, expected {want}"))

run_lru("example from the prompt", 2,
        [("put", 1, 10), ("put", 2, 20), ("get", 1), ("put", 3, 30), ("get", 2), ("get", 1), ("get", 3)],
        [10, -1, 10, 30])
run_lru("get on an empty cache", 3, [("get", 5)], [-1])
run_lru("capacity 1", 1, [("put", 1, 1), ("put", 2, 2), ("get", 1), ("get", 2)], [-1, 2])
run_lru("update keeps size and refreshes recency", 2,
        [("put", 1, 1), ("put", 2, 2), ("put", 1, 100), ("put", 3, 3), ("get", 1), ("get", 2), ("get", 3)],
        [100, -1, 3])
run_lru("get refreshes recency", 2,
        [("put", 1, 1), ("put", 2, 2), ("get", 1), ("put", 3, 3), ("get", 2), ("get", 1)],
        [1, -1, 1])
run_lru("a missed get does not change anything", 2,
        [("put", 1, 1), ("put", 2, 2), ("get", 9), ("put", 3, 3), ("get", 1), ("get", 2)],
        [-1, -1, 2])

# larger input: 200,000 puts with capacity 5,000, then reads (only the last 5,000 keys survive)
def big_run():
    cache = LRUCache(5_000)
    for k in range(200_000):
        cache.put(k, k * 2)
    return [cache.get(k) for k in range(194_000, 200_000)]
check_big("200,000 puts, 6,000 gets", big_run, [-1] * 1_000 + [k * 2 for k in range(195_000, 200_000)], limit=2.0)""",
     hint1="""Signal: O(1) lookup **and** O(1) "remove the oldest / move to the newest". A hash map gives the lookup;
a doubly linked list (or Python's `OrderedDict`, which is one inside) keeps the use order. Pattern: **design**
(hash map + doubly linked list).""",
     hint2="""1. Map `key -> node`; nodes form a doubly linked list from least recent (head side) to most recent (tail
side). Use dummy head and tail nodes to avoid edge cases.
2. `get`: if the key exists, unlink its node and re-insert it before the tail; return the value.
3. `put`: if the key exists, update the value and move it to the tail; else create a node, insert it at the tail and
   add it to the map. If the size exceeds capacity, unlink `head.next` and delete its key from the map.
4. With `OrderedDict`: `move_to_end(key)` on use, `popitem(last=False)` to evict.""",
     solution="""class Node:
    __slots__ = ("key", "val", "prev", "next")
    def __init__(self, key=0, val=0):
        self.key, self.val, self.prev, self.next = key, val, None, None

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}                                   # key -> Node
        self.head, self.tail = Node(), Node()           # dummies: head.next = least recent, tail.prev = most recent
        self.head.next, self.tail.prev = self.tail, self.head

    def _unlink(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _append(self, node):                            # insert just before the tail (most recent)
        node.prev, node.next = self.tail.prev, self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def get(self, key):
        node = self.map.get(key)
        if node is None:
            return -1
        self._unlink(node)
        self._append(node)
        return node.val

    def put(self, key, value):
        node = self.map.get(key)
        if node:
            node.val = value
            self._unlink(node)
        else:
            node = Node(key, value)
            self.map[key] = node
        self._append(node)
        if len(self.map) > self.cap:
            lru = self.head.next                        # least recently used
            self._unlink(lru)
            del self.map[lru.key]                       # the node stores its key so we can do this

# Short version that is usually accepted if you can explain what OrderedDict does inside:
from collections import OrderedDict

class LRUCacheShort:
    def __init__(self, capacity):
        self.cap, self.d = capacity, OrderedDict()

    def get(self, key):
        if key not in self.d:
            return -1
        self.d.move_to_end(key)
        return self.d[key]

    def put(self, key, value):
        self.d[key] = value
        self.d.move_to_end(key)
        if len(self.d) > self.cap:
            self.d.popitem(last=False)""",
     why="""The hash map finds a node in O(1); the doubly linked list lets you remove any node and append at the end
in O(1) because each node knows both neighbours. Dummy head and tail nodes mean you never special-case an empty list
or the first/last node. Each node stores its key so eviction can also delete the map entry. A plain list (`list.remove`
plus `append`) is O(n) per use.

**Follow-ups (what if...):**
- *What if many threads use the cache at once?* Protect `get` and `put` with one lock (simple), or shard the cache by
  key hash with one lock per shard to reduce contention.
- *What if you need LFU (least frequently used, LeetCode 460)?* Map key -> (value, freq) plus a map
  freq -> ordered set of keys and a `min_freq` pointer, still O(1).
- *What if entries should expire after a time-to-live?* Store the expiry time in the node; check it on `get` and
  lazily evict, or keep a heap of expiry times.
- *What if items have different sizes and the capacity is in bytes?* Track the total size and evict from the head in
  a loop until it fits.
- *Where is this used in data work?* `functools.lru_cache` for memoisation, feature caches in model serving, and
  database buffer pools.""",
     complexity="O(1) average time for `get` and `put`; O(capacity) space.",
     mistakes="Forgetting that `get` changes recency. Not updating recency when `put` overwrites an existing key. "
              "Evicting before inserting when the key already exists (the size did not grow). Using a list for the "
              "order (O(n) per operation). Forgetting to delete the evicted key from the map.",
     learn=["algo-design", "algo-linked-list", "algo-hashing"],
     source=("LeetCode 146", "https://leetcode.com/problems/lru-cache/"))

ex.save()
