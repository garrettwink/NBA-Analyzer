import pandas as pd


PLAYER_STATS_BASE_COLS = [
	"PLAYER_ID", "PLAYER_NAME", "TEAM_ID", "GP", "PTS", "AST", "REB",
	"OREB", "DREB", "STL", "BLK", "TOV", "FG_PCT", "FG3_PCT", "FT_PCT",
]

PLAYER_STATS_ADVANCED_COLS = [
	"PLAYER_ID", "AGE", "MIN", "USG_PCT", "NET_RATING", "PIE", "TS_PCT",
]

PLAYER_STATS_RENAME = {
	"PLAYER_ID": "player_id",
	"PLAYER_NAME": "player_name",
	"TEAM_ID": "team_id",
	"GP": "gp",
	"PTS": "pts",
	"AST": "ast",
	"REB": "reb",
	"OREB": "off_reb",
	"DREB": "def_reb",
	"STL": "stl",
	"BLK": "blk",
	"TOV": "tov",
	"FG_PCT": "fg_pct",
	"FG3_PCT": "fg3_pct",
	"FT_PCT": "ft_pct",
	"AGE": "age",
	"MIN": "min",
	"USG_PCT": "usg_pct",
	"NET_RATING": "net_rating",
	"PIE": "pie",
	"TS_PCT": "ts_pct",
}


def clean_player_stats(
	base: pd.DataFrame,
	advanced: pd.DataFrame,
	season: str,
) -> pd.DataFrame:
	"""Normalize base and advanced NBA API data into player-season stats."""
	base = base[PLAYER_STATS_BASE_COLS]
	advanced = advanced[PLAYER_STATS_ADVANCED_COLS]

	stats = base.merge(advanced, on="PLAYER_ID", how="inner")
	stats = stats.rename(columns=PLAYER_STATS_RENAME)
	stats["season"] = int(season.split("-")[0])
	stats["mpg"] = stats["min"] / stats["gp"]
	stats["team_id"] = stats["team_id"].astype(int)
	stats["player_id"] = stats["player_id"].astype(int)
	stats["age"] = stats["age"].astype(int)

	return stats.drop(columns=["min"])


def clean_team_standings(standings: pd.DataFrame, season: str) -> pd.DataFrame:
	"""Normalize NBA API standings into season-specific team records."""
	required_cols = [
		"TeamID", "TeamName", "Record", "WinPCT", "ClinchedPlayoffBirth",
	]
	standings = standings[required_cols].rename(columns={
		"TeamID": "team_id",
		"TeamName": "team_name",
		"Record": "record",
		"WinPCT": "win_pct",
	})

	standings["season"] = int(season.split("-")[0])
	standings["team_id"] = standings["team_id"].astype(int)
	standings["playoff_clinch"] = (
		standings["ClinchedPlayoffBirth"].fillna(False).astype(bool)
	)

	return standings[
		["season", "team_id", "team_name", "record", "win_pct", "playoff_clinch"]
	]


def combine_player_and_team_data(
	player_stats: pd.DataFrame,
	team_standings: pd.DataFrame,
) -> pd.DataFrame:
	"""Attach season-specific team context to player-season stats."""
	return (
		player_stats
		.merge(team_standings, on=["season", "team_id"], how="left")
		.rename(columns={
			"record": "team_record",
			"win_pct": "team_win_pct",
		})
	)


def add_empty_mvp_labels(history: pd.DataFrame) -> pd.DataFrame:
	"""Add placeholder target columns until award labels are joined."""
	history = history.copy()
	history["mvp_winner"] = False
	history["mvp_rank"] = None
	history["points_won"] = None
	history["mvp_vote_share"] = None
	return history
