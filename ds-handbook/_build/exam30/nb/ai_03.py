import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_easy_common import start, qc

# Day 3 AI: focus linear-regression; review bias-variance.
ex = start(3, loads=["diamonds"],
           builtin="`load_diabetes()` from scikit-learn (built in): 442 patients, 10 standardised features, "
                   "target = disease progression after one year.")

qc(ex, title="What does least squares assume?", minutes=4, kind="text",
   prompt="An examiner asks: \"What are the assumptions of linear regression, and which ones matter if I only "
          "care about prediction?\" Answer in about 90 seconds. Include the closed-form solution.",
   hint1="Signal: 'assumptions of OLS'. Pattern: linear regression theory (the LINE assumptions plus no perfect "
         "multicollinearity).",
   hint2="1. Model: `y = X b + e`. 2. Fit: minimise the sum of squared residuals, `b = (X^T X)^-1 X^T y`. "
         "3. List: Linearity, Independence, Normal errors, Equal variance, plus no perfect collinearity. "
         "4. Split them into 'needed for unbiased coefficients', 'needed for valid p-values', 'needed for "
         "prediction'.",
   solution="**Model answer (about 90 s):**\n\n"
            "\"Linear regression models `y = X b + e` and picks `b` to minimise the sum of squared residuals; the "
            "closed form is `b = (X^T X)^-1 X^T y` (in practice solved with QR or gradient descent, not an "
            "explicit inverse).\n\n"
            "The classic assumptions: (1) **linearity**: the mean of y is linear in the features (after any "
            "transforms); (2) **independent errors**, which breaks with time series or repeated users; "
            "(3) **constant error variance** (homoscedasticity); (4) **normal errors**, only needed for exact "
            "small-sample tests and intervals; (5) **no perfect multicollinearity**, so `X^T X` is invertible; and "
            "for a causal reading, errors uncorrelated with the features (no omitted confounders).\n\n"
            "For pure prediction, what matters most is that the functional form is good enough and that train and "
            "production data come from the same distribution. Heteroscedasticity, correlated errors and "
            "non-normality mainly break the standard errors and p-values, not the predictions. Multicollinearity "
            "makes single coefficients unstable and hard to interpret but usually does not hurt predictions; "
            "ridge regression fixes the instability.\"",
   why="The good answer separates three goals: unbiased coefficients, valid inference, good prediction. That shows "
       "you know why each assumption exists rather than reciting a list.",
   mistakes="Saying the features must be normally distributed (only the errors, and only for inference). Saying "
            "collinearity biases the coefficients (it inflates their variance). Forgetting the closed form.",
   learn=["ai-linear-regression"])

sol2 = '''def ols(X, y):
    """Least squares with an intercept. Returns [intercept, b1, ..., bp]."""
    X1 = np.column_stack([np.ones(len(X)), X])     # add a column of ones for the intercept
    beta, *_ = np.linalg.lstsq(X1, y, rcond=None)   # solves min ||X1 b - y||^2 stably (no explicit inverse)
    return beta'''
tests2 = '''from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
Xd, yd = load_diabetes(return_X_y=True)
ref = LinearRegression().fit(Xd, yd)
check(ols, [
    ((np.array([[0.0], [1.0], [2.0]]), np.array([1.0, 3.0, 5.0])), [1.0, 2.0]),          # y = 1 + 2x exactly
    ((np.array([[0.0], [1.0], [2.0], [3.0]]), np.array([1.0, 2.0, 2.0, 4.0])), [0.9, 0.9]),  # best line, not exact
    ((Xd, yd), np.r_[ref.intercept_, ref.coef_]),                                           # same as sklearn
], tol=1e-6)'''
qc(ex, title="Least squares by hand", minutes=6,
   prompt="Write `ols(X, y)` with numpy only. It fits a linear regression **with an intercept** and returns the "
          "array `[intercept, b1, ..., bp]`.\n\n"
          "Example: `X = [[0], [1], [2]]`, `y = [1, 3, 5]` gives `[1.0, 2.0]` (the line `y = 1 + 2x`).\n\n"
          "The last test compares your coefficients with scikit-learn's `LinearRegression` on the diabetes data.",
   stub="def ols(X, y):\n    # your code here\n    pass",
   tests=tests2,
   hint1="Signal: 'fit a line, numpy only'. Pattern: the normal equations, `b = (X^T X)^-1 X^T y`.",
   hint2="1. Add a column of ones to X for the intercept. 2. Solve the least-squares problem with "
         "`np.linalg.lstsq(X1, y, rcond=None)` (or `np.linalg.solve(X1.T @ X1, X1.T @ y)`). 3. Return the "
         "coefficient vector.",
   solution=sol2,
   why="Least squares minimises `||X1 b - y||^2`; setting the gradient to zero gives the normal equations "
       "`X1^T X1 b = X1^T y`. `lstsq` solves them through an SVD, which is stable even when features are nearly "
       "collinear, while `inv(X.T @ X)` can lose precision. In the second test the best line is `y = 0.9 + 0.9x`: "
       "the mean point (1.5, 2.25) lies on it, as it always does for OLS with an intercept.",
   complexity="`O(n p^2 + p^3)` time, `O(n p)` memory. For huge n or p use gradient descent (SGD) instead.",
   mistakes="Forgetting the intercept column (the line is forced through the origin). Using `np.linalg.inv` on "
            "an ill-conditioned matrix. Mixing up the order of the returned coefficients.",
   learn=["ai-linear-regression", "ai-gradient-descent"])

