"""Day 30 algorithms (light final check): Car Fleet, a custom data-processing problem (top creators by watch time
from raw event logs), a rapid pattern-recognition drill, and the day-before checklist."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam, learn_links
from _algo_hard_common import BIG, lc, compute

INTRO = """**Light day.** This is a short final check, not a new exam: about 45 minutes, no stress. Solve the two
problems with the five-step script from yesterday (clarify, examples, brute force, optimise, test), then do the
10-minute pattern drill out loud. Finish with the checklist at the end and stop studying algorithms for today."""

ex = Exam(30, "algorithms", title="Day 30: Algorithms (final check)", intro=INTRO)

LOG = '''def make_watch_log(seed=30):
    """MADE-UP raw player events of a short-video app.
    watch_events: rows (ts_seconds, user_id, video_id, event) with event in "play", "pause", "stop".
    videos: catalog video_id -> creator_id (a few deleted videos are missing from it).
    Like real logs: unsorted, retried duplicates, pauses with no play before them, double plays,
    and views that never stop (the app crashed)."""
    rng = random.Random(seed)
    creators = [f"c{i:02d}" for i in range(1, 41)]
    pop = {c: rng.paretovariate(1.2) for c in creators}                 # a few creators are much more popular
    all_videos = {f"v{i:04d}": rng.choice(creators) for i in range(1, 401)}
    ids = sorted(all_videos)
    weights = [pop[all_videos[v]] for v in ids]
    rows = []
    for u in range(1, 601):
        user = f"u{u:04d}"
        for video in set(rng.choices(ids, weights=weights, k=rng.randint(1, 12))):
            t = rng.randint(0, 86000)
            if rng.random() < 0.02:
                rows.append((t - rng.randint(1, 100), user, video, "pause"))      # pause with no play before it
            for seg in range(rng.randint(1, 4)):                                   # play ... pause segments
                rows.append((t, user, video, "play"))
                dur = rng.randint(2, 120)
                if rng.random() < 0.02:
                    rows.append((t + 1, user, video, "play"))                      # double play: ignored
                t += dur
                rows.append((t, user, video, "pause"))
                t += rng.randint(1, 300)
            if rng.random() < 0.9:
                rows[-1] = (rows[-1][0], user, video, "stop")                      # last pause becomes a stop
            else:
                rows.append((t, user, video, "play"))                              # never closed: app crashed
    rows += rng.sample(rows, len(rows) // 30)                                      # retried duplicates
    rng.shuffle(rows)
    deleted = set(rng.sample(ids, 10))
    videos = {v: c for v, c in all_videos.items() if v not in deleted}
    return rows, videos

watch_events, videos = make_watch_log()
print(len(watch_events), "events,", len(videos), "videos in the catalog, for example:", watch_events[:2])'''

ex.setup(BIG + "\n\n" + LOG)

# ---------------------------------------------------------------- Q1 Car Fleet (853)
SOL1 = '''def car_fleet_brute(target, position, speed):
    """A truck leads its own convoy only if no truck ahead of it arrives later or at the same time. O(n^2)."""
    times = [(target - p) / s for p, s in zip(position, speed)]
    fleets = 0
    for i in range(len(position)):
        blocked = any(position[j] > position[i] and times[j] >= times[i] for j in range(len(position)))
        fleets += not blocked
    return fleets

def car_fleet(target, position, speed):
    """Sort by position, closest to the target first. Keep the arrival time of the convoy in front:
    a slower-or-equal truck behind joins it, a truck that would arrive later starts a new convoy. O(n log n)."""
    fleets, lead_time = 0, 0.0
    for p, s in sorted(zip(position, speed), reverse=True):
        t = (target - p) / s                  # arrival time if the road were free
        if t > lead_time:                     # cannot catch the convoy ahead: new convoy
            fleets += 1
            lead_time = t
    return fleets

rng = random.Random(853)
for _ in range(3000):
    n = rng.randint(0, 8)
    pos = rng.sample(range(0, 30), n)
    spd = [rng.randint(1, 5) for _ in range(n)]
    assert car_fleet(30, pos, spd) == car_fleet_brute(30, pos, spd), (pos, spd)
print("stress test vs brute force: OK")   # prints: stress test vs brute force: OK'''

GEN1 = '''rng = random.Random(8530)
big_pos = rng.sample(range(10**6), 100000)
big_speed = [rng.randint(1, 10**3) for _ in range(100000)]'''
ANS1 = compute(SOL1, GEN1, expr="car_fleet(10**6, big_pos, big_speed)")
TESTS1 = """check(car_fleet, [
    ((20, [0, 4, 10, 16], [4, 2, 2, 1]), 3),
    ((10, [3], [3]), 1),
    ((10, [], []), 0),
    ((100, [0, 2, 4], [4, 2, 1]), 1),
    ((10, [6, 8], [3, 2]), 2),
    ((10, [0, 4, 8], [1, 1, 1]), 3),
    ((12, [4, 6], [6, 3]), 1),
    ((10, [0, 5], [2, 1]), 1),
])
# big test: 100000 trucks
@GEN@
check_big("n = 100000", lambda: car_fleet(10**6, big_pos, big_speed), @ANS@, limit=1.0)""".replace(
    "@GEN@", GEN1).replace("@ANS@", repr(ANS1))

ex.q("Convoys on a one-lane road", minutes=15, level="medium",
     prompt="""Delivery trucks drive on a one-lane road towards a depot at mile `target`. Truck `i` starts at mile
