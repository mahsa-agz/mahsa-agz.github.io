import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats_hard_common import start, shown, hidden_setup, PM

# Day 24 stats. Focus: network-effects (cluster randomization, switchback). Review: launch-decisions.
# No real dataset has interference by design, so all data today is simulated (said in the notebook).

HIDDEN = '''# Q1: a messaging feature randomized by community (cluster), made up
rng = np.random.default_rng(24)
_K = 120
_sizes = rng.integers(20, 81, _K)
_ct = rng.permutation(np.r_[np.ones(_K // 2), np.zeros(_K // 2)]).astype(int)
_ce = rng.normal(0, 1.6, _K)
_rows = []
for _k in range(_K):
    for _v in 10 + _ce[_k] + 0.6 * _ct[_k] + rng.normal(0, 6, _sizes[_k]):
        _rows.append((_k, "treatment" if _ct[_k] else "control", round(max(_v, 0), 1)))
net = pd.DataFrame(_rows, columns=["cluster_id", "group", "messages"])

# Q2: switchback test of a dispatch algorithm in one city, made up (2-hour blocks, 14 days)
rng = np.random.default_rng(255)
_bt = rng.integers(0, 2, 14 * 12)
_h = np.arange(14 * 24)
_hod, _day, _blk = _h % 24, _h // 24, _h // 2
_tr, _first, _prev = _bt[_blk], _h % 2 == 0, np.r_[0, _bt[:-1]][_blk]
_base = 6 + 2.5 * np.sin((_hod - 8) / 24 * 2 * np.pi) + rng.normal(0, 0.5, 14)[_day]
_eff = np.where(_tr == 1, np.where(_first & (_prev == 0), -0.2, -0.6), np.where(_first & (_prev == 1), -0.4, 0.0))
sw = pd.DataFrame({"hour": _h, "day": _day, "hour_of_day": _hod, "block": _blk, "treated": _tr,
                   "wait_min": (_base + _eff + rng.normal(0, 0.6, len(_h))).round(2)})

# Q4: daily lift of a feed redesign over 4 weeks, made up
rng = np.random.default_rng(2404)
_t = np.arange(1, 29)
lift = pd.DataFrame({"day": _t, "lift": (0.005 + 0.04 * np.exp(-(_t - 1) / 4) + rng.normal(0, 0.004, 28)).round(4),
                     "se": 0.004})
print(net.shape, sw.shape, lift.shape)'''

DATA = """All data today is **simulated** (made up): no public dataset has interference built in. The hidden cell builds:

| Table | One row = | Columns |
|---|---|---|
| `net` | one user; a messaging feature was randomized by **community** (`cluster_id`, 120 communities of 20 to 80 users) | `cluster_id`, `group`, `messages` (messages sent in the test week) |
| `sw` | one hour in one city; a new dispatch algorithm was switched on or off in random 2-hour blocks for 14 days | `hour` (0 to 335), `day`, `hour_of_day`, `block` (2-hour block id), `treated` (0/1), `wait_min` (average rider wait) |
| `lift` | one day of a 4-week user-level test of a feed redesign | `day` (1 = launch day), `lift` (relative lift in sessions per user), `se` (its standard error) |"""

ex = start(24, data_doc=DATA)
hidden_setup(ex, "Build today's simulated data (hidden)", HIDDEN)

