# Question Game API
This is an API that could be used with a bot for any kind of chat integration.

Game reads `questions-master.txt` and then answers API requests to /api/v1/secure/ask. Responds with random question.

```console
curl -s -H "X-API-Key: REDACTED_KEY1" https://[web_server_url]/api/v1/secure/ask 
{"question":"What's a scientific discovery you hope to see in your lifetime?"}
```

questions-master.txt has ~5 example questions but I would suggest finding about 1000 or so, so that it does not get too boring or repetitive. Can be themed and composed to whatever kind of questions you'd like. Sourced through web-scraping or generated with an LLM such as ChatGPT.

API Keys are hard-coded into auth.py.

Inspired by a game we have at home called Delve Deck https://www.boredwalk.com/products/delve-deck-conversation-cards

This is pretty much a copy/paste of https://timberry.dev/fastapi-with-apikeys that has been scoped and tailored for a simple purpose

# Running API

## Running without Docker
```console
# clone repo and enter source directory
git clone git@github.com:erickmetz/ask.git
cd ask

# Activate a Python virtual environment and install requirements
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run on localhost
uvicorn main:app --reload

# When finished, exit Python virtual environment
deactivate
```

## Runnign with Docker
```console
# Build container image
docker build . -t ask-api

# Run in non-detached mode (hit control C to exit)
docker run -p8000:8000 ask-api

# Alternatively, run in detatched mode, leaving API up in the background
docker run -d -p8000:8000 ask-api

# Finally, run in detached mode and restart every time server restarts unless/until you use the docker stop command.
docker run -d --restart unless-stopped -p8000:8000 ask-api
```

# Proxy through NGINX
Add this to site configuration within server {} section.

```
    location /api/v1/secure/ask {
        proxy_pass http://localhost:8000/api/v1/secure/ask;
    }
```

Verify configuration and restart NGINX
```
nginx -t && nginx -s reload
```
