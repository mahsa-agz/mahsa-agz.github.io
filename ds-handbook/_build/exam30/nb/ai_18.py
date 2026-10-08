import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_mid_common import setup, SMS

# Day 18 AI: focus pretraining-decoding; review attention-transformer.
ex = Exam(18, "ai")
setup(ex, SMS, '''import re
from collections import Counter

# a tiny "pretraining corpus": the ham (non-spam) messages, deduplicated, shuffled, 80/20 split
ham = sms.loc[sms["label"] == "ham", "text"].drop_duplicates().sample(frac=1, random_state=0)
sents = [s for s in (re.findall(r"[a-z0-9']+", t.lower()) for t in ham) if s]
cut = int(0.8 * len(sents))
word_count = Counter(w for s in sents[:cut] for w in s)
keep = {w for w, c in word_count.items() if c >= 2}            # words seen once in train become <unk>
unk = lambda S: [[w if w in keep else "<unk>" for w in s] for s in S]
ham_train, ham_test = unk(sents[:cut]), unk(sents[cut:])
print("train sentences", len(ham_train), "test sentences", len(ham_test), "vocab", len(keep) + 1)
print(ham_train[0])''', data=True)

ex.text("""**Data:** the ham messages of the SMS Spam Collection as a tiny language-modelling corpus: 4,514 unique
messages, lowercased and split into words, shuffled, 80% `ham_train` and 20% `ham_test` (lists of token lists). Words
seen only once in train are replaced by `<unk>` in both sets, so every test token is in the vocabulary.""")

# ---------------------------------------------------------------- Q1 bigram LM + perplexity
ex.q("A language model you can count by hand", minutes=8,
     prompt="""Write `bigram_perplexity(train, test, k)`:

- Wrap every sentence as `<s> w1 ... wn </s>`.
- Count bigrams on `train`. With add-k smoothing, `P(w | prev) = (count(prev, w) + k) / (count(prev) + k * V)`, where
  `count(prev)` is the number of bigrams that start with `prev` and `V` is the number of possible next tokens (the
  train words plus `</s>`).
- Perplexity on `test` = `exp(-mean log P)` over every predicted token, including each `</s>`.

Toy check: train = test = `[["a", "b"]]`. With `k = 0` every prediction has probability 1, so perplexity is 1. With
`k = 1`, `V = 3` and every prediction is `(1 + 1) / (1 + 3) = 0.5`, so perplexity is 2.

Then on the SMS corpus compare `k = 1`, `0.1`, `0.01` and a unigram model (each word with probability
`count / total`, no context), on test and on train. What do you conclude?""",
     stub="""def bigram_perplexity(train, test, k=1.0):
    # your code here
    pass""",
     tests="""check("perfect fit, k = 0", lambda: bigram_perplexity([["a", "b"]], [["a", "b"]], 0), 1.0)
check("add-one toy", lambda: bigram_perplexity([["a", "b"]], [["a", "b"]], 1), 2.0)
check("unseen bigram toy", lambda: bigram_perplexity([["a", "b"], ["b"]], [["b", "a"]], 1), 0.02 ** (-1 / 3))""",
     hint1="Signal: next-word probabilities from counts, \"perplexity\". Pattern: n-gram language model with "
           "smoothing; perplexity = exp of the average negative log-likelihood per token (cross-entropy).",
     hint2="1. Two Counters: `bigram[(prev, w)]` and `context[prev]`.\n2. `V = len(train words) + 1` for `</s>`.\n"
           "3. Loop over test bigrams, sum `log((bigram + k) / (context + k * V))`, count them.\n"
           "4. Return `exp(-total / count)`.",
     solution="""def bigram_perplexity(train, test, k=1.0):
    bigram, context = Counter(), Counter()
    for s in train:
        seq = ["<s>"] + s + ["</s>"]
        for prev, w in zip(seq, seq[1:]):
            bigram[(prev, w)] += 1
            context[prev] += 1
    V = len({w for s in train for w in s}) + 1                       # + </s>
    logp = []
    for s in test:
        seq = ["<s>"] + s + ["</s>"]
        for prev, w in zip(seq, seq[1:]):
            logp.append(np.log((bigram[(prev, w)] + k) / (context[prev] + k * V)))
    return float(np.exp(-np.mean(logp)))

def unigram_perplexity(train, test):
    u = Counter(w for s in train for w in s + ["</s>"])
    total = sum(u.values())
    return float(np.exp(-np.mean([np.log(u[w] / total) for s in test for w in s + ["</s>"]])))

print("unigram     test", round(unigram_perplexity(ham_train, ham_test), 1))
for k in (1, 0.1, 0.01):
    print(f"bigram k={k:<4} test", round(bigram_perplexity(ham_train, ham_test, k), 1),
          " train", round(bigram_perplexity(ham_train, ham_train, k), 1))
# unigram     test 318.7
# bigram k=1    test 670.2  train 555.6
# bigram k=0.1  test 319.4  train 142.7
# bigram k=0.01 test 269.3  train 55.5""",
     why="""Perplexity is `exp(cross-entropy)`: the effective number of equally likely choices the model hesitates
between at each token. Lower is better, and it is only comparable on the same test tokens with the same vocabulary.
The third toy test: `V = 3`, `count(<s>) = 2`, `count(b) = 2`, `count(a) = 1`. The test
predictions are `<s> -> b` (1 + 1) / (2 + 3) = 0.4, `b -> a` unseen (0 + 1) / (2 + 3) = 0.2 and `a -> </s>` unseen
(0 + 1) / (1 + 3) = 0.25, so perplexity = `(0.4 * 0.2 * 0.25) ** (-1/3) = 3.684`.

On the SMS corpus: add-one smoothing (k = 1) is terrible, 670, worse than the unigram's 319, because with 2,700
possible next words it moves most of the probability mass to bigrams never seen. A small k = 0.01 is best on test
(269). The train perplexity (55.5) is far below the test (269.3): the bigram table memorizes the training text,
classic overfitting from sparse counts. This is exactly why neural language models won: they share statistics across
similar contexts through embeddings instead of counting each exact context, and large transformers trained on
trillions of tokens reach single-digit perplexities on normal English text.""",
     complexity="O(training tokens) to count, O(test tokens) to score; the bigram table can grow to O(V^2) in the "
                "worst case but in practice stores only seen pairs.",
     mistakes="Forgetting `</s>` (the model never learns to stop, and perplexity looks lower); `V` that includes "
              "`<s>` (it is never predicted); averaging probabilities instead of log-probabilities; comparing "
              "perplexities computed with different vocabularies or tokenizers.",
     learn=["ai-pretraining-decoding", "ai-nlp-basics"])