# ---------------------------------------------------------------- Q1 cluster randomization
q1 = '''c, t = net[net.group == "control"].messages, net[net.group == "treatment"].messages
d = t.mean() - c.mean()
se_naive = np.sqrt(c.var() / len(c) + t.var() / len(t))
print(f"diff {d:.3f}, naive SE {se_naive:.3f}, naive z {d / se_naive:.2f}")

cm = net.groupby(["cluster_id", "group"]).messages.mean().reset_index()      # one row per cluster
tt = stats.ttest_ind(cm[cm.group == "treatment"].messages, cm[cm.group == "control"].messages)
print(f"cluster-level t-test: t = {tt.statistic:.2f}, p = {tt.pvalue:.3f}")

m = smf.ols("messages ~ C(group)", net).fit(cov_type="cluster", cov_kwds={"groups": net.cluster_id})
print(f"cluster-robust SE {m.bse.iloc[1]:.3f}, p = {m.pvalues.iloc[1]:.3f}")

g = net.groupby("cluster_id").messages
n, k, ni = len(net), g.ngroups, g.size()
msb = (ni * (g.mean() - net.messages.mean()) ** 2).sum() / (k - 1)
msw = ((net.messages - g.transform("mean")) ** 2).sum() / (n - k)
m0 = (n - (ni ** 2).sum() / n) / (k - 1)
icc = (msb - msw) / (msb + (m0 - 1) * msw)
deff = 1 + (ni.mean() - 1) * icc
print(f"ICC {icc:.3f}, mean cluster size {ni.mean():.1f}, design effect {deff:.2f}, effective n {n / deff:.0f} of {n}")
# diff 0.564, naive SE 0.151, naive z 3.74
# cluster-level t-test: t = 2.10, p = 0.038
# cluster-robust SE 0.321, p = 0.079
# ICC 0.067, mean cluster size 50.9, design effect 4.35, effective n 1403 of 6107'''
ex.q("Randomized by community", minutes=7, kind="python",
     prompt="A group-messaging feature only works if your friends have it too, so the team randomized whole "
            "**communities** (`cluster_id`) instead of users: 60 communities got it, 60 did not (`net`, simulated).\n\n"
            "1. A colleague ran a user-level t-test and reports z = 3.7. Reproduce it.\n"
            "2. Analyze at the level of the randomization: a cluster-level test and a regression with "
            "cluster-robust standard errors.\n"
            "3. Estimate the intra-cluster correlation (ICC) and the design effect `1 + (m - 1) * ICC`. How many "
            "independent users is this test worth?\n\n"
            "Example: with ICC 0.02 and clusters of 100 users, the design effect is `1 + 99 x 0.02 = 2.98`, so "
            "10,000 users count like about 3,356." +
            PM + "is the feature's lift proven?",
     hint1="Signal: the unit of randomization (community) is bigger than the unit of analysis (user), and users "
           "in a community resemble each other. Method: cluster-randomized analysis (cluster-level or "
           "cluster-robust inference) and the design effect.",
     hint2="1. Welch SE on users. 2. Average per cluster, then a t-test on 120 cluster means; or `smf.ols(...)"
           ".fit(cov_type='cluster', cov_kwds={'groups': net.cluster_id})`. 3. ICC from one-way ANOVA: "
           "`(MSB - MSW) / (MSB + (m0 - 1) MSW)`.",
     solution=q1,
     why="Users in the same community share friends, culture and activity level, so they are not independent: "
         "the ICC is about 0.07, and with about 51 users per community the variance is 4.35 times what the "
         "user-level formula assumes. 6,107 users carry the information of about 1,400 independent ones. The "
         "honest SE (0.32) is about twice the naive one (0.15), so z drops from 3.7 to about 1.8 "
         "(cluster-robust, p = 0.079) or 2.1 on the 120 cluster means (p = 0.038, which weights every community "
         "equally and answers a slightly different question). The evidence is borderline, not strong. Clustering "
         "is the price we pay for measuring the feature with its network effect included; plan it with the "
         "design effect at the power stage (more clusters help far more than bigger clusters)." + PM +
         "\"Communities with the feature sent about 0.56 more messages per user (about 6%), but because we could "
         "only randomize 120 communities the evidence is borderline; I would extend the test to more communities "
         "before we call it a win.\"",
     mistakes="Analyzing a cluster-randomized test as if users were randomized (too many false wins). Thinking "
              "more users per cluster fixes power (the design effect grows with cluster size). Too few clusters "
              "(cluster-robust SEs are unreliable with fewer than about 30 to 50 clusters).",
     learn=["stats-network-effects", "stats-clt-se"])
