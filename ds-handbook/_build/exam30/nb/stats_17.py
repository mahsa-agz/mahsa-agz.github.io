import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_mid_common import start, q, pm

# Day 17 stats: focus regression and interpretation; review CUPED.
ex = start(17, ["tips", "diamonds", "telco"],
           note="Q1 to Q3 use real data. Q4 (review) uses a small **simulated** experiment so that the true effect "
                "is known.")

# ---------------------------------------------------------------- Q1
q(ex, title="What drives the tip?", minutes=6,
  prompt="Fit `tip ~ total_bill + size + smoker + time` on `tips` with OLS (statsmodels formula API).\n\n"
         "(a) Print the coefficients, their p-values and R-squared. Interpret the `total_bill` and `size` "
         "coefficients in one sentence each (units!).\n\n"
         "(b) The residual spread grows with the bill. Refit with heteroscedasticity-robust standard errors "
         "(`cov_type='HC3'`). What changes and what does not?\n\n"
         "(c) Say it to a PM (the PM runs the restaurant).\n\n"
         "Follow-up: how would you test whether smokers tip a different *rate* per dollar of bill?",
  stub="# your code here",
  hint1="Signal: explain a numeric outcome with several drivers at once. Method: multiple linear regression; "
        "each coefficient is 'holding the others fixed'.",
  hint2="1. `fit = smf.ols('tip ~ total_bill + size + smoker + time', data=tips).fit()`. 2. `fit.params`, "
        "`fit.pvalues`, `fit.rsquared`. 3. `.fit(cov_type='HC3')` for robust SEs.",
  solution='''fit = smf.ols("tip ~ total_bill + size + smoker + time", data=tips).fit()
print(pd.DataFrame({"coef": fit.params, "p": fit.pvalues}).round(3))
print("R2", round(fit.rsquared, 3))
rob = smf.ols("tip ~ total_bill + size + smoker + time", data=tips).fit(cov_type="HC3")
print(pd.DataFrame({"se_classic": fit.bse, "se_HC3": rob.bse, "p_HC3": rob.pvalues}).round(3))
#                 coef      p
# Intercept      0.709  0.001
# smoker[T.Yes] -0.083  0.547
# time[T.Lunch]  0.001  0.997
# total_bill     0.094  0.000
# size           0.180  0.042
# R2 0.469
# HC3: total_bill SE 0.009 -> 0.017 (still p < 0.001); size SE 0.088 -> 0.117, p 0.042 -> about 0.12''',
  why="Each coefficient is the expected change in tip for a one-unit change in that variable with the other "
      "variables held fixed. Robust (HC3) standard errors do not change the coefficients at all, only their "
      "uncertainty. Here the total_bill coefficient is 0.094 (94 cents per extra 10 dollars) and size is 0.18 dollars "
      "per extra guest at the same bill. With fan-shaped residuals the classic SEs are too small for the variable "
      "that drives the spread: the total_bill SE almost doubles (0.009 to 0.017, still clearly significant) and "
      "size goes from p = 0.042 to about 0.12, so the size effect is not reliable. R-squared is 0.469."
      + pm("For every extra 10 dollars on the bill, guests tip about 94 cents more; once we know the bill, party "
           "size, smoking and lunch versus dinner add little or nothing we can rely on, and the model explains less than half of the variation "
           "in tips.",
           [("Different rate per dollar?", "Add an interaction: `tip ~ total_bill * smoker + size + time`. The "
             "`total_bill:smoker[T.Yes]` coefficient is the difference in slope; test it with its p-value (robust "
             "SE)."),
            ("Why is R-squared low?", "Tips are noisy person to person. A low R-squared does not make the "
             "coefficient wrong; it limits prediction, not interpretation.")]),
  complexity="O(n p^2) for OLS with n rows and p columns.",
  mistakes="Reading a coefficient without units. Saying 'size does not matter' (it is 'no evidence of an effect "
           "holding the bill fixed': bigger parties already have bigger bills). Forgetting the reference category for "
           "smoker and time.",
  learn=["stats-regression"])

