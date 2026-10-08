---
title: "Correlation and agreement: do the numbers move together, or do they match?"
date: 2026-08-03
category: stats-methods
read_time: 12
excerpt: "Why high correlation can still mean poor agreement, and how to choose Pearson, Spearman, Bland-Altman, ICC, CCC, or kappa."
lede: "Correlation asks whether two variables rise and fall together. Agreement asks whether two measurements are close enough to be used interchangeably. Mixing those questions up is one of the easiest ways to misread data."
description: "A beginner-friendly guide to correlation versus agreement, with examples, comparison tables, and a method map for Pearson, Spearman, Bland-Altman, ICC, CCC, and kappa."
---

## Start with the question

Imagine a clinic buys a new thermometer. For every patient, the new thermometer reads about 0.8 C higher than the old standard. The two devices will usually rank patients in the same order, so their correlation can be very high. But the devices still do **not** agree, because one of them is systematically higher.

That is the whole lesson in one line:

- **Correlation** asks: do the numbers move together?
- **Agreement** asks: are the numbers close enough to use one in place of the other?

If the only thing you remember from this page is that sentence, you will already avoid a very common mistake.

<div class="compare-grid">
  <section class="compare-card">
    <h3>Correlation</h3>
    <p><strong>Main question:</strong> when one value is high, is the other usually high too?</p>
    <ul>
      <li>Best for relationships and association</li>
      <li>Typical methods: Pearson and Spearman</li>
      <li>Common use: exploration, screening, prediction features</li>
      <li>Wrong use: claiming two devices or raters are interchangeable</li>
    </ul>
  </section>
  <section class="compare-card compare-card--accent">
    <h3>Agreement</h3>
    <p><strong>Main question:</strong> for the same subject, how close are the two measurements or ratings?</p>
    <ul>
      <li>Best for reliability and method comparison</li>
      <li>Typical methods: Bland-Altman, ICC, CCC, and kappa</li>
      <li>Common use: can method B replace method A?</li>
      <li>Wrong use: describing a relationship between two different variables</li>
    </ul>
  </section>
</div>

<div class="rule-box">
  <p><strong>Fast rule:</strong> if you care about <em>relationship</em>, think correlation. If you care about <em>replaceability</em>, think agreement.</p>
</div>

## Why high correlation can still mean poor agreement

Suppose method B is always exactly 10 units higher than method A:

- Patient 1: A = 20, B = 30
- Patient 2: A = 40, B = 50
- Patient 3: A = 60, B = 70

The points sit on a perfect straight line, so the correlation is extremely high. But the values are never equal. If a difference of 10 units matters in practice, the agreement is poor even though the correlation looks excellent.

