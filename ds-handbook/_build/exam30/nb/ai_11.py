import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_mid_common import setup

# Day 11 AI: focus gradient-descent; review unsupervised, logistic-regression.
ex = Exam(11, "ai")
setup(ex, '''mpg = pd.read_csv(data_path("mpg.csv", "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv"))
mpg = mpg.dropna(subset=["horsepower"])
X_raw = mpg[["weight", "horsepower", "model_year"]].to_numpy(float)
y_mpg = mpg["mpg"].to_numpy(float)
# standardized features plus a column of ones for the bias
Xs = np.c_[np.ones(len(y_mpg)), (X_raw - X_raw.mean(0)) / X_raw.std(0)]

telco = pd.read_csv(data_path("telco_churn.csv",
    "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"))
T_raw = np.c_[telco["tenure"], telco["MonthlyCharges"], telco["SeniorCitizen"],
              telco["Contract"] == "Month-to-month"].astype(float)
y_churn = (telco["Churn"] == "Yes").astype(int).to_numpy()
Xt = np.c_[np.ones(len(y_churn)), (T_raw - T_raw.mean(0)) / T_raw.std(0)]
print("mpg:", Xs.shape, " telco:", Xt.shape)''', data=True)

ex.text("""**Data:** `Xs`, `y_mpg` = the seaborn `mpg` cars table (392 cars with horsepower): bias column plus
standardized `weight`, `horsepower`, `model_year`; target miles per gallon. `Xt`, `y_churn` = IBM Telco churn
(7,043 customers): bias column plus standardized `tenure`, `MonthlyCharges`, `SeniorCitizen`, month-to-month contract
flag; target churned (1) or not (0).""")

# ---------------------------------------------------------------- Q1 batch GD for linear regression
ex.q("Fit a regression with your own optimizer", minutes=6,
     prompt="""Write `gd_linreg(X, y, lr, epochs)`: full-batch gradient descent on the mean squared error
`L(w) = mean((X @ w - y)**2)`, starting from `w = 0`. `X` already contains the bias column. Return `w`.

The test compares your weights with the exact least-squares answer (`np.linalg.lstsq`) on the mpg data.

Follow-ups to answer out loud:
1. Run it on raw (not standardized) features with `lr=0.1`. What happens and why?
2. What is the largest learning rate that still converges for this loss, in terms of the matrix `X.T @ X / n`?
3. With 50 million rows instead of 392, what do you change?""",
     stub="""def gd_linreg(X, y, lr=0.1, epochs=2000):
    w = np.zeros(X.shape[1])
    # your code here
    return w""",
     tests="""w_exact = np.linalg.lstsq(Xs, y_mpg, rcond=None)[0]
check("weights match least squares", lambda: gd_linreg(Xs, y_mpg, 0.1, 2000), w_exact, tol=1e-3)
check("no steps means w = 0", lambda: gd_linreg(Xs, y_mpg, 0.1, 0), np.zeros(4))""",
     hint1="Signal: minimize a smooth loss step by step. Pattern: batch gradient descent, `w <- w - lr * grad`. "
           "For MSE the gradient is `(2/n) * X.T @ (X @ w - y)`.",
     hint2="1. Loop `epochs` times.\n2. Residual `r = X @ w - y`.\n3. Gradient `g = 2 * X.T @ r / n`.\n"
           "4. `w = w - lr * g`.\n5. Print the MSE every few hundred steps to see it fall and flatten.",
     solution="""def gd_linreg(X, y, lr=0.1, epochs=2000):
    n = len(y)
    w = np.zeros(X.shape[1])
    for _ in range(epochs):
        grad = 2 * X.T @ (X @ w - y) / n
        w = w - lr * grad
    return w

w = gd_linreg(Xs, y_mpg)
print("w:", w.round(3))                              # w: [23.446 -5.47  -0.192  2.755]
print("MSE:", round(np.mean((Xs @ w - y_mpg) ** 2), 3))  # MSE: 11.647
for ep in (10, 100, 300):
    w_ep = gd_linreg(Xs, y_mpg, 0.1, ep)
    print(ep, "epochs, MSE", round(np.mean((Xs @ w_ep - y_mpg) ** 2), 3))
# 10 epochs, MSE 19.131
# 100 epochs, MSE 11.658
# 300 epochs, MSE 11.647
H = 2 * Xs.T @ Xs / len(y_mpg)                       # Hessian of the MSE
print("max stable lr:", round(2 / np.linalg.eigvalsh(H).max(), 3))  # max stable lr: 0.475""",
     why="""Gradient descent moves against the gradient, the direction of steepest increase. For MSE the loss is a
convex bowl, so with a small enough step it reaches the same answer as the closed form (here to 1e-3 after 2000 steps;
the MSE is already flat at 11.647 after about 300).

Follow-ups. (1) With raw features `weight` is in the thousands, so the gradient is huge, every step overshoots and the
weights blow up to `inf`/`nan`. Raw scales also make the bowl very long and thin (badly conditioned), so even a safe
learning rate zig-zags. Standardize first. (2) For a quadratic loss GD converges only if `lr < 2 / lambda_max`, where
`lambda_max` is the largest eigenvalue of the Hessian `2 * X.T @ X / n`; here that is 0.475, so `lr=0.1` is safe.
(3) With 50M rows, use mini-batch SGD (batches of 256 to 4096 rows, data streamed from disk), a learning-rate schedule,
or simply a closed form / distributed solver because linear regression has one. For deep nets there is no closed
form, which is why GD matters.""",
     complexity="O(epochs * n * d) time, O(d) extra memory. The closed form costs O(n * d^2 + d^3).",
     mistakes="Forgetting the bias column; dividing by n in one place but not another; using the sum instead of "
              "the mean (then the safe learning rate depends on n); not standardizing.",
     learn=["ai-gradient-descent", "ai-linear-regression", "cheat-numpy"])