# ---------------------------------------------------------------- Q2
q(ex, title="Better cut, lower price?", minutes=7,
  prompt="Using `diamonds`:\n\n"
         "(a) Mean price by `cut`. Which cut is cheapest on average? Is that surprising?\n\n"
         "(b) Fit `np.log(price) ~ np.log(carat) + C(cut) + C(color) + C(clarity)`. Interpret the `np.log(carat)` "
         "coefficient and the coefficient for `cut = Ideal` (reference is Fair) as a percentage "
         "(`exp(b) - 1`).\n\n"
         "(c) Explain the change from (a) to (b). Say it to a PM (a pricing manager).\n\n"
         "Follow-up: why model log(price) and not price?",
  stub="# your code here",
  hint1="Signal: a raw comparison that is confounded by another variable (size). Concept: omitted variable bias; "
        "a log-log model gives an elasticity.",
  hint2="1. `diamonds.groupby('cut').price.mean()` and also mean carat by cut. 2. `smf.ols('np.log(price) ~ "
        "np.log(carat) + C(cut) + C(color) + C(clarity)', data=diamonds).fit()`. 3. `np.exp(coef) - 1` for the "
        "Ideal row (name `C(cut)[T.Ideal]`).",
  solution='''print(diamonds.groupby("cut")[["price", "carat"]].mean().round(2).sort_values("price"))
fit = smf.ols("np.log(price) ~ np.log(carat) + C(cut) + C(color) + C(clarity)", data=diamonds).fit()
b_carat = fit.params["np.log(carat)"]
b_ideal = fit.params["C(cut)[T.Ideal]"]
print(f"log-carat coef {b_carat:.3f}, Ideal vs Fair {(np.exp(b_ideal) - 1) * 100:.1f}%, R2 {fit.rsquared:.3f}")
#              price  carat
# Ideal      3457.54   0.70
# Good       3928.86   0.85
# Very Good  3981.76   0.81
# Fair       4358.76   1.05
# Premium    4584.26   0.89
# log-carat coef 1.884, Ideal vs Fair 17.5%, R2 0.983''',
  why="Ideal diamonds are cheapest on average (3,458 vs 4,359 for Fair) because they are smaller on average "
      "(0.70 vs 1.05 carat), and carat drives price far "
      "more than cut. Once size (and color, clarity) is held fixed, an Ideal cut costs about 17.5% more than Fair. That is omitted "
      "variable bias: the raw comparison mixes the cut effect with the size difference. In a log-log model the "
      "carat coefficient is an elasticity: 1% more carat means about 1.88% more price (R-squared 0.983)."
      + pm("Ideal-cut stones look cheaper only because they tend to be smaller; for the same size, color and "
           "clarity, an Ideal cut sells for clearly more than a Fair cut, so cut quality does carry a premium.",
           [("Why log(price)?", "Price is right-skewed and its spread grows with size; effects are multiplicative "
             "(a better cut adds a percentage, not a fixed dollar amount). Logs make the relation nearly linear, "
             "stabilise the variance and make coefficients read as percentages."),
            ("Back to dollars?", "`exp(prediction)` estimates the median, not the mean, price; multiply by a "
             "smearing factor (mean of exp(residuals)) for the mean.")]),
  complexity="O(n p^2), about 25 columns after one-hot encoding.",
  mistakes="Reading `b_ideal` directly as a percentage (fine when small, wrong for large values: use exp(b) - 1). "
           "Concluding 'Ideal cut lowers price' from the group means.",
  learn=["stats-regression", "stats-causal-psm-rd-iv"])

# ---------------------------------------------------------------- Q3
q(ex, title="Who churns? Odds ratios for a PM", minutes=7,
  prompt="Using `telco`, create `churn = (Churn == 'Yes')` as 0/1. Fit a logistic regression "
         "`churn ~ tenure + MonthlyCharges + C(Contract)`.\n\n"
         "(a) Print odds ratios (`exp(coef)`) with 95% CIs. Interpret the tenure odds ratio per 12 months and the "
         "two-year contract odds ratio.\n\n"
         "(b) Average marginal effects (`fit.get_margeff().summary_frame()`): what is the effect of +1 month tenure "
         "on churn probability in percentage points?\n\n"
         "(c) Say it to a PM. Is this causal?\n\n"
         "Follow-up: why not also add `TotalCharges`?",
  stub="telco[\"churn\"] = (telco.Churn == \"Yes\").astype(int)\n# your code here",
  hint1="Signal: binary outcome, several drivers. Method: logistic regression; coefficients are log odds ratios, "
        "marginal effects give probability points.",
  hint2="1. `smf.logit('churn ~ tenure + MonthlyCharges + C(Contract)', data=telco).fit(disp=0)`. "
        "2. `np.exp(fit.params)`, `np.exp(fit.conf_int())`. 3. Per 12 months: `exp(12 * b)`. "
        "4. `fit.get_margeff().summary_frame()`.",
  solution='''telco["churn"] = (telco.Churn == "Yes").astype(int)
fit = smf.logit("churn ~ tenure + MonthlyCharges + C(Contract)", data=telco).fit(disp=0)
ors = pd.concat([np.exp(fit.params), np.exp(fit.conf_int())], axis=1)
ors.columns = ["OR", "lo", "hi"]
print(ors.round(3))
print("OR per 12 months tenure:", round(np.exp(12 * fit.params["tenure"]), 3))
me = fit.get_margeff().summary_frame()
print(me["dy/dx"].round(4))
#                             OR     lo     hi
# C(Contract)[T.One year]  0.346  0.284  0.421
# C(Contract)[T.Two year]  0.132  0.096  0.183
# tenure                   0.965  0.961  0.969
# MonthlyCharges           1.029  1.026  1.032
# OR per 12 months tenure: 0.651
# marginal effects: One year -0.1532, Two year -0.2917, tenure -0.0052, MonthlyCharges 0.0041''',
  why="Logistic coefficients are changes in log odds, so `exp(b)` multiplies the odds. Odds ratios are not "
      "probability ratios; for a PM, average marginal effects (in percentage points) are easier. Here: each extra year of tenure multiplies the odds of churn by 0.651 (35% lower odds); a two-year "
      "contract has 0.132 times the odds of month-to-month (CI 0.096 to 0.183). In probability terms, one more month "
      "of tenure lowers churn by about 0.52 pp on average, a two-year contract by about 29 pp versus "
      "month-to-month, and each extra dollar of monthly charge adds about 0.41 pp."
      + pm("Customers on two-year contracts and long-time customers churn far less, and higher monthly bills go with "
           "more churn; this tells us who is at risk, but not yet that moving people to long contracts would keep "
           "them, because loyal customers choose those contracts.",
           [("Causal?", "No. Contract type is chosen by the customer and linked to unobserved loyalty. To learn the "
             "effect of offering a contract, run an experiment (random discount offers), or at least use matching "
             "with good pre-period covariates (day 19)."),
            ("TotalCharges?", "It is roughly tenure times MonthlyCharges, so it is almost collinear with them. "
             "Coefficients become unstable and hard to read (check the VIF). It also has blank strings that must be "
             "converted first.")]),
  complexity="O(iterations * n p^2) for Newton steps.",
  mistakes="Calling an odds ratio of 0.5 'half the churn probability'. Reading coefficients without the reference "
           "category (Month-to-month). Treating the model as causal.",
  learn=["stats-regression", "ai-logistic-regression"])

