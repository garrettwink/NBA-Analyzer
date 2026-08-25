import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import sqlite3
    import pandas as pd

    conn = sqlite3.connect("nba.db")
    stats = pd.read_sql_query("SELECT * FROM stats", conn)
    stats.head()

    names = pd.read_sql_query("SELECT player_id, name FROM players", conn)
    return


if __name__ == "__main__":
    app.run()
