import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (Exam is created inside stats_common.start)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import start, Q

# Day 3 statistics: focus Bayes (base rates, posterior, updating). Review: probability (Q4).
ex = start(3, ["sms"])

Q(ex, "The fraud alert", minutes=7,
  prompt="A payments team has a fraud detector. 1% of transactions are fraud. The detector flags 95% of fraud "
         "(sensitivity) and wrongly flags 10% of good transactions (false positive rate, so specificity 90%).\n\n"
         "1. A transaction is flagged. What is the probability it is really fraud? Compute it with Bayes' rule.\n"
         "2. A second, independent detector with the same quality also flags it. Update the probability.\n"
         "3. Check part 1 with a simulation of 1,000,000 transactions (`rng = np.random.default_rng(0)`).\n\n"
         "This is the same maths as the classic 'positive medical test for a rare disease' question.",
  hint1="Signal: a rare event plus an imperfect test, and the question asks P(event | positive). Topic: Bayes' "
        "rule with a base rate: `P(F | +) = P(+ | F) P(F) / P(+)`.",
  hint2="1. `P(+) = 0.95 * 0.01 + 0.10 * 0.99` (true positives plus false positives). 2. Posterior = "
        "`0.95 * 0.01 / P(+)`. 3. For the second flag, use the first posterior as the new prior and repeat. "
        "4. Simulate: `fraud = rng.random(n) < 0.01`; `flag = np.where(fraud, rng.random(n) < 0.95, "
        "rng.random(n) < 0.10)`; answer = `fraud[flag].mean()`.",
  solution='''def posterior(prior, sens=0.95, fpr=0.10):
    return sens * prior / (sens * prior + fpr * (1 - prior))

p1 = posterior(0.01)
p2 = posterior(p1)                     # yesterday's posterior is today's prior
print(f"P(fraud | 1 flag)  = {p1:.4f}")
print(f"P(fraud | 2 flags) = {p2:.4f}")

rng = np.random.default_rng(0)
n = 1_000_000
fraud = rng.random(n) < 0.01
flag = np.where(fraud, rng.random(n) < 0.95, rng.random(n) < 0.10)
print(f"simulated P(fraud | flag) = {fraud[flag].mean():.4f}   flagged share = {flag.mean():.4f}")''',
  out="""P(fraud | 1 flag)  = 0.0876
P(fraud | 2 flags) = 0.4769
simulated P(fraud | flag) = 0.0877   flagged share = 0.1080""",
  why="Picture 10,000 transactions: 100 are fraud and 95 of them get flagged; 9,900 are good and 990 of them "
      "get flagged. So only 95 of 1,085 flags are fraud, about 8.8%. The false positives win because good "
      "transactions are 99 times more common. A second independent flag multiplies the odds by the same "
      "likelihood ratio again (`0.95 / 0.10 = 9.5`), which lifts the probability to about 48%. Odds form: "
      "posterior odds = prior odds x likelihood ratio, so `1/99 x 9.5 = 0.096` odds, which is 8.8%.",
  pm="Only about 9 in 100 flagged transactions are really fraud, because fraud is rare and the detector makes "
     "many false alarms. Blocking every flag would hurt about 10 good customers for each fraudster caught; "
     "a second check raises the hit rate to about 1 in 2.",
  mistakes="Answering 95% (that is `P(flag | fraud)`, not `P(fraud | flag)`). Forgetting the false positives in "
           "the denominator. Treating the two detectors as independent when they use the same features "
           "(then the second flag adds much less).",
  learn=["stats-bayes", "stats-probability"])