# ---------------------------------------------------------------- Q4 review
q(ex, title="Adjust for the right variable", minutes=6, review=True,
  prompt="Simulated experiment (seed 7, 20,000 users, 50/50): `x_pre ~ Normal(10, 3)` is last month's sessions. "
         "Treatment raises this month's sessions: `s_during = x_pre + 2 * treat + Normal(0, 1)`. The outcome is "
         "`y = 2 * x_pre + 0.5 * s_during + 1 * treat + Normal(0, 2)`. So the true total effect of treatment on y "
         "is `1 + 0.5 * 2 = 2`.\n\n"
         "(a) Estimate the effect with: plain difference in means; OLS `y ~ treat + x_pre`; OLS "
         "`y ~ treat + s_during`. Print estimate and SE for each.\n\n"
         "(b) Which adjusted estimate is wrong and why? Say it to a PM.",
  stub="rng = np.random.default_rng(7)\nn = 20000\n# your code here",
  hint1="Signal: choosing a covariate for variance reduction. Rule: CUPED or regression adjustment only with "
        "variables measured before assignment; a variable the treatment can change is a mediator.",
  hint2="1. Simulate the four arrays in order. 2. Put them in a DataFrame. 3. Three `smf.ols` fits, read "
        "`params['treat']` and `bse['treat']` (the plain difference is `y ~ treat`).",
  solution='''rng = np.random.default_rng(7)
n = 20000
treat = rng.integers(0, 2, n)
x_pre = rng.normal(10, 3, n)
s_during = x_pre + 2 * treat + rng.normal(0, 1, n)
y = 2 * x_pre + 0.5 * s_during + 1 * treat + rng.normal(0, 2, n)
df = pd.DataFrame(dict(treat=treat, x_pre=x_pre, s_during=s_during, y=y))
for f in ["y ~ treat", "y ~ treat + x_pre", "y ~ treat + s_during"]:
    fit = smf.ols(f, data=df).fit()
    print(f"{f:22s} effect {fit.params['treat']:.3f}  SE {fit.bse['treat']:.3f}")
# y ~ treat              effect 2.126  SE 0.110
# y ~ treat + x_pre      effect 2.011  SE 0.029
# y ~ treat + s_during   effect -2.540  SE 0.041''',
  why="Adjusting for `x_pre` is CUPED in regression form: still unbiased (2.011, truth 2) and the SE drops from 0.110 "
      "to 0.029. Adjusting for `s_during` gives -2.54, the wrong sign with a tiny SE. Holding s_during fixed, a "
      "treated user must have had about 2 fewer sessions last month (`x_pre` is about `s_during - 2`), and x_pre "
      "strongly drives y, so the model compares different kinds of users. Approximately `y = 2.5 * s_during - 3 * "
      "treat + ...`, which suggests -3; because s_during also contains noise, x_pre is only partly recovered and the theoretical "
      "value is about -2.6, matching the -2.54 we got."
      + pm("We can use last month's activity to sharpen the result, but we must not control for anything the new "
           "feature itself changed, or we will hide part of the feature's effect.",
           [("And variables measured during the test that the treatment cannot change (weather, day of week)?",
             "Those are safe but usually help little; the rule of thumb is pre-period only.")]),
  complexity="O(n).",
  mistakes="Using in-experiment engagement as a CUPED covariate because it is highly correlated with the outcome.",
  learn=["stats-cuped", "stats-regression"])

ex.save()
