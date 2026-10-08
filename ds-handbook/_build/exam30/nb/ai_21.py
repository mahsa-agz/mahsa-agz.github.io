"""Day 21 AI (mock exam, hard): recommenders, NLP basics, attention, pretraining and decoding, fine-tuning
and RLHF, RAG."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam  # noqa: F401
from _ai_hard_common import start, ask, MOCK_INTRO

SETUP = r'''def _t(name, got, want):
    good = got == want
    print(("PASS " if good else "FAIL ") + name + f" -> {got!r}" + ("" if good else f"   expected {want!r}"))

# toy RAG index (made up): 6 chunks and 4 queries as 4-dimensional embeddings
chunk_emb = np.array([[0.9, 0.1, 0.0, 0.1],    # c0 refund policy
                      [0.1, 0.9, 0.1, 0.0],    # c1 shipping times
                      [0.7, 0.0, 0.6, 0.0],    # c2 refunds for digital goods
                      [0.0, 0.2, 0.9, 0.1],    # c3 gift cards
                      [0.1, 0.1, 0.1, 0.9],    # c4 account deletion
                      [0.5, 0.5, 0.0, 0.5]])   # c5 general FAQ
query_emb = np.array([[1.0, 0.0, 0.2, 0.0],    # q0 "refund for an in-app purchase?"
                      [0.0, 1.0, 0.0, 0.1],    # q1 "when will my parcel arrive?"
                      [0.2, 0.0, 1.0, 0.0],    # q2 "refund a gift card?"
                      [0.0, 0.0, 0.0, 1.0]])   # q3 "delete my account"
relevant = [{2}, {1}, {3, 0}, {4}]             # relevant chunk ids per query'''

ex = start(21, intro=MOCK_INTRO + " Suggested split: about 3 to 4 minutes per short question and 6 minutes for "
           "the mini case (Q8).", extra=SETUP)

# Q1 recommenders (text)
ask(ex, title="Two towers, but popular items everywhere", minutes=3, kind="text",
    prompt="""You train a two-tower retrieval model (user tower, item tower, dot product) with in-batch negatives:
the other items in the batch are the negatives for each user. Offline you notice that the model ranks very
popular items too low (low recall on head items) and surfaces oddly niche items. Why does this happen, and what
are two fixes?""",
    hint1="""Signal: sampled softmax with in-batch negatives. Popular items appear in many batches, so they are
sampled as negatives far more often than uniform sampling would.""",
    hint2="""Name the sampling bias, then the logQ correction, mixed negatives, and evaluation by popularity
bucket.""",
    solution="""**Why:** with in-batch negatives, an item is used as a negative in proportion to how often it
appears in the training data, that is, its popularity `Q(i)`. The softmax is computed over a popularity-weighted
sample instead of the whole catalogue, so popular items are pushed down far more often than they should be. One
can show the uncorrected score converges to roughly `true score - log Q(i)`: the more popular the item, the bigger
the penalty. Head items are under-ranked and tail items look better than they are.

**Fixes:** (1) **logQ correction:** during training subtract `log Q(i)` from each sampled item's logit, so the
sampled softmax approximates the full softmax (the correction from Google's sampling-bias-corrected two-tower
paper, used for YouTube); at serving use the raw score. (2) **Mixed negatives:** add items sampled uniformly from
the catalogue to the in-batch ones. Also useful: hard negatives (shown but skipped) and evaluating recall per
popularity bucket plus catalogue coverage, not only the overall recall. **Follow-up: "but our feed is too
popular overall".** That is a different cause (positives are dominated by popular items, and the ranker and
feedback loop amplify them): fix with exploration, diversity in re-ranking and popularity-aware evaluation.""",
    why="""This is the most common deep follow-up on two-tower models: knowing that in-batch negatives are a biased
sample and the logQ fix shows real experience.""",
    learn=["ai-recommenders", "ai-embeddings"])

# Q2 attention (python)
ask(ex, title="Causal attention in ten lines of numpy", minutes=4,
    prompt="""Write `causal_attention(Q, K, V)` for one head: `Q, K, V` have shape `(T, d)`. Compute
