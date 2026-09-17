from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from data.db import engine, Players, Teams, Stats
from api.schemas import PlayerSchema, TeamSchema, PlayerStatSchema

Session = sessionmaker(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    with Session() as session:
        player_count = session.scalar(select(func.count()).select_from(Players))
        team_count = session.scalar(select(func.count()).select_from(Teams))
        season_count = session.scalar(select(func.count(func.distinct(Stats.season))))

    return {
        'title': 'NBA Analyzer Dashboard',
        'description': 'A simple API dashboard placeholder for future live game and analytics data.',
        'summary': {
            'players': player_count,
            'teams': team_count,
            'seasons': season_count,
        },
        'endpoints': [
            '/players',
            '/players/{player_id}',
            '/teams',
        ],
        'current_games': [],
        'note': 'Current games are not yet available. Future versions can add live matchup data here.',
    }