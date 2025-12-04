from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class NewGameRequest(BaseModel):
    mode: str = "free"
    letter_feedback: bool = False

class NewGameResponse(BaseModel):
    game_id: str
    max_attempts: int = 6
    settings: Dict[str, Any] = {}

class GuessRequest(BaseModel):
    game_id: str
    guess: str
    difficulty: str = "normal"

class GuessResponse(BaseModel):
    status: str
    attempt: int
    trait_feedback: Dict[str, Any]
    letter_feedback: Optional[List[Dict[str,str]]] = None
    answer: Optional[str] = None

class AnimalsResponse(BaseModel):
    items: List[str] = []
