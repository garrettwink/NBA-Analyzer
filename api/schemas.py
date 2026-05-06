from pydantic import BaseModel

class PlayerSchema(BaseModel):
    player_id: int
    name: str
    position: str
    draft_year: str
    
    class Config:
        from_attributes = True