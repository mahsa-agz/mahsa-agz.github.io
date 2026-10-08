import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats_hard_common import start, shown, PM

# Day 25 stats. Focus: probability-puzzles. Review: distributions, bayes.

SETUP = '''rng = np.random.default_rng(25)

def check_close(got, want, name="", tol=1e-6):
    """Prints PASS or FAIL for a numeric answer."""
    try:
        ok = abs(got - want) <= tol * max(1.0, abs(want))
    except Exception:
        ok = False
    print(("PASS " if ok else "FAIL ") + f"{name}: got {got!r}, expected {want!r}" + ("" if ok else "  <-- check"))'''

ex = start(25, extra=SETUP,
           data_doc="No dataset today: these are exam puzzles. Each answer is a formula **and** a quick "
                    "simulation that checks it. `check_close(got, want, name)` prints PASS or FAIL.")

# ---------------------------------------------------------------- Q1 pattern waiting times
q1 = '''def expected_wait(pattern, p=0.5):
    """Expected number of flips until `pattern` (a string of H/T) first appears; P(H) = p."""
    k = len(pattern)
    prob = {"H": p, "T": 1 - p}

    def next_state(s, c):                       # longest prefix of pattern that is a suffix of the text so far
        text = pattern[:s] + c
        for L in range(min(len(text), k), -1, -1):
            if text.endswith(pattern[:L]):
                return L

    # E[s] = 1 + sum_c P(c) E[next(s, c)] for s < k, E[k] = 0  ->  linear system
    A, b = np.eye(k), np.ones(k)
    for s in range(k):
        for c in "HT":
            t = next_state(s, c)
            if t < k:
                A[s, t] -= prob[c]
    return float(np.linalg.solve(A, b)[0])

def simulate(pattern, p=0.5, reps=20000):
    total = 0
    for _ in range(reps):
        s, n = "", 0
        while not s.endswith(pattern):
            s += "H" if rng.random() < p else "T"
            n += 1
        total += n
    return total / reps

print(f"HH {expected_wait('HH'):.3f} (sim {simulate('HH'):.2f}), HT {expected_wait('HT'):.3f} (sim {simulate('HT'):.2f})")
# HH 6.000 (sim about 6.0), HT 4.000 (sim about 4.0); the simulated values move a little with the random draws'''
q1_tests = '''check_close(expected_wait("HH"), 6, "HH fair")
check_close(expected_wait("HT"), 4, "HT fair")
check_close(expected_wait("HHH"), 14, "HHH fair")
check_close(expected_wait("HTH"), 10, "HTH fair")
check_close(expected_wait("HH", 0.25), 20, "HH with p = 0.25: (1 + p) / p^2")
check_close(expected_wait("HT", 0.25), 1 / (0.25 * 0.75), "HT with p = 0.25: 1 / (p(1 - p))")'''
ex.q("Two good days in a row", minutes=8, kind="python",
     stub="def expected_wait(pattern, p=0.5):\n    \"\"\"Expected number of flips until pattern (e.g. 'HH') first "
          "appears; P(H) = p.\"\"\"\n    pass\n\n# optional: a simulate(pattern, p) function that checks your answer",
     tests=q1_tests,
     prompt="A creator has a \"good day\" (H) or a \"bad day\" (T), each day independent, with P(good) = p. "
            "The app shows a badge the first time a given pattern of days appears.\n\n"
            "1. For p = 0.5, what is the expected number of days until the first **HH** (two good days in a row)? "
            "Until the first **HT** (a good day followed by a bad day)? Explain without heavy algebra why they "
            "differ although both patterns have probability 1/4.\n"
            "2. Write `expected_wait(pattern, p)` for any pattern of H and T, and check it by simulation.\n\n"
            "Example: for the one-letter pattern \"H\" with p = 0.5 the answer is 2 (a geometric distribution)." +
            PM + "explain why a 'two good days' streak takes longer than 'a good day then a bad day'.",
     hint1="Signal: 'expected number of trials until a pattern'. Method: first-step analysis on a Markov chain "
           "whose state is how much of the pattern you have matched so far.",
     hint2="1. States 0..k = length of the matched prefix. 2. `E[s] = 1 + p E[next(s, H)] + (1 - p) E[next(s, T)]`, "
           "`E[k] = 0`. 3. For HH from state 1, a T sends you back to 0; for HT from state 1, an H keeps you in 1. "
           "4. Solve the linear system with numpy.",
     solution=q1,
     why="For HT: once you have an H you never lose progress (another H still ends with H), so you wait 2 days "
         "for the first H and then 2 days for a T: 4. For HH: after an H, a T destroys all progress and you start "
         "over, so `E0 = 1 + E1/2 + E0/2` and `E1 = 1 + E0/2` give `E0 = 6`. The general formulas are "
         "`(1 + p) / p^2` for HH and `1 / (p (1 - p))` for HT. Patterns that overlap with themselves (HH, HTH, "
         "HHH) take longer, because a failure in the middle cannot be reused. Same probability per position "
         "does not mean same waiting time: occurrences of HH come in clumps." + PM +
         "\"Both patterns are equally likely on any two given days, but a failed streak of good days sends the "
         "creator back to zero, while 'good then bad' keeps its progress, so the streak badge takes 6 days on "
         "average instead of 4; if we want the badge earned in a week, the streak version is too hard for half "
         "of the creators.\"",
     complexity="Building the system is O(k^2) per state with the naive suffix check; solving is O(k^3). Fine for "
                "short patterns.",
     mistakes="Answering 4 for both because P(HH) = P(HT) = 1/4. Forgetting that after HT fails you may already "
              "hold a partial match. Simulating too few runs to separate 4 from 6.",
     learn=["stats-probability-puzzles", "stats-probability"])
