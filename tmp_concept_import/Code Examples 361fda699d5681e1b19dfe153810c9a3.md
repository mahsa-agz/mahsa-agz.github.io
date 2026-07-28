# Code Examples

# Python Code Examples for Missing Data

## 1. Load data

```python
import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")

df.head()
```

---

## 2. Count missing values by variable

```python
missing_count = df.isna().sum()
missing_percent = df.isna().mean() * 100

missing_summary = pd.DataFrame({
    "missing_count": missing_count,
    "missing_percent": missing_percent
}).sort_values("missing_percent", ascending=False)

print(missing_summary)
```

---

## 3. Count complete and incomplete rows

```python
n_rows = len(df)

complete_rows = df.dropna().shape[0]
incomplete_rows = n_rows - complete_rows

print("Total rows:", n_rows)
print("Complete rows:", complete_rows)
print("Incomplete rows:", incomplete_rows)
print("Percent incomplete:", incomplete_rows / n_rows * 100)
```

---

## 4. Visualize missing data by variable

```python
import matplotlib.pyplot as plt

missing_percent = df.isna().mean().sort_values(ascending=False) * 100

plt.figure(figsize=(10, 5))
missing_percent.plot(kind="bar")
plt.ylabel("Missing data (%)")
plt.title("Percentage of Missing Data by Variable")
plt.tight_layout()
plt.show()
```

---

## 5. Visualize missing-data pattern

```python
plt.figure(figsize=(12, 6))
plt.imshow(df.isna(), aspect="auto")
plt.xlabel("Variables")
plt.ylabel("Rows")
plt.title("Missing-Data Pattern")
plt.xticks(range(len(df.columns)), df.columns, rotation=90)
plt.tight_layout()
plt.show()
```

---

## 6. Missing data by group

Example: missing reaction-time data by experimental condition.

```python
df["reaction_time_missing"] = df["reaction_time"].isna().astype(int)

missing_by_condition = (
    df.groupby("condition")["reaction_time_missing"]
    .mean()
    .mul(100)
)

print(missing_by_condition)
```

---

## 7. Create missing-data indicators

```python
for col in df.columns:
    if df[col].isna().any():
        df[col + "_missing"] = df[col].isna().astype(int)
```

Example for selected variables:

```python
key_vars = ["reaction_time", "workload", "accuracy"]

for var in key_vars:
    df[var + "_missing"] = df[var].isna().astype(int)
```

---

## 8. Complete-case analysis

```python
analysis_vars = ["reaction_time", "workload", "age", "condition"]

df_complete = df.dropna(subset=analysis_vars)

print("Original sample size:", len(df))
print("Complete-case sample size:", len(df_complete))
print("Rows removed:", len(df) - len(df_complete))
```

---

## 9. Drop variables with too much missing data

Example: remove variables with more than 40% missing data.

```python
threshold = 0.40

cols_to_keep = df.columns[df.isna().mean() <= threshold]

df_reduced = df[cols_to_keep]

print("Original number of columns:", df.shape[1])
print("Reduced number of columns:", df_reduced.shape[1])
```

---

## 10. Mean imputation for numeric variables

```python
from sklearn.impute import SimpleImputer

numeric_cols = df.select_dtypes(include=["number"]).columns

mean_imputer = SimpleImputer(strategy="mean")

df_mean = df.copy()
df_mean[numeric_cols] = mean_imputer.fit_transform(df[numeric_cols])
```

---

## 11. Median imputation for numeric variables

```python
from sklearn.impute import SimpleImputer

numeric_cols = df.select_dtypes(include=["number"]).columns

median_imputer = SimpleImputer(strategy="median")

df_median = df.copy()
df_median[numeric_cols] = median_imputer.fit_transform(df[numeric_cols])
```

---

## 12. Mode imputation for categorical variables

```python
from sklearn.impute import SimpleImputer

categorical_cols = df.select_dtypes(include=["object", "category"]).columns

mode_imputer = SimpleImputer(strategy="most_frequent")

df_mode = df.copy()
df_mode[categorical_cols] = mode_imputer.fit_transform(df[categorical_cols])
```

