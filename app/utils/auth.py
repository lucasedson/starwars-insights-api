import os
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from urllib.parse import urlencode

def verify_google_token(token):
    """
    Verifica se o token de acesso fornecido é válido, com base em Google OAuth2.
    
    Parameters
    ----------
    token : str
        Token de acesso fornecido pelo usuário.
    
    Returns
    -------
    dict
        Dicionário com informações do usuário, caso o token seja válido.
    None
        Caso o token seja inválido.
    """
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
    """
    Retorna a URL para autenticação com a conta Google.

    A URL é montada com base nos parâmetros de ambiente, incluindo o client ID e o redirect URI.
    Os parâmetros de autenticação incluem o tipo de resposta (code), o escopo (openid, email e profile), o tipo de acesso (offline) e a opção de prompt (select_account).

    Returns
    -------
    str
        A URL para autenticação com a conta Google.
    """
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
    """
    Troca o código de autenticação pelo token de acesso.

    Parameters
    ----------
    code : str
        Código de autenticação retornado pelo Google.

    Returns
    -------
    dict or None
        Dicionário com o token de acesso ou None se houver erro.
    """
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