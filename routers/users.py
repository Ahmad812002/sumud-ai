from fastapi import APIRouter
from data_access.db import create_user

router = APIRouter()


@router.post("users")
def create_profil():
    create_user()

    pass