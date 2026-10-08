import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_easy_common import start, qc

# Day 2 AI: focus bias-variance; review ml-framing.
ex = start(2, loads=["mpg"],
           builtin="`load_breast_cancer()` from scikit-learn (built in, no download): 569 tumours, 30 numeric "
                   "features, target 1 = benign, 0 = malignant.")

qc(ex, title="Two kinds of error", minutes=4, kind="text",
   prompt="Explain the bias-variance trade-off in about 60 seconds. Include the decomposition of the expected "
          "squared error, one example of a high-bias model and one of a high-variance model, and how model "
          "complexity moves each term.",
   hint1="Signal: 'why does my test error go up when the model gets more flexible?'. Pattern: bias-variance "
         "decomposition.",
   hint2="1. Write `expected error = bias^2 + variance + irreducible noise`. 2. Bias: error from wrong "
         "assumptions (too simple). 3. Variance: sensitivity to the particular training sample (too flexible). "
         "4. Complexity up: bias down, variance up, so test error is U-shaped.",
   solution="**Model answer (about 60 s):**\n\n"
            "\"For squared loss, the expected test error at a point splits into three parts: "
            "`E[(y - f_hat(x))^2] = bias^2 + variance + noise`. Bias is how far the average prediction, over many "
            "possible training sets, is from the truth: it comes from a model that is too simple, like a straight "
            "line through a curved relationship. Variance is how much the prediction changes when the training set "
            "changes: a deep decision tree or a degree-15 polynomial fits the noise, so a new sample gives a very "
            "different model. Noise is the part no model can remove.\n\n"
            "As complexity grows, bias falls and variance rises, so the test error is U-shaped and training error "
            "keeps falling. We pick complexity with validation data. To cut variance: more data, regularization, "
            "simpler models, bagging. To cut bias: richer features, a more flexible model, less regularization, "
            "boosting.\"\n\n"
            "**Key formula:** `E[(y - f_hat)^2] = bias^2 + variance + sigma^2`.",
   why="This is the most common ML warm-up question. A strong answer gives the formula, defines both terms "
       "over repeated training sets (not over test points), and ends with the levers for each side.",
   mistakes="Saying 'bias = training error, variance = test error' (close as a diagnostic, wrong as a definition). "
            "Forgetting the noise term. Claiming more data reduces bias (it mainly reduces variance).",
   learn=["ai-bias-variance"])

sol2 = """from sklearn.model_selection import KFold, cross_validate
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

d = mpg.dropna(subset=["horsepower"])
X, y = d[["horsepower", "weight"]], d["mpg"]
cv = KFold(5, shuffle=True, random_state=0)
for k in [1, 3, 10, 30, 100, 300]:
    model = make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=k))
    r = cross_validate(model, X, y, cv=cv, scoring="neg_root_mean_squared_error", return_train_score=True)
    print(f"k {k:3d}: train RMSE {-r['train_score'].mean():.2f}  validation RMSE {-r['test_score'].mean():.2f}")
# out: k   1: train RMSE 0.61  validation RMSE 5.57
# out: k   3: train RMSE 3.14  validation RMSE 4.50
# out: k  10: train RMSE 3.66  validation RMSE 4.03
# out: k  30: train RMSE 3.78  validation RMSE 3.86
# out: k 100: train RMSE 4.11  validation RMSE 4.15
# out: k 300: train RMSE 7.52  validation RMSE 7.54"""
qc(ex, title="How many neighbours should vote?", minutes=7,
   prompt="Use `mpg` (drop rows where `horsepower` is missing). Predict `mpg` from `horsepower` and `weight` with "
          "k-nearest-neighbours regression, for k = 1, 3, 10, 30, 100 and 300.\n\n"
          "For each k, print the mean **train** RMSE and the mean **validation** RMSE over 5-fold CV "
          "(`KFold(5, shuffle=True, random_state=0)`). Scale the two features first.\n\n"
          "Which k would you pick? Where do you see high variance and where high bias? Is a small k a simple or a "
          "complex model?",
   stub="# mpg is loaded. Your code here\n",
   hint1="Signal: one knob for model flexibility and a question about train versus validation error. Pattern: "
         "bias-variance curve with cross-validation.",
   hint2="1. `make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=k))`. "
         "2. `cross_validate(..., scoring='neg_root_mean_squared_error', return_train_score=True)`. "
         "3. Flip the sign of the scores and average them. 4. Pick the k with the lowest validation RMSE.",
   solution=sol2,
   why="Small k is the most flexible model: with k = 1 each training car predicts itself (train RMSE 0.61) but "
       "validation RMSE is 5.57, a huge gap, so high variance. Large k averages almost the whole data: with k = 300 "
       "train and validation are both bad (7.52 and 7.54), so high bias. The validation curve is U-shaped with "
       "its minimum at k = 30 (3.86), where the train/validation gap is small. Pick k = 30 (or search 20 to 50 "
       "more finely).",
   complexity="kNN has no training cost; each prediction scans the training set, `O(n * p)`. Here well under a "
              "second.",
   mistakes="Choosing k by train error (k = 1 always wins). Not scaling: weight is in thousands of pounds and "
            "would dominate the distance. Forgetting that sklearn returns negative RMSE.",
   learn=["ai-bias-variance", "ai-regularization-cv"])

