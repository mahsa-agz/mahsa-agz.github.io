---
title: "Linear regression, intuitively"
date: 2026-05-26
category: classic-ml
read_time: 10
excerpt: "Residuals, R², adjusted R², F and the p-value — built up visually from the simplest mouse-weight example."
lede: "The simplest way to use one number to predict another. Once you see how it works on two variables, the rest of regression is the same idea with more dimensions."
description: "A visual walk through linear regression: residuals, the best line, R², adjusted R², and how F and p-value decide if the fit is real."
image: https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=760&q=85
---

## The setup

Suppose we have a small dataset of mice. For each mouse we know its **weight** and its **size**. We'd like to use weight to predict size for a new mouse — something like `size = a × weight + b`. The job is to find the values of `a` (slope) and `b` (intercept) that fit the data best.

## What does "best line" actually mean?

Pick any line through the data. For each point, measure the vertical distance to the line. That distance is called a **residual** — what's left over after the line "explains" the point. A line that fits well has small residuals; a line that fits badly has big ones.

To turn "small residuals" into a single number we can optimize, we square each residual and add them up. The result is the **sum of squared residuals**, usually written `SS(fit)`. Squaring keeps positive and negative misses from cancelling, and punishes big misses more than small ones.

<figure class="figure">
  <svg viewBox="0 0 480 240" role="img" aria-label="Scatter of mouse weight against mouse size with a fitted line and dashed vertical residuals from each point to the line.">
    <line class="fig-line" x1="50" y1="40"  x2="50"  y2="200"/>
    <line class="fig-line" x1="50" y1="200" x2="450" y2="200"/>
    <text class="fig-muted" x="40"  y="120" text-anchor="end">size</text>
    <text class="fig-muted" x="250" y="225" text-anchor="middle">weight</text>
    <line class="fig-fit-line" x1="70" y1="170" x2="430" y2="70"/>
    <line class="fig-residual" x1="90"  y1="155" x2="90"  y2="165"/>
    <line class="fig-residual" x1="140" y1="120" x2="140" y2="151"/>
    <line class="fig-residual" x1="190" y1="148" x2="190" y2="137"/>
    <line class="fig-residual" x1="240" y1="100" x2="240" y2="123"/>
    <line class="fig-residual" x1="290" y1="135" x2="290" y2="109"/>
    <line class="fig-residual" x1="340" y1="80"  x2="340" y2="95"/>
    <line class="fig-residual" x1="390" y1="110" x2="390" y2="81"/>
    <circle class="fig-dot" cx="90"  cy="155" r="4"/>
    <circle class="fig-dot" cx="140" cy="120" r="4"/>
    <circle class="fig-dot" cx="190" cy="148" r="4"/>
    <circle class="fig-dot" cx="240" cy="100" r="4"/>
    <circle class="fig-dot" cx="290" cy="135" r="4"/>
    <circle class="fig-dot" cx="340" cy="80"  r="4"/>
    <circle class="fig-dot" cx="390" cy="110" r="4"/>
    <text class="fig-muted-mono" x="240" y="20" text-anchor="middle">each dashed segment = a residual</text>
  </svg>
  <figcaption>Square each residual, add them up. That total — <code>SS(fit)</code> — is the line's "badness."</figcaption>
</figure>

## Finding the best line

Rotate the line a little. `SS(fit)` changes. Rotate further — it changes again. If we try many rotations and plot `SS(fit)` against the rotation, we see a U-shape. The bottom of the U is the rotation we want.

