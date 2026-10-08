import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (Exam is created inside stats_common.start)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import start, Q

# Day 1 statistics: focus descriptive statistics (center, spread, skew, outliers, percentiles, correlation). No review.
ex = start(1, ["tips", "taxis", "cookie", "penguins"])

Q(ex, "What is a typical tip?", minutes=6,
  prompt="The restaurant owner asks: *what does a typical table spend, and what tip rate do people leave?*\n\n"
         "Using `tips`:\n"
         "1. Print the mean, median and standard deviation of `total_bill`, and its skewness.\n"
         "2. Make `tip_pct = 100 * tip / total_bill` and print its mean, median and maximum.\n"
         "3. Which single number would you report as the *typical* bill, and why?\n\n"
         "Example of the output shape: `bill mean 19.79 ...`.",
  stub="# tips is loaded in the setup\n",
  hint1="Signal: 'typical' value of a money column. Money is right skewed (a few big bills), so compare the mean "
        "and the median before you choose. Topic: center and skew.",
  hint2="1. `tips.total_bill.agg(['mean', 'median', 'std', 'skew'])`. 2. Compute tip_pct as a new Series "
        "(do not overwrite `tips`). 3. Mean > median and skew > 0 means a long right tail: report the median "
        "as typical and the mean when you need totals.",
  solution='''bill = tips["total_bill"]
print(f"bill mean {bill.mean():.2f}  median {bill.median():.2f}  sd {bill.std():.2f}  skew {bill.skew():.2f}")
tip_pct = 100 * tips["tip"] / tips["total_bill"]
print(f"tip% mean {tip_pct.mean():.2f}  median {tip_pct.median():.2f}  max {tip_pct.max():.2f}")
row = tips.loc[tip_pct.idxmax()]
print(f"max tip% row: bill {row.total_bill:.2f}, tip {row.tip:.2f}")''',
  out="""bill mean 19.79  median 17.80  sd 8.90  skew 1.13
tip% mean 16.08  median 15.48  max 71.03
max tip% row: bill 7.25, tip 5.15""",
  why="The mean is pulled up by a few large bills (skew 1.13 > 0, so mean 19.79 > median 17.80). The median is "
      "the bill of the 'middle' table and is robust to the tail, so it is the better *typical* value. The mean "
      "is still the right number for totals (revenue = mean x number of tables). The 71% tip is a $5.15 tip on "
      "a $7.25 bill: a ratio with a small denominator explodes, which is why the median tip rate (15.48%) is "
      "safer than the mean (16.08%). pandas `std()` uses `n - 1` (sample sd); numpy `np.std` uses `n` by default.",
  pm="A typical table spends about $17.80 (half spend less, half more) and leaves about 15.5% as a tip. The "
     "average bill is higher, $19.79, because a few large parties pull it up.",
  mistakes="Reporting only the mean for a skewed money metric. Averaging ratios without looking at tiny "
           "denominators. Mixing `np.std` (divides by n) with `pandas.std` (divides by n - 1).",
  learn=["stats-descriptive", "cheat-pandas"])

