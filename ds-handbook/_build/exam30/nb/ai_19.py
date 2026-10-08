import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_mid_common import setup

# Day 19 AI: focus fine-tuning-rlhf; review pretraining-decoding.
ex = Exam(19, "ai")
setup(ex, '''# numpy and arithmetic only today: no data files, no model downloads
LLAMA2_7B_PARAMS = 6_738_415_616      # published parameter count of Llama-2-7B''')

# ---------------------------------------------------------------- Q1 LoRA forward + parameter count
ex.q("Train 0.06% of the weights", minutes=8,
     prompt="""LoRA freezes a pretrained weight `W (d_out, d_in)` and learns a low-rank update `B @ A` with
`A (r, d_in)`, `B (d_out, r)`, scaled by `alpha / r`.

1. `lora_forward(x, W, A, B, alpha)`: for inputs `x (n, d_in)` return `x @ W.T + (alpha / r) * (x @ A.T) @ B.T`.
2. `merge(W, A, B, alpha)`: the single matrix to deploy after training, so inference costs nothing extra.
3. `lora_params(layer_shapes, r, n_layers)`: trainable parameters when LoRA is put on every `(d_out, d_in)` matrix in
   `layer_shapes`, in each of `n_layers` layers.

For a Llama-2-7B-like model (32 layers, `d = 4096`), LoRA with `r = 8` on the query and value projections only
(`4096 x 4096` each) trains 4,194,304 parameters. What share of the 6.74B is that? Why is `B` initialized to zero?""",
     stub="""def lora_forward(x, W, A, B, alpha):
    pass

def merge(W, A, B, alpha):
    pass

def lora_params(layer_shapes, r, n_layers):
    pass""",
     tests="""r0 = np.random.default_rng(0)
W0, A0, x0 = r0.normal(size=(6, 5)), r0.normal(size=(2, 5)), r0.normal(size=(3, 5))
B_zero, B1 = np.zeros((6, 2)), r0.normal(size=(6, 2))
check("B = 0 gives the base model", lambda: lora_forward(x0, W0, A0, B_zero, 16), x0 @ W0.T)
check("merged weights give the same output", lambda: x0 @ merge(W0, A0, B1, 16).T,
      lambda out: np.allclose(out, lora_forward(x0, W0, A0, B1, 16)))
check("scale is alpha / r", lambda: lora_forward(x0, np.zeros((6, 5)), A0, B1, 4), 2 * (x0 @ A0.T) @ B1.T)
check("q and v, r = 8, 32 layers", lambda: lora_params([(4096, 4096), (4096, 4096)], 8, 32), 4194304)
check("rectangular matrix", lambda: lora_params([(11008, 4096)], 16, 1), 241664)""",
     hint1="Signal: \"freeze the big matrix, learn a small update\". Pattern: low-rank adaptation; parameters per "
           "matrix = `r * (d_in + d_out)` instead of `d_in * d_out`.",
     hint2="1. `r = A.shape[0]`, `scale = alpha / r`.\n2. Forward: base path plus `scale * x @ A.T @ B.T` (compute "
           "`x @ A.T` first: it is small).\n3. Merge: `W + scale * B @ A`.\n4. Count: `n_layers * sum(r * (d_out + "
           "d_in))`.",
     solution="""def lora_forward(x, W, A, B, alpha):
    r = A.shape[0]
    return x @ W.T + (alpha / r) * (x @ A.T) @ B.T

def merge(W, A, B, alpha):
    return W + (alpha / A.shape[0]) * B @ A

def lora_params(layer_shapes, r, n_layers):
    return n_layers * sum(r * (d_out + d_in) for d_out, d_in in layer_shapes)

qv = lora_params([(4096, 4096), (4096, 4096)], r=8, n_layers=32)
print(qv, f"= {qv / LLAMA2_7B_PARAMS:.4%} of the model")         # 4194304 = 0.0622% of the model
all_linear = [(4096, 4096)] * 4 + [(11008, 4096), (11008, 4096), (4096, 11008)]   # q k v o, gate up down
big = lora_params(all_linear, r=16, n_layers=32)
print(big, f"= {big / LLAMA2_7B_PARAMS:.2%}")                     # 39976960 = 0.59%
print("one full 4096 x 4096 matrix:", 4096 * 4096)               # one full 4096 x 4096 matrix: 16777216""",
     why="""LoRA's bet is that the change needed to adapt a pretrained model has low intrinsic rank. Instead of
updating `d_out * d_in` numbers per matrix, it learns `r * (d_in + d_out)`: for a 4096 by 4096 matrix with r = 8 that is
65,536 instead of 16,777,216, 256 times fewer. On q and v in all 32 layers the whole adapter is 4.2M parameters,
0.0622% of the model; even r = 16 on all seven linear layers is only 0.59%.

`B = 0` at the start (with `A` random) makes `B @ A = 0`, so training starts exactly from the pretrained model and the
first steps cannot damage it; `A` random keeps the gradient of `B` non-zero. The `alpha / r` scale keeps the update
size similar when you change r, so you do not retune the learning rate.

After training, `merge` folds the update into `W`, so serving cost is identical to the base model. Or keep adapters
separate: one base model in memory and many small task adapters (a few MB each) swapped per request. The benefits are
memory (no gradients or Adam states for the frozen weights), storage, and less catastrophic forgetting; the cost is a
little quality on tasks that need large changes, such as a new language.""",
     complexity="Extra forward cost O(n * r * (d_in + d_out)), small next to O(n * d_in * d_out); zero after merging.",
     mistakes="Computing `B @ A` first in the forward pass (builds a full d by d matrix, losing the saving); "
              "initializing both A and B to zero (then both gradients are zero and nothing ever "
              "trains); forgetting the alpha / r scale when merging.",
     learn=["ai-fine-tuning-rlhf", "cheat-llm"])

