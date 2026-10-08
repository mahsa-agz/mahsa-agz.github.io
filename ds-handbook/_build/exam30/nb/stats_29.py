import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats_hard_common import start, shown, hidden_setup, PM

# Day 29 stats: one full product / statistics exam round (case-framework + full loop).

INTRO = """**Full exam round (about 50 minutes).** This notebook is one product data science exam, in the
style of TikTok and Google product DS rounds: one scenario, five parts, and the examiner adds information as you
go. Set one timer for **50 minutes**. Do the parts in order and do not read ahead. Talk out loud as if the
examiner were listening: state the method, the assumptions and a decision. Open hints and solutions only after
the timer ends.

**The scenario.** You are the data scientist for the For You feed of a short-video app. Leadership worries that new
creators give up because nobody sees their first videos. The ranking team built **Creator Boost**: videos from
creators with fewer than 1,000 followers get a small extra exposure in the For You feed. The PM asks: *"Should we
launch Creator Boost?"*"""

HIDDEN = '''_r = np.random.default_rng(2029)
_n = 400_000
_t = _r.integers(0, 2, _n)
_pre = _r.gamma(0.6, 70, _n)
_w = (0.8 * _pre * _r.lognormal(-0.08, 0.4, _n) + _r.gamma(0.7, 12, _n)) * (1 - 0.003 * _t)
_views = 1 + _r.poisson(_w * 1.9)
_sk = np.clip(_r.beta(3.6, 16.4, _n) * (1 + 0.025 * _t), 0, 1)
viewers = pd.DataFrame({"user_id": np.arange(_n), "group": np.where(_t == 1, "treatment", "control"),
                        "country": _r.choice(["US", "BR", "ID", "DE"], _n, p=[0.4, 0.25, 0.25, 0.1]),
                        "pre_watch": _pre.round(1), "watch_min": _w.round(1), "views": _views,
                        "skips": _r.binomial(_views, _sk)})
_m = 60_000
_ct = _r.integers(0, 2, _m)
_b = _r.choice(["0-100", "100-1k", "1k+"], _m, p=[0.5, 0.35, 0.15])
_lam = _r.gamma(0.8, 6, _m) * np.where(_b == "1k+", 1.6, 1.0)
_mult = np.where(_ct == 1, np.select([_b == "0-100", _b == "100-1k"], [1.10, 1.04], 1.0), 1.0)
creators = pd.DataFrame({"creator_id": np.arange(_m), "group": np.where(_ct == 1, "treatment", "control"),
                         "followers": _b, "pre_videos": _r.poisson(_lam), "videos": _r.poisson(_lam * _mult)})
print(viewers.shape, creators.shape)'''

DATA = """Both tables are **simulated** (made up) for this round and built by the hidden cell. Do not read it.

| Table | One row = | Columns |
|---|---|---|
| `viewers` | one viewer in the **viewer-side** test (randomized by viewer, 2 weeks; treated viewers see boosted feeds) | `user_id`, `group`, `country`, `pre_watch` (minutes in the 2 weeks before), `watch_min` (minutes during the test), `views` (videos started), `skips` (videos left within 3 seconds) |
| `creators` | one creator in the **creator-side** test (randomized by creator, 4 weeks; treated creators are eligible for the boost if they have under 1,000 followers) | `creator_id`, `group`, `followers` (bucket at the start: 0-100, 100-1k, 1k+), `pre_videos` (videos posted in the 4 weeks before), `videos` (videos posted during the test) |"""

ex = start(29, intro=INTRO, data_doc=DATA)
hidden_setup(ex, "Build the round's data (hidden)", HIDDEN)

