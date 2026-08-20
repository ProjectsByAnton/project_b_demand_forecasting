from sqlalchemy import create_engine, text
import os

DB_PATH = os.path.join("data", "processed", "favorita.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

queries = {
    "Unique stores": "SELECT COUNT(DISTINCT store_nbr) FROM train;",
    "Unique product families": "SELECT COUNT(DISTINCT family) FROM train;",
    "Date range": "SELECT MIN(date), MAX(date) FROM train;",
    "Rows per family (top 10)": """
        SELECT family, COUNT(*) as row_count, SUM(sales) as total_sales
        FROM train
        GROUP BY family
        ORDER BY total_sales DESC
        LIMIT 10;
    """,
    "Zero-sales rate by family (top 10 most consistent)": """
        SELECT family,
               AVG(CASE WHEN sales = 0 THEN 1.0 ELSE 0.0 END) as zero_sales_rate,
               AVG(sales) as avg_sales
        FROM train
        GROUP BY family
        ORDER BY zero_sales_rate ASC
        LIMIT 10;
    """,
}

with engine.connect() as conn:
    for label, query in queries.items():
        print(f"\n--- {label} ---")
        result = conn.execute(text(query))
        for row in result:
            print(row)