Q(ex, "How expensive is a taxi ride?", minutes=6,
  prompt="A ride-hailing PM wants one slide on taxi fares. Using `taxis.fare`:\n"
         "1. Print the 50th, 90th and 99th percentiles and the IQR (Q3 minus Q1).\n"
         "2. Flag outliers with the 1.5 x IQR rule (above `Q3 + 1.5 * IQR`). Print the cut-off and the share of "
         "trips above it.\n"
         "3. Should the flagged trips be deleted before analysis? Answer in one sentence.\n\n"
         "Example: if Q1 = 4 and Q3 = 10, the IQR is 6 and the upper fence is 19.",
  stub="# taxis is loaded in the setup\n",
  hint1="Signal: 'one slide' on a long-tailed price. Report percentiles (p50, p90, p99), not mean +- sd. "
        "Topic: percentiles, IQR and outlier rules.",
  hint2="1. `q = taxis.fare.quantile([0.25, 0.5, 0.75, 0.9, 0.99])`. 2. `iqr = q[0.75] - q[0.25]`, "
        "`fence = q[0.75] + 1.5 * iqr`. 3. `(taxis.fare > fence).mean()` is the share. 4. Look at what the "
        "flagged trips are (long distance, airports) before you call them errors.",
  solution='''fare = taxis["fare"]
q = fare.quantile([0.25, 0.5, 0.75, 0.9, 0.99])
iqr = q[0.75] - q[0.25]
fence = q[0.75] + 1.5 * iqr
print(f"p50 {q[0.5]:.2f}  p90 {q[0.9]:.2f}  p99 {q[0.99]:.2f}  IQR {iqr:.2f}")
print(f"upper fence {fence:.2f}  share above {(fare > fence).mean():.3f}")
print(f"median distance (miles): flagged {taxis.loc[fare > fence, 'distance'].median():.2f}, "
      f"others {taxis.loc[fare <= fence, 'distance'].median():.2f}")''',
  out="""p50 9.50  p90 26.00  p99 52.00  IQR 8.50
upper fence 27.75  share above 0.092
median distance (miles): flagged 11.41, others 1.50""",
  why="Fares are bounded below and have a long right tail, so percentiles describe them better than the mean "
      "and sd. The 1.5 x IQR rule is a quick screen, not a verdict: the flagged trips are much longer, so they "
      "are real long rides (airports, outer boroughs), not data errors. Delete only impossible values (negative "
      "fares, zero distance with a huge fare); keep real extremes and use robust statistics or a log scale.",
  pm="Half of the rides cost $9.50 or less, 9 in 10 cost $26 or less, and only 1 in 100 costs more than "
     "$52. About 9% of rides are long trips (median 11.4 miles) that cost far more; they are a real segment, "
     "not bad data.",
  mistakes="Deleting every point outside the fence (you lose the airport business). Using mean +- 3 sd on a "
           "skewed metric. Forgetting that pandas `quantile` interpolates between values by default.",
  learn=["stats-descriptive"])

Q(ex, "One player, 49,854 rounds", minutes=6,
  prompt="In the Cookie Cats data, `sum_gamerounds` is the number of rounds a player played in the first week.\n\n"
         "1. Print the mean, median, standard deviation and maximum, and the share of players with 0 rounds.\n"
         "2. Remove only the single player with the maximum and print the mean and sd again.\n"
         "3. Which statistic changed a lot, which barely changed, and why?\n\n"
         "Example: for the values 1, 2, 3, 1000 the mean is 251.5 but the median is 2.5.",
  stub="# cookie is loaded in the setup\n",
  hint1="Signal: an engagement count with a huge maximum. Compare a non-robust statistic (mean, sd) with a "
        "robust one (median) before and after removing one point. Topic: robustness and outliers.",
  hint2="1. `g = cookie.sum_gamerounds`; print `g.mean(), g.median(), g.std(), g.max(), (g == 0).mean()`. "
        "2. `h = g[g < g.max()]` drops the one top player (check it is only one). 3. Compare.",
  solution='''g = cookie["sum_gamerounds"]
print(f"mean {g.mean():.2f}  median {g.median():.0f}  sd {g.std():.1f}  max {g.max()}  zero share {(g == 0).mean():.3f}")
h = g[g < g.max()]                       # drops exactly one player
print(f"rows removed {len(g) - len(h)}")
print(f"without max: mean {h.mean():.2f}  median {h.median():.0f}  sd {h.std():.1f}  max {h.max()}")''',
  out="""mean 51.87  median 16  sd 195.1  max 49854  zero share 0.044
rows removed 1
without max: mean 51.32  median 16  sd 102.7  max 2961""",
  why="The sd squares the distances from the mean, so one player at 49,854 rounds (about 5 rounds a minute, "
      "around the clock for a whole week, so likely a bot or a logging bug) dominates it: removing 1 of 90,189 rows "
      "nearly halves the sd. The mean moves only a little and the median does not move at all. In an A/B test "
      "this matters: a huge sd makes the t-test weak, and one extreme user can flip the sign of a mean "
      "difference. Fixes: investigate and remove clear errors, cap (winsorize) at a high percentile such as p99, "
      "or compare medians or use a log scale.",
  pm="A typical player played 16 rounds in the first week, and 4.4% never played at all. The average (about 52) "
     "is three times the typical value because a few heavy players pull it up, and one account with 49,854 "
     "rounds looks like a bot, so we report the median and clean that account before any A/B comparison.",
  mistakes="Quoting the mean and sd of a heavy-tailed metric without checking the maximum. Removing outliers "
           "with a rule chosen after seeing the A/B result (that is p-hacking). Forgetting the 4.4% of players "
           "who never played a round.",
  learn=["stats-descriptive", "stats-ab-pitfalls"])