`softmax(Q K^T / sqrt(d))` with a causal mask (token `i` may only attend to tokens `0..i`), then multiply by `V`.
Return `(output, weights)`. Use a numerically stable softmax.""",
    stub='''def causal_attention(Q, K, V):
    # your code here
    pass''',
    tests='''g = np.random.default_rng(0)
Q, K, V = g.normal(size=(5, 8)), g.normal(size=(5, 8)), g.normal(size=(5, 8))
res = causal_attention(Q, K, V)
out, w = res if res is not None else (np.zeros((5, 8)), np.zeros((5, 5)))
_t("rows sum to 1", bool(np.allclose(w.sum(axis=1), 1)), True)
_t("no attention to the future", bool(np.allclose(np.triu(w, 1), 0)), True)
_t("first token copies V[0]", bool(np.allclose(out[0], V[0])), True)
_t("output shape", out.shape, (5, 8))''',
    hint1="""Signal: scaled dot-product attention with a decoder (causal) mask.""",
    hint2="""1. `scores = Q @ K.T / sqrt(d)`. 2. Set the upper triangle (`np.triu(..., 1)`) to `-inf`.
3. Subtract the row max, exponentiate, normalise. 4. `weights @ V`.""",
    solution='''def causal_attention(Q, K, V):
    T, d = Q.shape
    scores = Q @ K.T / np.sqrt(d)
    scores = np.where(np.triu(np.ones((T, T), bool), 1), -np.inf, scores)
    scores = scores - scores.max(axis=1, keepdims=True)      # stable softmax
    w = np.exp(scores)
    w = w / w.sum(axis=1, keepdims=True)
    return w @ V, w''',
    why="""Dividing by `sqrt(d)` keeps the dot products at unit scale so the softmax does not saturate (tiny
gradients). The mask makes training parallel: all positions are predicted at once, each seeing only its past.
Token 0 can only attend to itself, so its output is exactly `V[0]`. Cost is `O(T ** 2 * d)` time and `O(T ** 2)`
memory for the weights, the reason long contexts are expensive (and why FlashAttention avoids storing the matrix).""",
    complexity="O(T^2 d) time, O(T^2) memory.",
    mistakes="Masking after the softmax (rows no longer sum to 1); masking the lower triangle; forgetting the "
             "scale; a softmax without max subtraction (overflow).",
    learn=["ai-attention-transformer"])

# Q3 tokenization (text)
ask(ex, title="Why can't the model count the r's?", minutes=3, kind="text",
    prompt="""A user asks an LLM "How many r's are in strawberry?" and it answers 2. Explain why in terms of how the
model reads text, and give one way to make the product answer correctly.""",
    hint1="""Signal: subword tokenization (BPE). The model sees token ids, not letters.""",
    hint2="""Explain BPE merges, what the model sees for "strawberry", and fixes: tool use or character-level input.""",
    solution="""LLMs read **subword tokens** made by byte-pair encoding (BPE): frequent character sequences are merged
into one token, so "strawberry" becomes 1 to 3 tokens such as "str" + "awberry". The model never sees the
individual letters, only token ids, and must have *memorised* how each token is spelled. Counting letters is
therefore a recall task across token boundaries, and it is easy to get wrong. The same cause explains weak
arithmetic on long numbers, trouble with reversing strings, and higher cost for languages that the tokenizer
splits into many tokens.

**Fixes:** let the model call a tool (run `"strawberry".count("r")` in code), or ask it to spell the word letter
by letter first (each letter becomes its own token) and then count; in products, route such tasks to code
execution. **Why subwords at all?** A fixed vocabulary (about 32k to 200k) with no unknown words, shorter
sequences than characters (cheaper attention), and a good balance between word-level meaning and coverage.""",
    why="""It tests whether you understand tokenization concretely and can turn a model limitation into a product
fix (tools).""",
    learn=["ai-nlp-basics", "ai-pretraining-decoding"])

# Q4 decoding (python)
ask(ex, title="Temperature and nucleus sampling", minutes=4,
    prompt="""Write `nucleus(logits, temperature=1.0, top_p=0.9)`: apply the temperature
(`softmax(logits / temperature)`), sort tokens by probability, keep the smallest set whose cumulative probability
reaches `top_p`, set the rest to 0 and renormalise. Return the new probability vector (same order as `logits`).

