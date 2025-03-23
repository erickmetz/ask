from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import secrets
from datetime import datetime, timedelta
from config import JWT_SECRET

security = HTTPBearer(
    scheme_name="JWT",
    description="Enter your JWT token",
    auto_error=False  # Allow requests without JWT
)

def create_access_token(subject: str):
    expires_delta = timedelta(hours=1)
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "iss": "ask-api-demo",          # Issuer
        "sub": subject,                 # Subject (user)
        "aud": "ask-api",               # Audience
        "iat": datetime.utcnow(),       # Issued At
        "exp": expire,                  # Expiration Time
        "jti": secrets.token_hex(16),   # JWT ID (unique identifier)
        "nbf": datetime.utcnow(),       # Not Before
        "typ": "JWT"                    # Token Type
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(
            credentials.credentials, 
            JWT_SECRET, 
            algorithms=["HS256"],
            options={
                "verify_exp": True,  # Verify expiration time
                "verify_iat": True,  # Verify issued at time
                "verify_nbf": True,  # Verify not before time
                "require": ["iss", "sub", "aud", "iat", "exp", "jti", "nbf", "typ"]  # Require all standard claims
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidIssuedAtError:
        raise HTTPException(status_code=401, detail="Invalid token issue time")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.MissingRequiredClaimError:
        raise HTTPException(status_code=401, detail="Missing required claims")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Token verification failed") 