import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_mid_common import start, q, pm

# Day 15 stats: focus ratio metrics and the delta method; review A/B pitfalls.
EXTRA = '''
# Today's tables (built from the real retail data):
# valid purchases only (no cancellations, known customer), one row per order, order revenue capped at the 99th
# percentile so a few giant wholesale orders do not dominate every number.
ok = retail.CustomerID.notna() & ~retail.InvoiceNo.str.startswith("C") & (retail.Quantity > 0) & (retail.UnitPrice > 0)
orders = (retail[ok].assign(rev=lambda d: d.Quantity * d.UnitPrice)
          .groupby(["CustomerID", "InvoiceNo"], as_index=False).rev.sum())
orders["rev"] = orders.rev.clip(upper=orders.rev.quantile(0.99))
users = orders.groupby("CustomerID").agg(rev=("rev", "sum"), n_orders=("rev", "size"))
print("orders", orders.shape, "users", users.shape)
'''
ex = start(15, ["retail", "ab", "countries"], extra=EXTRA,
           note="In Colab, if `online_retail.csv.gz` is not in your Drive data folder, upload it there (it is "
                "converted from the UCI xlsx, so there is no direct CSV link). The setup builds two tables:\n\n"
                "- `orders`: one row per order: `CustomerID`, `InvoiceNo`, `rev` (order revenue, capped at the 99th "
                "percentile).\n- `users`: one row per customer: `rev` (total revenue), `n_orders`.\n\n"
                "Think of every customer as a user in an experiment: randomisation is by customer, the metric is "
                "average order value (AOV) = total revenue / total orders.")

# ---------------------------------------------------------------- Q1
q(ex, title="The standard error of average order value", minutes=7,
  prompt="AOV is `sum(revenue) / sum(orders)` over all customers. Randomisation would be by customer, so customers "
         "(not orders) are the independent units.\n\n"
         "(a) Compute AOV.\n\n"
         "(b) 'Naive' SE: treat the 18,532 orders as independent, `sd(order revenue) / sqrt(#orders)`.\n\n"
         "(c) Delta-method SE with customers as units. With `Y` = revenue per customer, `N` = orders per customer, "
         "`R = mean(Y) / mean(N)`, n customers: "
         "`Var(R) = (var(Y) - 2 R cov(Y, N) + R^2 var(N)) / (n * mean(N)^2)`.\n\n"
         "(d) How many times larger is the delta SE? Say it to a PM.\n\n"
         "Follow-ups: when would the two SEs be about equal? Name a ratio metric where the unit of analysis is "
         "clearly not the unit of randomisation in a video app.",
  stub="Y, N = users.rev.values, users.n_orders.values\n# your code here",
  hint1="Signal: a metric that is a ratio of two sums, analysed at a finer level (orders) than the randomisation "
        "unit (customers). Method: the delta method (or a bootstrap over customers).",
  hint2="1. `R = Y.mean() / N.mean()`. 2. Naive: `orders.rev.std() / sqrt(len(orders))`. 3. Delta: use "
        "`np.var(.., ddof=1)` and `np.cov(Y, N)[0, 1]` in the formula. 4. Ratio of the two SEs.",
  solution='''Y, N = users.rev.values, users.n_orders.values

def delta_ratio(Y, N):
    """Ratio of means and its delta-method variance (units = rows of Y and N)."""
    n, mY, mN = len(Y), Y.mean(), N.mean()
    R = mY / mN
    var = (Y.var(ddof=1) - 2 * R * np.cov(Y, N)[0, 1] + R ** 2 * N.var(ddof=1)) / (n * mN ** 2)
    return R, var

R, var = delta_ratio(Y, N)
naive = orders.rev.std() / np.sqrt(len(orders))
print(f"AOV {R:.1f}, naive SE {naive:.2f}, delta SE {np.sqrt(var):.2f}, ratio {np.sqrt(var) / naive:.1f}")
# AOV 428.8, naive SE 3.95, delta SE 14.70, ratio 3.7''',
  why="Orders from the same customer are alike (a wholesaler always places big orders), so 18,532 orders carry much "
      "less independent information than their count suggests. The delta method linearises the ratio around the "
      "means and uses customer-level variances and the covariance of revenue and order count. Here the honest SE is "
      "3.7 times the naive one, so a naive test would have confidence intervals 3.7 times too narrow."
      + pm("Average order value is about 429; because big customers place many similar orders, our uncertainty is "
           "almost 4 times larger than a simple order-level calculation suggests, so we must use the customer-level "
           "method or we will declare false wins.",
           [("When are they equal?", "When orders within a customer are no more alike than orders across customers "
             "(no clustering), for example if every customer placed exactly one order."),
            ("Video app example?", "Click-through rate = clicks / impressions with users randomised; average watch "
             "time per video view; likes per session. All are ratios over a unit (impression, view, session) finer "
             "than the user.")]),
  complexity="O(number of customers) once the per-customer sums exist.",
  mistakes="Running a t-test on order-level rows. Forgetting the covariance term (Y and N are strongly correlated, "
           "and dropping it changes the answer a lot). Using population variance in one place and sample variance in "
           "another (minor).",
  learn=["stats-ratio-metrics"])

