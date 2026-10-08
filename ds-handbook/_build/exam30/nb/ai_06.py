import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_easy_common import start, qc

# Day 6 AI: focus regularization-cv; review classification-metrics, bias-variance.
ex = start(6, builtin="Built-in scikit-learn data (no download): `load_diabetes()` (442 patients, 10 features, "
                      "regression) and `load_breast_cancer()` (569 tumours, 30 features, 1 = benign). Q3 uses "
                      "simulated noise on purpose (said in the question).")

qc(ex, title="L1 or L2?", minutes=4, kind="text",
   prompt="Compare L1 (lasso) and L2 (ridge) regularization in about 90 seconds: the penalised loss, what each "
          "does to the coefficients and why, when you would pick each, and what elastic net adds.",
   hint1="Signal: 'penalty', 'sparse', 'shrink'. Pattern: regularization; the geometry of the constraint "
         "explains the zeros.",
   hint2="1. Ridge: `loss + lambda * sum(b^2)`; lasso: `loss + lambda * sum(|b|)`. 2. L2 shrinks smoothly, "
         "never exactly to 0. 3. L1 has a corner at 0, so coefficients hit exactly 0. 4. Scale features first.",
   solution="**Model answer (about 90 s):**\n\n"
            "\"Both add a penalty on coefficient size to the training loss. Ridge minimises "
            "`sum (y - Xb)^2 + lambda * sum b_j^2`; lasso uses `lambda * sum |b_j|`. Lambda trades bias for "
            "variance: bigger lambda, simpler model.\n\n"
            "Ridge shrinks all coefficients smoothly toward zero but never exactly to zero. It is great with many "
            "correlated features: it spreads the weight across them and stabilises the estimates, and it has a "
            "closed form, `(X^T X + lambda I)^-1 X^T y`.\n\n"
            "Lasso sets some coefficients exactly to zero, so it does feature selection. Geometrically the L1 "
            "constraint is a diamond with corners on the axes, and the loss contours usually touch it at a "
            "corner. Its gradient does not vanish near zero, unlike the L2 penalty, whose pull fades as b "
            "approaches 0. Downside: with correlated features it picks one somewhat arbitrarily and is unstable.\n\n"
            "Elastic net mixes both: sparse like lasso but keeps groups of correlated features like ridge. "
            "In all cases standardise the features first, because the penalty depends on their scale, and do not "
            "penalise the intercept. Choose lambda by cross-validation.\"",
   why="The key words: penalty formulas, 'exactly zero' and why (corners of the L1 ball), correlated features, "
       "scaling, and choosing lambda by CV. The Bayesian view (L2 = Gaussian prior, L1 = Laplace prior) is a "
       "good bonus.",
   mistakes="Saying ridge does feature selection. Forgetting to scale. Choosing lambda on the test set.",
   learn=["ai-regularization-cv"])

sol2 = '''from sklearn.datasets import load_diabetes
from sklearn.linear_model import Lasso, LassoCV, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_diabetes(return_X_y=True)
names = load_diabetes().feature_names
for alpha in [0.1, 1, 5, 10, 30]:
    lasso = make_pipeline(StandardScaler(), Lasso(alpha=alpha)).fit(X, y)
    ridge = make_pipeline(StandardScaler(), Ridge(alpha=alpha)).fit(X, y)
    nz_l = int((lasso[-1].coef_ != 0).sum())
    nz_r = int((ridge[-1].coef_ != 0).sum())
    print(f"alpha {alpha:>4}: lasso non-zero {nz_l:2d}   ridge non-zero {nz_r:2d}")
    if alpha == 10:
        print("   kept at alpha 10:", [n for n, c in zip(names, lasso[-1].coef_) if c != 0])
# out: alpha  0.1: lasso non-zero  9   ridge non-zero 10
# out: alpha    1: lasso non-zero  7   ridge non-zero 10
# out: alpha    5: lasso non-zero  5   ridge non-zero 10
# out: alpha   10: lasso non-zero  4   ridge non-zero 10
# out: kept at alpha 10: ['bmi', 'bp', 's3', 's5']
# out: alpha   30: lasso non-zero  2   ridge non-zero 10

cv_model = make_pipeline(StandardScaler(), LassoCV(cv=5, random_state=0)).fit(X, y)
print("LassoCV alpha:", round(cv_model[-1].alpha_, 3), " non-zero:", int((cv_model[-1].coef_ != 0).sum()))
print("dropped by LassoCV:", [n for n, c in zip(names, cv_model[-1].coef_) if c == 0])
# out: LassoCV alpha: 0.079  non-zero: 9
# out: dropped by LassoCV: ['s3']'''
qc(ex, title="Watch coefficients disappear", minutes=6,
   prompt="Use the diabetes data (10 features). Standardise the features, then for `alpha` in 0.1, 1, 5, 10, 30 "
          "fit `Lasso(alpha)` and `Ridge(alpha)` on all rows and print how many coefficients are non-zero for "
          "each.\n\n"
          "Then fit `LassoCV(cv=5, random_state=0)` (after scaling) and print the chosen alpha and its number of "
          "non-zero coefficients. Which features would you report to a doctor as 'not needed'?",
   stub="from sklearn.datasets import load_diabetes\n\n# your code here\n",
   hint1="Signal: 'which features can we drop?'. Pattern: L1 regularization path, alpha chosen by CV.",
   hint2="1. `make_pipeline(StandardScaler(), Lasso(alpha=a))`. 2. The fitted model is the last step: "
         "`pipe[-1].coef_`. 3. Count `coef_ != 0`. 4. `LassoCV` tries a grid of alphas and keeps the best CV error.",
   solution=sol2,
   why="Ridge keeps all 10 coefficients non-zero at every alpha; it only shrinks them. Lasso drops features as "
       "alpha grows: 9, 7, 5, 4, then 2 survive. CV picks a small alpha (0.079) that keeps 9 of 10, so for "
       "prediction almost every feature helps a little. The honest answer to the doctor: only `s3` is dropped, "
       "and even that is fragile. At alpha 10, `s3` is one of the 4 survivors (with bmi, bp and s5), but at the "
       "CV alpha it is the one dropped: s1 to s6 are correlated blood measures, so lasso swaps between them. "
       "'Not selected' means 'not needed given the others', not 'no effect'. To report stable selections, "
       "bootstrap the lasso and count how often each feature survives.",
   complexity="Coordinate descent on 442 x 10: milliseconds per alpha; LassoCV fits 100 alphas x 5 folds in "
              "well under a second.",
   mistakes="Not scaling (the penalty then depends on the units). Reading 'lasso dropped it' as 'it has no "
            "effect': with correlated features (here the six blood-serum measures) lasso keeps one and drops "
            "the others. In sklearn, `alpha` is the penalty strength (bigger = simpler), while in "
            "`LogisticRegression` the knob is `C = 1 / lambda` (bigger = less regularization).",
   learn=["ai-regularization-cv", "ai-linear-regression"])

