import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (Exam is created inside stats_common.start)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import start, Q

# Day 4 statistics: focus distributions (binomial, Poisson, normal; when they fit and when not). Review: Bayes (Q4).
ex = start(4, ["cookie", "taxis", "penguins"])

Q(ex, "How many of 20 new players come back?", minutes=7,
  prompt="In the control group of Cookie Cats (`version == 'gate_30'`), each player either comes back on day 1 "
         "(`retention_1`) or not.\n"
         "1. Estimate `p`, the day-1 retention rate of the control group.\n"
         "2. A community manager invites groups of 20 new players. Assuming players are independent, what is the "
         "probability that at least 10 of 20 come back? What are the expected count and its sd?\n"
         "3. Check against the real data: shuffle the control players with `rng = np.random.default_rng(0)`, cut "
         "them into groups of 20, and print the share of groups with at least 10 returners, plus the mean and sd "
         "of the group counts.",
  stub="# cookie is loaded in the setup\nctrl = cookie[cookie.version == 'gate_30']\n",
  hint1="Signal: a fixed number of independent yes/no trials with the same probability. Topic: the binomial "
        "distribution `Binomial(n = 20, p)`.",
  hint2="1. `p = ctrl.retention_1.mean()`. 2. `st.binom.sf(9, 20, p)` is `P(X >= 10)` (sf(k) = P(X > k)). "
        "Mean `n p`, sd `sqrt(n p (1 - p))`. 3. `r = rng.permutation(ctrl.retention_1.to_numpy())`, cut to a "
        "multiple of 20, `reshape(-1, 20).sum(axis=1)`.",
  solution='''ctrl = cookie[cookie["version"] == "gate_30"]
p = ctrl["retention_1"].mean()
n = 20
print(f"p = {p:.4f}")
print(f"model: P(X >= 10) = {st.binom.sf(9, n, p):.3f}   mean {n * p:.2f}   sd {np.sqrt(n * p * (1 - p)):.2f}")

rng = np.random.default_rng(0)
r = rng.permutation(ctrl["retention_1"].to_numpy().astype(int))
groups = r[: len(r) // n * n].reshape(-1, n).sum(axis=1)
print(f"data:  P(X >= 10) = {(groups >= 10).mean():.3f}   mean {groups.mean():.2f}   sd {groups.std(ddof=1):.2f}"
      f"   ({len(groups)} groups)")''',
  out="""p = 0.4482
model: P(X >= 10) = 0.402   mean 8.96   sd 2.22
data:  P(X >= 10) = 0.403   mean 8.96   sd 2.20   (2235 groups)""",
  why="Each player is a Bernoulli trial with the same `p`, and a random shuffle makes the players in a group "
      "independent, so the count of returners is `Binomial(20, 0.448)`. The model and the data agree on the "
      "tail probability, the mean (`n p` = 8.96) and the sd (`sqrt(n p (1 - p))`, about 2.22). `st.binom.sf(9, "
      "...)` gives `P(X > 9) = P(X >= 10)`: an off-by-one here is the most common bug. When would the binomial "
      "fail? If the 20 players are friends who joined together, their behaviour is correlated and the real sd "
      "is larger than the binomial sd (overdispersion).",
  pm="About 45% of new players come back the next day, so in a group of 20 we expect about 9, and a group "
     "reaching 10 or more happens roughly 4 times in 10. A group of 20 with 4 or fewer returners happens only "
     "about 2% of the time, so it would be worth a look.",
  mistakes="`st.binom.sf(10, ...)` (that is `P(X >= 11)`). Using the normal approximation without a continuity "
           "correction for such a small `n`. Assuming independence for players who joined together.",
  learn=["stats-distributions"])

