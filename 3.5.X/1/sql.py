import sqlite3
import pandas as pd

df = pd.read_csv('currencies.csv')
df.to_sql("currencies", con=sqlite3.connect("currencies.db"), index=False)