shown(ex)

# ---------------------------------------------------------------- Q2 meeting problem
q2 = '''def p_meet(a, b, T=60):
    """A arrives uniformly in [0, T] and stays a minutes; B arrives uniformly in [0, T] and stays b minutes."""
    return 1 - ((T - a) ** 2 + (T - b) ** 2) / (2 * T ** 2)

x, y = rng.uniform(0, 60, (2, 200_000))
sim = np.mean((y - x <= 10) & (x - y <= 10))
print(f"p_meet(10, 10) = {p_meet(10, 10):.4f}, simulated {sim:.3f}")
print(f"p_meet(10, 20) = {p_meet(10, 20):.4f}")
# p_meet(10, 10) = 0.3056, simulated about 0.306
# p_meet(10, 20) = 0.4306'''
q2_tests = '''check_close(p_meet(10, 10), 11 / 36, "equal stays of 10 min")
check_close(p_meet(10, 20), 1 - (50**2 + 40**2) / (2 * 3600), "stays 10 and 20 min")
check_close(p_meet(0, 0), 0.0, "zero stay")
check_close(p_meet(60, 60), 1.0, "stay the whole hour")
check_close(p_meet(30, 30, T=120), 1 - (90 / 120) ** 2, "2-hour window")'''
ex.q("Do the two friends overlap?", minutes=6, kind="python",
     stub="def p_meet(a, b, T=60):\n    \"\"\"P(the two users are online at the same time).\"\"\"\n    pass",
     tests=q2_tests,
     prompt="A live-stream reminder fires at 8:00. Two friends each open the app at an independent uniform "
            "random time between 8:00 and 9:00. Friend A stays `a` minutes, friend B stays `b` minutes "
            "(they may stay past 9:00).\n\n"
            "1. With `a = b = 10`, what is the probability that they are online at the same moment?\n"
            "2. Write `p_meet(a, b, T)` for the general case and check it by simulation.\n"
            "3. What happens if B stays 20 minutes?" +
            PM + "the product team wants friends to overlap in live streams. Which lever helps more: making "
                 "people stay longer, or making them arrive within a shorter window?",
     hint1="Signal: two continuous uniform times and a condition on their difference. Method: geometric "
           "probability (area in the unit square), checked by Monte Carlo.",
     hint2="1. Draw the square [0, 60] x [0, 60] of arrival times (x, y). 2. They meet when `-b <= y - x <= a`. "
           "3. The two corners where they miss are right triangles with legs `T - a` and `T - b`. 4. Subtract "
           "their areas from 1.",
     solution=q2,
     why="They miss each other when B arrives more than `a` minutes after A, or A arrives more than `b` minutes "
         "after B. Each miss region is a right triangle in the square, of area `(T - a)^2 / 2` and "
         "`(T - b)^2 / 2`. With 10 and 10 minutes: `1 - (50/60)^2 = 11/36 = 0.3056`. If B stays 20 minutes: "
         "`1 - (2500 + 1600) / 7200 = 0.4306`. The probability depends only on stay divided by window, so halving "
         "the arrival window is like doubling both stays." + PM + "\"Two friends who each drop in for 10 minutes "
         "during an hour overlap only about 31% of the time; a reminder that gathers people into a 30-minute "
         "window raises that to about 56%, more than asking one friend to stay twice as long (43%).\"",
     complexity="O(1) formula; the simulation is O(n) with n draws.",
     mistakes="Answering 10/60 or 20/60 (ignoring that either friend can come first). Forgetting the case where "
              "the stays differ (the triangles are not equal). Truncating the stays at 9:00 without saying so "
              "(it is a different question).",
     learn=["stats-probability-puzzles", "stats-distributions"])
