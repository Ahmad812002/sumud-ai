from pydantic import BaseModel
from data_access.db import get_preferences_collection
from fastapi import APIRouter
from business_logic.scorer_logic import run_scorer
from exceptions import ScorerServiceError


router = APIRouter()


messages_arr = []
last_reply = ""
result = ""

# This class to make a clear response from FastAPI
class ScoreRequest(BaseModel):
    job_description: str



@router.post('/scorer')
def scorer_endpoint(request: ScoreRequest):
    try:
        # now it gets directly from database, the UI should ask for them if there is nothing stored
        preferences = get_preferences_collection().get()["documents"]

        result = run_scorer(request.job_description.strip(), preferences)
        return result
    except Exception as e:
       raise ScorerServiceError("Error occurred while generating embedding") from e

