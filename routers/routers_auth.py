from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from business_logic.auth_logic import sign_up_user

router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(request: SignUpRequest):
    try:
        user_id = sign_up_user(request.email, request.password)
        return {"user_id": user_id}
    except ValueError as e:
        # user-facing errors from Supabase (e.g. email already registered)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)  # keep the details in server logs
        raise HTTPException(status_code=500, detail="Sign up failed.")
