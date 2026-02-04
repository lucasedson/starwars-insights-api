import base64
import json
import os
from pathlib import Path

import functions_framework
from dotenv import load_dotenv
from flask import Response

from app.controllers.auth_controller import AuthController
from app.controllers.insight_controller import InsightController
from app.models.database import FirestoreManager
from app.models.swapi import SWAPIClient
from app.utils.auth import verify_google_token

base_path = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base_path / ".env")

db_manager = FirestoreManager(os.getenv("GCP_PROJECT_ID"))
frontend_url = os.getenv("FRONTEND_URL")
frontend_short_url = os.getenv("FRONTEND_SHORT_URL")
swapi_client = SWAPIClient()
insight_controller = InsightController(db_manager, swapi_client)
auth_controller = AuthController()


@functions_framework.http
def star_wars_insights(request):
    """
    Função principal do Cloud Function, responsável por lidar com requisições HTTP.

    Parameters
    ----------
    request : flask.Request
        Requisição HTTP recebida pelo Cloud Function.

    Returns
    -------
    Response
        Resposta HTTP para a requisição recebida.
    """
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": frontend_short_url,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600",
        }
        return ("", 204, headers)

    auth_header = request.headers.get("Authorization")
    user_data = None
    user_info_encoded = request.headers.get("X-Apigateway-Api-Userinfo")

    if user_info_encoded:
        decoded = base64.b64decode(user_info_encoded + "===").decode("utf-8")
        user_data = json.loads(decoded)
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            user_data = verify_google_token(auth_header.split(" ")[1])
    if auth_header and auth_header.startswith("Bearer "):
        user_data = verify_google_token(auth_header.split(" ")[1])

    path = request.path.strip("/")

    def wrap_cors(controller_response):
        response_headers = {
            "Access-Control-Allow-Origin": frontend_short_url,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "3600",
        }

        if isinstance(controller_response, Response):
            for key, value in response_headers.items():
                controller_response.headers[key] = value
            return controller_response

        if isinstance(controller_response, tuple):
            res = list(controller_response)
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
        return wrap_cors(auth_controller.handle_login())

    if path == "callback":
        return wrap_cors(auth_controller.handle_callback(request))

    if path == "me":
        return wrap_cors(auth_controller.get_user(user_data))

    if path == "metadata":
        return wrap_cors(insight_controller.get_known_entities())

    if path == "history":
        return wrap_cors(insight_controller.get_my_history(user_data))

    return wrap_cors(insight_controller.handle_insight(request, user_data=user_data))