# ---------------------------------------------------------------- Q2 memory math
ex.q("Will it fit on one GPU?", minutes=6,
     prompt="""Write `train_memory_gb(n_params, n_trainable, weight_bytes)` for mixed-precision training with Adam,
ignoring activations:

- every parameter is stored once for the forward pass at `weight_bytes` bytes (2 for fp16/bf16, 0.5 for 4-bit);
- every **trainable** parameter also needs a gradient (2 bytes), an fp32 master copy (4), and Adam's `m` and `v`
  (4 + 4), so 14 more bytes.

Use GB = 10^9 bytes. Compute: (a) full fine-tuning of a 7B model in bf16, (b) LoRA with 40M trainable parameters on the
same bf16 model, (c) QLoRA: the same LoRA on a 4-bit base model. Which of them fits on one 24 GB GPU, which needs an
80 GB GPU, and which needs several? What did we ignore?""",
     stub="""def train_memory_gb(n_params, n_trainable, weight_bytes=2):
    # your code here
    pass""",
     tests="""check("full fine-tuning 7B", lambda: train_memory_gb(7e9, 7e9, 2), 112.0)
check("LoRA 40M on bf16", lambda: train_memory_gb(7e9, 40e6, 2), 14.56)
check("QLoRA 40M on 4-bit", lambda: train_memory_gb(7e9, 40e6, 0.5), 4.06)""",
     hint1="Signal: \"will it fit\". Pattern: training memory = weights + gradients + optimizer states (+ "
           "activations); about 16 bytes per trainable parameter with Adam in mixed precision.",
     hint2="1. `bytes = n_params * weight_bytes + n_trainable * 14`.\n2. Divide by `1e9`.\n3. Full FT: all 7B "
           "trainable, so 16 bytes each.",
     solution="""def train_memory_gb(n_params, n_trainable, weight_bytes=2):
    return (n_params * weight_bytes + n_trainable * (2 + 4 + 4 + 4)) / 1e9

for name, args in [("full FT bf16", (7e9, 7e9, 2)), ("LoRA bf16", (7e9, 40e6, 2)), ("QLoRA 4-bit", (7e9, 40e6, 0.5))]:
    print(f"{name:12s} {train_memory_gb(*args):7.2f} GB")
# full FT bf16  112.00 GB
# LoRA bf16      14.56 GB
# QLoRA 4-bit     4.06 GB""",
     why="""Full fine-tuning with Adam costs about 16 bytes per parameter (2 weights + 2 gradients + 4 master + 8 for the
two moments): 112 GB for 7B, more than one 80 GB GPU, so it needs several GPUs with sharding of the optimizer states
(ZeRO, FSDP). LoRA keeps the 14 GB of frozen weights and adds only 0.56 GB for the adapter's training state: it fits on
one 24 GB GPU, with room for activations. QLoRA stores the frozen base in 4 bits (3.5 GB) and computes in bf16: about
4 GB, so a 7B model can be fine-tuned on a laptop-class GPU and a 65B model on one 48 GB GPU.

We ignored activations, which grow with batch size times sequence length times layers times `d`, and are often the
largest term for long sequences. Gradient checkpointing (recompute activations in the backward pass) trades about 30%
more compute for much less activation memory. Also ignored: the KV cache is not needed in training, but framework
buffers and fragmentation take a few GB.""",
     complexity="O(1) arithmetic.",
     mistakes="Forgetting the fp32 master copy; counting optimizer states for frozen weights; mixing GB and GiB; "
              "saying \"7B in fp16 is 14 GB, so it fits on a 24 GB GPU for training\".",
     learn=["ai-fine-tuning-rlhf", "ai-safety-cost"])

