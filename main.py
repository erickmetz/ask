from fastapi import FastAPI, APIRouter, Depends
from fastapi.responses import JSONResponse
from auth import check_api_key
from ask import init_questions, get_question

app = FastAPI()
app.lines, app.max_lines = init_questions()

router = APIRouter()

@router.get("/ask")
async def get_testroute(user: dict = Depends(check_api_key)):
    question = get_question(app.lines, app.max_lines)
    data = {"question": question}

    return JSONResponse(data)

app.include_router(
    router,
    prefix="/api/v1/secure",
    dependencies=[Depends(check_api_key)]
)