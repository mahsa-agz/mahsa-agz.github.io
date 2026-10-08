import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (Exam is created inside stats_common.start)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import start, Q

# Day 2 statistics: focus probability (conditional probability, independence, complement rule, counting).
# Review: descriptive (Q4).
ex = start(2, ["titanic", "telco"])

Q(ex, "Who survived?", minutes=6,
  prompt="Using `titanic`, let S = 'survived' and F = 'female'.\n"
         "1. Print `P(S)`, `P(F)`, `P(S and F)`, `P(S | F)` and `P(F | S)`.\n"
         "2. Are S and F independent? Compare `P(S and F)` with `P(S) * P(F)`.\n"
         "3. Explain why `P(S | F)` and `P(F | S)` are different numbers.\n\n"
         "Example of the rule: if 30% of users are on iOS and 6% are iOS buyers, then "
         "`P(buy | iOS) = 0.06 / 0.30 = 0.20`.",
  stub="# titanic is loaded in the setup\n",
  hint1="Signal: 'given', 'among'. Topic: conditional probability `P(A | B) = P(A and B) / P(B)` and the "
        "independence check `P(A and B) = P(A) * P(B)`.",
  hint2="1. Make two boolean Series `s = titanic.survived == 1` and `f = titanic.sex == 'female'`. 2. The mean "
        "of a boolean Series is a probability: `s.mean()`, `(s & f).mean()`. 3. Divide to get the conditionals. "
        "4. Cross-check `P(S | F)` with `titanic.loc[f, 'survived'].mean()`.",
  solution='''s = titanic["survived"] == 1
f = titanic["sex"] == "female"
p_s, p_f, p_sf = s.mean(), f.mean(), (s & f).mean()
print(f"P(S) {p_s:.3f}  P(F) {p_f:.3f}  P(S and F) {p_sf:.3f}")
print(f"P(S|F) {p_sf / p_f:.3f}  P(F|S) {p_sf / p_s:.3f}")
print(f"P(S)*P(F) {p_s * p_f:.3f}  -> independent? {abs(p_sf - p_s * p_f) < 0.01}")
print(f"check: survival rate of women {titanic.loc[f, 'survived'].mean():.3f}")''',
  out="""P(S) 0.384  P(F) 0.352  P(S and F) 0.262
P(S|F) 0.742  P(F|S) 0.681
P(S)*P(F) 0.135  -> independent? False
check: survival rate of women 0.742""",
  why="`P(S | F)` divides by the number of women (survival rate among women, 74.2%). `P(F | S)` divides by the "
      "number of survivors (share of survivors who were women, 68.1%). Same joint count, different "
      "denominators. S and F are clearly dependent: `P(S and F)` is 0.262 but `P(S) * P(F)` is only 0.135, "
      "so being female almost doubled the joint probability compared with independence (the 'women and children "
      "first' rule). Mixing up the two conditionals is the 'prosecutor's fallacy' and a classic exam trap. "
      "With a sample this size the gap is far too big to be chance; a chi-square test (day 9) would make that "
      "formal.",
  pm="74% of women survived, against 38% of all passengers, so sex strongly predicted survival. Note the "
     "direction: 74% of women survived, while 68% of survivors were women; those are two different questions.",
  mistakes="Swapping `P(A | B)` and `P(B | A)`. Calling two events independent because they are 'unrelated in "
           "theory' without checking the product rule. Confusing independent with mutually exclusive (mutually "
           "exclusive events with positive probability are always dependent).",
  learn=["stats-probability", "stats-bayes"])

