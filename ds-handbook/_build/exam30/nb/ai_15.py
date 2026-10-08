import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_mid_common import setup, MOVIELENS

# Day 15 AI: focus recommenders; review embeddings.
ex = Exam(15, "ai")
setup(ex, MOVIELENS, '''# time split per user: the first 80% of each user's ratings (by timestamp) train, the last 20% test
r = ratings.sort_values(["userId", "timestamp", "movieId"]).copy()
r["pos"] = r.groupby("userId").cumcount()
r["n"] = r.groupby("userId")["movieId"].transform("size")
train, test = r[r["pos"] < 0.8 * r["n"]], r[r["pos"] >= 0.8 * r["n"]]
seen = train.groupby("userId")["movieId"].apply(set).to_dict()                  # user -> movies in train
relevant = test[test["rating"] >= 4].groupby("userId")["movieId"].apply(set).to_dict()   # user -> liked test movies
pop_counts = train["movieId"].value_counts()                                      # train popularity, descending

# binary user x item matrix for items with at least 10 train ratings (for collaborative filtering)
items = pop_counts[pop_counts >= 10].index.to_numpy()
users = np.array(sorted(train["userId"].unique()))
uidx, iidx = {u: i for i, u in enumerate(users)}, {m: j for j, m in enumerate(items)}
tr = train[train["movieId"].isin(iidx)]
B = np.zeros((len(users), len(items)))
B[tr["userId"].map(uidx), tr["movieId"].map(iidx)] = 1
print("train", len(train), "test", len(test), "eval users", len(relevant), "B", B.shape)''', data=True)

ex.text("""**Data:** MovieLens small. Split by time inside each user: the first 80% of a user's ratings are `train`,
the last 20% are `test`. A test movie is **relevant** if the user rated it 4 or more: `relevant[user]` is that set
(591 users have at least one). `seen[user]` = movies the user rated in train (never recommend them again).
`pop_counts` = number of train ratings per movie. `B` = binary users by items matrix (610 by 1,859) for the movies with
at least 10 train ratings; `users`, `items`, `uidx`, `iidx` map between ids and rows/columns.""")

# ---------------------------------------------------------------- Q1 ranking metrics
ex.q("Score a ranked list", minutes=5,
     prompt="""Write three metrics for one user, binary relevance:

- `precision_at_k(rec, rel, k)`: share of the top `k` recommendations that are relevant.
- `recall_at_k(rec, rel, k)`: share of the relevant items found in the top `k`.
- `ndcg_at_k(rec, rel, k)`: `DCG / IDCG`, with `DCG = sum over hits of 1 / log2(position + 1)` (position starts at 1)
  and IDCG = the DCG of a perfect list with `min(len(rel), k)` hits at the top.

`rec` is a list of item ids in ranked order, `rel` a set. Example: `rec = [5, 3, 9, 1, 7]`, `rel = {3, 7, 8}`, `k = 5`:
precision 0.4, recall 0.667, NDCG 0.478.

Follow-up: two lists both have 2 hits in the top 10. When do precision and NDCG disagree, and which one would you
report to a product team?""",
     stub="""def precision_at_k(rec, rel, k):
    pass

def recall_at_k(rec, rel, k):
    pass

def ndcg_at_k(rec, rel, k):
    pass""",
     tests="""rec, rel = [5, 3, 9, 1, 7], {3, 7, 8}
check("precision@5", lambda: precision_at_k(rec, rel, 5), 0.4)
check("recall@5", lambda: recall_at_k(rec, rel, 5), 2 / 3)
check("ndcg@5", lambda: ndcg_at_k(rec, rel, 5), 0.4777, tol=1e-4)
check("ndcg of a perfect list is 1", lambda: ndcg_at_k([3, 7, 8, 1], rel, 3), 1.0)
check("hit at rank 1 beats hit at rank 3", lambda: ndcg_at_k([3, 1, 2], {3}, 3) > ndcg_at_k([1, 2, 3], {3}, 3), True)
check("precision@2 counts only the top 2", lambda: precision_at_k(rec, rel, 2), 0.5)""",
     hint1="Signal: \"how good is this ranked list\". Pattern: top-k ranking metrics; NDCG discounts hits by "
           "`log2(position + 1)` so early hits count more.",
     hint2="1. `hits = [item in rel for item in rec[:k]]`.\n2. Precision = `sum(hits) / k`, recall = "
           "`sum(hits) / len(rel)`.\n3. DCG = `sum(h / log2(i + 2) for i, h in enumerate(hits))` (i from 0).\n"
           "4. IDCG = `sum(1 / log2(i + 2) for i in range(min(len(rel), k)))`.",
     solution="""def precision_at_k(rec, rel, k):
    return sum(item in rel for item in rec[:k]) / k

def recall_at_k(rec, rel, k):
    return sum(item in rel for item in rec[:k]) / len(rel)

def ndcg_at_k(rec, rel, k):
    dcg = sum(1 / np.log2(i + 2) for i, item in enumerate(rec[:k]) if item in rel)
    idcg = sum(1 / np.log2(i + 2) for i in range(min(len(rel), k)))
    return dcg / idcg

rec, rel = [5, 3, 9, 1, 7], {3, 7, 8}
print(precision_at_k(rec, rel, 5), round(recall_at_k(rec, rel, 5), 3), round(ndcg_at_k(rec, rel, 5), 3))
# 0.4 0.667 0.478""",
     why="""In the example the hits are at positions 2 and 5: `DCG = 1/log2(3) + 1/log2(6) = 0.631 + 0.387 = 1.018`;
the ideal list has 3 hits at the top: `IDCG = 1 + 0.631 + 0.5 = 2.131`; NDCG = 0.478.

Precision ignores order: 2 hits at positions 1 and 2 or at 9 and 10 both give 0.2. NDCG rewards the first list
because users look at the top of the feed and attention drops fast. For a product team I would report precision or
recall at k as the easy-to-explain number (\"2 of the 10 suggestions were movies the user went on to love\") and
use NDCG to compare rankers, since it matches how attention works. MAP and MRR are other order-aware options; MRR only
looks at the first hit.""",
     complexity="O(k) per user with `rel` as a set (O(k * |rel|) if it were a list).",
     mistakes="Dividing precision by the list length instead of k when fewer than k items are returned (be explicit "
              "about the convention); IDCG with `len(rel)` hits even when it exceeds k (NDCG then can never reach 1); "
              "position counted from 0 inside the log (`log2(1) = 0`, division by zero).",
     learn=["ai-recommenders", "cheat-ml-metrics"])

