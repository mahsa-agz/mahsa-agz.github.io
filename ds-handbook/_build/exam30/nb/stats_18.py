import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_mid_common import start, q, pm

# Day 18 stats: focus difference-in-differences; review regression.
EXTRA = '''
# SIMULATED city panel (made up, so we know the truth). 40 cities x 20 weeks. A food-delivery app launches
# "group ordering" in 15 cities in week 12. Metric: weekly orders per 1,000 users.
def make_panel(extra_trend=0.0, effect=3.0, seed=18):
    rng = np.random.default_rng(seed)
    city = np.repeat(np.arange(40), 20)
    week = np.tile(np.arange(20), 40)
    treated = (city < 15).astype(int)                        # launch cities were chosen, not random
    city_level = rng.normal(50, 5, 40)[city] + 6 * treated    # launch cities are bigger to begin with
    season = 2 * np.sin(week / 3)                             # shared ups and downs
    post = (week >= 12).astype(int)
    y = (city_level + season + extra_trend * treated * week + effect * treated * post
         + rng.normal(0, 1.5, len(city)))
    return pd.DataFrame(dict(city=city, week=week, treated=treated, post=post, y=y))

panel = make_panel()                       # parallel trends hold, true effect = 3
panel_bad = make_panel(extra_trend=0.4)    # launch cities were already growing faster, true effect = 3
print(panel.shape, panel_bad.shape)
'''
ex = start(18, ["mpg"], extra=EXTRA,
           note="Q1 to Q3 use a **simulated** city panel built in the setup cell (`panel`, `panel_bad`): one row per "
                "city and week with `city`, `week` (0 to 19), `treated` (1 = launch city), `post` (1 from week 12), "
                "`y` (orders per 1,000 users). The true launch effect is +3.0 in both tables; in `panel_bad` the "
                "launch cities also grow 0.4 per week faster on their own. Q4 (review) uses the real `mpg` data.")

# ---------------------------------------------------------------- Q1
q(ex, title="The launch cities went up. By how much because of us?", minutes=7,
  prompt="Using `panel`:\n\n"
         "(a) Compute the four means (treated/control x pre/post) and the difference-in-differences by hand. Also "
         "compute the naive 'after minus before in launch cities' and 'launch vs other cities after launch'.\n\n"
         "(b) Fit `y ~ treated * post` with standard errors clustered by city "
         "(`.fit(cov_type='cluster', cov_kwds={'groups': panel.city})`). Compare the clustered SE with the "
         "default SE.\n\n"
         "(c) Say it to a PM.\n\n"
         "Follow-up: what does adding city and week fixed effects (`y ~ treated:post + C(city) + C(week)`) change?",
  stub="# your code here",
  hint1="Signal: a launch in some units at a known time, no randomisation, data before and after for both. Method: "
        "difference-in-differences (2x2), as a regression with an interaction term.",
  hint2="1. `m = panel.groupby(['treated', 'post']).y.mean()`. 2. DiD = (m[1,1] - m[1,0]) - (m[0,1] - m[0,0]). "
        "3. The coefficient of `treated:post` equals that number. 4. Cluster by city because weeks of the same "
        "city are correlated.",
  solution='''m = panel.groupby(["treated", "post"]).y.mean()
did = (m[1, 1] - m[1, 0]) - (m[0, 1] - m[0, 0])
print(m.round(2))
print(f"before/after in launch cities {m[1, 1] - m[1, 0]:.2f}, launch vs others after {m[1, 1] - m[0, 1]:.2f}, "
      f"DiD {did:.2f}")
plain = smf.ols("y ~ treated * post", data=panel).fit()
clus = smf.ols("y ~ treated * post", data=panel).fit(cov_type="cluster", cov_kwds={"groups": panel.city})
print(f"coef {clus.params['treated:post']:.2f}, SE default {plain.bse['treated:post']:.2f}, "
      f"SE clustered {clus.bse['treated:post']:.2f}")
fe = smf.ols("y ~ treated:post + C(city) + C(week)", data=panel).fit(cov_type="cluster",
                                                                    cov_kwds={"groups": panel.city})
print(f"two-way FE: coef {fe.params['treated:post']:.2f}, SE {fe.bse['treated:post']:.2f}")
# means: control pre 51.56, post 49.29; launch pre 59.21, post 59.95
# before/after in launch cities 0.75, launch vs others after 10.67, DiD 3.02
# coef 3.02, SE default 0.70, SE clustered 0.23
# two-way FE: coef 3.02, SE 0.24''',
  why="The before/after change in launch cities mixes the launch with seasonality; the launch-vs-others gap mixes "
      "it with the fact that launch cities were bigger to start with. DiD subtracts both: the control cities' change "
      "estimates what would have happened in launch cities without the launch (parallel trends). Here: before/after "
      "says +0.75 (the season went down), launch vs others says +10.67 (they were bigger anyway), DiD says 3.02, "
      "close to the true 3. Weekly rows of the same city are not independent, so cluster by city. Note the "
      "direction: here the default SE (0.70) is *too large*, because it counts the stable city-to-city "
      "differences as noise although DiD differences them away; the clustered SE is 0.23. In real panels, "
      "shocks that persist over weeks usually make the default SE *too small* (Bertrand, Duflo and Mullainathan "
      "2004). Either way, the default is wrong for panel data."
      + pm("Orders in the launch cities rose by about 3 per 1,000 users more than in comparable cities over the same "
           "weeks, and that extra rise is our best estimate of what group ordering added.",
           [("Fixed effects?", "City fixed effects absorb every city's own level, week fixed effects absorb the "
             "shared season, so only the interaction is left. In a clean 2x2 with a balanced panel the estimate is "
             "the same (3.02 here) and the SE is about the same (0.24 vs 0.23); fixed effects matter more when the "
             "panel is unbalanced or you add covariates. With staggered launch dates "
             "this two-way fixed effects model can be biased (use Callaway-Sant'Anna or similar).")]),
  complexity="O(n) for the means; O(n p^2) for the FE regression with about 60 dummies.",
  mistakes="Using the default OLS SE for panel data (wrong when errors are correlated within a city; usually too small). Calling "
           "the before/after change in treated cities 'the effect'.",
  learn=["stats-causal-did", "stats-regression"])

