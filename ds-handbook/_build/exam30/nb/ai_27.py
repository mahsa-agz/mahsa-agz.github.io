"""Day 27 AI (hard): safety, cost and latency (focus); deployment monitoring and LLM evaluation (review)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam  # noqa: F401
from _ai_hard_common import start, ask

SETUP = r'''from scipy import stats
from collections import OrderedDict

def _t(name, got, want):
    good = got == want
    print(("PASS " if good else "FAIL ") + name + f" -> {got!r}" + ("" if good else f"   expected {want!r}"))

# Illustrative prices in USD per 1M tokens (made up, in the range of real price lists)
PRICES = {"large": {"in": 3.00, "out": 15.00}, "small": {"in": 0.25, "out": 1.25}}

# SIMULATED request stream for a support bot: 200,000 requests over 50,000 distinct questions (Zipf-like)
_g = np.random.default_rng(27)
_ranks = np.arange(1, 50_001)
_pz = 1 / _ranks ** 1.1
requests = _g.choice(50_000, size=200_000, p=_pz / _pz.sum())

# SIMULATED guardrail scores (higher = more likely harmful) for a red-team set and normal traffic
harm_scores = _g.beta(6, 2, 1_000)          # 1,000 harmful prompts from red-teaming
benign_scores = _g.beta(1.2, 8, 20_000)     # 20,000 normal user prompts
print("requests", requests.shape, " distinct", len(np.unique(requests)))'''

ex = start(27, extra=SETUP, data_note="""All numbers today are **made up or simulated** (prices, traffic, guardrail
scores): cost and safety questions in exams are back-of-the-envelope by nature. Prices in `PRICES` are
illustrative USD per million tokens; always check the current price list of your provider.""")

# ------------------------------------------------------------------ Q1 cost math
ask(ex, title="Cut the LLM bill without hurting users", minutes=7,
    prompt="""A support assistant gets 2M requests a day. Each request has a 1,500-token system prompt (the same
for everyone), 500 tokens of user context, and 300 output tokens. Prices are in `PRICES`.

Write `cost_per_request(model, cached_hit_rate=0.0)`: the system prompt can be cached; on a cache hit those
1,500 tokens are billed at 10% of the input price, on a miss at the full price. Then compute the daily cost of:

1. large model, no caching; 2. large model, 90% cache hits; 3. a router sends 70% of requests to the small model
   (both with 90% cache hits, the router itself is free).

Latency: time to first token (TTFT) plus output tokens times time per output token (TPOT). Large: TTFT 0.6 s,
TPOT 30 ms. Small: TTFT 0.2 s, TPOT 10 ms. Compare the full-answer latency. What is now the biggest cost driver?""",
    stub='''def cost_per_request(model, cached_hit_rate=0.0):
    # your code here
    pass''',
    tests='''_t("large, no cache", round(cost_per_request("large") or 0, 6), 0.0105)
_t("large, 90% hits", round(cost_per_request("large", 0.9) or 0, 6), 0.006855)
_t("small, 90% hits", round(cost_per_request("small", 0.9) or 0, 8), 0.00057125)''',
    hint1="""Signal: unit economics of an LLM feature. Cost = tokens times price, split into input, cached input
and output. Then the classic levers: caching, routing (model cascade), shorter outputs.""",
    hint2="""1. Effective system-prompt tokens = `1500 * (hit * 0.1 + (1 - hit))`. 2. Input cost = (that + 500) *
price_in / 1e6; output = 300 * price_out / 1e6. 3. Router: weighted average. 4. Latency = TTFT + 300 * TPOT.""",
    solution='''def cost_per_request(model, cached_hit_rate=0.0):
    p = PRICES[model]
    sys_tokens = 1500 * (cached_hit_rate * 0.1 + (1 - cached_hit_rate))
    return (sys_tokens + 500) * p["in"] / 1e6 + 300 * p["out"] / 1e6

N = 2_000_000
a = cost_per_request("large") * N
b = cost_per_request("large", 0.9) * N
c = (0.3 * cost_per_request("large", 0.9) + 0.7 * cost_per_request("small", 0.9)) * N
print(f"daily cost: large {a:,.0f}  + cache {b:,.0f}  + router {c:,.0f} USD  (monthly {30 * c:,.0f})")
out_share = 300 * PRICES["large"]["out"] / 1e6 / cost_per_request("large", 0.9)
print(f"share of the large model's cost that is output tokens (with cache): {out_share:.0%}")
print(f"latency: large {0.6 + 300 * 0.030:.1f} s, small {0.2 + 300 * 0.010:.1f} s")
# daily cost: large 21,000  + cache 13,710  + router 4,913 USD  (monthly 147,382)
# share of the large model's cost that is output tokens (with cache): 66%
# latency: large 9.6 s, small 3.2 s''',
    why="""The large model with no caching costs 21,000 USD a day (0.0105 per request). Caching the shared system prompt
