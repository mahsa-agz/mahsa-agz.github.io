import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_easy_common import start, qc

# Day 8 AI: focus trees-boosting; review regularization-cv.
ex = start(8, loads=["telco", "titanic"])

qc(ex, title="Many trees, two philosophies", minutes=5, kind="text",
   prompt="In about 90 seconds: how does a decision tree choose a split, and how do random forests and gradient "
          "boosting combine trees differently? Say which error (bias or variance) each one mainly reduces and "
          "name the two or three hyperparameters you would tune first for each.",
   hint1="Signal: 'random forest versus XGBoost'. Pattern: bagging (parallel, averages) versus boosting "
         "(sequential, corrects residuals).",
   hint2="1. Split = the feature and threshold with the largest impurity drop (Gini/entropy, or variance for "
         "regression). 2. Forest: deep trees on bootstrap samples with random feature subsets, averaged. "
         "3. Boosting: shallow trees, each fitted to the gradient of the loss (residuals), added with a small "
         "learning rate.",
   solution="**Model answer (about 90 s):**\n\n"
            "\"A tree greedily tries every feature and threshold and keeps the split that most reduces impurity: "
            "Gini `1 - sum p_k^2` or entropy for classification, variance for regression. It repeats in each "
            "child until a stopping rule. Single deep trees have low bias but very high variance.\n\n"
            "A **random forest** grows many deep trees in parallel, each on a bootstrap sample and with a random "
            "subset of features at each split, and averages them. Averaging decorrelated trees mainly cuts "
            "**variance**. It is hard to break: tune `max_features`, `min_samples_leaf`, and use enough trees "
            "(more trees never overfit, they just cost time).\n\n"
            "**Gradient boosting** grows shallow trees one after another; each new tree fits the negative "
            "gradient of the loss (for squared error, the residuals) of the current ensemble, and is added with "
            "a small learning rate. It mainly cuts **bias**, and it can overfit if you add too many trees. Tune "
            "`learning_rate` together with the number of trees (use early stopping on a validation set), "
            "`max_depth` or number of leaves, and subsampling of rows and columns. XGBoost, LightGBM and CatBoost "
            "add regularization, histogram splits and categorical handling.\n\n"
            "On tabular data, tuned boosting usually wins; a forest is a strong, low-effort baseline.\"",
   why="The bagging-versus-boosting contrast (parallel and variance versus sequential and bias) and the "
       "'learning rate times number of trees' coupling are what examiners listen for.",
   mistakes="Saying random forests reduce bias. Saying more trees always overfit a forest (they do not; they can "
            "in boosting). Forgetting that boosting fits gradients, not just 'the misclassified points' (that is "
            "AdaBoost's reweighting view).",
   learn=["ai-trees-boosting"])

sol2 = '''def gini(labels):
    labels = np.asarray(labels)
    if len(labels) == 0:
        return 0.0
    _, counts = np.unique(labels, return_counts=True)
    p = counts / counts.sum()
    return float(1 - np.sum(p ** 2))

def split_gain(left, right):
    """Impurity of the parent minus the size-weighted impurity of the two children."""
    parent = np.concatenate([left, right])
    n = len(parent)
    return gini(parent) - (len(left) / n * gini(left) + len(right) / n * gini(right))'''
tests2 = '''check(gini, [([0, 0, 1, 1], 0.5), ([1, 1, 1], 0.0), ([0, 1, 2], 2 / 3), ([0, 0, 0, 1], 0.375)])
check(split_gain, [(([0, 0], [1, 1]), 0.5),
                   (([0, 0, 0, 1], [1, 1, 1, 0]), 0.125),
                   (([0, 1], [0, 1]), 0.0),
                   (([0, 0, 0, 0, 1], [1]), 4 / 9 - 5 / 6 * 0.32)])'''
qc(ex, title="Score a split by hand", minutes=5,
   prompt="Write `gini(labels)` (Gini impurity `1 - sum p_k^2`, 0 for an empty list) and "
          "`split_gain(left, right)`: the parent's Gini minus the size-weighted Gini of the two children.\n\n"
          "Example: parent `[0, 0, 0, 1, 1, 1, 1, 0]` split into `[0, 0, 0, 1]` and `[1, 1, 1, 0]`: the parent "
          "has Gini 0.5, each child 0.375, so the gain is 0.125.\n\n"
          "Before running: what is the gain of a split that leaves both children with the same class mix as the "
          "parent?",
   stub="def gini(labels):\n    # your code here\n    pass\n\ndef split_gain(left, right):\n    # your code here\n    pass",
   tests=tests2,
   hint1="Signal: 'how does a tree pick a split'. Pattern: impurity decrease (Gini).",
   hint2="1. Class shares p_k with `np.unique(..., return_counts=True)`. 2. `1 - sum(p**2)`. 3. Gain = "
         "`gini(parent) - (n_L / n) gini(L) - (n_R / n) gini(R)`.",
   solution=sol2,
   why="Gini is the chance that two random draws from the node have different classes. A split that keeps the "
       "same mix in both children has gain 0, so the tree will not prefer it. The last test shows why trees "
       "like peeling off small pure groups: isolating one positive from `[0, 0, 0, 0, 1, 1]` gives a gain of "
       "0.178, while with only a few rows such splits are often noise; `min_samples_leaf` guards against that.",
   complexity="`gini` is `O(n)` (`O(n log n)` with `np.unique`). A real tree sorts each feature once and scans "
              "all thresholds, `O(n log n)` per feature per node.",
   mistakes="Forgetting to weight the children by size. Using the counts instead of the proportions.",
   learn=["ai-trees-boosting"])