# ---------------------------------------------------------------- Q2
q(ex, title="Were the launch cities already growing?", minutes=7,
  prompt="Now use `panel_bad` (true effect still +3.0).\n\n"
         "(a) Run the same 2x2 DiD regression. How wrong is it?\n\n"
         "(b) Check pre-trends: on pre-launch weeks only (week < 12), fit `y ~ treated * week` and look at "
         "`treated:week`. Do the same on `panel`.\n\n"
         "(c) Placebo test: on pre-launch weeks only, pretend the launch was at week 6 and run the DiD. What should "
         "you find if the design is sound?\n\n"
         "(d) Say it to a PM.\n\n"
         "Follow-up: how could you still estimate the effect from `panel_bad`?",
  stub="# your code here",
  hint1="Signal: doubt about the key DiD assumption. Checks: pre-period trend difference and a placebo (fake) "
        "launch date in the pre-period.",
  hint2="1. `pre = df[df.week < 12]`. 2. `smf.ols('y ~ treated * week', data=pre)` with city clusters. "
        "3. Placebo: `pre.assign(post=(pre.week >= 6).astype(int))`, then `y ~ treated * post`.",
  solution='''def did(df):
    fit = smf.ols("y ~ treated * post", data=df).fit(cov_type="cluster", cov_kwds={"groups": df.city})
    return fit.params["treated:post"], fit.bse["treated:post"]

def pretrend(df):
    pre = df[df.week < 12]
    fit = smf.ols("y ~ treated * week", data=pre).fit(cov_type="cluster", cov_kwds={"groups": pre.city})
    return fit.params["treated:week"], fit.pvalues["treated:week"]

def placebo(df):
    pre = df[df.week < 12].assign(post=lambda d: (d.week >= 6).astype(int))
    return did(pre)

for name, df in [("panel", panel), ("panel_bad", panel_bad)]:
    b, se = did(df)
    s, p = pretrend(df)
    pb, pse = placebo(df)
    print(f"{name}: DiD {b:.2f} (SE {se:.2f}) | pre-trend slope {s:.3f}, p {p:.3g} | placebo {pb:.2f} (SE {pse:.2f})")
# panel: DiD 3.02 (SE 0.23) | pre-trend slope 0.039, p 0.325 | placebo 0.07 (SE 0.32)
# panel_bad: DiD 7.02 (SE 0.23) | pre-trend slope 0.439, p 8.57e-29 | placebo 2.47 (SE 0.32)''',
  why="When launch cities were already growing faster, DiD adds that growth to the effect: 7.02 instead of 3, and the "
      "small SE (0.23) makes the wrong answer look precise. The bias is the extra trend times the gap between the "
      "average post and pre week: 0.4 * (15.5 - 5.5) = 4. Both checks catch it: "
      "the pre-period slope difference is 0.439 per week (p about 1e-28) and the fake week-6 launch shows an 'effect' "
      "of 2.47 although nothing happened. On the clean panel both are near zero (slope 0.039, p = 0.33; placebo "
      "0.07). Passing the checks does not prove parallel "
      "trends after launch, but failing them is a strong warning."
      + pm("The launch cities were already growing faster before we launched, so the simple comparison gives the "
           "feature credit for growth that was happening anyway; the real effect is smaller than that number "
           "suggests.",
           [("Still estimate it?", "Model the pre-trend: add a group-specific linear trend (`treated:week`) and "
             "check that it is stable; use synthetic control (weight control cities so their pre-period path "
             "matches); or pick control cities matched on pre-period growth. Each relies on its own assumption, so "
             "report several."),
            ("Event study plot", "Estimate one coefficient per week relative to launch (leads and lags). Leads near "
             "0 support the design; lags show how the effect builds up or fades.")]),
  complexity="O(n) per regression.",
  mistakes="Testing pre-trends with too few pre-periods and calling 'not significant' proof. Choosing control "
           "cities after looking at the outcome.",
  learn=["stats-causal-did"])

