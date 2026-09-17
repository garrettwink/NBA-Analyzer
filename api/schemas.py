from datetime import datetime

from pydantic import BaseModel


class AwardPredictionSchema(BaseModel):
    """
    The only thing the landing page reads: the current predicted
    MVP (or other award) winner, as computed by the model.
    """
    id: int
    award_name: str
    season: int
    predicted_player_id: int
    predicted_player_name: str
    predicted_team_name: str | None = None
    probability: float | None = None
    confidence: float | None = None
    ranking: int | None = None
    top_reasons: str | None = None
    model_version: str | None = None
    generated_at: datetime

    class Config:
        from_attributes = True