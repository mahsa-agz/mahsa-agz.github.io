import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats_hard_common import start, shown, hidden_setup, PM, MOCK_INTRO

# Day 28 stats MOCK. Review topics: metric-drop, launch-decisions, network-effects, probability-puzzles,
# bayesian-sequential, heterogeneous-effects. 5 questions, 30 minutes, one short case (Q5).

SETUP = '''rng = np.random.default_rng(28)'''

HIDDEN = '''_r = np.random.default_rng(2028)
_country = {"US": 0.40, "UK": 0.25, "DE": 0.20, "FR": 0.15}
_pay = {"US": (0.65, 0.20, 0.15), "UK": (0.60, 0.25, 0.15), "DE": (0.35, 0.50, 0.15), "FR": (0.60, 0.25, 0.15)}
_plat = {"US": (0.42, 0.33, 0.25), "UK": (0.42, 0.33, 0.25), "DE": (0.30, 0.35, 0.35), "FR": (0.40, 0.35, 0.25)}
_base = {"card": 0.72, "paypal": 0.70, "wallet": 0.80}
_padj = {"iOS": 0.02, "Android": 0.0, "Web": -0.05}
_rows = []
for _d in pd.date_range("2026-09-14", "2026-10-11"):
    _tot = 100_000 * (1.15 if _d.dayofweek >= 5 else 1.0)
    for _c, _cs in _country.items():
        for _p, _ps in zip(("iOS", "Android", "Web"), _plat[_c]):
            for _m, _ms in zip(("card", "paypal", "wallet"), _pay[_c]):
                if _p == "Web" and _m == "wallet":
                    continue
                _n = _r.poisson(_tot * _cs * _ps * _ms)
                _rate = _base[_m] + _padj[_p]
                if _c == "DE" and _p == "Web" and _m == "paypal" and _d >= pd.Timestamp("2026-10-06"):
                    _rate = 0.25
                _rows.append((_d, _c, _p, _m, _n, _r.binomial(_n, _rate)))
checkout = pd.DataFrame(_rows, columns=["date", "country", "platform", "payment", "starts", "purchases"])
print(checkout.shape)'''

DATA = """| Table | One row = | Columns | Real or simulated |
|---|---|---|---|
| `checkout` | one day x country x platform x payment method of an online shop | `date`, `country` (US/UK/DE/FR), `platform` (iOS/Android/Web), `payment` (card/paypal/wallet), `starts` (checkouts started), `purchases` | made up, built by the hidden cell (do not read it) |

The other questions need no data (puzzles and cases) or create small numbers in the prompt."""

ex = start(28, intro=MOCK_INTRO, extra=SETUP, data_doc=DATA)
hidden_setup(ex, "Build the checkout table (hidden)", HIDDEN)