<figure class="figure">
  <svg viewBox="0 0 480 220" role="img" aria-label="U-shaped curve of sum of squared residuals against line rotation, with the minimum marked.">
    <line class="fig-line" x1="60" y1="30"  x2="60"  y2="180"/>
    <line class="fig-line" x1="60" y1="180" x2="450" y2="180"/>
    <text class="fig-muted" x="50"  y="105" text-anchor="end">SS(fit)</text>
    <text class="fig-muted" x="255" y="205" text-anchor="middle">rotation of the line</text>
    <path class="fig-curve" d="M 80 50 Q 150 60 200 130 Q 255 175 310 130 Q 380 60 440 50"/>
    <circle class="fig-dot-muted" cx="100" cy="60"  r="3.5"/>
    <circle class="fig-dot-muted" cx="160" cy="100" r="3.5"/>
    <circle class="fig-dot-muted" cx="220" cy="155" r="3.5"/>
    <circle class="fig-dot"       cx="255" cy="166" r="5"/>
    <circle class="fig-dot-muted" cx="295" cy="155" r="3.5"/>
    <circle class="fig-dot-muted" cx="360" cy="100" r="3.5"/>
    <circle class="fig-dot-muted" cx="420" cy="60"  r="3.5"/>
    <text class="fig-accent-text" x="255" y="195" text-anchor="middle">the best line</text>
  </svg>
  <figcaption>Software finds this minimum in closed form — no rotating needed — but the picture is the point: <em>least squares</em>.</figcaption>
</figure>

## How good is the fit? Meet R²

Knowing the slope and intercept isn't enough. A non-zero slope means weight does help predict size — but *how much*?

The trick is to compare our line to the simplest possible model: just the **mean** of size, ignoring weight entirely. If our line is barely better than the mean, weight isn't really helping. If our line is dramatically better, weight matters.

We measure the mean model's badness the same way — squared distances from each point to the horizontal mean line. Call this `SS(mean)`. (It's just the total variance of size, before scaling.)

<figure class="figure">
  <svg viewBox="0 0 720 240" role="img" aria-label="Side-by-side panels. Left: points around a horizontal mean line with big dashed residuals. Right: same points around a tilted fitted line with smaller residuals.">
    <text class="fig-text" x="20" y="22">SS(mean)</text>
    <line class="fig-line" x1="50" y1="40"  x2="50"  y2="200"/>
    <line class="fig-line" x1="50" y1="200" x2="330" y2="200"/>
    <line class="fig-fit-line" x1="60" y1="120" x2="320" y2="120"/>
    <line class="fig-residual" x1="85"  y1="120" x2="85"  y2="170"/>
    <line class="fig-residual" x1="125" y1="120" x2="125" y2="85"/>
    <line class="fig-residual" x1="165" y1="120" x2="165" y2="155"/>
    <line class="fig-residual" x1="205" y1="120" x2="205" y2="70"/>
    <line class="fig-residual" x1="245" y1="120" x2="245" y2="160"/>
    <line class="fig-residual" x1="285" y1="120" x2="285" y2="75"/>
    <circle class="fig-dot" cx="85"  cy="170" r="4"/>
    <circle class="fig-dot" cx="125" cy="85"  r="4"/>
    <circle class="fig-dot" cx="165" cy="155" r="4"/>
    <circle class="fig-dot" cx="205" cy="70"  r="4"/>
    <circle class="fig-dot" cx="245" cy="160" r="4"/>
    <circle class="fig-dot" cx="285" cy="75"  r="4"/>
    <text class="fig-muted-mono" x="190" y="225" text-anchor="middle">distances from the mean</text>
    <text class="fig-text" x="390" y="22">SS(fit)</text>
    <line class="fig-line" x1="420" y1="40"  x2="420" y2="200"/>
    <line class="fig-line" x1="420" y1="200" x2="700" y2="200"/>
    <line class="fig-fit-line" x1="430" y1="170" x2="690" y2="70"/>
    <line class="fig-residual" x1="455" y1="170" x2="455" y2="158"/>
    <line class="fig-residual" x1="495" y1="138" x2="495" y2="115"/>
    <line class="fig-residual" x1="535" y1="138" x2="535" y2="125"/>
    <line class="fig-residual" x1="575" y1="104" x2="575" y2="115"/>
    <line class="fig-residual" x1="615" y1="105" x2="615" y2="88"/>
    <line class="fig-residual" x1="655" y1="78"  x2="655" y2="100"/>
    <circle class="fig-dot" cx="455" cy="158" r="4"/>
    <circle class="fig-dot" cx="495" cy="115" r="4"/>
    <circle class="fig-dot" cx="535" cy="125" r="4"/>
    <circle class="fig-dot" cx="575" cy="104" r="4"/>
    <circle class="fig-dot" cx="615" cy="88"  r="4"/>
    <circle class="fig-dot" cx="655" cy="78"  r="4"/>
    <text class="fig-muted-mono" x="560" y="225" text-anchor="middle">distances from the line</text>
  </svg>
  <figcaption><code>SS(mean)</code> is the variance the mean leaves unexplained. <code>SS(fit)</code> is what the line still can't explain. R² is built from their ratio.</figcaption>