Q(ex, "Longer bills, shallower bills?", minutes=7,
  prompt="A biologist plots `bill_length_mm` against `bill_depth_mm` for all `penguins` and says: *longer bills "
         "are shallower, the correlation is negative.*\n\n"
         "1. Print the Pearson correlation for all penguins together (drop rows with missing values).\n"
         "2. Print it again inside each species.\n"
         "3. Explain the difference in one sentence. What is this effect called?",
  stub="# penguins is loaded in the setup\n",
  hint1="Signal: one overall number versus the same number inside groups. Topic: correlation and a lurking "
        "grouping variable (Simpson's paradox).",
  hint2="1. `d = penguins.dropna(subset=['bill_length_mm', 'bill_depth_mm'])`. 2. "
        "`d.bill_length_mm.corr(d.bill_depth_mm)`. 3. Loop over `d.groupby('species')` and compute the same "
        "correlation per group.",
  solution='''d = penguins.dropna(subset=["bill_length_mm", "bill_depth_mm"])
print(f"all penguins: r = {d.bill_length_mm.corr(d.bill_depth_mm):.3f}  (n = {len(d)})")
for sp, grp in d.groupby("species"):
    print(f"{sp:<10} r = {grp.bill_length_mm.corr(grp.bill_depth_mm):.3f}  (n = {len(grp)})")
print(d.groupby("species")[["bill_length_mm", "bill_depth_mm"]].mean().round(1).to_string())''',
  out="""all penguins: r = -0.235  (n = 342)
Adelie     r = 0.391  (n = 151)
Chinstrap  r = 0.654  (n = 68)
Gentoo     r = 0.643  (n = 123)
           bill_length_mm  bill_depth_mm
species
Adelie               38.8           18.3
Chinstrap            48.8           18.4
Gentoo               47.5           15.0""",
  why="Inside every species, longer bills are also deeper (r about +0.4 to +0.65). Overall the sign flips to "
      "-0.235 because the species sit in different corners: Gentoo have long but shallow bills, Adelie short "
      "but deep bills. Pooling groups with different averages creates a trend that no group has. This is "
      "Simpson's paradox. Product version: a metric can rise in every country and still fall overall when the "
      "traffic mix shifts toward a low-metric country. Always ask 'is there a grouping variable?' before you "
      "trust a pooled correlation or a pooled rate.",
  pm="Within each species, penguins with longer bills also have deeper bills. The overall negative number is an "
     "artefact of mixing three species with different bill shapes, so we should report the per-species "
     "relationship.",
  mistakes="Reading a pooled correlation as a within-group relationship. Treating correlation as causation. "
           "Forgetting that Pearson r measures only linear association and is sensitive to outliers "
           "(Spearman is the rank-based, robust version).",
  learn=["stats-descriptive", "stats-metric-drop"])

ex.save()
