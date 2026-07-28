# Time Series Analysis Overview

Category: Time Series
Resource: https://youtu.be/GE3JOFwTWVM?si=0AIDvMSAJ7g7hXcF

## Time Series Analysis

A **time series** is data collected from the same entity at regular time intervals, such as sleep hours tracked every night.

Time series analysis is used to find patterns, extract insights, and forecast future values. Businesses use it for sales forecasting, inventory planning, commodity price prediction, and weather-related decisions in agriculture.

### Main Components

| Component | Meaning | Example |
| --- | --- | --- |
| Trend | Overall direction over time | Sales increasing yearly |
| Seasonality | Repeating pattern over a fixed period | Holiday sales spikes |
| Cycle | Repeating but irregular long-term pattern | Economic booms and busts |
| Variation / Noise | Random, unpredictable movement | Sudden unusual changes |

### Simple Visual

```
Hours
  ^
  |        /\        /\        /\
  |       /  \      /  \      /  \
  |______/____\____/____\____/____\____> Time
        seasonal repeating pattern
```

### Forecasting Models

**ARIMA** uses past values, differencing, and moving averages to forecast future data. It is useful when data has trends or patterns.

**Exponential smoothing** gives more weight to recent observations and less weight to older ones. It is useful for smoothing noisy data and forecasting when patterns are simple.

![image.png](image%2014.png)

### Python Tools

**pandas** is used for importing, cleaning, organizing, and analyzing time series data.

**matplotlib** is used for visualizing time series with line charts, scatter plots, and heat maps.

### Key Idea

Time series analysis helps reveal patterns in data over time and supports better predictions and decisions.