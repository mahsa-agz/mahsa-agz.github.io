import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_easy_common import start, qc

# Day 1 AI: focus ml-framing (no review yet).
ex = start(1, loads=["telco", "bank", "titanic"])

qc(ex, title="Turn a churn worry into an ML problem", minutes=5, kind="text",
   prompt="The head of a telecom company says: \"Too many customers leave. Can ML help?\"\n\n"
          "Frame it as an ML problem in about 90 seconds. Cover: the decision the model supports, the unit of "
          "prediction, the label (with a time window), the features you may use, the metric, the baseline, and how "
          "you would know it worked.",
   hint1="Signal: a vague business goal. Pattern: ML framing, start from the decision, not from the model.",
   hint2="1. Decision: who gets a retention offer this month. 2. Unit: one active customer at a snapshot date. "
         "3. Label: churned within the next 30 days after the snapshot. 4. Features: only what is known at the "
         "snapshot. 5. Offline metric (PR AUC, recall in the top 10%) and the business metric (saved revenue). "
         "6. Baseline: a simple rule. 7. A/B test the offer.",
   solution="**Model answer (about 90 s):**\n\n"
            "\"First I would ask what decision the model drives. Here: each month, which customers get a retention "
            "offer, given a budget for, say, 5% of customers. So the unit is one active customer on a snapshot date, "
            "and the label is 'cancels within the next 30 days'. That is binary classification, and what we really "
            "need is a good ranking, because we act on the top of the list.\n\n"
            "Features must be known at the snapshot date: tenure, contract type, monthly charges, services, support "
            "tickets, usage trends. Anything recorded after the snapshot, like a cancellation reason, is leakage.\n\n"
            "Churn is the minority class, so accuracy is useless. Offline I would use PR AUC and recall or precision "
            "in the top 5%. The baseline is a rule such as 'month-to-month contract and tenure under 6 months'; "
            "the model must beat it.\n\n"
            "Finally, a churn score is not the goal. Some customers leave whatever we do, and some stay anyway. "
            "I would run an A/B test: offer versus no offer among high-score customers, and measure retained "
            "revenue minus offer cost. Later, an uplift model can target the persuadable customers.\"\n\n"
            "**Key trade-off:** predicting churn is not the same as predicting who the offer will save.",
   why="Examiners test whether you start from the decision and the data available at prediction time. "
       "The label window, the leakage check, the baseline and the online test are the parts most candidates skip.",
   mistakes="Jumping to 'I would use XGBoost'. No time window in the label. Using accuracy. Forgetting that the "
            "offer has a cost and that a high churn score does not mean the offer works.",
   learn=["ai-ml-framing"])

sol2 = '''y = (telco["Churn"] == "Yes").astype(int)
print("customers:", len(telco))                         # out: customers: 7043
print("churn rate:", round(y.mean(), 3))                # out: churn rate: 0.265
print("majority-class accuracy:", round(1 - y.mean(), 3))  # out: majority-class accuracy: 0.735

rate = telco.groupby("Contract")["Churn"].apply(lambda s: (s == "Yes").mean()).round(3)
for contract, r in rate.items():
    print(contract, r)
# out: Month-to-month 0.427
# out: One year 0.113
# out: Two year 0.028'''
qc(ex, title="Know the target before you model", minutes=5,
   prompt="Use the `telco` table. Before any model:\n\n"
          "1. Print the number of customers and the churn rate (share of `Churn == \"Yes\"`, 3 decimals).\n"
          "2. Print the accuracy of a model that always predicts \"No churn\".\n"
          "3. Print the churn rate per `Contract` type.\n\n"
          "Then say in one sentence why a model with 80% accuracy may be weak here.",
   stub="# telco is loaded. Your code here\n",
   hint1="Signal: a classification task you have not seen yet. Pattern: check the base rate and the trivial "
         "baseline first.",
   hint2="1. `y = (telco['Churn'] == 'Yes').astype(int)`. 2. The mean of y is the churn rate. "
         "3. The always-No model is right for every non-churner, so its accuracy is `1 - churn rate`. "
         "4. `groupby('Contract')` and the mean of the 0/1 target.",
   solution=sol2,
   why="About 26.5% of customers churn, so predicting \"No\" for everyone already gives 73.5% accuracy. An 80% "
       "accurate model is only a little better than doing nothing. Contract type alone separates risk strongly "
       "(42.7% churn on month-to-month versus 2.8% on two-year), which gives a strong simple baseline rule.",
   mistakes="Reporting accuracy without the base rate. Taking the mean of the text column. Skipping the simple "
            "segment rates, which often give the best baseline and the first product insight.",
   learn=["ai-ml-framing", "ai-classification-metrics"])

