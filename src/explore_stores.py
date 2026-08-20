from sqlalchemy import create_engine, text
import os

DB_PATH = os.path.join("data", "processed", "favorita.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

query = """
    SELECT store_nbr,
           COUNT(*) as row_count,
           SUM(sales) as total_sales,
           AVG(sales) as avg_daily_sales,
           AVG(CASE WHEN sales = 0 THEN 1.0 ELSE 0.0 END) as zero_sales_rate
    FROM train
    WHERE family = 'GROCERY I'
    GROUP BY store_nbr
    ORDER BY total_sales DESC;
"""

with engine.connect() as conn:
    result = conn.execute(text(query))
    print(f"{'Store':<8}{'Rows':<10}{'Total Sales':<15}{'Avg Daily':<12}{'Zero Rate':<10}")
    for row in result:
        print(
            f"{row[0]:<8}{row[1]:<10}{row[2]:<15.0f}{row[3]:<12.2f}{row[4]:<10.3f}")