# ---------------------------------------------------------------- Q2 temperature and top-p
ex.q("Turning one distribution into many behaviours", minutes=6,
     prompt="""A model gives these logits for the next token:

| token | the | a | cat | dog | banana |
|---|---|---|---|---|---|
| logit | 2.0 | 1.5 | 1.0 | 0.5 | -1.0 |

Write:
- `apply_temperature(logits, T)`: `softmax(logits / T)` (numpy array in, probabilities out).
- `top_p_filter(probs, p)`: nucleus filtering. Keep the smallest set of most likely tokens whose total probability is
  at least `p`, set the others to 0, renormalize. Same order as the input.

At `T = 1` the probabilities are about `[0.445, 0.270, 0.164, 0.099, 0.022]`. With `p = 0.9`, which tokens survive?
What happens to the distribution as `T -> 0` and as `T` grows? What does `T = 0` mean in an API?""",
     stub="""def apply_temperature(logits, T):
    # your code here
    pass

def top_p_filter(probs, p):
    # your code here
    pass

logits = np.array([2.0, 1.5, 1.0, 0.5, -1.0])""",
     tests="""lg = np.array([2.0, 1.5, 1.0, 0.5, -1.0])
check("T = 1", lambda: apply_temperature(lg, 1.0), [0.44497, 0.26989, 0.1637, 0.09929, 0.02215], tol=1e-5)
check("T = 0.5 sharpens", lambda: apply_temperature(lg, 0.5), [0.64289, 0.23651, 0.08701, 0.03201, 0.00159], tol=1e-5)
check("T = 100 is almost uniform", lambda: apply_temperature(lg, 100.0), lambda q: np.allclose(q, 0.2, atol=0.01))
pr = np.array([0.44497, 0.26989, 0.1637, 0.09929, 0.02215])
check("top-p 0.9 keeps 4 tokens", lambda: top_p_filter(pr, 0.9), np.r_[pr[:4] / pr[:4].sum(), 0], tol=1e-6)
check("top-p 0.5 keeps 2 tokens", lambda: top_p_filter(pr, 0.5), np.r_[pr[:2] / pr[:2].sum(), 0, 0, 0], tol=1e-6)
check("top-p 0.4 keeps only the best", lambda: top_p_filter(pr, 0.4), [1, 0, 0, 0, 0])
check("order does not matter", lambda: top_p_filter(pr[::-1], 0.5), np.r_[0, 0, 0, pr[1::-1] / pr[:2].sum()], tol=1e-6)""",
     hint1="Signal: sampling knobs on a next-token distribution. Pattern: temperature rescales logits before the "
           "softmax; top-p (nucleus) truncates the sorted cumulative distribution.",
     hint2="1. Temperature: `z = logits / T; z -= z.max(); e = exp(z); e / e.sum()`.\n2. Top-p: `order = "
           "argsort(-probs)`, `cum = cumsum(probs[order])`.\n3. Keep a token if the mass **before** it is still "
           "below p: `cum - probs[order] < p`.\n4. Zero the rest, renormalize.",
     solution="""def apply_temperature(logits, T):
    z = np.asarray(logits, dtype=float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

def top_p_filter(probs, p):
    order = np.argsort(-probs)
    sorted_p = probs[order]
    keep_sorted = (np.cumsum(sorted_p) - sorted_p) < p      # mass before this token is still below p
    out = np.zeros_like(probs, dtype=float)
    out[order[keep_sorted]] = sorted_p[keep_sorted]
    return out / out.sum()

logits = np.array([2.0, 1.5, 1.0, 0.5, -1.0])
for T in (0.5, 1.0, 2.0):
    q = apply_temperature(logits, T)
    entropy = -(q * np.log2(q)).sum()
    print("T", T, q.round(3), "entropy", round(entropy, 2), "bits")
# T 0.5 [0.643 0.237 0.087 0.032 0.002] entropy 1.38 bits
# T 1.0 [0.445 0.27  0.164 0.099 0.022] entropy 1.91 bits
# T 2.0 [0.325 0.253 0.197 0.153 0.072] entropy 2.18 bits
print(top_p_filter(apply_temperature(logits, 1.0), 0.9).round(3))   # [0.455 0.276 0.167 0.102 0.   ]

rng_s = np.random.default_rng(0)
draws = rng_s.choice(5, size=10000, p=top_p_filter(apply_temperature(logits, 1.0), 0.9))
print("banana sampled", int((draws == 4).sum()), "times in 10000")   # banana sampled 0 times in 10000""",
     why="""Temperature divides the logits: `T < 1` makes gaps bigger (sharper, less random, entropy 1.38 bits at 0.5 versus 1.91 at 1),
`T > 1` makes them smaller (flatter, more diverse, 2.18 bits at 2). As `T -> 0` all mass goes to the argmax, which is
greedy decoding; APIs treat `T = 0` as greedy (no division by zero happens inside). As `T` grows the distribution
approaches uniform over the vocabulary, which produces nonsense.

Top-p with `p = 0.9`: cumulative masses are 0.445, 0.715, 0.879, 0.978, so `the, a, cat, dog` are kept (the first three
are not yet 0.9) and `banana` is cut. The point of top-p over a fixed top-k: the nucleus adapts. When the model is
confident, one or two tokens already cover 90% and the tail is cut; when it is unsure, many tokens stay. That removes
the long tail of individually unlikely tokens that, summed over thousands of tokens, would otherwise be sampled
surprisingly often and derail the text.

Typical settings: factual or code tasks `T` around 0 to 0.3; creative writing `T` 0.7 to 1.0 with `top_p` 0.9 to 0.95.
Temperature is applied first, then the filter, then sampling.""",
     complexity="O(V log V) for the sort per generated token (O(V) with partial selection); V is the vocabulary size.",
     mistakes="Keeping tokens while `cum < p` (drops the token that crosses p, so `p = 0.4` keeps nothing); "
              "forgetting to renormalize; applying temperature to probabilities instead of logits (then it is "
              "`probs ** (1/T)` renormalized, fine, but say so); assuming `T = 0` is a valid division.",
     learn=["ai-pretraining-decoding", "cheat-llm"])

