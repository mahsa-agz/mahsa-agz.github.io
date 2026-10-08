import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_mid_common import setup

# Day 17 AI: focus attention-transformer; review nlp-basics, embeddings.
ex = Exam(17, "ai")
setup(ex, '''# toy numpy only today: no data files needed
rng = np.random.default_rng(1)''')

# ---------------------------------------------------------------- Q1 scaled dot-product attention
ex.q("Every token looks at every other token", minutes=7,
     prompt="""Write `attention(Q, K, V, mask=None)` for one head, in numpy:

`weights = softmax(Q @ K.T / sqrt(d_k))` row by row, `output = weights @ V`. Shapes: `Q (n_q, d_k)`, `K (n_k, d_k)`,
`V (n_k, d_v)`. `mask` is an optional boolean array `(n_q, n_k)`: `True` = may attend, `False` = blocked (its weight
must be exactly 0). Return `(output, weights)`.

Example: `Q = K = [[1, 0], [0, 1]]`, `V = [[1, 2], [3, 4]]`. Each query matches its own key best, so row 0 of the
weights is `[0.6698, 0.3302]` and row 0 of the output is `[1.6605, 2.6605]`. With a causal mask (lower triangle),
token 0 can only see itself and its output is exactly `[1, 2]`.

Follow-ups: what are the time and memory costs in the sequence length n? Where does the causal mask come from in a
GPT-style model?""",
     stub="""def attention(Q, K, V, mask=None):
    # your code here
    pass""",
     tests="""Q = np.array([[1.0, 0.0], [0.0, 1.0]]); V = np.array([[1.0, 2.0], [3.0, 4.0]])
causal = np.tril(np.ones((2, 2), dtype=bool))
check("weights", lambda: attention(Q, Q, V)[1], [[0.66976155, 0.33023845], [0.33023845, 0.66976155]])
check("output", lambda: attention(Q, Q, V)[0], [[1.6604769, 2.6604769], [2.3395231, 3.3395231]])
check("causal mask output", lambda: attention(Q, Q, V, causal)[0], [[1.0, 2.0], [2.3395231, 3.3395231]])
check("masked weight is exactly 0", lambda: attention(Q, Q, V, causal)[1][0, 1], 0.0, tol=0)
big = rng.normal(size=(5, 64)) * 30
check("rows sum to 1 even with large scores", lambda: attention(big, big, big)[1].sum(1), np.ones(5))""",
     hint1="Signal: weights over positions that sum to 1, query/key/value. Pattern: scaled dot-product attention = "
           "a softmax over similarity scores, used to average the values.",
     hint2="1. `scores = Q @ K.T / np.sqrt(Q.shape[1])`.\n2. Mask: `np.where(mask, scores, -np.inf)`.\n"
           "3. Stable softmax per row (subtract the row max, `exp(-inf) = 0`).\n4. `out = weights @ V`.",
     solution="""def attention(Q, K, V, mask=None):
    scores = Q @ K.T / np.sqrt(Q.shape[1])
    if mask is not None:
        scores = np.where(mask, scores, -np.inf)
    scores = scores - scores.max(axis=1, keepdims=True)
    w = np.exp(scores)
    w = w / w.sum(axis=1, keepdims=True)
    return w @ V, w

out, w = attention(np.eye(2), np.eye(2), np.array([[1.0, 2.0], [3.0, 4.0]]))
print(w.round(4))        # [[0.6698 0.3302]
                         #  [0.3302 0.6698]]""",
     why="""Each query scores every key with a dot product, the softmax turns scores into weights that sum to 1, and the
output is the weighted average of the values: a token gathers information from the tokens most relevant to it, with
weights computed from the data. In the example the score of a query with its own key is `1 / sqrt(2) = 0.707`, with the
other key 0, so the weights are `exp(0.707) / (exp(0.707) + 1) = 0.67` and `0.33`.

A blocked position gets `-inf` before the softmax, so `exp(-inf) = 0` exactly. In a decoder (GPT), the causal mask is
the lower triangle: token t may only attend to positions up to t. This lets training predict every next token in
parallel without the model seeing the answer, and it is what makes the KV cache possible at generation time.

Cost: the score matrix is n by n, so time is `O(n^2 d)` and memory `O(n^2)` per head and layer. Doubling the context
quadruples this part. That is why long-context models use FlashAttention (same math, never stores the full matrix in
slow memory), sliding windows or sparse attention.""",
     complexity="O(n_q * n_k * d) time, O(n_q * n_k) memory for the weights.",
     mistakes="Dividing by `d_k` instead of `sqrt(d_k)`; softmax over the wrong axis (columns); masking after the "
              "softmax (rows no longer sum to 1); using a large negative number that is not large enough in fp16.",
     learn=["ai-attention-transformer", "cheat-llm"])

