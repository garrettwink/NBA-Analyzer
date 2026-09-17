import sqlite3
import pandas as pd

conn = sqlite3.connect("nba.db")

df_stat = pd.read_sql_query("SELECT * FROM player_season_history", conn)
df_award = pd.read_sql_query("SELECT * FROM mvp_awards", conn)

df = df_stat.merge(
    df_award[['player_id', 'season', 'mvp_rank', 'points_won', 'mvp_vote_share']],
    on=['player_id', 'season'],
    how='left'
)

