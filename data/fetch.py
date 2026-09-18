import time

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats, leaguestandingsv3
from requests.exceptions import RequestException
from sqlalchemy.orm import sessionmaker

from clean import (
    add_empty_mvp_labels,
    clean_player_stats,
    clean_team_standings,
    combine_player_and_team_data,
)
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

    return clean_player_stats(base, advanced, season)


def fetch_team_standings(season: str) -> pd.DataFrame:
    standings = safe_get_data_frame(
        leaguestandingsv3.LeagueStandingsV3,
        season=season,
        timeout=120,
    )

    return clean_team_standings(standings, season)


def build_historical_dataset(seasons: list[str]) -> pd.DataFrame:
    """
    One orchestrator: fetches all raw data needed for training the MVP model.
    Returns a single df shaped for PlayerSeasonHistory (plus a 'player_name'
    helper column used only to upsert the Players reference table).
    """
    frames = []

    for season in seasons:
        print(f"Fetching {season}", flush=True)
        player_stats = fetch_player_season_stats(season)
        team_standings = fetch_team_standings(season)
        time.sleep(1)

        frames.append(combine_player_and_team_data(player_stats, team_standings))

    full_df = add_empty_mvp_labels(pd.concat(frames, ignore_index=True))
    leading_cols = ["player_id", "player_name", "team_id", "team_name"]
    remaining_cols = [column for column in full_df.columns if column not in leading_cols]
    return full_df[leading_cols + remaining_cols]


PLAYER_SEASON_HISTORY_COLS = [
    "player_id", "player_name", "team_id", "team_name", "season", "pts", "ast", "reb", "off_reb", "def_reb",
    "stl", "blk", "tov", "fg_pct", "fg3_pct", "ft_pct", "gp", "mpg", "usg_pct",
    "net_rating", "pie", "ts_pct", "age", "team_record", "team_win_pct",
    "playoff_clinch"
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
    seasons = [f"{year}-{str(year + 1)[-2:]}" for year in range(2010, 2026)]
    df = build_historical_dataset(seasons)
    print(df.head())
    save_historical_dataset(df)