from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class players(Base):
    __tablename__ = 'Players'

    player_id = Column(Integer, primary_key=True)
    name = Column(String)
    position = Column(String)
    draft_year = Column(Integer)

