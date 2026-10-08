import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_easy_common import start, qc

# Day 4 AI: focus logistic-regression; review linear-regression.
ex = start(4, loads=["titanic", "telco"])

qc(ex, title="Why not just fit a line to 0/1?", minutes=4, kind="text",
   prompt="Explain logistic regression in about 90 seconds: why not use linear regression on a 0/1 target, the "
          "model formula, the loss it minimises, and how to read a coefficient.",
   hint1="Signal: binary target, 'probability', 'odds'. Pattern: logistic regression = linear model on the log-odds.",
   hint2="1. Linear regression gives values outside [0, 1] and assumes constant variance. 2. Model: "
         "`log(p / (1 - p)) = b0 + b x`, so `p = 1 / (1 + exp(-z))`. 3. Loss: log loss (cross-entropy), from "
         "maximum likelihood. 4. `exp(b)` = odds ratio for a one-unit increase.",
   solution="**Model answer (about 90 s):**\n\n"
            "\"With a 0/1 target, a straight line predicts values below 0 and above 1, the errors cannot be "
            "normal or constant-variance, and outliers in x pull the line and move the decision boundary. "
            "Logistic regression keeps a linear score `z = b0 + b x` but maps it through the sigmoid, "
            "`p = 1 / (1 + exp(-z))`, so the output is a probability. Equivalently, the **log-odds** "
            "`log(p / (1 - p))` are linear in x.\n\n"
            "It is fitted by maximum likelihood, which means minimising the log loss "
            "`-mean(y log p + (1 - y) log(1 - p))`. That loss is convex, so there is one optimum, found with "
            "gradient methods; there is no closed form. The gradient has a neat form: `X^T (p - y)`.\n\n"
            "A coefficient b means: one more unit of x multiplies the odds by `exp(b)`, holding the others fixed. "
            "For example b = 0.7 gives an odds ratio of about 2. It is not a fixed change in probability: the "
            "probability effect is largest near p = 0.5. The decision boundary `z = 0` is linear, so you need "
            "feature engineering or interactions for curved boundaries.\"",
   why="The three must-say points: sigmoid of a linear score, log loss from maximum likelihood, and odds-ratio "
       "interpretation. Bonus: convexity and the `X^T (p - y)` gradient.",
   mistakes="Saying the coefficient is the change in probability. Saying logistic regression is fitted with "
            "squared error. Calling it a regression model that 'cannot classify' (it is a classifier plus a "
            "threshold).",
   learn=["ai-logistic-regression"])

sol2 = '''def sigmoid(z):
    z = np.asarray(z, dtype=float)
    # exp(-|z|) never overflows; use the right algebraic form for each sign
    e = np.exp(-np.abs(z))
    return np.where(z >= 0, 1 / (1 + e), e / (1 + e))

def log_loss(y, p, eps=1e-15):
    y = np.asarray(y, dtype=float)
    p = np.clip(np.asarray(p, dtype=float), eps, 1 - eps)   # avoid log(0)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))'''
tests2 = '''check(sigmoid, [(0, 0.5), (np.log(3), 0.75), (([-1000.0, 1000.0],), [0.0, 1.0])])
check(log_loss, [(([1, 0], [0.5, 0.5]), np.log(2)),
                 (([1, 1, 0], [0.9, 0.8, 0.3]), 0.22839300363692283),
                 (([1, 0], [1.0, 0.0]), 1e-15)], tol=1e-9)'''
qc(ex, title="Squash and score", minutes=5,
   prompt="Write two numpy functions:\n\n"
          "- `sigmoid(z)`: works on scalars and arrays and does not overflow for `z = -1000` or `z = 1000`.\n"
          "- `log_loss(y, p)`: the mean binary cross-entropy. Clip p to `[1e-15, 1 - 1e-15]` so a perfect "
          "prediction does not give `log(0)`.\n\n"
          "Example: `sigmoid(0) = 0.5`, `sigmoid(log 3) = 0.75`, `log_loss([1, 0], [0.5, 0.5]) = log 2 = 0.693`.",
   stub="def sigmoid(z):\n    # your code here\n    pass\n\ndef log_loss(y, p):\n    # your code here\n    pass",
   tests=tests2,
   hint1="Signal: probabilities from scores, and a loss for probabilities. Pattern: logistic function and "
         "cross-entropy, with numerical stability.",
   hint2="1. `1 / (1 + exp(-z))` overflows for very negative z; for z < 0 use `exp(z) / (1 + exp(z))`. "
         "2. Log loss: `-mean(y log p + (1 - y) log(1 - p))` after clipping p.",
   solution=sol2,
   why="`sigmoid(log 3) = 1 / (1 + 1/3) = 0.75`: log 3 is the log-odds of 3 to 1. Writing the sigmoid with "
       "`exp(-|z|)` keeps every exponent at most 0, so nothing overflows. Log loss punishes confident wrong "
       "answers hard: predicting 0.01 for a positive costs `-log(0.01) = 4.6`, while 0.5 costs only 0.69. "
       "That is why it rewards calibrated probabilities, not only correct labels.",
   complexity="`O(n)` time and memory.",
   mistakes="Not clipping p, so one perfect wrong prediction gives infinity. Using the natural log in one place "
            "and log2 in another. `np.exp(-z)` overflow warnings for large negative z.",
   learn=["ai-logistic-regression", "ai-classification-metrics"])

