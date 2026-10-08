import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_easy_common import start, qc

# Day 9 AI: focus features-imbalance; review trees-boosting, classification-metrics.
ex = start(9, loads=["bank", "telco"])

qc(ex, title="Only 1 in 100 is positive", minutes=4, kind="text",
   prompt="Your positive class is 1% of the data. In about 90 seconds, explain what goes wrong with a default "
          "training and evaluation setup, and list the tools you would use, from first choice to last resort. "
          "Say what SMOTE is and one risk of resampling.",
   hint1="Signal: rare positives. Pattern: imbalance handling = right metric, right threshold, then weights or "
         "resampling, never touching the test distribution.",
   hint2="1. Accuracy and the 0.5 threshold mislead. 2. Use PR AUC, recall at a precision. 3. Move the "
         "threshold. 4. Class weights. 5. Resample the training folds only. 6. More positive data, better "
         "features.",
   solution="**Model answer (about 90 s):**\n\n"
            "\"With 1% positives, a model that always says 'no' has 99% accuracy, and the default 0.5 threshold "
            "flags almost nothing, so recall is tiny. The model itself may rank well; the problem is mostly the "
            "metric and the threshold.\n\n"
            "My order: (1) **Metrics**: PR AUC, recall at a fixed precision or precision in the top k, and a "
            "stratified split so every fold has positives. (2) **Threshold**: choose it from the costs of false "
            "positives and false negatives. (3) **Class weights** (`class_weight='balanced'` or "
            "`scale_pos_weight`), which make errors on positives cost more during training. (4) **Resampling** "
            "of the training data: random undersampling of negatives (fast, loses data) or oversampling such as "
            "SMOTE, which creates synthetic positives by interpolating between a positive and its nearest "
            "positive neighbours. (5) Better: more labelled positives and better features.\n\n"
            "Risks: weights and resampling distort predicted probabilities (they are no longer calibrated, so "
            "recalibrate if you need probabilities), and resampling must happen inside each training fold, "
            "never before the split and never on the test set, or the evaluation leaks and stops reflecting "
            "the real 1% world.\"",
   why="Examiners want to hear that imbalance is first a metric and threshold problem, and that resampling "
       "is applied to training folds only and breaks calibration.",
   mistakes="Oversampling before splitting (copies of the same positive end up in train and test). Reporting "
            "accuracy. Assuming SMOTE always helps (with strong models it often does not).",
   learn=["ai-features-imbalance", "ai-classification-metrics"])

sol2 = '''from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

y = (bank["y"] == "yes").astype(int)
X = bank.drop(columns=["y", "duration"])          # duration leaks (day 1)
cat = [c for c in X.columns if X[c].dtype == object]
num = [c for c in X.columns if c not in cat]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
print("positive rate:", round(y.mean(), 3))      # out: positive rate: 0.113

for weight in [None, "balanced"]:
    prep = ColumnTransformer([("num", StandardScaler(), num), ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
    model = make_pipeline(prep, LogisticRegression(max_iter=1000, class_weight=weight)).fit(X_tr, y_tr)
    p = model.predict_proba(X_te)[:, 1]
    pred = p >= 0.5
    print(f"class_weight={str(weight):8s} precision {precision_score(y_te, pred):.3f}  "
          f"recall {recall_score(y_te, pred):.3f}  ROC AUC {roc_auc_score(y_te, p):.3f}  "
          f"PR AUC {average_precision_score(y_te, p):.3f}  mean p {p.mean():.3f}")
# out: class_weight=None     precision 0.641  recall 0.214  ROC AUC 0.786  PR AUC 0.437  mean p 0.112
# out: class_weight=balanced precision 0.353  recall 0.619  ROC AUC 0.786  PR AUC 0.430  mean p 0.388'''
qc(ex, title="Do class weights make a better model?", minutes=7,
   prompt="Use `bank` **without** `duration` (it leaks, see day 1). Target `y == \"yes\"`. Split 75/25 "
          "(stratified, `random_state=0`). Scale numeric columns, one-hot text columns.\n\n"
          "Fit `LogisticRegression(max_iter=1000)` twice: with `class_weight=None` and with "
          "`class_weight=\"balanced\"`. For each, print precision and recall at threshold 0.5, ROC AUC, PR AUC and "
          "the mean predicted probability on the test set.\n\n"
          "Did the weights make the model better? What did they actually change?",
   stub="# bank is loaded. Your code here\n",
   hint1="Signal: imbalance (about 11% positives) and a 'fix' applied during training. Pattern: class weights "
         "versus threshold moving; compare threshold-free metrics.",
   hint2="1. Same pipeline twice, only `class_weight` differs. 2. Precision/recall need hard predictions "
         "(`p >= 0.5`); ROC AUC and PR AUC need the probabilities. 3. Compare the mean predicted probability "
         "with the positive rate.",
   solution=sol2,
   why="The ranking quality is the same: ROC AUC 0.786 for both, and PR AUC is even a little lower with "
       "weights (0.430 versus 0.437). What changed is the probability scale: the weighted model's mean "
       "prediction is 0.388 although only 11.3% subscribe, so more clients cross 0.5. Recall jumps from 0.214 "
       "to 0.619 and precision falls from 0.641 to 0.353. That is just a different point on almost the same "
       "precision-recall curve; you could reach it with the unweighted model by lowering its threshold. So class "
       "weights did not make a better model here, they moved the threshold and broke calibration (the "
       "unweighted mean 0.112 matches the base rate). Weights help more for models that cannot be thresholded "
       "well, or when the minority class is so rare that the model ignores it.",
   complexity="Two logistic fits on about 31,000 rows and about 60 columns: a few seconds at most.",
   mistakes="Concluding 'balanced is better' from the higher recall alone. Comparing at the same 0.5 threshold "
            "and forgetting that the two models live on different probability scales. Treating `pdays = 999` "
            "as a number (it is a code for 'never contacted before'; add a 0/1 flag).",
   learn=["ai-features-imbalance", "ai-classification-metrics"])

