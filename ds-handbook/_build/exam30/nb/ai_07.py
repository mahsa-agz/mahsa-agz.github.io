import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_easy_common import start, qc

# Day 7 AI: mock exam over ml-framing, bias-variance, linear-regression, logistic-regression,
# classification-metrics, regularization-cv. 8 questions: rapid concepts, one hands-on, one mini case.
INTRO = ("**Mock exam rules.** Set one timer for **30 minutes** for the whole notebook. Answer the rapid concept "
         "questions out loud (or in two or three written lines) in about 2 minutes each, then do the hands-on "
         "question and the mini case. Do not open any hint or solution until the timer rings. Afterwards, grade "
         "yourself with the solutions and log every question you missed or rushed.")
ex = start(7, loads=["penguins"], intro=INTRO)

qc(ex, title="Spam folder versus cancer screen", minutes=2, kind="text", review=True,
   prompt="For each product, say whether you would favour precision or recall, and why, in one or two sentences: "
          "(a) moving emails to the spam folder, (b) a first-round cancer screening test, (c) automatically "
          "banning accounts for fraud.",
   hint1="Signal: different costs of false positives and false negatives. Pattern: precision versus recall.",
   hint2="Ask for each: which error hurts more, a false alarm (precision) or a miss (recall)?",
   solution="- **(a) Spam: precision.** A real email hidden in spam (false positive) is worse than one spam "
            "message in the inbox.\n"
            "- **(b) Screening: recall.** Missing a cancer is far worse than a false alarm, which a second, more "
            "precise test can clear.\n"
            "- **(c) Auto-ban: precision**, because banning an honest user is costly and public. A common design "
            "is two thresholds: very high precision for automatic bans, and a lower threshold that sends cases "
            "to human review to keep recall.",
   why="The answer is always 'which error is more expensive here', and the strongest answers add a system "
       "design (second test, human review) instead of one threshold.",
   mistakes="Answering 'F1' for everything. Forgetting that the threshold, not the model, sets the trade-off.",
   learn=["ai-classification-metrics"])

qc(ex, title="Premium users and odds", minutes=3, kind="text", review=True,
   prompt="A logistic regression for 'buys in the next week' has intercept -2.0 and a coefficient of 0.7 on "
          "`is_premium` (0/1); no other features. (1) Interpret 0.7. (2) What is the predicted purchase "
          "probability for a non-premium and a premium user? (3) Is the premium effect '+0.7 probability'?",
   hint1="Signal: a logistic coefficient. Pattern: odds ratio `exp(b)` and the sigmoid.",
   hint2="1. `exp(0.7)`. 2. `p = 1 / (1 + exp(-z))` with z = -2.0 and z = -1.3.",
   solution="1. `exp(0.7) = 2.01`: premium users have about **twice the odds** of buying.\n"
            "2. Non-premium: `1 / (1 + exp(2.0)) = 0.119`. Premium: `1 / (1 + exp(1.3)) = 0.214`.\n"
            "3. No. The coefficient is in log-odds. In probability the effect is +9.5 points here, and it would "
            "be different at another baseline (largest near p = 0.5). Check: odds `0.119 / 0.881 = 0.135` and "
            "`0.214 / 0.786 = 0.273`, ratio 2.01.\n\n"
            "Also say: this is an association; premium users may differ in other ways (selection), so it is not "
            "the causal effect of making someone premium.",
   why="Converting between log-odds, odds and probability quickly is a standard check in DS exams.",
   mistakes="Saying 'premium increases purchase probability by 70%' or 'by 0.7'.",
   learn=["ai-logistic-regression"])

qc(ex, title="99 on train, 70 on test", minutes=2, kind="text", review=True,
   prompt="A gradient-boosted model has 99% training accuracy and 70% test accuracy. Give the diagnosis and "
          "three things you would try, in order.",
   hint1="Signal: large train/test gap. Pattern: high variance (plus a leakage or mismatch check).",
   hint2="First check the data (leakage in train only, train/test mismatch), then reduce complexity.",
   solution="**Diagnosis:** high variance (overfitting), unless train and test come from different distributions.\n\n"
            "1. **Check the data first**: is the test set from the same population and time? Are there "
            "duplicate rows across train and test, or a feature that only exists in train? (A mismatch looks "
            "like overfitting but needs a different fix.)\n"
            "2. **Reduce complexity / regularize**: shallower trees, more min samples per leaf, a lower learning "
            "rate with early stopping on a validation set, row and column subsampling.\n"
            "3. **More data or fewer noisy features**, and choose all settings with cross-validation.\n\n"
            "Also compare with the baseline: if 70% is the majority-class rate, the model learned nothing.",
   why="A quick, ordered answer shows you diagnose before you tune.",
   mistakes="Proposing a bigger model. Not checking the base rate and the split.",
   learn=["ai-bias-variance", "ai-trees-boosting"])

