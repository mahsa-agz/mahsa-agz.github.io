---
title: "ARIMA, intuitively"
date: 2026-07-09 00:02:00 +0900
category: time-series
read_time: 9
excerpt: "What the A, I, and M actually do, why stationarity matters, and when ARIMA is still a very strong forecasting baseline."
lede: "ARIMA works by saying: the present looks like a weighted memory of the past, but only after we remove the part that keeps drifting away."
description: "An intuitive guide to ARIMA and SARIMA: what the parameters mean, why differencing matters, and when to use or avoid the model."
image: /assets/images/blog/time-series-cover.png
---

## Why ARIMA still matters

ARIMA is old, but it is still one of the clearest forecasting models to learn because it forces you to ask the right questions:

- how much does the past explain the present?
- is the series stable enough to model directly?
- do recent forecast mistakes carry information too?

It is also still a strong baseline for many regular, numeric, single-series forecasting problems.

## What the letters mean

`ARIMA(p, d, q)` has three moving parts:

- **AR** = autoregressive part. The current value depends on past values.
- **I** = integrated part. We difference the series to remove drifting level or trend.
- **MA** = moving-average error part. The current value depends on recent forecast errors.

The parameters are:

- `p`: how many lagged values we use
- `d`: how many times we difference
- `q`: how many lagged errors we use

The intuition is simpler than the full algebra:

- AR says, "recent history matters."
- I says, "model changes instead of raw levels if the raw series keeps wandering."
- MA says, "recent misses are also informative."

## The AR part: memory of past values

Suppose demand today looks a lot like demand yesterday and the day before. That is an autoregressive pattern. A simple AR model says:

`today ~= weighted average of recent days`

If the weights on the recent lags are strong, the series has a clear memory. If they are weak, the past is not helping much.

## The I part: make the series more stable

A lot of real series are not stable enough to model in raw form. Sales may rise over time. A sensor may drift. Temperature may move with seasons.

That is where differencing helps.

- First difference: `y(t) - y(t-1)`
- Seasonal difference: `y(t) - y(t-s)`

Instead of asking ARIMA to model the raw level, we ask it to model the **change**. Often the change behaves more regularly than the level itself.

This is why the `I` part is so important: it turns a wandering series into something closer to a stable one.

## The MA part: learn from recent mistakes

The moving-average part is not a moving average in the everyday smoothing sense. In ARIMA, MA means the model uses **recent forecast errors**.

If the model underestimated yesterday, maybe that underestimation contains information about today too. The MA terms let the model absorb that short-term correction behavior.

## Why stationarity matters

Classical ARIMA likes a series whose behavior is fairly stable over time:

- similar average level after differencing
- similar variance
- similar dependence structure

That is the rough idea of stationarity.

If a series is still wildly changing after sensible differencing, ARIMA starts to strain. It is best when the underlying behavior can be made fairly regular.

## Seasonal ARIMA

Many series repeat on a fixed cycle: daily traffic by weekday, monthly sales by year, electricity load by hour.

That is where **SARIMA** comes in:

`SARIMA(p, d, q)(P, D, Q)_s`

The extra seasonal terms do the same job as the ordinary ARIMA terms, but at the seasonal lag `s`.

Examples:

- monthly data with yearly seasonality: `s = 12`
- daily data with weekly seasonality: `s = 7`
- hourly data with daily seasonality: `s = 24`

If the seasonal pattern is strong and regular, SARIMA is often much better than plain ARIMA.

## When ARIMA is a good fit

ARIMA is a strong choice when:

- the timestamps are regular
- you are forecasting one main numeric series
- the data has clear autocorrelation
- differencing can make the behavior stable enough
- you need an interpretable baseline or benchmark

In those settings, ARIMA is often one of the first models worth trying seriously.

## When ARIMA is not a good fit

ARIMA is not the right default when:

- you have many external drivers and complex feature interactions
- the pattern is strongly nonlinear
- future covariates matter more than the target's own history
- you have many related series and want one global model
- the timestamps are irregular or event-based

In those cases, lag-feature models, state-space models, or modern global deep models may be better choices.

## A practical workflow

Here is a simple ARIMA workflow that keeps you out of trouble:

1. Plot the raw series.
2. Check for missing periods, shocks, trend, and seasonality.
3. Difference only as much as needed.
4. Compare a small set of candidate models instead of blindly using a huge search.
5. Validate with rolling or expanding time splits.
6. Inspect residuals. If the residuals still contain obvious structure, the model is leaving signal on the table.

The key idea is not "find the perfect `(p, d, q)` by magic." The key idea is to make sure the model assumptions roughly match the data.

## ARIMA vs simpler and more flexible alternatives

- **Compared with seasonal naive**: ARIMA should add real structure, not just copy the last cycle.
- **Compared with ETS**: ARIMA is often better when autocorrelation structure matters, while ETS is often simpler for smooth level/trend/seasonal data.
- **Compared with boosting models**: ARIMA directly models temporal dependence, while boosting models need you to engineer lags and rolling features first.

## Takeaway

ARIMA is a model for regular series with memory. If the past explains the present and differencing can make the behavior stable, ARIMA is still one of the most sensible places to start.

If you want the broader map first, go back to <a href="{{ '/blog/time-series-overview.html' | relative_url }}">the time-series overview</a>. If you want the feature-engineering view next, continue to <a href="{{ '/blog/time-series-gradient-boosting.html' | relative_url }}">gradient boosting for time series</a>.
