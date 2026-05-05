from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Core player identity, info that doesn't change during a season
class Players(Base):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    position = Column(String)
    draft_year = Column(Integer)

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
    win_shares = Column(Float)
    vorp = Column(Float)
    per = Column(Float)
    usg_pct = Column(Float)

# Teams, only one entry per season
class Teams(Base):
    __tablename__ = 'teams'
    __table_args__ = (PrimaryKeyConstraint('team_id', 'season'),)

    team_id = Column(Integer)
    season = Column(Integer)
    record = Column(String)
    playoffs = Column(Boolean)
    championship = Column(Boolean)

# engine and table creation
engine = create_engine('sqlite:///nba.db')
Base.metadata.create_all(engine)


