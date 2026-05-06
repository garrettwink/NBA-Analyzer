from datetime import date

from pydantic import BaseModel, Field


class StatSchema(BaseModel):
    player_id: int
    team_id: int
    season: int
    pts: float
    ast: float
    reb: float
    off_reb: float
    def_reb: float
    stl: float
    blk: float
    tov: float
    fg_pct: float
    fg3_pct: float
    ft_pct: float
    gp: int
    mpg: float
    usg_pct: float
    net_rating: float
    pie: float
    ts_pct: float
    age: float

    class Config:
        from_attributes = True

class PlayerSchema(BaseModel):
    player_id: int
    name: str
    position: str
    draft_year: str
    birth_date: date
    height: str
    weight: str

    class Config:
        from_attributes = True

class PlayerStatSchema(BaseModel):
    player_id: int
    name: str
    position: str
    draft_year: str
    birth_date: date
    height: str
    weight: str
    stats: list[StatSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True

class TeamSchema(BaseModel):
    team_id: int
    team_name: str
    season: int
    record: str
    win_pct: float
    playoff_clinch: bool
    
    class Config:
        from_attributes = True