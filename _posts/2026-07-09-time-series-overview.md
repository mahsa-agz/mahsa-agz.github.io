---
title: "Time series, intuitively"
date: 2026-07-09 00:03:00 +0900
category: time-series
read_time: 12
excerpt: "A practical overview of time-series data: the core terms, the main problem types, common traps, and a choose-the-method cheat sheet."
lede: "Time series is not just data with dates. The order matters, the future cannot leak into the past, and the best method depends on the pattern in the series as much as on raw accuracy."
description: "An intuitive overview of time-series analysis: basic terms, types of time-series problems, common evaluation traps, and when to use popular forecasting methods."
image: /assets/images/blog/time-series-cover.png
---

## Why time series is different

In ordinary tabular machine learning, we often pretend each row is independent. Time series breaks that assumption immediately. Yesterday affects today. Last winter affects this winter. A promotion, a holiday, or a sensor failure can leave a pattern that echoes forward in time.

That is why time-series work is mostly about **structure**:

- structure in **order**
- structure in **repetition**
- structure in **change**

If we ignore that structure, we usually get two problems: a misleadingly strong validation score and a weak real-world forecast.

## Basic terms

- **Timestamp**: the moment attached to each observation.
- **Frequency / granularity**: how often the data arrives, such as hourly, daily, weekly, or monthly.
- **Lag**: a past value used to explain the present, such as `y(t-1)` or `y(t-7)`.
- **Forecast horizon**: how far ahead we want to predict. Forecasting tomorrow is a different problem from forecasting the next 12 months.
- **Trend**: a long-run upward or downward movement.
- **Seasonality**: a pattern that repeats on a known cycle, such as every day, week, or year.
- **Cycle**: a broader rise-and-fall pattern without a perfectly fixed period.
- **Noise**: the part that looks random after the main patterns are removed.
- **Stationarity**: a rough way of saying the statistical behavior stays stable over time. Many classical models like this.
- **Autocorrelation**: the idea that the series is correlated with its own past.
- **Exogenous variables**: outside drivers that may help prediction, such as price, weather, promotions, or holidays.
- **Leakage**: using future information when training a model. This is one of the easiest ways to fool yourself in time series.

## Different kinds of series

Not every time series behaves the same way. A good first question is: *what kind of series am I dealing with?*

- **Univariate vs multivariate**: one measured signal, or several related signals moving together.
- **Regular vs irregular**: evenly spaced timestamps, or events arriving at uneven times.
- **Stationary vs non-stationary**: roughly stable behavior, or a series whose mean/variance/pattern keeps drifting.
- **Single-series vs many related series**: one product, or thousands of products/stores/sensors that might benefit from one global model.
- **Smooth vs intermittent**: continuous demand, or long runs of zeros with sudden spikes.

## Different kinds of tasks

People often use "time series" to mean forecasting, but the field is broader than that.

- **Forecasting**: predict future values.
- **Nowcasting / imputation**: estimate the present or fill missing values.
- **Anomaly detection**: find behavior that breaks the usual pattern.
- **Change-point detection**: identify when the system shifted.
- **Classification**: assign a label to a sequence, such as normal vs faulty.
- **Segmentation / representation learning**: compress or summarize long sequences into useful features.

The method table below focuses on **forecasting**, because that is usually where people start.

## Before choosing a method

There is a practical order that helps more than jumping straight to the fanciest model:

1. Plot the series.
2. Identify trend, seasonality, missing periods, outliers, and shocks.
3. Build a naive baseline, especially a seasonal naive baseline if seasonality exists.
4. Split train, validation, and test **by time**, never randomly.
5. Choose an error metric that matches the business cost.

Some common metric choices:

- **MAE** when you want a direct average error in the original units.
- **RMSE** when large mistakes should hurt more.
- **MAPE / sMAPE** when relative error matters, but be careful around zeros.
- **Pinball loss** when you care about prediction intervals or quantiles, not only point forecasts.

## A quick mental map

If you only remember one thing, remember this:

- start simple
- beat the seasonal naive baseline
- let the data pattern decide the model family

For many real projects, a strong workflow beats a fashionable architecture.

