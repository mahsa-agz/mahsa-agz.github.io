import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_mid_common import setup

# Day 20 AI: focus rag; review fine-tuning-rlhf, embeddings.
ex = Exam(20, "ai")
setup(ex, '''from sklearn.feature_extraction.text import TfidfVectorizer

# A MADE-UP help center for a made-up short-video app (20 short articles) and 20 user questions,
# each with the id of the article that answers it (the "gold" document).
DOCS = {
 "d01": "Refund policy. Coin purchases can be refunded within 14 days if the coins were not spent. Open Settings, Purchase history, select the order and tap Request refund.",
 "d02": "Delete your account. Go to Settings, Account, Delete account. Deletion becomes permanent after a 30-day grace period; log in during that period to cancel it.",
 "d03": "Deactivate your account. Deactivating hides your profile and videos until you log in again. Your data is kept.",
 "d04": "Reset your password. On the login screen tap Forgot password and we email you a reset link that is valid for 1 hour.",
 "d05": "Two-step verification. Turn it on in Settings, Security. At each new login you enter a code from an authenticator app or from an SMS.",
 "d06": "Video length and size. Videos can be up to 10 minutes long and 4 GB in size. Supported formats are MP4 and MOV.",
 "d07": "Upload problems. If an upload is stuck or fails, check your connection, free up storage on your phone and update the app to the latest version.",
 "d08": "Going live. To start a live stream you need at least 1,000 followers and you must be 18 or older.",
 "d09": "Creator fund. The fund pays creators who have 10,000 followers and 100,000 views in the last 30 days. Earnings are calculated monthly.",
 "d10": "Payouts. Earnings are paid by bank transfer or PayPal once your balance reaches 50 dollars. Payouts are sent on the 15th of each month.",
 "d11": "Copyright. If someone reuploads your original content without permission, file a copyright report with a link to your original. We review reports within 3 days.",
 "d12": "Report a video. Press and hold the video, tap Report and choose a reason such as harassment, spam or dangerous acts.",
 "d13": "Block a user. Blocking stops that person from viewing your videos, sending you messages or commenting on your posts.",
 "d14": "Private account. With a private account only followers you approve can see your videos. Change it in Settings, Privacy.",
 "d15": "Comment filters. Filters hide comments that contain keywords you choose, and can hide offensive comments automatically. Settings, Privacy, Comments.",
 "d16": "Download your data. Request a copy of your information in Settings, Account, Download your data. The file is ready within 2 days.",
 "d17": "Screen time. Screen time management lets you set a daily limit. After the limit the app asks for a passcode.",
 "d18": "Teen accounts. Accounts of users under 16 are private by default and cannot send direct messages.",
 "d19": "Music licensing. Songs from the commercial sound library are licensed for use in videos on the app only, not on other platforms.",
 "d20": "Ad settings. You can change ad personalization in Settings, Privacy, Ads. Turning it off shows less relevant ads, not fewer ads.",
}
QUERIES = [
 ("how do I get a refund for coins", "d01"),
 ("I forgot my password", "d04"),
 ("how long can my videos be", "d06"),
 ("delete my account permanently", "d02"),
 ("how many followers do I need to go live", "d08"),
 ("stop someone from messaging me", "d13"),
 ("my upload keeps failing", "d07"),
 ("when do I get paid", "d10"),
 ("someone stole my clip and posted it as theirs", "d11"),
 ("make my profile visible only to people I accept", "d14"),
 ("limit how much time I spend in the app", "d17"),
 ("hide rude comments", "d15"),
 ("export my information", "d16"),
 ("turn off personalized ads", "d20"),
 ("protect my login with a code", "d05"),
 ("get my money back", "d01"),
 ("can a 15 year old send messages", "d18"),
 ("can I use popular songs in my videos", "d19"),
 ("strangers should not see my posts", "d14"),
 ("someone keeps harassing me in my DMs", "d13"),
]
doc_ids, doc_texts = list(DOCS), list(DOCS.values())
print(len(DOCS), "documents,", len(QUERIES), "labelled queries")''')

ex.text("""**Data (made up for this exam):** `DOCS` = 20 help-center articles of an invented short-video app,
`QUERIES` = 20 user questions with the id of the article that answers each one. Small on purpose: you can read every
document and see exactly why retrieval succeeds or fails. `doc_ids` and `doc_texts` are the same data as lists.""")

