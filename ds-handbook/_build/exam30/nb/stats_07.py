import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (Exam is created inside stats_common.start)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import start, Q

# Day 7 statistics: MOCK EXAM over days 1 to 6 (descriptive, probability, Bayes, distributions, CLT/SE, CIs),
# 5 questions, one of them a short case. One 30-minute timer for the whole notebook.
INTRO = ("**Mock exam rules.** Set one timer for **30 minutes** for the whole notebook. Work in order, but skip a "
         "question if you are stuck for more than 7 minutes. Do not open any Hint or Solution until the time is "
         "up. For every question write the number *and* the one-sentence answer for a PM: in the real exam "
         "the explanation is half of the score. After the timer: mark each question right, partly right or wrong, "
         "then read the solutions.")
ex = start(7, ["telco", "titanic"], intro=INTRO)

Q(ex, "The blank bills", minutes=5,
  prompt="In `telco`, the column `TotalCharges` should be numeric but pandas reads it as text.\n"
         "1. Convert it to numbers and print how many values fail to convert. What do those customers have in "
         "common?\n"
         "2. Decide how to fill them (drop, mean, or something else?) and justify it with the data.\n"
         "3. Print the mean and median of `TotalCharges` after your fix.",
  stub="# telco is loaded in the setup\n",
  hint1="Signal: a numeric column stored as text, with a few blanks. Topic: data cleaning before descriptive "
        "statistics; look at *who* the missing rows are before choosing a fill.",
  hint2="1. `tc = pd.to_numeric(telco.TotalCharges, errors='coerce')`. 2. `telco.loc[tc.isna(), 'tenure']`. "
        "3. Total charges are about `tenure x MonthlyCharges`, so tenure 0 means 0 charged so far. 4. Fill with "
        "0 and describe.",
  solution='''tc = pd.to_numeric(telco["TotalCharges"], errors="coerce")
bad = tc.isna()
print(f"failed to convert: {bad.sum()}   their tenure values: {sorted(telco.loc[bad, 'tenure'].unique().tolist())}")
print(f"raw text of one blank: {telco.loc[bad, 'TotalCharges'].iloc[0]!r}")
ratio = (tc / (telco["tenure"] * telco["MonthlyCharges"]))[~bad & (telco["tenure"] > 0)]
print(f"median of TotalCharges / (tenure x MonthlyCharges): {ratio.median():.3f}")
tc = tc.fillna(0)
print(f"after fill with 0: mean {tc.mean():.2f}   median {tc.median():.2f}")''',
  out="""failed to convert: 11   their tenure values: [0]
raw text of one blank: ' '
median of TotalCharges / (tenure x MonthlyCharges): 1.000
after fill with 0: mean 2279.73   median 1394.55""",
  why="All 11 failures are the text `' '` and all belong to customers with tenure 0, that is, customers who "
      "just signed up. Total charges track `tenure x MonthlyCharges` (median ratio about 1.0), so the correct "
      "value is 0, not missing at random. Filling with the mean (about 2,283) would invent two thousand "
      "dollars for brand-new customers; dropping them is acceptable for 11 of 7,043 rows but loses a real "
      "segment. The mean is far above the median because total charges grow with tenure and the tenure "
      "distribution is U-shaped (day 2).",
  pm="Eleven brand-new customers have no billing total yet, so we count them as zero. A typical customer has "
     "paid about 1,400 dollars in total, while the average is higher, about 2,280, because long-time "
     "customers have paid a lot.",
  mistakes="`astype(float)` crashing on the blanks, then dropping rows without looking at them. Mean "
           "imputation of a value that is structurally zero. Not checking a column's type before describing it.",
  learn=["stats-descriptive", "sql-dedup-cleaning"])

