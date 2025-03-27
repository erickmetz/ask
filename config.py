import secrets

# Generate a random secret key for JWT signing
JWT_SECRET = secrets.token_hex(32)

# Define valid API keys
api_keys = {
    "ask-api-key-123": "user123",
    "test-key-1": "user1"
}

channel_authorizations = {
    "user123": ["random", "master", "channel1", "channel2"],
    "user1": ["random","master", "channel1"]
}