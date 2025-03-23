from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Security
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from auth import authenticate, api_key_header
from config import api_keys, JWT_SECRET
from ask import init_questions, get_question
from demo import get_demo_page
from jwt_auth import create_access_token
from datetime import datetime, timedelta
from rate_limit import enforce_rate_limit
import jwt
import secrets
from fastapi import Request
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.lines, app.max_lines = init_questions()

router = APIRouter()
demo_router = APIRouter()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

@demo_router.get("/", response_class=HTMLResponse)
async def get_demo():
    return get_demo_page()

@demo_router.post("/token")
async def get_token(api_key: str = Security(api_key_header)):
    if not api_key or api_key not in api_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    user = api_keys[api_key]
    access_token = create_access_token(user)
    return {"access_token": access_token, "user": user}

@app.post("/api/v1/demo/token")
async def create_demo_token(request: Request):
    api_key = request.headers.get("X-API-Key")
    
    if api_key not in api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    user = api_keys[api_key]
    access_token = create_access_token(user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "user": user
    }

@router.get("/ask")
async def secure_ask(request: Request, username: str = Depends(authenticate)):
    # Check rate limit
    enforce_rate_limit(username)
    
    print(f"Request from user: {username}")
    question = get_question(app.lines, app.max_lines)
    data = {"question": question}
    return JSONResponse(data)

app.include_router(
    router,
    prefix="/api/v1/secure"
)

app.include_router(
    demo_router,
    prefix="/api/v1/demo"
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return get_demo_page()

@app.post("/api/v1/secure/ask")
async def secure_ask(
    question: str,
    api_key: str = Security(api_key_header),
    token: str = Security(bearer_scheme)
):
    # Check API key
    if api_key not in api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limit
    enforce_rate_limit(api_key)
    
    # Verify JWT token
    try:
        user = authenticate(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    # Process the question and return response
    return {"answer": f"Secure response for {user}: {question}"}

@app.post("/api/v1/ask")
async def ask(question: str, api_key: str = Security(api_key_header)):
    if api_key not in api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limit
    enforce_rate_limit(api_key)
    
    # Process the question and return response
    return {"answer": f"Response: {question}"}