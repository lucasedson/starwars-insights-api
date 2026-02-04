from app.utils.auth import get_google_auth_url
from flask import redirect
import os
import requests
import logging
from dotenv import load_dotenv

class AuthController:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.api_gateway_url = os.getenv("API_GATEWAY_URL")
        self.frontend_url = os.getenv("FRONTEND_URL")

    def handle_login(self):
        '''Redireciona o usuário para a autenticação do Google.'''
        return redirect(get_google_auth_url())
    
    
    def handle_callback(self, request):
        '''Recebe o código de autenticação do Google e retorna o token de acesso ao front.'''
        code = request.args.get('code')
        if not code:
            return {"error": "No code provided"}, 400

        try:
            token_endpoint = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": f"{self.api_gateway_url}/callback",
                "grant_type": "authorization_code",
            }

            response = requests.post(token_endpoint, data=data)
            token_data = response.json()

            if "error" in token_data:
                return {"error": f"Google API Error: {token_data.get('error_description')}"}, 400

            id_token = token_data.get("id_token")


            return redirect(f"{self.frontend_url}#id_token={id_token}")

        except Exception as e:
            return {"error": str(e)}, 500
        

    def get_user(self, user_data):
        """
        Verifica se o usuário está autenticado e retorna o status de autenticação.
        
        Parameters
        ----------
        user_data : dict
            Dados do usuário, incluindo o e-mail.
        
        Returns
        -------
        dict
            Dicionário com o status de autenticação do usuário.
        int
            Código de status HTTP.
        """
        if user_data:
            user_data["is_auth"] = True

            if "gserviceaccount.com" in user_data.get("email", ""):
                user_data["name"] = "Usuário Cloud"
            
            logging.info(f"🔥 [AUTH] Enviando status para o front: {user_data.get('email')}")
            return user_data, 200

        return {"is_auth": False}, 401