from nba_api.stats.endpoints import commonplayerinfo, leaguedashplayerstats
from nba_api.stats.static import players, teams
import time
from sqlalchemy.orm import sessionmaker
from data.db import engine, Players, Teams, Stats
import pandas as pd

Session = sessionmaker(bind=engine)

def populate_players():

    with Session() as session:
        all_players = players.get_active_players()
        print(f"Found {len(all_players)} players")

        for player in all_players:
            time.sleep(0.3)  
            info = commonplayerinfo.CommonPlayerInfo(player_id = player['id'], timeout=60)
            pl = info.get_data_frames()[0]

            player_obj = Players(
                player_id = int(pl.iloc[0]['PERSON_ID']),
                birthdate = pl.iloc[0]['BIRTHDATE'],
                name = pl.iloc[0]['DISPLAY_FIRST_LAST'],
                position = pl.iloc[0]['POSITION'],
                draft_year = pl.iloc[0]['DRAFT_YEAR'],
                height = pl.iloc[0]['HEIGHT'],
                weight = pl.iloc[0]['WEIGHT']
            )

            print(f"Adding {player['full_name']}")
            session.add(player_obj)
        session.commit()


def populate_stats():

    seasons = ['2019-20', '2020-21', '2021-22', '2022-23', '2023-24', '2024-25']

    with Session() as session:

        for season in seasons:
            season_int = int(season.split('-')[0])
            stats1 = leaguedashplayerstats.LeagueDashPlayerStats(season=season, measure_type_detailed_defense='Base', timeout=60).get_data_frames()[0]
            stat_basic = stats1[['PLAYER_ID','TEAM_ID','GP','PTS','AST','REB','OREB','DREB','STL','BLK','TOV','FG_PCT','FG3_PCT','FT_PCT']]
            stats2 = leaguedashplayerstats.LeagueDashPlayerStats(season=season, measure_type_detailed_defense='Advanced', timeout=60).get_data_frames()[0]
            stat_adv = stats2[['PLAYER_ID','AGE','MIN','USG_PCT','NET_RATING','PIE','TS_PCT']]
            stats = pd.merge(stat_basic, stat_adv, on='PLAYER_ID')
            stats['MPG'] = stats['MIN'] / stats['GP']

            for index, row in stats.iterrows():
                stat_obj = Stats(
                    player_id = int(row['PLAYER_ID']),
                    team_id = int(row['TEAM_ID']),
                    season = season_int,
                    pts = row['PTS'],
                    ast = row['AST'],
                    reb = row['REB'],
                    off_reb = row['OREB'],
                    def_reb = row['DREB'],
                    stl = row['STL'],
                    blk = row['BLK'],
                    tov = row['TOV'],
                    fg_pct = row['FG_PCT'],
                    fg3_pct = row['FG3_PCT'],
                    ft_pct = row['FT_PCT'],
                    gp = row['GP'],
                    mpg = row['MPG'],
                    usg_pct = row['USG_PCT'],
                    net_rating = row['NET_RATING'],
                    pie = row['PIE'],
                    ts_pct = row['TS_PCT'],
                    age = row['AGE']
                )

                print(f"Adding {stat_obj.player_id}")
                session.merge(stat_obj)
            session.commit()

if __name__ == '__main__':
    populate_stats()


    