# ---------------------------------------------------------------- Q2 multi-head attention
ex.q("Several heads at once, no loops", minutes=8,
     prompt="""Write `multi_head_attention(X, Wq, Wk, Wv, Wo, n_heads, causal=False)` for one sequence
`X (n, d_model)`:

1. `Q = X @ Wq`, `K = X @ Wk`, `V = X @ Wv` (each `(n, d_model)`).
2. Split into `n_heads` heads of size `d_head = d_model // n_heads`: head h uses columns `h*d_head` to
   `(h+1)*d_head - 1`. Use `reshape` and `transpose`, not a Python loop over heads.
3. Scaled dot-product attention in every head (scale by `sqrt(d_head)`), optional causal mask.
4. Concatenate the heads back to `(n, d_model)` and multiply by `Wo`.

The tests use a fixed random example and a **causality test**: with `causal=True`, changing the last token must not
change the outputs of the earlier tokens.

Follow-up: why several small heads instead of one big head with the same total size?""",
     stub="""def multi_head_attention(X, Wq, Wk, Wv, Wo, n_heads, causal=False):
    # your code here
    pass""",
     tests="""r1 = np.random.default_rng(1)
X3 = r1.normal(size=(3, 4)); W4 = [r1.normal(size=(4, 4)) for _ in range(4)]
check("2 heads", lambda: multi_head_attention(X3, *W4, 2),
      [[-1.4492, -0.6369, 2.0256, -0.0136], [0.7467, -0.4912, -0.7632, -0.925], [0.3173, -0.435, -0.4244, -0.9769]], tol=1e-4)
check("2 heads, causal", lambda: multi_head_attention(X3, *W4, 2, causal=True),
      [[-2.8765, -0.4653, 3.1203, -0.338], [-0.3634, -0.5735, 0.5081, -0.4815], [0.3173, -0.435, -0.4244, -0.9769]], tol=1e-4)
X3b = X3.copy(); X3b[2] += 5.0
check("future token does not change the past", lambda: multi_head_attention(X3b, *W4, 2, causal=True)[:2],
      lambda out: np.allclose(out, multi_head_attention(X3, *W4, 2, causal=True)[:2]))""",
     hint1="Signal: \"heads\", reshape instead of loops. Pattern: multi-head attention = batched attention over a "
           "head axis: `(n, d) -> (h, n, d_head)`.",
     hint2="1. `q = (X @ Wq).reshape(n, h, dh).transpose(1, 0, 2)`, same for k, v.\n2. `scores = q @ "
           "k.transpose(0, 2, 1) / sqrt(dh)`, shape `(h, n, n)`.\n3. Mask with `np.tril`, softmax on the last axis.\n"
           "4. `(w @ v).transpose(1, 0, 2).reshape(n, d) @ Wo`.",
     solution="""def multi_head_attention(X, Wq, Wk, Wv, Wo, n_heads, causal=False):
    n, d = X.shape
    dh = d // n_heads
    split = lambda M: M.reshape(n, n_heads, dh).transpose(1, 0, 2)      # (h, n, dh)
    q, k, v = split(X @ Wq), split(X @ Wk), split(X @ Wv)
    scores = q @ k.transpose(0, 2, 1) / np.sqrt(dh)                     # (h, n, n)
    if causal:
        scores = np.where(np.tril(np.ones((n, n), dtype=bool)), scores, -np.inf)
    scores = scores - scores.max(axis=-1, keepdims=True)
    w = np.exp(scores)
    w = w / w.sum(axis=-1, keepdims=True)
    heads = (w @ v).transpose(1, 0, 2).reshape(n, d)                    # concatenate heads
    return heads @ Wo

r = np.random.default_rng(0)
X_demo, W_demo = r.normal(size=(6, 8)), [r.normal(size=(8, 8)) for _ in range(4)]
print(multi_head_attention(X_demo, *W_demo, n_heads=4, causal=True).shape)     # (6, 8)""",
     why="""The reshape puts the head index in front, so numpy's batched matmul runs all heads at once; this is exactly
how framework code does it (with an extra batch axis). The last row is identical with and without the causal mask
because the last token may see everything anyway; earlier rows change because they lose access to later tokens. The
causality test is the property that matters: it would catch a mask applied on the wrong axis.

Why several heads: each head has its own `Wq`, `Wk`, `Wv` slice, so it can learn its own notion of relevance (one head
tracks the previous token, another the subject of the verb, another a matching bracket), and each produces its own
softmax. One big head would average all of these into a single distribution per token. The total cost is about the same
as one head of size `d_model`, so multiple heads add flexibility for free. Variants used in modern LLMs, multi-query
and grouped-query attention, share K and V across heads to shrink the KV cache.""",
     complexity="O(n^2 * d_model + n * d_model^2) time per layer (attention plus projections); O(h * n^2) memory "
                "for the weights.",
     mistakes="Reshaping to `(h, n, dh)` directly without the transpose (mixes tokens and heads); scaling by "
              "`sqrt(d_model)` instead of `sqrt(d_head)`; softmax over the head axis; forgetting `Wo`.",
     learn=["ai-attention-transformer", "cheat-numpy"])