shown(ex)

# ---------------------------------------------------------------- Q2 switchback
q2 = '''naive = sw.groupby("treated").wait_min.mean()
print(f"naive difference {naive[1] - naive[0]:+.3f}")
print(sw.groupby("treated").hour_of_day.apply(lambda h: h.between(7, 10).mean()).round(3).to_dict())   # rush share

fe = smf.ols("wait_min ~ treated + C(hour_of_day) + C(day)", sw).fit(cov_type="cluster", cov_kwds={"groups": sw.block})
print(f"with hour and day fixed effects: {fe.params['treated']:+.3f} (SE {fe.bse['treated']:.3f})")

sw["first_hour"] = (sw.hour % 2 == 0).astype(int)
sw["switched"] = (sw.treated != sw.treated.shift(2)).astype(int)        # previous block had the other arm
print(sw[sw.switched == 1].groupby(["treated", "first_hour"]).wait_min.mean().unstack().round(2))

later = sw[sw.first_hour == 0]                                          # burn-in: drop the first hour of each block
bi = smf.ols("wait_min ~ treated + C(hour_of_day) + C(day)", later).fit(cov_type="cluster",
                                                                        cov_kwds={"groups": later.block})
lo, hi = bi.conf_int().loc["treated"]
print(f"burn-in estimate {bi.params['treated']:+.3f}, 95% CI [{lo:+.3f}, {hi:+.3f}]")
# naive difference -0.041
# {0: 0.133, 1: 0.205}
# with hour and day fixed effects: -0.416 (SE 0.072)
# first_hour     0     1        (blocks right after a switch)
# treated
# 0           5.85  5.68        control: the first hour still benefits from the new algorithm
# 1           5.49  5.66        treated: the first hour is not fully treated yet
# burn-in estimate -0.589, 95% CI [-0.796, -0.383]'''
ex.q("Switching the algorithm on and off", minutes=8, kind="python",
     prompt="A ride-hailing app tests a new dispatch algorithm. Riders and drivers in one city share one supply, "
            "so a rider-level A/B test would leak (treated riders take drivers from control riders). Instead the "
            "whole city was switched between old and new algorithm in random **2-hour blocks** for 14 days (`sw`, "
            "simulated). Drivers need some time to reposition after a switch.\n\n"
            "1. Compute the naive difference in mean wait time (treated minus control). Why might it be wrong?\n"
            "2. Estimate the effect with hour-of-day and day fixed effects and standard errors clustered by block.\n"
            "3. Look for carryover: compare the first and second hour of blocks that follow a switch. Then "
            "re-estimate using only the second hour of each block.\n"
            "4. Which estimate do you report?" +
            PM + "how much does the new algorithm cut waits?",
     hint1="Signal: one shared marketplace, randomization over time, and an effect that lingers after a switch. "
           "Method: switchback experiment analysis: time fixed effects, block-level inference, burn-in periods "
           "for carryover.",
     hint2="1. Rush hours have long waits; check that both arms got the same share of them. 2. `wait_min ~ "
           "treated + C(hour_of_day) + C(day)` clustered by `block`. 3. `first_hour = hour % 2 == 0`; a block "
           "follows a switch when the previous block had the other arm. 4. Drop first hours and refit.",
     solution=q2,
     why="Randomizing over time removes the leak between riders, but creates two new problems. (1) Chance "
         "imbalance in time: treated blocks got more morning rush hours (20.5% versus 13.3% of hours 7 to 10), "
         "which hides the effect in the naive comparison (-0.04). Hour and day fixed effects fix that. (2) "
         "Carryover: after a switch, drivers are still positioned for the previous algorithm, so the first hour of "
         "a treated block is not fully treated and the first hour of a control block still benefits. That pulls "
         "the estimate toward zero (-0.42). Dropping the first hour of each block (a burn-in) gives -0.59 minutes "
         "(CI -0.80 to -0.38); the simulated truth is -0.60. Inference must use blocks, not hours, because hours "
         "within a block share conditions. Trade-off: longer blocks mean less carryover but fewer blocks and "
         "less power." + PM + "\"Once drivers have adjusted, the new algorithm cuts the average wait by about 0.6 "
         "minutes (between 0.4 and 0.8); the first quick read showed almost nothing because the new algorithm "
         "happened to run in more rush hours.\"",
     mistakes="Treating 336 hours as independent observations. Ignoring time-of-day imbalance. Reporting the "
              "estimate that includes the transition hours. Choosing blocks shorter than the carryover time.",
     learn=["stats-network-effects", "stats-regression"])
