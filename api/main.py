from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from data.db import engine, Players, Teams, Stats
from api.schemas import PlayerSchema, TeamSchema, PlayerDetailedSchema

Session = sessionmaker(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    pass

@app.get("/players", response_model=list[PlayerSchema])
def get_players():
    with Session() as session:
        players = session.execute(select(Players)).scalars().all()

        return players

@app.get("/players/{player_id}", response_model=PlayerDetailedSchema)
def get_player_id(player_id: int):
    with Session() as session:
        player = session.execute(select(Players).where(Players.player_id == player_id)).scalar_one_or_none()
        stats = session.execute(select(Stats).where(Stats.player_id == player_id)).scalars().all()

        if player is None:
            raise HTTPException(status_code=404, detail='Player not found')
        
        result = player.__dict__
        result['stats'] = stats
        
        return result
    
@app.get("/teams", response_model=list[TeamSchema])
def get_teams():
    with Session() as session:
        teams = session.execute(select(Teams)).scalars().all()

        return teams