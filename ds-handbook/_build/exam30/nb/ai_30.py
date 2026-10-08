"""Day 30 AI (light day): short mixed final check plus the checklist for the day before the exam."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam  # noqa: F401
from _ai_hard_common import start, ask

INTRO = """**Light day.** Four short questions (about 17 minutes) to check that the key ideas are ready, then the
checklist for the day before the exam. No new material today: if a question feels shaky, reread its
handbook section instead of learning anything new."""

SETUP = r'''def _t(name, got, want):
    good = got == want
    print(("PASS " if good else "FAIL ") + name + f" -> {got!r}" + ("" if good else f"   expected {want!r}"))'''

ex = start(30, intro=INTRO, extra=SETUP, title="Day 30: AI and ML (final check)")

ask(ex, title="How many alarms are real?", minutes=4,
    prompt="""0.5% of accounts are fake. A detector has recall 90% and false positive rate 2%. Write
`precision_at(prevalence, recall, fpr)` and compute the precision. Then: what false positive rate would you need
for 50% precision at the same recall?""",
    stub='''def precision_at(prevalence, recall, fpr):
    # your code here
    pass''',
    tests='''_t("example", round(precision_at(0.005, 0.9, 0.02) or 0, 4), 0.1844)
_t("no false positives", precision_at(0.01, 0.5, 0.0), 1.0)''',
    hint1="""Signal: base rates. Precision depends on prevalence, not only on the model.""",
    hint2="""`tp = prevalence * recall`, `fp = (1 - prevalence) * fpr`, precision `= tp / (tp + fp)`. For 50%
precision, set `fp = tp` and solve for fpr.""",
    solution='''def precision_at(prevalence, recall, fpr):
    tp = prevalence * recall
    fp = (1 - prevalence) * fpr
    return tp / (tp + fp)

print(round(precision_at(0.005, 0.9, 0.02), 4))        # 0.1844
print(round(0.005 * 0.9 / (1 - 0.005), 5))             # 0.00452  (FPR needed for 50% precision)''',
    why="""Only 18.4% of alarms are real: per 1,000 accounts, 4.5 fakes are caught and 19.9 real accounts are
flagged. For 50% precision the false positive rate must drop to about 0.45%, more than 4 times lower. The
one-sentence version for the exam: "with rare positives, false positives come from the huge negative
class, so judge a detector by precision at its operating point, not by FPR or accuracy.\"""",
    complexity="O(1).",
    mistakes="Confusing FPR (share of negatives flagged) with the false discovery rate (share of flags that are wrong).",
    learn=["ai-classification-metrics"])

ask(ex, title="Three explanations, 30 seconds each", minutes=5, kind="text",
    prompt="""Say each one out loud in about 30 seconds, then compare with the model answer:

1. What attention computes and why it is divided by `sqrt(d)`.
2. RAG or fine-tuning for a support bot that must know this week's policies?
3. Two biases of LLM-as-judge and how you control each.""",
    hint1="""Signal: rapid recall of the core LLM ideas: attention, adapting knowledge, evaluation.""",
    hint2="""1. Weighted average of values, weights from query-key similarity. 2. Knowledge that changes: retrieval.
Style and format: fine-tuning. 3. Position and length (or self-preference).""",
    solution="""1. **Attention:** each token builds a query and compares it with every token's key (dot products);
a softmax turns the scores into weights, and the output is the weighted average of the value vectors. So each
token gathers information from the tokens most relevant to it. Dividing by `sqrt(d)` keeps the dot products at a
stable scale as the dimension grows; otherwise the softmax saturates and gradients vanish.

2. **RAG** for knowledge that changes weekly: update the documents, re-index, and the bot cites the current text,
with no retraining and an audit trail. **Fine-tuning** teaches behaviour (tone, format, tool use), not fresh
facts, and is slow to update. Common answer: RAG for facts, light fine-tuning (or just prompting) for style.

3. **Position bias** (prefers the first answer): judge both orders, count disagreements as ties. **Length bias**
(prefers longer answers): instruct against it, report length-controlled win rates, watch length drift. Also
self-preference: use a judge from a different model family. Always validate the judge against human labels with
kappa.""",
    why="""These three are the most frequent LLM concept questions; crisp 30-second versions show confidence.""",
    learn=["ai-attention-transformer", "ai-rag", "ai-llm-evaluation"])

ask(ex, title="Does a 70B model fit on one 80 GB GPU?", minutes=4,
    prompt="""A 70B-parameter model is quantized to int4 (0.5 bytes per parameter). It has 80 layers, 8 key-value