# ---------------------------------------------------------------- Q2 optimizer steps
ex.q("Write one step of two popular optimizers", minutes=7,
     prompt="""Implement one update step of each optimizer (numpy arrays in, numpy arrays out):

- `momentum_step(w, g, vel, lr, beta)`: heavy-ball momentum in the PyTorch form `vel = beta * vel + g`,
  `w = w - lr * vel`.
- `adam_step(w, g, m, v, t, lr, b1, b2, eps)`: Adam with bias correction (`t` starts at 1).

Example: `w = [1, -2]`, gradient `g = [0.5, -4]`, fresh state. The first Adam step with `lr = 0.1` moves **both**
weights by almost exactly 0.1, even though one gradient is 8 times bigger. Why?

Then compare plain GD, momentum and Adam on the badly scaled bowl `f(w) = 0.5 * (w1**2 + 50 * w2**2)` from
`w = [10, 1]`: how many steps until `f < 1e-6`?""",
     stub="""def momentum_step(w, g, vel, lr=0.1, beta=0.9):
    # your code here
    return w, vel

def adam_step(w, g, m, v, t, lr=0.1, b1=0.9, b2=0.999, eps=1e-8):
    # your code here
    return w, m, v""",
     tests="""w0, g0, z = np.array([1.0, -2.0]), np.array([0.5, -4.0]), np.zeros(2)
check("momentum first step w", lambda: momentum_step(w0, g0, z, 0.1, 0.9)[0], [0.95, -1.6])
check("momentum keeps moving with zero gradient", lambda: momentum_step(w0, z, np.ones(2), 0.1, 0.9)[0], [0.91, -2.09])
check("adam first step w", lambda: adam_step(w0, g0, z, z, 1)[0], [0.9, -1.9])
check("adam first m", lambda: adam_step(w0, g0, z, z, 1)[1], [0.05, -0.4])
check("adam first v", lambda: adam_step(w0, g0, z, z, 1)[2], [0.00025, 0.016])""",
     hint1="Signal: \"one step of an optimizer\". Pattern: momentum keeps a running sum of gradients (velocity); "
           "Adam keeps running means of `g` and `g**2` and divides one by the square root of the other.",
     hint2="Adam:\n1. `m = b1*m + (1-b1)*g`, `v = b2*v + (1-b2)*g**2`.\n"
           "2. `m_hat = m / (1 - b1**t)`, `v_hat = v / (1 - b2**t)`.\n"
           "3. `w = w - lr * m_hat / (sqrt(v_hat) + eps)`.\n"
           "At t = 1, `m_hat = g` and `v_hat = g**2`, so the step is `lr * g / |g|`.",
     solution="""def momentum_step(w, g, vel, lr=0.1, beta=0.9):
    vel = beta * vel + g
    return w - lr * vel, vel

def adam_step(w, g, m, v, t, lr=0.1, b1=0.9, b2=0.999, eps=1e-8):
    m = b1 * m + (1 - b1) * g
    v = b2 * v + (1 - b2) * g * g
    m_hat = m / (1 - b1 ** t)
    v_hat = v / (1 - b2 ** t)
    return w - lr * m_hat / (np.sqrt(v_hat) + eps), m, v

curv = np.array([1.0, 50.0])                # f(w) = 0.5 * sum(curv * w**2), gradient = curv * w
def steps_to_converge(kind, lr, max_steps=5000):
    w, a, b = np.array([10.0, 1.0]), np.zeros(2), np.zeros(2)
    for t in range(1, max_steps + 1):
        g = curv * w
        if kind == "gd":
            w = w - lr * g
        elif kind == "momentum":
            w, a = momentum_step(w, g, a, lr)
        else:
            w, a, b = adam_step(w, g, a, b, t, lr)
        if 0.5 * np.sum(curv * w * w) < 1e-6:
            return t
    return "diverged or too slow"

for kind, lr in [("gd", 0.02), ("gd", 0.039), ("gd", 0.041), ("momentum", 0.02), ("adam", 0.1)]:
    print(kind, lr, steps_to_converge(kind, lr))
# gd 0.02 439
# gd 0.039 223
# gd 0.041 diverged or too slow
# momentum 0.02 153
# adam 0.1 305""",
     why="""Adam divides each coordinate's step by the root mean square of its own past gradients, so the step size is
roughly `lr` in every direction whatever the gradient scale. At t = 1 the bias correction makes `m_hat = g` and
`v_hat = g**2`, so the step is `lr * sign(g)`: both weights move by 0.1. Without bias correction, `m` and `v` start at
zero and the first steps would be badly scaled.

The bowl has curvature 1 in one direction and 50 in the other. Plain GD must keep `lr < 2 / 50 = 0.04` (0.041 diverges)
and then crawls along the flat direction (223 steps even at lr 0.039, right below the limit). Momentum adds up the consistent push along the
flat direction while the zig-zag in the steep direction cancels, so it needs only 153 steps at a smaller rate. Adam
rescales each direction, so it is robust to the scaling without tuning, but near the minimum it can oscillate, which is
why it needed 305 steps here. In practice: Adam or AdamW is the default for transformers; SGD with momentum is still
common for CNNs and often generalizes a little better when well tuned.""",
     complexity="Both steps are O(d) time. Momentum stores one extra vector, Adam two (m and v): optimizer memory "
                "is 2x the parameter count for Adam, which matters for large models.",
     mistakes="Forgetting bias correction; using `t = 0` (division by zero); putting eps inside the square root in "
              "a different place than the reference and then comparing exact numbers; updating `w` before `m`, `v`.",
     learn=["ai-gradient-descent", "cheat-deep-learning"])

