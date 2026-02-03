import os
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from urllib.parse import urlencode

def verify_google_token(token):
    """Valida o ID Token vindo do Header."""
    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), os.getenv("GOOGLE_CLIENT_ID")
        )
        return idinfo
    except Exception:
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
        "prompt": "select_account" # Força a escolha da conta para facilitar testes
    }
    
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    return f"{base_url}?{urlencode(params)}"


def exchange_code_for_token(code):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
        # ESTA URL deve ser exatamente a mesma cadastrada no Google Cloud Console
        "redirect_uri": "http://127.0.0.1:8080/callback" 
    }
    
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        print(f"Erro Google: {response.text}") # Isso vai te mostrar o erro real no terminal
        return None
    
    return response.json()