Example: `logits = [2.0, 1.0, 0.5, -1.0]` with `top_p=0.9` keeps tokens 0, 1 and 2.""",
    stub='''def nucleus(logits, temperature=1.0, top_p=0.9):
    # your code here
    pass''',
    tests='''r = nucleus(np.array([2.0, 1.0, 0.5, -1.0]), 1.0, 0.9)
r = np.zeros(4) if r is None else r
_t("keeps 3 tokens", int((r > 0).sum()), 3)
_t("sums to 1", bool(np.isclose(r.sum(), 1)), True)
r2 = nucleus(np.array([2.0, 1.0, 0.5, -1.0]), 0.1, 0.9)
r2 = np.zeros(4) if r2 is None else r2
_t("low temperature is greedy", [round(float(v), 3) for v in r2], [1.0, 0.0, 0.0, 0.0])''',
    hint1="""Signal: decoding strategies. Temperature reshapes the distribution; top-p cuts the long tail
adaptively.""",
    hint2="""1. Stable softmax of `logits / T`. 2. `order = argsort(-p)`, `cum = cumsum(p[order])`.
3. Keep up to and including the first index where `cum >= top_p`: `k = searchsorted(cum, top_p) + 1`.""",
    solution='''def nucleus(logits, temperature=1.0, top_p=0.9):
    z = np.asarray(logits, float) / temperature
    p = np.exp(z - z.max()); p /= p.sum()
    order = np.argsort(-p)
    cum = np.cumsum(p[order])
    k = int(np.searchsorted(cum, top_p)) + 1          # smallest prefix with cumulative prob >= top_p
    keep = np.zeros_like(p, bool); keep[order[:k]] = True
    out = np.where(keep, p, 0.0)
    return out / out.sum()

print(nucleus(np.array([2.0, 1.0, 0.5, -1.0])).round(3))   # [0.629 0.231 0.14  0.   ]''',
    why="""With temperature 1 the probabilities are about 0.61, 0.22, 0.14 and 0.03; the first three reach 0.97,
so the fourth (tail) token is dropped and the rest renormalised. Low temperature sharpens toward greedy decoding
(deterministic, good for extraction and code), high temperature flattens (more diverse, more errors). Top-p adapts
the number of candidates to the model's confidence, unlike top-k which always keeps k.""",
    complexity="O(V log V) for vocabulary size V (sorting); production uses partial sorts.",
    mistakes="Applying top-p before temperature (order matters); dropping the token that crosses the threshold; "
             "forgetting to renormalise.",
    learn=["ai-pretraining-decoding"])

# Q5 fine-tuning and RLHF (text)
ask(ex, title="SFT, RLHF or DPO for a polite support bot?", minutes=3, kind="text",
    prompt="""You have a base chat model and want it to follow your company's support style and refuse
off-policy requests. You have 20,000 good example conversations and 30,000 pairs of (better, worse) answers
from raters. Which training steps would you run, in what order, and what is the main risk of the preference
step? Mention one parameter-efficient option.""",
    hint1="""Signal: post-training pipeline. SFT on demonstrations first, then preference optimisation (RLHF with a
reward model and PPO, or DPO directly on pairs).""",
    hint2="""SFT on the 20k conversations; DPO (or reward model + PPO) on the 30k pairs with a KL constraint to the
SFT model; LoRA; risks: reward hacking, verbosity, over-refusal.""",
    solution="""1. **SFT** (supervised fine-tuning) on the 20,000 good conversations: teaches format, tone and the
basic behaviour. Hold out a test set.
2. **Preference optimisation** on the 30,000 pairs: either **RLHF** (train a reward model on the pairs, then
optimise the policy with PPO against it, with a KL penalty to stay close to the SFT model) or **DPO**, which
optimises the same objective directly from the pairs without a separate reward model or RL loop (simpler, more
stable, cheaper). For a support bot, DPO is the pragmatic default.
3. **Parameter-efficient:** LoRA (low-rank adapters on attention and MLP weights) trains under 1% of the
parameters, fits on small GPUs and lets you keep one adapter per product; QLoRA adds a 4-bit base model.

**Main risk of the preference step:** the model exploits what raters (or the reward model) reward instead of
real quality: longer answers (verbosity bias), flattery, or refusing too much if refusals were preferred
in safety pairs. The KL penalty (beta in DPO) limits drift; check length, refusal rate and task success on the
held-out set, and keep a general-capability eval to catch forgetting.""",
    why="""The examiner checks the standard order (SFT then preferences), the difference between RLHF and DPO, a
practical efficiency option, and awareness of reward hacking.""",
    learn=["ai-fine-tuning-rlhf"])

