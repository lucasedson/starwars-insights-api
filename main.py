import functions_framework
from app.controllers.insight_controller import InsightController
from app.models.database import FirestoreManager
from app.models.swapi import SWAPIClient
from app.utils.auth import verify_google_token
import os
from dotenv import load_dotenv
from pathlib import Path
from flask import Response
import json
import base64

# Configuração de Ambiente
base_path = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base_path / ".env")

# Injeção de dependência
db_manager = FirestoreManager(os.getenv("GCP_PROJECT_ID"))
swapi_client = SWAPIClient()
controller = InsightController(db_manager, swapi_client)

@functions_framework.http
def star_wars_insights(request):
    # --- 1. TRATAMENTO DE CORS (Obrigatório para Frontend) ---
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "https://lucasedson.github.io",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
        return ("", 204, headers)

    # Headers de resposta padrão para todas as outras requisições
    response_headers = {"Access-Control-Allow-Origin": "https://lucasedson.github.io"}

    # 2. IDENTIFICAÇÃO DO USUÁRIO
    auth_header = request.headers.get("Authorization")
    user_data = None
    user_info_encoded = request.headers.get("X-Apigateway-Api-Userinfo")
    
    if user_info_encoded:
        # Se o Gateway mandou esse header, ele é a autoridade máxima
        decoded = base64.b64decode(user_info_encoded + "===").decode("utf-8")
        user_data = json.loads(decoded)
    else:
        # Fallback para local ou chamadas sem Gateway
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            user_data = verify_google_token(auth_header.split(" ")[1])
    if auth_header and auth_header.startswith("Bearer "):
        user_data = verify_google_token(auth_header.split(" ")[1])

    # 3. ROTEAMENTO
    path = request.path.strip("/")

    # Função auxiliar para injetar headers em respostas do controller
    def wrap_cors(controller_response):
        # Use o seu domínio específico em vez de "*"
        response_headers = {
            "Access-Control-Allow-Origin": "https://lucasedson.github.io",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "3600"
        }

        if isinstance(controller_response, Response):
            for key, value in response_headers.items():
                controller_response.headers[key] = value
            return controller_response

        if isinstance(controller_response, tuple):
            res = list(controller_response)
            # Garante que o terceiro elemento (headers) exista e seja um dict
            if len(res) == 2:
                res.append(response_headers)
            elif len(res) == 3:
                if res[2] is None:
                    res[2] = response_headers
                else:
                    res[2].update(response_headers)
            return tuple(res)

        return controller_response, 200, response_headers
 
    if path == "login":
        return wrap_cors(controller.handle_login()) # Adicionado wrap_cors aqui
    
    if path == "callback":
        return wrap_cors(controller.handle_callback(request))
    
    if path == "me":
        return wrap_cors(controller.get_user_status(user_data))
    
    if path == "metadata":
        return wrap_cors(controller.get_known_entities())
    
    if path == "history":
        return wrap_cors(controller.get_my_history(user_data))
    
    # Busca principal (Root /)
    return wrap_cors(controller.handle_request(request, user_data=user_data))