# ---------------------------------------------------------------- Q1 TF-IDF retriever
ex.q("Find the right help article", minutes=6,
     prompt="""Write `retrieve(query, k=3)`: rank the documents by cosine similarity between TF-IDF vectors of the
query and of each document (`TfidfVectorizer(stop_words="english")` fitted on the documents) and return the ids of the
top `k` documents **with a score above 0**, best first (ties: keep document order). It may return fewer than `k` ids, or
none.

Examples: `retrieve("how do I get a refund for coins", 3)` starts with `"d01"`; `retrieve("get my money back")`
returns `[]`: after removing stop words only `money` is left, and no document contains it.

Follow-up: why is returning nothing better than returning the 3 \"least bad\" documents in a RAG system?""",
     stub="""def retrieve(query, k=3):
    # your code here
    pass""",
     tests="""check("refund question", lambda: retrieve("how do I get a refund for coins", 3)[0], "d01")
check("password question", lambda: retrieve("I forgot my password", 1), lambda r: list(r) == ["d04"])
check("no overlap returns nothing", lambda: retrieve("get my money back", 3), lambda r: list(r) == [])
check("at most k results", lambda: len(retrieve("settings privacy account videos", 2)), 2)""",
     hint1="Signal: \"find the documents that match a question\". Pattern: sparse lexical retrieval: TF-IDF vectors "
           "and cosine similarity (TfidfVectorizer rows are already L2-normalized, so a dot product is the cosine).",
     hint2="1. Fit the vectorizer once on `doc_texts`, keep the matrix `D`.\n2. `q = vec.transform([query])`.\n"
           "3. `scores = (D @ q.T).toarray().ravel()`.\n4. `order = np.argsort(-scores, kind=\"stable\")`, keep ids "
           "with `scores > 0`, first k.",
     solution="""vec = TfidfVectorizer(stop_words="english")
D = vec.fit_transform(doc_texts)                       # (20 docs, vocabulary), rows L2-normalized

def retrieve(query, k=3):
    scores = (D @ vec.transform([query]).T).toarray().ravel()
    order = np.argsort(-scores, kind="stable")
    return [doc_ids[i] for i in order if scores[i] > 0][:k]

print(retrieve("how do I get a refund for coins"))       # ['d01']
print(retrieve("stop someone from messaging me"))        # []
print(retrieve("strangers should not see my posts"))     # ['d13']""",
     why="""TF-IDF turns each text into a sparse vector of weighted words, and since sklearn L2-normalizes rows, the
dot product is the cosine. Only shared (non-stop) words give a positive score, so retrieval is purely lexical.

The two extra examples show the weakness. `messaging` is a different token from `messages`, so the blocking article
is not found at all. "strangers should not see my posts" keeps only `strangers` and
`posts` after stop words (see `vec.build_analyzer()(query)`), and `posts` appears only in the blocking article, so the
retriever returns d13 instead of the private-account article d14: a lexical match can be confident and still wrong.

Returning nothing is useful information in RAG: the application can say \"I could not find this in the help center\"
or ask a clarifying question, instead of feeding unrelated text to the LLM, which then tends to produce a fluent wrong
answer grounded in the wrong article. In production you would use a score threshold calibrated on labelled queries
rather than \"above 0\".""",
     complexity="Index: O(total tokens). Query: O(nonzeros of the matching postings) with an inverted index; here a "
                "sparse matrix product.",
     mistakes="Fitting the vectorizer on the queries too (leaks the test set into the IDF); forgetting that "
              "`transform` of a query with only unknown words gives an all-zero vector (every score 0, and argsort "
              "then returns document order as if it meant something).",
     learn=["ai-rag", "ai-nlp-basics"])

