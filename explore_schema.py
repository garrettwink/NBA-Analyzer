import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import sqlite3
    import pandas as pd

    conn = sqlite3.connect("nba.db")

    stat_df = pd.read_sql_query("SELECT * FROM player_season_history", conn)
    award_df = pd.read_sql_query("SELECT * FROM mvp_awards", conn)
    return award_df, stat_df


@app.cell
def _(stat_df):
    stat_df.head()
    return


@app.cell
def _(award_df):
    award_df.head()
    return


@app.cell
def _(stat_df):
    stat_df.columns
    return


@app.cell
def _(award_df):
    award_df.columns
    return


@app.cell
def _(stat_df):
    stat_df.duplicated(subset=['player_id', 'season']).sum()
    return


if __name__ == "__main__":
    app.run()