# ---------------------------------------------------------------- Q3 concept: pretraining objectives and scaling
ex.q("What pretraining actually optimizes", minutes=5, kind="text",
     prompt="""Answer out loud in 60 to 90 seconds: \"What is the pretraining objective of a GPT-style model and of a
BERT-style model? Why did next-token prediction win for generative models? What does the Chinchilla result say about
model size versus data?\"""",
     hint1="Signal: LLM pretraining. Pattern: causal LM (next token) versus masked LM; loss = cross-entropy, "
           "reported as perplexity; compute-optimal scaling.",
     hint2="1. GPT: minimize `-sum log P(x_t | x_<t)` with a causal mask.\n2. BERT: mask 15% of tokens, predict "
           "them from both sides; great encoder, not a generator.\n3. Next-token: every token is a training signal, "
           "matches generation, scales smoothly.\n4. Chinchilla: for a fixed compute budget, scale parameters and "
           "tokens together, about 20 tokens per parameter.",
     solution="""**Model answer (about 85 s):**

\"A GPT-style model is trained with causal language modelling: given the tokens so far, predict the next one. The loss
is the cross-entropy `-mean log P(x_t | x_1..x_{t-1})` over trillions of tokens of text and code; the causal mask lets
one forward pass train every position at once. Perplexity is just `exp` of that loss.

A BERT-style model uses masked language modelling: hide about 15% of the tokens and predict them from both left and
right context. That gives excellent bidirectional representations for classification and retrieval, but it is not a
natural generator.

Next-token prediction won for generation because the training task is exactly the task at inference, every token is a
label so no annotation is needed, and the loss keeps falling smoothly as a power law in model size, data and compute,
the scaling laws. Doing well on it requires modelling grammar, facts and some reasoning, so useful abilities emerge.

Chinchilla, from DeepMind in 2022, showed that earlier models like GPT-3 were too big for their data. For a fixed
compute budget, which is about `6 * params * tokens` FLOPs, parameters and tokens should grow together, roughly 20
tokens per parameter: a 70B model wants about 1.4 trillion tokens. In practice teams now train smaller models far past
that ratio, because a smaller model is cheaper to serve for years.\"""",
     why="Pretraining is the base of every LLM question; the examiner checks that you know the loss, the "
         "difference to BERT, and the compute trade-off.",
     learn=["ai-pretraining-decoding", "cheat-llm"])

