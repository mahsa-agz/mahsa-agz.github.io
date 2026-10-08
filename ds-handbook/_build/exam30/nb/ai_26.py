"""Day 26 AI (hard): deployment and monitoring (focus); ML system design (review)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam  # noqa: F401
from _ai_hard_common import start, ask

SETUP = r'''from scipy import stats

def _t(name, got, want):
    good = got == want
    print(("PASS " if good else "FAIL ") + name + f" -> {got!r}" + ("" if good else f"   expected {want!r}"))

# clean sales lines: drop cancellations (InvoiceNo starting with C), returns and zero prices
lines = retail[~retail.InvoiceNo.str.startswith("C") & (retail.Quantity > 0) & (retail.UnitPrice > 0)].copy()
lines["value"] = lines.Quantity * lines.UnitPrice
lines["month"] = lines.InvoiceDate.dt.to_period("M")
lines["xmas"] = lines.Description.fillna("").str.contains("CHRISTMAS")
# one row per invoice (an order): the kind of table a model would score
inv = (lines.groupby("InvoiceNo")
       .agg(date=("InvoiceDate", "min"), value=("value", "sum"), n_lines=("StockCode", "size"))
       .reset_index())
inv["month"] = inv.date.dt.to_period("M")
REF = pd.period_range("2011-01", "2011-03", freq="M")        # the "training" period
print("lines", lines.shape, " invoices", inv.shape)'''

ex = start(26, loads=("retail",), extra=SETUP, data_note="""- `retail` (UCI Online Retail, real, 541,909 invoice
lines from a UK online gift shop, 2010-12-01 to 2011-12-09). The setup builds `lines` (sales lines only:
cancellations, returns and zero prices removed; extra columns `value`, `month`, `xmas` = the description
contains "CHRISTMAS") and `inv` (one row per invoice: `date`, `value`, `n_lines`, `month`).
- Story: a model trained on January to March 2011 data (`REF`) scores orders for the rest of the year. Is the input
data still like the training data?""")

# ------------------------------------------------------------------ Q1 PSI
ask(ex, title="Has the order value distribution moved?", minutes=7,
    prompt="""Write `psi(ref, cur, bins=10, eps=1e-4)`, the population stability index:

- bin edges = quantiles of `ref` (so each bin holds about 10% of the reference); make the outer edges
  `-inf` and `+inf` so new extreme values still land in a bin; drop duplicate edges;
- `p`, `q` = share of `ref` and `cur` in each bin, clipped below at `eps`;
- `PSI = sum((q - p) * ln(q / p))`.

Then compute the PSI of invoice `value` for each month from 2011-04 to 2011-12 against the reference months
`REF`. Common rule of thumb: below 0.1 stable, 0.1 to 0.25 moderate shift, above 0.25 major shift.
What do you conclude?""",
    stub='''def psi(ref, cur, bins=10, eps=1e-4):
    # your code here
    pass''',
    tests='''g = np.random.default_rng(0)
a, b = g.normal(0, 1, 20000), g.normal(0, 1, 20000)
_t("same distribution is near 0", (psi(a, b) or 99) < 0.01, True)
_t("shift by 0.5 sd is moderate", round(psi(a, b + 0.5) or 0, 2), 0.23)
_t("new extreme values still counted", (psi(a, b + 10) or 0) > 5, True)
_t("PSI is not symmetric", psi(a, b + 0.5) != psi(b + 0.5, a), True)''',
    hint1="""Signal: compare a production feature distribution with the training one, without labels. PSI is a
symmetrised KL divergence on binned data, with bins fixed from the reference.""",
    hint2="""1. `edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))`, then `edges[0] = -np.inf`,
