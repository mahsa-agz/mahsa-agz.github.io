import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_mid_common import start, q, pm

# Day 20 stats: focus product metrics and metric trees; review PSM/RD/IV and A/B design.
EXTRA = '''
# Valid purchases with a known customer, one row per invoice line, plus a month column.
ok = retail.CustomerID.notna() & ~retail.InvoiceNo.str.startswith("C") & (retail.Quantity > 0) & (retail.UnitPrice > 0)
sales = retail[ok].assign(rev=lambda d: d.Quantity * d.UnitPrice, month=lambda d: d.InvoiceDate.dt.to_period("M"))
print("sales", sales.shape)
'''
ex = start(20, ["retail", "cats"], extra=EXTRA,
           note="The setup builds `sales` from the real retail data: valid purchase lines with `rev = Quantity * "
                "UnitPrice` and `month`. In Colab, upload `online_retail.csv.gz` to the data folder if it is "
                "missing.")

# ---------------------------------------------------------------- Q1
q(ex, title="Revenue jumped in November. Which branch of the tree?", minutes=8,
  prompt="Revenue can be split as a metric tree: `revenue = active customers * orders per customer * average "
         "order value (AOV)`.\n\n"
         "(a) For each month from 2011-01 to 2011-11, compute the three drivers and revenue.\n\n"
         "(b) Revenue rose from October to November 2011. Split the change into the three drivers using logs: "
         "`log(R1/R0) = log(C1/C0) + log(F1/F0) + log(A1/A0)`; show each driver's log change (in log points) next to the total.\n\n"
         "(c) Say it to a PM. What would you check next?\n\n"
         "Follow-up: why use logs and not the plain differences of the three drivers?",
  stub="# your code here",
  hint1="Signal: 'why did the top-line metric move?'. Method: metric tree (multiplicative decomposition); log "
        "changes add up exactly.",
  hint2="1. `m = sales.groupby('month').agg(revenue=('rev','sum'), customers=('CustomerID','nunique'), "
        "orders=('InvoiceNo','nunique'))`. 2. `freq = orders / customers`, `aov = revenue / orders`. "
        "3. Take the two months and compute `np.log(new / old)` for each driver and for revenue; the three driver terms add up to the revenue term.",
  solution='''m = sales.groupby("month").agg(revenue=("rev", "sum"), customers=("CustomerID", "nunique"),
                                orders=("InvoiceNo", "nunique"))
m["freq"] = m.orders / m.customers
m["aov"] = m.revenue / m.orders
m = m.loc["2011-01":"2011-11"]
print(m[["customers", "freq", "aov", "revenue"]].round(2))
a, b = m.loc["2011-10"], m.loc["2011-11"]
total = np.log(b.revenue / a.revenue)
for k in ["customers", "freq", "aov"]:
    print(f"{k}: {(b[k] / a[k] - 1) * 100:+.1f}%, log change {np.log(b[k] / a[k]):+.3f}")
print(f"revenue: {(b.revenue / a.revenue - 1) * 100:+.1f}%, log change {total:+.3f}")
#          customers  freq     aov     revenue
# 2011-10       1364  1.41  538.79  1039318.79
# 2011-11       1664  1.60  437.27  1161817.38
# customers: +22.0%, log change +0.199
# freq: +12.9%, log change +0.121
# aov: -18.8%, log change -0.209
# revenue: +11.8%, log change +0.111''',
  why="Revenue is a product of drivers, so its log change is exactly the sum of the drivers' log changes; this "
      "attribution has no leftover 'interaction' term. November revenue rose 11.8% (log +0.111), but the drivers "
      "moved much more than that: active customers +22.0% (+0.199) and orders per customer +12.9% (+0.121), while "
      "average order value fell 18.8% (-0.209). So the top line hides two opposite stories: many more, and more "
      "frequent, buyers before Christmas, placing clearly smaller orders. A good analyst reports both, because a "
      "falling AOV could become a problem once the seasonal customers leave."
      + pm("November revenue grew 12% because 22% more customers bought and they ordered more often, but each order "
           "was about 19% smaller, which ate most of the gain; next we should check who the extra customers are "
           "(new or returning, which country) and why orders got smaller, and compare with last November.",
           [("Why logs?", "Plain differences of a product do not add up to the total change (there is a cross term "
             "that grows when several drivers move together). Log changes add exactly, and with small changes they "
             "are close to percent changes."),
            ("Next checks", "Split customers into new vs returning, by country (UK vs rest), compare with "
             "November 2010 for seasonality, and break AOV into items per order times price per item.")]),
  complexity="O(n) group-by over 400k lines.",
  mistakes="Counting cancelled invoices or lines without a customer. Using the December 2011 month, which is only "
           "9 days long. Mixing customer-level and order-level averages.",
  learn=["stats-product-metrics", "stats-metric-drop"])

