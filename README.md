# Demand Forecasting Pipeline — Corporación Favorita Grocery Sales

A forecasting pipeline that predicts daily demand for a grocery category across stores of varying size, and translates forecast accuracy into a business-relevant service rate metric.

## Project Scope

This project forecasts daily sales for the **GROCERY I** product family — the highest-volume, most consistently-selling category in the dataset (lowest zero-sales rate among high-revenue categories).

To test model performance across different demand scales, forecasting is done independently for 5 stores, selected as follows:
1. Excluded stores with unreliable sales history (zero-sales rate > 1%)
2. From the remaining stores, sampled across the sales volume distribution (high, upper-mid, mid, lower-mid, low) rather than taking the top 5, to test whether the model generalizes across store sizes

Selected stores: **44** (highest volume), **3**, **40**, **16**, **32** (lowest volume, still clean data).

## Data Pipeline

1. Raw CSVs loaded into a local SQLite database (`load_data.py`)
2. SQL used to explore product families and rank stores by volume and data reliability (`explore_data.py`, `explore_stores.py`)
3. Scoped data pulled into Python for exploratory visualization (`eda.py`)
4. Prophet forecasting model fit per store, evaluated on a 90-day chronological holdout (`forecast.py`)
5. Forecasts translated into a simulated service rate and stockout risk (`service_rate.py`)

## EDA Findings

- All 5 stores show clear **weekly seasonality** (higher weekend sales) and a gradual **upward trend** from 2013 to 2017.
- A recurring sharp drop to near-zero sales appears roughly once a year across most stores — consistent with **Christmas Day closures**. This suggests incorporating `holidays_events.csv` would improve the model (see Limitations).
- **Store 32** shows an unusual spike cluster in late 2017, well above its typical pattern — flagged as an anomaly, not corrected for in this version.

## Forecast Accuracy (90-day holdout)

| Store | Volume Tier | MAE | MAPE |
|---|---|---|---|
| 44 | Highest | 1,171.6 | 11.3% |
| 3  | High | 935.2 | 11.3% |
| 40 | Mid | 802.0 | 14.0% |
| 16 | Lower-mid | 492.3 | 18.8% |
| 32 | Lowest | 1,040.2 | 74.6% |

**Finding:** accuracy generally degrades as store volume decreases (11.3% → 18.8% MAPE), consistent with smaller stores having noisier, proportionally more volatile demand. Store 32 is an outlier — its high error is driven by the late-2017 demand spike visible in the EDA, which the model (trained on prior history) could not anticipate. This highlights a real limitation of trend/seasonality-based forecasting: it struggles with sudden regime changes rather than gradual patterns.

## Service Rate Simulation

Simulated two stocking strategies against actual demand over the holdout period: stocking exactly to the forecast, and stocking to the forecast plus a 10% safety buffer.

| Store | Service Rate (no buffer) | Service Rate (+10% buffer) | Improvement | Avg. Daily Excess Stock (buffered) |
|---|---|---|---|---|
| 44 | 56.7% | 84.4% | +27.7pp | 1,382 units |
| 3  | 70.0% | 91.1% | +21.1pp | 1,390 units |
| 40 | 58.9% | 81.1% | +22.2pp | 799 units |
| 16 | 58.9% | 70.0% | +11.1pp | 337 units |
| 32 | 95.6% | 97.8% | +2.2pp | 1,280 units |

**Findings:**
- A flat 10% safety buffer is not equally effective across stores — Store 44 gains +27.7pp in service rate, while Store 16 gains only +11.1pp. This suggests safety stock policy should be store-specific rather than uniform, since demand volatility differs meaningfully by store.
- Store 32's high service rate despite its poor MAPE illustrates a limitation of aggregate service rate as a metric: it can mask the business impact of rare, large demand spikes — a single missed spike day may matter more operationally than many small, well-forecasted days.

## Limitations & Next Steps

- **Holidays not yet incorporated**: Prophet supports custom holiday effects; adding `holidays_events.csv` would likely improve accuracy around the Christmas dips visible in the EDA.
- **Flat safety buffer**: a store-specific buffer (e.g., based on each store's historical forecast error) would likely outperform the uniform 10% buffer used here.
- **Model choice**: Prophet was chosen for speed and interpretability. Gradient boosting models (LightGBM, XGBoost) with engineered lag and calendar features are commonly used to achieve higher accuracy on this dataset, and would be a natural next iteration.
- **Single category scope**: this project intentionally scopes to one product family (GROCERY I) and 5 stores to keep the analysis focused and fully explainable; extending to more categories/stores would follow the same pipeline.

## Tech Stack

Python (pandas, SQLAlchemy, Prophet, matplotlib), SQLite, SQL, Git/GitHub.

## Dataset

[Kaggle: Store Sales - Time Series Forecasting](https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data) — raw data excluded from this repo (see `.gitignore`); download separately and place in `data/raw/`.