sol3 = '''from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

tr, te = train_test_split(diamonds, test_size=0.25, random_state=0)

raw = LinearRegression().fit(tr[["carat"]], tr["price"])
print("raw: slope", round(raw.coef_[0]), " test R2", round(raw.score(te[["carat"]], te["price"]), 3))
# out: raw: slope 7745  test R2 0.851

loglog = LinearRegression().fit(np.log(tr[["carat"]]), np.log(tr["price"]))
print("log-log: slope", round(loglog.coef_[0], 3), " test R2 (log scale)",
      round(loglog.score(np.log(te[["carat"]]), np.log(te["price"])), 3))
# out: log-log: slope 1.674  test R2 (log scale) 0.934

# the raw model predicts negative prices for small stones
print("raw model, price of a 0.2 carat stone:", round(raw.predict(pd.DataFrame({"carat": [0.2]}))[0]))
# out: raw model, price of a 0.2 carat stone: -700'''
qc(ex, title="Price versus carat: straight or logged?", minutes=7,
   prompt="Use `diamonds`. Split 75/25 with `random_state=0`.\n\n"
          "1. Fit `price ~ carat`. Print the slope (rounded) and the test R^2.\n"
          "2. Fit `log(price) ~ log(carat)`. Print the slope (3 decimals) and the test R^2 on the log scale.\n"
          "3. Print what the first model predicts for a 0.2 carat diamond.\n\n"
          "Interpret the log-log slope in one sentence a jeweller understands. Why is the log model better here?",
   stub="# diamonds is loaded. Your code here\n",
   hint1="Signal: a price that grows faster than linearly and is always positive, with a right-skewed "
         "distribution. Pattern: log transform; a log-log slope is an elasticity.",
   hint2="1. `LinearRegression().fit(tr[['carat']], tr['price'])`. 2. Same with `np.log` applied to both. "
         "3. In a log-log model, a 1% increase in x changes y by about `slope` %.",
   solution=sol3,
   why="Price grows faster than linearly with carat, and its spread grows with its level. The straight line "
       "misses the curve, predicts -700 dollars for a 0.2 carat stone, and has residuals that fan out "
       "(heteroscedasticity). On the log-log scale the relation is close to a line with stable spread. "
       "Interpretation: a 1% heavier diamond costs about 1.67% more, so a 10% heavier stone costs about "
       "`1.1^1.674 - 1 = 17%` more. Note that the two R^2 values are on different scales (dollars versus log "
       "dollars), so 0.934 versus 0.851 is not a fair head-to-head comparison; compare RMSE in dollars after "
       "back-transforming for that.",
   complexity="One-feature least squares on about 40,000 rows: milliseconds.",
   mistakes="Comparing R^2 across different targets as if it were the same metric. Back-transforming with "
            "`exp(prediction)` and forgetting it estimates the median, not the mean (a smearing correction "
            "fixes it). Reading the log-log slope as dollars per carat.",
   learn=["ai-linear-regression", "ai-features-imbalance"])

