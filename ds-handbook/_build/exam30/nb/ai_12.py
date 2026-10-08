import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_mid_common import setup

# Day 12 AI: focus neural-networks; review gradient-descent.
ex = Exam(12, "ai")
setup(ex, '''from sklearn.model_selection import train_test_split

pg = pd.read_csv(data_path("penguins.csv", "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"))
feat = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
pg = pg.dropna(subset=feat)
species = sorted(pg["species"].unique())                    # ['Adelie', 'Chinstrap', 'Gentoo']
X = pg[feat].to_numpy(float)
y = pg["species"].map({s: i for i, s in enumerate(species)}).to_numpy()
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
mu, sd = X_tr.mean(0), X_tr.std(0)                           # scale with TRAIN statistics only
X_tr, X_te = (X_tr - mu) / sd, (X_te - mu) / sd
print("train", X_tr.shape, "test", X_te.shape, "classes", species)''', data=True)

ex.text("""**Data:** Palmer penguins (342 birds with all four body measurements). `X_tr`, `X_te` are standardized
bill length, bill depth, flipper length and body mass; `y_tr`, `y_te` are the species as integers 0, 1, 2
(Adelie, Chinstrap, Gentoo). Split 70/30, stratified.""")

# ---------------------------------------------------------------- Q1 backprop from scratch
ex.q("A two-layer network by hand", minutes=9,
     prompt="""Write `mlp_loss_grads(P, X, y)` for a network with one hidden ReLU layer and a softmax output:

```
h = X @ W1 + b1          (n, H)
a = relu(h)
z = a @ W2 + b2          (n, C)   logits
loss = mean cross-entropy of softmax(z) against the integer labels y
```

`P` is a dict with `W1 (d, H)`, `b1 (H,)`, `W2 (H, C)`, `b2 (C,)`. Return `(loss, grads)` where `grads` has the same
keys and shapes as `P`. No autograd: derive the backward pass yourself.

The tests do a **numerical gradient check** (central differences) on a tiny random network. Then train on the
penguins with plain gradient descent (16 hidden units, He initialization, lr 0.1, 300 epochs) and report test accuracy.

Follow-ups: what is the loss at the very start if `W2 = 0`, and why? Why do we not initialize all weights to zero?""",
     stub="""def mlp_loss_grads(P, X, y):
    n = len(y)
    # forward

    # backward

    return loss, grads""",
     tests="""rng = np.random.default_rng(0)
Pg = {"W1": rng.normal(size=(4, 5)), "b1": rng.normal(size=5) * 0.1, "W2": rng.normal(size=(5, 3)), "b2": np.zeros(3)}
Xg, yg = rng.normal(size=(6, 4)), np.array([0, 1, 2, 0, 1, 2])

def numeric_grad(name, eps=1e-6):
    G = np.zeros_like(Pg[name])
    for idx in np.ndindex(Pg[name].shape):
        old = Pg[name][idx]
        Pg[name][idx] = old + eps; up = mlp_loss_grads(Pg, Xg, yg)[0]
        Pg[name][idx] = old - eps; down = mlp_loss_grads(Pg, Xg, yg)[0]
        Pg[name][idx] = old
        G[idx] = (up - down) / (2 * eps)
    return G

for name in ["W1", "b1", "W2", "b2"]:
    check("gradient " + name + " matches numeric", lambda: mlp_loss_grads(Pg, Xg, yg)[1][name],
          lambda g: np.allclose(g, numeric_grad(name), atol=1e-6))
P0 = dict(Pg, W2=np.zeros((5, 3)))
check("loss with W2 = 0 is log(3)", lambda: mlp_loss_grads(P0, Xg, yg)[0], np.log(3))""",
     hint1="Signal: \"no autograd, derive the backward pass\". Pattern: backpropagation = chain rule applied layer by "
           "layer from the loss back to the inputs. Key fact: for softmax + cross-entropy, `dL/dz = (p - onehot) / n`.",
     hint2="1. Forward: h, a = max(h, 0), z, stable softmax p (subtract the row max).\n"
           "2. `dz = p; dz[range(n), y] -= 1; dz /= n`.\n"
           "3. `dW2 = a.T @ dz`, `db2 = dz.sum(0)`.\n"
           "4. `da = dz @ W2.T`, `dh = da * (h > 0)`.\n"
           "5. `dW1 = X.T @ dh`, `db1 = dh.sum(0)`. Each gradient has the shape of its parameter.",
     solution="""def mlp_loss_grads(P, X, y):
    n = len(y)
    h = X @ P["W1"] + P["b1"]
    a = np.maximum(h, 0)
    z = a @ P["W2"] + P["b2"]
    z = z - z.max(axis=1, keepdims=True)              # stable softmax
    p = np.exp(z)
    p /= p.sum(axis=1, keepdims=True)
    loss = -np.mean(np.log(p[np.arange(n), y]))

    dz = p.copy()
    dz[np.arange(n), y] -= 1
    dz /= n
    grads = {"W2": a.T @ dz, "b2": dz.sum(0)}
    dh = (dz @ P["W2"].T) * (h > 0)                   # ReLU passes gradient only where h > 0
    grads["W1"] = X.T @ dh
    grads["b1"] = dh.sum(0)
    return loss, grads

# train on the penguins
rng = np.random.default_rng(0)
H, C = 16, 3
P = {"W1": rng.normal(0, np.sqrt(2 / 4), (4, H)), "b1": np.zeros(H),     # He init: std = sqrt(2 / fan_in)
     "W2": rng.normal(0, np.sqrt(2 / H), (H, C)), "b2": np.zeros(C)}
for epoch in range(301):
    loss, g = mlp_loss_grads(P, X_tr, y_tr)
    for k in P:
        P[k] -= 0.1 * g[k]
    if epoch % 100 == 0:
        print("epoch", epoch, "loss", round(loss, 4))
# epoch 0 loss 2.9189
# epoch 100 loss 0.0711
# epoch 200 loss 0.0421
# epoch 300 loss 0.0304

predict = lambda X: np.argmax(np.maximum(X @ P["W1"] + P["b1"], 0) @ P["W2"] + P["b2"], axis=1)
print("train acc", round((predict(X_tr) == y_tr).mean(), 3), " test acc", round((predict(X_te) == y_te).mean(), 3))
# train acc 0.992  test acc 0.99""",
     why="""Backprop is the chain rule, reused from the output backwards so each gradient is computed once. The softmax
plus cross-entropy pair has the clean gradient `p - onehot(y)` (divided by n for the mean), and ReLU passes the gradient
through only where its input was positive. The numerical check `(L(w + eps) - L(w - eps)) / (2 eps)` is the standard
way to catch backprop bugs; it is too slow for training but perfect for tests.

On the penguins the network reaches 0.99 test accuracy (102 of 103), exactly what a plain sklearn logistic regression gets on
the same split: the classes are almost linearly separable, so a hidden layer is not needed here. Say that in an exam.

Follow-ups. With `W2 = 0` all logits are equal, so softmax gives 1/3 to each class and the loss is `log(3) = 1.0986`.
A useful sanity check: the initial loss of a C-class classifier should be close to `log(C)`. With all weights zero,
every hidden unit computes the same thing and gets the same gradient, so they stay identical forever (symmetry is never
broken). Random init with variance `2 / fan_in` (He, for ReLU) keeps activations from shrinking or exploding.""",
     complexity="One forward plus backward pass is O(n * (d*H + H*C)) time, about twice the forward cost; memory "
                "O(n * H) to keep the activations for the backward pass.",
     mistakes="Forgetting to divide by n (gradient check then fails by a factor n); using `h` instead of `a` in "
              "`dW2`; ReLU mask on `a` instead of `h` (same here but wrong for other activations); unstable softmax "
              "giving `nan`; scaling the test set with its own mean.",
     learn=["ai-neural-networks", "cheat-deep-learning", "cheat-numpy"])