# ---------------------------------------------------------------- Q3
q(ex, title="Case: a launch in one country only", minutes=6, kind="text",
  prompt="Your app launched a new onboarding flow in Korea only, on 1 March, for business reasons (no A/B test). "
         "The PM asks: 'Did it improve 7-day retention of new users?' Describe how you would estimate it with a "
         "difference-in-differences design in 5 to 7 bullets: comparison group, metric and unit, time windows, "
         "checks, threats, and how you report it. Then give the PM the two-sentence version.\n\n"
         "Follow-up: other countries also got the new flow gradually over three months. What changes?",
  hint1="Framework: who is treated and when, who is the counterfactual, parallel-trend evidence, threats "
        "(concurrent events, spillovers, composition changes), uncertainty.",
  hint2="1. Control: similar countries without the launch (Japan, Taiwan), picked on pre-period trends. 2. Unit: "
        "weekly signup cohorts per country. 3. Several weeks pre and post. 4. Event study + placebo. 5. Threats: "
        "Korea-only marketing, holidays, new acquisition channels changing who signs up.",
  solution="""- **Treated group and timing:** new users in Korea, signup cohorts from 1 March. Pre-period: 8 to 12
  weekly cohorts before; post: 6 to 8 weekly cohorts after (each cohort needs 7 days to mature).
- **Control group:** countries that did not get the flow and had similar retention *trends* before March (for
  example Japan and Taiwan), or a weighted mix of countries (synthetic control) matched on the pre-period path.
- **Metric and unit:** day-7 retention of each weekly signup cohort per country, weighted by cohort size. Also look
  at onboarding completion (the mechanism) and day-30 retention later.
- **Estimate:** `retention ~ korea * post` or with country and week fixed effects; SEs clustered by country, or with
  few countries, use a permutation (placebo) test that assigns the 'launch' to each control country in turn.
- **Checks:** event study (leads near 0), placebo launch dates before March, and stable signup mix (channels,
  platforms) in Korea before and after.
- **Threats:** Korea-specific events in March (marketing push, a holiday, a competitor outage), acquisition changes
  that alter who signs up (composition), and too few control countries for reliable SEs.
- **Report:** the effect with a range, the checks that passed, and the main assumption in one line.

**Say it to a PM:** "Compared with similar countries over the same weeks, Korean new users' 7-day retention rose
about X points more after the new onboarding; this assumes Korea would otherwise have moved like those countries, which
held in the 3 months before launch."

**Follow-up (staggered rollout):** each country has its own launch date. Use an estimator built for staggered timing
(Callaway and Sant'Anna, Sun and Abraham, or stacked DiD); the plain two-way fixed effects regression can give a
misleading average because already-treated countries act as controls for later ones, which is wrong when effects
change over time.""",
  why="Examiners want to hear the counterfactual named explicitly, the parallel-trend assumption, concrete "
      "checks, and threats specific to the setting. Few treated units (one country) also means standard errors "
      "need care; a permutation test is a good answer.",
  mistakes="Comparing Korea before vs after only. Using all other countries without checking trends. Forgetting "
           "cohort maturity for a 7-day metric.",
  learn=["stats-causal-did", "stats-case-framework"])

