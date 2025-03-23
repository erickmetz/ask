from collections import defaultdict
import time
from fastapi import HTTPException

# Rate limiting configuration
RATE_LIMIT = 50  # requests per minute
rate_limit_data = defaultdict(list)

def check_rate_limit(identifier: str) -> bool:
    current_time = time.time()
    # Remove requests older than 1 minute
    rate_limit_data[identifier] = [t for t in rate_limit_data[identifier] if current_time - t < 60]
    
    # Check if we're over the limit
    if len(rate_limit_data[identifier]) >= RATE_LIMIT:
        return False
    
    # Add current request
    rate_limit_data[identifier].append(current_time)
    return True

def enforce_rate_limit(identifier: str):
    if not check_rate_limit(identifier):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before making more requests."
        ) 