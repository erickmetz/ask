from fastapi import HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jwt_auth import verify_token
from config import api_keys, JWT_SECRET
import jwt
from datetime import datetime, timedelta
import secrets

# Security schemes
api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="Enter your API key",
    auto_error=False  # Allow requests without API key
)

jwt_bearer = HTTPBearer(
    scheme_name="JWT",
    description="Enter your JWT token",
    auto_error=False  # Allow requests without JWT
)

async def authenticate(
    api_key: str | None = Security(api_key_header),
    jwt_token: HTTPAuthorizationCredentials | None = Security(jwt_bearer)
):
    
    username = None

    # Try X-API-Key authentication first
    if api_key is not None:
        if api_key not in api_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")
        username = api_keys[api_key]
    elif jwt_token is not None:
        jwt_token.credentials
        # If no API key, try JWT authentication
        if not jwt_token.credentials:
            raise HTTPException(status_code=401, detail="No valid authorization header")   
        token = jwt_token.credentials
        
        try:
            # Verify the token
            decoded = jwt.decode(
                token, 
                JWT_SECRET, 
                algorithms=["HS256"],
                audience="ask-api",  # Expected audience
                options={
                    "verify_aud": True,  # Verify audience
                    "require": ["aud"]   # Require audience claim
                }
            )
            username = decoded.get("sub", "unknown")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=401, detail="Token verification failed")
           
    return username
