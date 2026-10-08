import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_mid_common import setup, MOVIELENS

# Day 13 AI: focus embeddings; review neural-networks.
ex = Exam(13, "ai")
setup(ex, MOVIELENS, '''# movies with at least 50 ratings; rating minus that user's mean rating; missing = 0
counts = ratings["movieId"].value_counts()
r50 = ratings[ratings["movieId"].isin(counts[counts >= 50].index)].copy()
r50["centered"] = r50["rating"] - r50.groupby("userId")["rating"].transform("mean")
M_df = r50.pivot_table(index="movieId", columns="userId", values="centered", fill_value=0)
M = M_df.to_numpy()                        # (movies, users)
movie_ids = list(M_df.index)
n_ratings = counts.loc[movie_ids].to_numpy()
print("item x user matrix:", M.shape)''', data=True)

ex.text("""**Data:** MovieLens small (100,836 ratings by 610 users). `M` is an item by user matrix for the 450 movies
with at least 50 ratings: each entry is the rating minus that user's mean rating, and 0 when the user did not rate the
movie. `movie_ids[i]` is the movieId of row `i`, `title_of[movieId]` its title, `n_ratings[i]` its rating count.""")

# ---------------------------------------------------------------- Q1 cosine top-k
ex.q("Nearest neighbours in vector space", minutes=5,
     prompt="""Write `top_k_cosine(E, i, k)`: given an embedding matrix `E (n, d)` (one row per item), return the
indices of the `k` rows most similar to row `i` by cosine similarity, most similar first, **excluding `i` itself**.
Use vectorized numpy (no Python loop over items).

Example: `E = [[1, 0], [10, 1], [0, 1], [-1, 0]]`, `i = 0`, `k = 2` returns `[1, 2]`: row 1 points almost the same
way (cosine 0.995), row 2 is orthogonal (0), row 3 is opposite (-1).

Follow-ups: with the **dot product** instead of cosine, what would change in this example, and why does that matter
for recommendations? What do you do when n is 100 million?""",
     stub="""def top_k_cosine(E, i, k):
    # your code here
    pass""",
     tests="""E_toy = np.array([[1.0, 0.0], [10.0, 1.0], [0.0, 1.0], [-1.0, 0.0]])
check("toy example", lambda: list(top_k_cosine(E_toy, 0, 2)), [1, 2])
check("query excluded even when k = n - 1", lambda: list(top_k_cosine(E_toy, 0, 3)), [1, 2, 3])
check("from another row", lambda: list(top_k_cosine(E_toy, 3, 1)), [2])
check("scale does not matter", lambda: list(top_k_cosine(E_toy * [[1], [100], [0.01], [5]], 0, 3)), [1, 2, 3])""",
     hint1="Signal: \"most similar vectors\". Pattern: L2-normalize rows, then one matrix-vector product gives all "
           "cosines; sort descending and drop the query.",
     hint2="1. `En = E / np.linalg.norm(E, axis=1, keepdims=True)`.\n2. `sims = En @ En[i]`.\n"
           "3. `sims[i] = -np.inf` so the query cannot win.\n4. `np.argsort(-sims)[:k]` (or `np.argpartition` for "
           "large n, then sort only the k winners).",
     solution="""def top_k_cosine(E, i, k):
    En = E / np.linalg.norm(E, axis=1, keepdims=True)
    sims = En @ En[i]
    sims[i] = -np.inf
    return np.argsort(-sims)[:k]

E_toy = np.array([[1.0, 0.0], [10.0, 1.0], [0.0, 1.0], [-1.0, 0.0]])
print(top_k_cosine(E_toy, 0, 2))        # [1 2]
print(E_toy @ E_toy[2])                 # [0. 1. 1. 0.]  dot product from row 2: rows 1 and 2 tie""",
     why="""Cosine is the dot product of unit vectors, so it compares direction only: `cos(a, b) = a.b / (|a| |b|)`.
Normalizing once and multiplying by the query gives all n similarities in O(n d).

Dot product versus cosine: the dot product also rewards length. From row 2, `[0, 1]`, the dot product gives row 1
(`[10, 1]`, mostly pointing elsewhere) the same score as row 2 itself, only because it is long. In learned embeddings
the norm often grows with popularity or frequency, so dot-product retrieval pushes popular items and cosine retrieval
gives \"more like this\" items. Two-tower recommenders often use the dot product on purpose, because popularity is
useful signal for clicks; for similar-item lists cosine is usually better.

At 100 million items, exact search is too slow per query, so use approximate nearest neighbour search (HNSW graphs,
IVF with product quantization, libraries such as FAISS or ScaNN), which trades a little recall for 100x to 1000x speed.""",
     complexity="O(n d) for the similarities plus O(n log n) for the full sort (O(n + k log k) with argpartition).",
     mistakes="Forgetting to exclude the query (it is always its own best match); normalizing along the wrong axis; "
              "dividing by zero for an all-zero row (add a small eps); sorting ascending.",
     learn=["ai-embeddings", "cheat-numpy"])