shown(ex)

# ---------------------------------------------------------------- Q3 coupon collector
q3 = '''def expected_videos(n):
    """Expected draws to see all n equally likely badges: n * (1 + 1/2 + ... + 1/n)."""
    return n * sum(1 / k for k in range(1, n + 1))

def expected_distinct(n, m):
    """Expected number of different badges after m draws: n * (1 - (1 - 1/n)^m)."""
    return n * (1 - (1 - 1 / n) ** m)

print(f"all 10 badges: {expected_videos(10):.2f} videos on average")
print(f"different badges after 20 videos: {expected_distinct(10, 20):.3f}")

w = np.array([0.3] + [0.7 / 9] * 9)                     # follow-up: one common badge, nine rare ones
draws = []
for _ in range(5000):
    seen, k = set(), 0
    while len(seen) < 10:
        seen.add(rng.choice(10, p=w))
        k += 1
    draws.append(k)
print(f"unequal badges, simulated mean: {np.mean(draws):.1f}")
# all 10 badges: 29.29 videos on average
# different badges after 20 videos: 8.784
# unequal badges, simulated mean: about 36.6 (exact value 36.4; the simulation moves a little)'''
q3_tests = '''check_close(expected_videos(10), 29.289682539682538, "10 badges")
check_close(expected_videos(1), 1, "1 badge")
check_close(expected_videos(2), 3, "2 badges")
check_close(expected_distinct(10, 20), 10 * (1 - 0.9 ** 20), "distinct after 20")
check_close(expected_distinct(10, 0), 0, "no draws")'''
ex.q("Collect all the stickers", minutes=6, kind="python",
     stub="def expected_videos(n):\n    pass\n\ndef expected_distinct(n, m):\n    pass", tests=q3_tests,
     prompt="A summer campaign gives one of **10** stickers after each video a user posts, each sticker equally "
            "likely and independent. The full set unlocks a prize.\n\n"
            "1. Expected number of videos to collect all 10?\n"
            "2. Expected number of **different** stickers after 20 videos?\n"
            "3. Follow-up: marketing makes one sticker common (probability 0.3) and the other nine share the "
            "rest equally. Does the full set get easier or harder? Estimate by simulation." +
            PM + "how many videos a user needs for the prize, and what the change in item 3 does.",
     hint1="Signal: 'collect all n types with random draws'. Method: coupon collector (sum of geometric waits) "
           "and linearity of expectation with indicators.",
     hint2="1. After collecting k types, a new one appears with probability `(n - k) / n`, so the wait is "
           "geometric with mean `n / (n - k)`; sum over k. 2. Indicator per sticker: P(seen) = `1 - (1 - 1/n)^m`. "
           "3. Simulate with `rng.choice(10, p=w)`.",
     solution=q3,
     why="The waits add up: `10/10 + 10/9 + ... + 10/1 = 10 x H_10 = 29.29`. The last sticker alone takes 10 "
         "videos on average, which is why sets feel slow at the end. For item 2, each sticker is missing after 20 "
         "videos with probability `0.9^20 = 0.12`, so by linearity of expectation `10 x (1 - 0.9^20) = 8.78` "
         "different stickers, with no independence needed. Making one sticker common makes the set **harder** "
         "(about 36 videos; the exact value is 36.4): the nine rare ones each have probability 0.078 instead of 0.1. Uniform probabilities "
         "minimize the expected time to collect all." + PM + "\"With equal odds a user needs about 29 videos for "
         "the full set, and the last sticker alone takes about 10; making one sticker common pushes that to "
         "about 36, so if we want more users to finish, we should guarantee a new sticker after a few repeats.\"",
     complexity="Formulas are O(n); the simulation costs about reps x expected draws.",
     mistakes="Answering 10 (one per sticker) or 20. Multiplying probabilities for item 2 instead of using "
              "indicators. Assuming that a common sticker makes the set easier.",
     learn=["stats-probability-puzzles", "stats-distributions"])