# ---------------------------------------------------------------- Q4 concept: decoding strategies
ex.q("Pick the decoding strategy", minutes=4, kind="text",
     prompt="""For each product, say which decoding you would use and why (about 60 to 90 seconds in total):
(a) SQL generation for an analytics assistant, (b) a creative caption generator for short videos,
(c) a machine-translation system, (d) a chatbot that keeps repeating the same sentence. Mention greedy, beam search,
temperature, top-k, top-p and repetition penalties.""",
     hint1="Signal: decoding choice depends on the task. Pattern: deterministic search (greedy, beam) for "
           "one-correct-answer tasks; sampling (temperature, top-p) for diverse open-ended text.",
     hint2="1. SQL: greedy or T near 0, plus validation (parse, run).\n2. Captions: sampling, T 0.8 to 1, top-p "
           "0.9, several candidates then rerank.\n3. Translation: beam search (4 to 5), length normalization.\n"
           "4. Repetition: often greedy/beam on open text; use sampling, repetition or frequency penalty, "
           "no-repeat n-gram.",
     solution="""**Model answer (about 85 s):**

\"(a) SQL has one correct answer and a strict syntax, so I want the most likely output: greedy decoding or temperature
near 0. I would not trust decoding alone: parse the query, run it on a sample, and retry with the error message if it
fails. Self-consistency, sampling several and voting on the result, can add accuracy at extra cost.

(b) Captions should be varied and fun. I would sample with temperature around 0.8 to 1.0 and top-p 0.9: diverse, but
the low-probability tail that produces nonsense is cut. Generate 5 candidates and rerank them with a quality and safety
model.

(c) Translation is close to one-answer and short: beam search with a beam of 4 or 5 keeps several partial hypotheses
and usually beats greedy on BLEU. It needs a length normalization, otherwise it prefers short outputs because every
extra token lowers the total log-probability.

(d) Repetition loops are typical of greedy or beam search on open-ended text: once a phrase is likely, repeating it
makes it even more likely. Fixes: switch to sampling with top-p, add a repetition or frequency penalty that lowers the
logits of tokens already generated, or a no-repeat n-gram rule. Top-k with a fixed k is simpler but does not adapt to
how confident the model is, which is why top-p is the common default.\"""",
     why="Decoding is the cheapest lever on LLM behaviour, and the examiner wants to hear that the choice "
         "depends on whether the task has one right answer.",
     learn=["ai-pretraining-decoding", "ai-llm-evaluation"])

