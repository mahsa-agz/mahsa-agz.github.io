import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_easy_common import start, qc

# Day 5 AI: focus classification-metrics; review logistic-regression.
ex = start(5, loads=["telco"])

sol1 = '''def prf(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else 0.0   # of the flagged, how many are right
    recall = tp / (tp + fn) if tp + fn else 0.0      # of the real positives, how many we caught
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1'''
tests1 = '''check(prf, [((8, 2, 4), (0.8, 2 / 3, 0.7272727272727273)),
            ((5, 0, 5), (1.0, 0.5, 2 / 3)),
            ((0, 0, 7), (0.0, 0.0, 0.0)),        # model never says positive
            ((90, 910, 10), (0.09, 0.9, 0.16363636363636364))])'''
qc(ex, title="Three numbers from four boxes", minutes=4,
   prompt="Write `prf(tp, fp, fn)` that returns `(precision, recall, f1)` from confusion-matrix counts. If a "
          "denominator is 0, return 0.0 for that metric.\n\n"
          "Example: 8 true positives, 2 false positives, 4 false negatives gives precision 0.8, recall 0.667, "
          "F1 0.727.\n\n"
          "Look at the last test case: what kind of model is it, and would accuracy reveal the problem?",
   stub="def prf(tp, fp, fn):\n    # your code here\n    pass",
   tests=tests1,
   hint1="Signal: confusion-matrix counts. Pattern: precision = TP / predicted positives, recall = TP / actual "
         "positives, F1 = harmonic mean.",
   hint2="1. `precision = tp / (tp + fp)`. 2. `recall = tp / (tp + fn)`. 3. `f1 = 2 P R / (P + R)`. "
         "4. Guard each division.",
   solution=sol1,
   why="Precision answers 'when the model says yes, how often is it right'; recall answers 'of all real "
       "positives, how many did we catch'. F1 is the harmonic mean, so it is low if either one is low. The last "
       "case flags 1,000 items to catch 90 of 100 positives: recall 0.9 but precision 0.09, F1 0.164. If there "
       "are, say, 100,000 items, its accuracy is still about 99%, so accuracy hides that 91% of alerts are false.",
   complexity="`O(1)`.",
   mistakes="Swapping FP and FN. Using the arithmetic mean instead of the harmonic mean. Dividing by zero for a "
            "model that never predicts positive.",
   learn=["ai-classification-metrics"])

sol2 = '''from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

df = telco.drop(columns="customerID").copy()
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)   # blanks = brand-new customers
y = (df.pop("Churn") == "Yes").astype(int)
num = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
cat = [c for c in df.columns if c not in num]
X_tr, X_te, y_tr, y_te = train_test_split(df, y, test_size=0.25, stratify=y, random_state=0)
model = make_pipeline(ColumnTransformer([("num", StandardScaler(), num),
                                        ("cat", OneHotEncoder(handle_unknown="ignore"), cat)]),
                      LogisticRegression(max_iter=1000))
model.fit(X_tr, y_tr)
p_te = model.predict_proba(X_te)[:, 1]
pred = (p_te >= 0.5).astype(int)

tn, fp, fn, tp = confusion_matrix(y_te, pred).ravel()
print("TN FP FN TP:", tn, fp, fn, tp)                 # out: TN FP FN TP: 1150 144 222 245
print("accuracy ", round(accuracy_score(y_te, pred), 3))     # out: accuracy  0.792
print("precision", round(precision_score(y_te, pred), 3))    # out: precision 0.63
print("recall   ", round(recall_score(y_te, pred), 3))       # out: recall    0.525
print("ROC AUC  ", round(roc_auc_score(y_te, p_te), 3))       # out: ROC AUC   0.844
print("PR AUC   ", round(average_precision_score(y_te, p_te), 3), " base rate", round(y_te.mean(), 3))
# out: PR AUC    0.638  base rate 0.265'''
qc(ex, title="Score the churn model properly", minutes=7,
   prompt="Build a churn model on `telco`:\n\n"
          "- drop `customerID`; convert `TotalCharges` to numbers (blanks become 0); target = `Churn == \"Yes\"`;\n"
          "- numeric columns `tenure`, `MonthlyCharges`, `TotalCharges`, `SeniorCitizen` are scaled, all other "
          "columns one-hot encoded; `LogisticRegression(max_iter=1000)`;\n"
          "- 75/25 split, stratified, `random_state=0`.\n\n"
          "Keep the test probabilities in `p_te` (you need them in Q3). At threshold 0.5, print TN, FP, FN, TP, "
          "accuracy, precision and recall. Then print ROC AUC, PR AUC (average precision) and the test base rate.\n\n"
          "Which single number would you show the retention team, and why?",
   stub="# telco is loaded. Your code here\n",
   hint1="Signal: an imbalanced binary problem and a request for 'the right metric'. Pattern: confusion matrix "
         "at a threshold plus threshold-free ranking metrics (ROC AUC, PR AUC).",
   hint2="1. `pd.to_numeric(..., errors='coerce').fillna(0)`. 2. ColumnTransformer + LogisticRegression in a "
         "pipeline. 3. `predict_proba(X_te)[:, 1]`. 4. `confusion_matrix(...).ravel()` returns TN, FP, FN, TP. "
         "5. Compare PR AUC with the base rate, which is what a random model scores.",
   solution=sol2,
   why="At 0.5 the model catches 245 of 467 test churners (recall 0.525) with precision 0.63; accuracy is 0.792, "
       "only 5.7 points above the 0.735 you get by predicting 'no churn' for everyone. ROC AUC 0.844 says the "
       "ranking is good: a random churner outscores a random stayer 84% of the time. PR AUC 0.638 versus a "
       "base rate of 0.265 says the same on the positive class. For the retention team, show a number tied to "
       "their action: precision and recall at the size of list they can call (for example 'calling the top "
       "500 reaches X churners'), not accuracy. Threshold 0.5 is arbitrary; Q3 picks it from costs.",
   complexity="About 5,300 training rows and 45 one-hot columns: well under a second.",
   mistakes="Calling `roc_auc_score` with hard 0/1 predictions instead of probabilities. Reading `confusion_matrix` "
            "in the wrong order (sklearn puts true labels in rows, negatives first). Comparing PR AUC with 0.5 "
            "instead of with the base rate.",
   learn=["ai-classification-metrics", "ai-logistic-regression"])

