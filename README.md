# Question Game API

This is an API that could be used with a bot for any kind of chat integration.

Game reads `questions-master.txt` and then answers API requests to /api/v1/secure/ask. Responds with random question.

```console
curl -s -H "X-API-Key: test-key-1" https://[web_server_url]/api/v1/secure/ask 
{"question":"What's a scientific discovery you hope to see in your lifetime?"}
```

questions-master.txt has ~5 example questions but I would suggest finding about 1000 or so, so that it does not get too boring or repetitive. Can be themed and composed to whatever kind of questions you'd like. Sourced through web-scraping or generated with an LLM such as ChatGPT.

API Keys are hard-coded into config.py.

Inspired by a game we have at home called Delve Deck https://www.boredwalk.com/products/delve-deck-conversation-cards

This started out as a copy/paste of https://timberry.dev/fastapi-with-apikeys and has grown from that point.

## LLM/AI Disclosure
I used the Cursor IDE Ask/Agent functions to generate and refactor a lot 
much of these commit contents. This is my first time using such an IDE tool. 
It's been pretty intersting but has also needed a fair amount of steering,
troubleshooting, and corrections.

## Channel Context Support
The API now supports multiple question decks through channel contexts:

- `questions-master.txt`: Default questions available to all users
- `questions-channel1.txt`, `questions-channel2.txt`, etc.: Additional question decks that can be restricted to specific users

Channel selection can be done in three ways:
1. No channel specified: Uses the master questions (default)
2. Single channel: `channel=channel1`
3. Multiple channels: `channel=channel1,channel2` (randomly selects from specified channels)

Example with channel selection:
```console
# Get a question from a specific channel
curl -s -H "X-API-Key: test-key-1" "https://[web_server_url]/api/v1/secure/ask?channel=channel1"

# Get a question from multiple channels
curl -s -H "X-API-Key: test-key-1" "https://[web_server_url]/api/v1/secure/ask?channel=channel1,channel2"
```

The demo webpage includes a channel selector that shows only the channels the authenticated user has access to. Users can select multiple channels to get questions from any of them randomly.

# API Demo Webpage
![Screenshot](media/screenshot.png)

![Screenshot](media/screenshot_authenticated.png)

## Landing Page
The API includes a demo webpage that showcases the API's functionality. The page is built using a modern, dark-themed UI and is served using FastAPI's templating system with Jinja2. The page is organized into separate components:

- HTML template (`templates/demo.html`): Contains the page structure and dynamic content
- CSS styles (`static/css/styles.css`): Handles all styling with a dark theme and responsive design
- JavaScript (`static/js/main.js`): Manages client-side functionality and API interactions

The templating system uses versioning to ensure browsers always load the latest version of static files. A random version number is generated on server startup and appended to static file URLs (e.g., `/static/css/styles.css?n=123456`).

## JWT Authentication
The demo page implements a secure authentication flow using JWT tokens:

1. Users enter their API key in the landing page
2. The key is validated against the server's configured API keys
3. Upon successful validation, a JWT token is generated and stored in a cookie
4. The token is automatically included in subsequent API requests
5. The server validates the token and enforces rate limiting
6. Rate limit errors are displayed in red text on the page
7. Authentication state is persisted across page reloads

The authentication system includes:
- Automatic token validation on page load
- Graceful error handling for invalid tokens
- Rate limit enforcement with user-friendly error messages

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

## Running with Docker
Pick *one* of the three "docker run" commands shown based on comment above them.
```console
# Build container image
docker build . -t ask-api

# Run in non-detached mode (hit control C to exit)
docker run -p8000:8000 ask-api

# Run in detatched mode, leaving API up in the background
docker run -d -p8000:8000 ask-api

# Run in detached mode and restart every time docker daemon is restarted (until you use the docker stop command)
docker run -d --restart unless-stopped -p8000:8000 ask-api
```

# Proxy through NGINX
Add these locations to your site configuration within server {} section.

```
    # API endpoint
    location /api/v1/secure/ask {
        proxy_pass http://localhost:8000/api/v1/secure/ask;
    }

    # Landing, token endpoint, static assets
    location /api/v1/demo/ {
        proxy_pass http://localhost:8000/api/v1/demo;
    }
```

Verify configuration and restart NGINX
```
nginx -t && nginx -s reload
```