# ---------------------------------------------------------------- Q3 concept batch size / SGD / AdamW
ex.q("Batch size, learning rate and weight decay", minutes=4, kind="text",
     prompt="""An examiner asks, in one breath: \"What is the difference between batch, mini-batch and stochastic
gradient descent? If I increase the batch size from 32 to 1024, what should I do with the learning rate? And why do
people use AdamW instead of Adam with L2 regularization?\"

Answer out loud in 60 to 90 seconds.""",
     hint1="Signal: optimizer trade-offs. Pattern: gradient noise versus cost per step; learning rate scaling; "
           "decoupled weight decay.",
     hint2="1. Batch = exact gradient, expensive; SGD = one example, very noisy; mini-batch = the middle, uses GPUs "
           "well.\n2. Bigger batch = less noise, so you can take bigger steps: linear scaling rule plus warmup.\n"
           "3. In Adam, an L2 term goes through the adaptive scaling; AdamW subtracts `lr * wd * w` directly.",
     solution="""**Model answer (about 75 s):**

\"All three follow the gradient of the loss; they differ in how many examples estimate it. Batch GD uses all n rows:
an exact gradient, but one step costs a full pass, so it does not scale. Stochastic GD uses one example: cheap and very
noisy. Mini-batch, say 32 to 4096 rows, is the standard: the noise falls like `1 / sqrt(batch size)`, and the matrix
math uses the GPU well. Some noise is even helpful: it helps escape sharp minima.

If I go from 32 to 1024, the gradient is about 32 times less noisy, so I can take bigger steps. The common heuristic is
the linear scaling rule, `lr_new = lr_old * 1024 / 32`, together with a warmup of the learning rate over the first few
hundred or thousand steps so early steps do not explode. For Adam a square-root rule is often closer. Very large
batches can generalize worse, so I would validate it.

On AdamW: with plain SGD, L2 regularization and weight decay are the same thing. In Adam, an L2 term is added to the
gradient and then divided by `sqrt(v_hat)`, so weights with large gradients get almost no decay. AdamW decouples it: it
applies `w = w - lr * wd * w` directly, outside the adaptive scaling. That regularizes every weight evenly and is the
default for transformers.\"""",
     why="These three ideas (noise versus cost, scaling the learning rate with the batch, decoupled weight decay) are "
         "the usual follow-ups after \"explain gradient descent\" in ML exams.",
     learn=["ai-gradient-descent", "ai-regularization-cv", "cheat-deep-learning"])