# ---------------------------------------------------------------- Q5 review: KV cache memory
ex.q("How big is the cache?", minutes=5, review=True,
     prompt="""Write `kv_cache_bytes(n_layers, n_kv_heads, d_head, seq_len, batch, bytes_per_value)`: the memory to
store keys **and** values for every layer, KV head and position.

Then answer:
1. A Llama-2-7B-like model: 32 layers, 32 KV heads of size 128, fp16 (2 bytes). How many GiB for one 4,096-token
   sequence? For a batch of 16?
2. A Llama-3-8B-like model uses grouped-query attention with 8 KV heads (same 32 layers, size 128). How many GiB for one
   8,192-token sequence?
3. Why does this number, not the weights, often limit how many users one GPU can serve?""",
     stub="""def kv_cache_bytes(n_layers, n_kv_heads, d_head, seq_len, batch=1, bytes_per_value=2):
    # your code here
    pass""",
     tests="""check("7B, 4096 tokens", lambda: kv_cache_bytes(32, 32, 128, 4096, 1, 2), 2 * 1024 ** 3)
check("GQA 8B, 8192 tokens", lambda: kv_cache_bytes(32, 8, 128, 8192, 1, 2), 1 * 1024 ** 3)
check("scales with batch", lambda: kv_cache_bytes(2, 2, 4, 10, 3, 4), 3840)""",
     hint1="Signal: memory of cached keys and values. Pattern: KV cache size = 2 (K and V) x layers x KV heads x "
           "head size x tokens x batch x bytes.",
     hint2="1. Multiply everything, with a factor 2 for K and V.\n2. Divide by `1024**3` for GiB.\n3. Compare "
           "with the weights: 7B params x 2 bytes = 14 GB.",
     solution="""def kv_cache_bytes(n_layers, n_kv_heads, d_head, seq_len, batch=1, bytes_per_value=2):
    return 2 * n_layers * n_kv_heads * d_head * seq_len * batch * bytes_per_value

GiB = 1024 ** 3
print(kv_cache_bytes(32, 32, 128, 4096) / GiB)              # 2.0
print(kv_cache_bytes(32, 32, 128, 4096, batch=16) / GiB)    # 32.0
print(kv_cache_bytes(32, 8, 128, 8192) / GiB)               # 1.0
print("per token, 7B:", kv_cache_bytes(32, 32, 128, 1) // 1024, "KiB")   # per token, 7B: 512 KiB""",
     why="""Every generated or prompt token stores one key and one value vector per layer and KV head:
`2 * 32 * 32 * 128 * 2 bytes = 512 KiB` per token for the 7B model, so 4,096 tokens take 2 GiB and a batch of 16
takes 32 GiB, more than double the 14 GB of fp16 weights. Grouped-query attention lets 4 query heads share one KV head,
cutting the cache 4x, so the 8B model stores twice as many tokens (8,192) in half the memory (1 GiB).

This is why serving is often memory-bound: the weights are loaded once and shared by all requests, but each request
needs its own cache that grows with its context. The cache decides the maximum batch size and context length, and
therefore throughput and cost per token. Engineering answers: GQA or multi-query attention, cache quantization to
8 or 4 bits, paged attention (vLLM) to avoid fragmentation, and prefix caching for shared system prompts.""",
     complexity="O(1) arithmetic; the cache itself is O(layers * kv_heads * d_head * seq_len * batch).",
     mistakes="Forgetting the factor 2 for keys and values; using the number of query heads with GQA; mixing GB "
              "(10^9) and GiB (2^30).",
     learn=["ai-attention-transformer", "ai-safety-cost"])

ex.save()
