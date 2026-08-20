from sqlalchemy import create_engine, text
import pandas as pd
from prophet import Prophet
import os

DB_PATH = os.path.join("data", "processed", "favorita.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

selected_stores = [44, 3, 40, 16, 32]
HOLDOUT_DAYS = 90
SAFETY_BUFFER = 1.10  # stock 10% above forecast as a safety margin

query = f"""
    SELECT date, store_nbr, sales
    FROM train
    WHERE family = 'GROCERY I'
    AND store_nbr IN ({','.join(map(str, selected_stores))})
    ORDER BY store_nbr, date;
"""

df = pd.read_sql(text(query), engine, parse_dates=["date"])

results = []

for store in selected_stores:
    store_df = df[df["store_nbr"] == store].copy()
    store_df = store_df.rename(columns={"date": "ds", "sales": "y"})

    train_df = store_df.iloc[:-HOLDOUT_DAYS]
    test_df = store_df.iloc[-HOLDOUT_DAYS:]

    model = Prophet(yearly_seasonality=True,
                    weekly_seasonality=True, daily_seasonality=False)
    model.fit(train_df[["ds", "y"]])

    future = model.make_future_dataframe(periods=HOLDOUT_DAYS)
    forecast = model.predict(future)

    forecast_test = forecast.set_index("ds").loc[test_df["ds"]]
    actual = test_df.set_index("ds")["y"]
    predicted = forecast_test["yhat"]

    # Simulate stocking decisions
    stock_no_buffer = predicted
    stock_with_buffer = predicted * SAFETY_BUFFER

    stockout_days_no_buffer = (actual > stock_no_buffer).sum()
    stockout_days_with_buffer = (actual > stock_with_buffer).sum()

    service_rate_no_buffer = 100 * (1 - stockout_days_no_buffer / len(actual))
    service_rate_with_buffer = 100 * \
        (1 - stockout_days_with_buffer / len(actual))

    # Average excess stock (waste risk) with buffer
    avg_excess_with_buffer = (stock_with_buffer - actual).clip(lower=0).mean()

    print(f"\nStore {store}:")
    print(
        f"  Service rate (no buffer):   {service_rate_no_buffer:.1f}%  ({stockout_days_no_buffer} stockout days / {len(actual)})")
    print(
        f"  Service rate (+10% buffer): {service_rate_with_buffer:.1f}%  ({stockout_days_with_buffer} stockout days / {len(actual)})")
    print(
        f"  Avg daily excess stock (with buffer): {avg_excess_with_buffer:.1f} units")

    results.append({
        "store": store,
        "service_rate_no_buffer": service_rate_no_buffer,
        "service_rate_with_buffer": service_rate_with_buffer,
        "avg_excess_with_buffer": avg_excess_with_buffer,
    })

results_df = pd.DataFrame(results)
print("\n--- Summary ---")
print(results_df)
results_df.to_csv(os.path.join("data", "processed",
                  "service_rate_results.csv"), index=False)
print("\nSaved to data/processed/service_rate_results.csv")