sol3 = '''# uses y_te and p_te from Q2
value_saved, cost_contact = 100, 20
y_arr = y_te.to_numpy()
best = None
for t in np.arange(0.05, 0.96, 0.05):
    flag = p_te >= t
    tp = int((flag & (y_arr == 1)).sum())
    profit = value_saved * tp - cost_contact * int(flag.sum())
    if best is None or profit > best[1]:
        best = (round(t, 2), profit, int(flag.sum()))
    if round(t, 2) in (0.2, 0.5):
        print(f"threshold {t:.2f}: contacted {int(flag.sum())}, churners reached {tp}, profit {profit}")
print("best threshold", best[0], "profit", best[1], "contacted", best[2])
# out: threshold 0.20: contacted 839, churners reached 406, profit 23820
# out: threshold 0.50: contacted 389, churners reached 245, profit 16720
# out: best threshold 0.2 profit 23820 contacted 839'''
qc(ex, title="Where to cut the list", minutes=6,
   prompt="Use `y_te` and `p_te` from Q2. The retention team calls every customer with a churn probability "
          "at or above a threshold `t`. Each call costs 20 dollars. Each **churner** who gets a call is worth "
          "100 dollars of saved revenue (on average; non-churners are worth nothing extra).\n\n"
          "`profit = 100 * (churners called) - 20 * (customers called)`\n\n"
          "Try `t = 0.05, 0.10, ..., 0.95`. Print the result for `t = 0.2` and `t = 0.5`, and the best threshold. "
          "Can you predict the best threshold before running the code?",
   stub="# uses y_te and p_te from Q2. Your code here\n",
   hint1="Signal: different costs for the two kinds of error. Pattern: choose the threshold by expected value, "
         "not 0.5.",
   hint2="1. For each t: flag = p_te >= t; count flagged and true positives among them. 2. Compute profit. "
         "3. Theory: call a customer when `100 * p > 20`, so with calibrated probabilities the best t is near "
         "`20 / 100 = 0.2`.",
   solution=sol3,
   why="The rule 'call if expected gain beats cost' is `100 * p > 20`, so `p > 0.2`. The sweep agrees: 0.2 is "
       "best, with profit 23,820 dollars from 839 calls, versus 16,720 at the default 0.5 (389 calls). At 0.2 "
       "precision is only `406 / 839 = 0.48`, yet it is the most profitable choice, because a missed churner "
       "costs five times more than a wasted call. The theory works because logistic regression gives roughly "
       "calibrated probabilities; with an uncalibrated model you must sweep.",
   complexity="19 thresholds x 1,761 test rows: instant. (Sort once by score for a large list.)",
   mistakes="Keeping the default 0.5. Choosing the threshold on the test set and then reporting test profit as "
            "an unbiased estimate (pick it on validation data). Forgetting that 'worth 100 dollars' already "
            "assumes the call actually saves the customer; an A/B test should measure that.",
   learn=["ai-classification-metrics", "ai-ml-framing"])