sol3 = '''from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

y = (bank["y"] == "yes").astype(int)
X = bank.drop(columns="y")
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)

def test_auc(cols):
    cat = [c for c in cols if X[c].dtype == object]
    num = [c for c in cols if c not in cat]
    prep = ColumnTransformer([("num", StandardScaler(), num),
                              ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
    model = make_pipeline(prep, LogisticRegression(max_iter=1000))
    model.fit(X_tr[cols], y_tr)
    return roc_auc_score(y_te, model.predict_proba(X_te[cols])[:, 1])

all_cols = list(X.columns)
honest = [c for c in all_cols if c != "duration"]
print("AUC with duration:   ", round(test_auc(all_cols), 3))  # out: AUC with duration:    0.934
print("AUC without duration:", round(test_auc(honest), 3))    # out: AUC without duration: 0.786
print("AUC duration only:   ", round(test_auc(["duration"]), 3))  # out: AUC duration only:    0.83'''
qc(ex, title="The model that is too good", minutes=7,
   prompt="The marketing team wants to know **before a call** which clients are likely to subscribe, so the call "
          "center can call them first. A colleague trained a logistic regression on all columns of `bank` and "
          "reports a test ROC AUC of about 0.93.\n\n"
          "1. Read the column list. Which column cannot be used for this decision, and why?\n"
          "2. Show the effect: fit the same pipeline with all columns, without that column, and with that column "
          "alone. Print the three test AUCs (stratified 75/25 split, `random_state=0`).\n\n"
          "Pipeline: scale numeric columns, one-hot encode text columns, `LogisticRegression(max_iter=1000)`.",
   stub="# bank is loaded. Your code here\n",
   hint1="Signal: a suspiciously high score and a column that is only filled in after the event. Pattern: "
         "target leakage (feature not available at prediction time).",
   hint2="1. `duration` is the length of the call; it is known only after the call ends, and a 0-second call "
         "always means \"no\". 2. Write one function that builds the ColumnTransformer for a list of columns, fits "
         "on train and returns the test AUC. 3. Call it three times.",
   solution=sol3,
   why="`duration` is measured after the call, and long calls happen because the client is interested. It is a "
       "consequence of the outcome, not a cause known in advance. Alone it reaches 0.83 AUC, more than all the honest columns together, and it lifts the "
       "full model from 0.786 to 0.934. The honest number for a 'whom to call first' model is about 0.79. The UCI "
       "page itself says to drop `duration` for a realistic predictive model.",
   complexity="Logistic regression on about 31,000 rows and about 60 one-hot columns: around a second.",
   mistakes="Trusting a high score without asking 'when is each column known?'. Removing the column only from "
            "the test set. Forgetting other subtle leaks (for example a column updated after the outcome, or IDs "
            "that encode time).",
   learn=["ai-ml-framing", "ai-features-imbalance"],
   source=("UCI Bank Marketing dataset", "https://archive.ics.uci.edu/dataset/222/bank+marketing"))

