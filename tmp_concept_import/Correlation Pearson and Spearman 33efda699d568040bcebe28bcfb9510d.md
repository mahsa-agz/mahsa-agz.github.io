# Correlation: Pearson and Spearman

Category: Exploratory Data Analysis (EDA), Statistical Methods (Inference-Oriented)
Status: Needs Review

## **What is correlation?**

Correlation is a statistical way to describe how two variables move together.

It tells you two main things:

- **Direction**: whether two variables tend to move in the same direction or in opposite directions
- **Strength**: how strongly they are related

If one variable tends to increase when the other increases, the correlation is positive. If one tends to decrease when the other increases, the correlation is negative.

For example, if study time and exam score increase together, they have a positive correlation. If reaction time variability increases while quality of life decreases, they have a negative correlation.

## **What correlation tells you**

Correlation tells you:

- whether there is a relationship in direction
- how strong that relationship appears to be
- whether the pattern is positive or negative

### **What correlation does not tell you**

Correlation does not tell you:

- that one variable causes the other
- whether the relationship remains after controlling for other variables
- whether the relationship is clinically or practically important
- the full shape of the relationship

So correlation is a useful summary, but it is not the whole story.

## **Why are there different kinds of correlation?**

Not all relationships in data look the same.

Some relationships are close to a straight line. Others are curved but still move in one direction overall. Some datasets contain outliers. Some are skewed. Some are better understood by rank order than by exact distances.

Because of this, different kinds of correlation exist. Two common ones are Pearson correlation and Spearman correlation.

They are both measures of association, but they capture different aspects of the relationship.

## **Linear and monotonic relationships**

Before comparing Pearson and Spearman, it helps to understand two types of patterns: linear and monotonic.

### **Linear relationship**

A linear relationship means that two variables follow a pattern that is roughly like a straight line.

If one variable increases, the other tends to increase or decrease at a fairly proportional rate.

Example:

If each extra hour of study is associated with about 10 more points on a test, that is a linear relationship.

### **Monotonic relationship**

A monotonic relationship means that as one variable increases, the other generally moves in only one direction overall.

It may always increase, or always decrease, but not necessarily in a straight line.

Example:

Stress may increase with workload, but slowly at first and then much faster later. That is monotonic, but not linear.

### **Key difference**

- A linear relationship is usually monotonic
- A monotonic relationship is not always linear

This is why one correlation method may describe a relationship better than another.

## **Spearman correlation**

Spearman correlation measures how strongly two variables are associated in terms of rank order.

It is most useful when:

- the relationship is monotonic but not necessarily linear
- the data are skewed
- there may be outliers
- you care about consistent direction rather than exact numeric change

Spearman converts values into ranks and then evaluates the relationship using those ranks.

Because it uses ranks, it is often more robust when:

- some values are extreme
- the scale is uneven
- the pattern is curved but still ordered

### Spearman correlation Formula:

$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$

- where
    
    d_i = difference between ranks of X and Y for observation i
    
    n = number of observations
    
    \rho = Spearman rank correlation coefficient
    

## **Pearson correlation**

Pearson correlation measures how strongly two variables follow a linear pattern using their actual values.

It is most useful when:

- variables are continuous
- the relationship is roughly linear
- there are no strong outliers dominating the pattern
- the exact numeric distances matter

Pearson uses the real values, so it reflects how close the data are to a straight-line pattern.

Because it uses raw values, it is more sensitive to:

- extreme observations
- skewed distributions
- unusual shapes in the data

### Pearson correlation Formula:

$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \;\sum (y_i - \bar{y})^2}}$

- where
    
    x_i = value of X for observation i
    
    y_i = value of Y for observation i
    
    x̄ = mean of X
    
    ȳ = mean of Y
    
    Σ = sum across all observations
    
    r = Pearson correlation coefficient
    

## Pearson Vs Spearman

Pearson Vs Spearman both describe association, but they do so differently.

