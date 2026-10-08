import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_easy_common import start, qc

# Day 10 AI: focus unsupervised (k-means, PCA); review features-imbalance.
ex = start(10, loads=["penguins"],
           builtin="`load_breast_cancer()` from scikit-learn (built in): 569 tumours, 30 numeric features on very "
                   "different scales.")

qc(ex, title="Groups without labels", minutes=4, kind="text",
   prompt="Explain k-means in about 90 seconds: the objective, the algorithm, how you pick k, and three "
          "situations where it fails. Finish with one sentence on how PCA differs from clustering.",
   hint1="Signal: 'segment users, no labels'. Pattern: k-means (minimise within-cluster squared distance) and "
         "its assumptions.",
   hint2="1. Objective: inertia `sum ||x - mu_c(x)||^2`. 2. Lloyd's algorithm: assign to nearest centre, move "
         "centres to the mean, repeat. 3. k-means++ init, several restarts. 4. Choose k: elbow, silhouette, "
         "business use. 5. Fails: unscaled features, non-spherical or unequal clusters, outliers, categorical data.",
   solution="**Model answer (about 90 s):**\n\n"
            "\"k-means splits the data into k groups to minimise the within-cluster sum of squared distances, "
            "the inertia `sum_i ||x_i - mu_c(i)||^2`. Lloyd's algorithm alternates two steps: assign each point "
            "to its nearest centre, then move each centre to the mean of its points. Each step lowers the "
            "inertia, so it converges, but only to a local optimum; so we use k-means++ initialisation (spread-out "
            "starting centres) and several restarts. Each iteration costs `O(n k d)`.\n\n"
            "To choose k: the elbow of inertia versus k, the silhouette score, the stability of clusters across "
            "samples, and above all whether the segments are usable by the business.\n\n"
            "It fails when features are on different scales (the largest unit dominates the distance), when "
            "clusters are elongated, nested or of very different sizes or densities (it assumes round, "
            "similar-size blobs), with outliers (means get pulled), and with categorical data (use k-modes or "
            "Gower distance). Alternatives: Gaussian mixtures, DBSCAN, hierarchical clustering.\n\n"
            "PCA is different: it does not group rows, it finds new axes (directions of maximum variance) to "
            "compress the columns.\"",
   why="The objective, the two alternating steps, local optima with k-means++, how to choose k, and the "
       "scaling/shape assumptions cover what examiners check.",
   mistakes="Saying k-means finds the global optimum. Forgetting scaling. Choosing k only by the elbow when the "
            "curve has no clear elbow.",
   learn=["ai-unsupervised"])

sol2 = '''from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
d = penguins.dropna(subset=cols)
print("rows:", len(d))                                           # out: rows: 342

raw_labels = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(d[cols])
Z = StandardScaler().fit_transform(d[cols])
km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(Z)
print("ARI unscaled:", round(adjusted_rand_score(d["species"], raw_labels), 3))   # out: ARI unscaled: 0.331
print("ARI scaled:  ", round(adjusted_rand_score(d["species"], km.labels_), 3))    # out: ARI scaled:   0.793
print(pd.crosstab(d["species"], km.labels_, colnames=["cluster"]).to_string())
# (cluster numbers are arbitrary and can differ between versions)
# out: cluster      0    1   2
# out: species
# out: Adelie       0  127  24
# out: Chinstrap    0    5  63
# out: Gentoo     123    0   0'''
qc(ex, title="Can k-means find the species?", minutes=7,
   prompt="Use `penguins` with the four body measurements (drop rows where any is missing). Pretend you do not "
          "know `species`.\n\n"
          "1. Run `KMeans(n_clusters=3, n_init=10, random_state=0)` on the **raw** measurements, and again on "
          "**standardised** measurements.\n"
          "2. Compare each clustering with the true species using the adjusted Rand index (ARI: 1 = perfect "
          "match, about 0 = random).\n"
          "3. Print a crosstab of species versus the scaled clusters.\n\n"
          "Why does scaling matter so much here? Which species get mixed up?",
   stub="from sklearn.cluster import KMeans\nfrom sklearn.metrics import adjusted_rand_score\n\n# your code here\n",
   hint1="Signal: clustering with features in different units (mm and grams). Pattern: k-means needs scaled "
         "features; evaluate against known labels with ARI.",
   hint2="1. `KMeans(...).fit_predict(X)`. 2. `StandardScaler().fit_transform(X)`. "
         "3. `adjusted_rand_score(true, pred)` ignores how clusters are numbered. 4. `pd.crosstab`.",
   solution=sol2,
   why="On raw data, `body_mass_g` (in grams, standard deviation about 800) dwarfs the millimetre columns "
       "(standard deviations of about 2 to 14), so k-means clusters almost only on weight: ARI 0.331. Adelie "
       "and Chinstrap weigh about the same, so weight cannot separate them. After standardising, every "
       "measurement counts equally, and bill length (long in Chinstrap, short in Adelie) can do its job: ARI "
       "0.793. Gentoo is found perfectly (123 of 123 in one cluster); the remaining confusion is 24 Adelie "
       "placed with the Chinstrap and 5 Chinstrap placed with the Adelie, two species that overlap in body "
       "shape. Real segmentation has no labels to check against, so you would judge clusters by stability "
       "and usefulness instead.",
   complexity="`O(n k d)` per iteration, 10 restarts: milliseconds for 342 rows.",
   mistakes="Using accuracy to compare clusters with labels (cluster numbers are arbitrary; use ARI or a "
            "crosstab). Forgetting `n_init` (one unlucky start can give a poor local optimum). Scaling with "
            "statistics from data you will later evaluate on, in a supervised setting.",
   learn=["ai-unsupervised", "ai-features-imbalance"])