sol3 = '''from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline

rng = np.random.default_rng(0)
X = rng.normal(size=(100, 2000))         # 2,000 pure-noise features
y = rng.integers(0, 2, size=100)         # random labels: true accuracy is 50%
cv = StratifiedKFold(5, shuffle=True, random_state=0)

# WRONG: pick the 20 "best" features using ALL rows, then cross-validate
X_sel = SelectKBest(f_classif, k=20).fit_transform(X, y)
wrong = cross_val_score(LogisticRegression(max_iter=1000), X_sel, y, cv=cv).mean()

# RIGHT: selection is a step of the pipeline, refit inside each training fold
pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=1000))
right = cross_val_score(pipe, X, y, cv=cv).mean()
print("selection outside CV:", round(wrong, 2))
print("selection inside CV: ", round(right, 2))
# out: selection outside CV: 0.81
# out: selection inside CV:  0.52'''
qc(ex, title="Eighty percent on random labels", minutes=7,
   prompt="This question uses **simulated** data on purpose: 100 rows, 2,000 features of pure noise, and random "
          "0/1 labels (`np.random.default_rng(0)`, normal features, then integer labels). No model can beat "
          "50% on new data.\n\n"
          "1. The wrong way: select the 20 features most related to y (`SelectKBest(f_classif, k=20)`) on all "
          "rows, then run 5-fold CV of a logistic regression on those 20 features.\n"
          "2. The right way: put the selection inside a pipeline and cross-validate the pipeline.\n\n"
          "Use `StratifiedKFold(5, shuffle=True, random_state=0)` and print both CV accuracies. Explain the gap.",
   stub="from sklearn.feature_selection import SelectKBest, f_classif\n"
        "rng = np.random.default_rng(0)\nX = rng.normal(size=(100, 2000))\ny = rng.integers(0, 2, size=100)\n\n"
        "# your code here\n",
   hint1="Signal: a data-dependent preprocessing step done before the split. Pattern: leakage in "
         "cross-validation; every fitted step must live inside the CV loop.",
   hint2="1. Wrong: `X_sel = SelectKBest(...).fit_transform(X, y)`, then `cross_val_score(lr, X_sel, y, cv=cv)`. "
         "2. Right: `make_pipeline(SelectKBest(...), LogisticRegression(...))` and `cross_val_score(pipe, X, y, cv=cv)`.",
   solution=sol3,
   why="Selecting on all 100 rows lets the labels of the validation folds choose the features. Among 2,000 "
       "noise columns, some correlate with these particular random labels by chance, and the wrong CV then "
       "rewards that chance fit: 0.81 accuracy on labels that are pure coin flips. Inside a pipeline the "
       "selection is refit on each training fold only, and the honest estimate is 0.52, about chance. Rule: "
       "every step that looks at the data (scaling, imputation, selection, encoding, resampling) is part of the "
       "model and must be fitted inside the CV loop.",
   complexity="20 tiny logistic fits plus 5 F-tests over 2,000 columns: under a second.",
   mistakes="Scaling, imputing, target-encoding, oversampling (SMOTE) or selecting features on the full data "
            "before CV: all are the same leak. Tuning hyperparameters on the same folds you report (use nested "
            "CV or a final untouched test set).",
   learn=["ai-regularization-cv", "ai-features-imbalance"],
   source=("Hastie, Tibshirani, Friedman, The Elements of Statistical Learning, section 7.10.2",
           "https://hastie.su.domains/ElemStatLearn/"))