# ---------------------------------------------------------------- Q2 concept: activations, vanishing gradients, init
ex.q("Why depth needs care", minutes=4, kind="text",
     prompt="""Answer out loud in 60 to 90 seconds: \"Why does a neural network need a nonlinear activation? What are
vanishing and exploding gradients, and name three things that fix them.\"""",
     hint1="Signal: deep network training problems. Pattern: products of many Jacobians in backprop.",
     hint2="1. Without nonlinearity, layers collapse into one linear map.\n2. Backprop multiplies one factor per "
           "layer: factors below 1 shrink to zero, above 1 blow up.\n3. Fixes: ReLU family, He/Xavier init, "
           "normalization layers, residual connections, gradient clipping (for exploding), LSTM gates in RNNs.",
     solution="""**Model answer (about 80 s):**

\"Without a nonlinearity, a stack of layers is still one linear function: `W2 (W1 x) = (W2 W1) x`. Depth would add
nothing, and the model could only draw linear decision boundaries. A nonlinearity like ReLU between layers lets the
network build piecewise functions and approximate almost any function.

In backprop the gradient at an early layer is a product of one factor per layer above it. If those factors are
typically below 1, the product shrinks exponentially with depth: vanishing gradients, early layers stop learning. The
sigmoid is a classic cause, since its derivative is at most 0.25. If the factors are above 1 it explodes: the loss
jumps to `nan`. RNNs suffer most because the same matrix is multiplied at every time step.

Fixes: first, ReLU-type activations, whose derivative is 1 for positive inputs. Second, careful initialization, Xavier
for tanh and He for ReLU, which keeps the activation variance constant across layers. Third, normalization layers,
batch norm or layer norm. Fourth, residual connections, `x + f(x)`, which give the gradient a direct identity path;
this is why transformers and ResNets can have 100+ layers. For exploding gradients specifically, gradient clipping by
norm.\"""",
     why="This is one of the most common deep-learning screening questions. The strong answer gives the mechanism "
         "(product of per-layer factors) and not just the names of fixes.",
     learn=["ai-neural-networks", "cheat-deep-learning"])