Q(ex, "Is it spam if it says FREE?", minutes=7,
  prompt="Using the real `sms` data, let `has_free` be 'the message contains the word *free*' (whole word, any "
         "case: `sms.text.str.contains(r'\\bfree\\b', case=False)`).\n"
         "1. Print `P(spam)`, `P(free | spam)` and `P(free | ham)`.\n"
         "2. Compute `P(spam | free)` with Bayes' rule from those three numbers, and check it by counting directly.\n"
         "3. A new product has an inbox where only 1% of messages are spam, and the words behave the same. What "
         "is `P(spam | free)` there?",
  stub="# sms is loaded in the setup\nhas_free = sms.text.str.contains(r'\\bfree\\b', case=False)\n",
  hint1="Signal: you know how often a word appears in each class and want the class given the word. Topic: "
        "Bayes' rule (the building block of the naive Bayes classifier).",
  hint2="1. `spam = sms.label == 'spam'`. 2. `P(free | spam) = has_free[spam].mean()`, same for ham. "
        "3. `P(spam | free) = P(free|spam) P(spam) / (P(free|spam) P(spam) + P(free|ham) P(ham))`. 4. Direct "
        "check: `spam[has_free].mean()`. 5. Part 3: same formula with prior 0.01.",
  solution='''spam = sms["label"] == "spam"
has_free = sms["text"].str.contains(r"\\bfree\\b", case=False)

def p_spam_given_free(prior, l_spam, l_ham):
    return l_spam * prior / (l_spam * prior + l_ham * (1 - prior))

p_spam, l_spam, l_ham = spam.mean(), has_free[spam].mean(), has_free[~spam].mean()
print(f"P(spam) {p_spam:.3f}  P(free|spam) {l_spam:.3f}  P(free|ham) {l_ham:.4f}")
print(f"Bayes P(spam|free) {p_spam_given_free(p_spam, l_spam, l_ham):.3f}   direct count {spam[has_free].mean():.3f}")
print(f"inbox with 1% spam: P(spam|free) {p_spam_given_free(0.01, l_spam, l_ham):.3f}")''',
  out="""P(spam) 0.134  P(free|spam) 0.228  P(free|ham) 0.0122
Bayes P(spam|free) 0.742   direct count 0.742
inbox with 1% spam: P(spam|free) 0.158""",
  why="Bayes' rule just reorganises the same counts, so it must match the direct count (0.742). The likelihood "
      "ratio `P(free | spam) / P(free | ham)` is about 19: 'free' is strong evidence. But the posterior also "
      "depends on the prior: with only 1% spam, the same word gives only about 16%. A classifier trained on one "
      "base rate is miscalibrated on another (you must re-weight the prior). Naive Bayes multiplies such "
      "likelihood ratios for many words, assuming the words are independent given the class.",
  pm="In this data, a text with the word 'free' is spam about 3 times out of 4. In an inbox where spam is rare "
     "(1%), the same word means spam only about 1 time in 6, so we should not auto-delete on that word alone.",
  mistakes="Using `str.contains('free')`, which also matches 'freedom' and 'carefree'. Reporting `P(free | spam)` "
           "(23%) as the answer. Reusing a probability from one population in another with a different base "
           "rate.",
  learn=["stats-bayes", "ai-nlp-basics"])

