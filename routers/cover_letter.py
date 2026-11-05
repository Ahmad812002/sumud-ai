from pydantic import BaseModel 
from business_logic.cover_letter_logic import run_cover_letter
from fastapi import APIRouter, HTTPException
from business_logic.scorer_logic import process_job_description, run_scorer
from data_access.db import get_preferences_collection
import routers.scorer as scorer_router

router = APIRouter()

class CoverLetterRequest(BaseModel):
    job_description: str
    fit_category: str = ""
    profile_chunks: str = ""
    matching_points: list[str] = []
    soft_skills: list[str] = []
    reasoning: str = ""
    

@router.post("/cover_letter")
def generate_cover_letter(request: CoverLetterRequest): 
    try:
        generated_cover_letter = run_cover_letter(request.profile_chunks,
                                                request.job_description,
                                                request.fit_category,
                                                request.matching_points,
                                                request.soft_skills,
                                                request.reasoning)

        if(generated_cover_letter['opening']):
            return {
                        "opening": generated_cover_letter['opening'],
                        "middle": generated_cover_letter['middle'],
                        "soft_skills": generated_cover_letter['soft_skills'],
                        "closing": generated_cover_letter['closing']
                        }
    except ValueError as e:
        print(e)
        raise  HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