# ---------------------------------------------------------------- Q3 stable softmax and cross-entropy
ex.q("Logits that break naive code", minutes=5,
     prompt="""Write two functions that work for any finite logits, including huge ones:

- `softmax(z)`: row-wise softmax of a 2-D array.
- `cross_entropy(z, y)`: mean cross-entropy of the logits `z (n, C)` against integer labels `y`, computed **from the
  logits** with log-sum-exp (do not take `log(softmax(z))`).

Example: `z = [[1000, 1001, 1002]]`. A naive `np.exp(z)` gives `inf / inf = nan`. The right softmax is
`[0.0900, 0.2447, 0.6652]` and the cross-entropy for label 2 is `0.4076`.

Follow-up: why do PyTorch's `CrossEntropyLoss` and Keras's `from_logits=True` want logits, not probabilities?""",
     stub="""def softmax(z):
    # your code here
    pass

def cross_entropy(z, y):
    # your code here
    pass""",
     tests="""big = np.array([[1000.0, 1001.0, 1002.0]])
check("softmax of huge logits", lambda: softmax(big), [[0.09003057, 0.24472847, 0.66524096]], tol=1e-7)
check("softmax rows sum to 1", lambda: softmax(np.array([[1.0, 2.0], [-50.0, 50.0]])).sum(1), [1.0, 1.0])
check("cross-entropy of huge logits", lambda: cross_entropy(big, np.array([2])), 0.40760596, tol=1e-7)
check("cross-entropy with a very wrong confident logit", lambda: cross_entropy(np.array([[0.0, 800.0]]), np.array([0])), 800.0)""",
     hint1="Signal: `exp` of large numbers overflows. Pattern: softmax is shift invariant, so subtract the row max; "
           "`log softmax(z)_k = z_k - logsumexp(z)`.",
     hint2="1. `m = z.max(axis=1, keepdims=True)`.\n2. `softmax = exp(z - m) / sum(exp(z - m))`.\n"
           "3. `logsumexp = m + log(sum(exp(z - m)))`.\n4. Loss = `mean(logsumexp - z[range(n), y])`.",
     solution="""def softmax(z):
    e = np.exp(z - z.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

def cross_entropy(z, y):
    m = z.max(axis=1, keepdims=True)
    lse = (m + np.log(np.exp(z - m).sum(axis=1, keepdims=True)))[:, 0]
    return float(np.mean(lse - z[np.arange(len(y)), y]))

print(softmax(np.array([[1000.0, 1001.0, 1002.0]])))                # [[0.09   0.2447 0.6652]]
print(cross_entropy(np.array([[0.0, 800.0]]), np.array([0])))       # 800.0""",
     why="""Softmax does not change if you add the same constant to every logit, so subtracting the max makes the largest
exponent `exp(0) = 1`: no overflow, and at least one term is 1, so no division by zero.

For the loss, `log(softmax(z))` fails in the other direction: a tiny probability underflows to 0 and `log(0) = -inf`.
The last test shows why: the true class has probability `exp(-800)`, which is 0 in float64, but log-sum-exp gives the
exact loss 800. That is why frameworks take logits: they fuse softmax and log into one stable operation, and the
gradient is the simple `p - onehot`.""",
     complexity="O(n * C) time and memory.",
     mistakes="Subtracting the global max instead of the row max (still stable, but students then get the axis wrong "
              "elsewhere); forgetting `keepdims=True` (broadcasting error); applying softmax before a loss that "
              "already expects logits (double softmax, a classic silent bug).",
     learn=["ai-neural-networks", "ai-logistic-regression", "cheat-numpy"])