# Q6 RAG retrieval (python)
ask(ex, title="Score the retriever", minutes=4,
    prompt="""In the setup, `chunk_emb` (6 chunks) and `query_emb` (4 queries) are toy embeddings and `relevant[i]`
is the set of relevant chunk ids for query `i`. Retrieve by cosine similarity and write
`retrieval_metrics(query_emb, chunk_emb, relevant, k=2)` returning `(mean recall@k, MRR)`; MRR = mean over
queries of `1 / rank of the first relevant chunk` in the full ranking.""",
    stub='''def retrieval_metrics(query_emb, chunk_emb, relevant, k=2):
    # your code here
    pass''',
    tests='''res = retrieval_metrics(query_emb, chunk_emb, relevant, k=2) or (0, 0)
_t("recall@2", round(res[0], 3), 0.875)
_t("MRR", round(res[1], 3), 0.875)''',
    hint1="""Signal: dense retrieval evaluation. Normalise vectors, dot product = cosine, rank, then recall@k and
mean reciprocal rank.""",
    hint2="""1. `qn = q / ||q||`, `cn = c / ||c||`, `S = qn @ cn.T`. 2. `ranking = argsort(-S[i])`.
3. Recall@k = `|top k & relevant| / |relevant|`; RR = 1 / (first position with a relevant id + 1).""",
    solution='''def retrieval_metrics(query_emb, chunk_emb, relevant, k=2):
    qn = query_emb / np.linalg.norm(query_emb, axis=1, keepdims=True)
    cn = chunk_emb / np.linalg.norm(chunk_emb, axis=1, keepdims=True)
    S = qn @ cn.T
    recalls, rrs = [], []
    for i, rel in enumerate(relevant):
        ranking = list(np.argsort(-S[i]))
        recalls.append(len(set(ranking[:k]) & rel) / len(rel))
        rrs.append(1 / (next(j for j, c in enumerate(ranking) if c in rel) + 1))
    return float(np.mean(recalls)), float(np.mean(rrs))

print(retrieval_metrics(query_emb, chunk_emb, relevant, k=2))   # (0.875, 0.875)''',
    why="""Recall@2 and MRR are both 0.875 here, for different reasons. The in-app purchase query (q0) ranks the
generic refund policy (c0) above the specific digital-goods chunk (c2): the relevant chunk is second, so its
reciprocal rank is 0.5 (it is still inside the top 2, so recall is 1). The gift-card refund query (q2) finds the
gift-card chunk first, but its second relevant chunk (the general refund policy) is third, so recall@2 is 0.5.
MRR rewards the position of the first hit (good for "one answer" search); recall@k checks that the generator
gets *all* the evidence it needs (multi-part questions). For RAG, recall@k at the k you pass to the LLM is the key
retriever metric, and a reranker is the usual fix when a generic chunk outranks the specific one.""",
    complexity="O(Q C d) for the similarity matrix plus sorting.",
    mistakes="Dot products on unnormalised vectors (long vectors win); recall divided by k; MRR computed on the "
             "top k only without saying so.",
    learn=["ai-rag", "ai-embeddings"])

