from sqlalchemy import create_engine, text
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import os

DB_PATH = os.path.join("data", "processed", "favorita.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

selected_stores = [44, 3, 40, 16, 32]
HOLDOUT_DAYS = 90  # last 90 days used as test set

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

    # Split into train/test
    train_df = store_df.iloc[:-HOLDOUT_DAYS]
    test_df = store_df.iloc[-HOLDOUT_DAYS:]

    # Fit Prophet
    model = Prophet(yearly_seasonality=True,
                    weekly_seasonality=True, daily_seasonality=False)
    model.fit(train_df[["ds", "y"]])

    # Forecast forward over the holdout period
    future = model.make_future_dataframe(periods=HOLDOUT_DAYS)
    forecast = model.predict(future)

    # Compare predictions to actual test values
    forecast_test = forecast.set_index("ds").loc[test_df["ds"]]
    actual = test_df.set_index("ds")["y"]
    predicted = forecast_test["yhat"]

    mae = (actual - predicted).abs().mean()
    mape = ((actual - predicted).abs() / actual.replace(0, pd.NA)).mean() * 100

    print(f"Store {store}: MAE = {mae:.1f}, MAPE = {mape:.1f}%")
    results.append({"store": store, "mae": mae, "mape": mape})

    # Plot actual vs predicted for this store
    plt.figure(figsize=(10, 4))
    plt.plot(actual.index, actual.values, label="Actual", linewidth=1)
    plt.plot(predicted.index, predicted.values, label="Predicted", linewidth=1)
    plt.title(
        f"Store {store} - Actual vs Predicted (last {HOLDOUT_DAYS} days)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join("data", "processed",
                f"forecast_store_{store}.png"))
    plt.close()

results_df = pd.DataFrame(results)
print("\n--- Summary ---")
print(results_df)
results_df.to_csv(os.path.join("data", "processed",
                  "forecast_results.csv"), index=False)
print("\nResults saved to data/processed/forecast_results.csv")