sol3 = '''import time
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

df = telco.drop(columns="customerID").copy()
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
y = (df.pop("Churn") == "Yes").astype(int)
num = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
cat = [c for c in df.columns if c not in num]
X_tr, X_te, y_tr, y_te = train_test_split(df, y, test_size=0.25, stratify=y, random_state=0)
prep = ColumnTransformer([("num", StandardScaler(), num),
                          ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat)])
models = {
    "logistic regression": LogisticRegression(max_iter=1000),
    "random forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=5, n_jobs=-1, random_state=0),
    "gradient boosting": HistGradientBoostingClassifier(learning_rate=0.05, max_iter=200, max_depth=3,
                                                        random_state=0),
}
for name, m in models.items():
    pipe = make_pipeline(prep, m).fit(X_tr, y_tr)
    print(f"{name:20s} test AUC {roc_auc_score(y_te, pipe.predict_proba(X_te)[:, 1]):.3f}")
# out: logistic regression  test AUC 0.844
# out: random forest        test AUC 0.842
# out: gradient boosting    test AUC 0.844'''
qc(ex, title="Does the fancy model win on churn?", minutes=7,
   prompt="Use `telco` with the same preparation as day 5 (drop `customerID`, numeric `TotalCharges` with blanks "
          "as 0, scale the 4 numeric columns, one-hot the rest, 75/25 stratified split with `random_state=0`).\n\n"
          "Compare the test ROC AUC of:\n\n"
          "- `LogisticRegression(max_iter=1000)`\n"
          "- `RandomForestClassifier(n_estimators=300, min_samples_leaf=5, random_state=0)`\n"
          "- `HistGradientBoostingClassifier(learning_rate=0.05, max_iter=200, max_depth=3, random_state=0)`\n\n"
          "Which wins? What would you tell a manager who says \"just use XGBoost, it always wins\"?",
   stub="# telco is loaded. Your code here\n",
   hint1="Signal: model comparison on a small tabular dataset. Pattern: bagging versus boosting versus a linear "
         "baseline, all on the same split.",
   hint2="1. One ColumnTransformer reused in three pipelines (`sparse_output=False` so every model gets a dense "
         "array). 2. Loop over a dict of models; fit, then `roc_auc_score` on `predict_proba(X_te)[:, 1]`.",
   solution=sol3,
   why="All three land at about the same test AUC: 0.844 for logistic regression and boosting, 0.842 for the "
       "forest. A 0.002 gap on 1,761 test rows is noise. Telco churn is driven by a few strong, mostly monotonic "
       "signals (contract, tenure, charges, fibre internet), which a linear model on one-hot features already "
       "captures. For the manager: boosting often wins on large tabular data with interactions, but not "
       "always; here the logistic model is equally good, faster, calibrated and explainable, so it is the "
       "better default. Decide with cross-validation and the business metric, not by reputation.",
   complexity="The forest builds 300 trees on about 5,300 rows (a second or two with `n_jobs=-1`); "
              "histogram boosting with 200 shallow trees is under a second.",
   mistakes="Comparing models on different splits or different preprocessing. Declaring a winner from a "
            "0.005 AUC gap on one split of 1,761 rows. Tuning the boosted model a lot and the baseline not at all.",
   learn=["ai-trees-boosting", "ai-classification-metrics"])