| **Aspect** | **Pearson** | **Spearman** |
| --- | --- | --- |
| Definition | Measures linear association using raw values | Measures monotonic association using ranks |
| What it looks at | Actual numerical values and distances between them | Order or ranking of values |
| Core idea | Do the variables move together in a straight-line way? | Do higher values of one variable go with higher or lower values of the other? |
| Main intuition | Focuses on exact numeric change | Focuses on overall order |
| Best use | Linear relationships in reasonably clean data | Ordered relationships, especially when data may be skewed or nonlinear |
| Less suitable when | Relationship is strongly nonlinear or heavily affected by outliers | Exact numeric spacing is important |
| Example | Study time and exam score increasing steadily | Symptom severity increasing with disease stage, but not linearly |
| Sensitive to outliers | More sensitive, because extreme values affect the raw-value distances | Less sensitive, because ranks reduce the effect of extreme values |
| Works well with skewed data | Less well, because skew affects distances and linear fit | Better, because ranking reduces the effect of skew |
| Typical interpretation | Best for straight-line relationships | Best for generally ordered relationships |

## **How to interpret Pearson and Spearman together**

This is one of the most important practical parts.

The safest and most useful question is not “Which one is bigger?” The better question is:

- Do Pearson and Spearman tell a similar story or not?

That is the main interpretation principle.

### **If Pearson and Spearman are similar**

If they are similar in direction and size, that usually suggests:

- the relationship is fairly stable
- both the raw values and the rank order support the same conclusion
- the result is less likely to depend only on unusual points
- the interpretation is more convincing

Example:

Pearson = -0.31 and Spearman = -0.32

This suggests a stable negative relationship.

### **If Pearson and Spearman are not similar**

If they differ noticeably, that suggests:

- the shape of the data may matter
- outliers, skew, clustering, or nonlinearity may be affecting the result
- the finding needs closer inspection
- a scatterplot would be helpful

The important point is that the difference itself is not a final explanation. It is a signal to inspect the data more carefully.

**Example of similar and different Pearson and Spearman** 

| **Pattern** | **Example** | **Safer interpretation** |
| --- | --- | --- |
| Pearson and Spearman are similar | -0.31 vs -0.32 | Stable and consistent association |
| Pearson and Spearman are somewhat different | -0.31 vs -0.18 | The data structure may be affecting the result; inspect further |
| Pearson and Spearman are very different | 0.40 vs 0.05 | The association may depend strongly on shape, outliers, or instability |
| Opposite signs | 0.10 vs -0.15 | Unstable or unusual pattern; inspect the data closely |

**A practical interpretation table**

| **Situation** | **What to focus on** |
| --- | --- |
| Pearson and Spearman are similar | The association appears stable |
| They differ somewhat | Check data shape and scatterplot |
| They differ a lot | Be cautious; the result may not be robust |
| One is significant and the other is not | Look more closely before drawing conclusions |

## **Why we should not over-interpret Pearson > Spearman or Spearman > Pearson**

It is tempting to say:

- Pearson is bigger, so outliers must be the reason
- Spearman is bigger, so the relationship must be nonlinear

These can sometimes be reasonable hints, but they are not reliable rules.

A difference between Pearson and Spearman can happen because of:

- outliers
- skewed distributions
- nonlinear shape
- clustered data
- limited sample size
- general instability in the data

So the better interpretation is not:

- “Pearson > Spearman means X”
- “Spearman > Pearson means Y”

The better interpretation is:

- “Pearson and Spearman are either broadly consistent or not broadly consistent”

That is a more accurate and defensible way to interpret them.

A good sentence for notes is:

In practice, the key question is not which one is larger, but whether Pearson and Spearman show a similar pattern. Similar values support a stable association, while different values suggest that the result may depend on the structure of the data and should be examined more carefully.

## **Why outliers matter more for Pearson**

Pearson uses actual values and actual distances. This means extreme values can influence it a lot.

An outlier does not always make Pearson smaller. It can:

- weaken Pearson
- strengthen Pearson
- or even change the pattern substantially

What matters is where the outlier falls.

If the outlier pulls in the same direction as the trend, Pearson can become larger. If it goes against the trend, Pearson can become smaller.

That is why the safest statement is:

Pearson is more sensitive to outliers because it uses raw values and exact distances.

Spearman is often more stable because it uses ranks rather than exact magnitudes.

## 

Univariate analysis means looking at one predictor at a time in relation to an outcome.

Examples:

- reaction time variability vs quality of life
- accuracy vs quality of life
- omission rate vs quality of life

This is useful for exploration because it helps identify possible relationships.

But it also has an important limitation: it treats each predictor separately and ignores overlap between predictors.