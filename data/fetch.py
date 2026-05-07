from nba_api.stats.endpoints import commonplayerinfo, leaguedashplayerstats, leaguestandingsv3
from nba_api.stats.library.http import NBAStatsHTTP
import time
from requests.exceptions import RequestException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from data.db import engine, Players, Teams, Stats
import pandas as pd

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


def ensure_columns(df, required_columns, source_name):
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns from {source_name}: {missing}")
    return df


def populate_players():

    with Session() as session:
        player_ids = session.execute(select(Stats.player_id).distinct()).scalars().all()

        for player_id in player_ids:
            time.sleep(0.3)
            try:
                pl = safe_get_data_frame(commonplayerinfo.CommonPlayerInfo, player_id=player_id, timeout=60)
                player_obj = Players(
                    player_id=int(pl.iloc[0]['PERSON_ID']),
                    birth_date=pl.iloc[0]['BIRTHDATE'],
                    name=pl.iloc[0]['DISPLAY_FIRST_LAST'],
                    position=pl.iloc[0]['POSITION'],
                    draft_year=pl.iloc[0]['DRAFT_YEAR'],
                    height=pl.iloc[0]['HEIGHT'],
                    weight=pl.iloc[0]['WEIGHT'],
                )
                print(f"Adding {pl.iloc[0]['DISPLAY_FIRST_LAST']}")
                session.merge(player_obj)
                session.commit()
            except Exception as exc:
                session.rollback()
                print(f"Failed to fetch or save player {player_id}: {exc}")
                continue


def populate_stats():

    seasons = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25', '2025-26']

    with Session() as session:

        for season in seasons:
            try:
                season_int = int(season.split('-')[0])
                stats1 = safe_get_data_frame(
                    leaguedashplayerstats.LeagueDashPlayerStats,
                    season=season,
                    measure_type_detailed_defense='Base',
                    per_mode_detailed='PerGame',
                    timeout=60,
                )
                stats1 = ensure_columns(
                    stats1,
                    ['PLAYER_ID', 'TEAM_ID', 'GP', 'PTS', 'AST', 'REB', 'OREB', 'DREB', 'STL', 'BLK', 'TOV', 'FG_PCT', 'FG3_PCT', 'FT_PCT'],
                    f'base stats {season}',
                )

                stats2 = safe_get_data_frame(
                    leaguedashplayerstats.LeagueDashPlayerStats,
                    season=season,
                    measure_type_detailed_defense='Advanced',
                    per_mode_detailed='PerGame',
                    timeout=60,
                )
                stat_basic = stats1[['PLAYER_ID', 'TEAM_ID', 'GP', 'PTS', 'AST', 'REB', 'OREB', 'DREB', 'STL', 'BLK', 'TOV', 'FG_PCT', 'FG3_PCT', 'FT_PCT']]

                stats2 = ensure_columns(
                    stats2,
                    ['PLAYER_ID', 'AGE', 'MIN', 'USG_PCT', 'NET_RATING', 'PIE', 'TS_PCT'],
                    f'advanced stats {season}',
                )

                stat_adv = stats2[['PLAYER_ID', 'AGE', 'MIN', 'USG_PCT', 'NET_RATING', 'PIE', 'TS_PCT']]
                stats = pd.merge(stat_basic, stat_adv, on='PLAYER_ID')
                stats['MPG'] = stats['MIN'] / stats['GP']

                for index, row in stats.iterrows():
                    try:
                        stat_obj = Stats(
                            player_id=int(row['PLAYER_ID']),
                            team_id=int(row['TEAM_ID']),
                            season=season_int,
                            pts=row['PTS'],
                            ast=row['AST'],
                            reb=row['REB'],
                            off_reb=row['OREB'],
                            def_reb=row['DREB'],
                            stl=row['STL'],
                            blk=row['BLK'],
                            tov=row['TOV'],
                            fg_pct=row['FG_PCT'],
                            fg3_pct=row['FG3_PCT'],
                            ft_pct=row['FT_PCT'],
                            gp=row['GP'],
                            mpg=row['MPG'],
                            usg_pct=row['USG_PCT'],
                            net_rating=row['NET_RATING'],
                            pie=row['PIE'],
                            ts_pct=row['TS_PCT'],
                            age=row['AGE'],
                        )
                        print(f"Adding {stat_obj.player_id}")
                        session.merge(stat_obj)
                    except Exception as row_exc:
                        print(f"Skipping stat row {index} for season {season}: {row_exc}")
                        continue
                session.commit()
            except Exception as exc:
                session.rollback()
                print(f"Failed to fetch or save stats for season {season}: {exc}")
                continue


def populate_teams():
    seasons = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25', '2025-26']

    with Session() as session:
        for season in seasons:
            try:
                season_int = int(season.split('-')[0])
                stats = safe_get_data_frame(leaguestandingsv3.LeagueStandingsV3, season=season, timeout=60)
                stats = ensure_columns(
                    stats,
                    ['TeamID', 'TeamName', 'Record', 'WinPCT', 'ClinchedPlayoffBirth'],
                    f'team standings {season}',
                )

                for index, row in stats.iterrows():
                    try:
                        playoffs = bool(row['ClinchedPlayoffBirth']) if not pd.isna(row['ClinchedPlayoffBirth']) else False
                        team_obj = Teams(
                            team_id=row['TeamID'],
                            team_name=row['TeamName'],
                            season=season_int,
                            record=row['Record'],
                            win_pct=row['WinPCT'],
                            playoff_clinch=playoffs,
                        )
                        print(f"Adding {team_obj.team_name}")
                        session.merge(team_obj)
                    except Exception as row_exc:
                        print(f"Skipping team row {index} for season {season}: {row_exc}")
                        continue
                session.commit()
            except Exception as exc:
                session.rollback()
                print(f"Failed to fetch or save teams for season {season}: {exc}")
                continue


if __name__ == '__main__':
    populate_stats()
    populate_players()
    populate_teams()


    