# ---------------------------------------------------------------- Q2 SVD item embeddings on MovieLens
ex.q("Movie vectors from ratings alone", minutes=7,
     prompt="""Build 20-dimensional movie embeddings from the rating matrix `M` with a truncated SVD:
`M ~ U_k S_k V_k^T`, item vectors = `U_k * S_k` (rows of `U` are items here because `M` is item by user).

1. Write `item_embeddings(M, k)` returning an array of shape `(n_items, k)`.
2. Using your `top_k_cosine` idea, print the 5 nearest movies to `Godfather, The (1972)` and to `Toy Story (1995)`.
3. What share of the total squared singular values (\"energy\") do 20 dimensions keep?

No genres or titles are used, only who rated what. Follow-ups: why subtract each user's mean rating first? What is
wrong with filling missing ratings with 0, and what does real matrix factorization (ALS, SGD) do instead?""",
     stub="""def item_embeddings(M, k):
    # your code here
    pass""",
     tests="""check("shape", lambda: item_embeddings(M, 20).shape, (450, 20))
check("same as numpy SVD up to column signs", lambda: np.abs(item_embeddings(M, 5)),
      np.abs(np.linalg.svd(M, full_matrices=False)[0][:, :5] * np.linalg.svd(M, full_matrices=False)[1][:5]), tol=1e-6)""",
     hint1="Signal: a big sparse co-occurrence or rating matrix, \"vectors for items\". Pattern: low-rank matrix "
           "factorization (truncated SVD); similar rows of `U_k S_k` = items rated alike by the same users.",
     hint2="1. `U, S, Vt = np.linalg.svd(M, full_matrices=False)`.\n2. Return `U[:, :k] * S[:k]`.\n"
           "3. Normalize rows, cosine with the query row, sort, skip the query.\n"
           "4. Energy kept = `(S[:k]**2).sum() / (S**2).sum()`.",
     solution="""def item_embeddings(M, k):
    U, S, Vt = np.linalg.svd(M, full_matrices=False)
    return U[:, :k] * S[:k]

E = item_embeddings(M, 20)
En = E / np.linalg.norm(E, axis=1, keepdims=True)
row_of = {title_of[m]: i for i, m in enumerate(movie_ids)}
for q in ["Godfather, The (1972)", "Toy Story (1995)"]:
    sims = En @ En[row_of[q]]
    sims[row_of[q]] = -np.inf
    best = np.argsort(-sims)[:5]
    print(q, "->", [(title_of[movie_ids[j]], round(float(sims[j]), 2)) for j in best])
# Godfather, The (1972) -> Godfather: Part II (0.95), Goodfellas (0.91), Cool Hand Luke (0.73),
#                          Reservoir Dogs (0.73), Apocalypse Now (0.72)
# Toy Story (1995) -> Aladdin (0.78), Toy Story 3 (0.68), Full Monty (0.62), Babe (0.59), Toy Story 2 (0.54)

S = np.linalg.svd(M, compute_uv=False)
print("energy kept by 20 dims:", round((S[:20] ** 2).sum() / (S ** 2).sum(), 3))   # 0.332
norms = np.linalg.norm(E, axis=1)
print("corr(vector length, number of ratings):", round(np.corrcoef(norms, n_ratings)[0, 1], 2))  # 0.74""",
     why="""SVD finds the best rank-k approximation of `M` (Eckart-Young). Movies rated in the same pattern by the
same users get nearby rows, so the Godfather sits next to its sequel and other crime classics, and Toy Story next to
family animation, with no genre information at all. That is the core idea of collaborative filtering and of all learned
embeddings: meaning comes from co-occurrence. 20 of 450 dimensions keep only 33% of the energy, which is normal: the
rest is mostly noise from sparse data.

Subtracting each user's mean removes rating style (a harsh rater gives 3 to films they like) so the vectors capture
taste. The final line shows why Q1's cosine matters: vector length correlates 0.74 with the number of ratings, so a
dot-product search would favour blockbusters.

Filling missing ratings with 0 treats \"not watched\" as \"exactly average\", which biases the factors, and a dense SVD
does not scale past millions of items. Real matrix factorization fits `r_ui ~ mu + b_u + b_i + p_u . q_i` only on the
observed entries, with L2 regularization, by alternating least squares or SGD. For implicit feedback (views, clicks),
weighted ALS or a two-tower network is used.""",
     complexity="Dense SVD of an m by n matrix is O(m n min(m, n)); for large sparse matrices use a truncated "
                "solver (`scipy.sparse.linalg.svds`, randomized SVD) costing about O(nnz * k).",
     mistakes="Taking rows of `Vt` (those are users here); forgetting to multiply by `S` (then all dimensions count "
              "equally; both conventions exist, but say which); comparing raw dot products; not excluding the query.",
     learn=["ai-embeddings", "ai-recommenders", "ai-unsupervised"])