Q(ex, "The gambler's two bets", minutes=6,
  prompt="A classic (the Chevalier de Mere problem). Which bet is more likely to win?\n"
         "- Bet A: roll one die 4 times; you win if at least one 6 appears.\n"
         "- Bet B: roll two dice 24 times; you win if at least one double six appears.\n\n"
         "1. Compute both probabilities exactly on paper, then in code.\n"
         "2. Check with a simulation of 200,000 games each (`rng = np.random.default_rng(0)`).\n\n"
         "Exam follow-up: a feature fails on 1% of page loads. What is the chance a user who loads the "
         "page 50 times sees at least one failure?",
  hint1="Signal: 'at least one'. Topic: the complement rule `P(at least one) = 1 - P(none)`, with independent "
        "trials so `P(none) = (1 - p)^n`.",
  hint2="1. A: `1 - (5/6)**4`. 2. B: one roll of two dice is a double six with p = 1/36, so `1 - (35/36)**24`. "
        "3. Simulate: `rng.integers(1, 7, size=(200_000, 4))`, then `(x == 6).any(axis=1).mean()`. For B draw "
        "two arrays of shape (200_000, 24). 4. Follow-up: `1 - 0.99**50`.",
  solution='''rng = np.random.default_rng(0)
pa, pb = 1 - (5 / 6) ** 4, 1 - (35 / 36) ** 24
n = 200_000
sim_a = (rng.integers(1, 7, size=(n, 4)) == 6).any(axis=1).mean()
d1, d2 = rng.integers(1, 7, size=(n, 24)), rng.integers(1, 7, size=(n, 24))
sim_b = ((d1 == 6) & (d2 == 6)).any(axis=1).mean()
print(f"bet A exact {pa:.4f}  simulated {sim_a:.4f}")
print(f"bet B exact {pb:.4f}  simulated {sim_b:.4f}")
print(f"follow-up: P(at least one failure in 50 loads) = {1 - 0.99 ** 50:.3f}")''',
  out="""bet A exact 0.5177  simulated 0.5180
bet B exact 0.4914  simulated 0.4916
follow-up: P(at least one failure in 50 loads) = 0.395""",
  why="Counting the ways to get 'at least one' is messy (one 6, two 6s ...). The complement 'no 6 at all' is a "
      "single product because the rolls are independent. Bet A wins 51.8% of the time and bet B only 49.1%, "
      "even though both look like 'expected 2/3 successes' (4 x 1/6 = 24 x 1/36 = 2/3). The expected number of "
      "successes is not the probability of at least one. The simulation agrees to about 0.001, which is the "
      "size of the simulation error (`sqrt(0.25 / 200000)`, about 0.0011).",
  pm="A 1% failure rate per page load sounds small, but a user who loads the page 50 times has about a 40% "
     "chance of seeing at least one failure, so heavy users will notice it.",
  mistakes="Adding probabilities (4 x 1/6 = 0.67) instead of using the complement. Forgetting that the "
           "complement trick needs independent trials. Running a simulation without a seed (the numbers change "
           "every run).",
  learn=["stats-probability", "stats-probability-puzzles"])

