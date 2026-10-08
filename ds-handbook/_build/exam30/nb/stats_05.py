import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (Exam is created inside stats_common.start)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import start, Q

# Day 5 statistics: focus CLT and standard error. Review: distributions (Q4).
ex = start(5, ["cookie", "ab"])

Q(ex, "Averages of a wild metric", minutes=7,
  prompt="`sum_gamerounds` in `cookie` is extremely skewed. Treat all players except the one 49,854-round account "
         "as the population.\n"
         "1. Print the population mean, sd and skewness.\n"
         "2. For sample sizes n = 5, 30 and 500, draw 10,000 random samples (with replacement, "
         "`rng = np.random.default_rng(0)`) and compute each sample's mean.\n"
         "3. For each n print: the sd of the 10,000 sample means, the formula `sd / sqrt(n)`, and the skewness of "
         "the sample means.\n"
         "4. What does this tell you about using a t-test or z-test on this metric?",
  stub="# cookie is loaded in the setup\npop = cookie.sum_gamerounds[cookie.sum_gamerounds < 49854].to_numpy()\n",
  hint1="Signal: 'distribution of the sample mean' for a non-normal metric. Topic: the central limit theorem "
        "and the standard error `SE = sd / sqrt(n)`.",
  hint2="1. `rng.choice(pop, size=(10_000, n))` gives 10,000 samples of size n. 2. `.mean(axis=1)` gives the "
        "sample means. 3. Compare `means.std()` with `pop.std() / np.sqrt(n)`; skewness with `st.skew(means)`.",
  solution='''pop = cookie["sum_gamerounds"][cookie["sum_gamerounds"] < 49854].to_numpy()
print(f"population: mean {pop.mean():.2f}  sd {pop.std():.1f}  skew {st.skew(pop):.1f}")
rng = np.random.default_rng(0)
for n in (5, 30, 500):
    means = rng.choice(pop, size=(10_000, n)).mean(axis=1)
    print(f"n={n:<4} sd of means {means.std():6.2f}   sd/sqrt(n) {pop.std() / np.sqrt(n):6.2f}   "
          f"skew of means {st.skew(means):.2f}")''',
  out="""population: mean 51.32  sd 102.7  skew 6.0
n=5    sd of means  45.46   sd/sqrt(n)  45.92   skew of means 2.71
n=30   sd of means  18.85   sd/sqrt(n)  18.75   skew of means 1.02
n=500  sd of means   4.64   sd/sqrt(n)   4.59   skew of means 0.23""",
  why="The SE formula `sd / sqrt(n)` is exact for any distribution with finite variance: the simulated sd of "
      "the means matches it for every n. What needs a large n is the *shape*: the CLT says the mean becomes "
      "normal, but how fast depends on the skew. Skewness of a mean shrinks like `skew / sqrt(n)`, so with a "
      "population skew of 6, n = 30 still gives means with skew about 1 (`6 / sqrt(30) = 1.1`) while n = 500 "
      "is close to normal (0.23). In a real A/B test with "
      "tens of thousands of players per arm, the normal approximation for the mean is fine; with small samples "
      "of a heavy-tailed metric it is not (use a bootstrap or a log/capped metric). The 'n = 30 is enough' "
      "rule only works for mild skew.",
  pm="A sample of 30 players gives a very shaky average for rounds played, it can easily be off by about 20 "
     "rounds; with 500 players the error shrinks to about 5 rounds and becomes predictable. Our A/B tests have "
     "tens of thousands of players, so averages are reliable there, but small pilots are not.",
  mistakes="Saying the CLT makes the *data* normal (it is about the sample mean). Quoting 'n >= 30' as a "
           "universal rule. Confusing the sd of the data (spread of players) with the SE (uncertainty of the "
           "average).",
  learn=["stats-clt-se", "stats-distributions"])

