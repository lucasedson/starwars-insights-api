import logging
from flask import redirect
from app.views.responses import format_insight_response
from app.controllers.nlp_controller import NLPController
from app.utils.auth import get_google_auth_url
import requests
import os
from app.models.data_service import DataService

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
api_gateway_url = os.getenv("API_GATEWAY_URL")
frontend_url = os.getenv("FRONTEND_URL")
class InsightController:
    def __init__(self, db_manager, swapi_client):
        self.db = db_manager
        self.swapi = swapi_client
        self.nlp = NLPController(self.db)

        self.data_service = DataService(self.db, self.swapi)

    def handle_login(self):
        return redirect(get_google_auth_url())

    def handle_callback(self, request):
        code = request.args.get('code')
        if not code:
            return {"error": "No code provided"}, 400

        try:
            token_endpoint = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": f"{api_gateway_url}/callback",
                "grant_type": "authorization_code",
            }

            response = requests.post(token_endpoint, data=data)
            token_data = response.json()

            if "error" in token_data:
                return {"error": f"Google API Error: {token_data.get('error_description')}"}, 400

            id_token = token_data.get("id_token")


            return redirect(f"{frontend_url}#id_token={id_token}")

        except Exception as e:
            return {"error": str(e)}, 500
    def get_user(self, user_data):
        # Se chegamos aqui e user_data existe, mas o e-mail é da conta de serviço,
        # significa que estamos em produção e o token original foi trocado.
        
        # DICA: Verifique se o objeto já tem os campos que o AlpineJS espera
        if user_data:
            user_data["is_auth"] = True
            # Garante que não retorne o e-mail da Service Account para o front
            if "gserviceaccount.com" in user_data.get("email", ""):
                user_data["name"] = "Usuário Cloud" # Fallback visual
            
            logging.info(f"🔥 [AUTH] Enviando status para o front: {user_data.get('email')}")
            return user_data, 200

        return {"is_auth": False}, 200
        

    def get_known_entities(self):
        """Retorna todas as entidades conhecidas catalogadas no sistema."""
        settings = self.db.get_metadata("nlp_settings") or {}
        
        # Filtramos apenas as chaves que começam com 'known_'
        known_data = {
            key: value for key, value in settings.items() 
            if key.startswith("known_")
        }
        
        # Caso o documento esteja vazio, retornamos as listas vazias para manter o contrato
        default_structure = {
            "known_films": [], "known_people": [], "known_planets": [],
            "known_starships": [], "known_species": [], "known_vehicles": []
        }
        
        return {**default_structure, **known_data}, 200

    def get_my_history(self, user_data=None):
        if not user_data:
            return {"error": "User not authenticated"}, 401
        
        user_email = user_data.get("email")
        return self.db.get_my_search_history(user_email), 200
    
    
    def handle_insight(self, request, user_data=None):
        params = request.args
        query_natural = params.get("q")
        
        if query_natural:
            nlp_res = self.nlp.parse_sentence(query_natural)
            search_name = nlp_res.get("name")
            display_name = nlp_res.get("raw_name")
            entity_type = nlp_res.get("type")
            raw_filters = nlp_res.get("filter")
        else:
            display_name = params.get("name")
            search_name = self.nlp._fuzzy_correction(display_name)
            entity_type = params.get("type")
            raw_filters = params.get("filter")

        suggestion = None
        if search_name.lower() != display_name.lower():
            suggestion = search_name

        data = self.db.get(entity_type, search_name)
        source = "firestore"

        if not data:
            source = "live"
            data = self.data_service.fetch_and_learn(search_name, entity_type)
            if not data or "error" in data:
                return format_insight_response(data or {"error": "Not found"}, self.data_service.parse_filters(raw_filters), "error")
            
            data = self.data_service.hydrate_all_parallel(data)
            data['type'] = entity_type
            self.data_service.cache_new_data(entity_type, (data.get("name") or data.get("title")), data)
        else:
            data['type'] = entity_type


        if user_data:            
            self.db.create_or_update_my_search_history(user_data.get("email"), params)

        return format_insight_response(
            data, 
            self.data_service.parse_filters(raw_filters), 
            source, 
            suggestion=suggestion
        )