# ---------------------------------------------------------------- Q1 metric drop drill-down
q1 = '''checkout["period"] = np.where(checkout.date >= "2026-10-06", "after",
                              np.where(checkout.date.between("2026-09-29", "2026-10-04"), "before", "other"))
d = checkout[checkout.period != "other"]
o = checkout.groupby("date")[["starts", "purchases"]].sum()
print((o.purchases / o.starts).loc["2026-10-02":"2026-10-08"].round(4).rename(lambda x: x.strftime("%b %d")).to_dict())

def cut(dims):
    g = d.groupby(dims + ["period"])[["starts", "purchases"]].sum().unstack("period")
    tot = d.groupby("period").starts.sum()
    t = pd.DataFrame({"conv_before": g.purchases.before / g.starts.before, "conv_after": g.purchases.after / g.starts.after})
    t["contribution"] = g.purchases.after / tot.after - g.purchases.before / tot.before
    return t.round(4).sort_values("contribution")

tb = d.groupby("period")[["starts", "purchases"]].sum()
print(f"overall: {tb.purchases.before / tb.starts.before:.4f} -> {tb.purchases.after / tb.starts.after:.4f}")
for dim in (["country"], ["platform"], ["payment"]):
    print(cut(dim).head(2))
print(cut(["country", "platform", "payment"]).head(3))
seg = d[(d.country == "DE") & (d.platform == "Web") & (d.payment == "paypal") & (d.period == "after")]
print(f"lost orders per day: {seg.starts.sum() / seg.date.nunique() * (0.6523 - 0.2503):.0f}")
# {'Oct 02': 0.7226, 'Oct 03': 0.7193, 'Oct 04': 0.7201, 'Oct 05': 0.7206, 'Oct 06': 0.7044, 'Oct 07': 0.7016, 'Oct 08': 0.7066}
# overall: 0.7206 -> 0.7044
# worst country DE (0.7086 -> 0.6349, contribution -0.0145), worst platform Web (-0.0150), worst payment paypal (-0.0146)
# DE / Web / paypal: 0.6523 -> 0.2503, contribution -0.0147 of the total -0.0162; next segment only -0.0009
# lost orders per day: 1478'''
ex.q("Checkout conversion slipped", minutes=8, kind="python",
     prompt="The shop's checkout conversion (`purchases / starts`) dropped by about 1.6 points (from about 72% to about 70.4%) "
            "starting on a Tuesday in early October. Use `checkout` (made up; do not read the hidden cell).\n\n"
            "1. Find the first day of the drop.\n"
            "2. Compare the 6 days before (Sep 29 to Oct 4) with the days after the start. Cut by country, platform "
            "and payment method, with contributions that add up to the total change.\n"
            "3. Each single cut points somewhere. Find the real cause and say how sure you are." +
            PM + "what broke and what to do.",
     hint1="Signal: a ratio metric drops suddenly; several single cuts each show a partial drop. Method: "
           "metric-drop drill-down: one-dimensional cuts, then the intersection of the suspicious segments.",
     hint2="1. Daily conversion. 2. `contribution = purchases_after / starts_after_total - purchases_before / "
           "starts_before_total` per segment. 3. If DE, Web and PayPal each drop, cut by all three together.",
     solution=q1,
     why="The drop is a step on Tuesday Oct 6, not a trend, which points to a release or an outage. Each single "
         "cut shows DE, Web and PayPal as the worst segments, but each one only partly: the cross cut shows one "
         "combination, PayPal on Web in Germany, falling from about 65% to 25% and explaining almost all of the "
         "1.6-point overall drop (-0.0147 of -0.0162), while every other combination is flat. A sudden step in one payment method on "
         "one platform in one country looks like a payment integration failure (for example a PayPal redirect or "
         "a German locale setting on the web checkout), not user behaviour." + PM + "\"Checkout conversion is "
         "down 1.6 points since Tuesday because PayPal on our German website fails: its conversion fell from 65% "
         "to 25% while everything else is unchanged; payments engineering should check the PayPal web "
         "integration for Germany now, and we lose roughly 1,500 orders a day until it is fixed.\"",
     mistakes="Stopping at the first single cut (blaming Germany or the web). Comparing a period with weekends "
              "to one without (the windows here are both full weeks of days). Averaging segment rates instead of "
              "using sums.",
     learn=["stats-metric-drop"])
shown(ex)

# ---------------------------------------------------------------- Q2 probability puzzle
q2 = '''from math import factorial, e
formula = sum(1 / factorial(n) for n in range(0, 30))    # E[N] = sum over n >= 0 of P(N > n) = sum 1/n!
u = rng.random((200_000, 12)).cumsum(axis=1)              # 12 draws are enough: P(N > 12) = 1/12! is tiny
n_draws = (u <= 1).sum(axis=1) + 1
print(f"formula {formula:.4f}, e = {e:.4f}, simulated {n_draws.mean():.3f}")
print(f"P(N > 2) = P(U1 + U2 <= 1) = {np.mean(n_draws > 2):.3f} (exact 1/2), P(N > 3) = {np.mean(n_draws > 3):.3f} (exact 1/6)")
# formula 2.7183, e = 2.7183, simulated about 2.718
# P(N > 2) about 0.500 (exact 1/2), P(N > 3) about 0.167 (exact 1/6)'''
ex.q("Fill the bar", minutes=5, kind="python",
     prompt="A loading bar fills by a uniform random amount between 0 and 1 (of the full bar) at each step, "
            "independent of the past. On average, how many steps does it take until the bar is **more than "
            "full** (total > 1)?\n\n"
            "Give the exact answer with a short argument, then check it by simulation." +
            PM + "the answer in one sentence and why it is not 2.",
     hint1="Signal: expected number of uniform draws until the sum passes a threshold. Method: tail-sum formula "
           "`E[N] = sum P(N > n)` and the volume of a simplex.",
     hint2="1. `N > n` means the first n draws sum to at most 1. 2. That probability is the volume of "
           "`{u1 + ... + un <= 1}` in the unit cube, which is `1/n!`. 3. Sum over n >= 0.",
     solution=q2,
     why="`P(N > n) = P(U1 + ... + Un <= 1) = 1/n!` (the corner simplex of the unit cube; for n = 2 it is a "
         "triangle of area 1/2). So `E[N] = sum over n >= 0 of 1/n! = 1 + 1 + 1/2 + 1/6 + ... = e = 2.718`. "
         "The intuitive answer 2 (the mean step is 1/2) is wrong because N is the first time the sum passes 1: "
         "you always need at least 2 steps and sometimes 3 or more, and stopping times do not average that "
         "simply." + PM + "\"It takes about 2.72 steps on average, not 2: the bar always needs at least two "
         "steps, and about one time in two it needs a third or more.\"",
     mistakes="Answering 2 from `1 / E[U]`. Forgetting the n = 0 term (P(N > 0) = 1). Simulating with a fixed "
              "small number of draws that cannot reach the threshold.",
     learn=["stats-probability-puzzles"])
