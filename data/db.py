from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase

engine = create_engine('sqlite:///nba.db')


class Base(DeclarativeBase):
    pass


class Players(Base):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True)
    birth_date = Column(String)
    name = Column(String)
    position = Column(String)
    draft_year = Column(String)
    weight = Column(String)

class Teams(Base):
    __tablename__ = 'teams'
    __table_args__ = (PrimaryKeyConstraint('team_id', 'season'),)

    team_id = Column(Integer)
    team_name = Column(String)
    season = Column(Integer)
    record = Column(String)
    win_pct = Column(Float)
    playoff_clinch = Column(Boolean)


class PlayerSeasonHistory(Base):
    __tablename__ = 'player_season_history'
    __table_args__ = (PrimaryKeyConstraint('player_id', 'season', 'team_id'),)

    player_id = Column(Integer, ForeignKey('players.player_id'))
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    season = Column(Integer)

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

    team_record = Column(String)
    team_win_pct = Column(Float)
    playoff_clinch = Column(Boolean)

    mvp_winner = Column(Boolean, default=False)
    mvp_rank = Column(Integer, nullable=True)
    mvp_vote_share = Column(Float, nullable=True)


class AwardPrediction(Base):
    __tablename__ = 'award_prediction'

    id = Column(Integer, primary_key=True, autoincrement=True)
    award_name = Column(String, nullable=False)
    season = Column(Integer, nullable=False)
    predicted_player_id = Column(Integer, ForeignKey('players.player_id'))
    predicted_player_name = Column(String, nullable=False)
    predicted_team_name = Column(String, nullable=True)
    probability = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    ranking = Column(Integer, nullable=True)
    top_reasons = Column(Text, nullable=True)
    model_version = Column(String, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)