# ---------------------------------------------------------------- Q2 retrieval metrics
ex.q("Is the retriever good enough?", minutes=6,
     prompt="""Write two retrieval metrics over a labelled query set. `retriever(query, k)` returns a ranked list of ids;
`queries` is a list of `(question, gold_id)` pairs with one gold document each.

- `recall_at_k(retriever, queries, k)`: share of queries whose gold id is in the top `k`.
- `mrr(retriever, queries, k=10)`: mean reciprocal rank: `1 / rank` of the gold id (rank starts at 1), 0 if it is not in
  the top `k`.

Then evaluate your Q1 `retrieve` on `QUERIES`: recall@1, recall@3 and MRR. List the queries it misses. Why is recall@k
the key retrieval metric for RAG, more than precision?""",
     stub="""def recall_at_k(retriever, queries, k):
    pass

def mrr(retriever, queries, k=10):
    pass""",
     tests="""fake = lambda q, k: {"a": ["x", "y", "z"], "b": ["y", "x"], "c": []}[q][:k]
qs = [("a", "z"), ("b", "y"), ("c", "x")]
check("recall@1", lambda: recall_at_k(fake, qs, 1), 1 / 3)
check("recall@3", lambda: recall_at_k(fake, qs, 3), 2 / 3)
check("mrr", lambda: mrr(fake, qs), (1 / 3 + 1 + 0) / 3)
check("mrr respects k", lambda: mrr(fake, qs, k=2), 1 / 3)""",
     hint1="Signal: \"is the right document in what we retrieved\". Pattern: retrieval evaluation with a labelled "
           "query set: recall@k and MRR.",
     hint2="1. For each pair, `ranked = retriever(q, k)`.\n2. Recall: `gold in ranked`.\n3. MRR: `1 / "
           "(ranked.index(gold) + 1)` if present else 0.\n4. Average over queries.",
     solution="""def recall_at_k(retriever, queries, k):
    return float(np.mean([gold in retriever(q, k) for q, gold in queries]))

def mrr(retriever, queries, k=10):
    rr = []
    for q, gold in queries:
        ranked = list(retriever(q, k))
        rr.append(1 / (ranked.index(gold) + 1) if gold in ranked else 0.0)
    return float(np.mean(rr))

print("recall@1", recall_at_k(retrieve, QUERIES, 1), " recall@3", recall_at_k(retrieve, QUERIES, 3),
      " MRR", round(mrr(retrieve, QUERIES), 3))
# recall@1 0.7  recall@3 0.7  MRR 0.7
missed = [q for q, gold in QUERIES if gold not in retrieve(q, 3)]
print(missed)
# ['stop someone from messaging me', 'someone stole my clip and posted it as theirs',
#  'make my profile visible only to people I accept', 'get my money back',
#  'strangers should not see my posts', 'someone keeps harassing me in my DMs']""",
     why="""14 of 20 questions get the right article at rank 1, and the other 6 do not get it in the top 3 at all, so
recall@1 = recall@3 = MRR = 0.7. The misses are all vocabulary mismatch: the user says `messaging`, `stole`, `money
back`, `strangers`, `harassing`, the article says `messages`, `reuploads`, `refund`, `private`, `harassment`.

For RAG, recall@k of the retriever is an upper bound on answer quality: if the right passage is not in the k chunks
given to the LLM, the model can only answer from memory, or hallucinate. Precision matters less because the LLM can
ignore a few irrelevant chunks, although too many of them cost tokens and can distract it. So the usual setup is: high
recall at k = 20 to 100 from cheap retrieval, then a reranker to put the best 3 to 5 chunks in the prompt. Keep a
labelled query set like this one (from real user questions, with the gold document) and track recall@k on every
change to chunking, embeddings or the index.""",
     complexity="O(number of queries * retrieval cost).",
     mistakes="Counting a query as a hit when the gold id appears beyond k; averaging MRR only over found queries; "
              "building the eval set from the documents themselves (questions that copy article words make lexical "
              "search look perfect).",
     learn=["ai-rag", "ai-llm-evaluation", "ai-recommenders"])