<figure class="figure">
  <svg viewBox="0 0 760 300" role="img" aria-label="Two scatterplots. Left panel shows points on a line above the identity line, meaning high correlation but poor agreement. Right panel shows points close to the identity line, meaning high correlation and good agreement.">
    <text class="fig-text" x="28" y="26">High correlation, poor agreement</text>
    <line class="fig-line" x1="60" y1="50" x2="60" y2="250"/>
    <line class="fig-line" x1="60" y1="250" x2="340" y2="250"/>
    <text class="fig-muted" x="44" y="155" text-anchor="end">Method B</text>
    <text class="fig-muted" x="200" y="278" text-anchor="middle">Method A</text>
    <path class="fig-arrow-muted" d="M 85 225 L 315 85"/>
    <text class="fig-muted-mono" x="310" y="78" text-anchor="end">identity line: B = A</text>
    <line class="fig-fit-line" x1="85" y1="195" x2="315" y2="55"/>
    <circle class="fig-dot" cx="105" cy="183" r="4"/>
    <circle class="fig-dot" cx="135" cy="165" r="4"/>
    <circle class="fig-dot" cx="165" cy="147" r="4"/>
    <circle class="fig-dot" cx="195" cy="129" r="4"/>
    <circle class="fig-dot" cx="225" cy="111" r="4"/>
    <circle class="fig-dot" cx="255" cy="93" r="4"/>
    <circle class="fig-dot" cx="285" cy="75" r="4"/>
    <text class="fig-accent-text" x="305" y="50" text-anchor="end">same pattern, shifted upward</text>

    <text class="fig-text" x="408" y="26">High correlation, good agreement</text>
    <line class="fig-line" x1="440" y1="50" x2="440" y2="250"/>
    <line class="fig-line" x1="440" y1="250" x2="720" y2="250"/>
    <text class="fig-muted" x="424" y="155" text-anchor="end">Method B</text>
    <text class="fig-muted" x="580" y="278" text-anchor="middle">Method A</text>
    <path class="fig-arrow-muted" d="M 465 225 L 695 85"/>
    <text class="fig-muted-mono" x="690" y="78" text-anchor="end">identity line: B = A</text>
    <line class="fig-fit-line" x1="470" y1="220" x2="690" y2="90"/>
    <circle class="fig-dot" cx="485" cy="213" r="4"/>
    <circle class="fig-dot" cx="515" cy="190" r="4"/>
    <circle class="fig-dot" cx="545" cy="172" r="4"/>
    <circle class="fig-dot" cx="575" cy="150" r="4"/>
    <circle class="fig-dot" cx="605" cy="135" r="4"/>
    <circle class="fig-dot" cx="635" cy="118" r="4"/>
    <circle class="fig-dot" cx="665" cy="97" r="4"/>
    <text class="fig-accent-text" x="690" y="54" text-anchor="end">close to the identity line</text>
  </svg>
  <figcaption>Both panels can have very high correlation. Only the right panel shows good agreement, because the paired values are close to equality.</figcaption>
</figure>

## Correlation methods: use these for association

Correlation is about whether two variables co-vary. It is not about whether they give the same value.

Before choosing a correlation coefficient, look at a scatterplot. The plot tells you whether the pattern is roughly linear, strongly curved, or dominated by outliers. The coefficient should come after the picture, not before it.

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Method</th>
        <th>Use it when</th>
        <th>What it tells you</th>
        <th>Do not use it when</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Pearson correlation</strong></td>
        <td>The variables are continuous and the relationship is roughly linear.</td>
        <td>How strongly the raw values follow a straight-line pattern.</td>
        <td>You have strong outliers, an obviously curved pattern, ordinal categories, or a replaceability question.</td>
      </tr>
      <tr>
        <td><strong>Spearman correlation</strong></td>
        <td>The relationship is monotonic, the data are skewed, or you care more about rank order than exact spacing.</td>
        <td>Whether higher values of one variable tend to go with higher or lower values of the other.</td>
        <td>You need exact numeric closeness, a slope in the original units, or proof that two methods agree.</td>
      </tr>
    </tbody>
  </table>
</div>

### Pearson in plain words

Pearson answers: *if one variable changes by a little, does the other tend to change in a proportional straight-line way too?*

Good example:

- Hours studied and exam score
- Height and weight
- Dose and blood concentration over a small linear range

Not a good example:

- Two devices measuring the same thing, when your real question is whether they can substitute for one another

### Spearman in plain words

Spearman answers: *if I rank people from low to high on one variable, do they get a similar rank on the other?*

Good example:

- Disease stage and symptom severity
- Class rank and interview rank
- A monotonic but curved relationship

Not a good example:

- Two thermometers, two scales, or two raters where exact closeness matters

## Agreement methods for continuous measurements

Now switch to a different kind of question: two devices, two lab methods, or two raters measuring the **same continuous quantity** on the **same subjects**.

That is where agreement methods belong.

### Bland-Altman: the most practical first step

A Bland-Altman plot does something correlation does not do: it looks directly at the **differences** between paired measurements.

For each subject:

1. Compute the average of the two methods.
2. Compute the difference between the two methods.
3. Plot difference versus average.

That simple plot answers two very useful questions:

- Is one method systematically higher or lower on average? This is the **bias**.
- How wide is the typical disagreement? These are the **limits of agreement**.

