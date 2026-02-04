import os
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from urllib.parse import urlencode

def verify_google_token(token):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    api_url = os.getenv("FUNCTION_URL")

    function_url = f"{api_url}/star_wars_insights/me"
    
    try:

        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            audience=[client_id, function_url],
            clock_skew_in_seconds=10
        )
        return idinfo
    except Exception as e:
        print(f"DEBUG_AUTH_ERROR: {str(e)}")
        return None

def get_google_auth_url():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("REDIRECT_URI")
    
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }
    
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    return f"{base_url}?{urlencode(params)}"


def exchange_code_for_token(code):
    token_url = "https://oauth2.googleapis.com/token"
    redirect_uri = os.getenv("REDIRECT_URI")
    payload = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",

        "redirect_uri": redirect_uri
    }
    
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        print(f"Erro Google: {response.text}")
        return None
    
    return response.json()