sol3 = '''from sklearn.datasets import load_breast_cancer
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer()
X = data.data

pca_raw = PCA().fit(X)
top = data.feature_names[np.argmax(np.abs(pca_raw.components_[0]))]
print("unscaled: PC1 explains", round(pca_raw.explained_variance_ratio_[0], 3), "| biggest weight:", top)
# out: unscaled: PC1 explains 0.982 | biggest weight: worst area

pca = PCA().fit(StandardScaler().fit_transform(X))
cum = np.cumsum(pca.explained_variance_ratio_)
print("scaled: PC1", round(pca.explained_variance_ratio_[0], 3), " PC1+PC2", round(cum[1], 3))
print("components for 95% of variance:", int(np.searchsorted(cum, 0.95) + 1), "of", X.shape[1])
# out: scaled: PC1 0.443  PC1+PC2 0.632
# out: components for 95% of variance: 10 of 30'''
qc(ex, title="Thirty columns, how many directions?", minutes=6,
   prompt="Use the breast cancer data (30 features).\n\n"
          "1. Run PCA on the **raw** features. Print the share of variance explained by the first component and "
          "the feature with the largest absolute weight in it.\n"
          "2. Run PCA on **standardised** features. Print the share explained by PC1, by PC1 + PC2, and the "
          "number of components needed to keep 95% of the variance.\n\n"
          "What does the raw result really tell you? When would you use PCA before a model, and what do you lose?",
   stub="from sklearn.datasets import load_breast_cancer\nfrom sklearn.decomposition import PCA\n\n# your code here\n",
   hint1="Signal: many correlated numeric columns. Pattern: PCA (directions of maximum variance), which is "
         "scale-sensitive.",
   hint2="1. `PCA().fit(X)`; `explained_variance_ratio_`; `components_[0]` holds PC1's weights. 2. Scale "
         "first. 3. `np.cumsum` and the first index where it reaches 0.95.",
   solution=sol3,
   why="On raw data PC1 explains 98.2% of the variance, but that only says 'worst area' has by far the largest "
       "numbers (areas are in the hundreds to thousands, smoothness is around 0.1). PCA maximises variance, so "
       "unscaled it just finds the biggest unit. On standardised data PC1 explains 44.3% and the first two "
       "63.2%, and 10 of the 30 components keep 95% of the information, because the features are strongly "
       "correlated (radius, perimeter and area measure nearly the same thing). Use PCA before a model to "
       "remove collinearity, to speed up distance-based models, or to plot data in 2-D. You lose "
       "interpretability (each component mixes all features) and possibly signal: PCA ignores the target, so "
       "a low-variance direction can still be the predictive one.",
   complexity="PCA via SVD is `O(n d^2)` for `n > d`: instant for 569 x 30.",
   mistakes="Running PCA on unscaled data with mixed units. Fitting PCA on all data before a train/test split "
            "(fit it inside the pipeline). Explaining components as if they were original features.",
   learn=["ai-unsupervised"])

sol4 = '''def kmeans_step(X, centers):
    """One Lloyd iteration: assign each point to the nearest center, then move each center to its points' mean."""
    X, centers = np.asarray(X, dtype=float), np.asarray(centers, dtype=float)
    dist = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)   # (n, k) squared distances
    labels = dist.argmin(axis=1)
    new = centers.copy()                                               # an empty cluster keeps its center
    for j in range(len(centers)):
        if np.any(labels == j):
            new[j] = X[labels == j].mean(axis=0)
    return new'''