# ---------------------------------------------------------------- Q4 concept: dropout and other regularizers
ex.q("Your network memorizes the training set", minutes=4, kind="text",
     prompt="""Training accuracy is 99.8%, validation accuracy is 81% and still falling. Answer out loud in 60 to 90
seconds: what do you try, in which order? Explain exactly what dropout does at training time and at inference time.""",
     hint1="Signal: big train/validation gap. Pattern: overfitting, so add regularization or data; dropout is one "
           "regularizer with a train/test difference.",
     hint2="1. More data or augmentation, early stopping on validation loss.\n2. Weight decay, dropout, a smaller "
           "model.\n3. Inverted dropout: at train time zero each unit with probability p and scale the rest by "
           "`1/(1-p)`; at inference do nothing.\n4. Check for leakage or a train/validation distribution difference.",
     solution="""**Model answer (about 80 s):**

\"A large gap that keeps growing is overfitting: the network has the capacity to memorize. First, I check it is not a
data problem: is the validation set from the same distribution, and is there no leakage or duplicate between them?

Then in order of cost: early stopping, keeping the checkpoint with the best validation loss; more data or data
augmentation, which is usually the strongest fix; weight decay, which pulls weights towards zero; dropout; and a
smaller model or fewer epochs.

Dropout, at training time, sets each hidden unit to zero with probability p, say 0.1 to 0.5, with a new random mask for
every example. Units cannot rely on specific partners, so the network learns redundant features; it acts like training
an ensemble of many thinned networks that share weights. In the common inverted form, the surviving activations are
multiplied by `1 / (1 - p)` during training, so the expected activation is unchanged. At inference dropout is turned
off and nothing is rescaled. That is why forgetting `model.eval()` in PyTorch gives noisy, worse predictions.

Batch norm also regularizes a little, through the noise of batch statistics, and it too behaves differently at train
and inference time.\"""",
     why="The order (data and early stopping before architecture tweaks) and the exact train/inference behaviour "
         "of dropout are what examiners listen for.",
     learn=["ai-neural-networks", "ai-bias-variance", "ai-regularization-cv"])

# ---------------------------------------------------------------- Q5 review: loss goes to nan
ex.q("The loss turned into nan", minutes=4, kind="text", review=True,
     prompt="""Your training loss falls for 2 epochs, then jumps up and becomes `nan`. Answer out loud in about 60
seconds: list the likely causes in the order you would check them, and explain what a learning-rate warmup and a
cosine schedule do.""",
     hint1="Signal: loss explodes after starting well. Pattern: learning rate too high for the current curvature, or "
           "a numerical problem.",
     hint2="1. Learning rate too high: lower it, add warmup, clip gradients.\n2. Numerics: log of 0, division by 0, "
           "unstable softmax, fp16 overflow.\n3. Bad data: a `nan` or a huge value in a batch.\n4. Schedules: "
           "warmup = small lr at the start; cosine = decay to near zero at the end.",
     solution="""**Model answer (about 70 s):**

\"A loss that first falls and then explodes is most often a learning rate that is too high: once the model enters a
sharper region of the loss, the step overshoots, the loss grows, gradients grow, and it diverges. I would log the
gradient norm; a spike right before the `nan` confirms it. Fixes: lower the learning rate, add gradient clipping by
global norm, say 1.0, and add warmup.

Second, numerics: `log(0)` in a hand-written loss, division by a zero variance in a normalization layer, a softmax
without max subtraction, or overflow in fp16 mixed precision, where loss scaling must be on.

Third, the data: one batch with a `nan`, an infinite value or a huge unscaled feature. I would add an assertion on the
inputs and find the batch where it happened.

On schedules: warmup increases the learning rate linearly from near zero over the first few hundred or thousand steps.
Early on, Adam's second-moment estimates are noisy and the weights are random, so big steps are risky. A cosine
schedule then decays the rate smoothly from the peak to near zero, `lr_t = lr_min + 0.5 (lr_max - lr_min)(1 + cos(pi t / T))`,
which gives big exploratory steps early and fine steps at the end.\"""",
     why="Debugging training is a frequent practical follow-up. It reviews yesterday's gradient-descent ideas "
         "(step size versus curvature) in a deep-learning setting.",
     learn=["ai-gradient-descent", "ai-neural-networks"])

ex.save()