`position[i]` (all different) and drives at `speed[i]` miles per hour. A truck can never pass another one: when it
catches up with a slower truck, it slows down and they drive on together as one **convoy** (a convoy can grow).
A truck that catches up exactly at the depot also counts as part of that convoy. Return the number of convoys that
arrive at the depot.

Examples:
- `target = 20, position = [0, 4, 10, 16], speed = [4, 2, 2, 1]` -> `3`. The truck at 16 needs 4 hours, the one at
  10 needs 5 hours (cannot catch it), the one at 4 needs 8 hours, and the one at 0 would need 5 hours, so it catches
  the truck from 4 and joins it.
- `target = 10, position = [0, 5], speed = [2, 1]` -> `1` (both would arrive after 5 hours: they meet at the depot)

Constraints: `0 <= n <= 10**5`. Target: O(n log n). The big test has 100000 trucks.""",
     stub="def car_fleet(target, position, speed):\n    pass",
     tests=TESTS1,
     hint1="Signal: objects that cannot pass each other, so only the order by position matters, and each one is "
           "compared with the group in front of it. Pattern: **sort, then one pass** (a monotonic stack of arrival "
           "times also works).",
     hint2="""1. Arrival time if alone: `t = (target - position) / speed`.
2. Sort trucks by position, **closest to the depot first**.
3. Keep `lead_time`, the arrival time of the convoy just in front. If `t > lead_time`, this truck cannot catch it:
   new convoy, `lead_time = t`. Otherwise it joins (and is slowed down to `lead_time`).
4. The answer is the number of new convoys.""",
     solution=SOL1,
     why="""A truck behind can only be slowed down by the convoy directly in front of it, and once it joins, the
convoy arrives at the time of its leader. So after sorting by position from the front, every truck either starts a
new convoy (it would arrive later than the convoy ahead) or merges (it would arrive earlier or at the same time).
Sorting dominates the cost. The brute force asks, for every truck, whether any truck ahead arrives later, which is
O(n^2).

**Follow-ups the examiner may ask:**
- Floating point: compare `(target - p1) * s2` with `(target - p2) * s1` to stay exact with integers.
- When does each truck reach the depot (LeetCode 1776, Car Fleet II, asks for the collision times)? Monotonic stack
  from the front.
- Positions are already sorted: O(n).
- Streaming: trucks join at the back over time: keep the last `lead_time`.""",
     complexity="Brute force: O(n^2). Sort and scan: O(n log n) time, O(n) space for the sorted pairs.",
     mistakes="Sorting from the back of the road instead of the front. Using `>=` instead of `>` (a truck that ties "
              "at the depot must join). Integer division for the time. Forgetting the empty input.",
     learn=["algo-sorting-intervals", "algo-monotonic-stack", "algo-greedy"], source=("LeetCode 853", lc("car-fleet")))

# ---------------------------------------------------------------- Q2 top creators by watch time (custom)
SOL2 = '''import heapq
from collections import defaultdict

def _watch_seconds(events_of_pair):
    """Sum of closed play segments of one (user, video) pair. Events must be in time order."""
    total, open_at = 0, None
    for ts, ev in events_of_pair:
        if ev == "play":
            if open_at is None:                   # a second play while open is ignored
                open_at = ts
        elif open_at is not None:                 # pause or stop closes the open segment
            total += ts - open_at
            open_at = None
    return total                                  # a segment still open at the end is dropped

def top_creators_brute(events, videos, k):
    """For every creator, scan the whole log again for that creator's events. O(C * n log n)."""
    totals = {}
    for creator in set(videos.values()):
        pairs = defaultdict(list)
        for ts, user, video, ev in events:
            if videos.get(video) == creator:
                pairs[(user, video)].append((ts, ev))
        secs = sum(_watch_seconds(sorted(evs)) for evs in pairs.values())
        if secs > 0:
            totals[creator] = secs
    return sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))[:k]