# ---------------------------------------------------------------- Q2
q(ex, title="Pick the north star for a short-video app", minutes=7, kind="text",
  prompt="You join a short-video app (think TikTok or YouTube Shorts) as the DS for the 'For You' feed. The "
         "head of product asks: 'What should our one north star metric be, and how do we know it is healthy?'\n\n"
         "Give: (1) a north star metric with a precise definition, (2) a metric tree of 3 to 4 input metrics that "
         "teams can move, (3) 3 guardrail or counter metrics, (4) one way the north star could be gamed. Then say it "
         "to the head of product in two sentences.\n\n"
         "Follow-ups: why not 'daily active users'? How would you check that your north star predicts long-term "
         "retention?",
  hint1="Framework: the north star reflects value delivered to users and leads revenue; inputs are levers teams own; "
        "guardrails catch harm; every metric needs a unit, a time window and a population.",
  hint2="1. Candidate: daily 'satisfied watch time' or 'qualified views' per DAU. 2. Tree: DAU x sessions per DAU x "
        "videos per session x satisfaction per video. 3. Guardrails: 7-day retention, report/skip rate, creator "
        "uploads, latency, wellbeing. 4. Gaming: clickbait and autoplay loops.",
  solution="""- **North star:** total *satisfied* watch time per day: minutes from video views that were watched past
  50% or got a like/share/follow, excluding autoplay without interaction, summed over all users. Teams track it per
  DAU too. It captures value for viewers (they chose to keep watching) and leads ad revenue.
- **Metric tree (inputs):**
  - DAU (acquisition, reactivation, notifications team)
  - sessions per DAU (habit, notifications)
  - videos per session x satisfied share of views (ranking quality, the feed team's main lever)
  - minutes per satisfied view (content mix, video length)
- **Guardrails / counter metrics:** 7-day and 28-day retention (short-term watch time can burn users out), negative
  feedback rate (skip within 2 s, "not interested", reports), creator-side health (uploads per creator, share of views
  going to new creators), app performance (start-up time, crash rate), and wellbeing or late-night usage limits.
- **Gaming risk:** ranking can push clickbait or endless low-quality autoplay that adds minutes but lowers
  satisfaction and retention later (Goodhart's law). The 'satisfied' filter and the retention guardrail are there to
  catch it.

**Say it to the head of product:** "Our north star is satisfied watch time per day, because it grows only when people
choose to keep watching and it leads revenue; each team owns one branch of the tree (users, sessions, feed quality),
and we only celebrate a win if retention and negative feedback stay healthy."

**Follow-ups:**
- *Why not DAU?* It moves slowly, is driven a lot by marketing and notifications, and says nothing about whether the
  feed is good. It is an input in the tree, not the goal.
- *Does it predict retention?* Check historically: users or cohorts whose satisfied watch time rose, did they retain
  better 4 weeks later, controlling for prior activity? Better: in past experiments, did the short-term north star
  effect predict the long-term retention effect (from long-running holdouts)? If not, change the definition.""",
  why="A strong answer defines the metric precisely (unit, filter, time window), shows how teams can move it "
      "(the tree), and protects it from being gamed (guardrails). It also explains *why* this metric reflects "
      "user value and business value.",
  mistakes="Picking revenue (lags, not owned by the feed team) or raw views (easy to game). Listing many metrics "
           "without a tree. No counter metric for the gaming risk.",
  learn=["stats-product-metrics", "stats-case-framework"])