# ---------------------------------------------------------------- Q3 concept: sqrt(d), positions, KV cache
ex.q("Three details examiners love", minutes=5, kind="text",
     prompt="""Answer each in about 30 seconds:

1. Why divide the scores by `sqrt(d_k)`? Give the variance argument.
2. Attention is permutation invariant. How does the transformer know word order? Name two kinds of position encoding.
3. What is the KV cache during generation, and why does it make generation much faster?""",
     hint1="Signal: transformer internals. Pattern: variance of a dot product grows with dimension; positional "
           "information must be added; decoding reuses past keys and values.",
     hint2="1. With unit-variance entries, `q . k` has variance `d_k`: big scores saturate the softmax, tiny gradients.\n"
           "2. Absolute (sinusoidal or learned, added to embeddings) versus relative (RoPE rotates q and k, ALiBi "
           "adds a distance bias).\n3. Store K and V of earlier tokens; each new token computes only its own q, k, v.",
     solution="""**Model answer (about 90 s):**

1. \"If the entries of q and k are independent with mean 0 and variance 1, their dot product is a sum of `d_k` terms,
so its variance is `d_k` and its standard deviation `sqrt(d_k)`. With `d_k = 128` the scores are around plus or minus
11, the softmax becomes almost one-hot, and its gradient is nearly zero, so training stalls. Dividing by `sqrt(d_k)`
brings the variance back to 1.\"

2. \"Attention treats its input as a set: shuffle the tokens and each output is shuffled the same way. So order must be
injected. Absolute encodings add a position vector to each token embedding, either fixed sinusoids, as in the original
transformer, or learned vectors, as in BERT and GPT-2. Relative methods encode distances instead: RoPE rotates q and k
by an angle proportional to the position so their dot product depends on the offset, which Llama-style models use;
ALiBi adds a penalty proportional to the distance. Relative methods extend better to longer contexts.\"

3. \"A decoder generates one token at a time. Without a cache, each step recomputes keys and values for the whole
prefix, so generating n tokens costs `O(n^2)` projections. Since the past tokens never change under a causal mask,
we store their K and V per layer and head, and each new token computes only its own q, k, v and attends to the cache.
The cost: memory. The cache grows linearly with the sequence length and the batch size, and for long contexts it is
often bigger than the model weights, which is why grouped-query attention and cache quantization exist.\"""",
     why="These three are the most common transformer follow-ups after \"explain attention\". Each has a one-line "
         "mechanism you should be able to say quickly.",
     learn=["ai-attention-transformer", "ai-pretraining-decoding", "cheat-llm"])