cuts it to 13,710 (input cost falls by about 60%), and routing 70% of traffic to the small model brings it to
4,913 USD a day, about 147k a month: 77% less than the start. The small model also answers in 3.2 s instead of
9.6 s. After caching, **output tokens are 66% of the large model's cost**, so the next lever is shorter answers
(a concise style in the prompt, `max_tokens`, structured output), which also cuts latency, since output tokens
are generated one by one.

**Trade-offs to say out loud.** A router only saves money if the small model is good enough on the traffic it
gets: measure quality on routed traffic with the judge (by intent), and add an escalation path (the small model
or a verifier can hand off to the large one). Caching needs the shared prefix first and identical; put dynamic
content (user data, date) after it. Latency: users feel TTFT, so stream the answer; the full-answer time matters
for tool-using flows. **Follow-up: "batch API?"** Offline jobs (nightly summaries, labelling) can use batch
pricing, often about half price, with hours of delay.""",
    complexity="O(1).",
    mistakes="Pricing input and output tokens the same; forgetting that caching only helps the shared prefix (it "
             "must be byte-identical and at the start of the prompt); claiming router savings without measuring "
             "quality on the routed traffic.",
    learn=["ai-safety-cost"])

# ------------------------------------------------------------------ Q2 quantization and memory
ask(ex, title="Will the model fit, and what does int8 cost in accuracy?", minutes=7,
    prompt="""Part A (memory). An 8B-parameter decoder: 32 layers, 8 key-value heads (grouped-query attention),
head dimension 128. Compute the weight memory in fp32, bf16, int8 and int4, and the KV cache in bf16 per token,
per 8,192-token sequence and for a batch of 32 such sequences: `KV bytes per token = 2 (K and V) * layers *
kv_heads * head_dim * bytes`. How much would the KV cache be with 32 KV heads (no grouping)?

Part B (quantization). Write `quantize_int8(W, axis=None)`: symmetric int8, `scale = max|W| / 127` per tensor
(`axis=None`) or per output row (`axis=1`), `Wq = round(W / scale)` clipped to [-127, 127]; return the dequantized
`Wq * scale`. On the weight matrix below (one row has much larger weights, as in real LLMs), compare the relative
error `||W - W_hat|| / ||W||` and the error on the layer output `W @ x` for both options.

```python
g = np.random.default_rng(0)
W = g.normal(0, 0.02, (256, 512)); W[7] *= 50          # one outlier row
x = g.normal(0, 1, 512)
```""",
    stub='''def quantize_int8(W, axis=None):
    # your code here
    pass''',
    tests='''g = np.random.default_rng(0)
W = g.normal(0, 0.02, (256, 512)); W[7] *= 50
Wt, Wc = quantize_int8(W), quantize_int8(W, axis=1)
ok = Wt is not None and Wc is not None
_t("per-row error is smaller", ok and np.linalg.norm(W - Wc) < np.linalg.norm(W - Wt), True)
_t("error at most half a step", ok and bool(np.all(np.abs(W - Wc) <= np.abs(W).max(axis=1, keepdims=True) / 127 / 2 + 1e-12)), True)''',
    hint1="""Signal: deployment memory budget. Weights = params times bytes; the KV cache grows with layers, KV