Q(ex, "Collect all six stickers", minutes=6,
  prompt="A classic. Each cereal box contains one of 6 stickers, each equally likely and independent.\n"
         "1. What is the expected number of boxes you must buy to collect all 6?\n"
         "2. Check with a simulation of 20,000 collectors (`rng = np.random.default_rng(0)`), and also print the "
         "median and the 90th percentile of the number of boxes.\n\n"
         "Product version: a game gives one of 6 random badges per day. How long until a typical player has them "
         "all?",
  hint1="Signal: 'expected number of tries until ...' with stages that get harder. Topic: geometric waiting "
        "times and linearity of expectation (the coupon collector problem).",
  hint2="1. When you already have k stickers, a new one arrives with probability `(6 - k) / 6`, so the wait for "
        "it is geometric with mean `6 / (6 - k)`. 2. Add the means for k = 0..5: `6 * (1 + 1/2 + ... + 1/6)`. "
        "3. Simulate with a loop that draws until the set has 6 items.",
  solution='''expected = sum(6 / (6 - k) for k in range(6))
print(f"expected boxes {expected:.2f}")

rng = np.random.default_rng(0)
counts = []
for _ in range(20_000):
    seen, boxes = set(), 0
    while len(seen) < 6:
        seen.add(int(rng.integers(6)))
        boxes += 1
    counts.append(boxes)
counts = np.array(counts)
print(f"simulated mean {counts.mean():.2f}   median {np.median(counts):.0f}   p90 {np.percentile(counts, 90):.0f}")''',
  out="""expected boxes 14.70
simulated mean 14.70   median 13   p90 23""",
  why="Split the wait into stages: the first sticker is immediate (1 box), the second takes on average 6/5 "
      "boxes, ... the last takes 6/1 = 6 boxes. Expectations add even though the stages are random, so the "
      "total is `6 x H(6) = 14.7`. The distribution is right skewed: the median is below the mean, and 10% of "
      "collectors need 23 or more boxes. For n items the expectation is about `n ln n`, so collections get "
      "expensive fast.",
  pm="On average a player needs about 15 days to collect all 6 badges, but 1 in 10 players needs 23 days or "
     "more, mostly waiting for the last badge. If we want most players to finish in two weeks, we should make "
     "missing badges more likely.",
  mistakes="Answering 6 (or 6 x 6 = 36). Forgetting that the last sticker alone takes 6 boxes on average. "
           "Reporting only the mean of a skewed waiting time.",
  learn=["stats-probability", "stats-distributions", "stats-probability-puzzles"])

Q(ex, "How good is the moderation model?", minutes=6,
  prompt="0.5% of posts on a platform break the rules. A moderation model catches 90% of bad posts (recall) and "
         "wrongly flags 2% of good posts.\n"
         "1. What share of flagged posts are really bad (the precision)?\n"
         "2. What false positive rate would the model need for precision to reach 50%, keeping recall at 90%?\n"
         "3. Check part 1 by simulating 2,000,000 posts (`rng = np.random.default_rng(0)`).",
  hint1="Signal: rare class plus a classifier, question asks about the flagged ones. Topic: Bayes' rule; "
        "precision is `P(bad | flagged)`.",
  hint2="1. `precision = 0.9 * 0.005 / (0.9 * 0.005 + 0.02 * 0.995)`. 2. Precision 50% means true positives = "
        "false positives: `0.9 * 0.005 = fpr * 0.995`. 3. Simulate like the fraud question on day 3.",
  solution='''prev, recall, fpr = 0.005, 0.90, 0.02
tp, fp = recall * prev, fpr * (1 - prev)
print(f"precision {tp / (tp + fp):.3f}")
print(f"FPR needed for 50% precision: {recall * prev / (1 - prev):.4f}")

rng = np.random.default_rng(0)
n = 2_000_000
bad = rng.random(n) < prev
flag = np.where(bad, rng.random(n) < recall, rng.random(n) < fpr)
print(f"simulated precision {bad[flag].mean():.3f}   flagged per 1000 posts {1000 * flag.mean():.1f}")''',
  out="""precision 0.184
FPR needed for 50% precision: 0.0045
simulated precision 0.183   flagged per 1000 posts 24.5""",
  why="Out of 1,000 posts, 5 are bad and 4.5 get flagged; 995 are good and 19.9 get flagged. So about 18% of "
      "flags are correct. With a rare class, precision is driven by the false positive rate on the huge good "
      "class: reaching 50% needs the FPR to fall from 2% to about 0.45%, more than 4 times lower. This is why "
      "moderation systems send flags to human review or use a second-stage model.",
  pm="Only about 1 in 5 posts the model flags is really breaking the rules, because good posts are 200 times "
     "more common. Auto-removing flags would hurt many good creators; we should route flags to review or cut "
     "the false alarm rate about 4 times.",
  mistakes="Saying precision is 90% (that is recall). Improving recall when the problem is the false positive "
           "rate. Forgetting that a 2% FPR on 99.5% of posts is a lot of posts.",
  learn=["stats-bayes", "ai-classification-metrics"])