sol3 = '''raw = telco["TotalCharges"]
print("dtype:", raw.dtype)                                    # out: dtype: object
num = pd.to_numeric(raw, errors="coerce")
bad = telco[num.isna()]
print("rows that do not convert:", len(bad))                   # out: rows that do not convert: 11
print("their raw values:", sorted(set(bad["TotalCharges"])))   # out: their raw values: [' ']
print("their tenure:", sorted(set(bad["tenure"])))             # out: their tenure: [0]
print("customers with tenure 0:", int((telco["tenure"] == 0).sum()))   # out: customers with tenure 0: 11

clean = num.fillna(0)              # new customers have not been billed yet
# sanity check: TotalCharges is close to tenure * MonthlyCharges
ratio = (clean / (telco["tenure"] * telco["MonthlyCharges"])).replace([np.inf, -np.inf], np.nan)
print("median TotalCharges / (tenure * MonthlyCharges):", round(ratio.median(), 3))
# out: median TotalCharges / (tenure * MonthlyCharges): 1.0'''
qc(ex, title="The column that will not convert", minutes=5,
   prompt="In `telco`, `TotalCharges` should be a number, but pandas reads it as text.\n\n"
          "1. Print its dtype, convert it with `pd.to_numeric(..., errors=\"coerce\")`, and print how many rows "
          "fail, their raw values and their `tenure`.\n"
          "2. Print how many customers have `tenure == 0`.\n"
          "3. Decide how to fill the failures and justify it. As a sanity check, print the median of "
          "`TotalCharges / (tenure * MonthlyCharges)` over customers with tenure above 0.\n\n"
          "Would `fillna(median)` be a good choice here?",
   stub="# telco is loaded. Your code here\n",
   hint1="Signal: a numeric column stored as text. Pattern: data cleaning; find why values are missing before "
         "you impute them.",
   hint2="1. `pd.to_numeric(raw, errors='coerce')`, then `.isna()` finds the failures. 2. Look at those rows: "
         "what do they have in common? 3. Missing for a reason (not billed yet) means a meaningful fill value.",
   solution=sol3,
   why="All 11 failures are a single space, and they are exactly the 11 customers with tenure 0: brand-new "
       "customers who have not received a bill yet. So the right value is 0, not a guess. The median ratio "
       "of 1.0 confirms that `TotalCharges` is basically `tenure * MonthlyCharges`. Filling with the median "
       "(about 1,400 dollars) would invent a bill history for new customers and blur the strongest churn "
       "signal (new customers churn most). Also note that `TotalCharges` is almost redundant with tenure "
       "times monthly charges, which matters for interpreting linear coefficients.",
   complexity="`O(n)`.",
   mistakes="`astype(float)`, which crashes on ' '. Dropping the rows silently. Imputing with the mean or "
            "median without asking why the value is missing. Computing an imputation value on the full data "
            "before the train/test split (fit it on train only).",
   learn=["ai-features-imbalance"])

