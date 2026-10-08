import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_mid_common import setup, SMS

# Day 16 AI: focus nlp-basics; review recommenders.
ex = Exam(16, "ai")
setup(ex, SMS, '''import re
from sklearn.model_selection import train_test_split
tr, te = train_test_split(sms, test_size=0.25, random_state=42, stratify=sms["y"])
print("train", tr.shape, "test", te.shape)''', data=True)

ex.text("""**Data:** UCI SMS Spam Collection: 5,572 real text messages labelled `ham` or `spam` (13.4% spam).
`sms` has `label`, `text` and `y` (1 = spam). `tr` and `te` are a stratified 75/25 split (`random_state=42`).""")

# ---------------------------------------------------------------- Q1 tokenizer and bag of words
ex.q("From messages to numbers", minutes=5,
     prompt="""Write two functions:

- `tokenize(text)`: lowercase; tokens are runs of letters and digits, and a word may keep one inner apostrophe part
  (`"I'm"` gives `"i'm"`); any token made of **5 or more digits** becomes the single token `"<num>"` (phone numbers and
  short codes are typical spam, but each exact number is rare).
- `bag_of_words(docs)`: returns `(vocab, counts)` where `vocab` is the sorted list of all tokens and `counts` an
  integer numpy array of shape `(len(docs), len(vocab))`.

Examples: `tokenize("Call 08452810075 NOW for FREE!!")` gives `['call', '<num>', 'now', 'for', 'free']`.
`bag_of_words(["free free call", "call me"])` gives `(['call', 'free', 'me'], [[1, 2, 0], [1, 0, 1]])`.

Follow-up: what does an LLM tokenizer (BPE) do differently, and why?""",
     stub="""def tokenize(text):
    # your code here
    pass

def bag_of_words(docs):
    # your code here
    pass""",
     tests="""check("phone number", lambda: tokenize("Call 08452810075 NOW for FREE!!"), lambda t: t == ['call', '<num>', 'now', 'for', 'free'])
check("short numbers stay", lambda: tokenize("I'm 2 tired, see u at 1230"), lambda t: t == ["i'm", '2', 'tired', 'see', 'u', 'at', '1230'])
check("punctuation only", lambda: tokenize("... !!"), lambda t: t == [])
check("vocab", lambda: bag_of_words(["free free call", "call me"])[0], lambda v: list(v) == ['call', 'free', 'me'])
check("counts", lambda: bag_of_words(["free free call", "call me"])[1], [[1, 2, 0], [1, 0, 1]])""",
     hint1="Signal: turn raw text into features. Pattern: tokenization (regex), normalization (lowercase, number "
           "token), then a document-term count matrix (bag of words).",
     hint2="1. `re.findall(r\"[a-z0-9]+(?:'[a-z]+)?\", text.lower())`.\n2. Replace tokens where `t.isdigit() and "
           "len(t) >= 5` with `\"<num>\"`.\n3. Vocab = `sorted(set(all tokens))`, index map `{word: j}`.\n"
           "4. Fill a zeros array with `+= 1` per token.",
     solution="""def tokenize(text):
    toks = re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower())
    return ["<num>" if t.isdigit() and len(t) >= 5 else t for t in toks]

def bag_of_words(docs):
    tokenized = [tokenize(d) for d in docs]
    vocab = sorted({t for toks in tokenized for t in toks})
    col = {w: j for j, w in enumerate(vocab)}
    counts = np.zeros((len(docs), len(vocab)), dtype=int)
    for i, toks in enumerate(tokenized):
        for t in toks:
            counts[i, col[t]] += 1
    return vocab, counts

vocab, counts = bag_of_words(tr["text"])
print("vocab size", len(vocab), " share of '<num>' in spam vs ham:",
      round(tr.loc[tr.y == 1, "text"].map(lambda s: "<num>" in tokenize(s)).mean(), 3),
      round(tr.loc[tr.y == 0, "text"].map(lambda s: "<num>" in tokenize(s)).mean(), 3))
# vocab size 7232  share of '<num>' in spam vs ham: 0.755 0.001""",
     why="""Tokenization decides what the model can see. Lowercasing merges `FREE` and `free`; the `<num>` token turns
thousands of unique phone numbers (each seen once, useless alone) into one very strong feature: 76% of spam messages in
train contain a 5+ digit number, against 0.1% of ham. This is feature engineering inside the tokenizer.

LLM tokenizers use subwords (BPE, WordPiece, SentencePiece): start from bytes or characters and repeatedly merge the
most frequent adjacent pair until the vocabulary has, say, 50k to 200k entries. Common words become one token, rare
words split into pieces (`\"tokenization\"` may become `\"token\" + \"ization\"`), so there is no out-of-vocabulary word,
the vocabulary stays fixed, and misspellings like `fr33` still get pieces. The cost: token counts differ across
languages, numbers split oddly, and prices and context limits are counted in tokens.""",
     complexity="O(total characters) to tokenize; the dense count matrix is O(docs * vocab) memory, which is why "
                "real code uses a sparse matrix (`CountVectorizer`).",
     mistakes="Building the vocabulary on train plus test (leakage); a dense matrix for a big corpus; regex that drops "
              "digits; forgetting that `str.split()` keeps punctuation glued to words (`\"free!!\"`).",
     learn=["ai-nlp-basics", "cheat-python"])