Q(ex, "Survival by ticket class, with error bars", minutes=6,
  prompt="Using `titanic`:\n"
         "1. Print the survival rate and number of passengers for 1st and 3rd class.\n"
         "2. For each class, compute a 95% CI for the survival rate with the normal (Wald) formula and with the "
         "Wilson method (`from statsmodels.stats.proportion import proportion_confint`).\n"
         "3. Compute a 95% CI for the difference (1st minus 3rd). Is the gap clearly real?",
  stub="# titanic is loaded in the setup\nfrom statsmodels.stats.proportion import proportion_confint\n",
  hint1="Signal: a rate per group with 'how sure are we'. Topic: CI for a proportion (Wald vs Wilson) and for a "
        "difference of two proportions.",
  hint2="1. `k, n = survivors, passengers` per class. 2. Wald: `p +- 1.96 sqrt(p (1 - p) / n)`. Wilson: "
        "`proportion_confint(k, n, method='wilson')`. 3. Difference: `SE = sqrt(p1 q1 / n1 + p3 q3 / n3)`.",
  solution='''from statsmodels.stats.proportion import proportion_confint
g = titanic.groupby("pclass")["survived"].agg(["sum", "count"])
res = {}
for c in (1, 3):
    k, n = g.loc[c]
    p = k / n
    se = np.sqrt(p * (1 - p) / n)
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    res[c] = (p, n)
    print(f"class {c}: {p:.3f} (n={n})  Wald [{p - 1.96 * se:.3f}, {p + 1.96 * se:.3f}]  Wilson [{wl:.3f}, {wh:.3f}]")
(p1, n1), (p3, n3) = res[1], res[3]
d, se_d = p1 - p3, np.sqrt(p1 * (1 - p1) / n1 + p3 * (1 - p3) / n3)
print(f"difference {d:.3f}   95% CI [{d - 1.96 * se_d:.3f}, {d + 1.96 * se_d:.3f}]")''',
  out="""class 1: 0.630 (n=216)  Wald [0.565, 0.694]  Wilson [0.563, 0.691]
class 3: 0.242 (n=491)  Wald [0.204, 0.280]  Wilson [0.207, 0.282]
difference 0.387   95% CI [0.313, 0.462]""",
  why="With hundreds of passengers per class and rates away from 0 and 1, Wald and Wilson almost agree. Wilson "
      "is the safer default: Wald fails for small n or rates near 0 or 1 (it can even go below 0). The "
      "difference CI is far from 0, so the gap is not sampling noise. It is still not proof that the ticket "
      "*caused* survival: class is mixed up with sex, age and cabin location (confounding).",
  pm="About 63% of first-class passengers survived against 24% in third class; even allowing for chance, the "
     "gap is between about 31 and 46 points. Class was strongly linked to survival, partly because of where "
     "people were on the ship and who travelled in each class.",
  mistakes="Using Wald for a small group or a rate like 1 out of 40. Saying two CIs that overlap a little means "
           "'no difference' (compare with the CI of the difference instead). Reading a group difference as a "
           "causal effect.",
  learn=["stats-confidence-intervals", "stats-clt-se"])

Q(ex, "Case: the average went up, the median went down", minutes=7, kind="text",
  prompt="Short case. A video app shipped a new 'autoplay next episode' feature to all users on Monday. A week "
         "later the PM says: *'Average watch time per daily user rose from 52 to 56 minutes (+8%). Huge success!'* "
         "You check and see that the **median** watch time per daily user fell from 31 to 30 minutes, and the "
         "number of daily users is flat.\n\n"
         "In about 2 minutes (out loud or 6 to 8 sentences): how can both be true, what would you check, and "
         "would you call it a success?",
  hint1="Signal: mean and median move in opposite directions. Topic: descriptive statistics of a skewed metric "
        "(the tail moved), plus uncertainty and the lack of a control group.",
  hint2="1. A mean rises while the median falls when the top of the distribution grows and the middle shrinks a "
        "little. 2. Check the percentiles (p10, p50, p90, p99), heavy users, and 'idle' watch (autoplay running "
        "with nobody watching). 3. A before/after has no control: weekday effects, a new show, seasonality. "
        "4. Put a CI on the change; ask for an A/B test with guardrails.",
  solution='''**Model answer.**

1. **How both can be true.** Watch time is right skewed. The mean rises if the top tail grows, while the median falls if the typical user watches a bit less. Autoplay can do exactly this: it adds hours for people who leave the app running (binge sessions, falling asleep), while some typical users may stop earlier or be annoyed.
2. **What I would check first.** The percentiles before and after (p10, p25, p50, p75, p90, p99) and the share of users above, say, 4 hours a day; how much of the gain comes from autoplayed minutes with no interaction (a proxy for idle play); the change by segment (new versus existing users, platform, country).
3. **Is it real at all?** This is a before/after comparison with no control group, so a new popular show or a holiday week could explain it. A heavy-tailed mean is noisy, so I would put a bootstrap CI on the change in the mean and in the median.
4. **Decision.** Not a success yet. I would run a proper A/B test with a primary metric that is robust and meaningful (for example active watch time per user, or a capped mean, or retention), with guardrails such as user complaints, battery or data use, and next-week retention.''',
  why="Examiners use this case to check that you (1) know the mean is pulled by the tail, (2) look at the "
      "whole distribution, (3) question a before/after comparison without a control, and (4) translate the "
      "analysis into a decision and a next step. A structured answer (explain, check, uncertainty, decide) "
      "scores well even without numbers.",
  pm="The higher average comes from a small group watching much more, possibly with autoplay running while "
     "nobody watches, while the typical user watches slightly less. I would not call it a win until an A/B test "
     "shows that real, active watching and retention went up.",
  mistakes="Accepting the mean at face value. Explaining only the statistics without saying what to do next. "
           "Ignoring that before/after comparisons are confounded by time.",
  learn=["stats-descriptive", "stats-metric-drop", "stats-case-framework"])

ex.save()