Q(ex, "Shared birthdays", minutes=6,
  prompt="A classic. In a room of `n` people with birthdays spread evenly over 365 days (ignore 29 February):\n"
         "1. Compute exactly the probability that at least two people share a birthday, for n = 23 and n = 50.\n"
         "2. Find the smallest n where the probability is above 50%.\n"
         "3. Check n = 23 with a simulation of 100,000 rooms.\n\n"
         "Product follow-up: why does this matter when you give users random short IDs or coupon codes?",
  hint1="Signal: 'at least two share'. Topic: complement rule plus counting. P(all different) is a product of "
        "shrinking fractions.",
  hint2="1. `P(all different) = 365/365 * 364/365 * ... * (365 - n + 1)/365`, use `np.prod`. 2. Loop n from 1 up "
        "until `1 - P(all different) > 0.5`. 3. Simulation: `b = rng.integers(0, 365, size=(100_000, 23))`; a "
        "room has a match if the number of unique values in the row is below 23 (sort each row and check "
        "`(np.diff(np.sort(b, axis=1), axis=1) == 0).any(axis=1)`).",
  solution='''def p_shared(n):
    return 1 - np.prod((365 - np.arange(n)) / 365)

print(f"n=23: {p_shared(23):.4f}   n=50: {p_shared(50):.4f}")
n = 1
while p_shared(n) <= 0.5:
    n += 1
print("smallest n above 50%:", n)

rng = np.random.default_rng(0)
b = np.sort(rng.integers(0, 365, size=(100_000, 23)), axis=1)
print(f"simulated n=23: {(np.diff(b, axis=1) == 0).any(axis=1).mean():.4f}")''',
  out="""n=23: 0.5073   n=50: 0.9704
smallest n above 50%: 23
simulated n=23: 0.5070""",
  why="The number of *pairs* grows like `n * (n - 1) / 2`: 23 people form 253 pairs, and each pair matches with "
      "probability 1/365, so a match somewhere is likely. The exact answer uses the complement (all birthdays "
      "different) because 'at least one match' has many cases. Product link: with random IDs from `N` possible "
      "values, collisions become likely after about `sqrt(N)` IDs, not `N / 2`. A 6-digit code (1,000,000 "
      "values) has a 50% chance of a duplicate after only about 1,178 codes.",
  pm="With only 23 people there is already a 51% chance that two share a birthday. In the same way, random "
     "6-digit coupon codes start to collide after about a thousand codes, so we need longer codes or a "
     "uniqueness check.",
  mistakes="Comparing each person only with you (that gives `1 - (364/365)^22`, about 6%). Forgetting the "
           "complement. Assuming collisions need about half of all possible values.",
  learn=["stats-probability", "stats-probability-puzzles"])

Q(ex, "Who leaves the phone company?", minutes=6, review=True,
  prompt="Review of descriptive statistics. Using `telco`:\n"
         "1. Print the churn rate (share of `Churn == 'Yes'`).\n"
         "2. For churned and staying customers separately, print the mean, median, 25th and 75th percentile of "
         "`tenure` (months).\n"
         "3. Print how many customers have tenure 1 and tenure 72 (the maximum). What does the shape of the "
         "distribution look like?",
  stub="# telco is loaded in the setup\n",
  hint1="Signal: compare a numeric column across two groups. Topic: group-wise describe (center and spread) "
        "plus a look at the shape (piles at the edges).",
  hint2="1. `(telco.Churn == 'Yes').mean()`. 2. `telco.groupby('Churn').tenure.describe()` or `.agg([...])` "
        "with `lambda x: x.quantile(0.25)`. 3. `telco.tenure.value_counts()` for 1 and 72.",
  solution='''print(f"churn rate {(telco['Churn'] == 'Yes').mean():.3f}")
desc = telco.groupby("Churn")["tenure"].describe()[["mean", "25%", "50%", "75%"]].round(1)
print(desc.to_string())
vc = telco["tenure"].value_counts()
print(f"tenure 1: {vc[1]} customers   tenure 72: {vc[72]} customers   tenure 0: {vc[0]}")''',
  out="""churn rate 0.265
       mean   25%   50%   75%
Churn
No     37.6  15.0  38.0  61.0
Yes    18.0   2.0  10.0  29.0
tenure 1: 613 customers   tenure 72: 362 customers   tenure 0: 11""",
  why="Churned customers are new customers: half of them left within 10 months, while the median stayer has "
      "been there 38 months. The distribution of tenure is U-shaped: a pile at 1 month (new sign-ups, many "
      "about to leave) and a pile at 72 months (the data is capped at 6 years, so 72 means '72 or more'). A "
      "single mean (32 months overall) hides both piles, which is why you look at the distribution, not only "
      "the average. The 11 customers with tenure 0 are brand new and their `TotalCharges` is blank.",
  pm="About 27% of customers churned, and most of them were new: the typical churner left after 10 months, "
     "while the typical loyal customer has stayed 38 months. Retention work should focus on the first year.",
  mistakes="Reading 'mean tenure of churners = 18 months' as 'customers churn after 18 months' (the median is "
           "10 and the spread is huge). Missing the cap at 72. Ignoring the tenure 0 rows that later break "
           "`TotalCharges`.",
  learn=["stats-descriptive", "stats-product-metrics"])

ex.save()