# ---------------------------------------------------------------- Q3 concept: word2vec
ex.q("How word vectors are learned", minutes=4, kind="text",
     prompt="""Answer out loud in 60 to 90 seconds: \"Explain how word2vec skip-gram with negative sampling learns
embeddings. What is the training objective, why negative sampling, and how is it related to what you just did with
SVD?\" Mention one limitation of static word vectors.""",
     hint1="Signal: \"how are embeddings trained\". Pattern: predict context from a word; dot products as logits; "
           "negative sampling turns a huge softmax into small binary classifications.",
     hint2="1. Pairs (center word, context word within a window).\n2. Score = `sigmoid(u_center . v_context)`.\n"
           "3. Positive pairs pushed to 1, k random negatives pushed to 0.\n4. Equivalent to factorizing a shifted "
           "PMI matrix.\n5. Limitation: one vector per word, no context (\"bank\").",
     solution="""**Model answer (about 80 s):**

\"Skip-gram slides a window over text and makes pairs: a center word and each word within, say, 5 positions. Each word
has two vectors, one as center and one as context. The model wants `sigmoid(u_center . v_context)` to be high for real
pairs.

A full softmax over a vocabulary of a million words for every pair is too expensive, so negative sampling replaces it:
for each real pair, draw k random words, usually 5 to 20, from the unigram distribution raised to the power 0.75, and
train a logistic regression to say 1 for the real pair and 0 for the fakes. The loss is
`-log sigmoid(u . v_pos) - sum over negatives of log sigmoid(-u . v_neg)`. Words that appear in similar contexts end up
with similar vectors, which is the distributional hypothesis.

Levy and Goldberg showed that this implicitly factorizes a word-context matrix of pointwise mutual information, shifted
by `log k`. So it is the same family as my SVD of the rating matrix: co-occurrence counts in, low-rank vectors out.

The limitation: one static vector per word, so \"bank\" has the same vector in \"river bank\" and \"bank loan\".
Contextual models like BERT or GPT produce a different vector for each occurrence, which is why they replaced word2vec
for most tasks.\"""",
     why="It checks that you know embeddings are trained by a prediction task, not hand-made, and connects neural "
         "and matrix-factorization views.",
     learn=["ai-embeddings", "ai-nlp-basics"])

