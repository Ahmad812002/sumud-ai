from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from business_logic.auth_logic import sign_up_user

router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(request: SignUpRequest):
    user_id = sign_up_user(request.email, request.password)
    return {"user_id": user_id}
