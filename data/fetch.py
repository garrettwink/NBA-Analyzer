from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.static import players
import time
from sqlalchemy.orm import sessionmaker
from data.db import engine, Players, Teams, Stats

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

if __name__ == '__main__':
    populate_players()


    