def top_creators(events, videos, k):
    """One pass to group by (user, video), sort each group, sum per creator, then a heap for the top k.
    O(n log n) for the sorts + O(C log k) for the top k."""
    pairs = defaultdict(list)
    for ts, user, video, ev in events:
        if video in videos:                        # deleted / unknown videos are ignored
            pairs[(user, video)].append((ts, ev))
    per_creator = defaultdict(int)
    for (user, video), evs in pairs.items():
        evs.sort()                                 # time order; exact duplicates sit next to each other
        per_creator[videos[video]] += _watch_seconds(evs)
    ranked = ((secs, creator) for creator, secs in per_creator.items() if secs > 0)
    best = heapq.nsmallest(k, ranked, key=lambda x: (-x[0], x[1]))
    return [(creator, secs) for secs, creator in best]

rng = random.Random(3030)
for _ in range(200):
    sample = rng.sample(watch_events, 300)
    k = rng.randint(1, 8)
    assert top_creators(sample, videos, k) == top_creators_brute(sample, videos, k)
print("stress test vs brute force: OK")              # prints: stress test vs brute force: OK
print(top_creators(watch_events, videos, 3))         # prints: @TOP3@'''

TOP3 = compute(BIG, LOG, SOL2.split("rng = random.Random(3030)")[0], expr="top_creators(watch_events, videos, 3)")
SOL2 = SOL2.replace("@TOP3@", repr(TOP3))
ANS2 = compute(BIG, LOG, SOL2, expr="top_creators(watch_events, videos, 5)")
NEV = compute(BIG, LOG, expr="len(watch_events)")

TESTS2 = """V = {"v1": "alice", "v2": "bob", "v3": "alice", "v4": "cara"}
basic = [(0, "u1", "v1", "play"), (100, "u1", "v1", "stop"),
         (10, "u2", "v2", "play"), (70, "u2", "v2", "pause"), (80, "u2", "v2", "play"), (90, "u2", "v2", "stop")]
check(top_creators, [
    # play/stop and play/pause/play/stop segments
    ((basic, V, 2), [("alice", 100), ("bob", 70)]),
    # the same events in another order
    ((basic[::-1], V, 2), [("alice", 100), ("bob", 70)]),
    # equal totals: smaller creator id first, and k cuts the list
    (([(0, "u1", "v1", "play"), (50, "u1", "v1", "stop"), (0, "u1", "v2", "play"), (50, "u1", "v2", "stop")], V, 1),
     [("alice", 50)]),
    # pause with nothing open, double play, and a view on v3 that never stops
    (([(5, "u1", "v1", "pause"), (10, "u1", "v1", "play"), (20, "u1", "v1", "play"), (40, "u1", "v1", "pause"),
       (50, "u1", "v3", "play")], V, 3), [("alice", 30)]),
    # a video missing from the catalog is ignored
    (([(0, "u1", "v9", "play"), (500, "u1", "v9", "stop"), (0, "u1", "v4", "play"), (5, "u1", "v4", "stop")], V, 3),
     [("cara", 5)]),
    # two users on the same video at the same time
    (([(0, "u1", "v2", "play"), (5, "u2", "v2", "play"), (10, "u1", "v2", "stop"), (25, "u2", "v2", "stop")], V, 3),
     [("bob", 30)]),
    # retried duplicate rows count once
    (([(0, "u1", "v1", "play"), (0, "u1", "v1", "play"), (30, "u1", "v1", "stop"), (30, "u1", "v1", "stop")], V, 3),
     [("alice", 30)]),
    # empty log
    (([], V, 3), []),
])
# big test: the made-up log from the setup cell, top 5
check_big(f"watch_events ({len(watch_events)} rows), k = 5", lambda: top_creators(watch_events, videos, 5),
          @ANS@, limit=1.0)""".replace("@ANS@", repr(ANS2))