---

## 13. Constant-value imputation

```python
df_constant = df.copy()

df_constant["education_level"] = df_constant["education_level"].fillna("Unknown")
```

For numeric data:

```python
df_constant["number_of_errors"] = df_constant["number_of_errors"].fillna(0)
```

Use this only when the constant has a defensible meaning.

---

## 14. Multiple-imputation-style method using IterativeImputer

`IterativeImputer` is similar to MICE, although it is not a full replacement for formal multiple imputation with pooled estimates.

```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

numeric_cols = df.select_dtypes(include=["number"]).columns

imputer = IterativeImputer(
    max_iter=10,
    random_state=42
)

df_iterative = df.copy()

df_iterative[numeric_cols] = imputer.fit_transform(df[numeric_cols])
```

---

## 15. KNN imputation

```python
from sklearn.impute import KNNImputer

numeric_cols = df.select_dtypes(include=["number"]).columns

knn_imputer = KNNImputer(n_neighbors=5)

df_knn = df.copy()

df_knn[numeric_cols] = knn_imputer.fit_transform(df[numeric_cols])
```

---

## 16. KNN imputation with scaling

KNN imputation is sensitive to variable scale.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer

numeric_cols = df.select_dtypes(include=["number"]).columns

knn_pipeline = Pipeline(steps=[
    ("scaler", StandardScaler()),
    ("imputer", KNNImputer(n_neighbors=5))
])

df_knn_scaled = df.copy()

df_knn_scaled[numeric_cols] = knn_pipeline.fit_transform(df[numeric_cols])
```

---

## 17. Check whether missingness is associated with observed variables

Example: model whether reaction time is missing.

```python
import statsmodels.api as sm
import pandas as pd

df_check = df.copy()

df_check["reaction_time_missing"] = df_check["reaction_time"].isna().astype(int)

predictors = ["age", "condition", "workload", "trial_number"]

df_model = df_check[predictors + ["reaction_time_missing"]].copy()

df_model = pd.get_dummies(df_model, columns=["condition"], drop_first=True)

df_model = df_model.dropna()

X = df_model.drop(columns=["reaction_time_missing"])
y = df_model["reaction_time_missing"]

X = sm.add_constant(X)

missingness_model = sm.Logit(y, X).fit()

print(missingness_model.summary())
```

Interpretation:

```
If observed variables predict whether a value is missing, MCAR is unlikely.
If missingness depends only on observed variables, MAR may be plausible.
If missingness depends on the unobserved missing value itself, MNAR may be possible.
```

---

## 18. Complete-case regression

```python
import statsmodels.formula.api as smf

df_complete = df.dropna(
    subset=["reaction_time", "workload", "age", "condition"]
)

model_complete = smf.ols(
    "reaction_time ~ workload + age + condition",
    data=df_complete
).fit()

print(model_complete.summary())
```

---

## 19. Regression after iterative imputation

```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import statsmodels.api as sm
import pandas as pd

analysis_vars = ["reaction_time", "workload", "age", "condition"]

df_analysis = df[analysis_vars].copy()

df_encoded = pd.get_dummies(
    df_analysis,
    columns=["condition"],
    drop_first=True
)

imputer = IterativeImputer(
    max_iter=10,
    random_state=42
)

df_imputed = pd.DataFrame(
    imputer.fit_transform(df_encoded),
    columns=df_encoded.columns
)

X = df_imputed.drop(columns=["reaction_time"])
y = df_imputed["reaction_time"]

X = sm.add_constant(X)

model_imputed = sm.OLS(y, X).fit()

print(model_imputed.summary())
```

---

## 20. Compare complete-case and imputed results

```python
comparison = pd.DataFrame({
    "complete_case": model_complete.params,
    "imputed": model_imputed.params
})

print(comparison)
```

Interpretation:

```
If coefficients are similar, results may be robust.
If coefficients differ substantially, missing data may affect the conclusion.
```

---

## 21. Machine-learning pipeline with imputation

This avoids data leakage.

```python
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