`edges[-1] = np.inf`. 2. `np.histogram(x, edges)[0] / len(x)`. 3. Clip, then sum.
4. Loop over months: `inv.value[inv.month == m]` versus `inv.value[inv.month.isin(REF)]`.""",
    solution='''def psi(ref, cur, bins=10, eps=1e-4):
    ref, cur = np.asarray(ref, float), np.asarray(cur, float)
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.clip(np.histogram(ref, edges)[0] / len(ref), eps, None)
    q = np.clip(np.histogram(cur, edges)[0] / len(cur), eps, None)
    return float(np.sum((q - p) * np.log(q / p)))

ref_val = inv.value[inv.month.isin(REF)]
print("reference invoices:", len(ref_val))
for m in pd.period_range("2011-04", "2011-12", freq="M"):
    cur = inv.value[inv.month == m]
    print(m, f"n={len(cur):5d}  PSI={psi(ref_val, cur):.3f}  median value={cur.median():.0f}")
# reference invoices: 3640
# 2011-04 n= 1246  PSI=0.011  median value=302
# 2011-05 n= 1681  PSI=0.014  median value=305
# 2011-06 n= 1533  PSI=0.014  median value=294
# 2011-07 n= 1475  PSI=0.018  median value=304
# 2011-08 n= 1361  PSI=0.008  median value=306
# 2011-09 n= 1837  PSI=0.031  median value=326
# 2011-10 n= 2040  PSI=0.013  median value=314
# 2011-11 n= 2769  PSI=0.008  median value=301
# 2011-12 n=  819  PSI=0.014  median value=301''',
    why="""The order value distribution is stable all year: every month has PSI between 0.008 and 0.031, far below
0.1, even in November when the number of invoices is 2,769 versus about 1,213 a month in the reference. More
orders does not mean different orders. A volume monitor would fire; a distribution monitor on value correctly
stays quiet.

**Why PSI works this way:** each term `(q - p) * ln(q / p)` is never negative, and it grows when a bin gains or
loses share, more so when the bin was small. It is the symmetric KL divergence `KL(q||p) + KL(p||q)` on the bins.
(The test shows it is not symmetric in practice once bins come from the reference.) **Follow-ups.** *Why
quantile bins?* Equal-width bins on skewed data like order value put almost everything in one bin. *How many
rows?* Even with no drift, PSI is positive because of sampling noise: roughly `(bins - 1) * (1/n_ref + 1/n_cur)`.
For April that is `9 * (1/3640 + 1/1246) = 0.0097`, almost exactly the observed 0.011, so these small values are
pure noise. Small windows look drifted; use at least a few hundred rows and compare with this noise floor.""",
    complexity="O(n log n) for the quantiles, O(n log bins) for the binning.",
    mistakes="Bins from the current data (they move with the drift you want to measure); no `inf` outer edges "
             "(new extreme values vanish); no `eps` (log of 0); comparing tiny samples (PSI is noisy below a few "
             "hundred rows per window).",
    learn=["ai-deployment-monitoring"])

# ------------------------------------------------------------------ Q2 what drifts, and is a p-value useful?
ask(ex, title="Which drift alarms deserve a page?", minutes=7,
    prompt="""Two monitors for each month from 2011-04 to 2011-12 against `REF`:

1. For invoice `value` (10 reference-quantile bins as in Q1): a chi-square test of the binned counts
   (reference counts versus current counts, `stats.chi2_contingency`). Print the PSI and the p-value.
2. For the product mix at line level: the share of lines with `xmas == True`, and the PSI of this binary feature
   (two bins: True and False).

Which monitor would you alert on, and why is the chi-square p-value a poor alert rule? What should the alert
compare with, given that this business is seasonal? (If you did not finish Q1, copy its solution first.)""",
    stub='''# your code here''',
    hint1="""Signal: a drift alarm on large samples. Statistical significance is not practical importance: with
thousands of rows, tiny shifts give small p-values. Use an effect size (PSI) with thresholds, and seasonal
baselines.""",
    hint2="""1. Bin both samples with the reference edges, stack the two count vectors into a 2 x 10 table,