## Forecasting method cheat sheet

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Method</th>
        <th>Use it when</th>
        <th>Avoid it when</th>
        <th>Notes</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Naive / seasonal naive</strong></td>
        <td>You need a trustworthy baseline and the series has a clear recent level or repeating seasonal pattern.</td>
        <td>You are treating it as the final answer for a complex forecasting problem.</td>
        <td>Every serious forecast should beat this baseline. If it does not, the rest of the pipeline needs inspection.</td>
      </tr>
      <tr>
        <td><strong>ETS / Holt-Winters</strong></td>
        <td>The pattern is mostly level, trend, and seasonality, and you want an interpretable short- to medium-horizon forecast.</td>
        <td>The data has many external drivers, abrupt regime changes, or strong nonlinear interactions.</td>
        <td>Excellent classical baseline for business data. Usually one of the first methods worth trying.</td>
      </tr>
      <tr>
        <td><strong>ARIMA / SARIMA</strong></td>
        <td>You have a regular univariate series with autocorrelation, and differencing can make the behavior more stable.</td>
        <td>The problem is highly nonlinear, very irregular, or driven by many covariates you need to model directly.</td>
        <td>Still one of the most useful classical families. <a href="{{ '/blog/time-series-arima.html' | relative_url }}">Deep dive</a>.</td>
      </tr>
      <tr>
        <td><strong>SARIMAX / dynamic regression</strong></td>
        <td>You have a mostly linear series plus a few external drivers whose future values are known or can be forecasted.</td>
        <td>You have dozens of weak covariates, unknown future drivers, or complex nonlinear effects.</td>
        <td>Good bridge between pure time-series models and regression with covariates.</td>
      </tr>
      <tr>
        <td><strong>VAR / multivariate autoregression</strong></td>
        <td>Several series influence one another and you care about their joint dynamics.</td>
        <td>You have many variables but short history, or the relationships are strongly nonlinear.</td>
        <td>Useful in economics and systems work, but parameter count grows quickly.</td>
      </tr>
      <tr>
        <td><strong>Prophet</strong></td>
        <td>You want a quick, readable business forecast with trend, seasonality, and holiday effects.</td>
        <td>You expect it to automatically solve messy high-frequency data or very complex nonlinear behavior.</td>
        <td>Fast to operationalize, but not magic. Good productivity model, not a guaranteed accuracy winner.</td>
      </tr>
      <tr>
        <td><strong>Gradient boosting with lagged features</strong></td>
        <td>You have rich calendar, event, weather, pricing, or cross-sectional features and expect nonlinear interactions.</td>
        <td>You have tiny data, no useful features beyond the target history, or you have not engineered lag/rolling features carefully.</td>
        <td>Often a very strong practical baseline in industry. <a href="{{ '/blog/time-series-gradient-boosting.html' | relative_url }}">Deep dive</a>.</td>
      </tr>
      <tr>
        <td><strong>LSTM / GRU</strong></td>
        <td>You have a large amount of sequential data and believe long nonlinear dependencies matter.</td>
        <td>You are using it by default on a small or medium tabular business dataset.</td>
        <td>Famous and flexible, but often beaten by simpler baselines unless data scale is large.</td>
      </tr>
      <tr>
        <td><strong>Modern global deep models</strong><br><code>N-BEATS</code>, <code>TFT</code>, <code>PatchTST</code></td>
        <td>You have many related series, enough data volume, and a real reason to trade simplicity for scale.</td>
        <td>Interpretability, lightweight deployment, or limited data matter more than leaderboard performance.</td>
        <td>These are among the more modern forecasting families. They shine most in large-scale multi-series settings.</td>
      </tr>
    </tbody>
  </table>
</div>

### One special case worth remembering

If your data has **intermittent demand** with long runs of zeros, ordinary models often behave badly. That is where methods like **Croston** and related inventory-focused approaches become useful. They are not general-purpose forecasting models, but they matter a lot in the right setting.

## A simple rule for choosing methods

You can often narrow the field with four questions:

1. Is the data mostly one series or many related series?
2. Do I have important external drivers?
3. Is the pattern mostly linear and seasonal, or strongly nonlinear?
4. Do I care more about interpretability, raw accuracy, or scale?

That usually leads to a sensible starting point:

- **One clean series, few covariates**: ETS or ARIMA.
- **One clean series plus known external drivers**: SARIMAX or boosting with lagged features.
- **Many related series with lots of history**: modern global models.
- **Need a baseline right now**: seasonal naive, then ETS.

## First deep dives

I started the method details with two pages that make a good pair:

- <a href="{{ '/blog/time-series-arima.html' | relative_url }}">ARIMA, intuitively</a> for the classical statistical view.
- <a href="{{ '/blog/time-series-gradient-boosting.html' | relative_url }}">Gradient boosting for time series, intuitively</a> for the feature-engineering-and-ML view.

More method pages can grow from here, but these two already show the two most common mindsets:

- model the time dependence directly
- or turn history into features and let a supervised learner do the rest

## Takeaway

Time series is mostly a discipline of respecting order. Once you do that, the method choice becomes much less mysterious: start with the pattern in the data, match the model family to that pattern, and only then worry about adding complexity.
