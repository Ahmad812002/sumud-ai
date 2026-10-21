from pydantic import BaseModel 
from business_logic.cover_letter_logic import run_cover_letter 
from fastapi import APIRouter, HTTPException
from business_logic.scorer_logic import process_job_description, run_scorer
from data_access.db import get_preferences_collection

router = APIRouter()

class CoverLetterRequest(BaseModel):
    job_description: str
    fit_category: str = ""
    profile_chunks: str = ""
    matching_points: list[str] = []
    gaps: list[str] = []
    reasoning: str = ""
    

@router.post("/cover_letter")
def generate_cover_letter(request: CoverLetterRequest):
    try:
        job_preferences = get_preferences_collection().get()["documents"]
        # scorer_result = run_scorer(request.job_description.strip(), job_preferences)
        # profile_chunks = process_job_description(request.job_description)

        generated_cover_letter = run_cover_letter(request.profile_chunks,
                                                request.job_description,
                                                request.fit_category,
                                                request.matching_points,
                                                request.gaps, 
                                                request.reasoning)
        # print("cover letter: ", generated_cover_letter)

        if(generated_cover_letter['opening']):
            return {
                        "opening": generated_cover_letter['opening'],
                        "middle": generated_cover_letter['middle'],
                        "gap": generated_cover_letter['gap'],
                        "closing": generated_cover_letter['closing']
                        }
    except ValueError as e:
        print(e)
        raise  HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