# ---------------------------------------------------------------- Q4 review
q(ex, title="Heavy cars, thirsty cars", minutes=6, review=True,
  prompt="Using `mpg` (drop rows with missing `horsepower`):\n\n"
         "(a) Fit `mpg ~ weight + horsepower + displacement + model_year`. Interpret the `weight` coefficient per "
         "1,000 lbs and the `model_year` coefficient.\n\n"
         "(b) Compute the variance inflation factor (VIF) for the four predictors. What does it say about the "
         "`horsepower` and `displacement` coefficients?\n\n"
         "(c) Say it to a PM (a car buyer's guide editor).",
  stub="from statsmodels.stats.outliers_influence import variance_inflation_factor\n"
       "cars = mpg.dropna(subset=[\"horsepower\"])\n# your code here",
  hint1="Signal: correlated predictors in a regression. Method: OLS plus VIF to diagnose multicollinearity.",
  hint2="1. `smf.ols(...).fit()`. 2. `X = sm.add_constant(cars[cols])`, then "
        "`variance_inflation_factor(X.values, i)` for i = 1..4. 3. VIF above about 5 to 10 means unstable "
        "coefficients.",
  solution='''from statsmodels.stats.outliers_influence import variance_inflation_factor
cars = mpg.dropna(subset=["horsepower"])
fit = smf.ols("mpg ~ weight + horsepower + displacement + model_year", data=cars).fit()
print(pd.DataFrame({"coef": fit.params, "p": fit.pvalues}).round(4))
print("R2", round(fit.rsquared, 3), " weight per 1000 lbs:", round(1000 * fit.params["weight"], 2))
cols = ["weight", "horsepower", "displacement", "model_year"]
X = sm.add_constant(cars[cols])
print({c: round(variance_inflation_factor(X.values, i + 1), 1) for i, c in enumerate(cols)})
# weight -0.0066 (p < 0.001), horsepower -0.0067 (p 0.53), displacement 0.0018 (p 0.73), model_year 0.7505 (p < 0.001)
# R2 0.808  weight per 1000 lbs: -6.59
# VIF: weight 8.1, horsepower 5.6, displacement 10.4, model_year 1.2''',
  why="Weight, horsepower and displacement are strongly correlated (big engines sit in heavy cars), so their "
      "individual coefficients are unstable: VIFs of 8.1 (weight), 5.6 (horsepower) and 10.4 (displacement) mean "
      "inflated SEs, and displacement even gets a positive sign (bigger engine, more mpg?) with p = 0.73. Weight "
      "still stands out: -6.59 mpg per 1,000 lbs. R-squared is 0.808. The model as a whole still predicts well. The model_year coefficient (VIF 1.2) is stable: +0.75 mpg per "
      "model year at the same weight and power."
      + pm("Weight is the main driver of fuel use: each extra 1,000 lbs costs about 6.6 miles per gallon, and newer "
           "cars of the same weight do about 0.75 mpg better each model year; engine size and power overlap so much with weight that "
           "we cannot separate their effects from this data.",
           [("Fix for multicollinearity?", "Drop or combine overlapping variables (for example keep weight only), "
             "use ridge regression, or simply do not interpret the individual collinear coefficients; prediction is "
             "unaffected.")]),
  complexity="O(n p^2).",
  mistakes="Dropping a variable because its p-value is high when the cause is collinearity. Reading the weight "
           "coefficient per pound without rescaling.",
  learn=["stats-regression", "ai-linear-regression"])

ex.save()