shown(ex)

# ---------------------------------------------------------------- Q3 Bayesian read and the day-4 trap
q3 = '''a_conv, a_n, b_conv, b_n = 120, 2400, 150, 2400
pa = rng.beta(1 + a_conv, 1 + a_n - a_conv, 400_000)
pb = rng.beta(1 + b_conv, 1 + b_n - b_conv, 400_000)
print(f"P(B > A) = {(pb > pa).mean():.3f}, expected loss of choosing B = {np.maximum(pa - pb, 0).mean():.5f}")
p0 = (a_conv + b_conv) / (a_n + b_n)
z = (b_conv / b_n - a_conv / a_n) / np.sqrt(p0 * (1 - p0) * (1 / a_n + 1 / b_n))
print(f"z = {z:.2f}, two-sided p = {2 * stats.norm.sf(z):.3f}")
# P(B > A) = 0.970, expected loss of choosing B = 0.00008 (third decimal of P moves a little with the draws)
# z = 1.88, two-sided p = 0.060'''
ex.q("97% on day 4", minutes=5, kind="python",
     prompt="Day 4 of a test planned for 14 days: A has 120 purchases out of 2,400 users, B has 150 out of 2,400.\n\n"
            "1. With Beta(1, 1) priors, compute P(B > A) and the expected loss of choosing B.\n"
            "2. Compute the classic two-proportion z-test.\n"
            "3. The PM wants to stop now. What do you say?" +
            PM + "your answer to the PM.",
     hint1="Signal: a Bayesian summary on early data and a wish to stop. Method: Beta-binomial posterior, then "
           "the optional stopping problem.",
     hint2="1. Posteriors `Beta(1 + conv, 1 + n - conv)`, sample and compare. 2. Pooled z-test. 3. Is day 4 a "
           "planned look? Weekly cycle? Size of the effect?",
     solution=q3,
     why="P(B > A) is about 0.97 while the two-sided p is 0.06: the two numbers are consistent (with flat priors "
         "P(B > A) is close to one minus the one-sided p of 0.03). The observed lift is +25% relative (5.0% to "
         "6.25%), far larger than most real effects, which is typical for small early samples and novelty. "
         "Stopping when the dashboard first shows 97% is optional stopping: it inflates false wins whether the "
         "number is Bayesian or not, and 4 days miss the weekend. Keep the plan, or use a pre-registered "
         "sequential boundary." + PM + "\"The early read is promising (97% chance B is better) but it is 4 "
         "days, no weekend, and a +25% lift that is probably inflated; stopping on good early numbers turns "
         "many duds into wins, so we finish the planned two weeks.\"",
     mistakes="Treating 97% as a guarantee of a 25% lift. Saying the Bayesian and frequentist results disagree "
              "(they mostly differ in what they report). Ignoring the weekly cycle.",
     learn=["stats-bayesian-sequential"])
shown(ex)