`stats.chi2_contingency(table)[1]`. 2. Binary PSI: `p = [1 - a, a]`, `q = [1 - b, b]` with the shares.
3. Compare one row per month.""",
    solution='''def psi(ref, cur, bins=10, eps=1e-4):                        # from Q1
    ref, cur = np.asarray(ref, float), np.asarray(cur, float)
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.clip(np.histogram(ref, edges)[0] / len(ref), eps, None)
    q = np.clip(np.histogram(cur, edges)[0] / len(cur), eps, None)
    return float(np.sum((q - p) * np.log(q / p)))

def psi_shares(p, q, eps=1e-4):
    p, q = np.clip(np.asarray(p, float), eps, None), np.clip(np.asarray(q, float), eps, None)
    return float(np.sum((q - p) * np.log(q / p)))

ref_val = inv.value[inv.month.isin(REF)]
edges = np.unique(np.quantile(ref_val, np.linspace(0, 1, 11)))
edges[0], edges[-1] = -np.inf, np.inf
ref_counts = np.histogram(ref_val, edges)[0]
x_ref = lines.xmas[lines.month.isin(REF)].mean()
print(f"reference xmas share {x_ref:.4f}")
for m in pd.period_range("2011-04", "2011-12", freq="M"):
    cur = inv.value[inv.month == m]
    pval = stats.chi2_contingency(np.vstack([ref_counts, np.histogram(cur, edges)[0]]))[1]
    x = lines.xmas[lines.month == m].mean()
    print(f"{m}  value: PSI {psi(ref_val, cur):.3f} chi2 p {pval:.1e}   xmas share {x:.3f} PSI {psi_shares([1 - x_ref, x_ref], [1 - x, x]):.3f}")
# reference xmas share 0.0056
# 2011-04  value: PSI 0.011 chi2 p 3.3e-01   xmas share 0.003 PSI 0.002
# 2011-05  value: PSI 0.014 chi2 p 5.7e-02   xmas share 0.002 PSI 0.003
# 2011-06  value: PSI 0.014 chi2 p 7.8e-02   xmas share 0.006 PSI 0.000
# 2011-07  value: PSI 0.018 chi2 p 2.4e-02   xmas share 0.015 PSI 0.009
# 2011-08  value: PSI 0.008 chi2 p 5.7e-01   xmas share 0.026 PSI 0.032
# 2011-09  value: PSI 0.031 chi2 p 2.3e-05   xmas share 0.072 PSI 0.174
# 2011-10  value: PSI 0.013 chi2 p 4.6e-02   xmas share 0.100 PSI 0.282
# 2011-11  value: PSI 0.008 chi2 p 2.3e-01   xmas share 0.098 PSI 0.275
# 2011-12  value: PSI 0.014 chi2 p 3.9e-01   xmas share 0.082 PSI 0.212''',
    why="""The value monitor gives small p-values (2.3e-05 in September) although the PSI is only 0.031: with thousands of
invoices, a chi-square test detects shifts too small to matter. In other months the p-value bounces around 0.05
with no real change. A p-value answers "is there any difference", not "is it big enough to hurt the model", and
it gets smaller just because traffic grows. Alerting on it means paging people every busy day.

The product mix monitor shows a real, large shift: Christmas items go from 0.56% of lines in the reference to
7.2% in September and 10.0% in October (PSI 0.174 then 0.282, "major"). A model trained on January to March has
almost never seen these products (for example a demand or recommendation model), so this is the alert worth a
page, or at least a ticket.

**Better alert rule:** effect size (PSI) above a threshold for k consecutive windows, per feature, with the
threshold set from the historical noise floor of that feature. **Seasonality:** compare with the same period
last year (or a model of the expected seasonal profile), and retrain with at least one full year of data so
October looks like last October. Drift alone is not failure: confirm with model metrics (when labels arrive)
or with prediction drift.""",
    complexity="O(n) per month after sorting the reference once.",
    mistakes="Paging on p-values from huge samples; one global threshold for every feature (binary and rare "
             "features need their own); treating seasonal change as model failure without checking last year.",
    learn=["ai-deployment-monitoring", "stats-hypothesis-tests"])

# ------------------------------------------------------------------ Q3 deployment and monitoring (text)
ask(ex, title="Ship a new model safely and know when it breaks", minutes=6, kind="text",
    prompt="""Examiner: "You have a new fraud model that is better offline. Walk me through how you deploy it,