sol3 = '''import statsmodels.formula.api as smf

d = titanic.dropna(subset=["age"])
fit = smf.logit("survived ~ C(sex) + C(pclass) + age", data=d).fit(disp=0)
print("rows used:", len(d))   # out: rows used: 714
for name, b in fit.params.items():
    print(f"{name:20s} coef {b:+.3f}  odds ratio {np.exp(b):.3f}")
# out: Intercept            coef +3.777  odds ratio 43.685
# out: C(sex)[T.male]       coef -2.523  odds ratio 0.080
# out: C(pclass)[T.2]       coef -1.310  odds ratio 0.270
# out: C(pclass)[T.3]       coef -2.581  odds ratio 0.076
# out: age                  coef -0.037  odds ratio 0.964

# predicted survival probability for two 30-year-olds in 3rd class
new = pd.DataFrame({"sex": ["female", "male"], "pclass": [3, 3], "age": [30, 30]})
print(fit.predict(new).round(3).tolist())   # out: [0.522, 0.08]'''
qc(ex, title="Read the odds on the Titanic", minutes=7,
   prompt="Use `titanic`, keeping only rows with a known `age`. Fit a logistic regression of `survived` on `sex`, "
          "`pclass` (as a category) and `age`, without regularization (statsmodels `smf.logit` is ideal).\n\n"
          "1. Print the number of rows used and, for each coefficient, the value and the odds ratio `exp(coef)`.\n"
          "2. Print the predicted survival probability of a 30-year-old woman and a 30-year-old man, both in "
          "3rd class.\n\n"
          "Interpret the `male` and `age` odds ratios in one sentence each.",
   stub="import statsmodels.formula.api as smf\n\n# your code here\n",
   hint1="Signal: 'interpret the coefficients'. Pattern: logistic regression with odds ratios, `exp(b)`.",
   hint2="1. `smf.logit('survived ~ C(sex) + C(pclass) + age', data=d).fit(disp=0)`. 2. Loop over "
         "`fit.params`. 3. `fit.predict(new_df)` gives probabilities.",
   solution=sol3,
   why="Holding class and age fixed, being male multiplies the odds of survival by 0.080, about 12 times lower "
       "odds. Each extra year of age multiplies the odds by 0.964, about 3.6% lower odds per year, so 10 years "
       "gives `0.964^10 = 0.69`. The two passengers differ only in sex, yet their probabilities are 0.522 versus "
       "0.08: the odds ratio of 0.080 does not mean 'probability times 0.08', because odds = p / (1 - p) "
       "(`0.522 / 0.478 = 1.09` and `0.080 / 0.920 = 0.087`, ratio 0.08).",
   complexity="Newton steps on 714 rows and 5 parameters: milliseconds.",
   mistakes="Treating `pclass` as a number (forces equal steps from 1st to 2nd and 2nd to 3rd class). Reading "
            "odds ratios as probability ratios. Dropping missing ages without saying it changes the sample "
            "(177 passengers removed).",
   learn=["ai-logistic-regression", "stats-regression"])