shown(ex)

# ---------------------------------------------------------------- Q3 design case
ex.q("Designing a test for a sharing feature", minutes=6, kind="text",
     prompt="A short-video app wants to test a new **\"send to friends\"** sheet that makes sharing a video by "
            "direct message much easier. Success means more shares, more conversations and more sessions started "
            "by a shared link.\n\n"
            "1. Why is a plain user-level A/B test biased here, and in which direction?\n"
            "2. Propose a design, the unit, how you would form the units, and the main metrics.\n"
            "3. How would you measure the spillover itself?\n"
            "4. What do you lose with your design, and how do you decide whether that is acceptable?" +
            PM + "explain why the test takes longer or needs more users than usual.",
     hint1="Signal: the treatment of one user changes the outcome of others (friends receive shares). Method: "
           "network interference: cluster (graph) randomization or ego-network designs, and a two-level design "
           "to measure spillover.",
     hint2="1. Control users receive shares from treated friends (their outcome goes up) and treated users "
           "send to friends who cannot reply in the new way. 2. Cluster the friendship graph into communities "
           "and randomize communities. 3. Vary the treated share across clusters. 4. Fewer units, design effect, "
           "power.",
     solution="""**1. Bias.** Treated users share more with friends, many of whom are in control. Control users
then receive more shares and start more sessions from shared links, so the control group is *contaminated upward*,
and the difference treatment minus control *underestimates* the full-launch effect (SUTVA is violated). The bias can
also go the other way for metrics like replies: a treated user's shares get fewer replies when friends lack the new
sheet.

**2. Design.** Graph cluster randomization: partition the friendship or messaging graph into communities with a
clustering algorithm (for example Louvain), keeping most edges inside communities, then randomize **communities**.
Choose clusters so that a high share of each user's messaging edges stay inside the cluster (for example over 70%).
Metrics: shares per user (primary), conversations started, sessions from shared links, and guardrails like
notification disable rate and blocks or reports. Analyze at cluster level or with cluster-robust SEs, plan power
with the design effect `1 + (m - 1) ICC`, and stratify the randomization by cluster size and activity.

**3. Spillover.** Use a two-stage design: randomly choose for each cluster a treated share (for example 0%, 50%,
100%), then randomize users inside. Comparing control users in 50% clusters with control users in 0% clusters
measures the spillover directly; comparing 100% with 0% clusters estimates the full-launch effect. Ego-network
randomization (treat a user and look at their friends) is an alternative for one-hop effects.

**4. Cost.** Far fewer independent units, so wider CIs or a longer test; imperfect clusters still leak at the edges
(bias toward zero remains, but smaller); clusters differ (country, age), so balance checks matter. It is acceptable if
the expected bias of a user-level test is larger than the precision you lose, which you can check by running both
designs at once (a user-level test inside some clusters) and comparing.

**Say it to a PM:** "Sharing spreads between friends, so if we randomize single users, the control group gets the
benefit from treated friends and the test underestimates the feature; we will randomize whole friend groups instead,
which is more accurate but needs about two to three times more time or traffic.\"""",
     why="Examiners want the direction of the bias, a concrete clustering design, a way to measure spillover, "
         "and the power trade-off stated honestly.",
     learn=["stats-network-effects", "stats-ab-design"])

