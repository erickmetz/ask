from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Security
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from auth import authenticate, api_key_header, check_channel_authorization, get_authorized_channels
from config import api_keys, JWT_SECRET
from ask import question_decks
from demo import get_demo_page
from jwt_auth import create_access_token
from datetime import datetime, timedelta
from rate_limit import enforce_rate_limit
from fastapi import Request
from fastapi.staticfiles import StaticFiles
import random
app = FastAPI()

router = APIRouter()
demo_router = APIRouter()

# Mount static files
app.mount("/api/v1/demo/static", StaticFiles(directory="static"), name="static")

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

@demo_router.get("/channels")
async def get_channels(username: str = Depends(authenticate)):
    authorized_channels = get_authorized_channels(username)
    return {"channels": authorized_channels}

@demo_router.get("/", response_class=HTMLResponse)
async def get_demo():
    return get_demo_page([])  # Initial empty list, will be populated by frontend

@demo_router.post("/token")
async def get_token(api_key: str = Security(api_key_header)):
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
async def secure_ask(
    request: Request, 
    username: str = Depends(authenticate),
    channel: str = None
):
    # Check rate limit
    enforce_rate_limit(username)
    
    print(f"Request from user: {username}, channel: {channel}")
    if channel is None:
        channel = "master"

    if channel == "random":
        authorized_channels = get_authorized_channels(username)
        channel = random.choice(authorized_channels[1:])
    elif "," in channel:
        # Handle comma-separated list of channels
        requested_channels = [c.strip() for c in channel.split(",")]
        authorized_channels = get_authorized_channels(username)
        valid_channels = [c for c in requested_channels if c in authorized_channels]
        
        if not valid_channels:
            raise HTTPException(status_code=400, detail="No valid channels provided")
        
        channel = random.choice(valid_channels)
    elif channel not in question_decks:
        raise HTTPException(status_code=400, detail="Invalid channel")
    
    if not check_channel_authorization(username, channel):
        raise HTTPException(status_code=403, detail="Access denied")

    if question_decks[channel].is_empty():
        raise HTTPException(status_code=400, detail="No questions available for this channel")
    
    question = question_decks[channel].get_question()
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