X = df.drop(columns=["outcome"])
y = df["outcome"]

numeric_cols = X.select_dtypes(include=["number"]).columns
categorical_cols = X.select_dtypes(include=["object", "category"]).columns

numeric_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median"))
])

categorical_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_pipeline, numeric_cols),
    ("cat", categorical_pipeline, categorical_cols)
])

model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(random_state=42))
])

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

model.fit(X_train, y_train)

print("Test accuracy:", model.score(X_test, y_test))
```

Important:

```
The imputer is fitted only on the training data.
The test data are transformed using the imputer learned from the training data.
This avoids data leakage.
```

---

## 22. Cross-validation with imputation inside the pipeline

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(
    model,
    X,
    y,
    cv=5,
    scoring="accuracy"
)

print("Cross-validation scores:", scores)
print("Mean accuracy:", scores.mean())
print("Standard deviation:", scores.std())
```

Because imputation is inside the pipeline, it is repeated properly within each cross-validation fold.

---

## 23. Time-series interpolation

Use only for short gaps where interpolation is theoretically defensible.

```python
df = df.sort_values("timestamp")

df["heart_rate_interpolated"] = df["heart_rate"].interpolate(
    method="linear",
    limit=3
)
```

For time-indexed data:

```python
df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.set_index("timestamp").sort_index()

df["sensor_value_interpolated"] = df["sensor_value"].interpolate(
    method="time",
    limit=3
)
```

Interpretation:

```
limit=3 means that only gaps of up to three consecutive missing values are interpolated.
Longer gaps remain missing.
```

---

## 24. Human-factors example: reaction-time missing data

```python
import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv("experiment_data.csv")

df["rt_missing"] = df["reaction_time"].isna().astype(int)

missing_by_condition = (
    df.groupby("condition")["rt_missing"]
    .mean()
    .mul(100)
)

print(missing_by_condition)
```

Model the probability that reaction time is missing:

```python
missing_model = smf.logit(
    "rt_missing ~ condition + workload + trial_number",
    data=df
).fit()

print(missing_model.summary())
```

Analyze complete cases:

```python
df_complete = df.dropna(
    subset=["reaction_time", "condition", "workload", "trial_number"]
)

rt_model = smf.ols(
    "reaction_time ~ condition + workload + trial_number",
    data=df_complete
).fit()

print(rt_model.summary())
```

---

## 25. Sensitivity analysis template

```python
results = {}

# Complete-case analysis
df_complete = df.dropna(
    subset=["reaction_time", "workload", "age", "condition"]
)

model_complete = smf.ols(
    "reaction_time ~ workload + age + condition",
    data=df_complete
).fit()

results["complete_case"] = model_complete.params

# Median imputation
df_median = df.copy()

numeric_cols = ["reaction_time", "workload", "age"]

median_imputer = SimpleImputer(strategy="median")

df_median[numeric_cols] = median_imputer.fit_transform(df_median[numeric_cols])

model_median = smf.ols(
    "reaction_time ~ workload + age + condition",
    data=df_median
).fit()

results["median_imputation"] = model_median.params

# Compare coefficients
comparison = pd.DataFrame(results)

print(comparison)
```

---

## 26. Recommended code workflow

```python
# 1. Summarize missing data
missing_summary = pd.DataFrame({
    "missing_count": df.isna().sum(),
    "missing_percent": df.isna().mean() * 100
}).sort_values("missing_percent", ascending=False)

print(missing_summary)

# 2. Create missing indicators for important variables
key_vars = ["reaction_time", "workload", "accuracy"]

for var in key_vars:
    df[var + "_missing"] = df[var].isna().astype(int)

# 3. Check missing data by condition
for var in key_vars:
    print(df.groupby("condition")[var + "_missing"].mean() * 100)

# 4. Conduct complete-case analysis
analysis_vars = ["reaction_time", "workload", "age", "condition"]

df_complete = df.dropna(subset=analysis_vars)

# 5. Conduct imputed analysis
# Choose imputation method depending on the research goal.

# 6. Compare results
# If results differ, report that missing data influence the conclusion.
```