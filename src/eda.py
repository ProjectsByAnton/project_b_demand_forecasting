from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt
import os

DB_PATH = os.path.join("data", "processed", "favorita.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

selected_stores = [44, 3, 40, 16, 32]

query = f"""
    SELECT date, store_nbr, sales
    FROM train
    WHERE family = 'GROCERY I'
    AND store_nbr IN ({','.join(map(str, selected_stores))})
    ORDER BY store_nbr, date;
"""

df = pd.read_sql(text(query), engine, parse_dates=["date"])
print(df.head())
print(f"\nTotal rows: {len(df)}")

# Plot each store's sales over time
fig, axes = plt.subplots(len(selected_stores), 1,
                         figsize=(12, 14), sharex=True)
for ax, store in zip(axes, selected_stores):
    store_data = df[df["store_nbr"] == store]
    ax.plot(store_data["date"], store_data["sales"], linewidth=0.7)
    ax.set_title(f"Store {store} - GROCERY I Daily Sales")
    ax.set_ylabel("Sales")

plt.tight_layout()
plt.savefig(os.path.join("data", "processed", "store_sales_eda.png"))
print("\nPlot saved to data/processed/store_sales_eda.png")
plt.show()