# ---------------------------------------------------------------- Q2
q(ex, title="Prove it: 1,000 fake experiments", minutes=7,
  prompt="Run 1,000 A/A tests: each time, assign every customer to A or B at random (50/50, seed 0) and test the "
         "difference in AOV with (i) the naive order-level z-test and (ii) the delta-method z-test "
         "`z = (R_A - R_B) / sqrt(Var(R_A) + Var(R_B))`.\n\n"
         "(a) What share of A/A tests is 'significant' at 0.05 for each method?\n\n"
         "(b) Say it to a PM.\n\n"
         "Follow-up: what other method gives a correct SE here without any formula?",
  stub="rng = np.random.default_rng(0)\n# your code here",
  hint1="Signal: check a variance formula by simulation. Method: A/A tests with random splits of the real units; a "
        "correct test is 'significant' about 5% of the time.",
  hint2="1. Map each order to its customer's position. 2. Each run: `g = rng.integers(0, 2, n_users).astype(bool)`. "
        "3. Delta: `delta_ratio` on each half. 4. Naive: order revenues of each half, Welch-style z. "
        "5. Count |z| > 1.96.",
  solution='''def delta_ratio(Y, N):
    n, mY, mN = len(Y), Y.mean(), N.mean()
    R = mY / mN
    return R, (Y.var(ddof=1) - 2 * R * np.cov(Y, N)[0, 1] + R ** 2 * N.var(ddof=1)) / (n * mN ** 2)

rng = np.random.default_rng(0)
Y, N = users.rev.values, users.n_orders.values
pos = orders.CustomerID.map(pd.Series(np.arange(len(users)), index=users.index)).values
o_rev = orders.rev.values
hits_naive = hits_delta = 0
sims = 1000
for _ in range(sims):
    g = rng.integers(0, 2, len(users)).astype(bool)
    Ra, va = delta_ratio(Y[g], N[g])
    Rb, vb = delta_ratio(Y[~g], N[~g])
    hits_delta += abs(Ra - Rb) / np.sqrt(va + vb) > 1.96
    a, b = o_rev[g[pos]], o_rev[~g[pos]]
    z = (a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    hits_naive += abs(z) > 1.96
print("false positive rate naive:", hits_naive / sims, " delta:", hits_delta / sims)
# false positive rate naive: 0.611  delta: 0.051''',
  why="A correct 5% test should flag about 5% of A/A splits. The naive order-level test flags 61% of them, because its SE is about 3.7 times too small, so `|z|` is inflated by the same factor. The delta "
      "method lands at 5.1%."
      + pm("When we pretend orders are independent, more than half of experiments with no real change would look "
           "like wins; with the customer-level method about 1 in 20 does, which is what we promise.",
           [("Without a formula?", "A bootstrap that resamples *customers* (with all their orders), recomputing AOV "
             "each time. Or compute per-customer AOV contributions and use a cluster-robust regression of order "
             "revenue on treatment with customer clusters, which gives the same answer as the delta method.")]),
  complexity="O(sims * n_orders), a few seconds for 1,000 runs.",
  mistakes="Resampling orders instead of customers in a bootstrap (same mistake as the naive test). Too few A/A runs "
           "to see the rate (with 1,000 runs the 5% estimate has a standard error of about 0.7 pp).",
  learn=["stats-ratio-metrics", "stats-ab-pitfalls"])