ex.q("Top creators by watch time from raw player events", minutes=20, level="medium",
     prompt=f"""The setup cell created two **made-up** objects:
- `watch_events`: about {round(NEV, -3)} raw player events `(ts, user_id, video_id, event)`, where `ts` is in seconds and
  `event` is `"play"`, `"pause"` or `"stop"`. The log is unsorted and messy, like a real one.
- `videos`: the catalog `video_id -> creator_id` (a few deleted videos are missing from it).

Write `top_creators(events, videos, k)` that returns the `k` creators with the most **watch time**, as a list of
`(creator_id, seconds)`, sorted by seconds (largest first), ties by `creator_id` (smallest first). Only creators with
more than 0 seconds appear. Watch time is computed per `(user_id, video_id)` pair, with the events in time order:
1. `"play"` opens a segment if none is open (a second `"play"` while one is open is ignored).
2. `"pause"` or `"stop"` closes the open segment and adds `close_ts - open_ts` seconds (ignored if nothing is open).
3. A segment still open at the end of the log is dropped (we do not know when it ended).
4. Events of videos that are not in `videos` are ignored. Exact duplicate rows must not change the result (with
   these rules they do not).

Example with `videos = {{"v1": "alice", "v2": "bob"}}`:
```
(0,  "u1", "v1", "play"), (100, "u1", "v1", "stop")
(10, "u2", "v2", "play"), (70,  "u2", "v2", "pause"), (80, "u2", "v2", "play"), (90, "u2", "v2", "stop")
-> top 2: [("alice", 100), ("bob", 70)]       (bob: 60 + 10 seconds)
```
Ask first in a real exam: can events arrive out of order (yes), what about duplicates and crashes (rules 1 to
3), and what to do on ties (rule above).""",
     stub="def top_creators(events, videos, k):\n    pass",
     tests=TESTS2,
     hint1="Signal: raw events must be turned into durations per entity, then aggregated and ranked. Pattern: "
           "**data processing: group by key, sort each group, a small state machine, then top k with a heap**.",
     hint2="""1. Group: `pairs[(user, video)].append((ts, event))`, skipping videos not in the catalog.
2. For each pair, sort by time and walk it with one variable `open_at` (None when nothing is open).
3. Add each pair's seconds to `per_creator[videos[video]]`.
4. Top k: `heapq.nsmallest(k, items, key=lambda x: (-seconds, creator))`, or sort if the number of creators is small.""",
     solution=SOL2,
     why="""Watch time only makes sense inside one viewing (one user on one video), so the events must be grouped by
that key before any arithmetic; summing per creator directly would pair a play of one user with a pause of
another. Sorting each group fixes the order of the unsorted log, and the two-state machine (open or closed) applies
rules 1 to 3 in one pass. Duplicates are harmless because a repeated play while open and a repeated pause while
closed are both ignored. The heap keeps the top k in O(C log k), which matters when there are millions of creators.

**Follow-ups the examiner may ask:**
- **SQL version**: `LEAD(ts) OVER (PARTITION BY user_id, video_id ORDER BY ts)` gives the next event; but double
  plays and orphan pauses make plain LEAD wrong, so first keep only state changes (a play after a close, a close after
  a play), then pair them.
- **Distributed**: shuffle by `(user_id, video_id)` to compute segments, then shuffle by `creator_id` to sum, then
  merge the per-worker top k lists. Taking a top k per worker before summing by creator would be wrong.
- **Real time**: a dashboard of top creators in the last hour: windowed sums per creator plus a heap; for huge
  cardinality, a Count-Min sketch with a heap of heavy hitters.
- Data quality: cap a segment at the video length or at an idle timeout, remove bots (thousands of views per hour),
  and report how many open segments were dropped (a crash rate metric).""",
     complexity="Brute force: O(C * n log n) (one scan per creator). Group, sort, sum: O(n log n) for the sorts, "
                "O(n) memory, plus O(C log k) for the top k.",
     mistakes="Summing play to pause across different users or videos. Sorting the whole log by time but not grouping. "
              "Counting an open segment up to the end of the day. Breaking ties in the wrong direction. Returning "
              "creators with 0 seconds.",
     learn=["algo-data-processing", "algo-heap", "algo-hashing"])