</figure>

Then:

```
R²  =  1 − SS(fit) / SS(mean)
```

R² is the fraction of variance in size that weight explains. If R² = 0.6, that's "60% of the variation in mouse size can be explained by mouse weight."

## R² extremes

At one extreme, the line passes exactly through every point: `SS(fit) = 0`, so R² = 1 — weight explains everything. At the other extreme, the best line is flat: `SS(fit) = SS(mean)`, so R² = 0 — weight explains nothing.

<figure class="figure">
  <svg viewBox="0 0 720 240" role="img" aria-label="Two panels comparing R² extremes. Left: random scatter with horizontal best-fit line, R² near zero. Right: points lying perfectly on a tilted line, R² equal to one.">
    <text class="fig-text" x="20" y="22">R² = 0</text>
    <text class="fig-muted-mono" x="20" y="40">weight explains nothing</text>
    <line class="fig-line" x1="50" y1="60"  x2="50"  y2="200"/>
    <line class="fig-line" x1="50" y1="200" x2="330" y2="200"/>
    <line class="fig-fit-line" x1="60" y1="130" x2="320" y2="130"/>
    <circle class="fig-dot" cx="85"  cy="170" r="4"/>
    <circle class="fig-dot" cx="125" cy="85"  r="4"/>
    <circle class="fig-dot" cx="165" cy="155" r="4"/>
    <circle class="fig-dot" cx="205" cy="100" r="4"/>
    <circle class="fig-dot" cx="245" cy="170" r="4"/>
    <circle class="fig-dot" cx="285" cy="95"  r="4"/>
    <circle class="fig-dot" cx="115" cy="115" r="4"/>
    <circle class="fig-dot" cx="225" cy="140" r="4"/>
    <text class="fig-text" x="390" y="22">R² = 1</text>
    <text class="fig-muted-mono" x="390" y="40">weight explains everything</text>
    <line class="fig-line" x1="420" y1="60"  x2="420" y2="200"/>
    <line class="fig-line" x1="420" y1="200" x2="700" y2="200"/>
    <line class="fig-fit-line" x1="430" y1="180" x2="690" y2="70"/>
    <circle class="fig-dot" cx="450" cy="172" r="4"/>
    <circle class="fig-dot" cx="490" cy="155" r="4"/>
    <circle class="fig-dot" cx="530" cy="138" r="4"/>
    <circle class="fig-dot" cx="570" cy="121" r="4"/>
    <circle class="fig-dot" cx="610" cy="104" r="4"/>
    <circle class="fig-dot" cx="650" cy="87"  r="4"/>
    <circle class="fig-dot" cx="685" cy="72"  r="4"/>
  </svg>
  <figcaption>Most real data lands somewhere between these two — and R² tells you where.</figcaption>
</figure>

## More predictors: the adjusted R² trap

What if we also have tail length, and want to use both weight and tail to predict size? The model becomes a plane (`size = a × weight + b × tail + c`). The math is the same — minimize the sum of squared residuals.

There's a subtle issue: **adding any predictor can only push R² up, never down**. Even pure noise will improve R² a little by chance. So a higher R² doesn't always mean a better model — it might just mean a more complex one.

**Adjusted R²** corrects for this. It penalizes extra parameters and only rises when a new predictor genuinely earns its keep.

<figure class="figure">
  <svg viewBox="0 0 520 240" role="img" aria-label="Line chart: as predictors are added, plain R² climbs monotonically, while adjusted R² rises, peaks, and starts to fall.">
    <line class="fig-line" x1="60" y1="30"  x2="60"  y2="200"/>
    <line class="fig-line" x1="60" y1="200" x2="490" y2="200"/>
    <text class="fig-muted" x="50"  y="115" text-anchor="end">value</text>
    <text class="fig-muted" x="275" y="225" text-anchor="middle">number of predictors</text>
    <path class="fig-fit-line" d="M 80 175 L 140 140 L 200 110 L 260 85 L 320 70 L 380 60 L 440 55"/>
    <text class="fig-text" x="455" y="55">R²</text>
    <path class="fig-curve" d="M 80 175 L 140 145 L 200 125 L 260 115 L 320 120 L 380 135 L 440 155"/>
    <text class="fig-accent-text" x="455" y="155">adj. R²</text>
    <circle class="fig-dot" cx="260" cy="115" r="5"/>
    <text class="fig-muted-mono" x="260" y="100" text-anchor="middle">sweet spot</text>
  </svg>
  <figcaption>Plain R² is a hill that never descends; adjusted R² peaks where extra predictors stop earning their keep.</figcaption>