sol4 = '''from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

y = (bank["y"] == "yes").astype(int)
X = bank.drop(columns=["y", "duration"])
cat = [c for c in X.columns if X[c].dtype == object]
num = [c for c in X.columns if c not in cat]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)

# undersample the negatives in TRAIN to a 50/50 mix
pos = y_tr[y_tr == 1].index
neg = y_tr[y_tr == 0].sample(n=len(pos), random_state=0).index
keep = pos.union(neg)
beta = len(neg) / (y_tr == 0).sum()                  # share of negatives we kept
prep = ColumnTransformer([("num", StandardScaler(), num), ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
model = make_pipeline(prep, LogisticRegression(max_iter=1000)).fit(X_tr.loc[keep], y_tr.loc[keep])
p = model.predict_proba(X_te)[:, 1]
p_fixed = beta * p / (beta * p + 1 - p)              # undo the sampling (prior correction)

print("kept share of negatives (beta):", round(beta, 3))
print("actual test positive rate:     ", round(y_te.mean(), 3))
print("mean predicted p (undersampled):", round(p.mean(), 3))
print("mean predicted p (corrected):   ", round(p_fixed.mean(), 3))
print("ROC AUC before / after correction:", round(roc_auc_score(y_te, p), 3), round(roc_auc_score(y_te, p_fixed), 3))
# out: kept share of negatives (beta): 0.127
# out: actual test positive rate:      0.113
# out: mean predicted p (undersampled): 0.389
# out: mean predicted p (corrected):    0.114
# out: ROC AUC before / after correction: 0.784 0.784'''
qc(ex, title="Undersampling and the inflated probabilities", minutes=6, review=True,
   prompt="Same `bank` setup as Q2 (no `duration`, same split). Undersample the **training** negatives at random "
          "(`random_state=0`) so that train is 50/50, fit the logistic regression, and score the untouched test "
          "set.\n\n"
          "1. Print `beta`, the share of training negatives you kept, and the actual test positive rate.\n"
          "2. Print the mean predicted probability on test, before and after the correction "
          "`p_fixed = beta * p / (beta * p + 1 - p)`.\n"
          "3. Print the test ROC AUC before and after the correction.\n\n"
          "Why does the correction fix the mean but not change the AUC?",
   stub="# bank is loaded. Your code here\n",
   hint1="Signal: a model trained on a different class balance than the real one. Pattern: calibration and prior "
         "correction after resampling.",
   hint2="1. `y_tr[y_tr == 0].sample(n=len(pos), random_state=0)`. 2. beta = kept negatives / all training "
         "negatives. 3. The correction scales the odds by beta: `odds_fixed = beta * odds`.",
   solution=sol4,
   why="The model saw a 50/50 world, so its average prediction is 0.389 while the real rate is 0.113. Keeping only "
       "a share beta = 0.127 of the negatives multiplies the odds of every row by `1 / beta`; the correction "
       "multiplies them back by beta, which brings the mean to 0.114, right on the real rate. The correction is "
       "a monotonic transform of p, so it never changes the order of the customers: ROC AUC stays 0.784 before "
       "and after. Use the corrected probabilities for anything that needs real probabilities (forecasts, "
       "expected-value thresholds); for ranking either works. (The AUC is slightly below the 0.786 of Q2 "
       "because we threw away 87% of the negatives.)",
   complexity="One logistic fit on about 7,000 balanced rows: under a second.",
   mistakes="Undersampling before the split (the test set no longer looks like reality). Using the raw "
            "probabilities for a forecast or an expected-value threshold. Expecting the correction to change "
            "the ranking.",
   learn=["ai-features-imbalance", "ai-classification-metrics"])

qc(ex, title="What trees do not need", minutes=3, kind="text", review=True,
   prompt="For decision-tree ensembles (random forest, gradient boosting), answer yes or no with one reason "
          "each: (1) Do you need to scale features? (2) Do you need one-hot encoding? (3) Can they handle missing "
          "values? (4) Can they extrapolate beyond the training range? (5) Can they model interactions without "
          "you creating them?",
   hint1="Signal: preprocessing for tree models. Pattern: trees split on thresholds of one feature at a time.",
   hint2="Thresholds do not care about scale; categories and missing values depend on the library; leaves "
         "predict constants.",
   solution="1. **No scaling needed.** A split `x < t` gives the same partition after any monotonic transform of "
            "x.\n"
            "2. **Not necessarily.** Ordinal or native categorical encoding often works better than one-hot for "
            "trees (LightGBM, CatBoost and sklearn's `HistGradientBoosting` support categories directly). "
            "One-hot of a high-cardinality feature spreads the signal over many weak columns.\n"
            "3. **Often yes.** XGBoost, LightGBM and sklearn's histogram boosting learn which side missing values "
            "go to. Classic sklearn `RandomForestClassifier` gained missing-value support only in recent "
            "versions, so check yours or impute (a sentinel such as -1 works for trees).\n"
            "4. **No.** Each leaf predicts a constant learned from training data, so predictions are flat "
            "outside the training range. For trends over time, use a linear model or features like differences.\n"
            "5. **Yes.** A path of splits on different features is an interaction; deeper trees capture "
            "higher-order interactions.",
   why="Knowing what trees do not need (scaling) and cannot do (extrapolation) is a quick way to show you "
       "understand how they work, not just how to call them.",
   mistakes="Scaling features 'because it is good practice' and then claiming it helped a forest. Using trees to "
            "forecast a growing trend.",
   learn=["ai-trees-boosting", "ai-features-imbalance"])

ex.save()