sol4 = '''from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))
grid = GridSearchCV(pipe, {"logisticregression__C": [0.001, 0.01, 0.1, 1, 10, 100]},
                    cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="roc_auc")
grid.fit(X_tr, y_tr)
for C, s in zip(grid.cv_results_["param_logisticregression__C"], grid.cv_results_["mean_test_score"]):
    print(f"C {C:>7}: CV AUC {s:.4f}")
print("best C:", grid.best_params_["logisticregression__C"])
print("test AUC:", round(roc_auc_score(y_te, grid.predict_proba(X_te)[:, 1]), 4))
# out: C   0.001: CV AUC 0.9892
# out: C    0.01: CV AUC 0.9933
# out: C     0.1: CV AUC 0.9953
# out: C     1.0: CV AUC 0.9947
# out: C    10.0: CV AUC 0.9902
# out: C   100.0: CV AUC 0.9876
# out: best C: 0.1
# out: test AUC: 0.9929'''
qc(ex, title="Pick C without touching the test set", minutes=5,
   prompt="Use the breast cancer data. Hold out 25% as a test set (stratified, `random_state=0`). On the training "
          "part, tune `C` of a scaled logistic regression over `[0.001, 0.01, 0.1, 1, 10, 100]` with 5-fold "
          "stratified CV (`shuffle=True, random_state=0`) and ROC AUC as the score.\n\n"
          "Print the CV AUC for each C, the best C, and the test AUC of the refitted best model. Which side of the "
          "grid is underfitting?",
   stub="from sklearn.datasets import load_breast_cancer\n\n# your code here\n",
   hint1="Signal: a hyperparameter plus a held-out test set. Pattern: GridSearchCV on the training data only, "
         "then one final test evaluation.",
   hint2="1. Pipeline(StandardScaler, LogisticRegression). 2. Param name: `logisticregression__C`. "
         "3. `GridSearchCV(..., scoring='roc_auc')`, fit on train. 4. `grid.predict_proba(X_te)` uses the "
         "refitted best model.",
   solution=sol4,
   why="The CV AUC peaks at C = 0.1 (0.9953). Small C means strong regularization: C = 0.001 underfits "
       "(0.9892). Large C means weak regularization: C = 100 overfits a little (0.9876). The curve is flat near "
       "the top (0.1 and 1 differ by 0.0006), so any C from 0.01 to 1 is fine. The test AUC of the refitted "
       "model is 0.9929, close to the CV estimate, which suggests no leakage. Stratified folds keep the "
       "benign/malignant ratio the same in every fold, which makes the fold scores less noisy.",
   complexity="6 values x 5 folds = 30 fits plus one refit, each milliseconds.",
   mistakes="Putting the scaler outside the pipeline (fitted on all training folds, a small leak). Reading `C` "
            "like lasso's alpha (in LogisticRegression a small C means strong regularization). Reporting the "
            "best CV score as the expected performance: it is optimistically biased, which is why we keep a "
            "test set.",
   learn=["ai-regularization-cv", "ai-classification-metrics"])

qc(ex, title="Turn the penalty knob", minutes=3, kind="text", review=True,
   prompt="You increase the ridge penalty lambda from 0 to a huge value. Describe what happens to the training "
          "error, the validation error, the bias and the variance along the way. Where is the best lambda, and "
          "how do you find it without using the test set?",
   hint1="Signal: one knob that controls complexity. Pattern: bias-variance trade-off (regularization path).",
   hint2="1. lambda = 0: plain least squares (lowest bias, highest variance). 2. lambda huge: all coefficients "
         "near 0, the model predicts the mean. 3. Validation error is U-shaped; pick its minimum with K-fold CV "
         "on the training data.",
   solution="**Model answer:** \"At lambda = 0 we have ordinary least squares: lowest training error, lowest "
            "bias, highest variance. As lambda grows, the coefficients shrink, so training error rises steadily "
            "(the model is constrained), bias rises and variance falls. Validation error first falls, because "
            "the variance we remove is worth more than the bias we add, then rises once the model underfits. At "
            "a huge lambda all slopes are near zero and the model predicts the mean: high bias, almost zero "
            "variance.\n\n"
            "The best lambda is at the bottom of the validation curve. Find it with K-fold cross-validation on "
            "the training data over a log-spaced grid (for example 1e-3 to 1e3), optionally with the "
            "one-standard-error rule to prefer the simpler model. The test set is used once at the end.\"",
   why="It connects regularization to the bias-variance picture you learned on day 2: lambda is a complexity "
       "knob, just like tree depth or k in kNN.",
   mistakes="Saying training error can go down as lambda grows. Using a linear grid instead of a log grid. "
            "Picking lambda on the test set.",
   learn=["ai-bias-variance", "ai-regularization-cv"])

ex.save()
