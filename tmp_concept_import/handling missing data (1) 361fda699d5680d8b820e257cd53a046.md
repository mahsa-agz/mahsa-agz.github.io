# handling missing data (1)

Category: Feature Engineering and Data Preparation

Code Examples: 

[Code Examples](Code%20Examples%20361fda699d5681e1b19dfe153810c9a3.md)

```markdown
# Page 1 — Missing Data: Concepts, Rules of Thumb, and Imputation Methods

## 1. What is missing data?

**Missing data** refers to values that should have been observed or recorded but are absent from the dataset.

In formal writing, especially for journal articles, it is usually better to say:

| Casual term           | Formal term                                    |
| --------------------- | ---------------------------------------------- |
| missingness           | missing data                                   |
| missingness rate      | proportion of missing data                     |
| missingness pattern   | pattern of missing data                        |
| missing values        | missing observations / incomplete observations |
| handling missingness  | addressing missing data                        |
| missingness mechanism | missing-data mechanism                         |

Example journal-style sentence:

> The extent and pattern of missing data were examined before analysis.

## 2. Why missing data matter

Missing data are not only a technical problem. They can affect:

* statistical power
* parameter estimates
* standard errors
* p-values
* confidence intervals
* model performance
* generalizability
* validity of conclusions

A dataset with missing values can still be usable, but the method used to address missing data must match the **reason the data are missing**.

## 3. Main types of missing-data mechanisms

The most important question is:

> Why are the data missing?

There are three classic missing-data mechanisms.

## 3.1 MCAR: Missing Completely at Random

Data are **missing completely at random** when the probability of missingness is unrelated to both observed and unobserved data.

### Example

A sensor randomly fails for 2% of trials because of a temporary software error.

The failure is unrelated to:

* participant characteristics
* experimental condition
* task difficulty
* outcome value

### Implication

MCAR is the least problematic mechanism.

If missing data are MCAR and the missing proportion is small, complete-case analysis may be acceptable.

### Example sentence

> Missing data were assumed to be missing completely at random because missingness was not associated with observed participant characteristics or experimental conditions.

## 3.2 MAR: Missing at Random

Data are **missing at random** when the probability of missingness depends on observed variables, but not on the missing value itself after accounting for those observed variables.

### Example

Older participants are less likely to answer a workload questionnaire, but within each age group, missingness is unrelated to their actual workload score.

Here, missingness depends on an observed variable: age.

### Implication

MAR is common in real research.

Appropriate methods include:

* multiple imputation
* maximum likelihood estimation
* mixed-effects models
* inverse probability weighting

### Example sentence

> Missing data were addressed under a missing-at-random assumption using multiple imputation.

## 3.3 MNAR: Missing Not at Random

Data are **missing not at random** when the probability of missingness depends on the missing value itself.

### Example

Participants with very high stress are less likely to report their stress level.

The missing value itself influences the probability that it is missing.

### Implication

MNAR is the most difficult case.

Standard imputation methods may be biased unless the missing-data mechanism is modeled explicitly.

Possible approaches include:

* sensitivity analysis
* selection models
* pattern-mixture models
* joint models
* external validation data
* transparent discussion of limitations

### Example sentence

> Because missingness may have depended on unobserved values, sensitivity analyses were conducted to evaluate the robustness of the findings.

# 4. General workflow for handling missing data

A good missing-data workflow is:

## Step 1: Quantify missing data

Ask:

* How many values are missing?
* Which variables have missing data?
* Which participants, cases, or trials have missing data?
* Is the missing data concentrated in specific variables?

Useful summaries:

* number of missing values per variable
* percentage of missing values per variable
* number of incomplete cases
* percentage of complete cases

## Step 2: Examine missing-data patterns

Ask:

* Are missing values randomly scattered?
* Do they cluster by group, condition, participant, time point, site, device, or trial type?
* Are missing values more common in specific experimental conditions?
* Are missing values associated with observed variables?

Example:

> In a human-factors experiment, reaction-time data may be missing more often in a high-workload condition.

That would suggest missing data are not completely random.

## Step 3: Consider the missing-data mechanism

Classify the likely mechanism:

| Mechanism | Meaning                                              | Risk level |
| --------- | ---------------------------------------------------- | ---------- |
| MCAR      | Missingness unrelated to observed or unobserved data | Lowest     |
| MAR       | Missingness related to observed data                 | Moderate   |
| MNAR      | Missingness related to the unobserved missing value  | Highest    |

Important note:

> You cannot prove MCAR, MAR, or MNAR with certainty from the observed data alone. You can only assess whether an assumption is plausible.

## Step 4: Choose a method

The method depends on:

* amount of missing data
* missing-data mechanism
* whether the missing variable is a predictor or outcome
* whether the goal is inference or prediction
* field-specific expectations
* sample size
* study design

## Step 5: Conduct sensitivity analyses

Sensitivity analysis means checking whether the conclusion changes when using different reasonable approaches.

For example:

* complete-case analysis
* multiple imputation
* median imputation
* model-based analysis
* excluding variables with high missingness

If conclusions are stable across methods, confidence increases.

If conclusions change, missing data are influencing the results and must be discussed carefully.

# 5. Rules of thumb for amount of missing data

These are practical guidelines, not universal laws.

| Missing-data proportion | Interpretation                                                                   |
| ----------------------: | -------------------------------------------------------------------------------- |
|                    < 5% | Usually minor, but still report it                                               |
|                   5–10% | Investigate patterns; deletion may be acceptable only if MCAR is plausible       |
|                  10–20% | Use principled methods such as multiple imputation or model-based approaches     |
|                  20–40% | Results may be sensitive; sensitivity analysis is important                      |
|                   > 40% | High risk; variable may be unreliable unless theoretically essential             |
|                   > 60% | Usually very difficult to justify without strong assumptions or external support |

Important:

> Missingness in the main outcome is more serious than missingness in a minor covariate.

# 6. Complete-case analysis

## What it is

Complete-case analysis, also called **listwise deletion**, removes all cases with missing values in any variable used in the analysis.

## Example

If a regression model uses:

* age
* workload
* condition
* reaction time

then any row missing one of these values is removed.

## When it may be acceptable

Complete-case analysis may be acceptable when:

* missing data are minimal
* MCAR is plausible
* sample size remains adequate
* missingness is not associated with key variables

## Advantages

* simple
* transparent
* easy to reproduce
* commonly understood

## Disadvantages

* reduces sample size
* reduces statistical power
* can introduce bias if data are not MCAR
* may change the composition of the sample

## Journal-style sentence

> Complete-case analysis was used because the proportion of missing data was small and missingness was not associated with observed study variables.

# 7. Available-case analysis

## What it is

Available-case analysis uses all available data for each analysis.

For example, one correlation may use 200 participants, while another uses 180 participants depending on which variables are missing.

## Advantages

* uses more information than complete-case analysis
* simple for descriptive statistics

## Disadvantages

* sample size differs across analyses
* results may be hard to compare
* covariance or correlation matrices can become inconsistent
* still biased if missingness is not MCAR

## Best use

Available-case analysis is often acceptable for descriptive summaries, but less ideal for main inferential models.

# 8. Single imputation methods

Single imputation replaces each missing value with one estimated value.

These methods are simple but can underestimate uncertainty because they treat imputed values as if they were truly observed.

## 8.1 Mean imputation

## What it is

Missing values are replaced with the mean of the observed values.

## Example

If the mean workload score is 55, all missing workload scores are replaced with 55.

## Advantages

* very simple
* easy to explain

## Disadvantages

* reduces variance
* weakens correlations
* can bias regression estimates
* underestimates uncertainty

## Recommendation

Mean imputation is usually not recommended for formal inference.

## 8.2 Median imputation

## What it is

Missing values are replaced with the median of the observed values.

## Advantages

* simple
* more robust than mean imputation for skewed variables

## Disadvantages

* still underestimates uncertainty
* can distort relationships between variables

## Recommendation

Median imputation may be acceptable for basic prediction workflows, but it is usually not ideal for inferential research.

## 8.3 Mode imputation

## What it is

Missing categorical values are replaced with the most frequent category.

## Example

If most participants are in the “control” group, missing condition values are replaced with “control.”

## Disadvantages

* can inflate the most common category
* can distort group proportions
* ignores uncertainty

## Recommendation

Use cautiously. It is usually better to create an explicit “missing” category for some categorical predictors, especially in prediction contexts.

## 8.4 Constant-value imputation

## What it is

Missing values are replaced with a constant such as:

* 0
* -999
* “Unknown”
* “Not reported”

## When it may be useful

This can be useful when missingness has a meaningful interpretation.

Example:

> If the number of prior accidents is missing because the participant reported none, replacing missing values with 0 may be justified.

## Warning

Do not use arbitrary constants unless the meaning is defensible.

# 9. Missing-indicator method

## What it is

A missing-data indicator is a binary variable showing whether a value was missing.

Example:

| workload | workload_missing |
| -------: | ---------------: |
|       45 |                0 |
|       NA |                1 |
|       70 |                0 |

## When useful

Missing indicators can be useful when:

* the goal is prediction
* missingness itself may contain information
* tree-based models are used
* clinical or behavioral nonresponse may be meaningful

## Warning for inference

For inferential models, missing indicators can produce biased coefficients if used carelessly.

## Example sentence

> Missing-data indicators were included to preserve information about systematic nonresponse.

# 10. Multiple imputation

## What it is

Multiple imputation replaces each missing value multiple times, creating several complete datasets.

Each dataset is analyzed separately, and the results are combined.

The typical process is:

1. Create multiple imputed datasets.
2. Analyze each dataset.
3. Pool the results.
4. Report combined estimates and uncertainty.

## Why it is better than single imputation

Multiple imputation accounts for uncertainty in the missing values.

Instead of pretending there is one correct imputed value, it recognizes that several values are plausible.

## When it is appropriate

Multiple imputation is appropriate when:

* data are plausibly MAR
* missingness is not trivial
* the goal is statistical inference
* important predictors or covariates have missing values

## Important principles

The imputation model should include:

* variables used in the analysis model
* variables related to missingness
* variables related to the missing values
* auxiliary variables that improve prediction of missing values

## Advantages

* preserves sample size
* reduces bias under MAR
* reflects uncertainty better than single imputation
* widely accepted in high-level journals

## Disadvantages

* requires assumptions
* more complex to implement
* results depend on the imputation model
* not a cure for MNAR data

## Journal-style sentence

> Missing values were imputed using multiple imputation under a missing-at-random assumption. The imputation model included all variables used in the analytic model and auxiliary variables associated with missingness.

# 11. MICE: Multiple Imputation by Chained Equations

## What it is

MICE is a flexible form of multiple imputation.

Each variable with missing data is imputed using a model based on the other variables.

For example:

* missing age may be imputed using condition, workload, and outcome
* missing workload may be imputed using age, condition, and outcome
* missing reaction time may be imputed using age, condition, workload, and trial number

This process is repeated iteratively.

## When useful

MICE is useful when:

* several variables have missing data
* variables are of different types
* missingness is plausibly MAR
* relationships among variables are important

## Advantages

* flexible
* widely used
* handles several variables with missing data
* suitable for many applied research datasets

## Disadvantages

* requires careful model specification
* can be unstable with small samples
* may perform poorly if the imputation model is wrong

# 12. K-nearest-neighbor imputation

## What it is

KNN imputation replaces a missing value using values from similar cases.

Similarity is usually based on other observed variables.

## Example

If participant A is missing workload score, KNN finds participants with similar age, performance, and condition, then uses their workload values.

## Advantages

* intuitive
* captures local structure
* useful for prediction

## Disadvantages

* sensitive to scaling
* computationally expensive for large datasets
* less ideal for formal inference
* does not naturally account for uncertainty

## Best use

KNN imputation is more common in machine learning than in explanatory statistical modeling.

# 13. Regression imputation

## What it is

A regression model predicts missing values from observed variables.

## Example

Missing workload score is predicted from:

* age
* condition
* task performance
* trial number

## Advantages

* uses relationships among variables
* better than mean imputation

## Disadvantages

* can overstate certainty
* may strengthen relationships artificially
* does not fully account for imputation uncertainty unless combined with multiple imputation

# 14. Maximum likelihood methods

## What they are

Maximum likelihood methods estimate model parameters directly using all available information, without explicitly filling in missing values.

Common examples:

* full information maximum likelihood, often called FIML
* mixed-effects models
* structural equation models with missing data

## When useful

Maximum likelihood methods are useful when:

* the analysis model is correctly specified
* data are plausibly MAR
* the goal is inference
* repeated-measures or longitudinal data are involved

## Advantages

* statistically principled
* avoids creating filled-in datasets
* uses all available information
* common in longitudinal analysis and SEM

## Disadvantages

* depends on model assumptions
* can be less flexible than multiple imputation
* not appropriate for all data structures

## Journal-style sentence

> Models were estimated using full information maximum likelihood to use all available observations under a missing-at-random assumption.

# 15. Mixed-effects models for repeated-measures data

## What they are

Mixed-effects models are often used for repeated-measures or longitudinal data.

They can handle missing outcome observations under MAR assumptions, as long as the model is correctly specified.

## Example

In a human-factors experiment, some participants may have missing reaction-time values for some trials.

A mixed-effects model can use the available trials without deleting the entire participant.

## Advantages

* useful for repeated measures
* does not require complete data for every participant
* can model participant-level variability
* appropriate for many experimental designs

## Disadvantages

* missingness assumptions still matter
* dropout related to unobserved outcomes can still bias results
* model specification is important

# 16. Inverse probability weighting

## What it is

Inverse probability weighting gives more weight to observations that represent cases likely to be missing.

The general idea is:

1. Model the probability that each observation is complete.
2. Give higher weight to observations with lower probability of being observed.
3. Analyze the weighted data.

## When useful

It is useful when:

* missingness depends on observed variables
* dropout or attrition is present
* complete cases are not representative of the full sample

## Advantages

* directly addresses selection into observed data
* useful for attrition and survey nonresponse

## Disadvantages

* requires a good model for missingness
* unstable when some observation probabilities are very small
* can increase variance

# 17. Sensitivity analysis for MNAR

## What it is

Sensitivity analysis examines how results change under different assumptions about missing data.

## Why it is important

MNAR cannot be solved by standard imputation alone.

If missingness may depend on unobserved values, the researcher should test whether conclusions are robust.

## Examples

You may ask:

* What if missing outcomes were systematically higher than imputed values?
* What if participants who dropped out had worse outcomes?
* What if missing reaction times were slower than observed reaction times?
* What if missing workload scores were higher in the high-workload condition?

## Journal-style sentence

> Sensitivity analyses were conducted to evaluate the robustness of the findings under alternative assumptions about the missing-data mechanism.

# 18. Missing data in prediction vs inference

## Inference

Inference asks:

> What is the relationship between variables?

Examples:

* Does workload affect reaction time?
* Does interface type influence task performance?
* Is fatigue associated with error rate?

For inference, missing-data methods must preserve:

* unbiased estimates
* valid standard errors
* valid confidence intervals
* valid p-values

Preferred methods:

* multiple imputation
* maximum likelihood
* mixed-effects models
* inverse probability weighting
* sensitivity analysis

## Prediction

Prediction asks:

> How accurately can we predict new observations?

Examples:

* Can we predict driver fatigue?
* Can we classify high-risk users?
* Can we forecast task failure?

For prediction, the priority is out-of-sample performance.

Preferred methods:

* train-test split before imputation
* imputation inside cross-validation
* missing indicators
* tree-based models that handle missing data
* median/mode/KNN imputation as preprocessing

Important rule:

> Never impute using the full dataset before train-test split. This causes data leakage.

# 19. Field-specific considerations

## Psychology and human factors

Common sources of missing data:

* skipped questionnaire items
* participant dropout
* unusable trials
* reaction-time trimming
* eye-tracking signal loss
* EEG artifacts
* motion capture failure
* sensor malfunction

Important distinction:

> Technical data loss and behavior-related missingness are not the same.

Example:

* Eye-tracking loss due to calibration failure may be technical.
* Eye-tracking loss because participants look away during difficult trials may be behaviorally meaningful.

## Medicine and clinical trials

Missing data are high-stakes because they can affect treatment-effect estimates.

Common concerns:

* dropout
* adverse-event-related missingness
* nonadherence
* death
* missed follow-up visits

Sensitivity analyses are often expected.

## Surveys and social science

Common sources:

* item nonresponse
* refusal to answer sensitive questions
* attrition
* panel dropout

Sensitive variables such as income, health status, and political attitudes may be MNAR.

## Engineering and sensor data

Common sources:

* sensor failure
* communication loss
* saturation
* device drift
* environmental interference

Short gaps may sometimes be interpolated.

Long or systematic gaps should not be filled automatically.

# 20. Recommended decision guide

## If missing data are less than 5%

Use:

* descriptive missing-data report
* complete-case analysis may be acceptable if MCAR is plausible
* sensitivity analysis if the variable is important

## If missing data are 5–20%

Use:

* missing-data pattern analysis
* logistic regression predicting missingness
* multiple imputation or maximum likelihood if MAR is plausible
* complete-case analysis as sensitivity check

## If missing data are 20–40%

Use:

* multiple imputation or model-based methods
* sensitivity analyses
* careful reporting
* consider whether the variable is still reliable

## If missing data are greater than 40%

Use:

* strong theoretical justification
* sensitivity analysis
* possibly remove the variable
* discuss limitations clearly

## If missing data are in the main outcome

Use:

* mixed-effects models for repeated measures
* multiple imputation
* inverse probability weighting
* sensitivity analysis

Avoid relying only on simple imputation.

## If missing data are in predictors

Use:

* multiple imputation for inference
* median/mode/KNN imputation for prediction
* missing indicators when missingness may be informative

## If MNAR is suspected

Use:

* sensitivity analysis
* pattern-mixture models
* selection models
* transparent limitations

Do not claim that ordinary imputation fully solves the problem.

# 21. Good reporting template

## Methods section

> The extent and pattern of missing data were examined before analysis. We assessed whether missing data were associated with observed participant characteristics, experimental conditions, or outcome-related variables. Missing values were addressed using [method] under a [MCAR/MAR/MNAR] assumption. Sensitivity analyses were conducted to compare results from [main method] with [alternative method].

## Results section

> Overall, [X]% of observations were incomplete. The proportion of missing observations was highest for [variable]. Missing data were more common in [group/condition/time point], suggesting that complete-case analysis alone may be biased. Results were similar across the main and sensitivity analyses.

## Limitations section

> Although missing data were addressed using [method], the possibility that missingness depended on unobserved values cannot be ruled out. Therefore, the findings should be interpreted with caution.

# 22. Key principles to remember

1. Do not delete missing data automatically.
2. Always report the amount and pattern of missing data.
3. The missing-data mechanism matters more than the percentage alone.
4. Mean imputation is usually weak for formal analysis.
5. Multiple imputation is often preferred under MAR.
6. MNAR requires sensitivity analysis.
7. Prediction and inference require different handling.
8. Imputation must be done inside the training pipeline in machine learning.
9. Missing outcome data are more serious than missing predictor data.
10. Field-specific context determines whether missingness is ignorable or meaningful.

# Short version to remember

For your Notion summary:

> Missing data should first be described, then diagnosed, then addressed using a method appropriate to the missing-data mechanism and research goal. Complete-case analysis may be acceptable when missing data are minimal and plausibly MCAR. For MAR data, multiple imputation, maximum likelihood, or mixed-effects models are usually preferred. If MNAR is suspected, sensitivity analysis is necessary. In machine learning, imputation must be performed inside the training pipeline to avoid data leakage.

```