# ---------------------------------------------------------------- Q4 parameter count
ex.q("Where do 124 million parameters live?", minutes=6,
     prompt="""Write two functions (all linear layers have biases, each LayerNorm has a scale and a shift vector):

- `block_params(d, d_ff)`: parameters of one transformer block = multi-head attention (`Wq, Wk, Wv, Wo`, each
  `d x d` plus bias) + feed-forward network (`d -> d_ff -> d`, with biases) + 2 LayerNorms. The number of heads does not
  matter. Why?
- `gpt_params(vocab, n_ctx, d, n_layers)`: token embeddings `vocab x d` + learned position embeddings `n_ctx x d` +
  `n_layers` blocks with `d_ff = 4 d` + one final LayerNorm. The output layer reuses the token embedding matrix
  (weight tying), so it adds nothing.

Check: GPT-2 small has `vocab = 50257`, `n_ctx = 1024`, `d = 768`, `12` layers, and should come out at exactly
124,439,808. What share of it is the embedding table? What share of each block is the feed-forward network?""",
     stub="""def block_params(d, d_ff):
    # your code here
    pass

def gpt_params(vocab, n_ctx, d, n_layers):
    # your code here
    pass""",
     tests="""check("block d=512, d_ff=2048", lambda: block_params(512, 2048), 3152384)
check("block d=768, d_ff=3072", lambda: block_params(768, 3072), 7087872)
check("GPT-2 small", lambda: gpt_params(50257, 1024, 768, 12), 124439808)
check("GPT-2 medium", lambda: gpt_params(50257, 1024, 1024, 24), 354823168)""",
     hint1="Signal: \"count the parameters\". Pattern: transformer parameter math: attention `4(d^2 + d)`, FFN "
           "`2 d d_ff + d_ff + d`, LayerNorm `2d`; roughly `12 d^2` per block.",
     hint2="1. Attention: 4 matrices `d x d` + 4 biases of size d.\n2. FFN: `d x d_ff` + `d_ff` + `d_ff x d` + `d`.\n"
           "3. Two LayerNorms: `2 * 2d`.\n4. Model: `vocab*d + n_ctx*d + n_layers*block + 2d`.",
     solution="""def block_params(d, d_ff):
    attn = 4 * (d * d + d)
    ffn = d * d_ff + d_ff + d_ff * d + d
    norms = 2 * 2 * d
    return attn + ffn + norms

def gpt_params(vocab, n_ctx, d, n_layers):
    return vocab * d + n_ctx * d + n_layers * block_params(d, 4 * d) + 2 * d

total = gpt_params(50257, 1024, 768, 12)
print(f"{total:,}")                                                   # 124,439,808
print("token embedding share:", round(50257 * 768 / total, 3))         # 0.31
d = 768
print("FFN share of a block:", round((2 * d * 4 * d + 5 * d) / block_params(d, 4 * d), 3))   # 0.666""",
     why="""Attention has four `d x d` projections whatever the number of heads, because the heads just split those
matrices into slices: more heads means smaller `d_head`, not more parameters. With `d_ff = 4d`, the FFN has `8 d^2` and
attention `4 d^2`, so a block is about `12 d^2` parameters and two thirds of it is the feed-forward network (0.666).
That is the basis of the rule of thumb `params ~ 12 * n_layers * d^2` for the non-embedding part.

In GPT-2 small the token embedding table is 31% of all parameters, a big share for a small model; in a 70B model it is
only a few percent or less. Weight tying saves another `vocab x d` matrix. Knowing this lets you sanity-check claims (\"a 7B model
with d = 4096 has about 32 layers\": `12 * 32 * 4096^2 = 6.4B` plus embeddings) and estimate memory and FLOPs: about
`2 * params` FLOPs per token for a forward pass.""",
     complexity="O(1) arithmetic.",
     mistakes="Counting heads as multiplying parameters; forgetting biases or LayerNorm; adding the output layer "
              "when weights are tied; using `d_ff = 4d` in the test call with a different `d_ff`.",
     learn=["ai-attention-transformer", "ai-pretraining-decoding"])

# ---------------------------------------------------------------- Q5 review: from text to the first layer
ex.q("What actually enters the first layer", minutes=4, kind="text", review=True,
     prompt="""Answer out loud in about 60 seconds: \"Walk me from the raw string 'unbelievable refunds!' to the
matrix that enters the first transformer layer. How is that different from the TF-IDF vector you built on day 16, and
from a word2vec vector?\"""",
     hint1="Signal: the input pipeline of a transformer. Pattern: subword tokenization, then embedding lookup plus "
           "position; contrast sparse counts and static vectors with contextual ones.",
     hint2="1. BPE splits into subword ids (`un`, `believ`, `able`, ` ref`, `unds`, `!`, roughly).\n2. Each id "
           "selects a row of the embedding matrix (`vocab x d`).\n3. Add (or later rotate with) position "
           "information: matrix `n_tokens x d`.\n4. TF-IDF: one sparse vector per document, no order. word2vec: one "
           "fixed vector per word type. Transformer: the layers make each token's vector depend on its context.",
     solution="""**Model answer (about 70 s):**

\"First the tokenizer, usually byte-level BPE, splits the string into subword pieces from a fixed vocabulary, for
example 'un', 'believ', 'able', ' ref', 'unds', '!', and maps each to an integer id. Rare words become several pieces,
so nothing is out of vocabulary.

Each id selects one row of the learned token embedding matrix, size `vocab x d`; this lookup is the same as
multiplying a one-hot vector by the matrix. Position information is added, either a learned position vector per index
or, in RoPE models, a rotation applied later inside attention. The result is a matrix of shape `n_tokens x d`, one
dense row per token, and that enters layer 1.

Compared with day 16's TF-IDF: TF-IDF gives one sparse vector per whole message, as long as the vocabulary, with no
order and no notion that 'refund' and 'money back' are related. word2vec gives each word type one dense vector,
learned from co-occurrence, so synonyms are close, but the vector is the same in every context. In a transformer the
input embedding is also static, but after each attention layer every token's vector is mixed with its context, so
'bank' near 'river' and 'bank' near 'loan' end up with different representations.\"""",
     why="Reviews tokenization (day 16) and embeddings (day 13) and connects them to the transformer input.",
     learn=["ai-nlp-basics", "ai-embeddings", "ai-attention-transformer"])

ex.save()
