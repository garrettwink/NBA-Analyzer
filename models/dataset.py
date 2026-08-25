import sqlite3
import pandas as pd

conn = sqlite3.connect("nba.db")
df = pd.read_sql_query("SELECT * FROM stats", conn)

print(df.head())