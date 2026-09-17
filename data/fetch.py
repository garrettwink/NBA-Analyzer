import time
from typing import List

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats, leaguestandingsv3
from nba_api.stats.library.http import NBAStatsHTTP
from requests.exceptions import RequestException
from sqlalchemy.orm import sessionmaker

from data.db import engine, Players, Teams, Stats

Session = sessionmaker(bind=engine)

MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5


def safe_get_data_frame(endpoint_cls, *args, **kwargs):
    last_exc = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return endpoint_cls(*args, **kwargs).get_data_frames()[0]
        except (RequestException, NBAStatsHTTP, TimeoutError, ValueError) as exc:
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
    This is the core dataset you will later train on.
    """
    base = safe_get_data_frame(
        leaguedashplayerstats.LeagueDashPlayerStats,
        season=season,
        measure_type_detailed_defense="Base",
        per_mode_detailed="PerGame",
        timeout=60,
    )

    advanced = safe_get_data_frame(
        leaguedashplayerstats.LeagueDashPlayerStats,
        season=season,
        measure_type_detailed_defense="Advanced",
        per_mode_detailed="PerGame",
        timeout=60,
    )

    required_base = [
        "PLAYER_ID", "TEAM_ID", "GP", "PTS", "AST", "REB",
        "OREB", "DREB", "STL", "BLK", "TOV",
        "FG_PCT", "FG3_PCT", "FT_PCT"
    ]

    required_advanced = [
        "PLAYER_ID", "AGE", "MIN", "USG_PCT", "NET_RATING", "PIE", "TS_PCT"
    ]

    base = base[required_base]
    advanced = advanced[required_advanced]

    stats = pd.merge(base, advanced, on="PLAYER_ID", how="inner")
    stats["SEASON"] = int(season.split("-")[0])
    stats["MPG"] = stats["MIN"] / stats["GP"]
    stats["TEAM_ID"] = stats["TEAM_ID"].astype(int)
    stats["PLAYER_ID"] = stats["PLAYER_ID"].astype(int)

    return stats


def fetch_team_standings(season: str) -> pd.DataFrame:
    standings = safe_get_data_frame(
        leaguestandingsv3.LeagueStandingsV3,
        season=season,
        timeout=60,
    )

    required = ["TeamID", "TeamName", "Record", "WinPCT", "ClinchedPlayoffBirth"]
    standings = standings[required]

    standings["SEASON"] = int(season.split("-")[0])
    standings["TEAM_ID"] = standings["TeamID"].astype(int)
    standings["TEAM_NAME"] = standings["TeamName"]
    standings["WIN_PCT"] = standings["WinPCT"]
    standings["PLAYOFFS"] = standings["ClinchedPlayoffBirth"].fillna(False).astype(bool)

    return standings[["SEASON", "TEAM_ID", "TEAM_NAME", "Record", "WIN_PCT", "PLAYOFFS"]]


def build_historical_dataset(seasons: list[str]) -> pd.DataFrame:
    """
    One orchestrator: fetches all raw data needed for training the MVP model.
    """
    frames = []

    for season in seasons:
        player_stats = fetch_player_season_stats(season)
        team_standings = fetch_team_standings(season)

        merged = player_stats.merge(
            team_standings,
            on=["SEASON", "TEAM_ID"],
            how="left"
        )

        frames.append(merged)

    full_df = pd.concat(frames, ignore_index=True)

    # Add a target column later when you decide the actual modeling setup.
    # Example:
    # full_df["MVP_WINNER"] = ...
    # full_df["MVP_RANK"] = ...

    return full_df


def save_historical_dataset(df: pd.DataFrame):
    """
    Write to a model-focused table.
    You would normally add a dedicated table in [data/db.py](data/db.py),
    like player_season_history or award_feature_table.
    """
    with Session() as session:
        # This is just a sketch; your exact table structure depends on your schema.
        for row in df.to_dict(orient="records"):
            # Example pseudocode:
            # session.merge(PlayerSeasonHistory(**row))
            pass

        session.commit()


if __name__ == "__main__":
    seasons = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
    df = build_historical_dataset(seasons)
    print(df.head())
    save_historical_dataset(df)