# ---------------------------------------------------------------- Q3 hybrid retrieval
ex.q("Fix the misses without a neural model", minutes=7,
     prompt="""Many misses are word-form problems (`messaging` versus `messages`, `harassing` versus `harassment`).
Write `hybrid_retrieve(query, k=3, w=0.5)`:

1. A second index: `TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)` on the documents
   (character pieces of 3 to 5 letters inside word boundaries).
2. Score = `w * word_score + (1 - w) * char_score`, where `word_score` is your Q1 cosine.
3. Return the top `k` ids with a score above 0.

Evaluate recall@1, recall@3 and MRR with your Q2 functions. Which query still fails, and what kind of method would fix
it?""",
     stub="""def hybrid_retrieve(query, k=3, w=0.5):
    # your code here
    pass""",
     tests="""check("word form fixed", lambda: hybrid_retrieve("stop someone from messaging me", 1), lambda r: list(r) == ["d13"])
check("still finds the easy ones", lambda: hybrid_retrieve("I forgot my password", 1), lambda r: list(r) == ["d04"])
check("w = 1 equals the word retriever", lambda: hybrid_retrieve("delete my account permanently", 3, w=1.0),
      lambda r: list(r) == ["d02", "d14", "d03"])""",
     hint1="Signal: misses caused by different word forms. Pattern: hybrid retrieval: combine two scorers (here word "
           "TF-IDF and character n-gram TF-IDF) with a weighted sum.",
     hint2="1. Fit the char vectorizer on `doc_texts`.\n2. Two score vectors for the query, each a cosine in [0, 1] "
           "(so they are on comparable scales).\n3. Weighted sum, stable argsort, keep scores > 0, first k.",
     solution="""cvec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
C = cvec.fit_transform(doc_texts)

def hybrid_retrieve(query, k=3, w=0.5):
    word = (D @ vec.transform([query]).T).toarray().ravel()
    char = (C @ cvec.transform([query]).T).toarray().ravel()
    scores = w * word + (1 - w) * char
    order = np.argsort(-scores, kind="stable")
    return [doc_ids[i] for i in order if scores[i] > 0][:k]

print("recall@1", recall_at_k(hybrid_retrieve, QUERIES, 1), " recall@3", recall_at_k(hybrid_retrieve, QUERIES, 3),
      " MRR", round(mrr(hybrid_retrieve, QUERIES), 3))
# recall@1 0.8  recall@3 0.95  MRR 0.867
print([q for q, gold in QUERIES if gold not in hybrid_retrieve(q, 3)])     # ['get my money back']
print(hybrid_retrieve("get my money back"))                               # ['d10', 'd09', 'd07']""",
     why="""Character n-grams match shared pieces such as `messag`, `harass` and `someone`, so different word forms and
small typos still overlap. Recall@3 goes from 0.7 to 0.95 and MRR from 0.7 to 0.867. The cost is more noise: almost
every query now shares some 3-letter pieces with many documents, so scores are rarely 0 and the \"return nothing\"
behaviour from Q1 is lost: `get my money back` now returns three wrong articles (payouts first, through shared pieces like
`mon` from `month` and ` ba` from `bank`). You would need a calibrated score threshold.

The query that still fails, `get my money back` for the refund article, has no shared words or pieces at all: it is a
pure synonym problem. That needs semantic matching: a dense embedding retriever (a bi-encoder that maps question and
passage into the same vector space, trained on question-answer pairs), query rewriting or expansion by an LLM
(\"money back\" to \"refund\"), or a hand-made synonym list for a small domain. In practice teams run BM25 and dense
retrieval together and fuse the rankings (for example reciprocal rank fusion), because lexical search is best at exact
names, codes and rare terms, and dense search at paraphrases.

Be careful with this result: 20 queries is tiny (one query = 5 points of recall), and the char weights were not tuned
on a separate set. With real data, tune `w` on a validation query set and report on a held-out one.""",
     complexity="Same as Q1 per scorer; char n-gram indexes are several times larger than word indexes.",
     mistakes="Adding raw scores from scorers on different scales (BM25 scores are unbounded; normalize or use rank "
              "fusion); tuning `w` on the same queries you report; declaring victory on 20 queries.",
     learn=["ai-rag", "ai-embeddings", "ai-nlp-basics"])