# ---------------------------------------------------------------- Q4 review: logistic regression from scratch
ex.q("Churn model without sklearn", minutes=6, review=True,
     prompt="""Write `fit_logreg(X, y, lr, epochs)`: logistic regression trained by full-batch gradient descent on
the mean log loss, starting from `w = 0`. `X` already has the bias column. Return `w`.

The test compares your weights with sklearn's `LogisticRegression` (no regularization) on the Telco data `Xt`,
`y_churn`.

Then answer: which feature raises churn risk most per standard deviation? Why is the gradient of the log loss so similar
to the gradient of linear regression?""",
     stub="""def fit_logreg(X, y, lr=0.5, epochs=2000):
    w = np.zeros(X.shape[1])
    # your code here
    return w""",
     tests="""from sklearn.linear_model import LogisticRegression
sk = LogisticRegression(C=1e10, max_iter=5000).fit(Xt[:, 1:], y_churn)   # huge C = no regularization
w_sk = np.r_[sk.intercept_, sk.coef_[0]]
check("weights match sklearn", lambda: fit_logreg(Xt, y_churn, 0.5, 2000), w_sk, tol=1e-3)""",
     hint1="Signal: binary target, \"without sklearn\". Pattern: logistic regression = sigmoid of a linear score, "
           "trained with gradient descent on log loss. The gradient is `X.T @ (p - y) / n`.",
     hint2="1. `p = 1 / (1 + exp(-X @ w))`.\n2. `grad = X.T @ (p - y) / n`.\n3. `w -= lr * grad`, repeat.\n"
           "4. Read the coefficients: features are standardized, so they are comparable (change in log-odds per SD).",
     solution="""def fit_logreg(X, y, lr=0.5, epochs=2000):
    w = np.zeros(X.shape[1])
    for _ in range(epochs):
        p = 1 / (1 + np.exp(-X @ w))
        w = w - lr * X.T @ (p - y) / len(y)
    return w

w = fit_logreg(Xt, y_churn)
names = ["bias", "tenure", "MonthlyCharges", "SeniorCitizen", "month_to_month"]
print({k: float(v) for k, v in zip(names, w.round(3))})
# {'bias': -1.54, 'tenure': -0.953, 'MonthlyCharges': 0.839, 'SeniorCitizen': 0.178, 'month_to_month': 0.624}
p = 1 / (1 + np.exp(-Xt @ w))
print("log loss:", round(-np.mean(y_churn * np.log(p) + (1 - y_churn) * np.log(1 - p)), 4))  # log loss: 0.4362""",
     why="""The log loss is convex in `w`, so gradient descent reaches the same optimum as sklearn's solver.

Coefficients are changes in log-odds per one standard deviation. `MonthlyCharges` raises churn most (+0.839 per SD),
then the month-to-month contract (+0.624); longer tenure lowers it strongly (-0.953). `exp(0.839) = 2.3`, so one SD
more in monthly charges multiplies the odds of churn by about 2.3, holding the others fixed. This is association, not
causation.

The gradient `X.T @ (p - y) / n` has the same form as linear regression's `X.T @ (Xw - y) / n` (up to the factor 2)
because the sigmoid's derivative `p (1 - p)` cancels against the derivative of the log loss. Both are generalized
linear models with their canonical link: \"prediction minus target, times the inputs\".""",
     complexity="O(epochs * n * d).",
     mistakes="Using the MSE gradient with the sigmoid (non-convex and slow); `np.exp` overflow on unscaled "
              "features; comparing with sklearn's default `C=1.0`, which adds L2 regularization.",
     learn=["ai-logistic-regression", "ai-gradient-descent"])