# ---------------------------------------------------------------- Q3 preference losses
ex.q("Learning from \"A is better than B\"", minutes=7,
     prompt="""Preference data has a prompt, a chosen answer `w` and a rejected answer `l`. Write two losses with
numerically stable code (no `log(sigmoid(...))` written naively):

- `reward_model_loss(r_w, r_l)`: Bradley-Terry loss for a reward model, `-log sigmoid(r_w - r_l)`, averaged over
  pairs (numpy arrays).
- `dpo_loss(pi_w, pi_l, ref_w, ref_l, beta)`: DPO loss, `-log sigmoid(beta * ((pi_w - ref_w) - (pi_l - ref_l)))`,
  averaged, where each argument is the summed log-probability of the whole answer under the policy (`pi_`) or the
  frozen reference model (`ref_`).

Example: policy log-probs chosen -10, rejected -12; reference -11 and -11; `beta = 0.1`. The implicit reward margin is
`0.1 * (1 - (-1)) = 0.2` and the loss is 0.5981. What is the DPO loss at the start of training, when the policy equals
the reference? What does `beta` control?""",
     stub="""def reward_model_loss(r_w, r_l):
    pass

def dpo_loss(pi_w, pi_l, ref_w, ref_l, beta=0.1):
    pass""",
     tests="""a = lambda *v: np.array(v, dtype=float)
check("reward model loss", lambda: reward_model_loss(a(2.0), a(0.5)), 0.2014, tol=1e-4)
check("reward model loss, mean of pairs", lambda: reward_model_loss(a(2.0, 0.0), a(0.5, 0.0)), (0.20141 + np.log(2)) / 2, tol=1e-4)
check("DPO example", lambda: dpo_loss(a(-10), a(-12), a(-11), a(-11), 0.1), 0.5981, tol=1e-4)
check("DPO at start = log 2", lambda: dpo_loss(a(-50, -7), a(-60, -9), a(-50, -7), a(-60, -9), 0.1), np.log(2))
check("stable for a huge wrong margin", lambda: dpo_loss(a(-2000), a(-10), a(-10), a(-10), 0.1), 199.0, tol=1e-6)""",
     hint1="Signal: pairwise preferences, \"chosen versus rejected\". Pattern: Bradley-Terry logistic loss on a score "
           "difference; DPO uses the log-probability ratio to the reference model as the implicit reward.",
     hint2="1. `-log sigmoid(x) = log(1 + exp(-x)) = np.logaddexp(0, -x)` (stable).\n2. Reward model: `x = r_w - r_l`.\n"
           "3. DPO: `x = beta * ((pi_w - ref_w) - (pi_l - ref_l))`.\n4. Take the mean.",
     solution="""def neg_log_sigmoid(x):
    return np.logaddexp(0, -x)              # log(1 + exp(-x)) without overflow

def reward_model_loss(r_w, r_l):
    return float(np.mean(neg_log_sigmoid(r_w - r_l)))

def dpo_loss(pi_w, pi_l, ref_w, ref_l, beta=0.1):
    margin = beta * ((pi_w - ref_w) - (pi_l - ref_l))
    return float(np.mean(neg_log_sigmoid(margin)))

a = lambda *v: np.array(v, dtype=float)
print(round(dpo_loss(a(-10), a(-12), a(-11), a(-11), 0.1), 4))     # 0.5981
for beta in (0.01, 0.1, 0.5):
    print("beta", beta, "loss", round(dpo_loss(a(-10), a(-12), a(-11), a(-11), beta), 4))
# beta 0.01 loss 0.6832
# beta 0.1 loss 0.5981
# beta 0.5 loss 0.3133""",
     why="""Both losses are logistic regression on a difference: the model should give the chosen answer a higher score
than the rejected one. For the reward model the score is a scalar head on an LLM, trained on human comparisons. At the
start of DPO the policy equals the reference, so the margin is 0 and the loss is `log 2 = 0.693`. The gradient raises
the policy's log-probability of chosen answers and lowers it for rejected ones, weighted by how wrong the current
margin is.

DPO's insight: in the RLHF objective (maximize reward minus `beta * KL(policy || reference)`) the optimal policy
satisfies `reward = beta * log(pi / ref) + const`, so you can plug that into the Bradley-Terry loss and train the
policy directly on preference pairs: no separate reward model, no sampling, no PPO. `beta` is the strength of the KL
leash: a small beta lets the policy move far from the reference (the same margin of log-ratios gives a smaller implicit
reward, so it must push harder); a large beta keeps it close. In the example, larger beta gives a lower loss for the
same log-probabilities.

The stable form matters: the last test has a margin of -199, and a naive `-log(sigmoid(-199))` gives `log(0) = inf` in
float32 code paths.""",
     complexity="O(number of pairs) after the forward passes; DPO needs a forward pass of both the policy and the "
                "frozen reference for each answer (the reference log-probs can be precomputed).",
     mistakes="Swapping chosen and rejected; using per-token average log-probs in one place and sums in another; "
              "forgetting the reference terms (that is plain preference fine-tuning, which drifts); naive "
              "`np.log(1 / (1 + np.exp(-x)))`.",
     learn=["ai-fine-tuning-rlhf", "ai-logistic-regression"])