# ---------------------------------------------------------------- Q4 concept: embeddings in production
ex.q("Shipping a \"similar videos\" embedding", minutes=5, kind="text",
     prompt="""You trained video embeddings and offline neighbours look good. Answer out loud in 60 to 90 seconds:
how do you evaluate them before launch, how do you serve nearest-neighbour lookups for 50 million videos at low
latency, and what happens to a video uploaded 5 minutes ago?""",
     hint1="Signal: embeddings in production. Pattern: offline retrieval metrics + online A/B, ANN index, cold start "
           "with content features.",
     hint2="1. Offline: recall@k of held-out co-watched pairs, human judgments, slices (new, niche, languages).\n"
           "2. Online: A/B on watch time, not only clicks.\n3. Serving: ANN index (HNSW, IVF-PQ), rebuilt or updated "
           "regularly; version the model and index together.\n4. Cold start: content encoders (title, audio, frames) "
           "into the same space, then blend in behaviour data.",
     solution="""**Model answer (about 85 s):**

\"Offline, I hold out recent sessions and measure recall at k: when a user watched A then B, is B in A's top 50
neighbours? I compare against simple baselines like co-view counts and popularity, check slices such as new videos,
small creators and each language, and do a quick human review for nonsense or unsafe neighbours. But offline metrics
only rank candidates; the launch decision comes from an A/B test on watch time, retention and diversity.

Serving: exact search over 50 million vectors of dimension 128 is about 6 billion multiply-adds per query, too slow.
I would use an approximate nearest-neighbour index, HNSW or IVF with product quantization in FAISS or ScaNN, which
answers in a few milliseconds with roughly 95% recall. Embeddings and index must be versioned together: vectors from
two model versions live in different spaces and must never be mixed.

A video uploaded 5 minutes ago has no interactions, so a pure collaborative embedding does not exist for it. I would
train a content tower that maps title, audio, frames and creator into the same space, use that vector at upload time,
and blend in the behaviour-based vector as views arrive. Exploration traffic for new videos also helps collect that
data.\"""",
     why="TikTok and Google style ML exams quickly move from \"what is an embedding\" to retrieval at scale, "
         "versioning and cold start.",
     learn=["ai-embeddings", "ai-recommenders", "ai-ml-system-design"])

# ---------------------------------------------------------------- Q5 review: batch norm vs layer norm
ex.q("Two normalization layers", minutes=4, kind="text", review=True,
     prompt="""Answer out loud in about 60 seconds: \"What is the difference between batch normalization and layer
normalization? Why do transformers use layer norm?\" For an activation tensor of shape `(batch, features)`, say over
which axis each one computes its mean and variance.""",
     hint1="Signal: normalization layers. Pattern: which axis the statistics are computed over, and what that means "
           "at inference and for variable-length sequences.",
     hint2="1. BatchNorm: per feature, over the batch (axis 0); running averages at inference.\n2. LayerNorm: per "
           "example, over the features (axis 1); same computation at train and inference.\n3. Both then apply a "
           "learned scale and shift.\n4. Transformers: small or variable batches, sequences, autoregressive "
           "decoding one token at a time.",
     solution="""**Model answer (about 70 s):**

\"Both standardize activations and then apply a learned scale `gamma` and shift `beta`. The difference is the axis.

Batch norm computes, for each feature, the mean and variance over the examples in the mini-batch, axis 0 of a
`(batch, features)` tensor. So each example's output depends on the other examples in the batch. At inference there is
no batch, so it uses running averages collected during training, and train and inference behave differently. It works
well for CNNs with large batches, but it is fragile with small batches and awkward for sequences of different lengths.

Layer norm computes the mean and variance over the features of each single example, axis 1, or the last axis for a
token. It does not depend on the batch at all, so training and inference are identical, batch size 1 works, and every
token in every sequence is normalized on its own.

That is why transformers use it: batches of variable-length text, often small per device, and generation one token at a
time. Modern LLMs often use RMSNorm, which drops the mean subtraction, and put the norm before each sub-layer, called
pre-norm, which makes deep stacks more stable.\"""",
     why="Reviews yesterday's neural-network training tricks and prepares the transformer block on day 17.",
     learn=["ai-neural-networks", "ai-attention-transformer"])

ex.save()