qc(ex, title="Why do some weights hit exactly zero?", minutes=2, kind="text", review=True,
   prompt="In two or three sentences: why does lasso set some coefficients exactly to zero while ridge does not, "
          "and what must you do to the features before using either?",
   hint1="Signal: 'exactly zero'. Pattern: L1 versus L2 penalty shape.",
   hint2="Think of the gradient of `|b|` versus `b^2` near zero, or the diamond versus circle picture.",
   solution="The L1 penalty `lambda * |b|` pushes with a constant force (its slope is `lambda` in size) even when "
            "b is tiny, so a coefficient whose benefit to the loss is smaller than lambda is pushed exactly to "
            "0. The L2 penalty `lambda * b^2` has slope `2 lambda b`, which fades to zero near 0, so coefficients "
            "shrink but never reach exactly 0. Geometrically, the L1 constraint region is a diamond whose corners "
            "lie on the axes. Before either: **standardise the features**, because the penalty depends on their "
            "units, and do not penalise the intercept.",
   why="The slope argument is the cleanest one-breath explanation; the diamond picture is the classic visual.",
   mistakes="Saying ridge selects features. Forgetting scaling.",
   learn=["ai-regularization-cv"])

qc(ex, title="Which split for which data?", minutes=3, kind="text", review=True,
   prompt="Name the right validation split for each and say why: (a) predicting tomorrow's demand from 3 years of "
          "daily data; (b) predicting a user's next click with 50 events per user; (c) a medical model with 300 "
          "patients and 5% positives.",
   hint1="Signal: time order, repeated rows per entity, small and imbalanced data. Pattern: choose the CV scheme "
         "that copies production.",
   hint2="Time split / group split / stratified (repeated) K-fold.",
   solution="- **(a) Time-based split** (train on the past, test on the next period; rolling or expanding "
            "window, `TimeSeriesSplit`). A random split lets the model see the future.\n"
            "- **(b) Group split by user** (`GroupKFold`) if the model must work for new users, so the same "
            "user is never in both train and test; otherwise its score is inflated by memorising users. If it "
            "only serves existing users, split by time within users.\n"
            "- **(c) Stratified K-fold, repeated** (for example 5 x 5) so each fold has positives (only 15 in "
            "total), and report the mean and spread. Use PR AUC or recall at a fixed precision, not accuracy.",
   why="Validation must mimic how the model meets new data. Each wrong split here leaks information and gives "
       "an optimistic score.",
   mistakes="Shuffled K-fold for everything. Forgetting that one user's rows are not independent.",
   learn=["ai-regularization-cv", "ai-ml-framing"])

qc(ex, title="A negative R^2", minutes=2, kind="text", review=True,
   prompt="A colleague reports test R^2 = -0.3 and says that must be a bug, since R^2 is a squared number. Is "
          "it? What does it mean?",
   hint1="Signal: R^2 outside [0, 1]. Pattern: the definition `R^2 = 1 - SS_res / SS_tot`.",
   hint2="On test data, SS_res can be larger than SS_tot.",
   solution="Not a bug. `R^2 = 1 - SS_res / SS_tot`, where SS_tot is the error of always predicting the mean of "
            "y. It equals a squared correlation only for least squares with an intercept, evaluated on its own "
            "training data. On a test set, a model can be worse than predicting the mean, so SS_res > SS_tot and "
            "R^2 < 0. Here the model is 30% worse than the constant mean: typical of heavy overfitting, a "
            "distribution shift, or a bug in the features at prediction time (for example a different unit or "
            "scaling).",
   why="Knowing the definition, not the name, is the point.",
   mistakes="Clipping it to 0. Assuming R^2 is always a squared correlation.",
   learn=["ai-linear-regression", "ai-bias-variance"])

