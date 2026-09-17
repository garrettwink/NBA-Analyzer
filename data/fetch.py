import time

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats, leaguestandingsv3
from requests.exceptions import RequestException
from sqlalchemy.orm import sessionmaker

from db import engine, Players, Teams, PlayerSeasonHistory

Session = sessionmaker(bind=engine)

MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5


def safe_get_data_frame(endpoint_cls, *args, **kwargs):
    last_exc = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return endpoint_cls(*args, **kwargs).get_data_frames()[0]
        except (RequestException, TimeoutError, ValueError) as exc:
            last_exc = exc
            if attempt == MAX_RETRIES:
                break
            wait = BACKOFF_FACTOR * attempt
            print(f"Request failed ({attempt}/{MAX_RETRIES}): {exc}. Retrying in {wait:.1f}s...")
            time.sleep(wait)

    raise last_exc


def fetch_player_season_stats(season: str) -> pd.DataFrame:
    """
    Pull player-season stats needed for MVP modeling.
    Column names here are already aligned to db.py's Stats / PlayerSeasonHistory schema.
    """
    base = safe_get_data_frame(
        leaguedashplayerstats.LeagueDashPlayerStats,
        season=season,
        measure_type_detailed_defense="Base",
        per_mode_detailed="PerGame",
        timeout=120,
    )

    advanced = safe_get_data_frame(
        leaguedashplayerstats.LeagueDashPlayerStats,
        season=season,
        measure_type_detailed_defense="Advanced",
        per_mode_detailed="PerGame",
        timeout=120,
    )

    required_base = [
        "PLAYER_ID", "PLAYER_NAME", "TEAM_ID", "GP", "PTS", "AST", "REB",
        "OREB", "DREB", "STL", "BLK", "TOV",
        "FG_PCT", "FG3_PCT", "FT_PCT",
    ]

    required_advanced = [
        "PLAYER_ID", "AGE", "MIN", "USG_PCT", "NET_RATING", "PIE", "TS_PCT",
    ]

    base = base[required_base]
    advanced = advanced[required_advanced]

    stats = pd.merge(base, advanced, on="PLAYER_ID", how="inner")

    stats = stats.rename(columns={
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
    })

    stats["season"] = int(season.split("-")[0])
    stats["mpg"] = stats["min"] / stats["gp"]
    stats["team_id"] = stats["team_id"].astype(int)
    stats["player_id"] = stats["player_id"].astype(int)
    stats["age"] = stats["age"].astype(int)

    return stats.drop(columns=["min"])


def fetch_team_standings(season: str) -> pd.DataFrame:
    standings = safe_get_data_frame(
        leaguestandingsv3.LeagueStandingsV3,
        season=season,
        timeout=120,
    )

    required = ["TeamID", "TeamName", "Record", "WinPCT", "ClinchedPlayoffBirth"]
    standings = standings[required]

    standings = standings.rename(columns={
        "TeamID": "team_id",
        "TeamName": "team_name",
        "Record": "record",
        "WinPCT": "win_pct",
    })

    standings["season"] = int(season.split("-")[0])
    standings["team_id"] = standings["team_id"].astype(int)
    standings["playoff_clinch"] = standings["ClinchedPlayoffBirth"].fillna(False).astype(bool)

    return standings[["season", "team_id", "team_name", "record", "win_pct", "playoff_clinch"]]


def build_historical_dataset(seasons: list[str]) -> pd.DataFrame:
    """
    One orchestrator: fetches all raw data needed for training the MVP model.
    Returns a single df shaped for PlayerSeasonHistory (plus a 'player_name'
    helper column used only to upsert the Players reference table).
    """
    frames = []

    for season in seasons:
        print(f"Fetching {season}...", flush=True)
        player_stats = fetch_player_season_stats(season)
        team_standings = fetch_team_standings(season)
        time.sleep(1)

        merged = player_stats.merge(
            team_standings,
            on=["season", "team_id"],
            how="left",
        )

        merged = merged.rename(columns={
            "record": "team_record",
            "win_pct": "team_win_pct",
        })

        frames.append(merged)

    full_df = pd.concat(frames, ignore_index=True)

    # Target columns - fill in once labeling strategy (e.g. scraping actual
    # MVP voting results) is decided.
    full_df["mvp_winner"] = False
    full_df["mvp_rank"] = None
    full_df["points_won"] = None
    full_df["mvp_vote_share"] = None

    return full_df


PLAYER_SEASON_HISTORY_COLS = [
    "player_id", "team_id", "season", "pts", "ast", "reb", "off_reb", "def_reb",
    "stl", "blk", "tov", "fg_pct", "fg3_pct", "ft_pct", "gp", "mpg", "usg_pct",
    "net_rating", "pie", "ts_pct", "age", "team_record", "team_win_pct",
    "playoff_clinch", "mvp_winner", "mvp_rank", "mvp_vote_share",
]

STATS_COLS = [
    "player_id", "team_id", "season", "pts", "ast", "reb", "off_reb", "def_reb",
    "stl", "blk", "tov", "fg_pct", "fg3_pct", "ft_pct", "gp", "mpg", "usg_pct",
    "net_rating", "pie", "ts_pct", "age",
]


def save_historical_dataset(df: pd.DataFrame):
    """
    Upserts into Players, Teams, Stats, and PlayerSeasonHistory.
    Uses session.merge() so re-running for the same season/player/team is safe.
    """
    with Session() as session:
        # --- Players (dedupe by player_id, keep latest name seen) ---
        players = df[["player_id", "player_name"]].drop_duplicates("player_id", keep="last")
        for row in players.to_dict(orient="records"):
            session.merge(Players(player_id=row["player_id"], name=row["player_name"]))

        # --- Teams (dedupe by team_id + season) ---
        teams = df[["team_id", "season", "team_name", "team_record", "team_win_pct", "playoff_clinch"]] \
            .drop_duplicates(["team_id", "season"], keep="last")
        for row in teams.to_dict(orient="records"):
            session.merge(Teams(
                team_id=row["team_id"],
                season=row["season"],
                team_name=row["team_name"],
                record=row["team_record"],
                win_pct=row["team_win_pct"],
                playoff_clinch=row["playoff_clinch"],
            ))

        # --- PlayerSeasonHistory (model-ready table) ---
        for row in df[PLAYER_SEASON_HISTORY_COLS].to_dict(orient="records"):
            session.merge(PlayerSeasonHistory(**row))

        session.commit()


if __name__ == "__main__":
    seasons = [f"{year}-{str(year + 1)[-2:]}" for year in range(2010, 2025)]
    df = build_historical_dataset(seasons)
    print(df.head())
    save_historical_dataset(df)