<figure class="figure">
  <svg viewBox="0 0 560 300" role="img" aria-label="Bland-Altman plot with average on the x-axis and difference on the y-axis. A central mean-bias line is above zero and two dashed limits of agreement show the spread of differences.">
    <line class="fig-line" x1="70" y1="40" x2="70" y2="250"/>
    <line class="fig-line" x1="70" y1="250" x2="510" y2="250"/>
    <text class="fig-muted" x="55" y="150" text-anchor="end">Difference (B - A)</text>
    <text class="fig-muted" x="290" y="278" text-anchor="middle">Average of A and B</text>

    <line class="fig-line-accent" x1="90" y1="118" x2="490" y2="118"/>
    <text class="fig-accent-text" x="495" y="122">Mean bias</text>

    <path class="fig-arrow-muted" d="M 90 72 L 490 72"/>
    <path class="fig-arrow-muted" d="M 90 182 L 490 182"/>
    <text class="fig-muted-mono" x="495" y="76">Upper limit</text>
    <text class="fig-muted-mono" x="495" y="186">Lower limit</text>

    <line class="fig-arrow-muted" x1="70" y1="150" x2="510" y2="150"/>
    <text class="fig-muted-mono" x="82" y="145">zero difference</text>

    <circle class="fig-dot" cx="120" cy="108" r="4"/>
    <circle class="fig-dot" cx="150" cy="130" r="4"/>
    <circle class="fig-dot" cx="180" cy="95" r="4"/>
    <circle class="fig-dot" cx="210" cy="122" r="4"/>
    <circle class="fig-dot" cx="240" cy="145" r="4"/>
    <circle class="fig-dot" cx="270" cy="116" r="4"/>
    <circle class="fig-dot" cx="300" cy="99" r="4"/>
    <circle class="fig-dot" cx="330" cy="126" r="4"/>
    <circle class="fig-dot" cx="360" cy="110" r="4"/>
    <circle class="fig-dot" cx="390" cy="134" r="4"/>
    <circle class="fig-dot" cx="420" cy="88" r="4"/>
    <circle class="fig-dot" cx="450" cy="120" r="4"/>
  </svg>
  <figcaption>If the mean bias is far from zero, one method is systematically shifted. If the limits are too wide for your application, the methods do not agree well enough to be interchangeable.</figcaption>
</figure>

### ICC and CCC: useful summaries, but not the whole story

Two other names often appear in papers:

- **ICC** = intraclass correlation coefficient
- **CCC** = Lin's concordance correlation coefficient

Both try to summarize agreement for continuous measurements with a single number, but they answer slightly different versions of the reliability question.

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Method</th>
        <th>Best use</th>
        <th>Helpful for</th>
        <th>Be careful because</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Bland-Altman</strong></td>
        <td>Paired continuous measurements from two methods on the same subjects</td>
        <td>Seeing bias, spread, and whether the disagreement is practically acceptable</td>
        <td>It needs paired data, and it works best when you already know what difference would count as acceptable in practice.</td>
      </tr>
      <tr>
        <td><strong>ICC</strong></td>
        <td>Reliability or reproducibility of continuous ratings or measurements</td>
        <td>Summarizing how much of the variation is due to real subject-to-subject differences rather than measurement error</td>
        <td>A high ICC can still happen even when there is systematic bias, especially if subjects differ a lot from one another. It should not replace a Bland-Altman check.</td>
      </tr>
      <tr>
        <td><strong>CCC</strong></td>
        <td>One-number summary of how close paired values are to the 45-degree identity line</td>
        <td>Combining precision and closeness to equality in a single statistic</td>
        <td>Like any single number, it can hide patterns. Use it with a plot, not instead of a plot.</td>
      </tr>
    </tbody>
  </table>
</div>

### When not to stop at one number

If someone reports only `r = 0.94` or only `ICC = 0.91`, ask one more question:

> Are the paired measurements actually close enough for the decision we need to make?

That practical question is why agreement studies should nearly always show more than one summary.

## Agreement methods for categorical ratings

Sometimes the data are not continuous numbers. They are categories such as:

- yes / no
- mild / moderate / severe
- class A / class B / class C