# ---------------------------------------------------------------- Q4 concept: RAG system design
ex.q("Design the help-center assistant", minutes=6, kind="text",
     prompt="""The app wants a chat assistant that answers support questions from 5,000 help articles that change
every week. Answer out loud in 60 to 90 seconds: describe the RAG pipeline end to end, and how you would evaluate it
before and after launch. Name two typical failure modes.""",
     hint1="Signal: answer from a changing document set. Pattern: retrieval-augmented generation: index, retrieve, "
           "rerank, generate with citations; evaluate retrieval and generation separately.",
     hint2="1. Ingest: clean, chunk (by section, about 200 to 500 tokens, with overlap and titles), embed, index "
           "(hybrid BM25 + vectors), re-index on change.\n2. Query: rewrite, retrieve top 50, rerank (cross-encoder) "
           "to 5, prompt with instructions and citations, allow \"I don't know\".\n3. Eval: recall@k on labelled "
           "questions; faithfulness and answer correctness (human or LLM judge); online: resolution rate, escalations, "
           "thumbs.\n4. Failures: retrieval miss, stale index, the LLM ignores or contradicts context, prompt injection "
           "in documents.",
     solution="""**Model answer (about 90 s):**

\"Offline ingestion: I split each article into chunks by section, a few hundred tokens each with the article title
attached, so a chunk is understandable alone. Each chunk is indexed twice: BM25 for exact terms like 'PayPal' or error
codes, and a dense embedding for paraphrases. Because articles change weekly, ingestion is incremental, keyed by
article id and version, so stale chunks are deleted.

At query time: optionally rewrite the question using the chat history, retrieve about 50 chunks from both indexes,
fuse them, and rerank with a cross-encoder down to the best 5. The prompt tells the model to answer only from these
sources, cite the article ids, and say it does not know or hand off to a human if the sources do not answer.

Evaluation in layers. Retrieval: a labelled set of real user questions with gold articles, tracking recall at 5 and
MRR. Generation: correctness and faithfulness, meaning every claim is supported by a cited chunk, judged by humans on
a sample and by an LLM judge calibrated against them. After launch: an A/B test on resolution without a human agent,
escalation rate, thumbs down, and repeat contacts within 7 days.

Failure modes: first, the retriever misses the right chunk and the model answers from memory with an outdated policy;
second, the right chunk is there but the model ignores or contradicts it, or follows instructions injected into a
document. Citations, faithfulness checks and an 'I don't know' path are the defences.\"""",
     why="RAG design is the most common applied LLM exam question. The examiner wants the separation of "
         "retrieval and generation quality, and concrete metrics for each.",
     learn=["ai-rag", "ai-llm-evaluation", "ai-ml-system-design"])

# ---------------------------------------------------------------- Q5 review: RAG or fine-tuning
ex.q("RAG, fine-tuning, or both?", minutes=4, kind="text", review=True,
     prompt="""Answer out loud in about 60 seconds: for each case say RAG, fine-tuning (for example LoRA), or both, and
why. (a) The assistant must know this week's refund policy. (b) Answers must always be valid JSON in a fixed schema
and in the brand's friendly tone. (c) A small cheap model should answer as well as a big one on support questions.
(d) A legal team needs every answer to cite its source.""",
     hint1="Signal: knowledge versus behaviour. Pattern: RAG adds fresh, citable knowledge at inference; "
           "fine-tuning changes behaviour, format and style (and can distill a big model into a small one).",
     hint2="1. Fresh facts: RAG (update the index, not the weights).\n2. Format and tone: fine-tuning or "
           "constrained decoding.\n3. Small model: distillation by fine-tuning on the big model's answers, plus RAG "
           "for facts.\n4. Citations: RAG.",
     solution="""**Model answer (about 70 s):**

\"The rule I use: RAG for knowledge, fine-tuning for behaviour.

(a) This week's refund policy is fresh, changing knowledge, so RAG. Updating an index takes minutes; retraining for
every policy change is slow and the model would still mix old and new versions from its weights.

(b) A fixed JSON schema and a brand tone are behaviour. A few-shot prompt may be enough, but for reliability I would
fine-tune with LoRA on a few thousand examples, and enforce the schema with constrained or structured decoding and a
validator.

(c) That is distillation: generate high-quality answers with the big model, ideally grounded with RAG, and fine-tune
the small model on them. The small model still uses RAG for the facts, so both.

(d) Citations need the source text at answer time, so RAG, with the instruction to cite chunk ids and a check that
each cited chunk supports the claim. Fine-tuning cannot give reliable citations because the weights do not remember
where a fact came from.

Often the best system is both: a fine-tuned model that is good at reading retrieved context and following the house
format, plus a retriever that supplies current facts.\"""",
     why="Reviews fine-tuning (day 19) against today's RAG; \"RAG or fine-tune?\" is one of the most frequent LLM "
         "product questions.",
     learn=["ai-rag", "ai-fine-tuning-rlhf"])

ex.save()