# ---------------------------------------------------------------- Q2 popularity baseline
ex.q("The baseline everyone forgets", minutes=5,
     prompt="""Write `recommend_popular(user, k)`: the `k` most-rated movies in **train** that the user has not seen
in train, most popular first. Then evaluate it on every user in `relevant`: mean precision@10 and mean NDCG@10 (use your
functions from Q1).

Before running it, guess: will popularity be far behind a personalized model, or close? Why is this baseline so hard
to beat on MovieLens and in many real products?""",
     stub="""def recommend_popular(user, k=10):
    # your code here
    pass""",
     tests="""recs = recommend_popular(1, 10)
check("returns k items", lambda: len(recommend_popular(1, 10)), 10)
check("never recommends a seen movie", lambda: set(recommend_popular(1, 10)) & seen[1], lambda s: len(s) == 0)
check("most popular first", lambda: [pop_counts[m] for m in recommend_popular(1, 10)],
      lambda c: all(a >= b for a, b in zip(c, c[1:])))""",
     hint1="Signal: \"most-rated\", same list for everyone minus what they saw. Pattern: popularity baseline; always "
           "build it first.",
     hint2="1. `pop_counts.index` is already sorted by count.\n2. Walk down it, skip movies in `seen[user]`, stop at "
           "k.\n3. Loop over `relevant.items()`, compute both metrics, take the mean.",
     solution="""popular_list = list(pop_counts.index)

def recommend_popular(user, k=10):
    s = seen.get(user, set())
    out = []
    for m in popular_list:
        if m not in s:
            out.append(m)
            if len(out) == k:
                break
    return out

P = [precision_at_k(recommend_popular(u), rel, 10) for u, rel in relevant.items()]
N = [ndcg_at_k(recommend_popular(u), rel, 10) for u, rel in relevant.items()]
print("popularity  P@10", round(np.mean(P), 4), " NDCG@10", round(np.mean(N), 4))
# popularity  P@10 0.0562  NDCG@10 0.074
print("titles for user 1:", [title_of[m] for m in recommend_popular(1, 3)])
# titles for user 1: ['Shawshank Redemption, The (1994)', 'Silence of the Lambs, The (1991)', 'Terminator 2: Judgment Day (1991)']""",
     why="""On average 0.56 of the 10 popular movies shown to a user are later rated 4 or more, out of 9,700 movies. That is a
strong result for a non-personalized list, because popularity is a real signal: popular movies are popular because
most people like them, and in a log-based test set the same exposure bias that made them popular also decides what
users rate next. Many papers have shown that badly tuned \"advanced\" recommenders lose to this baseline. Always report
it, and report it per segment: popularity is weak for heavy users with niche taste.

Its problems are not in the accuracy number: every user gets the same list, it never surfaces new or niche items
(low catalog coverage), and it creates a feedback loop where the popular get more popular.""",
     complexity="O(k + |seen|) per user after one O(n log n) sort of the counts.",
     mistakes="Computing popularity on the full data (test leaks into train); forgetting to remove seen items; "
              "averaging over all users including those with no relevant test item (their score is undefined).",
     learn=["ai-recommenders", "ai-ml-framing"])

