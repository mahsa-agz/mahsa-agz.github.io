# handling missing data

Category: Feature Engineering and Data Preparation

Code Examples: 

[Code Examples](Code%20Examples%20361fda699d5680e2880cf61485b7fc8b.md)

## Practical workflow

A good missing-data handling workflow is:

1. **Quantify** missing data by variable and case.
2. **Check patterns** by group, condition, time, site, or device.
3. **Ask why values are missing** using domain knowledge.
4. **Classify likely mechanism**: MCAR, MAR, or MNAR.
5. **Choose method** based on goal: inference or prediction.
6. **Run sensitivity analyses** if missing data affects key variables.
7. **Report assumptions and method clearly.**

## Missing data mechanism Classification

The key question is: **why is the value missing?**

### MCAR: Missing Completely at Random

The probability of missing data is unrelated to observed or unobserved data.

Example: a lab machine randomly fails for 3% of samples.

This is the least problematic case. Complete-case analysis may be acceptable if the missing rate is small.

### MAR: Missing at Random

missing data depends on observed variables, but not on the missing value itself after conditioning on those variables.

Example: older participants are less likely to answer income questions, but within age groups, missing data is not related to income.

This is common in practice. Multiple imputation, maximum likelihood, or model-based methods are often appropriate.

### MNAR: Missing Not at Random

missing data depends on the unobserved missing value itself.

Example: high-income individuals are less likely to report income; depressed participants are less likely to complete a depression survey.

This is the hardest case. Standard imputation can be biased. Sensitivity analysis is usually needed.

## General rules of thumb

### Do not delete missing data automatically

Listwise deletion is simple, but it can reduce power and introduce bias unless data are MCAR or the missing fraction is very small.

### Always report missing data

Report how much data are missing, where they are missing, and whether missing data differs by key groups.

For example:

> “Outcome data were missing for 8.4% of participants. missing data was higher among older participants and those in the control group.”
> 

### Visualize the missing data pattern

Before choosing a method, inspect whether missing data clusters by variable, group, time point, site, condition, or measurement device.

### Avoid single mean imputation

Mean imputation is usually poor because it underestimates variance, weakens correlations, and creates artificial certainty.

### Prefer principled methods when missing data is nontrivial

Common choices:

| Situation | Better approach |
| --- | --- |
| Small MCAR missing data | Complete-case analysis may be okay |
| MAR missing predictors | Multiple imputation |
| MAR missing outcomes | Maximum likelihood, multiple imputation, mixed models |
| Longitudinal dropout | Mixed-effects models, inverse probability weighting, joint models |
| MNAR suspected | Sensitivity analysis, selection models, pattern-mixture models |
| Machine learning prediction | Imputation inside cross-validation, missing data indicators, models that handle missing data |

## Rough thresholds for amount missing

These are not laws, but practical heuristics:

| Missing data level | Practical interpretation |
| --- | --- |
| < 5% | Often minor; complete-case may be acceptable if plausibly MCAR |
| 5–10% | Investigate patterns; simple deletion may still be risky |
| 10–20% | Use principled imputation/modeling unless strong MCAR evidence |
| 20–40% | Results become sensitive; report carefully and run sensitivity checks |
| > 40% | High risk; variable may be unusable unless theoretically critical or recoverable |
| > 60% | Usually not reliable without strong assumptions or external validation |

These thresholds depend heavily on the variable’s role. missing data in a minor covariate is less serious than missing data in the main outcome.

## Predictor vs outcome missing data

missing data in **predictors** and **outcomes** should be handled differently.

### Missing predictor values

Often handled with:

- multiple imputation
- model-based imputation
- missing data indicators, especially in prediction models
- domain-specific replacement rules, where justified

### Missing outcome values

More serious, because the target of inference is partly unobserved.

For outcome missing data, use:

- mixed-effects models for repeated measures
- multiple imputation including outcome-related predictors
- inverse probability weighting for attrition
- sensitivity analysis if dropout may depend on the unobserved outcome

## Inference vs prediction matters

### If your goal is inference

For example, estimating the effect of treatment, age, workload, interface type, or exposure.

You need methods that preserve unbiased estimates and valid uncertainty:

- multiple imputation
- likelihood-based models
- inverse probability weighting
- sensitivity analysis

Avoid casual imputation because it can distort standard errors and p-values.

### If your goal is prediction

For example, building a classifier or forecasting model.

The priority is out-of-sample performance:

- impute within each training fold
- never impute using the full dataset before train-test split
- include missing data indicators if missing data itself may be informative
- use models that can handle missing values, such as tree-based boosting methods

## Are rules field-dependent?

Yes.

### Medicine / clinical trials

Missing data handling is high-stakes. Regulators usually expect clear assumptions, prespecified methods, and sensitivity analyses. Outcome dropout is especially serious.

### Psychology / human factors

Missing survey responses, failed trials, eye-tracking loss, reaction-time exclusions, and participant dropout are common. You need to distinguish between technical missing data and behavior-related missing data. For example, missing eye-tracking data may reflect poor calibration, but it may also reflect gaze aversion or task difficulty.

### Education research

Attrition and nonresponse may correlate with ability, socioeconomic status, or school quality. MAR is often plausible only after including rich covariates.

### Economics / social science

Income, wealth, and sensitive variables are often MNAR. Weighting, imputation, and sensitivity analysis are common.

### Engineering / sensor data

missing data may come from device failure, communication dropouts, saturation, or environmental conditions. Interpolation may be acceptable for short gaps in time series but not for long or systematic gaps.

### Machine learning

The rules are more performance-oriented, but leakage control is critical. Imputation must be learned only from training data and then applied to validation/test data.

## Minimal reporting template

You can write something like:

> missing data was assessed for all variables before analysis. Variables with less than 5% missing data were retained. For variables with 5–20% missing data, missing data patterns were examined across experimental condition, participant characteristics, and outcome measures. Because missing data ppeared related to observed covariates, multiple imputation was used under a missing-at-random assumption. Analyses were repeated using complete cases as a sensitivity check. Results were interpreted cautiously where conclusions differed across methods.
> 

>