qc(ex, title="Which kind of ML problem is it?", minutes=4, kind="text",
   prompt="For each request, name the ML task type, the label (if any) and one metric:\n\n"
          "1. Estimate how many minutes a food delivery will take.\n"
          "2. Flag card transactions that are fraud (about 0.1% are).\n"
          "3. Split our 2 million shoppers into a few groups for the marketing team.\n"
          "4. Order the 500 candidate videos for a user's feed.\n"
          "5. Forecast next week's daily orders per city.",
   hint1="Signal: different output types. Pattern: map the output (number, class, group, order, future value) to "
         "a task type.",
   hint2="Ask for each: is there a label? Is the output a number, a class, an ordering, or a future value of a "
         "time series? Then pick a metric that matches the cost of errors.",
   solution="| # | Task type | Label | Metric |\n|---|---|---|---|\n"
            "| 1 | Regression | actual delivery minutes | MAE (minutes are easy to explain); also check the share of "
            "late predictions |\n"
            "| 2 | Binary classification, very imbalanced (or anomaly detection if labels are scarce) | "
            "chargeback / confirmed fraud | PR AUC, recall at a fixed precision or at a review budget |\n"
            "| 3 | Unsupervised clustering | none | silhouette as a check, but mainly whether the groups are "
            "stable and actionable |\n"
            "| 4 | Ranking (learning to rank) | watch time, finish, like | NDCG@k or recall@k offline; "
            "watch time in an A/B test |\n"
            "| 5 | Time-series forecasting (regression over time) | future orders | MAPE or MAE per city, "
            "validated with a time-based split |\n\n"
            "**Say out loud:** the output type picks the family; the cost of each error picks the metric.",
   why="Naming the task type correctly in the first seconds tells the examiner you know which losses, metrics "
       "and validation schemes apply. Note the traps: fraud needs imbalance-aware metrics, forecasts need a time "
       "split, and ranking is judged on the top of the list.",
   mistakes="Calling the feed a classification problem and using accuracy. Using a random split for the forecast. "
            "Treating clustering quality as a single number.",
   learn=["ai-ml-framing", "ai-unsupervised"])

sol5 = '''from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

df = titanic[["survived", "sex", "pclass", "age", "fare"]].copy()
X_tr, X_te = train_test_split(df, test_size=0.3, stratify=df["survived"], random_state=1)

# 1. majority class: everybody dies
print("majority baseline:", round((X_te["survived"] == 0).mean(), 3))      # out: majority baseline: 0.616
# 2. one rule: women survive, men do not
rule = (X_te["sex"] == "female").astype(int)
print("rule 'women survive':", round((rule == X_te["survived"]).mean(), 3))  # out: rule 'women survive': 0.802

# 3. logistic regression; the age median comes from the TRAIN part only
med_age = X_tr["age"].median()
def features(d):
    return pd.DataFrame({"female": (d["sex"] == "female").astype(int), "pclass": d["pclass"],
                         "age": d["age"].fillna(med_age), "fare": d["fare"]})
lr = LogisticRegression(max_iter=1000).fit(features(X_tr), X_tr["survived"])
print("logistic regression:", round(lr.score(features(X_te), X_te["survived"]), 3))  # out: logistic regression: 0.772'''
qc(ex, title="Does the model beat a one-line rule?", minutes=6,
   prompt="Use `titanic`. Split it 70/30 (stratified on `survived`, `random_state=1`). On the test part, print the "
          "accuracy of:\n\n"
          "1. the majority class (everybody dies),\n"
          "2. the rule \"women survive, men do not\",\n"
          "3. a logistic regression on `sex` (as 0/1), `pclass`, `age` (fill missing with the train median) and "
          "`fare`.\n\n"
          "What would you tell a PM who wants a model?",
   stub="# titanic is loaded. Your code here\n",
   hint1="Signal: 'is ML worth it?'. Pattern: compare against trivial and rule-based baselines on the same test set.",
   hint2="1. `train_test_split(df, test_size=0.3, stratify=df['survived'], random_state=1)`. 2. Baseline accuracy "
         "is the share of zeros in the test labels. 3. The rule is `sex == 'female'`. 4. Fit the median on train, "
         "apply it to both parts, fit `LogisticRegression(max_iter=1000)`.",
   solution=sol5,
   why="Everybody-dies gives 0.616, the one-line rule gives 0.802, and the model gives 0.772: the model is "
       "**worse** than a rule you can explain in three words. Sex carries most of the signal; the model adds "
       "noisy linear effects of age and fare and has no sex-by-class interaction, so it flips some correct "
       "rule predictions. With 268 test passengers, 3 points is about 8 people, so one split cannot rank them "
       "reliably; use cross-validation before deciding. For the PM: ship the rule as the baseline, and build a "
       "model only if it beats the rule clearly in CV and the gain is worth the maintenance.",
   complexity="Tiny data: milliseconds.",
   mistakes="Filling missing age with the median of the full data (a small leak from test into train). "
            "Comparing models on different splits. Not reporting a baseline at all.",
   learn=["ai-ml-framing", "ai-logistic-regression"])

ex.save()