# ---------------------------------------------------------------- Part 1 clarify and metrics
ex.q("Part 1: clarify the goal and choose the metrics", minutes=7, kind="text",
     prompt="The examiner says: *\"Before we look at any data: how would you decide whether Creator Boost "
            "works?\"*\n\n"
            "Ask the clarifying questions you need (write them with the answers you would assume), state the "
            "goal, and give: one primary metric for creators, one for viewers, two or three guardrails, and the "
            "experiment design you would propose (unit of randomization on each side and why)." +
            PM + "summarize the plan in two sentences.",
     hint1="Signal: a two-sided platform change (creators and viewers). Method: case framework: clarify, goal, "
           "metric tree on both sides, guardrails, and a design that respects interference.",
     hint2="1. Clarify: what 'give up' means, which creators, which markets, the size of the boost. 2. Creator "
           "metric: posting or retention of small creators. 3. Viewer metric: watch time, plus a quality "
           "signal. 4. Viewer-side and creator-side tests measure different things; one unit cannot do both.",
     solution="""**Clarifying questions (with assumed answers).** What does "give up" mean? (A creator with under
1,000 followers who posts no video for 4 weeks.) How big is the boost? (Small: about 2% of feed impressions move to
small creators.) Global or some markets? (Global.) Is there a quality filter on boosted videos? (Only the normal
integrity filters.) Time horizon? (Leadership cares about creator supply over the next 6 to 12 months.)

**Goal:** more new creators keep posting, without making the feed worse for viewers.

**Primary metrics.** Creators: videos posted per eligible creator over 4 weeks (and, longer term, the share of
eligible creators still posting after 8 weeks). Viewers: watch time per user.

**Guardrails.** Quick skips (share of views left within 3 seconds, a relevance signal), viewer day-7 retention, and
watch time of creators with 1,000+ followers (the boost takes impressions from them). Integrity: reports per 1,000
views on boosted videos.

**Design.** Two tests, because one unit cannot measure both sides. (1) **Viewer-side**: randomize viewers; treated
viewers see feeds with the boost. This measures the viewer cost. (2) **Creator-side**: randomize creators; treated
small creators are eligible for the boost. This measures the creator response, but with interference: boosted
creators take impressions from control creators, so the difference is **larger** than the effect of a full launch
(where all small creators are boosted and share the extra exposure). To measure the full effect, add a market-level
holdout (some countries or regions without the boost), analyzed at the market level.

**Say it to a PM:** "We will run one test on viewers to measure what the boost costs in watch time and quality, and one
on creators to see if they post more; because boosted creators partly take views from other creators, we will also
keep a few markets without the boost to measure the real total effect.\"""",
     why="Examiners grade structure: clear goal, metrics on both sides of the platform, guardrails tied to "
         "the risk (quality, big creators), and a design that admits the interference.",
     learn=["stats-case-framework", "stats-product-metrics", "stats-network-effects"])

# ---------------------------------------------------------------- Part 2 sample size
q2 = '''from scipy.stats import norm
za, zb = norm.ppf(0.975), norm.ppf(0.80)

def n_per_group(sd, delta):
    return int(np.ceil(2 * (za + zb) ** 2 * sd ** 2 / delta ** 2))

n_view = n_per_group(55, 0.005 * 42)
print(f"viewers per group: {n_view:,}; with CUPED (rho 0.8): {int(np.ceil(n_view * (1 - 0.8 ** 2))):,}")
n_cre = n_per_group(5.8, 0.03 * 4.8)
print(f"eligible creators per group: {n_cre:,}")
print(f"weeks to reach that with 20,000 new eligible creators a week and 50% in treatment: {2 * n_cre / 20_000:.1f}")
# viewers per group: 1,076,774; with CUPED (rho 0.8): 387,639
# eligible creators per group: 25,467
# weeks to reach that with 20,000 new eligible creators a week and 50% in treatment: 2.5'''
ex.q("Part 2: how big must the tests be?", minutes=7, kind="python",
     prompt="The examiner gives numbers:\n\n"
            "- Viewers: watch time per user over 2 weeks has mean 42 minutes and standard deviation 55. Leadership "
            "accepts a cost of at most **0.5% relative**, so the test must detect a 0.5% change. The "
            "correlation between the 2 weeks before and the test weeks is about 0.8.\n"
            "- Creators: videos posted per eligible creator over 4 weeks has mean 4.8 and standard deviation "
            "5.8. The team wants to detect a **3% relative** lift. About 20,000 new creators become eligible each "
            "week.\n\n"
            "1. With two-sided alpha 0.05 and power 80%, how many viewers per group? How many with CUPED?\n"
            "2. How many eligible creators per group, and roughly how long does it take to enrol them?\n"
            "3. Name one thing that could make these numbers wrong." +
            PM + "explain the size of the tests.",
     hint1="Signal: 'how many users do we need'. Method: power and MDE for a difference in means, with variance "
           "reduction from CUPED (variance times `1 - rho^2`).",
     hint2="1. `n = 2 (z_0.975 + z_0.8)^2 sd^2 / delta^2` with `delta` the absolute MDE. 2. Viewer delta = "
           "0.005 x 42 = 0.21 minutes. 3. CUPED multiplies n by `1 - 0.8^2 = 0.36`. 4. Creator delta = 0.03 x 4.8.",
     solution=q2,
     why="A 0.5% change in a very skewed metric is tiny compared with its spread (sd 55 on a mean of 42), so the "
         "plain test needs about 1.08 million viewers per group. CUPED with a correlation of 0.8 removes 64% of "
         "the variance and cuts that to about 388k per group. For creators, 3% of 4.8 videos is 0.144 videos, "
         "which needs about 25.5k creators per group, about 2.5 weeks of new eligible creators. Things that "
         "break the numbers: the creator test is affected by interference (it measures a larger effect than "
         "launch, so it could look well powered for the wrong number), heavy tails (a few extreme users inflate "
         "the sd: consider capping), novelty (the effect may change over the weeks), and clustering if "
         "randomization is not by the analysis unit." + PM + "\"To see a cost as small as half a percent of "
         "watch time we need about 400,000 viewers per group using last month's behaviour to reduce noise, and "
         "about 25,000 creators per group, which takes about two and a half weeks to enrol.\"",
     mistakes="Using the relative MDE (0.005) in the formula instead of the absolute one (0.21 minutes). "
              "Forgetting the factor 2 for two groups. Applying CUPED to new users with no pre-period.",
     learn=["stats-power-mde", "stats-cuped"])
