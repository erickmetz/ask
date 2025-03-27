from fastapi.responses import HTMLResponse
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import api_keys
from jwt_auth import create_access_token, verify_token
from jinja2 import Environment, FileSystemLoader
import os
import secrets

# Set up Jinja2 environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

# Generate a random version number for static files
static_version = secrets.randbelow(1000000)

def get_demo_page(channels):
    template = env.get_template('demo.html')
    return template.render(
        welcome_message="Welcome to the Ask API demo!",
        static_version=static_version,
        channels=channels
    ) 