sol7 = '''from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

d = penguins.dropna(subset=["sex", "bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"])
y = (d["sex"] == "MALE").astype(int)
print("rows:", len(d), " male share:", round(y.mean(), 3))   # out: rows: 333  male share: 0.505
cv = StratifiedKFold(5, shuffle=True, random_state=0)
num = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]

def cv_acc(num_cols, cat_cols):
    prep = ColumnTransformer([("num", StandardScaler(), num_cols)] +
                             ([("cat", OneHotEncoder(), cat_cols)] if cat_cols else []))
    return cross_val_score(make_pipeline(prep, LogisticRegression(max_iter=1000)), d, y, cv=cv).mean()

print("body mass only:          ", round(cv_acc(["body_mass_g"], []), 3))   # out: body mass only:           0.61
print("4 measurements:          ", round(cv_acc(num, []), 3))              # out: 4 measurements:           0.895
print("4 measurements + species:", round(cv_acc(num, ["species"]), 3))     # out: 4 measurements + species: 0.913'''
qc(ex, title="Male or female penguin?", minutes=7, review=True,
   prompt="Use `penguins`. Drop rows with a missing `sex` or measurement. Predict `sex == \"MALE\"` with a scaled "
          "logistic regression and report the mean 5-fold CV accuracy (`StratifiedKFold(5, shuffle=True, "
          "random_state=0)`) for three feature sets:\n\n"
          "1. `body_mass_g` only; 2. the four body measurements; 3. the four measurements plus `species` (one-hot).\n\n"
          "Print the number of rows and the share of males first. Why is body mass alone so weak, although males are heavier? Why does species still add something?",
   stub="# penguins is loaded. Your code here\n",
   hint1="Signal: a binary target, a few numeric features, and a categorical one. Pattern: logistic regression "
         "with a pipeline, compared by cross-validation.",
   hint2="1. `dropna(subset=[...])`. 2. A ColumnTransformer with StandardScaler (and OneHotEncoder for species). "
         "3. `cross_val_score(pipe, d, y, cv=cv).mean()`.",
   solution=sol7,
   why="Body mass alone reaches only 0.61 (base rate 0.505). Males are heavier **within** each species, but "
       "the species differ even more: female Gentoo average about 4,680 g, heavier than male Adelie (about "
       "4,040 g) and male Chinstrap (about 3,940 g), so one global cut on mass mixes them up. The four measurements reach 0.895 because together they also "
       "encode the species (Gentoo have shallow bills, for example), so the model can compare a bird with its "
       "own kind. Adding species explicitly gives each species its own baseline and lifts accuracy to 0.913. "
       "Lesson: a confounding grouping variable can hide a strong within-group signal; species-by-measurement "
       "interactions, or a tree model, could add more.",
   complexity="15 tiny logistic fits: milliseconds.",
   mistakes="Using accuracy without checking the base rate (here about 50%, so accuracy is fine). Forgetting the "
            "pipeline and scaling before the split. Not dropping NaN rows consistently for all three runs (then "
            "the comparisons use different rows).",
   learn=["ai-logistic-regression", "ai-regularization-cv"])

qc(ex, title="Mini case: a loan default model", minutes=9, kind="text", review=True,
   prompt="A fintech app wants a model that decides, at application time, whether to approve a small loan. "
          "Defaults (not repaid within 90 days of the due date) are about 4%. You have 2 years of applications "
          "with app usage data, bureau scores, and repayment history.\n\n"
          "In about 3 minutes: frame it (unit, label, timing), list two leakage risks, choose metrics and the "
          "threshold logic, and describe validation and launch. Mention one fairness or feedback-loop issue.",
   hint1="Signal: a decision at a point in time, rare positives, money on both sides. Pattern: the ML framing "
         "checklist plus cost-based thresholds and a time split.",
   hint2="1. Unit = application; label = default within 90 days of due date; features frozen at application "
         "time. 2. Leaks: post-application data, label not yet matured. 3. PR AUC, expected profit. "
         "4. Out-of-time validation, then a careful rollout. 5. Rejected applicants have no labels.",
   solution="**Model answer (about 3 min):**\n\n"
            "1. **Framing.** One row per loan application, scored at submission. Label = 1 if the loan is not "
            "repaid within 90 days after the due date. Only applications whose outcome window has fully "
            "passed can be used (immature loans would look like non-defaults). Binary classification with "
            "4% positives; the output must be a calibrated probability because it feeds a money decision.\n"
            "2. **Features and leakage.** Use only what is known at submission: bureau score, past repayments, "
            "app usage before the application. Leaks: anything logged after approval (collections calls, "
            "repayment reminders, later bureau pulls), aggregates computed over the full history including the "
            "future, and the approval decision itself.\n"
            "3. **Metrics and threshold.** Offline: PR AUC and log loss or Brier score (calibration), plus "
            "approval rate and default rate at the chosen cut. Threshold from economics: approve if "
            "`(1 - p) * margin > p * loss_given_default`, for example a 10 dollar margin and a 100 dollar loss "
            "means approve when p < 10 / 110, about 0.09.\n"
            "4. **Validation and launch.** Out-of-time split (train on the first 18 months, test on the last "
            "6), compare with the current rule or bureau-score cutoff. Then a gradual rollout or A/B test with "
            "limits per user, tracking default rate, approval rate and profit once loans mature.\n"
            "5. **Fairness and feedback loop.** We only observe outcomes for approved loans, so the model never "
            "learns about people we reject (selection bias, 'reject inference'). Approve a small random share "
            "near the threshold to keep learning. Check that error rates and approval rates do not differ "
            "unfairly across protected groups, and avoid proxies (for example postcode). Lending is regulated, "
            "so decisions need reasons (explainable model or reason codes).",
   why="The mock case checks whether you combine the week's topics: framing, leakage, imbalance-aware metrics, "
       "cost-based threshold, the right split, and an online test.",
   mistakes="Using accuracy (96% by approving everyone). Training on loans whose outcome is not yet known. "
            "Random split instead of out-of-time. Ignoring that rejected applicants have no labels.",
   learn=["ai-ml-framing", "ai-classification-metrics", "ai-regularization-cv"])

ex.save()