# ---------------------------------------------------------------- Q3 pattern drill (text)
ex.q("Rapid drill: name the method", minutes=10, level="mixed", kind="text", review=True,
     prompt="""Do not code. For each problem, say out loud in under 30 seconds: the method you would use and the
target time complexity. Write your answers as a short list, then open the solution.

1. A **sorted** list of prices and a budget: find two items whose total is exactly the budget.
2. The longest stretch of a string that contains at most 2 different characters.
3. Friendship pairs arrive one by one; after each pair, report how many separate friend groups exist.
4. A list of meetings `[start, end]`: the minimum number of rooms needed.
5. For each day's temperature, how many days until a warmer day.
6. The minimum number of coins (given denominations) to make an amount.
7. The smallest truck capacity that ships all packages, in their given order, within `D` days.
8. The shortest route from the start to the exit in a grid maze where every step costs the same.
9. All ways to split a string into pieces that are palindromes.
10. The 10 most frequent search queries in a log of 50 million rows.""",
     hint1="Look for the signal words: **sorted**, **contiguous** / **at most**, **groups that merge**, "
           "**overlapping intervals**, **next greater**, **minimum number of ways / count**, **smallest value that "
           "works**, **shortest steps, equal cost**, **all ways**, **most frequent**.",
     hint2="""Map of signals to methods: sorted + pair -> two pointers. Contiguous + at most k -> sliding window. Merging
groups over time -> union-find. Overlapping intervals at the same time -> sort + heap. Next greater element -> monotonic
stack. Optimal count over amounts -> DP. "Smallest value that works" and a yes/no check -> binary search on the
answer. Unweighted shortest path -> BFS. "All" combinations -> backtracking. Frequency + top k -> hash map + heap.""",
     solution="""| # | Method | Target complexity |
|---|---|---|
| 1 | Two pointers from both ends (sorted input); a hash set also works in O(n) | O(n) time, O(1) space |
| 2 | Variable-size sliding window with a count map | O(n) |
| 3 | Union-find with path compression and union by size; groups = n minus successful unions | almost O(1) per pair |
| 4 | Sort by start, min-heap of end times (or a sweep over +1/-1 events) | O(n log n) |
| 5 | Monotonic stack of indexes with decreasing temperatures | O(n) |
| 6 | 1D DP over amounts: `dp[a] = 1 + min(dp[a - c])` | O(amount * coins) |
| 7 | Binary search on the capacity, greedy check "how many days with this capacity?" | O(n log(sum of weights)) |
| 8 | BFS from the start (all steps cost the same) | O(rows * cols) |
| 9 | Backtracking (cut a palindrome prefix, recurse); precompute a palindrome table to speed up checks | O(n * 2^n) worst case |
| 10 | Hash map counts, then a min-heap of size 10 (on many machines: count per partition by query, then merge) | O(n + U log 10), U = distinct queries |""",
     why="In the exam, recognizing the method in the first two minutes is most of the work. If one of these "
         "took you more than 30 seconds, re-read that section of the handbook tonight (only that one).",
     learn=["algo-recognize", "cheat-algo-patterns", "cheat-big-o"])

ex.text("""---
## Checklist for the day before the exam

**Practice (at most 60 minutes):**
- Redo, from memory, the 3 problems in your mistake log that you missed most recently. No new problems today.
- Say the five-step script out loud once on any easy problem: clarify, examples, brute force, optimise, test.
- Skim the pattern cheat sheet and the Big O cheat sheet (10 minutes, no deep reading).

**Python toolkit you should type without thinking:**
- `collections`: `Counter`, `defaultdict(list)`, `deque` (`popleft`).
- `heapq`: `heappush`, `heappop`, `nsmallest`; max-heap by pushing `-x`; tuples `(priority, tie_breaker, item)`.
- `bisect.bisect_left` / `bisect_right`; `sorted(items, key=lambda x: (-x[1], x[0]))`.
- `functools.lru_cache` for memo, `sys.setrecursionlimit` or an explicit stack for deep recursion.
- `float("inf")`, `enumerate`, `zip`, list slicing, `"".join(...)`.

**Logistics:**
- Test the exam tool, camera, microphone and internet. Know how to run code in the shared editor.
- Prepare 3 questions for the examiner (team, data, how success is measured).
- Water, paper and pen on the desk.

**During the exam:**
- Clarify before coding. Say the brute force and its complexity even if you know the optimal method.
- Stuck for 5 minutes? Say what you are thinking and ask for a hint; a hint costs less than silence.
- Leave 5 minutes to test with your own small cases and edge cases (empty, one element, duplicates, very large).

**Tonight:** stop studying early, sleep 7 to 8 hours.

""" + learn_links(["cheat-exam-day", "cheat-algo-patterns", "cheat-big-o", "algo-recognize"]))

ex.save()