# ---------------------------------------------------------------- Q4 concept: SFT, RLHF, DPO
ex.q("From base model to assistant", minutes=5, kind="text",
     prompt="""Answer out loud in 60 to 90 seconds: \"Walk me through how a pretrained base model becomes a chat
assistant: SFT, RLHF with PPO, and DPO. What does the KL penalty do, and what is reward hacking?\" Then one sentence:
when would you fine-tune at all instead of prompting?""",
     hint1="Signal: post-training pipeline. Pattern: supervised fine-tuning on demonstrations, then preference "
           "optimization (reward model + PPO, or DPO) with a KL constraint to the SFT model.",
     hint2="1. SFT: next-token loss on (prompt, ideal answer) pairs; teaches format and following instructions.\n"
           "2. RLHF: humans rank answers, reward model (Bradley-Terry), PPO maximizes reward - beta * KL.\n"
           "3. DPO: same objective, closed form, one supervised loss on pairs.\n4. Reward hacking: exploiting reward "
           "model flaws (long, flattering, confident).\n5. Fine-tune when the behaviour, style or format is stable "
           "and prompting is not enough or too costly.",
     solution="""**Model answer (about 90 s):**

\"A base model only continues text. Step one is supervised fine-tuning: tens of thousands of high-quality prompt and
response pairs, trained with the same next-token loss but only on the response tokens. That teaches the format and to
follow instructions.

Step two aligns it with preferences, because it is easier for people to say which of two answers is better than to
write the perfect one. In classic RLHF, labelers compare pairs of model answers, a reward model is trained on those
comparisons with a Bradley-Terry loss, and then PPO, a policy-gradient RL method, updates the model to maximize the
reward minus `beta` times the KL divergence from the SFT model. The KL term is a leash: without it the policy drifts
into strange text that the reward model happens to score highly, and loses fluency and diversity. That exploitation
is reward hacking: answers get longer, more flattering, more confident, without being better.

DPO reaches the same objective without RL: it uses the policy's log-probability ratio to the reference model as an
implicit reward and trains directly on the preference pairs with a logistic loss. It is simpler and more stable, so
it is now very common; PPO-style online methods are still used when you can generate fresh samples and have a good
reward, for example verifiable math or code.

I fine-tune instead of prompting when the desired behaviour is stable and specific, such as a strict output format, a
domain style or a smaller cheaper model distilled from a big one, and when good prompts plus a few examples are not
enough. For changing facts I use RAG, not fine-tuning.\"""",
     why="Post-training is now asked in nearly every LLM exam; the key points are the order of steps, why "
         "preferences, the role of KL, and when not to fine-tune.",
     learn=["ai-fine-tuning-rlhf", "ai-rag"])