</figure>

## Is the line meaningful? The F-statistic

Even when R² looks promising, we should ask: could this fit have happened by chance? The **F-statistic** answers this by comparing how much our model improved over the mean-only model, relative to how much error is left.

```
F  =  ( SS(mean) − SS(fit) ) / ( d_fit − d_mean )
      ─────────────────────────────────────────
                SS(fit) / ( n − d_fit )
```

The numerator is "improvement per extra parameter." The denominator is "remaining error per remaining degree of freedom." Big F = the line is doing a lot of explaining for what it cost in parameters.

> With only two data points, `n − d_fit = 2 − 2 = 0` and F isn't defined. A line through two points is always perfect — but it tells you nothing about whether the relationship is real.

## From F to p-value

To know whether our F is unusually big, we compare it to the distribution of F values you'd get from data with no real relationship at all. Conceptually: generate millions of random datasets, fit a line to each, record F, plot the histogram. That's the "null distribution" of F.

The **p-value** is the fraction of those random Fs that are bigger than the F we observed. A small p-value (say below 0.05) means "this F would be rare if there were no real relationship" — the slope is probably real, not noise.

<figure class="figure">
  <svg viewBox="0 0 520 240" role="img" aria-label="Histogram of F values under the null hypothesis. Most of the area is on the left; the right tail past our observed F is shaded and labelled p-value.">
    <line class="fig-line" x1="60" y1="30"  x2="60"  y2="200"/>
    <line class="fig-line" x1="60" y1="200" x2="490" y2="200"/>
    <text class="fig-muted" x="50"  y="115" text-anchor="end">count</text>
    <text class="fig-muted" x="275" y="225" text-anchor="middle">F (under null)</text>
    <rect class="fig-bar" x="70"  y="100" width="28" height="100"/>
    <rect class="fig-bar" x="100" y="55"  width="28" height="145"/>
    <rect class="fig-bar" x="130" y="40"  width="28" height="160"/>
    <rect class="fig-bar" x="160" y="65"  width="28" height="135"/>
    <rect class="fig-bar" x="190" y="95"  width="28" height="105"/>
    <rect class="fig-bar" x="220" y="125" width="28" height="75"/>
    <rect class="fig-bar" x="250" y="150" width="28" height="50"/>
    <rect class="fig-bar" x="280" y="165" width="28" height="35"/>
    <rect class="fig-bar-tail" x="310" y="175" width="28" height="25"/>
    <rect class="fig-bar-tail" x="340" y="183" width="28" height="17"/>
    <rect class="fig-bar-tail" x="370" y="188" width="28" height="12"/>
    <rect class="fig-bar-tail" x="400" y="193" width="28" height="7"/>
    <rect class="fig-bar-tail" x="430" y="196" width="28" height="4"/>
    <line class="fig-line-accent" x1="310" y1="20" x2="310" y2="200"/>
    <text class="fig-accent-text" x="310" y="15" text-anchor="middle">your F</text>
    <text class="fig-muted-mono" x="395" y="170" text-anchor="middle">p-value = tail area</text>
  </svg>
  <figcaption>Tables (or your stats library) give you this tail area from the F value and the degrees of freedom.</figcaption>
</figure>

## Takeaway

Linear regression rests on three nested ideas:

1. **Find the line** by minimising the sum of squared residuals.
2. **Judge the fit** with R²; penalise complexity with adjusted R².
3. **Trust the fit** with the F-statistic and its p-value — is the improvement over the mean more than chance would produce?

Multiple regression, regularised regression, generalised linear models — they're all refinements of one of these three steps.