shown(ex)

# ---------------------------------------------------------------- Part 3 viewer-side results
q3 = '''print(viewers.group.value_counts().to_dict(), f"SRM p = {stats.chisquare(viewers.group.value_counts()).pvalue:.2f}")
c, t = viewers[viewers.group == "control"], viewers[viewers.group == "treatment"]
theta = np.cov(viewers.pre_watch, viewers.watch_min)[0, 1] / viewers.pre_watch.var()
adj = viewers.watch_min - theta * (viewers.pre_watch - viewers.pre_watch.mean())
print(f"theta {theta:.3f}, corr(pre, watch) {np.corrcoef(viewers.pre_watch, viewers.watch_min)[0, 1]:.2f}")
for name, y in (("plain", viewers.watch_min), ("CUPED", adj)):
    yc, yt = y[viewers.group == "control"], y[viewers.group == "treatment"]
    d, se, base = yt.mean() - yc.mean(), np.sqrt(yc.var() / len(yc) + yt.var() / len(yt)), c.watch_min.mean()
    print(f"{name}: {d / base:+.2%} [{(d - 1.96 * se) / base:+.2%}, {(d + 1.96 * se) / base:+.2%}]")

def ratio(d):                                  # skip rate = skips / views, delta-method SE (unit = viewer)
    x, y = d.views, d.skips
    r = y.sum() / x.sum()
    v = (y.var() - 2 * r * np.cov(x, y)[0, 1] + r ** 2 * x.var()) / (len(d) * x.mean() ** 2)
    return r, np.sqrt(v)

(rc, sc), (rt, st) = ratio(c), ratio(t)
z = (rt - rc) / np.sqrt(sc ** 2 + st ** 2)
print(f"skip rate {rc:.4f} -> {rt:.4f} ({rt / rc - 1:+.1%} relative), z = {z:.1f}")
# {'treatment': 200241, 'control': 199759} SRM p = 0.45
# theta 0.799, corr(pre, watch) 0.87
# plain: -0.45% [-1.19%, +0.28%]
# CUPED: -0.17% [-0.54%, +0.19%]
# skip rate 0.1803 -> 0.1844 (+2.3% relative), z = 9.5'''
ex.q("Part 3: what does the viewer test say?", minutes=10, kind="python",
     prompt="The viewer-side test ran 2 weeks (`viewers`, simulated).\n\n"
            "1. Run the checks you always run first.\n"
            "2. Estimate the relative change in watch time per user with a 95% CI, plain and with CUPED.\n"
            "3. Estimate the change in the **skip rate** (`total skips / total views`) with a correct standard "
            "error.\n"
            "4. Is the viewer cost within what leadership accepts (at most 0.5% of watch time)?" +
            PM + "the viewer-side result.",
     hint1="Signal: an experiment readout with a pre-period covariate and a ratio guardrail. Methods: SRM check, "
           "CUPED for the mean metric, delta method for the ratio metric.",
     hint2="1. Chi-square on group counts. 2. `theta = cov(pre, y) / var(pre)`, adjusted metric, Welch CI, divide "
           "by the control mean. 3. Delta method with the viewer as the unit (views of one viewer are "
           "correlated). 4. Compare the CI with -0.5%.",
     solution=q3,
     why="The split is fine (SRM p = 0.45). Plain watch time is -0.45% with a wide CI (-1.19% to +0.28%) that "
         "includes values beyond the accepted cost. CUPED (correlation about 0.87 here) narrows it to -0.17%, CI "
         "-0.54% to +0.19%: the cost is small and at most about half a percent, right at leadership's limit. "
         "The skip rate rises from 18.03% to 18.44% (+2.3% relative), clearly significant (z = 9.5): viewers find "
         "boosted videos slightly less relevant. The ratio needs the delta method because views of one viewer "
         "are not independent." + PM + "\"For viewers, the boost costs at most about half a percent of watch "
         "time (best estimate -0.2%), but people skip boosted videos a bit more (skip rate +2.3%), so the feed "
         "is slightly less relevant; the cost is within the limit but not free.\"",
     mistakes="Skipping the SRM check. Reporting the plain CI and concluding the cost may be over 1%. Computing "
              "the skip-rate SE with views as independent trials.",
     learn=["stats-ab-analysis", "stats-cuped", "stats-ratio-metrics"])
