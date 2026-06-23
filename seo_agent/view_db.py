import sqlite3
import pandas as pd

conn = sqlite3.connect("seo_history.db")

df = pd.read_sql(
    "SELECT * FROM ranking_history",
    conn
)

print(df)

conn.close()