Q(ex, "How precise is our conversion rate?", minutes=6,
  prompt="Using the cleaned `ab` table (one row per user), look at the control group only.\n"
         "1. Print the conversion rate `p`, the number of users `n` and the standard error "
         "`SE = sqrt(p (1 - p) / n)`.\n"
         "2. Print the 95% margin of error `1.96 * SE`, in percentage points.\n"
         "3. How many control users would we need for an SE of 0.05 percentage points (0.0005)? How does the SE "
         "change if we only had a quarter of the users?\n\n"
         "Example: with p = 0.5 and n = 100, `SE = sqrt(0.25 / 100) = 0.05`.",
  stub="# ab is loaded and cleaned in the setup\n",
  hint1="Signal: precision of a rate. Topic: the standard error of a proportion (a binomial share), and the "
        "square-root law.",
  hint2="1. `c = ab[ab.group == 'control'].converted`; `p = c.mean()`, `n = len(c)`. 2. `se = np.sqrt(p * (1 - "
        "p) / n)`. 3. Solve `p (1 - p) / n = 0.0005**2` for n. 4. A quarter of n doubles the SE.",
  solution='''c = ab.loc[ab["group"] == "control", "converted"]
p, n = c.mean(), len(c)
se = np.sqrt(p * (1 - p) / n)
print(f"p {p:.4f}   n {n}   SE {se:.5f}")
print(f"95% margin of error: +- {100 * 1.96 * se:.2f} percentage points")
print(f"users for SE 0.0005: {p * (1 - p) / 0.0005 ** 2:,.0f}")
print(f"SE with n/4 users: {np.sqrt(p * (1 - p) / (n / 4)):.5f}  (ratio {np.sqrt(p * (1 - p) / (n / 4)) / se:.1f})")''',
  out="""p 0.1204   n 145274   SE 0.00085
95% margin of error: +- 0.17 percentage points
users for SE 0.0005: 423,574
SE with n/4 users: 0.00171  (ratio 2.0)""",
  why="A conversion flag is a 0/1 variable with variance `p (1 - p)`, so the SE of the rate is `sqrt(p (1 - p) "
      "/ n)`. The SE falls with `sqrt(n)`, not with n: 4 times the users halves the SE, and halving the SE "
      "again needs 4 times more. That is why detecting small lifts is expensive. The formula assumes "
      "independent users; it is the user that is randomised, so the unit of analysis must be the user (we "
      "cleaned duplicates for that reason).",
  pm="Our control conversion rate is 12.04%, and with 145,000 users it is precise to about plus or minus 0.17 "
     "percentage points. Making it twice as precise would need four times as many users.",
  mistakes="Using `p / sqrt(n)` or forgetting the square root. Mixing percent and fraction in the same formula. "
           "Counting page views instead of users as n when users visit many times.",
  learn=["stats-clt-se", "stats-confidence-intervals"])