qc(ex, title="ROC AUC or PR AUC?", minutes=4, kind="text",
   prompt="Explain in about 60 seconds what ROC AUC measures (give the probability interpretation), what PR AUC "
          "measures, and which one you would report for a fraud model with 0.2% positives. Why?",
   hint1="Signal: imbalanced data and two curve metrics. Pattern: ROC uses the false-positive rate (divided by "
         "the many negatives); PR uses precision (divided by predicted positives).",
   hint2="1. ROC: TPR versus FPR over all thresholds; AUC = P(random positive scored above random negative). "
         "2. PR: precision versus recall; random baseline = prevalence. 3. With very few positives, a small FPR "
         "can still be many false alarms.",
   solution="**Model answer (about 60 s):**\n\n"
            "\"ROC AUC is the area under the curve of true-positive rate versus false-positive rate as the "
            "threshold moves. It equals the probability that a random positive gets a higher score than a "
            "random negative, so 0.5 is random and 1.0 is perfect ranking. It does not depend on the class "
            "balance.\n\n"
            "PR AUC (average precision) plots precision against recall. Its random baseline is the positive "
            "rate, so 0.002 for fraud.\n\n"
            "For fraud with 0.2% positives I would report PR AUC, plus precision at the review capacity. The "
            "reason: with 1 million transactions and 2,000 frauds, a false-positive rate of just 1% is 9,980 "
            "false alarms, five times the number of frauds. ROC barely moves, because FPR divides by the 998,000 "
            "negatives, so ROC AUC can be 0.98 while precision is poor. PR AUC shows that pain directly. ROC AUC "
            "is still useful to compare rankers when the class balance changes between datasets.\"",
   why="Examiners want the probabilistic meaning of ROC AUC and the reason PR is preferred under heavy "
       "imbalance, ideally with a quick numeric example.",
   mistakes="Saying 'ROC AUC is bad for imbalanced data' without explaining why. Forgetting that the PR "
            "baseline is the prevalence, not 0.5.",
   learn=["ai-classification-metrics", "ai-features-imbalance"])

qc(ex, title="Is 0.3 really 30%?", minutes=3, kind="text", review=True,
   prompt="Your logistic regression gives a customer a churn probability of 0.3. The finance team wants to "
          "multiply probabilities by revenue to forecast losses. When can you trust 0.3 as a 30% chance, and "
          "when not? How do you check?",
   hint1="Signal: using scores as probabilities. Pattern: calibration.",
   hint2="1. Plain logistic regression trained on representative data is usually well calibrated. 2. Things "
         "that break it: class weights or resampling, strong regularization, distribution shift. 3. Check with "
         "a reliability curve and the Brier score; fix with Platt or isotonic calibration.",
   solution="**Model answer:** \"Logistic regression minimises log loss, so on data like its training data it "
            "tends to be well calibrated: among customers scored about 0.3, about 30% churn. That breaks when "
            "(1) we trained with class weights, undersampling or oversampling, which inflate the scores of the "
            "rare class; (2) strong regularization shrinks scores toward the middle; (3) the population or the "
            "churn rate has shifted since training; (4) the model is misspecified.\n\n"
            "To check: on a held-out set, bin the predictions (for example deciles), compare the mean predicted "
            "probability with the observed churn rate in each bin (a reliability curve, "
            "`sklearn.calibration.calibration_curve`), and track the Brier score. If it is off, recalibrate on "
            "held-out data with Platt scaling or isotonic regression (`CalibratedClassifierCV`). For a finance "
            "forecast also compare the sum of probabilities with the actual churn count each month.\"",
   why="Ranking quality (AUC) and calibration are different properties. A finance use case needs calibrated "
       "probabilities; a 'who to call first' use case only needs a good ranking.",
   mistakes="Assuming any classifier's `predict_proba` is a probability (boosted trees, SVMs and naive Bayes "
            "often are not calibrated). Calibrating on the training data.",
   learn=["ai-logistic-regression", "ai-classification-metrics"])

ex.save()