Q(ex, "Taxi pickups per hour", minutes=7,
  prompt="A dispatcher models the number of taxi pickups per hour as Poisson. Using `taxis` (keep March 2019 "
         "only):\n"
         "1. Count pickups in every hour of March (include hours with 0 pickups). Print the mean and the variance "
         "of the hourly counts.\n"
         "2. Under a Poisson model with that mean, what share of hours would have 0 pickups? What share do we "
         "see?\n"
         "3. Is Poisson a good model here? Why or why not?\n\n"
         "Reminder: a Poisson count has variance equal to its mean.",
  stub="# taxis is loaded in the setup (pickup is a datetime)\n",
  hint1="Signal: counts of events in fixed time windows. Topic: the Poisson distribution and its check "
        "`variance = mean` (dispersion).",
  hint2="1. `m = taxis[taxis.pickup >= '2019-03-01']`; `h = m.set_index('pickup').resample('h').size()` "
        "(resample includes empty hours). 2. `h.mean()`, `h.var()`. 3. `st.poisson.pmf(0, h.mean())` versus "
        "`(h == 0).mean()`. 4. Also look at mean and variance inside one hour of the day.",
  solution='''m = taxis[taxis["pickup"] >= "2019-03-01"]
h = m.set_index("pickup").resample("h").size()
lam = h.mean()
print(f"hours {len(h)}   mean {lam:.2f}   variance {h.var():.2f}   ratio {h.var() / lam:.2f}")
print(f"P(0 pickups): Poisson {st.poisson.pmf(0, lam):.5f}   observed {(h == 0).mean():.4f}")
by_hour = h.groupby(h.index.hour).agg(["mean", "var"])
print(f"inside one hour of the day, mean of var/mean ratios: {(by_hour['var'] / by_hour['mean']).mean():.2f}")''',
  out="""hours 744   mean 8.65   variance 26.37   ratio 3.05
P(0 pickups): Poisson 0.00018   observed 0.0457
inside one hour of the day, mean of var/mean ratios: 1.63""",
  why="A Poisson model assumes a constant rate. Taxi demand has a strong daily cycle (about 2 pickups an hour "
      "at 4 am, 13 at 7 pm in this sample), so the hourly counts are a mix of Poisson counts with different "
      "rates. A mix always has variance above its mean (here about 3 times the mean), and many more empty hours "
      "than a single Poisson predicts. Even inside one hour of the day the ratio stays above 1 (about 1.6 on average), because weekdays "
      "and weekends differ. Fixes: model the rate by hour and weekday, or use a negative binomial, which has "
      "an extra parameter for overdispersion.",
  pm="Demand is far less steady than a simple model assumes: about 5% of hours had no pickups in this sample, "
     "while the simple model says that should almost never happen. Staffing plans need to use the rate for each "
     "hour and weekday, not one average.",
  mistakes="Counting with `groupby(dt.hour)` and missing the empty hours (zeros never appear in a groupby). "
           "Accepting Poisson without checking `variance = mean`. Forgetting that this file is a sample of all "
           "trips, so the absolute counts are small.",
  learn=["stats-distributions", "stats-descriptive"])

Q(ex, "How heavy is a Gentoo penguin?", minutes=6,
  prompt="Using `penguins`, keep species Gentoo (drop missing `body_mass_g`).\n"
         "1. Print the mean and sd of body mass.\n"
         "2. Treat body mass as normal with that mean and sd. What share of Gentoo should weigh more than 6,000 g? "
         "What share actually does?\n"
         "3. Check the 68-95 rule: what share is within 1 sd and within 2 sd of the mean?\n"
         "4. A Gentoo weighs 6,300 g. What is its z-score?",
  stub="# penguins is loaded in the setup\n",
  hint1="Signal: a continuous measurement, symmetric, from one homogeneous group. Topic: the normal distribution, "
        "z-scores and the 68-95-99.7 rule.",
  hint2="1. `g = penguins.loc[penguins.species == 'Gentoo', 'body_mass_g'].dropna()`. 2. "
        "`st.norm.sf(6000, mu, sd)` versus `(g > 6000).mean()`. 3. `(abs(g - mu) < sd).mean()`. 4. "
        "`z = (6300 - mu) / sd`.",
  solution='''g = penguins.loc[penguins["species"] == "Gentoo", "body_mass_g"].dropna()
mu, sd = g.mean(), g.std()
print(f"n {len(g)}   mean {mu:.0f} g   sd {sd:.0f} g")
print(f"P(mass > 6000): normal {st.norm.sf(6000, mu, sd):.3f}   observed {(g > 6000).mean():.3f} ({(g > 6000).sum()} birds)")
print(f"within 1 sd {(abs(g - mu) < sd).mean():.3f}   within 2 sd {(abs(g - mu) < 2 * sd).mean():.3f}")
print(f"z-score of 6300 g: {(6300 - mu) / sd:.2f}")''',
  out="""n 123   mean 5076 g   sd 504 g
P(mass > 6000): normal 0.033   observed 0.016 (2 birds)
within 1 sd 0.675   within 2 sd 0.984
z-score of 6300 g: 2.43""",
  why="The 68-95 rule fits well (about 67% and 98%), so the normal model describes the middle of the data. "
      "The far tail is where it is weakest: the model says about 3% are above 6,000 g, the data has 2 birds "
      "out of 123 (1.6%). With 123 birds, a tail share is estimated from only a handful of points, so neither "
      "number is precise. Note that males and females differ, so the full mass distribution is a mix of two "
      "normals; a model by sex would fit better. A z-score of 2.43 means 6,300 g is 2.43 sd above the mean, "
      "unusual but not impossible (about 1 in 130 under the model).",
  pm="A typical Gentoo weighs about 5,080 g, and two thirds weigh within about 500 g of that. A 6,300 g bird is "
     "among the heaviest we would expect to see, roughly 1 in 130.",
  mistakes="Using the normal model for far tails or for skewed data (money, counts). Using the population sd "
           "formula by accident (`np.std` divides by n). Pooling males and females and calling the mix normal.",
  learn=["stats-distributions"])