# ---------------------------------------------------------------- Q3 item-item collaborative filtering
ex.q("People who watched this also watched", minutes=8,
     prompt="""Build item-based collaborative filtering on the binary matrix `B` (users by items):

1. Item-item cosine similarity `S = Bn.T @ Bn`, where `Bn` has each **column** scaled to unit length; set the
   diagonal to 0.
2. Keep only the 20 most similar items in each column of `S` (set the rest to 0). This neighbourhood trimming removes
   noisy weak similarities.
3. Scores for all users: `B @ S`. A user's score for item j = sum of similarities between j and the items the user
   already watched.

Write `item_knn_scores(B, n_neighbors)` that returns the users by items score matrix. Then recommend the top 10
unseen items for every user in `relevant`, and compare mean precision@10 and NDCG@10 with popularity. Also compare
**catalog coverage**: how many distinct movies appear across all users' top-10 lists.

Follow-up: an examiner says \"your model is only 20% better than popularity, so it is useless\". Answer.""",
     stub="""def item_knn_scores(B, n_neighbors=20):
    # your code here
    pass""",
     tests="""check("score matrix shape", lambda: item_knn_scores(B, 20).shape, B.shape)
check("matches the definition on a toy matrix",
      lambda: item_knn_scores(np.array([[1.0, 1, 0], [1, 1, 0], [0, 1, 1]]), 1),
      [[0.8165, 0.8165, 0.5774], [0.8165, 0.8165, 0.5774], [0.8165, 0.0, 0.5774]], tol=1e-4)""",
     hint1="Signal: \"also watched\", item-to-item. Pattern: neighbourhood collaborative filtering: cosine between "
           "item columns, keep top neighbours, score = sum of similarities to the user's history.",
     hint2="1. `Bn = B / norm(B, axis=0)` (guard zero columns).\n2. `S = Bn.T @ Bn`, `np.fill_diagonal(S, 0)`.\n"
           "3. Per column, threshold at the n-th largest value: `th = -np.sort(-S, axis=0)[n - 1]`, then "
           "`S[S < th] = 0`.\n4. `scores = B @ S`; set seen items to `-inf`; `argsort` descending.",
     solution="""def item_knn_scores(B, n_neighbors=20):
    Bn = B / np.maximum(np.linalg.norm(B, axis=0), 1e-12)
    S = Bn.T @ Bn
    np.fill_diagonal(S, 0)
    th = -np.sort(-S, axis=0)[n_neighbors - 1]          # n-th largest similarity in each column
    S[S < th] = 0
    return B @ S

scores = item_knn_scores(B, 20)
def recommend_knn(user, k=10):
    s = scores[uidx[user]].copy()
    s[B[uidx[user]] > 0] = -np.inf                       # never recommend seen items
    return list(items[np.argsort(-s)[:k]])

for name, rec in [("popularity", recommend_popular), ("item-kNN", recommend_knn)]:
    lists = {u: rec(u) for u in relevant}
    P = np.mean([precision_at_k(lists[u], rel, 10) for u, rel in relevant.items()])
    N = np.mean([ndcg_at_k(lists[u], rel, 10) for u, rel in relevant.items()])
    cover = len(set(m for l in lists.values() for m in l))
    print(f"{name:10s} P@10 {P:.4f}  NDCG@10 {N:.4f}  coverage {cover}")
# popularity P@10 0.0562  NDCG@10 0.0740  coverage 98
# item-kNN   P@10 0.0680  NDCG@10 0.0902  coverage 794""",
     why="""Item-kNN scores a movie by how strongly it co-occurs with what the user already watched, so the list is
personal. It beats popularity by about 21% on precision@10 (0.068 versus 0.056) and 22% on NDCG@10, and, more
important for the product, it uses 794 distinct movies across users instead of 98. The toy test: items 0 and 1 have
cosine `2 / sqrt(2 * 3) = 0.8165`, and with 1 neighbour each item keeps only its single best partner.

The follow-up: a 20% relative lift in an offline ranking metric is large; production teams ship 1 to 2% online gains.
Offline numbers on logged data also underrate personalization, because the test set was generated under the old
(popularity-heavy) exposure. And coverage, novelty and fairness for creators matter as much as accuracy. The right
next step is an online A/B test on watch time and retention, not giving up. Stronger models (matrix factorization,
EASE, two-tower networks) usually add more, and popularity often stays as a feature or a fallback for new users.""",
     complexity="Similarity O(users * items^2) time, O(items^2) memory: fine for 1,859 items, impossible for 10 "
                "million. At scale, compute co-occurrence with sparse joins in Spark or use embeddings plus ANN search.",
     mistakes="Normalizing rows instead of columns (that gives user-user similarity); keeping the diagonal (each "
              "item recommends itself); not excluding seen items; evaluating on items the model cannot score "
              "without saying so.",
     learn=["ai-recommenders", "ai-embeddings"])