# Q7 perplexity (python)
ask(ex, title="Read a perplexity value", minutes=3,
    prompt="""A language model assigned these probabilities to the true next token at each of 6 positions:
`[0.5, 0.25, 0.25, 0.125, 0.5, 0.25]`. Write `perplexity(p)` = `exp(mean(-ln p))`. What is the value, how do
you read it, and can you compare perplexities of two models with different tokenizers?""",
    stub='''def perplexity(p):
    # your code here
    pass''',
    tests='''_t("example", round(perplexity([0.5, 0.25, 0.25, 0.125, 0.5, 0.25]) or 0, 4), 3.5636)
_t("uniform over 10", round(perplexity([0.1] * 5) or 0, 6), 10.0)''',
    hint1="""Signal: the pretraining loss. Cross-entropy per token, exponentiated.""",
    hint2="""`np.exp(np.mean(-np.log(p)))`. Uniform guessing over n tokens gives perplexity n.""",
    solution='''def perplexity(p):
    return float(np.exp(np.mean(-np.log(np.asarray(p, float)))))

print(round(perplexity([0.5, 0.25, 0.25, 0.125, 0.5, 0.25]), 4))   # 3.5636''',
    why="""The mean cross-entropy is about 1.27 nats per token, so perplexity is about 3.56: the model is as
uncertain as if it chose uniformly among about 3.6 tokens at each step. Lower is better. **Different tokenizers:**
no direct comparison, because per-token perplexity depends on how text is split (a tokenizer with longer tokens
has fewer, harder predictions). Compare bits per byte or per character instead, or compare on downstream tasks.
Also, perplexity measures next-token prediction, not helpfulness: a chat model after RLHF often has *higher*
perplexity on web text yet is much more useful.""",
    complexity="O(n).",
    mistakes="Using log base 2 and then exp (mixing bases); averaging probabilities instead of log probabilities; "
             "comparing perplexity across tokenizers or datasets.",
    learn=["ai-pretraining-decoding"])

# Q8 mini case (text)
ask(ex, title="Mini case: a help-center assistant gives outdated answers", minutes=6, kind="text",
    prompt="""A RAG assistant answers creators' questions from the help-center documents of a short-video app.
Last week the monetisation policy changed (minimum followers went from 10k to 5k), the document was updated,
but the assistant still says 10k for many users. In 6 minutes: list the possible causes along the pipeline, how
you would confirm each one, and the fix. Then say how you would evaluate the assistant so this is caught
automatically next time.""",
    hint1="""Signal: RAG debugging. Walk the pipeline: ingestion and index freshness, chunking, retrieval ranking,
caching, generation (parametric memory overriding context), and evaluation.""",
    hint2="""Causes: index not rebuilt, old and new chunks both indexed, retriever ranks the old chunk higher,
answer cache, model ignores context. Checks: look at retrieved chunks for failing queries. Fixes plus a
freshness test set.""",
    solution="""**Causes, checks, fixes (walk the pipeline):**
1. **Ingestion and index freshness.** The re-index job did not run, or failed silently. *Check:* does the index
   contain the new text, and when was it last built? *Fix:* event-driven re-indexing on document change,
   alerts on job failures, an "index age" metric.
2. **Duplicates.** Old and new versions are both indexed (new URL, or a copy in a blog post or FAQ). *Check:*
   search the index for "10k". *Fix:* delete by document id on update, metadata with version and date, filter or
   boost by recency, retire old pages.
3. **Retrieval ranking.** The new chunk exists but ranks below an older, similar chunk (for example a "creator
   fund" FAQ that mentions 10k). *Check:* retrieved chunks and their scores for the failing queries. *Fix:*
   hybrid search, a reranker, chunking that keeps the number with its context, recency boost for policy docs.
4. **Caching.** An answer or semantic cache still serves last week's answers. *Check:* cache hit flag in the
   logs. *Fix:* invalidate the cache for affected topics when documents change; TTL.
5. **Generation.** The model's parametric memory (it learned "10k" in pretraining) overrides the context, or the
   prompt allows answering without citing. *Check:* answers where the retrieved chunk says 5k but the answer
   says 10k. *Fix:* instruct to answer only from the provided context and cite it; a groundedness check that
   compares numbers in the answer with the cited chunk.

**"Many users" but not all** points to 2, 3 or 4: some query phrasings retrieve or hit the stale content.

**Evaluation to catch it next time:** a regression suite with questions tied to specific document facts
(including numbers and dates), re-run automatically whenever a document changes, scoring retrieval recall (is the
updated chunk in the top k) and faithfulness (does the answer match the chunk). Online: sample answers on
policy topics, judge them for groundedness, and monitor the citation rate and the share of answers citing
documents older than the latest version.""",
    why="""A mock-exam case rewards a systematic walk through the pipeline with a concrete check for each hypothesis,
rather than guessing. Stale knowledge is the most common real RAG incident.""",
    learn=["ai-rag", "ai-llm-evaluation"])

ex.save()