# ---------------------------------------------------------------- Q4 review: novelty and launch decision
q4 = '''w1 = lift[lift.day <= 7]
w4 = lift[lift.day >= 22]
for name, w in (("week 1", w1), ("week 4", w4)):
    m, se = w.lift.mean(), np.sqrt((w.se ** 2).sum()) / len(w)
    print(f"{name}: mean lift {m:+.2%}, 95% CI [{m - 1.96 * se:+.2%}, {m + 1.96 * se:+.2%}]")

from scipy.optimize import curve_fit
f = lambda t, a, b, c: a + b * np.exp(-(t - 1) / c)
par, cov = curve_fit(f, lift.day, lift.lift, p0=[0.01, 0.03, 5], sigma=lift.se, absolute_sigma=True)
print(f"long-run lift a = {par[0]:+.2%} (SE {np.sqrt(cov[0, 0]):.2%}), first-day extra b = {par[1]:+.2%}, "
      f"decay time c = {par[2]:.1f} days")
# week 1: mean lift +2.60%, 95% CI [+2.30%, +2.89%]
# week 4: mean lift +0.52%, 95% CI [+0.23%, +0.82%]
# long-run lift a = +0.57% (SE 0.10%), first-day extra b = +4.13%, decay time c = 3.2 days'''
ex.q("The lift that faded", minutes=5, kind="python", review=True,
     prompt="A feed redesign ran for 4 weeks (`lift`, simulated: daily relative lift in sessions per user with "
            "its SE). The PM read the dashboard after week 1 and wants to launch with a forecast of \"+2.5% "
            "sessions\".\n\n"
            "1. Compare the mean lift in week 1 and week 4, each with a 95% CI (treat days as independent).\n"
            "2. Fit `lift = a + b * exp(-(day - 1) / c)` and report the long-run lift `a`.\n"
            "3. What do you tell the PM, and what extra cut would confirm that this is novelty and not a slow "
            "learning effect?" +
            PM + "the forecast you would put in the launch doc.",
     hint1="Signal: the treatment effect changes with time since exposure. Method: novelty effect check: compare "
           "early and late windows, fit the decay, forecast the long-run lift for the launch decision.",
     hint2="1. Mean of daily lifts; SE of a mean of independent estimates = `sqrt(sum(se^2)) / k`. 2. "
           "`scipy.optimize.curve_fit` with `sigma=se`. 3. New users have no old habit, so they show no novelty.",
     solution=q4,
     why="The lift falls from +2.6% in week 1 to about +0.5% in week 4, and the fitted curve says the extra "
         "early lift (+4.1% on day 1) decays with a time constant of 3.2 days (half-life about 2 days) toward a "
         "long-run lift of +0.57% (SE 0.10%). Users click on what is new and then return to their habits. A forecast based on week 1 would "
         "be about 4 to 5 times too high. To confirm novelty, cut by user tenure: new users who never saw the old "
         "design should show a flat lift over time near the long-run value; if instead the lift grows for "
         "everyone, it is learning. The launch decision should use the long-run +0.6% against the cost of the "
         "redesign." + PM + "\"The redesign adds about 0.6% sessions in the long run (not 2.5%): most of the "
         "first-week gain was curiosity that faded within about two weeks; it is still positive, so we can launch "
         "if the cost is small, with a holdout to keep measuring.\"",
     mistakes="Deciding from the first week. Averaging the whole 4 weeks and calling it the long-run effect. "
              "Confusing novelty (decay) with a learning effect (growth). Treating daily lifts as independent "
              "when the same users appear every day (the CI here is optimistic).",
     learn=["stats-launch-decisions", "stats-ab-pitfalls"])
shown(ex)

ex.save()