heads of dimension 128, and the KV cache is stored in bf16 (2 bytes). You want to serve 16 sequences of 4,096
tokens at once. Write `serving_memory_gb(params, bytes_per_param, layers, kv_heads, head_dim, kv_bytes, tokens,
batch)` returning `(weights_gb, kv_gb)` in units of 1e9 bytes, and decide whether it fits in 80 GB (leave about 10%
for activations and overhead).""",
    stub='''def serving_memory_gb(params, bytes_per_param, layers, kv_heads, head_dim, kv_bytes, tokens, batch):
    # your code here
    pass''',
    tests='''w, kv = serving_memory_gb(70e9, 0.5, 80, 8, 128, 2, 4096, 16) or (0, 0)
_t("weights", round(w, 1), 35.0)
_t("kv cache", round(kv, 1), 21.5)''',
    hint1="""Signal: serving memory = weights + KV cache (+ overhead).""",
    hint2="""Weights: `params * bytes`. KV: `2 * layers * kv_heads * head_dim * kv_bytes * tokens * batch`.""",
    solution='''def serving_memory_gb(params, bytes_per_param, layers, kv_heads, head_dim, kv_bytes, tokens, batch):
    weights = params * bytes_per_param
    kv = 2 * layers * kv_heads * head_dim * kv_bytes * tokens * batch
    return weights / 1e9, kv / 1e9

w, kv = serving_memory_gb(70e9, 0.5, 80, 8, 128, 2, 4096, 16)
print(round(w, 1), round(kv, 1), round(w + kv, 1))   # 35.0 21.5 56.5''',
    why="""Weights take 35 GB and the KV cache 21.5 GB, 56.5 GB in total: it fits in 80 GB with room for overhead
(about 72 GB usable). The KV cache scales with batch and context: 64 sequences, or 16 sequences of 16k tokens,
would need about 86 GB of KV cache alone and no longer fit. Levers: shorter contexts, KV cache quantization
(int8 halves it), paged attention to avoid waste, or a second GPU (tensor parallelism).""",
    complexity="O(1).",
    mistakes="Forgetting the factor 2 (keys and values); using all attention heads instead of the KV heads under "
             "grouped-query attention; mixing GB (1e9) and GiB (2^30).",
    learn=["ai-safety-cost"])

ask(ex, title="Your opening for any ML design question", minutes=4, kind="text",
    prompt="""Write the outline you will use tomorrow for any ML system design question (feed, moderation, search,
fraud, an LLM feature), with the time you plan for each step in a 45-minute exam and one question you will
ask the examiner at the start.""",
    hint1="""Signal: a reusable framework, so you never start from a blank page.""",
    hint2="""Clarify, metrics, data and labels, features, model, evaluation, serving, monitoring, then deep
dives and trade-offs.""",
    solution="""| Step | Minutes | What to say |
|---|---|---|
| 1. Clarify scope | 3 | users, scale (QPS, catalogue size), latency limit, what exists today |
| 2. Goal and metrics | 4 | business goal, online primary metric, guardrails, offline metric that tracks it |
| 3. Data and labels | 5 | logs, label definition, biases (exposure, position, delayed labels), splits by time |
| 4. Features | 5 | user, item, context, cross features; freshness; leakage |
| 5. Model | 8 | baseline first, then the funnel (retrieval, ranking, re-ranking) or a cascade; loss and objectives |
| 6. Evaluation | 6 | offline (sliced, calibrated), online A/B with guardrails and long-term holdout |
| 7. Serving | 5 | latency budget, feature store, caching, cost (back-of-the-envelope numbers) |
| 8. Monitoring | 4 | drift, data quality, model and business metrics, retraining, rollback |
| Deep dives | 5 | the examiner's choice: cold start, feedback loops, bias, adversaries, cost |

**Opening question:** "What is the business goal you care most about here, and are there constraints I should
know (latency, scale, what already exists)?" Then say your plan in one sentence ("I will go from metrics to
data, model, evaluation and serving, and leave time for deep dives"), and keep a visible structure while
talking.""",
    why="""A framework saves the first minutes, keeps you from forgetting evaluation or monitoring, and shows the
examiner you can drive an ambiguous discussion.""",
    learn=["ai-ml-system-design", "cheat-exam-day"])

ex.text("""---
## Checklist for the day before the exam

**Knowledge (60 to 90 minutes, no more)**
- Redo the AI questions in your mistake log that are still red; read only their solutions, no new topics.
- Say out loud once: the ML design outline (Q4), the A/B test readout (primary, guardrails, decision), the
  attention and RAG explanations (Q2), precision at low prevalence (Q1), and one cost or memory calculation (Q3).
- Review the handbook cheat sheets for ML metrics, LLMs and the exam day.

**Stories (30 minutes)**
- Two projects you can explain end to end in 2 minutes each: problem, your role, data, model, metric, result in
  numbers, what you would do differently.
- One example each of: a model that failed in production or an experiment that surprised you, a disagreement
  with a stakeholder, a trade-off you made under time pressure.

**Logistics**
- Confirm the time zone, the link or address, and the examiner names if you have them.
- Test camera, microphone, internet and the coding environment (shared editor or Colab), charger plugged in.
- Water, paper and pen for back-of-the-envelope math; a quiet room.
- Prepare three questions for the examiners (team, how models are evaluated, what success looks like in the
  first six months).

**Energy**
- Stop studying early in the evening. Light exercise, normal dinner, sleep at your usual time.
- Morning: a short warm-up only (one easy problem and the ML outline), then arrive or log in 10 minutes early.

**During the exam:** clarify first, think out loud, give numbers, name trade-offs, and when you do not know,
say how you would find out.""")

ex.save()