# ---------------------------------------------------------------- Q4 concept: recsys design and evaluation
ex.q("From a model to a For You feed", minutes=5, kind="text",
     prompt="""Answer out loud in 60 to 90 seconds: \"Netflix-prize style recommenders predicted star ratings and
optimized RMSE. Why do modern feeds (TikTok, YouTube) not do that? Describe the usual two-stage architecture and how
you would evaluate it.\"""",
     hint1="Signal: explicit versus implicit feedback, production recommender. Pattern: candidate generation then "
           "ranking; offline ranking metrics then online A/B.",
     hint2="1. Implicit signals (watch time, completion, likes, skips) are abundant; ratings are rare and biased.\n"
           "2. RMSE on observed ratings is not ranking quality.\n3. Stage 1: retrieve hundreds from millions (two-tower "
           "+ ANN, co-occurrence, follows). Stage 2: rich ranker predicts several engagement events, combined into "
           "one score. 4. Re-ranking for diversity and policy.\n5. Offline recall@k / NDCG, then A/B on long-term "
           "metrics.",
     solution="""**Model answer (about 85 s):**

\"Explicit ratings are rare, most users never rate, and they are biased toward things people chose to watch. Feeds
have plenty of implicit feedback instead: watch time, completion, replays, likes, shares, skips. Also the product
problem is ranking, choosing the few items to show now, and a model that predicts 3.6 versus 3.8 stars with low RMSE
can still order the top of the list badly. So we predict engagement events and optimize ranking.

Architecture: stage one is candidate generation. From tens of millions of videos, several cheap retrievers pick a few
hundred: a two-tower embedding model with approximate nearest neighbour search, co-occurrence, followed creators,
trending and fresh content for exploration. Stage two is a heavy ranker, a deep model with user, item, context and
cross features, that predicts several outcomes such as probability of finishing, liking or skipping, and combines them
into one score with business weights. A final re-ranking step adds diversity, freshness and policy rules.

Evaluation: offline, recall at k for retrieval and NDCG or AUC per event for the ranker, on a time-based split. But the
data is logged under the old system, so the real decision is an online A/B test on long-term metrics: watch time per
user, retention, creator diversity, and guardrails such as reports and hides.\"""",
     why="This is the bridge from today's toy recommender to the ML system design rounds on days 24 and 29.",
     learn=["ai-recommenders", "ai-ml-system-design"])

# ---------------------------------------------------------------- Q5 review: MF embeddings and cold start
ex.q("Users and items in one space", minutes=4, kind="text", review=True,
     prompt="""Answer out loud in about 60 seconds: \"In matrix factorization and in a two-tower model, what are the
user and item embeddings, and how is a score computed? How do you recommend for a brand-new user who has done
nothing yet?\"""",
     hint1="Signal: user and item vectors. Pattern: score = dot product of a user embedding and an item embedding; "
           "cold start needs features instead of an id.",
     hint2="1. MF: `r_ui ~ p_u . q_i` (+ biases); one learned vector per id.\n2. Two-tower: each tower is a network "
           "over features (id, history, context; item content), output vectors, dot product.\n3. New user: "
           "onboarding choices, context (country, device, time), popular per segment, then fast updates from the "
           "first interactions; explore and exploit.",
     solution="""**Model answer (about 70 s):**

\"In matrix factorization every user u gets a vector `p_u` and every item i a vector `q_i`, usually 32 to 256
numbers, learned so that `p_u . q_i` plus user and item biases predicts the interaction. Items that are liked by the
same users get similar `q` vectors; that is exactly the embedding idea from day 13.

A two-tower model generalizes this: the user tower is a neural network over the user id plus features such as recent
watch history, country, device and time of day; the item tower is a network over the item id plus content features
such as creator, text, audio and visual embeddings. The score is still the dot product of the two output vectors, so
all item vectors can be precomputed and searched with an ANN index.

For a brand-new user there is no id embedding worth using. I would fall back to what we know: context features
(country, language, device, time), any onboarding interests, and popular or trending items in that segment. Because the
user tower also takes recent history as input, the recommendations can update after the first few videos within the
same session. Some exploration, such as a bandit over topic categories, speeds up learning the user's taste.\"""",
     why="Reviews embeddings (day 13) in the recommender setting and covers cold start, the most common follow-up.",
     learn=["ai-embeddings", "ai-recommenders"])

ex.save()