tests4 = '''pts = [[0, 0], [0, 2], [10, 0], [10, 2]]
check(kmeans_step, [
    ((pts, [[1, 1], [9, 1]]), [[0, 1], [10, 1]]),
    ((pts, [[0, 0], [0, 2]]), [[5, 0], [5, 2]]),            # a poor start: splits top/bottom instead of left/right
    ((pts, [[0, 1], [100, 100]]), [[5, 1], [100, 100]]),    # second center gets no points: it stays put
    (([[1], [2], [3], [10], [11]], [[0], [20]]), [[4], [11]]),   # 10 is equally far from 0 and 20: tie -> center 0
])'''
qc(ex, title="One step of the algorithm", minutes=6,
   prompt="Write `kmeans_step(X, centers)` with numpy: assign each row of X to its nearest center (squared "
          "Euclidean distance; on a tie, the lower index wins), then return the new centers, the mean of the points "
          "assigned to each. A center that gets no points stays where it is.\n\n"
          "Example: points `(0,0), (0,2), (10,0), (10,2)` and centers `(1,1), (9,1)` give `(0,1), (10,1)`.\n\n"
          "Look at the second test: what does it say about k-means and initialisation?",
   stub="def kmeans_step(X, centers):\n    # your code here\n    pass",
   tests=tests4,
   hint1="Signal: 'assign, then average'. Pattern: Lloyd's algorithm for k-means.",
   hint2="1. Distances with broadcasting: `X[:, None, :] - centers[None, :, :]`, square, sum over the last axis. "
         "2. `argmin(axis=1)` gives labels (ties go to the first). 3. For each j, mean of `X[labels == j]` if any.",
   solution=sol4,
   why="Both steps can only lower the inertia, which is why k-means converges. The second test starts with "
       "centers at `(0,0)` and `(0,2)`: the step splits the data into a bottom pair and a top pair, giving "
       "centers `(5,0)` and `(5,2)`. That is already a fixed point (another step changes nothing), with inertia "
       "100, while the natural left/right split has inertia 4. So k-means can get stuck in a bad local optimum; "
       "k-means++ initialisation and several restarts (`n_init`) are the cure.",
   complexity="`O(n k d)` time and `O(n k)` memory for the distance matrix per step.",
   mistakes="Taking the square root (not needed for argmin). Crashing on an empty cluster (mean of nothing is "
            "NaN). Looping over points in Python instead of broadcasting.",
   learn=["ai-unsupervised", "cheat-numpy"])

qc(ex, title="Prepare customers for clustering", minutes=3, kind="text", review=True,
   prompt="Marketing wants customer segments. Columns: `age`, `annual_income` (heavily right-skewed), "
          "`orders_last_year` (many zeros, a few heavy buyers), `country` (40 values), `signup_date`. What "
          "feature work do you do before k-means, and why?",
   hint1="Signal: distance-based method plus mixed, skewed, categorical features. Pattern: feature engineering "
         "for distances (transform, scale, encode).",
   hint2="Log-transform skewed money and count columns, turn dates into durations, handle the 40 countries "
         "(group or use regions), then standardise everything.",
   solution="**Model answer:** \"k-means uses Euclidean distance, so every feature must be numeric, on a "
            "comparable scale, and not dominated by a few extreme values.\n\n"
            "- `annual_income`: `log1p` (otherwise a few rich customers decide the clusters), then standardise.\n"
            "- `orders_last_year`: `log1p` or clip at a high percentile; maybe add a 0/1 'has ordered' flag.\n"
            "- `signup_date`: convert to tenure in months; a raw date is not a meaningful distance.\n"
            "- `country`: 40 one-hot columns would dominate the distance and make the clusters about geography. "
            "Group into regions or markets, or cluster within each market. If categorical data matters, use "
            "k-prototypes or Gower distance instead.\n"
            "- Standardise all numeric features; consider PCA if many are correlated.\n"
            "- Choose features by the business question (behaviour versus demographics), then check that the "
            "segments are stable across random seeds and samples and that they are explainable.\"",
   why="It reuses the day 9 lessons (skew, encoding, missing meaning) for a distance-based method, where scale "
       "decides everything.",
   mistakes="One-hot encoding 40 countries next to 3 numeric columns. Clustering raw income. Treating the "
            "signup date as a number.",
   learn=["ai-features-imbalance", "ai-unsupervised"])

ex.save()