sol4 = '''from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

d = titanic[["survived", "pclass", "sex", "age", "fare", "sibsp", "parch"]].copy()
d["female"] = (d.pop("sex") == "female").astype(int)
d["age"] = d["age"].fillna(-1)                      # trees can split missing (-1) apart
d["random_id"] = np.random.default_rng(0).permutation(len(d))   # pure noise with many unique values
y = d.pop("survived")
X_tr, X_te, y_tr, y_te = train_test_split(d, y, test_size=0.3, stratify=y, random_state=0)

rf = RandomForestClassifier(n_estimators=300, random_state=0, n_jobs=-1).fit(X_tr, y_tr)
perm = permutation_importance(rf, X_te, y_te, n_repeats=10, random_state=0)
print(f"{'feature':10s} impurity  permutation(test)")
for name, imp, pm in sorted(zip(d.columns, rf.feature_importances_, perm.importances_mean), key=lambda t: -t[1]):
    print(f"{name:10s} {imp:8.3f}  {pm:8.3f}")
# out: feature    impurity  permutation(test)
# out: female        0.241     0.205
# out: fare          0.231     0.033
# out: random_id     0.196    -0.004
# out: age           0.163     0.046
# out: pclass        0.082     0.041
# out: sibsp         0.046    -0.001
# out: parch         0.042     0.016'''
qc(ex, title="The noise column that looks important", minutes=6,
   prompt="Use `titanic`. Features: `pclass`, `female` (0/1), `age` (missing as -1), `fare`, `sibsp`, `parch`, "
          "and `random_id`, a column of pure noise (a random permutation of 0..890, seed 0). Split 70/30 "
          "(stratified, `random_state=0`) and fit `RandomForestClassifier(n_estimators=300, random_state=0)`.\n\n"
          "Print, for each feature, the forest's built-in (impurity) importance and the permutation importance "
          "on the **test** set (`n_repeats=10, random_state=0`), sorted by impurity importance.\n\n"
          "Where does `random_id` rank under each method, and which method would you show a stakeholder?",
   stub="# titanic is loaded. Your code here\n",
   hint1="Signal: 'which features matter?' from a tree ensemble. Pattern: impurity importance is biased toward "
         "high-cardinality features; permutation importance on held-out data is not.",
   hint2="1. Build the feature frame and the noise column. 2. `rf.feature_importances_`. "
         "3. `sklearn.inspection.permutation_importance(rf, X_te, y_te, n_repeats=10, random_state=0)`.",
   solution=sol4,
   why="The forest's impurity importance ranks pure noise third (0.196), above age and class. Impurity "
       "importance is measured on the training data, and a feature with 891 unique values offers many split "
       "points, so deep trees use it to memorise individual passengers. Permutation importance on the test set "
       "asks 'how much does test accuracy drop if I shuffle this column?', and `random_id` gets -0.004, "
       "i.e. nothing. It also shows that `fare` (0.231 versus 0.033) is inflated for the same reason. Show the "
       "stakeholder permutation importance on held-out data (or SHAP values), and say that it measures "
       "predictive use, not causal effect.",
   complexity="300 trees on 623 rows plus 7 features x 10 shuffles of test predictions: a second or two.",
   mistakes="Reporting impurity importance as 'what drives survival'. Computing permutation importance on the "
            "training set (it then also rewards memorised noise). Forgetting that correlated features share or "
            "hide importance under both methods (for example `pclass` and `fare`).",
   learn=["ai-trees-boosting", "ai-features-imbalance"])

qc(ex, title="Tame an overfitting booster", minutes=3, kind="text", review=True,
   prompt="Your LightGBM model has validation AUC 0.81 and training AUC 0.99, and validation AUC starts falling "
          "after about 150 trees. Which knobs do you turn, in what order, and how do you choose their values "
          "without fooling yourself?",
   hint1="Signal: boosting plus a train/validation gap. Pattern: regularization of boosting and honest tuning "
         "with cross-validation.",
   hint2="Learning rate with early stopping; tree size; row/column subsampling; L1/L2 on leaf values; minimum "
         "data per leaf. Tune with CV on training data only, then one test evaluation.",
   solution="**Model answer:** \"First, early stopping: keep the number of trees where validation loss is best "
            "(here about 150) rather than a fixed large number. Then lower the learning rate (say 0.1 to 0.03) "
            "and let early stopping pick more trees; smaller steps generalise better. Next, smaller trees: "
            "fewer leaves or lower depth, and a higher minimum number of samples per leaf. Then randomness: "
            "row subsampling (bagging fraction 0.7 to 0.9) and column subsampling. Finally explicit L1/L2 "
            "penalties on leaf weights.\n\n"
            "To choose values honestly: tune on the training data with K-fold CV (random or Bayesian search "
            "over a few of these), use the early-stopping set inside each fold, and keep the test set untouched "
            "for one final number. If the train/validation gap stays large, check for leakage or a "
            "train/validation distribution shift before tuning more.\"",
   why="It is the boosting version of day 6: regularization is anything that limits complexity, and its "
       "strength must be chosen on validation data, not on the test set.",
   mistakes="Adding more trees. Using the test set for early stopping. Tuning ten knobs at once on one split.",
   learn=["ai-regularization-cv", "ai-trees-boosting"])

ex.save()