heads, head size, sequence length and batch. Quantization error depends on the scale, and one outlier ruins a
shared scale.""",
    hint2="""A: 8e9 * (4, 2, 1, 0.5) bytes. KV: `2 * 32 * 8 * 128 * 2` bytes per token. B: `scale = np.abs(W).max(axis=axis,
keepdims=True) / 127` (for `axis=None` use the global max), `np.clip(np.round(W / scale), -127, 127) * scale`.""",
    solution='''# Part A
P = 8e9
for name, b in [("fp32", 4), ("bf16", 2), ("int8", 1), ("int4", 0.5)]:
    print(f"weights {name}: {P * b / 1e9:.0f} GB")
kv_tok = 2 * 32 * 8 * 128 * 2
print(f"KV per token {kv_tok / 1024:.0f} KiB, per 8k sequence {kv_tok * 8192 / 2**30:.2f} GiB, "
      f"batch 32: {kv_tok * 8192 * 32 / 2**30:.0f} GiB, without GQA: {4 * kv_tok * 8192 * 32 / 2**30:.0f} GiB")

# Part B
def quantize_int8(W, axis=None):
    if axis is None:
        scale = np.abs(W).max() / 127
    else:
        scale = np.abs(W).max(axis=axis, keepdims=True) / 127
    return np.clip(np.round(W / scale), -127, 127) * scale

g = np.random.default_rng(0)
W = g.normal(0, 0.02, (256, 512)); W[7] *= 50
x = g.normal(0, 1, 512)
for name, Wh in [("per-tensor", quantize_int8(W)), ("per-row", quantize_int8(W, axis=1))]:
    rel_w = np.linalg.norm(W - Wh) / np.linalg.norm(W)
    y, yh = W @ x, Wh @ x
    rel_y_normal = np.linalg.norm(np.delete(y - yh, 7)) / np.linalg.norm(np.delete(y, 7))
    print(f"{name:10s} weight error {rel_w:.4f}  output error on the 255 normal rows {rel_y_normal:.4f}")
# weights fp32: 32 GB / bf16: 16 GB / int8: 8 GB / int4: 4 GB
# KV per token 128 KiB, per 8k sequence 1.00 GiB, batch 32: 32 GiB, without GQA: 128 GiB
# per-tensor weight error 0.1147  output error on the 255 normal rows 0.4107
# per-row    weight error 0.0075  output error on the 255 normal rows 0.0083''',
    why="""**Memory.** Weights: 32 GB in fp32, 16 GB in bf16, 8 GB in int8, 4 GB in int4 (plus some overhead for
scales). The KV cache is 128 KiB per token, 1 GiB per 8k-token sequence and 32 GiB for a batch of 32: as big as
two copies of the bf16 weights. Without grouped-query attention (32 KV heads instead of 8) it would be 128 GiB.
That is why serving systems use GQA, paged KV caches, KV cache quantization, and limit context length per request:
the KV cache, not the weights, often sets the maximum batch size and so the cost per token.

**Quantization.** With one scale for the whole matrix, the outlier row sets the scale 50 times too large for the
other rows, so their weights are rounded to only a few levels: the output error on normal rows is 41%. One scale
per row drops it to 0.8%. Real LLMs have exactly this problem (a few outlier features and channels with huge
values), which is why practical methods use per-channel or per-group scales (for example groups of 128 weights),
keep outliers in higher precision, or rescale activations into the weights before quantizing.

**Exam trade-off:** int8 weights halve memory and speed up memory-bound decoding with little quality loss;
int4 halves again but loses more quality, especially on reasoning and long-context tasks. Always re-run the eval
suite after quantizing, sliced by task type.""",
    complexity="O(size of W).",
    mistakes="Forgetting the KV cache (it often limits batch size more than the weights do); using one scale per "
             "tensor when there are outliers; reporting only the average error while the outlier-heavy layers "
             "dominate the damage; quantizing and never re-running the eval suite.",
    learn=["ai-safety-cost", "ai-attention-transformer"])

# ------------------------------------------------------------------ Q3 caching trade-offs
ask(ex, title="How much does an answer cache save?", minutes=7,
    prompt="""`requests` holds 200,000 question ids (a skewed stream: a few questions are very common).
An exact-match cache returns a stored answer in 20 ms; a miss calls the LLM (1,200 ms, 0.004 USD).

1. Write `lru_hit_rate(stream, capacity)`: simulate a least-recently-used cache, return the hit rate.
2. Report hit rate, mean latency and daily cost (per 200,000 requests) for capacities 100, 1,000 and 10,000.
3. A teammate proposes a *semantic* cache (return the stored answer if the new question's embedding has cosine
   similarity above 0.9 with a cached one). What can go wrong, and how do you set the threshold?""",
    stub='''def lru_hit_rate(stream, capacity):
    # your code here
    pass''',
    tests='''_t("tiny stream", lru_hit_rate([1, 2, 1, 3, 2, 1], 2), 1 / 6)
_t("capacity 3", lru_hit_rate([1, 2, 1, 3, 2, 1], 3), 0.5)
_t("all distinct", lru_hit_rate(list(range(10)), 5), 0.0)''',
    hint1="""Signal: a cache with limited size and a skewed (Zipf) workload. LRU with an ordered dict: move to end on
a hit, evict the oldest when full. Then expected latency and cost are a mixture of hit and miss.""",
    hint2="""1. `OrderedDict`; on hit `move_to_end(k)`; on miss insert and `popitem(last=False)` if over capacity.
