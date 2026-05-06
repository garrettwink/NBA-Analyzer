from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase

engine = create_engine('sqlite:///nba.db')

class Base(DeclarativeBase):
    pass

# Core player identity, info that doesn't change during a season
class Players(Base):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True)
    birth_date = Column(String)
    name = Column(String)
    position = Column(String)
    draft_year = Column(String)
    height = Column(String)
    weight = Column(String)

# Stats of each player, can have multiple team ids during one season
class Stats(Base):
    __tablename__ = 'stats'
    __table_args__ = (PrimaryKeyConstraint('player_id', 'team_id', 'season'),)

    player_id = Column(Integer, ForeignKey('players.player_id'))
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    season = Column(Integer)
    
    # Actual player stats measured - long chunk incoming
    pts = Column(Float)
    ast = Column(Float)
    reb = Column(Float)
    off_reb = Column(Float)
    def_reb = Column(Float)
    stl = Column(Float)
    blk = Column(Float)
    tov = Column(Float)
    fg_pct = Column(Float)
    fg3_pct = Column(Float)
    ft_pct = Column(Float)
    gp = Column(Integer)
    mpg = Column(Float)
    usg_pct = Column(Float)
    net_rating = Column(Float)
    pie = Column(Float)
    ts_pct = Column(Float)
    age = Column(Integer)

# Teams, only one entry per season
class Teams(Base):
    __tablename__ = 'teams'
    __table_args__ = (PrimaryKeyConstraint('team_id', 'season'),)

    team_id = Column(Integer)
    team_name = Column(String)
    season = Column(Integer)
    record = Column(String)
    win_pct = Column(Float)
    playoff_clinch = Column(Boolean)


Base.metadata.create_all(engine)