what you monitor, and what you do when labels (chargebacks) arrive 30 to 60 days late." Follow-ups to expect:
"What is training-serving skew and how do you catch it?" and "When do you retrain: on a schedule or on drift?\"""",
    hint1="""Signal: MLOps lifecycle. Rollout stages (shadow, canary, A/B), layered monitoring (system, data,
model, business), proxies for delayed labels, and rollback.""",
    hint2="""1. Offline gate, then shadow mode (score live traffic, take no action, compare), canary 1 to 5%, A/B or
ramp. 2. Monitor: latency and errors; input drift and missing values; score distribution and decision rate;
early proxies of labels; business KPIs. 3. Skew: log the features used at serving and compare with training.""",
    solution="""**Deployment, step by step**
1. **Offline gate:** better than the current model on a time-based holdout, also per slice (new merchants,
   countries), calibrated, with latency within budget.
2. **Shadow mode** (1 to 2 weeks): the new model scores live traffic but takes no action. Compare score
   distributions and decision rates with the old model; inspect cases where they disagree most; check the
   serving features equal the offline features for the same events (skew test).
3. **Canary:** 1 to 5% of traffic, automatic rollback on system metrics (errors, p99 latency) and on decision
   rate jumping outside a band (for example the block rate doubles).
4. **A/B or ramp:** 5, 25, 50, 100%, with business metrics: fraud loss, false declines (customer friction),
   manual review volume. Keep the old model deployable (versioned artifacts, feature definitions and thresholds)
   for one-click rollback.

**Monitoring, four layers**
- System: QPS, latency p50 and p99, error and timeout rate, fallbacks used.
- Data: PSI per feature against training, share of missing or default values, freshness of streamed features,
  schema changes (a new country code, a unit change).
- Model: score distribution, decision rate at the threshold, calibration once labels arrive, disagreement with
  the previous model.
- Business: fraud loss, decline rate, complaints.

**Delayed labels:** use early proxies (customer disputes in the first 7 days, manual review outcomes, rule hits),
measure performance on mature cohorts (transactions older than 60 days) and report it by cohort week, and keep a
small random holdout (or a lower threshold on a sample) so you can estimate what the model misses without
feedback-loop bias.

**Training-serving skew:** the same feature computed differently offline (batch SQL) and online (streaming code),
or offline data that includes information not available at decision time. Catch it by logging the exact feature
vector at serving time and training on those logs, by a shared feature store with one definition, and by a daily
job that recomputes features offline for a sample of served events and compares them value by value.

**Retrain on a schedule or on drift?** Both: a regular schedule (weekly or monthly, depending on how fast fraud
patterns move) gives fresh models predictably; drift alarms trigger an investigation, not an automatic retrain,
because drift can come from a bug (a broken feature) and retraining on broken data would hide it. Every retrain
passes the same offline gate and canary.""",
    why="""This is the standard MLOps answer: staged rollout with automatic rollback, monitoring at system, data,
model and business layers, a plan for delayed labels, and skew prevention through logged features. Mentioning
that drift alarms trigger investigation rather than blind retraining shows experience.""",
    learn=["ai-deployment-monitoring"])

# ------------------------------------------------------------------ Q4 canary sizing
ask(ex, title="How long must the canary run?", minutes=5,
    prompt="""The current model's request error rate is 0.5%. You want the canary to detect an increase to 0.6%
(one-sided test, alpha 0.05, power 0.8). Traffic is 2,000 requests per second and the canary gets 5% of it; the
comparison group is a 5% slice of the old model.

1. Write `n_per_group(p1, p2, alpha=0.05, power=0.8)` for a one-sided two-proportion test:
   `n = (z_a * sqrt(2 * pbar * (1 - pbar)) + z_b * sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2`,
   with `pbar = (p1 + p2) / 2`, rounded up.
2. How many minutes must the canary run? And to detect 0.5% to 1.0%?
3. The on-call engineer checks the dashboard every minute and rolls back at the first p below 0.05. What goes
   wrong?""",
    stub='''def n_per_group(p1, p2, alpha=0.05, power=0.8):
    # your code here
    pass''',
    tests='''_t("0.5% to 0.6%", n_per_group(0.005, 0.006), 67634)
_t("0.5% to 1.0%", n_per_group(0.005, 0.010), 3681)''',
    hint1="""Signal: an A/B power calculation applied to a deployment: a small rate, a small lift, many requests per
second. Then the peeking problem for repeated checks.""",
    hint2="""1. `z_a = stats.norm.ppf(1 - alpha)`, `z_b = stats.norm.ppf(power)`. 2. Canary requests per minute =
2000 * 0.05 * 60. 3. Minutes = n / that.""",
    solution='''import math

def n_per_group(p1, p2, alpha=0.05, power=0.8):
    za, zb = stats.norm.ppf(1 - alpha), stats.norm.ppf(power)
    pbar = (p1 + p2) / 2
    n = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2
    return math.ceil(n)

per_min = 2000 * 0.05 * 60
for p2 in (0.006, 0.010):
    n = n_per_group(0.005, p2)
    print(f"0.5% -> {p2:.1%}: {n:,} requests per group, {n / per_min:.1f} minutes")
# 0.5% -> 0.6%: 67,634 requests per group, 11.3 minutes
# 0.5% -> 1.0%: 3,681 requests per group, 0.6 minutes''',
    why="""To see 0.5% to 0.6% you need about 67,634 requests in each group: at 100 canary requests per second (6,000 per
minute) that is **11.3 minutes**. A bigger regression (0.5% to 1.0%) needs only 3,681 requests, about **0.6
minutes**. So: a short canary catches disasters quickly, but subtle regressions need longer runs or more
traffic; set the canary length from the smallest regression you care about.

**Peeking:** checking every minute and stopping at the first p below 0.05 raises the false-alarm rate far above
5% (with 11 equally spaced looks it is about 18%, by simulation), so you roll back good models for nothing. Fixes: a fixed horizon (decide
after 12 minutes), or a sequential test designed for continuous monitoring (SPRT, alpha spending, always-valid
p-values); plus hard limits that roll back instantly for catastrophic errors (error rate above 2%) without any
statistics.""",
    complexity="O(1).",
    mistakes="Using a two-sided test when only an increase matters (needs more traffic); ignoring the peeking "
             "problem; checking only the average latency (regressions hide in p99 and in one region or device).",
    learn=["ai-deployment-monitoring", "stats-power-mde"])