In that setting, simple percent agreement is a start, but it is not enough by itself because some agreement happens by chance.

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Method</th>
        <th>Use it when</th>
        <th>What it handles well</th>
        <th>Do not rely on it when</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Percent agreement</strong></td>
        <td>You want a simple descriptive starting point</td>
        <td>Showing the raw proportion of times raters matched</td>
        <td>You need an agreement measure that adjusts for chance. Use it as context, not as the main result.</td>
      </tr>
      <tr>
        <td><strong>Cohen's kappa</strong></td>
        <td>Two raters and nominal categories</td>
        <td>Adjusting for chance agreement</td>
        <td>The categories are ordered or one category is overwhelmingly common and you need a fuller interpretation.</td>
      </tr>
      <tr>
        <td><strong>Weighted kappa</strong></td>
        <td>Two raters and ordered categories</td>
        <td>Giving partial credit when raters are close rather than completely different</td>
        <td>The categories are purely nominal with no natural order.</td>
      </tr>
      <tr>
        <td><strong>Fleiss' kappa</strong></td>
        <td>More than two raters and nominal categories</td>
        <td>Multi-rater agreement in classification tasks</td>
        <td>The outcome is continuous or the problem is really about association instead of agreement.</td>
      </tr>
    </tbody>
  </table>
</div>

## Worked examples

The easiest way to choose a method is to look at the question, not the software menu.

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Scenario</th>
        <th>Best first method</th>
        <th>Why</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Hours studied versus exam score</td>
        <td><strong>Pearson</strong> if the pattern is roughly linear, otherwise <strong>Spearman</strong></td>
        <td>You care about association between two different variables, not interchangeability.</td>
      </tr>
      <tr>
        <td>Old blood-pressure device versus new blood-pressure device on the same patients</td>
        <td><strong>Bland-Altman</strong>, often with <strong>ICC</strong> or <strong>CCC</strong> as a supplement</td>
        <td>You care about whether the new device can replace the old one.</td>
      </tr>
      <tr>
        <td>Two radiologists saying yes or no to pneumonia</td>
        <td><strong>Cohen's kappa</strong></td>
        <td>You have two raters and nominal categories.</td>
      </tr>
      <tr>
        <td>Two clinicians rating pain as mild, moderate, or severe</td>
        <td><strong>Weighted kappa</strong></td>
        <td>The categories are ordered, so near-misses should count differently from complete disagreement.</td>
      </tr>
      <tr>
        <td>Three raters labeling wound stage categories</td>
        <td><strong>Fleiss' kappa</strong></td>
        <td>You have more than two raters and categorical labels.</td>
      </tr>
    </tbody>
  </table>
</div>

## A simple decision guide

<ul class="method-checklist">
  <li><strong>Step 1:</strong> Ask whether your goal is association or agreement.</li>
  <li><strong>Step 2:</strong> If it is association, start with a scatterplot and then choose Pearson or Spearman.</li>
  <li><strong>Step 3:</strong> If it is agreement for continuous measurements, look at paired differences with Bland-Altman and add ICC or CCC if a summary number helps.</li>
  <li><strong>Step 4:</strong> If it is agreement for categorical ratings, choose from the kappa family.</li>
  <li><strong>Step 5:</strong> Decide before analysis what amount of disagreement would still be acceptable in the real application.</li>
</ul>

## Common mistakes to avoid

- Reporting a high correlation and concluding that two methods agree.
- Reporting only percent agreement for rater studies and ignoring chance agreement.
- Using a single summary number without showing the pattern of disagreements.
- Forgetting that agreement is a practical judgment as well as a statistical one. A small bias may be acceptable in one context and unacceptable in another.
- Choosing a method first and only later deciding what question you were actually trying to answer.

## Takeaway

Correlation and agreement are neighbors, not twins.

- Correlation tells you whether values move together.
- Agreement tells you whether values are close enough to stand in for one another.

That is why a method can correlate beautifully and still be useless as a replacement. Start with the scientific question, then choose the statistic that actually answers it.
