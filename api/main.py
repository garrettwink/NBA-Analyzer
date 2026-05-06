from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from data.db import engine, Players, Teams, Stats

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

@app.get("/players")
def get_players():
    with Session() as session:
        players = session.execute(select(Players)).scalars().all()

        return players


