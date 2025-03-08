from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")
api_keys = {
    "REDACTED_KEY1": "redacted_clientname_1",
    "REDACTED_KEY2": "redacted_clientname_2",
    "REDACTED_KEY3": "redacted_clientname_3",
}

def check_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key"
        )
        
    user = api_keys[api_key_header]
    return user