# ---------------------------------------------------------------- Q3
q(ex, title="Find the 'aha' moment", minutes=6,
  prompt="Use the control group (gate_30) of Cookie Cats.\n\n"
         "(a) Day-7 retention by rounds played in the first 14 days, in buckets "
         "`[0, 1, 5, 10, 20, 30, 50, 100, inf)` (left-closed). Also the share of players in each bucket.\n\n"
         "(b) A PM proposes an activation metric 'played at least N rounds'. For N in (10, 20, 30, 50), compute the "
         "share of players activated and the day-7 retention of activated vs not activated players. Which N would "
         "you choose and why?\n\n"
         "(c) Say it to a PM. Can the team raise retention by pushing everyone to N rounds?",
  stub="ctl = cats[cats.version == \"gate_30\"]\n# your code here",
  hint1="Signal: define an activation ('aha') metric from behaviour. Method: retention by engagement bucket, then "
        "pick a threshold that separates retained from not retained and that many users can reach.",
  hint2="1. `pd.cut(ctl.sum_gamerounds, bins=[0,1,5,10,20,30,50,100,np.inf], right=False)`. "
        "2. `groupby(bucket).retention_7.agg(['mean','size'])`. 3. For each N: `act = rounds >= N`, share and "
        "retention by act.",
  solution='''ctl = cats[cats.version == "gate_30"]
bins = [0, 1, 5, 10, 20, 30, 50, 100, np.inf]
b = pd.cut(ctl.sum_gamerounds, bins=bins, right=False)
t = ctl.groupby(b, observed=True).retention_7.agg(["mean", "size"])
t["share"] = t["size"] / len(ctl)
print(t[["share", "mean"]].round(3))
for n in [10, 20, 30, 50]:
    act = ctl.sum_gamerounds >= n
    print(f"N={n}: activated {act.mean():.3f}, r7 activated {ctl.retention_7[act].mean():.3f}, "
          f"not {ctl.retention_7[~act].mean():.3f}")
# retention_7 by bucket: [0,1) 0.008 | [1,5) 0.012 | [5,10) 0.027 | [10,20) 0.063 | [20,30) 0.113
#                        [30,50) 0.185 | [50,100) 0.375 | [100,inf) 0.711
# N=10: activated 0.623, r7 activated 0.295, not 0.017
# N=20: activated 0.464, r7 activated 0.375, not 0.031
# N=30: activated 0.373, r7 activated 0.439, not 0.043
# N=50: activated 0.253, r7 activated 0.558, not 0.065''',
  why="Day-7 retention climbs steeply with rounds played: under 3% below 10 rounds, 71% at 100 or "
      "more. N = 30 is a reasonable choice: 37% of players reach it and their day-7 retention is 43.9% vs 4.3% (about "
      "10 times); N = 50 separates more but only 25% reach it. It is also the level of the first gate, a natural "
      "milestone. A good activation threshold separates the groups strongly "
      "*and* is reached by a meaningful share of players early enough to act on. Here the measurement window "
      "(14 days) overlaps the outcome (day 7), which is a leak: players who came back on day 7 had more time to play "
      "rounds. A clean activation metric uses only the first 1 to 3 days."
      + pm("Players who reach about 30 rounds are about ten times more likely to still be playing after a week, so "
           "'30 rounds' is a useful early warning and segment, but forcing people to play more rounds will not "
           "automatically make them stay: we would need to test interventions that help players get there.",
           [("Can we push everyone to N?", "No, not from this data. Rounds and retention share a cause (players who "
             "like the game do both). The famous 'aha' metrics (7 friends in 10 days) were hypotheses to test, not "
             "proofs. Run an experiment (for example an onboarding change that helps players reach N) and measure "
             "retention directly; or use the random variation in such a test as an instrument (Q4)."),
            ("Choosing N", "Look for the knee where retention jumps and the activated share is still large; check it "
             "is stable across cohorts; prefer a window that ends before the outcome starts.")]),
  complexity="O(n).",
  mistakes="Defining activation with data from after the outcome. Choosing the N with the biggest retention ratio "
           "even if only 2% of users reach it. Treating the correlation as a causal lever.",
  learn=["stats-product-metrics", "stats-causal-psm-rd-iv"])