# ---------------------------------------------------------------- Q2 TF-IDF + logistic regression
ex.q("A spam filter in ten lines", minutes=6,
     prompt="""Train a spam classifier on `tr`, evaluate on `te`:

- `TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), min_df=2)` fitted on the train texts only.
- `LogisticRegression(C=10, max_iter=2000)`.

Report for the spam class: precision, recall, F1, the confusion matrix, and average precision (PR AUC). What
accuracy would a model that says \"ham\" for everything get?

Then answer: the product manager says \"never put a real friend's message in the spam folder\". Which number does that
constrain, and how do you choose the threshold?""",
     hint1="Signal: short texts, binary label, need a strong fast baseline. Pattern: TF-IDF features + a linear "
           "classifier; evaluate with precision/recall on the minority class, not accuracy.",
     hint2="1. `vec.fit_transform(tr.text)`, `vec.transform(te.text)`.\n2. Fit the model, `predict_proba(...)[:, 1]`.\n"
           "3. `precision_score`, `recall_score`, `f1_score`, `confusion_matrix`, `average_precision_score`.\n"
           "4. Majority baseline = share of ham in test.\n5. Threshold: fix the false-positive rate (precision), "
           "maximize recall under it, on a validation set.",
     solution="""from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (precision_score, recall_score, f1_score, confusion_matrix,
                             average_precision_score)

vec = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), min_df=2)
X_tr, X_te = vec.fit_transform(tr["text"]), vec.transform(te["text"])
clf = LogisticRegression(C=10, max_iter=2000).fit(X_tr, tr["y"])
p_te = clf.predict_proba(X_te)[:, 1]
pred = (p_te >= 0.5).astype(int)
print("features", X_tr.shape[1])                                     # features 11456
print("precision", round(precision_score(te.y, pred), 3), "recall", round(recall_score(te.y, pred), 3),
      "F1", round(f1_score(te.y, pred), 3))                          # precision 0.994 recall 0.904 F1 0.947
print("confusion [tn fp fn tp]:", confusion_matrix(te.y, pred).ravel())   # [1205    1   18  169]
print("PR AUC", round(average_precision_score(te.y, p_te), 3))       # PR AUC 0.979
print("all-ham accuracy", round(1 - te.y.mean(), 3))                 # all-ham accuracy 0.866
for th in (0.5, 0.3, 0.2):
    pr = (p_te >= th).astype(int)
    print(th, "precision", round(precision_score(te.y, pr), 3), "recall", round(recall_score(te.y, pr), 3))
# 0.5 precision 0.994 recall 0.904
# 0.3 precision 0.977 recall 0.925
# 0.2 precision 0.967 recall 0.947""",
     why="""TF-IDF weights a term by how often it is in the message (here `1 + log(tf)` with `sublinear_tf`) times how
rare it is across messages (`idf = log((1 + N) / (1 + df)) + 1` in sklearn), and normalizes each message to unit
length. Bigrams add short phrases like \"call now\". With thousands of sparse features a regularized linear model is
fast, strong and easy to explain.

At the default 0.5 threshold, 169 of 187 test spams are caught (recall 0.904) and only 1 of 1,206 ham messages is
flagged (precision 0.994). Accuracy would look great even for a useless model: saying ham to everything already gives
0.866, so we report precision, recall and PR AUC (0.979) for the spam class.

\"Never lose a real message\" is a false-positive constraint, so precision on spam (or the ham false-positive rate).
Lowering the threshold to 0.2 catches more spam (recall 0.947) but flags 6 ham instead of 1. Choose the threshold on
a validation set (not this test set): the lowest threshold whose false-positive rate stays under the agreed budget,
and often add a softer action (a \"possible spam\" label) for the middle band.""",
     complexity="Vectorizing is linear in the text length; training is about O(iterations * nonzeros).",
     mistakes="Fitting the vectorizer on all data; reporting accuracy; tuning the threshold on the test set; "
              "reading TF-IDF + LR probabilities as calibrated without checking.",
     learn=["ai-nlp-basics", "ai-classification-metrics", "ai-logistic-regression"])

