from pydantic import BaseModel 
from fastapi import APIRouter, HTTPException
from business_logic.preferences_logic import collecting_preferences, upserting_preferences

router = APIRouter()


class PreferencesRequest(BaseModel):
    preferences: str

@router.post("/upsert_preferences")
# Add or update user preferences in the database.
def upsert_preferences(request: PreferencesRequest):
    try:
        upserting_preferences(request.preferences)
        return {"status": "success", "preferences": collecting_preferences()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_preferences")
def get_preferences():
    try:
        preferences = collecting_preferences()

        return preferences
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))