# ---------------------------------------------------------------- Q4 review
q(ex, title="Should we push everyone into communities?", minutes=6, review=True, kind="text",
  prompt="Users who join a community in their first week have 30-day retention of 60% vs 25% for users who do not. "
         "The PM wants to auto-join every new user to a community. How do you find out whether joining *causes* "
         "higher retention?\n\n"
         "Give three designs in order of preference (one experiment, two observational), the key assumption of each, "
         "and what each one actually estimates. Then say it to the PM in two sentences.",
  hint1="Framework: randomised experiment first; if you cannot force joining, randomise an encouragement (IV); "
        "otherwise matching on pre-join behaviour (PSM) or a cutoff (RD) if one exists.",
  hint2="1. A/B: auto-join (or a strong join prompt) vs control, measure 30-day retention by assigned group (ITT). "
        "2. IV: the prompt is the instrument for joining, estimate = ITT / change in join rate. 3. PSM: match "
        "joiners to non-joiners on first-days activity, device, channel; assumption: no unobserved confounders.",
  solution="""1. **A/B test of the actual policy (best).** Randomise new users to auto-join vs current experience.
   Analyse by assigned group: the ITT effect on 30-day retention *is* the effect of the policy the PM wants. No
   confounding by design. Guardrails: notification opt-outs, leaving rates, community moderation load (and
   interference: auto-joined users change the community for others, so watch community-level metrics or randomise
   by community).
2. **Encouragement design + IV.** If forcing membership is not acceptable, randomise a join prompt. ITT = effect of
   the prompt; IV = ITT / (increase in join rate) = effect of joining for *compliers* (users who join only because of
   the prompt). Assumptions: the prompt affects retention only through joining (exclusion), and nobody is put off
   joining by it (monotonicity).
3. **Propensity score matching on historical data.** Match joiners with non-joiners who had the same first-days
   behaviour (sessions, follows, posts before joining), acquisition channel, device, country. Estimates the effect on
   joiners (ATT) *if* there are no unobserved confounders, which is doubtful (motivation). Use it to size the
   opportunity, not to decide.

(If joining was ever unlocked by a threshold, for example 'after 3 posts', a regression discontinuity around that
threshold would be another option.)

**Say it to the PM:** "Most of the 60% vs 25% gap is probably that engaged users both join and stay, so auto-joining
everyone will not deliver a 35 point lift; let's run a 50/50 test of auto-join, which tells us within a month the real
effect of exactly the policy you want to launch."
""",
  why="Self-selection is the core problem: joiners differ before they join. The answer ranks designs by how "
      "strongly they remove that bias and names what each estimates (policy ITT, complier LATE, ATT under "
      "unconfoundedness). That is the medium-level skill: matching the method to the decision.",
  mistakes="Promising a 35 point lift. Proposing PSM first when an experiment is feasible. Forgetting that IV gives a "
           "local effect for compliers.",
  learn=["stats-causal-psm-rd-iv", "stats-ab-design"])

ex.save()