# ---------------------------------------------------------------- Q3 error analysis
ex.q("Read the mistakes, not just the score", minutes=7,
     prompt="""Do an error analysis of the Q2 model (re-create it in your cell if needed):

1. The 10 n-grams with the largest positive coefficients (push towards spam) and the 5 most negative.
2. The missed spams (false negatives) with the lowest spam probability: read them. What do they have in common?
3. A data check: how many test messages appear **word for word** in the training set? What does that do to the
   reported metrics? Re-compute precision and recall on the test messages that are not in train.
4. Try one fix for the misses you saw and measure it.""",
     hint1="Signal: \"why does the model fail\". Pattern: error analysis = inspect weights, read the worst errors, "
           "check the split for leakage (duplicates), then targeted fixes.",
     hint2="1. `vec.get_feature_names_out()` with `np.argsort(clf.coef_[0])`.\n2. Filter `te` where `y == 1` and "
           "`p < 0.5`, sort by p.\n3. `te.text.isin(set(tr.text))`.\n4. Ideas: character n-grams "
           "(`analyzer=\"char_wb\"`) for obfuscated spellings, the `<num>` token, a lower threshold.",
     solution="""names = vec.get_feature_names_out()
order = np.argsort(clf.coef_[0])
print("spam side:", list(names[order[-10:][::-1]]))
print("ham side :", list(names[order[:5]]))
# spam side: ['txt', 'call', 'text', 'reply', 'uk', 'www', 'free', '150p', 'to', 'mobile']
# ham side : ['me', 'my', 'your call', 'that', 'ok']

errs = te.assign(p=p_te)
missed = errs[(errs.y == 1) & (errs.p < 0.5)].sort_values("p")
for t, p in zip(missed.text[:4], missed.p[:4]):
    print(round(p, 3), t[:70])
# 0.008 Do you realize that in about 40 years, we'll have thousands of old lad
# 0.021 Hi ya babe x u 4goten bout me?' scammers getting smart..Though this is
# 0.023 For sale - arsenal dartboard. Good condition but no doubles or trebles
# 0.027 ringtoneking 84484

dup = errs.text.isin(set(tr.text))
print("test messages also in train:", dup.sum(), "of", len(errs), "(spam:", errs[dup].y.sum(), ")")
# test messages also in train: 151 of 1393 (spam: 37 )
clean = errs[~dup]
pr = (clean.p >= 0.5).astype(int)
print("without duplicates: precision", round(precision_score(clean.y, pr), 3),
      "recall", round(recall_score(clean.y, pr), 3))      # without duplicates: precision 0.992 recall 0.88

vec_c = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True, min_df=2)
clf_c = LogisticRegression(C=10, max_iter=2000).fit(vec_c.fit_transform(tr.text), tr.y)
pred_c = clf_c.predict(vec_c.transform(te.text))
print("char n-grams: precision", round(precision_score(te.y, pred_c), 3), "recall",
      round(recall_score(te.y, pred_c), 3), confusion_matrix(te.y, pred_c).ravel())
# char n-grams: precision 1.0 recall 0.941 [1206    0   11  176]""",
     why="""The weights make sense (`txt`, `call`, `free`, `150p`, `www`, `claim` style words for spam; personal words
like `me`, `my`, `ok` for ham), which is a basic sanity check. The worst misses look like personal chat or jokes, an
item for sale, or a bare short code (`ringtoneking 84484`, a 5-digit number our word features never saw). Some labels
are even debatable. That tells you where gains are: number and URL features, character patterns, maybe better labels.

The data check is the big finding: 151 of 1,393 test messages (37 of them spam) appear word for word in train, because
spam campaigns send the same text many times. Those are easy points; on the unseen messages recall falls from 0.904
to 0.88. The honest setup is to deduplicate before splitting (or split by group, e.g. by campaign or by time) so the
test set measures new messages.

Character n-grams (2 to 5 characters inside word boundaries) see pieces like `txt`, `£`, `0800`, `www.` and survive
misspellings, so they raise recall to 0.941 with no false positives here. Compare them on the deduplicated split too
before claiming the win.""",
     complexity="Error analysis is cheap; the char n-gram model has about 35k features and trains in about a second.",
     mistakes="Only looking at aggregate metrics; reading coefficients of unscaled or highly correlated features as "
              "importance; fixing errors by looking at the test set again and again (it becomes a training set).",
     learn=["ai-nlp-basics", "ai-features-imbalance"])

