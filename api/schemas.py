from pydantic import BaseModel

class PlayerSchema(BaseModel):
    player_id: int
    name: str
    position: str
    draft_year: str
    birth_date: str
    height: int
    weight: int
    
    class Config:
        from_attributes = True