# ---------------------------------------------------------------- Q5 review: perplexity after fine-tuning
ex.q("Perplexity went up after fine-tuning", minutes=4, kind="text", review=True,
     prompt="""After SFT on your support-chat data, the model's perplexity on a general web test set rose from 8.1 to
9.0, while human ratings on support chats improved a lot. Answer out loud in about 60 seconds: is this a problem?
And a teammate wants to compare your model's perplexity with another vendor's model on the same test text: is that a
fair comparison?""",
     hint1="Signal: perplexity interpretation. Pattern: perplexity measures fit to one distribution; fine-tuning "
           "shifts the distribution (some forgetting); perplexity depends on the tokenizer.",
     hint2="1. Some rise is expected: the model moved toward chat style; check it on held-out chat data and on "
           "capability evals, not web perplexity.\n2. Large drops in general skills = catastrophic forgetting: lower "
           "LR, LoRA, mix in general data.\n3. Different tokenizers give different token counts, so per-token "
           "perplexity is not comparable; use bits per byte or task metrics.",
     solution="""**Model answer (about 70 s):**

\"Not necessarily. Perplexity measures how well the model predicts one particular text distribution. SFT moved the
model toward support-chat style, so it spends a bit more probability on that and less on general web text; a rise from
8.1 to 9.0 is a mild shift, and the metric I care about, human ratings on support chats, improved. What I would check
is that real general abilities did not break: a few capability benchmarks and safety evals before and after. If they
drop a lot, that is catastrophic forgetting, and the fixes are a lower learning rate, fewer epochs, LoRA instead of
full fine-tuning, or mixing some general data into the SFT set.

Comparing perplexity with another vendor's model is not fair if the tokenizers differ. Perplexity is per token: a
tokenizer that splits text into more, smaller tokens makes each one easier to predict, so the numbers measure
different things. A tokenizer-independent version is bits per byte or per character, the total negative log-likelihood
of the text divided by its length in bytes. Even then, for a product decision I would compare both models on the task
itself, with the same prompts and a proper evaluation set.\"""",
     why="Reviews perplexity from day 18 in a realistic post-training situation.",
     learn=["ai-pretraining-decoding", "ai-fine-tuning-rlhf", "ai-llm-evaluation"])

ex.save()