# ---------------------------------------------------------------- Q4 concept: TF-IDF vs modern NLP
ex.q("Is TF-IDF still worth knowing?", minutes=4, kind="text",
     prompt="""Answer out loud in 60 to 90 seconds: \"Explain TF-IDF in one formula. What can a bag-of-words model
not capture? When would you still ship TF-IDF plus logistic regression in 2026 instead of a transformer?\"""",
     hint1="Signal: classic versus modern NLP trade-off. Pattern: sparse lexical features versus dense contextual "
           "embeddings; cost, latency, data size, interpretability.",
     hint2="1. `tfidf(t, d) = tf(t, d) * log(N / df(t))`, then L2-normalize.\n2. Misses: word order beyond n-grams, "
           "synonyms, negation, context.\n3. Ship it when: little labelled data is still enough, latency or cost is "
           "tight, interpretability, a strong baseline, keyword-heavy tasks.",
     solution="""**Model answer (about 80 s):**

\"TF-IDF scores a term in a document as `tf(t, d) * log(N / df(t))`: frequent in this document, rare across documents.
Each document becomes a sparse vector over the vocabulary, usually L2-normalized, and words like 'the' get almost no
weight.

What it cannot capture: meaning beyond exact tokens. 'Refund' and 'money back' share nothing, so synonyms are missed.
Word order is lost except for short n-grams, so 'not good' needs a bigram, and the same word in different contexts,
like 'bank', gets one feature.

A fine-tuned transformer usually wins on accuracy for semantic tasks. But I would still ship TF-IDF plus logistic
regression when: the signal is lexical, as in spam, keyword routing or log classification, where it already gets 0.95+
F1; latency and cost must be tiny, microseconds on a CPU versus milliseconds on a GPU; I need to explain decisions or
let analysts read the weights; or labels are few and change quickly, since it retrains in seconds. And it is always
the baseline: if a transformer only beats it by one point, the extra cost may not be worth it. In retrieval, BM25, a
TF-IDF cousin, is still part of most hybrid search systems.\"""",
     why="Examiners like candidates who know the classic baseline, its limits, and the cost trade-off, not only "
         "the newest model.",
     learn=["ai-nlp-basics", "ai-rag"])

# ---------------------------------------------------------------- Q5 review: offline vs online recommender
ex.q("Great offline, flat online", minutes=4, kind="text", review=True,
     prompt="""Your new recommender improves offline NDCG@10 by 8% on last month's logs, but the A/B test shows no
change in watch time. Answer out loud in about 60 seconds: give at least three reasons and what you would do.""",
     hint1="Signal: offline/online mismatch. Pattern: logged-data bias (exposure, position), metric mismatch, "
           "and system effects.",
     hint2="1. Logs only contain what the old system showed: exposure and position bias.\n2. The offline label "
           "(click, rating) is not the online goal (watch time).\n3. Leakage or a random split instead of a time split.\n"
           "4. Serving differences: features, latency, candidate set.\n5. Novelty effects and A/B power.",
     solution="""**Model answer (about 75 s):**

\"First, the offline data is biased: the logs only contain items the old system chose to show, and at certain
positions. A model that imitates the old ranking scores well offline without being better for users. Fixes: evaluate
with exploration data or inverse propensity weighting, and use counterfactual or interleaving tests.

Second, metric mismatch: offline I may have optimized clicks or ratings while the A/B readout is watch time. Clickbait
can lift NDCG on clicks and do nothing for watch time. I would align the offline label with the online goal, for
example completion-weighted relevance.

Third, the evaluation itself: a random split instead of a time split leaks the future, or features available offline
are missing or stale at serving time, which is training-serving skew. I would log the online features and replay them.

Fourth, the system: the ranker may be fine but the candidate generator never surfaces the items it would rank well,
or latency went up. And finally the experiment: check power, sample ratio mismatch and novelty effects before
concluding there is no change.\"""",
     why="Reviews yesterday's recommender evaluation; this offline/online gap is one of the most asked follow-ups "
         "in recommender exams.",
     learn=["ai-recommenders", "ai-deployment-monitoring"])

ex.save()