# ---------------------------------------------------------------- Q3
q(ex, title="Which average order value?", minutes=6,
  prompt="(a) Compute two versions of 'average order value': the ratio of sums `sum(rev) / sum(orders)` and the "
         "mean of per-customer ratios `mean(rev_i / orders_i)`. Why do they differ?\n\n"
         "(b) A treatment adds free shipping on small orders. Toy numbers (made up): in control each user places 2 "
         "orders of 50; in treatment each user places the same 2 orders plus one extra order of 20. Compute AOV and "
         "revenue per user in each arm.\n\n"
         "(c) Say it to a PM: which metric should decide the launch?",
  stub="# your code here",
  hint1="Signal: an average of ratios vs a ratio of totals, and a denominator the treatment can change. Concept: "
        "ratio metric definition and denominator shift.",
  hint2="1. `users.rev.sum() / users.n_orders.sum()` vs `(users.rev / users.n_orders).mean()`. "
        "2. Toy: AOV = revenue / orders per arm; revenue per user = revenue / users.",
  solution='''ratio_of_sums = users.rev.sum() / users.n_orders.sum()
mean_of_ratios = (users.rev / users.n_orders).mean()
print(f"ratio of sums {ratio_of_sums:.1f}, mean of ratios {mean_of_ratios:.1f}")
# ratio of sums 428.8, mean of ratios 371.2

# toy: 1 user per arm is enough to see it
aov_c, rpu_c = (50 + 50) / 2, 50 + 50
aov_t, rpu_t = (50 + 50 + 20) / 3, 50 + 50 + 20
print(f"control AOV {aov_c:.0f}, revenue/user {rpu_c}; treatment AOV {aov_t:.0f}, revenue/user {rpu_t}")
# control AOV 50, revenue/user 100; treatment AOV 40, revenue/user 120''',
  why="The ratio of sums weights each customer by their number of orders, so frequent buyers (who here place larger "
      "orders) count more; the mean of ratios gives every customer one vote. Neither is wrong, but they answer "
      "different questions: 'the typical order' vs 'the typical customer's basket'. In the toy case AOV drops 20% "
      "while revenue per user rises 20%: the treatment changed the denominator (more, smaller orders), so AOV alone "
      "would kill a good feature."
      + pm("Average order value went down because people added small extra orders, but each user spends 20% more, "
           "so we should judge the launch on revenue per user and keep AOV as a diagnostic.",
           [("Rule of thumb", "Pick as the decision metric a per-randomisation-unit metric (revenue per user). Use "
             "ratio metrics such as AOV or CTR to explain *why*, and always check whether the treatment moved the "
             "denominator (orders, impressions) first.")]),
  complexity="O(n).",
  mistakes="Mixing the two definitions between dashboards. Declaring a loss because AOV fell when the number of "
           "orders rose.",
  learn=["stats-ratio-metrics", "stats-product-metrics"])

# ---------------------------------------------------------------- Q4 review
q(ex, title="The UK looks different", minutes=6, review=True,
  prompt="Join the cleaned `ab` table (drop group/page mismatches, keep the first row per user) with `countries`. "
         "A stakeholder wants the landing page result by country.\n\n"
         "(a) For each country: conversion in each arm, difference, and the two-proportion z-test p-value.\n\n"
         "(b) Is any country significant after a Bonferroni correction for 3 tests? Note which country has a "
         "positive difference.\n\n"
         "(c) Say it to a PM who wants to launch the new page in the UK only.",
  stub="ok = (ab.group == \"treatment\") == (ab.landing_page == \"new_page\")\n"
       "clean = ab[ok].sort_values(\"timestamp\").drop_duplicates(\"user_id\").merge(countries, on=\"user_id\")\n"
       "# your code here",
  hint1="Signal: one test sliced into segments after the fact. Pitfall: multiple testing and post-hoc segment "
        "picking. Correct alpha (Bonferroni 0.05/3) and look at the CIs.",
  hint2="1. `groupby(['country', 'group']).converted.agg(['sum', 'count'])`. 2. z-test per country. 3. Compare each "
        "p with 0.05/3 = 0.0167.",
  solution='''ok = (ab.group == "treatment") == (ab.landing_page == "new_page")
clean = ab[ok].sort_values("timestamp").drop_duplicates("user_id").merge(countries, on="user_id")
for country, d in clean.groupby("country"):
    g = d.groupby("group").converted.agg(["sum", "count"])
    x_c, n_c = g.loc["control"]
    x_t, n_t = g.loc["treatment"]
    pool = (x_c + x_t) / (n_c + n_t)
    diff = x_t / n_t - x_c / n_c
    z = diff / np.sqrt(pool * (1 - pool) * (1 / n_c + 1 / n_t))
    print(f"{country}: control {x_c / n_c:.4f}, treatment {x_t / n_t:.4f}, diff {diff * 100:+.2f} pp, "
          f"p {2 * stats.norm.sf(abs(z)):.3f}")
# CA: control 0.1188, treatment 0.1119, diff -0.69 pp, p 0.195
# UK: control 0.1200, treatment 0.1212, diff +0.11 pp, p 0.635
# US: control 0.1206, treatment 0.1185, diff -0.22 pp, p 0.132''',
  why="No country is significant even before correction (all p > 0.13), and none comes close to 0.0167. The UK "
      "is the only country with a positive difference (+0.11 pp, p = 0.64), which is what you expect by chance "
      "when slicing 3 ways. Heterogeneity should be tested directly (an interaction term), not by eyeballing "
      "separate p-values."
      + pm("No country shows a real effect; the UK's small plus is well within noise, so a UK-only launch would be "
           "based on luck. If we believe the UK is different, we should run a new test there with that hypothesis "
           "written down first.",
           [("How to test 'UK is different'?", "Logistic regression `converted ~ treatment * country` and test the "
             "interaction terms jointly, or a chi-square test of homogeneity of the effects. Plan segments before the "
             "test.")]),
  complexity="O(n log n) for the sort and merge.",
  mistakes="Comparing p-values between segments ('UK p = 0.64 vs US p = 0.13, so the effect differs'): a difference "
           "in significance is not a significant difference.",
  learn=["stats-ab-pitfalls", "stats-heterogeneous-effects"])

ex.save()
