from fastapi import APIRouter, Depends
from auth import check_api_key
from ask import get_question

router = APIRouter()

@router.get("/ask")
async def get_testroute(user: dict = Depends(check_api_key)):
    return get_question()