# ---------------------------------------------------------------- Q5 review: k-means as optimization
ex.q("Why k-means always stops but not always well", minutes=4, kind="text", review=True,
     prompt="""Answer out loud in about 60 seconds: \"What objective does k-means minimize? Prove in one sentence that
Lloyd's algorithm always converges. Why can it still give a bad answer, and what do you do about it? How is it related
to gradient descent?\"""",
     hint1="Signal: \"objective, convergence\" for clustering. Pattern: k-means = coordinate descent on the "
           "within-cluster sum of squares (inertia).",
     hint2="1. Objective: sum of squared distances to the assigned centroid.\n2. Assignment step and update step "
           "each never increase it; finite number of partitions.\n3. Non-convex: local minima, so k-means++ and "
           "several restarts (`n_init`).\n4. Scale features; choose k with elbow / silhouette / business use.",
     solution="""**Model answer (about 60 s):**

\"k-means minimizes the inertia, `sum over points of ||x - mu_c(x)||**2`, the squared distance of each point to its
cluster's centroid. Lloyd's algorithm alternates two steps: assign each point to the nearest centroid, which can only
lower the objective for fixed centroids, and move each centroid to the mean of its points, which is the exact minimizer
for fixed assignments. The objective never increases and there are finitely many partitions, so it must stop.

But the objective is not convex, so it stops at a local minimum that depends on the starting centroids. The fixes are
k-means++ initialization, which spreads the first centroids out, and several restarts keeping the lowest inertia;
sklearn's `n_init` does this. Also standardize features, because squared distance is dominated by the largest-scale
feature, and remember k-means assumes round, similar-size clusters.

The link to gradient descent: Lloyd's algorithm is coordinate descent, exact minimization in one block of variables at
a time. Mini-batch k-means for big data is a stochastic-gradient version of the centroid update.\"""",
     why="It connects today's optimization view (objective, steps that decrease it, local minima) with the "
         "unsupervised review topic. Examiners like the one-line convergence proof.",
     learn=["ai-unsupervised", "ai-gradient-descent"])

ex.save()