2. Mean latency = `h * 20 + (1 - h) * 1200`; cost = `(1 - h) * n * 0.004`.""",
    solution='''def lru_hit_rate(stream, capacity):
    cache, hits = OrderedDict(), 0
    for k in stream:
        if k in cache:
            hits += 1
            cache.move_to_end(k)
        else:
            cache[k] = True
            if len(cache) > capacity:
                cache.popitem(last=False)
    return hits / len(stream)

stream = requests.tolist()
print(f"no cache: latency 1200 ms, cost {len(stream) * 0.004:,.0f} USD")
for cap in (100, 1_000, 10_000):
    h = lru_hit_rate(stream, cap)
    print(f"capacity {cap:>6,}: hit rate {h:.3f}, mean latency {h * 20 + (1 - h) * 1200:.0f} ms, "
          f"cost {(1 - h) * len(stream) * 0.004:,.0f} USD")
# no cache: latency 1200 ms, cost 800 USD
# capacity    100: hit rate 0.467, mean latency 649 ms, cost 426 USD
# capacity  1,000: hit rate 0.691, mean latency 384 ms, cost 247 USD
# capacity 10,000: hit rate 0.865, mean latency 180 ms, cost 108 USD''',
    why="""Because a few questions dominate, even a 100-entry cache answers 46.7% of requests; 1,000 entries give 69.1%,
and 10,000 give 86.5%. Mean latency falls from 1,200 ms to 180 ms and the cost from 800 to 108 USD per 200,000
requests. Returns diminish: going from 1,000 to 10,000 entries (10x the memory) adds 17 points of hit rate. But
the p95 latency does not improve until the hit rate passes 95%, because the slow 5% are still misses.

**Semantic cache risks:** (1) wrong answers: "How do I cancel my order?" and "How do I cancel my subscription?"
can be 0.9 similar but need different answers; (2) personalised answers (account data) must never be shared
between users, a privacy bug; (3) stale answers after a policy or product change; (4) the cache can spread one
bad answer to thousands of users. **Setting the threshold:** label a sample of (new question, cached question)
pairs as "same answer is correct" or not, and plot the false-hit rate against the hit rate; choose the threshold
by the cost of a wrong answer, often accepting a much lower hit rate. Add expiry (TTL), invalidation on content
updates, and cache only non-personal intents.""",
    complexity="O(n) for n requests, O(capacity) memory.",
    mistakes="Caching personalised or time-sensitive answers; no expiry (answers go stale when the policy or the "
             "product changes); reporting the mean latency only (users feel the p95, which is still a miss); "
             "a semantic threshold tuned on a handful of examples.",
    learn=["ai-safety-cost", "ai-embeddings"])

# ------------------------------------------------------------------ Q4 safety numbers
ask(ex, title="Prove the guardrail is safe enough", minutes=7,
    prompt="""Two safety questions an examiner may ask with numbers.

1. Red-teaming found **0** harmful completions in 3,000 attack prompts. What can you claim? Compute the exact
   one-sided 95% upper bound for the failure rate (`1 - 0.05 ** (1 / n)`) and compare with the "rule of three"
   (`3 / n`). How many attack prompts are needed to claim a rate below 1 in 10,000?
2. An input guardrail scores each prompt (`harm_scores` for 1,000 red-team prompts, `benign_scores` for 20,000
   normal prompts, both simulated). For thresholds 0.3 to 0.7 (step 0.1), print the attack pass rate (harmful
   prompts with score below the threshold) and the over-refusal rate (normal prompts at or above it). Product
   accepts at most 1% over-refusal: which threshold, and what attack pass rate remains?""",
    stub='''# your code here''',
    hint1="""Signal: zero observed events still need a confidence bound (rule of three); a guardrail is a binary
classifier with two costs: attacks that pass (false negatives) and over-refusals (false positives).""",
    hint2="""1. With 0 events the exact bound solves `(1 - p) ** n = 0.05`. For the needed n: `n >= log(0.05) /
log(1 - 1e-4)`. 2. Loop over thresholds, `np.mean(harm_scores < t)` and `np.mean(benign_scores >= t)`.""",
    solution='''import math
n = 3000
print(f"exact upper bound {1 - 0.05 ** (1 / n):.6f}, rule of three {3 / n:.6f}")
print("prompts needed for < 1e-4:", math.ceil(math.log(0.05) / math.log(1 - 1e-4)))
for t in np.arange(0.3, 0.71, 0.1):
    print(f"threshold {t:.1f}: attack pass rate {np.mean(harm_scores < t):.3f}, "
          f"over-refusal {np.mean(benign_scores >= t):.4f}")
# exact upper bound 0.000998, rule of three 0.001000
# prompts needed for < 1e-4: 29956
# threshold 0.3: attack pass rate 0.004, over-refusal 0.0814
# threshold 0.4: attack pass rate 0.025, over-refusal 0.0232
# threshold 0.5: attack pass rate 0.062, over-refusal 0.0054
# threshold 0.6: attack pass rate 0.174, over-refusal 0.0006
# threshold 0.7: attack pass rate 0.348, over-refusal 0.0001''',
    why="""**1.** Zero failures in 3,000 prompts only shows the failure rate is below about 0.1% (exact bound 0.000998;
the rule of three gives the same 0.001). To claim below 1 in 10,000 you need about 30,000 attack prompts with no
failure (29,956). And the claim only holds for attacks like those in the set; new jailbreak styles are not
covered, so keep red-teaming and monitor production.

