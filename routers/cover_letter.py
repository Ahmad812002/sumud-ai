from pydantic import BaseModel 
from business_logic.cover_letter_logic import run_cover_letter
from fastapi import APIRouter, HTTPException

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
    print("cover letter endpoint", flush=True)
    return run_cover_letter(
            request.profile_chunks,
            request.job_description,
            request.fit_category,
            request.matching_points,
            request.soft_skills,
            request.reasoning
        )