# ---------------------------------------------------------------- Q4 network effects (marketplace)
ex.q("Testing a seller discount", minutes=6, kind="text",
     prompt="An e-commerce marketplace inside a video app wants to test **free shipping coupons** given to "
            "buyers, paid by the platform. Sellers have limited stock, and the coupon budget is a fixed amount per "
            "day. The PM proposes a 50/50 buyer-level A/B test with GMV per buyer as the metric.\n\n"
            "1. Name two ways this design is biased, and the direction of each bias.\n"
            "2. Propose a better design and its analysis.\n"
            "3. What do you give up?" +
            PM + "why the 50/50 buyer test would overstate the gain.",
     hint1="Signal: a two-sided marketplace with shared, limited resources (stock and budget). Method: "
           "interference: market-level (cluster) randomization, switchback, or budget-split designs.",
     hint2="1. Treated buyers buy stock that control buyers would have bought. 2. The shared daily budget: "
           "who spends it? 3. Randomize markets or time, or split both supply and budget.",
     solution="""**1. Biases.** (a) **Stock cannibalization:** treated buyers, with coupons, buy limited items that
control buyers would have bought. Treatment goes up partly because control goes down, so the difference
**overstates** the net gain at full launch (some sales are only moved, not created). (b) **Shared budget:** the
daily coupon budget runs out earlier because of treated buyers. At 50% traffic it lasts part of the day; at 100% it
runs out even earlier, so the per-buyer effect at launch is smaller than measured (again **overstated**). Also
sellers may raise prices or change stock in response, which a 2-week buyer test does not capture.

**2. Better design.** Randomize at a level where supply and budget are not shared: (a) **market or region
clusters** (cities or categories with little cross-buying), with the budget scaled per cluster, analyzed at cluster
level with cluster-robust SEs; or (b) a **budget-split design**: split both buyers and the seller inventory/budget
into two independent halves so each arm has its own supply; or (c) a **switchback** by day in a market, with day
and weekday fixed effects and burn-in for carryover (stock refill). Metric: total GMV and orders per market (not per
buyer), coupon cost, platform margin, plus seller-side guardrails (stock-outs, cancellations).

**3. Cost.** Fewer independent units (wider CIs, longer tests), cluster heterogeneity, and for switchbacks, carryover
and the inability to measure long-term buyer habits. You accept this because the buyer-level test answers the wrong
question with high precision.

**Say it to a PM:** "In a buyer split, coupon users partly take items and budget away from the other half, so the test
shows a gain that is partly just moved from control; testing by whole market shows the real net gain, at the cost of
a longer test.\"""",
     why="The key points: name the shared resources, give the direction of each bias, choose a unit where the "
         "resource is not shared, and switch the metric to the market level.",
     learn=["stats-network-effects"])

# ---------------------------------------------------------------- Q5 short case
ex.q("Short case: good on average, bad for new users", minutes=6, kind="text",
     prompt="A ranking change was tested for 3 weeks. Results versus control:\n\n"
            "| Metric | All users | Existing users (85%) | New users (15%, pre-registered segment) |\n"
            "|---|---|---|---|\n"
            "| Watch time per user | +0.8% (p < 0.001) | +1.0% (p < 0.001) | -0.4% (p = 0.45) |\n"
            "| Day-7 retention | +0.1% (p = 0.60) | +0.3% (p = 0.20) | -1.5% (p = 0.03) |\n\n"
            "Should we launch? Give a decision with conditions." +
            PM + "your recommendation in two sentences.",
     hint1="Signal: an overall win with a pre-registered segment that loses on a long-term metric. Method: "
           "heterogeneous effects plus a launch decision: value of each segment, long-term impact, targeted "
           "remedies.",
     hint2="1. Is the new-user loss credible (pre-registered, p = 0.03, a plausible mechanism)? 2. New users "
           "are the future user base: compound the effect. 3. Options: launch for existing users only, fix "
           "the new-user experience, retest.",
     solution="""**Reading it.** The overall gain comes from existing users (+1.0% watch time). New users are the
pre-registered segment, so their -1.5% day-7 retention is not segment fishing; p = 0.03 is moderate evidence, and
there is a plausible mechanism: the new ranking exploits learned preferences, which new users do not have yet, so
their feed may be less diverse or less relevant. Day-7 retention of new users is a leading indicator of future DAU:
losing 1.5% of each new cohort compounds over months, while +1% watch time of existing users is a one-time level
gain.

**Decision.** Launch for existing users (for example users older than 30 days), keep the old ranking for new users,
and ask the ranking team for a cold-start fix (more exploration for new accounts). Retest the fix on new users with
day-7 and day-30 retention as primary metrics. Keep a small long-term holdout for the existing-user launch to confirm
the watch-time gain does not fade.

**Check before shipping:** the segment boundary (users who become "existing" during the test), novelty in the
existing-user gain, and that the new-user effect is not driven by one acquisition channel.

**Say it to a PM:** "The change helps existing users but likely hurts new users' retention, and new users are our
future, so let us ship it only for accounts older than 30 days and fix the new-user experience before we roll it out
to everyone.\"""",
     why="Strong answers respect the pre-registered segment, weigh long-term retention above short-term watch "
         "time, and propose a targeted launch plus a fix instead of a yes or no.",
     learn=["stats-heterogeneous-effects", "stats-launch-decisions"])

ex.save()