**2.** Raising the threshold lowers over-refusal but lets more attacks through. At 0.4, over-refusal is 2.3%
(too high); at **0.5** it is 0.54% (within the 1% budget) and 6.2% of red-team attacks pass the input guardrail.
At 0.6, over-refusal is tiny but 17.4% of attacks pass. So choose 0.5, and do not rely on one layer: add an output
classifier, safety training of the model, rate limits and human review for repeat offenders (defence in depth).
The total risk is the product of the layers' miss rates only if they fail independently, which they usually do
not, so test the full stack end to end.

**Follow-up: "how do you measure over-refusal?"** A set of benign prompts that look risky (medical, security
education, fiction) plus a random sample of real traffic, both judged by humans or a validated judge.""",
    complexity="O(n) per threshold.",
    mistakes="Saying \"0 failures means it is safe\"; testing only on attacks the team already knows (the bound "
             "only covers that distribution); tuning the guardrail only for attacks and discovering the "
             "over-refusal rate after launch.",
    learn=["ai-safety-cost", "ai-llm-evaluation"])

# ------------------------------------------------------------------ Q5 review: monitor an LLM feature (text)
ask(ex, title="Monitor an LLM feature after launch", minutes=5, kind="text", review=True,
    prompt="""Your LLM support assistant is live. The provider can silently update the model, users change what
they ask, and your team edits the prompt every week. Design the monitoring: what you log, which metrics you
compute daily, how the LLM judge is kept honest, and what triggers a rollback. About 90 seconds.""",
    hint1="""Signal: monitoring for a system without ground-truth labels and with three sources of change (model,
prompt, traffic). Combine offline regression tests with online sampled evaluation and drift on inputs.""",
    hint2="""1. Log prompt version, model version, inputs, outputs, tool calls, tokens, latency. 2. Daily: judge
scores on a sample, user signals, cost, latency, safety flags. 3. Pin versions; regression suite before every
change. 4. Judge audits with human labels (kappa).""",
    solution="""**Log every request** with prompt version, model id and version, retrieved documents, output,
tool calls, tokens in and out, latency (TTFT and total), guardrail decisions and user feedback. Pin the model
version when the provider allows it.

**Before any change (offline regression):** a fixed suite of a few hundred real, anonymised conversations plus
known hard and adversarial cases. Every prompt edit or model update must pass it: LLM-judge pass rate, safety
red-team set, format checks, cost and latency. No silent changes.

**Daily online metrics:**
- Quality: judge score on a random sample (for example 1,000 conversations a day), sliced by intent and
  language; resolution rate (no human handoff), thumbs down rate, re-ask rate.
- Safety: guardrail block rate, policy-violation rate from sampled audits, prompt-injection detections.
- Cost and latency: tokens per request, cache hit rate, cost per resolved conversation, p95 latency.
- Drift: topic mix of incoming questions (embedding clusters, PSI of the cluster shares), new clusters with low
  judge scores are the to-do list for the next prompt or document update.

**Keep the judge honest:** each week humans label a small stratified sample (more from low judge scores);
compute kappa and the judge's fail recall; if they drop, fix the judge before trusting its trend. Use both answer
orders for pairwise judgments and watch length drift (day 23).

**Rollback triggers:** a drop in judge pass rate or resolution rate beyond its normal daily noise for two days,
any confirmed severe safety incident, cost per request up more than an agreed limit, or p95 latency above the
SLO. The previous prompt and model version stay deployable with one switch.""",
    why="""This combines day 23 (judge validation, biases), day 26 (drift, rollout and rollback) and today's cost
and safety metrics into one plan. The key insight: LLM systems change from three sides (model, prompt, traffic),
so you need version pinning, a regression suite and sampled online evaluation together.""",
    learn=["ai-deployment-monitoring", "ai-llm-evaluation"])

ex.save()