sol3 = '''from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
for depth in [1, 2, 3, 5, 8, None]:
    tree = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X_tr, y_tr)
    print(f"max_depth {str(depth):>4}: train {tree.score(X_tr, y_tr):.3f}  test {tree.score(X_te, y_te):.3f}")
# out: max_depth    1: train 0.932  test 0.889
# out: max_depth    2: train 0.942  test 0.906
# out: max_depth    3: train 0.980  test 0.901
# out: max_depth    5: train 0.997  test 0.912
# out: max_depth    8: train 1.000  test 0.906
# out: max_depth None: train 1.000  test 0.906'''
qc(ex, title="A tree that memorises", minutes=6,
   prompt="Use scikit-learn's breast cancer data. Split 70/30 (stratified, `random_state=0`). Fit "
          "`DecisionTreeClassifier(max_depth=d, random_state=0)` for `d` in 1, 2, 3, 5, 8 and `None` (no limit), "
          "and print train and test accuracy for each.\n\n"
          "Which depths are high bias, which are high variance? What does the train accuracy of the unlimited "
          "tree tell you?",
   stub="from sklearn.datasets import load_breast_cancer\n\n# your code here\n",
   hint1="Signal: a single complexity knob (depth) and a train/test gap. Pattern: diagnose bias versus variance "
         "from the two errors.",
   hint2="1. `load_breast_cancer(return_X_y=True)`. 2. Loop over depths, fit, use `.score` on train and test. "
         "3. Small gap but low scores = bias; train near 1.0 with a lower test score = variance.",
   solution=sol3,
   why="Depth 1 and 2 are high bias: train accuracy is only 0.932 and 0.942. From depth 8 on, the tree is "
       "pure on the training data (train 1.000) but test stays at 0.906: the extra splits memorise single tumours, "
       "which is variance. Train accuracy 1.000 for the unlimited tree says nothing about quality; it only shows "
       "the tree can memorise. The best test score here is depth 5 (0.912), but all depths from 2 up sit within "
       "about 1 point, so prefer the simpler tree (or tune depth with CV).",
   complexity="Each tree is `O(n * p * log n)` to grow; here a few milliseconds.",
   mistakes="Reading one test split as the truth: with 171 test rows, one tumour is 0.6 points, so differences of "
            "1 to 2 points between depths are within noise. Use CV to choose the depth.",
   learn=["ai-bias-variance", "ai-trees-boosting"])

qc(ex, title="Read the learning numbers", minutes=4, kind="text",
   prompt="Three teams report their model errors (classification error rate). The best achievable error "
          "(human level) is about 1%.\n\n"
          "- Team A: train 14%, validation 15%.\n"
          "- Team B: train 1%, validation 12%.\n"
          "- Team C: train 7%, validation 18%.\n\n"
          "Diagnose each and give two concrete next steps per team.",
   hint1="Signal: train and validation errors next to a target error. Pattern: bias = gap from train to the best "
         "possible error; variance = gap from train to validation.",
   hint2="1. Avoidable bias = train error minus 1%. 2. Variance = validation minus train. 3. Fix the larger gap "
         "first.",
   solution="| Team | Avoidable bias (train - 1%) | Variance (val - train) | Diagnosis |\n|---|---|---|---|\n"
            "| A | 13 points | 1 point | High bias (underfitting) |\n"
            "| B | 0 points | 11 points | High variance (overfitting) |\n"
            "| C | 6 points | 11 points | Both |\n\n"
            "- **A:** a more flexible model (trees or boosting instead of a linear model, more depth), better "
            "features, less regularization. More data will not help much: train and validation already agree.\n"
            "- **B:** more training data or data augmentation, stronger regularization (L2, dropout, smaller "
            "depth, min samples per leaf), early stopping, bagging, fewer features.\n"
            "- **C:** fix variance and bias together: better features plus regularization; also check that "
            "train and validation come from the same distribution (an 11-point gap can be data mismatch, "
            "not only overfitting).",
   why="The two gaps tell you which lever to pull. The examiner wants you to compare train error with the "
       "best achievable error, not just with zero.",
   mistakes="Calling Team A 'fine' because the gap is small. Recommending more data for a high-bias model. "
            "Ignoring a train/validation distribution mismatch.",
   learn=["ai-bias-variance"])

qc(ex, title="A random split for next month's sales", minutes=3, kind="text", review=True,
   prompt="A colleague forecasts next month's daily sales. She uses a random 80/20 split of three years of daily "
          "rows, with features like 'sales 7 days ago' and 'mean sales of this month'. Validation MAPE is 4%; "
          "in production it is 15%. What went wrong and how should she validate?",
   hint1="Signal: time-ordered data and a big offline/online gap. Pattern: leakage through the split "
         "(and through features computed with future data).",
   hint2="1. Random split puts future days in train. 2. 'Mean sales of this month' uses days after the "
         "prediction date. 3. Use a time-based split that mimics production.",
   solution="**Model answer:** \"Two leaks. First, a random split mixes days: the model trains on, say, the 14th "
            "and 16th and is tested on the 15th, so it interpolates instead of forecasting. Second, 'mean sales "
            "of this month' is computed with the whole month, including days after the prediction date, so it "
            "contains the answer. In production neither is available, so error jumps from 4% to 15%.\n\n"
            "Fix: build features only from data before the forecast date (lags of at least the forecast horizon, "
            "rolling means that end at the cutoff), and validate with a time split: train on months 1 to k, test "
            "on month k+1, then roll forward (expanding window, `TimeSeriesSplit`). Report the average over "
            "several cutoffs.\"",
   why="Leakage through the split is the most common reason an offline score does not hold online. The rule: "
       "validation must copy the production situation, including what is known at prediction time.",
   mistakes="Only fixing the split and keeping the leaky feature. Using lag-1 features for a 30-day-ahead forecast.",
   learn=["ai-ml-framing", "ai-regularization-cv"])

ex.save()
