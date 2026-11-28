from fastapi import APIRouter
from data_access.db import create_profile_user

router = APIRouter()


@router.post("users")
def create_profil():
    create_profile_user(1)

    pass