Q(ex, "Sessions are not users", minutes=6, kind="text",
  prompt="A PM shows you a dashboard: *'Average session length is 6.2 minutes, with a standard error of 0.01 "
         "minutes, computed over 2 million sessions from 100,000 users.'* They plan to call any change larger "
         "than 0.03 minutes 'significant'.\n\n"
         "Explain in 4 to 6 sentences:\n"
         "1. the difference between the sd and the SE here,\n"
         "2. why this SE is probably too small, and\n"
         "3. how you would compute a correct SE.",
  hint1="Signal: many rows per user, and the SE was computed as if every row were independent. Topic: standard "
        "error and the independence assumption (clustered data, the unit of analysis).",
  hint2="1. sd = spread of session lengths; SE = uncertainty of the average. 2. `sd / sqrt(n)` assumes n "
        "independent rows; sessions from the same user are correlated. 3. Options: aggregate to one number per "
        "user, the delta method for a ratio of sums, a cluster-robust SE, or a bootstrap that resamples users.",
  solution='''**Model answer.** The sd describes how much single sessions differ from each other (some are 1 minute, some are 30). The SE describes how much the *average* would move if we repeated the measurement with new users; `SE = sd / sqrt(n)` only holds when the n rows are independent. Here the 2 million sessions come from only 100,000 users, and sessions of the same user are similar (a heavy user has many long sessions), so the effective sample size is much closer to 100,000 than to 2 million. Using n = 2,000,000 makes the SE too small, possibly by a factor of 2 to 4 or more, so the PM would call noise 'significant' far too often. A correct SE resamples or aggregates at the level of the user (the unit that was randomised or sampled): compute per-user totals and use the delta method for the ratio `total minutes / total sessions`, use a cluster-robust SE, or bootstrap by drawing users with replacement.

Quick numbers to say out loud: if each user had 20 identical sessions, the real information would be 100,000 values, and the correct SE would be `sqrt(20)`, about 4.5 times, larger than the naive one.''',
  why="The SE formula has a hidden assumption: independent observations. Whenever the analysis unit (session, "
      "page view) is smaller than the unit that varies or is randomised (user), the naive SE is too small and "
      "false positives rise. This exact trap appears in A/B exams as the 'unit of randomisation versus "
      "unit of analysis' question.",
  pm="The 0.01-minute error bar is too optimistic because it treats 2 million sessions as 2 million independent "
     "people, while they come from only 100,000 users. Once we measure the uncertainty per user, the error bar "
     "will be several times wider, so a 0.03-minute change may well be noise.",
  mistakes="Saying 'more data always means a smaller SE' without asking whether the rows are independent. "
           "Confusing sd and SE. Fixing it by dividing by the number of users while keeping the session-level "
           "sd (still wrong: use the delta method or a bootstrap over users).",
  learn=["stats-clt-se", "stats-ratio-metrics"])

Q(ex, "Support tickets per hour", minutes=5, review=True,
  prompt="Review of distributions. A support team gets 3 tickets per hour on average, arriving independently at "
         "a steady rate.\n"
         "1. What is the probability of more than 6 tickets in one hour?\n"
         "2. What is the probability of no ticket at all in the next 30 minutes?\n"
         "3. Check both with a simulation of 200,000 hours (`rng = np.random.default_rng(0)`).",
  hint1="Signal: counts of independent events in a time window at a known average rate. Topic: the Poisson "
        "distribution (and the exponential waiting time between events).",
  hint2="1. `st.poisson.sf(6, 3)` is `P(X > 6)`. 2. In 30 minutes the rate is 1.5, so `P(0) = exp(-1.5)`. "
        "3. `rng.poisson(3, 200_000)` and `rng.poisson(1.5, 200_000)`.",
  solution='''print(f"P(X > 6 in 1 hour) = {st.poisson.sf(6, 3):.4f}")
print(f"P(no ticket in 30 min) = {np.exp(-1.5):.4f}")
rng = np.random.default_rng(0)
print(f"simulated: {(rng.poisson(3, 200_000) > 6).mean():.4f} and {(rng.poisson(1.5, 200_000) == 0).mean():.4f}")''',
  out="""P(X > 6 in 1 hour) = 0.0335
P(no ticket in 30 min) = 0.2231
simulated: 0.0335 and 0.2231""",
  why="Independent arrivals at a steady rate give a Poisson count, with rate proportional to the window length "
      "(3 per hour = 1.5 per 30 minutes). `P(0) = exp(-rate)` is also the probability that the exponential "
      "waiting time to the next ticket is longer than 30 minutes. The model only holds when the rate is steady; "
      "real tickets come in bursts after an outage (overdispersion), so the true tail is fatter than this.",
  pm="In a normal hour, more than 6 tickets happens only about 3% of the time, so a 7-ticket hour is a signal "
     "worth checking. There is about a 22% chance of a quiet half hour with no tickets.",
  mistakes="`st.poisson.sf(7, 3)` (that is P(X > 7)). Forgetting to rescale the rate for a 30-minute window. "
           "Applying Poisson to bursty data without checking variance against the mean.",
  learn=["stats-distributions"])

ex.save()