shown(ex)

# ---------------------------------------------------------------- Part 4 creator-side results
q4 = '''rows = []
for b, x in creators.groupby("followers"):
    m = smf.ols("videos ~ C(group) + pre_videos", x).fit(cov_type="HC1")
    base = x[x.group == "control"].videos.mean()
    est, se = m.params.iloc[1], m.bse.iloc[1]
    rows.append((b, len(x), round(base, 2), f"{est / base:+.1%}",
                 f"[{(est - 1.96 * se) / base:+.1%}, {(est + 1.96 * se) / base:+.1%}]", round(m.pvalues.iloc[1], 3)))
print(pd.DataFrame(rows, columns=["followers", "creators", "control_mean", "lift", "95% CI", "p"]))
el = creators[creators.followers != "1k+"]
m = smf.ols("videos ~ C(group) + pre_videos", el).fit(cov_type="HC1")
print(f"all eligible creators: {m.params.iloc[1] / el[el.group == 'control'].videos.mean():+.1%}")
#   followers  creators  control_mean   lift           95% CI     p
# 0     0-100     30238          4.78  +9.8%  [+8.4%, +11.3%]  0.00
# 1    100-1k     20880          4.87  +3.4%   [+1.7%, +5.1%]  0.00
# 2       1k+      8882          7.55  +0.6%   [-1.5%, +2.7%]  0.59
# all eligible creators: +7.2%'''
ex.q("Part 4: do creators post more?", minutes=8, kind="python",
     prompt="The creator-side test ran 4 weeks (`creators`, simulated). Creators with 1k+ followers were "
            "randomized too, but the boost never applies to them.\n\n"
            "1. Estimate the relative lift in videos posted for each follower bucket, adjusting for `pre_videos`, "
            "with 95% CIs.\n"
            "2. What is the 1k+ bucket good for?\n"
            "3. The examiner asks: *\"Is +X% what we will get after launch?\"* Answer carefully." +
            PM + "the creator-side result and its main caveat.",
     hint1="Signal: per-segment effects where one segment cannot be affected. Methods: regression adjustment "
           "(ANCOVA) per segment, a placebo segment, and interference reasoning.",
     hint2="1. Per bucket: `videos ~ C(group) + pre_videos` with robust SEs; divide by the control mean. 2. The "
           "1k+ creators are a placebo: their effect should be zero. 3. Where do boosted creators' extra views "
           "come from in this test, and at full launch?",
     solution=q4,
     why="The boost works most for the smallest creators (+9.8%, CI +8.4% to +11.3%), less for 100 to 1k "
         "(+3.4%), +7.2% across all eligible creators, and the 1k+ placebo shows nothing (+0.6%, p = 0.59), which supports that randomization and "
         "measurement are sound. But the creator test overstates the launch effect: here treated creators get "
         "extra impressions partly taken from **control** small creators, which pushes control down and widens "
         "the gap. At launch all small creators share the same extra exposure, so each gets less. The market "
         "holdout from Part 1 is needed to size the real effect; a reasonable plan is to treat these numbers as "
         "an upper bound." + PM + "\"The boost makes the smallest creators post about 10% more, and the "
         "placebo group confirms the test is clean; the real launch gain will be smaller, because in the test "
         "boosted creators partly took views from other small creators, so we will confirm the size with a "
         "few markets kept without the boost.\"",
     mistakes="Forgetting the placebo check. Pooling all buckets including 1k+ (dilutes the effect). Reporting "
              "the creator-test lift as the launch impact.",
     learn=["stats-heterogeneous-effects", "stats-network-effects", "stats-regression"])