# ------------------------------------------------------------------ Q5 review: debug a metric drop after a deploy (text)
ask(ex, title="Watch time fell 3% the morning after a model push", minutes=5, kind="text", review=True,
    prompt="""You own the feed ranker (day 24). A new ranking model went to 100% last night. This morning total
watch time is down 3% versus the same weekday last week. What do you do in the first hour, and how do you find the
cause? Give a structured answer.""",
    hint1="""Signal: metric drop triage plus model deployment. First mitigate (rollback is cheap), then isolate:
is it real, is it the model, which part of the pipeline, which segment.""",
    hint2="""1. Is it real (data pipeline, logging, holidays)? 2. Correlate in time with the deploy; compare with the
holdout still on the old model. 3. Roll back if the holdout confirms. 4. Then debug: features (skew, missing),
scores (distribution, calibration), candidates, re-ranking, segments.""",
    solution="""**1. Mitigate first.** If the drop lines up with the deploy and the long-term holdout (users still on
the old model) did not drop, roll back now: rollback is cheap, lost watch time is not. Then investigate offline.

**2. Is it real?** Check logging and dashboards (a broken event pipeline also looks like a drop), the calendar
(holiday, big event), and other products in the same app (an app release or outage). Compare with the holdout
group, which is the best counterfactual.

**3. Isolate the cause, along the pipeline:**
- **Features:** missing or default values at serving (a feature store table that did not refresh), training-
  serving skew (the new model uses a feature computed differently online), PSI of each feature.
- **Model outputs:** score distribution versus yesterday, calibration of each head, whether the fusion weights
  were deployed with the right version.
- **Candidates and re-ranking:** did retrieval return fewer or older candidates? Did a diversity rule change?
- **Segments:** new versus returning users, countries, app versions, Android versus iOS. A drop in one segment
  usually points to a bug (one app version does not send a feature).

**4. Why did the offline evaluation miss it?** Typical answers: the offline set did not contain the broken
feature path (skew), the offline metric (AUC of one head) is not the online one (total watch time), or the
change shifted the content mix (more short videos: higher completion, less total time).

**5. Prevent it next time:** canary with automatic guardrails on watch time per user and skip rate, a shadow
comparison of score distributions before ramp, and feature-level checks in the deploy pipeline.""",
    why="""Examiners want a calm, ordered answer: protect users (rollback using the holdout as evidence),
verify the drop is real, then bisect the system (data, model, candidates, re-ranking, segments), and finally fix
the process so it cannot happen again.""",
    learn=["ai-ml-system-design", "ai-deployment-monitoring", "stats-metric-drop"])

ex.save()