sol4 = '''import statsmodels.formula.api as smf

order = ["Fair", "Good", "Very Good", "Premium", "Ideal"]
summary = diamonds.groupby("cut").agg(mean_price=("price", "mean"), mean_carat=("carat", "mean")).loc[order]
for cut, row in summary.iterrows():
    print(f"{cut:10s} mean price {row.mean_price:6.0f}  mean carat {row.mean_carat:.2f}")
# out: Fair       mean price   4359  mean carat 1.05
# out: Good       mean price   3929  mean carat 0.85
# out: Very Good  mean price   3982  mean carat 0.81
# out: Premium    mean price   4584  mean carat 0.89
# out: Ideal      mean price   3458  mean carat 0.70

fit = smf.ols("np.log(price) ~ np.log(carat) + C(cut, Treatment('Fair'))", data=diamonds).fit()
for cut in order[1:]:
    b = fit.params[f"C(cut, Treatment('Fair'))[T.{cut}]"]
    print(f"{cut:10s} vs Fair, same carat: {100 * (np.exp(b) - 1):+.1f}% price")
# out: Good       vs Fair, same carat: +17.7% price
# out: Very Good  vs Fair, same carat: +27.2% price
# out: Premium    vs Fair, same carat: +26.9% price
# out: Ideal      vs Fair, same carat: +37.3% price'''
qc(ex, title="Why are the best cuts the cheapest?", minutes=6,
   prompt="A PM looks at `diamonds` and says: \"Ideal-cut diamonds have the lowest average price, so cut quality "
          "does not matter to buyers.\"\n\n"
          "1. Print mean price and mean carat per cut (order: Fair, Good, Very Good, Premium, Ideal).\n"
          "2. Fit `log(price) ~ log(carat) + cut` with Fair as the reference level (statsmodels formula is "
          "fine). Print, for each cut, the price difference versus Fair **at the same carat**, in percent.\n\n"
          "Explain to the PM what is going on.",
   stub="import statsmodels.formula.api as smf\n\n# your code here\n",
   hint1="Signal: a raw group comparison where a third variable differs a lot between groups. Pattern: "
         "confounding; control for it with a multiple regression.",
   hint2="1. `groupby('cut').agg(...)`. 2. `smf.ols(\"np.log(price) ~ np.log(carat) + C(cut, Treatment('Fair'))\", "
         "data=diamonds).fit()`. 3. A dummy coefficient b in a log model means `exp(b) - 1` percent.",
   solution=sol4,
   why="Carat drives price, and Ideal stones are much smaller on average (0.70 carat versus 1.05 for Fair). The "
       "raw averages mix the effect of cut with the effect of size. Holding carat fixed, the order flips: every "
       "better cut is worth more than Fair, and an Ideal stone costs about 37% more than a Fair stone of the same weight. For the PM: cut matters a lot; "
       "the raw average is confounded by size. (Color and clarity also differ by cut, so a full model would "
       "add them too.)",
   complexity="One regression with 5 parameters on 53,940 rows: well under a second.",
   mistakes="Reading a dummy coefficient in a log model as dollars. Forgetting which level is the reference. "
            "Concluding causality: this is still observational data.",
   learn=["ai-linear-regression", "stats-regression"])

qc(ex, title="More features, better model?", minutes=3, kind="text", review=True,
   prompt="You have 500 rows and a linear regression with 10 features. A teammate adds 200 more features "
          "(mostly weak or noise). What happens to training R^2, to test error, and to the bias and the variance "
          "of the model? What would you do instead?",
   hint1="Signal: many features relative to rows. Pattern: bias-variance; training R^2 never goes down when you "
         "add features.",
   hint2="1. Training fit can only improve (OLS minimises over a larger set). 2. Each extra coefficient is "
         "estimated with noise, so variance rises. 3. Remedies: regularization, feature selection with CV, "
         "more data.",
   solution="**Model answer:** \"Training R^2 can only go up: OLS with more columns minimises the same loss over "
            "a larger set, so it fits at least as well, including the noise. With 210 features and 500 rows, each "
            "coefficient is estimated from little data, so the model's variance rises sharply: the test error "
            "usually goes up even though the bias went down slightly. Adjusted R^2 or a validation set shows it; "
            "plain R^2 hides it. Near `p = n` OLS interpolates the training data and the test error explodes.\n\n"
            "Instead: keep the features but add ridge or lasso and choose the penalty by cross-validation; or "
            "select features with CV (never on the full data); or get more rows. Lasso also tells you which "
            "features carry signal.\"",
   why="Examiners check that you know training metrics cannot judge model size, and that you link 'more "
       "features' to variance, not to 'more information'.",
   mistakes="Saying R^2 can drop on training data. Selecting features on the full data before cross-validation "
            "(leakage, see day 6).",
   learn=["ai-bias-variance", "ai-regularization-cv"])

ex.save()