Q(ex, "Which coin did I pick?", minutes=5, review=True,
  prompt="Review of Bayes. A bag has 2 coins: one fair and one with heads on both sides. You pick one at random "
         "and flip it 3 times: heads, heads, heads.\n"
         "1. What is the probability you picked the two-headed coin?\n"
         "2. What is the probability that the next flip is heads?\n"
         "3. Check part 1 with a simulation of 200,000 picks (`rng = np.random.default_rng(0)`).",
  hint1="Signal: 'given what you observed, which hidden case is it?'. Topic: Bayes' rule with two hypotheses, "
        "then the law of total probability for the next flip.",
  hint2="1. Prior 1/2 each. Likelihood of HHH: fair `(1/2)^3 = 1/8`, two-headed 1. 2. Posterior = "
        "`1 * 1/2 / (1 * 1/2 + 1/8 * 1/2)`. 3. Next heads = `post * 1 + (1 - post) * 1/2`. 4. Simulation: draw "
        "the coin, draw 3 flips, keep only the runs with 3 heads.",
  solution='''post = (1 * 0.5) / (1 * 0.5 + (1 / 8) * 0.5)
print(f"P(two-headed | HHH) = {post:.4f}   P(next is heads) = {post + (1 - post) * 0.5:.4f}")

rng = np.random.default_rng(0)
n = 200_000
two_headed = rng.random(n) < 0.5
p_heads = np.where(two_headed, 1.0, 0.5)
hhh = (rng.random((n, 3)) < p_heads[:, None]).all(axis=1)
print(f"simulated P(two-headed | HHH) = {two_headed[hhh].mean():.4f}   (runs kept: {hhh.sum()})")''',
  out="""P(two-headed | HHH) = 0.8889   P(next is heads) = 0.9444
simulated P(two-headed | HHH) = 0.8909   (runs kept: 112638)""",
  why="The evidence HHH is 8 times more likely under the two-headed coin (likelihood ratio 1 / (1/8) = 8). "
      "The prior odds are 1 : 1, so the posterior odds are 8 : 1, which is 8/9 = 0.889. The next flip mixes "
      "both coins with the posterior weights: `8/9 x 1 + 1/9 x 1/2 = 17/18 = 0.944`. The simulation keeps only "
      "the runs that match the evidence, which is exactly what conditioning means.",
  pm="After three heads in a row we are about 89% sure it is the trick coin, and the next flip is heads with "
     "about 94% probability. Evidence moves our belief, but the starting belief still matters.",
  mistakes="Answering 1/2 (ignoring the evidence) or 1 (ignoring the fair coin). Saying the next flip is 1/2 "
           "(the coin is uncertain, so we average over both).",
  learn=["stats-bayes", "stats-probability-puzzles"])

ex.save()