sol4 = '''from sklearn.linear_model import LogisticRegression

X = pd.DataFrame({
    "tenure_years": telco["tenure"] / 12,
    "monthly_per_10usd": telco["MonthlyCharges"] / 10,
    "one_year": (telco["Contract"] == "One year").astype(int),
    "two_year": (telco["Contract"] == "Two year").astype(int),
})
y = (telco["Churn"] == "Yes").astype(int)
lr = LogisticRegression(C=1e6, max_iter=1000).fit(X, y)   # huge C = practically no regularization
for name, b in zip(X.columns, lr.coef_[0]):
    print(f"{name:18s} odds ratio {np.exp(b):.3f}")
# out: tenure_years       odds ratio 0.651
# out: monthly_per_10usd  odds ratio 1.331
# out: one_year           odds ratio 0.346
# out: two_year           odds ratio 0.133

two = pd.DataFrame({"tenure_years": [1 / 12, 5.0], "monthly_per_10usd": [9.0, 9.0],
                    "one_year": [0, 0], "two_year": [0, 1]})
print(lr.predict_proba(two)[:, 1].round(3).tolist())   # out: [0.719, 0.039]'''
qc(ex, title="Who is about to leave?", minutes=6,
   prompt="Use `telco`. Build four features: tenure in **years**, monthly charges in **units of 10 dollars**, and "
          "two 0/1 columns for `One year` and `Two year` contracts (month-to-month is the reference). Fit a "
          "logistic regression with practically no regularization (`C=1e6`) on all rows.\n\n"
          "1. Print the odds ratio of each feature.\n"
          "2. Print the churn probability of (a) a month-to-month customer in month 1 paying 90 dollars and "
          "(b) a two-year-contract customer with 5 years of tenure paying 90 dollars.\n\n"
          "Why did we rescale tenure and charges before reading the odds ratios?",
   stub="from sklearn.linear_model import LogisticRegression\n\n# telco is loaded. Your code here\n",
   hint1="Signal: a business question about drivers plus a probability for a specific customer. Pattern: "
         "logistic regression, odds ratios per meaningful unit.",
   hint2="1. Build the four columns in a DataFrame. 2. `LogisticRegression(C=1e6, max_iter=1000).fit(X, y)`. "
         "3. `np.exp(lr.coef_[0])`. 4. `predict_proba(new)[:, 1]`.",
   solution=sol4,
   why="Each extra year of tenure cuts the odds of churn by about 35% (0.651), every extra 10 dollars a month "
       "raises them by about 33% (1.331), and a two-year contract has 0.133 times the odds of a month-to-month "
       "one at the same tenure and price. The two example customers sit at 0.719 versus 0.039. Rescaling "
       "chooses the unit the odds ratio refers to: per month the tenure odds ratio would be `0.651^(1/12) = "
       "0.965`, which looks tiny but is the same effect. Pick units a PM thinks in. Note sklearn regularizes by "
       "default (`C=1.0`); for interpretation either turn it down, as here, or standardise the features so "
       "the penalty treats them equally.",
   complexity="Four features, 7,043 rows: milliseconds.",
   mistakes="Reading coefficients from a default sklearn model as if they were unpenalised. Comparing raw "
            "coefficients of features on different scales to rank 'importance'. Reading the contract effect "
            "as causal (customers choose their contract).",
   learn=["ai-logistic-regression"])

qc(ex, title="The coefficient with the wrong sign", minutes=3, kind="text", review=True,
   prompt="A linear regression predicts house price from `square_meters` and `number_of_rooms`. The coefficient "
          "on rooms is **negative**, although houses with more rooms sell for more. A stakeholder says the model "
          "is broken. Explain what happens and what you would do.",
   hint1="Signal: two features that move together and a counter-intuitive sign. Pattern: multicollinearity and "
         "'holding the other fixed' interpretation.",
   hint2="1. A coefficient is the effect with the other features held constant. 2. At fixed size, more rooms "
         "means smaller rooms. 3. Correlated features inflate coefficient variance (check VIF).",
   solution="**Model answer:** \"The model may be right. A coefficient in a multiple regression is the effect of "
            "one feature **holding the others fixed**. At the same square meters, an extra room means the space "
            "is cut into smaller rooms, which buyers may value less, so a negative sign is plausible. The "
            "univariate correlation of rooms with price is positive because rooms is a proxy for size.\n\n"
            "Also, size and rooms are strongly correlated (multicollinearity), so the two coefficients are "
            "estimated with large variance and can swing or flip between samples, even though predictions stay "
            "good. I would check the variance inflation factor (VIF above about 5 to 10 is a warning), "
            "bootstrap the coefficients to see if the sign is stable, and if the goal is interpretation, use "
            "one size feature or a ratio like `square_meters / rooms`, or ridge regression to stabilise them.\"",
   why="This tests whether you can read coefficients 'all else equal' and separate prediction quality from "
       "coefficient stability.",
   mistakes="Dropping a feature only because its sign looks wrong. Saying multicollinearity biases the "
            "coefficients (it inflates their variance).",
   learn=["ai-linear-regression", "ai-regularization-cv"])

ex.save()
