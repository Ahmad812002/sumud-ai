from fastapi import HTTPException
import os
from data_access.db import get_preferences_collection

PREFERENCES_ID = os.environ.get("PREFERENCES_ID")
def collecting_preferences():
    try:
            preferences = get_preferences_collection().get(ids=[PREFERENCES_ID])
            if preferences and preferences['documents']:
                return { "preferences": preferences['documents'][0]}
            else:
                raise HTTPException(status_code=404, detail="No preferences found. Please set preferences first.")
    except HTTPException as e:
        raise
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

def upserting_preferences(preferences: str):
    try:
        collection = get_preferences_collection()
        collection.update(
                    ids=[PREFERENCES_ID],
                    documents=[preferences],
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))