Q(ex, "Switch or stay?", minutes=6,
  prompt="A classic (Monty Hall). A prize is behind one of 3 doors. You pick door 1. The host, who knows where "
         "the prize is, always opens a door you did not pick that has no prize, and offers a switch.\n\n"
         "1. Use Bayes' rule to compute `P(prize behind door 1 | host opens door 3)` and the same for door 2.\n"
         "2. Simulate 100,000 games with `rng = np.random.default_rng(0)` and print the win rate of 'always stay' "
         "and 'always switch'.\n"
         "3. Why does the host's knowledge matter?",
  hint1="Signal: new information arrives that is not random (the host chooses). Topic: Bayes' rule with "
        "likelihoods `P(host opens 3 | prize at d)`.",
  hint2="1. Priors 1/3 each. 2. Likelihoods of 'host opens 3': prize at 1 -> 1/2 (host picks 2 or 3), prize at "
        "2 -> 1 (forced), prize at 3 -> 0. 3. Normalise. 4. Simulation: you pick door 0; staying wins when "
        "`prize == 0`; switching wins otherwise (the host removed the only other empty door).",
  solution='''prior = np.array([1, 1, 1]) / 3
lik = np.array([1 / 2, 1, 0])          # P(host opens door 3 | prize behind door 1, 2, 3)
post = prior * lik / (prior * lik).sum()
print("posterior for doors 1, 2, 3:", np.round(post, 3).tolist())

rng = np.random.default_rng(0)
prize = rng.integers(0, 3, size=100_000)    # you always pick door 0
stay = (prize == 0).mean()
print(f"stay wins {stay:.3f}   switch wins {1 - stay:.3f}")''',
  out="""posterior for doors 1, 2, 3: [0.333, 0.667, 0.0]
stay wins 0.332   switch wins 0.668""",
  why="Your first pick is right 1/3 of the time and the host cannot change that. When you are wrong (2/3 of the "
      "time) the host is forced to show the only other empty door, so switching wins exactly then. In Bayes "
      "terms, the host opening door 3 is twice as likely when the prize is behind door 2 (probability 1) as "
      "when it is behind door 1 (probability 1/2). If the host opened a random door and it happened to be "
      "empty, both remaining doors would be 1/2: the information depends on how the data was generated.",
  pm="Switching wins two times out of three. The lesson for product data is the same: what a signal means "
     "depends on how it was produced, so always ask who chose what we are looking at.",
  mistakes="Saying 50/50 because two doors are left. Ignoring the process that created the evidence (a "
           "selection effect, like surveying only users who chose to answer).",
  learn=["stats-bayes", "stats-probability-puzzles"])

Q(ex, "Twenty metrics, one winner", minutes=5, review=True,
  prompt="Review of probability. An A/B test has no real effect at all, but the dashboard shows 20 independent "
         "metrics, each tested at `alpha = 0.05`.\n"
         "1. What is the probability that at least one metric shows a 'significant' result? How many false "
         "positives do you expect?\n"
         "2. With the Bonferroni rule (test each metric at `0.05 / 20`), what is that probability now?\n"
         "3. Check part 1 with a simulation: under no effect a p-value is uniform on [0, 1], so draw "
         "100,000 x 20 uniform numbers.",
  hint1="Signal: 'at least one' across many independent tries. Topic: complement rule, then expected value of a "
        "count (binomial mean `n * p`).",
  hint2="1. `1 - 0.95**20`; expected false positives `20 * 0.05`. 2. `1 - (1 - 0.05/20)**20`. 3. "
        "`p = rng.random((100_000, 20))`; `(p < 0.05).any(axis=1).mean()`.",
  solution='''k, alpha = 20, 0.05
print(f"P(at least one false positive) {1 - (1 - alpha) ** k:.3f}   expected false positives {k * alpha:.1f}")
print(f"with Bonferroni: {1 - (1 - alpha / k) ** k:.4f}")
rng = np.random.default_rng(0)
p = rng.random((100_000, k))
print(f"simulated: {(p < alpha).any(axis=1).mean():.3f}")''',
  out="""P(at least one false positive) 0.642   expected false positives 1.0
with Bonferroni: 0.0488
simulated: 0.642""",
  why="Each metric alone has a 5% false alarm rate, but the chance that all 20 stay quiet is `0.95^20 = 0.358`, "
      "so 64% of null experiments show at least one 'winner'. Bonferroni divides alpha by the number of tests "
      "and brings the family-wise error back under 5% (it is conservative when metrics are correlated). In "
      "practice: pick one primary metric before the test, treat the other metrics as guardrails or exploration, "
      "and correct (Bonferroni or Benjamini-Hochberg) when you must test many.",
  pm="If we look at 20 metrics, there is about a 64% chance that one of them looks like a win purely by luck. "
     "We should decide the main metric before the test and treat surprise wins on other metrics as ideas to "
     "re-test, not as results.",
  mistakes="Saying 'each test has 5% error so the dashboard has 5% error'. Using `20 x 0.05 = 1` as a "
           "probability (it is an expected count). Choosing the primary metric after looking at the results.",
  learn=["stats-probability", "stats-ab-pitfalls"])

ex.save()