shown(ex)

# ---------------------------------------------------------------- Part 5 decision
ex.q("Part 5: the recommendation and follow-ups", minutes=8, kind="text",
     prompt="The examiner says: *\"You have 3 minutes with the VP. What do you recommend?\"* Then come "
            "three follow-ups. Answer all of them.\n\n"
            "1. Your recommendation, with the numbers from Parts 3 and 4 and a launch plan.\n"
            "2. Follow-up A: *\"How do you trade 0.2% of watch time against 10% more posts by small creators?\"*\n"
            "3. Follow-up B: *\"Creators might stay under 1,000 followers on purpose to keep the boost. How would "
            "you detect that?\"*\n"
            "4. Follow-up C: *\"How will we know in 6 months that it was the right call?\"*" +
            PM + "the 3-minute recommendation.",
     hint1="Signal: a launch decision with a measured cost on one side and a benefit on the other. Method: "
           "decision with conditions, an exchange rate between metrics, gaming checks (bunching at a "
           "threshold), and long-term holdouts.",
     hint2="1. Cost: at most 0.5% watch time, +2.3% skips. Benefit: +10% posting for 0 to 100 followers, smaller "
           "after launch. 2. Exchange rate: value of a retained creator in future content and watch time. 3. "
           "Look at the follower distribution near 1,000 (bunching). 4. Long-term holdout and creator retention.",
     solution="""**1. Recommendation.** Launch Creator Boost gradually, with a long-term holdout. The viewer cost is
small and bounded (watch time -0.17%, CI -0.54% to +0.19%), with a real but small relevance cost (skip rate +2.3%).
Small creators respond strongly (+9.8% posts for 0 to 100 followers, +3.4% for 100 to 1k; the placebo is flat), but
that is an upper bound because of interference. Plan: launch to 90% of markets, keep 10% of markets as a holdout for
6 months to measure the total effect on creator supply and viewer watch time at the market level; tune the boost to
send more of the extra exposure to boosted videos with good early signals (lower skips) to recover relevance.

**2. Exchange rate.** Translate both into the same long-term unit. A creator who keeps posting produces future videos
and future watch time. Estimate (from history) the watch time a retained small creator's videos generate over 12
months, multiply by the extra retained creators, and compare with the 0.2% watch-time cost per year. Leadership
should set the exchange rate once (for example "1% more active creators is worth 0.3% watch time") so that every
creator-side launch is judged consistently.

**3. Gaming at 1,000 followers.** Look for **bunching**: a histogram of follower counts should be smooth around
1,000; a pile-up just below 1,000 after launch (compared with before, and with the holdout markets) signals gaming,
for example creators deleting followers or opening second accounts. A density test (McCrary style) at the threshold
measures it. Remedy: phase the boost out smoothly (no hard cliff) or base eligibility on account age.

**4. In 6 months.** Compare treated versus holdout markets on: share of new creators still posting after 8 weeks,
total videos posted, total viewer watch time and DAU. Check that the creator gain persists (not novelty) and that
the viewer cost did not grow. If the holdout shows no lasting creator gain, roll back.

**Say it to a PM:** "Creator Boost makes the smallest creators post about 10% more and costs viewers at most half a
percent of watch time, so I recommend launching it in most markets while keeping a few without it for six months;
that tells us the true long-term effect, and we will fix the slight drop in feed relevance by boosting only videos
that viewers do not skip.\"""",
     why="The final part tests synthesis: a clear decision, numbers with uncertainty, a plan that resolves the "
         "remaining unknowns (holdout), and concrete answers to follow-ups (exchange rate, bunching, long-term "
         "measurement).",
     learn=["stats-launch-decisions", "stats-causal-psm-rd-iv", "stats-case-framework"])

ex.save()