shown(ex)

# ---------------------------------------------------------------- Q4 review: Bayes for an experiment program
q4 = '''def p_real_given_win(prior, power=0.8, alpha=0.05):
    """A win = significant AND positive. A null idea wins with probability alpha / 2 (two-sided test)."""
    return prior * power / (prior * power + (1 - prior) * alpha / 2)

for prior in (0.10, 0.02):
    print(f"prior {prior:.0%}: P(real | win) = {p_real_given_win(prior):.3f}, "
          f"expected false wins in 200 tests = {200 * (1 - prior) * 0.025:.1f}, "
          f"expected true wins = {200 * prior * 0.8:.1f}")
print(f"prior 2%, alpha 0.01: {p_real_given_win(0.02, alpha=0.01):.3f}")
# prior 10%: P(real | win) = 0.780, expected false wins in 200 tests = 4.5, expected true wins = 16.0
# prior 2%: P(real | win) = 0.395, expected false wins in 200 tests = 4.9, expected true wins = 3.2
# prior 2%, alpha 0.01: 0.766'''
q4_tests = '''check_close(p_real_given_win(0.10), 0.08 / (0.08 + 0.9 * 0.025), "prior 10%")
check_close(p_real_given_win(0.02), 0.016 / (0.016 + 0.98 * 0.025), "prior 2%")
check_close(p_real_given_win(1.0), 1.0, "every idea works")
check_close(p_real_given_win(0.0), 0.0, "no idea works")'''
ex.q("How many of our wins are real?", minutes=5, kind="python", review=True,
     stub="def p_real_given_win(prior, power=0.8, alpha=0.05):\n    pass", tests=q4_tests,
     prompt="An experimentation team runs 200 A/B tests a quarter, each with 80% power for the effect it targets "
            "and a two-sided test at alpha 0.05. A **win** is a significant **positive** result.\n\n"
            "1. If 10% of ideas truly work, what fraction of wins are real? How many false and true wins per "
            "quarter?\n"
            "2. Same with 2% (typical for mature products such as a large feed).\n"
            "3. What changes if the team uses alpha 0.01 (with the same 80% power, so larger tests)?" +
            PM + "explain why some shipped wins do not show up in the long-term numbers.",
     hint1="Signal: P(hypothesis | evidence) with a base rate. Method: Bayes' rule (the false discovery rate of "
           "an experiment program).",
     hint2="1. P(win | real) = power (assume real effects are positive). 2. P(win | null) = alpha / 2 (only the "
           "positive tail counts). 3. `P(real | win) = prior x power / (prior x power + (1 - prior) x alpha/2)`.",
     solution=q4,
     why="With a 10% base rate, 78% of wins are real (16 true versus 4.5 false wins per quarter). With 2%, only "
         "about 40% are real: the 196 null ideas produce about 4.9 false wins, more than the 3.2 true wins. "
         "Lowering alpha to 0.01 raises it to about 77%, at the cost of larger tests. This is why winning effects "
         "shrink after launch (also the winner's curse: significant estimates are biased upward), and why "
         "holdouts and replication matter." + PM + "\"When few ideas truly work, a lot of 'significant' wins "
         "are luck: at our success rate maybe half of them; that is why we re-test big wins and keep a long-term "
         "holdout before we count them in the roadmap.\"",
     mistakes="Saying 'p < 0.05 means a 95% chance the effect is real'. Using alpha instead of alpha / 2 for "
              "positive wins. Forgetting that the base rate dominates when it is small.",
     learn=["stats-bayes", "stats-ab-pitfalls"])
shown(ex)

ex.save()
