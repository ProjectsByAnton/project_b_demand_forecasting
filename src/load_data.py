import pandas as pd
from sqlalchemy import create_engine
import os

# Paths
RAW_DIR = os.path.join("data", "raw")
DB_PATH = os.path.join("data", "processed", "favorita.db")

# Create the database engine (creates the .db file if it doesn't exist)
engine = create_engine(f"sqlite:///{DB_PATH}")

# Map each CSV to a table name
files_to_load = {
    "train.csv": "train",
    "stores.csv": "stores",
    "oil.csv": "oil",
    "holidays_events.csv": "holidays_events",
    "transactions.csv": "transactions",
    "test.csv": "test",
}

for filename, table_name in files_to_load.items():
    filepath = os.path.join(RAW_DIR, filename)
    print(f"Loading {filename} into table '{table_name}'...")
    df = pd.read_csv(filepath)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"  -> {len(df):,} rows loaded.")

print("\nDone. Database created at:", DB_PATH)