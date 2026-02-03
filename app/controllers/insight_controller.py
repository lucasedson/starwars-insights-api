import logging
from datetime import date
from flask import redirect
from concurrent.futures import ThreadPoolExecutor
from app.views.responses import format_insight_response
from app.controllers.nlp_controller import NLPController
from app.utils.auth import get_google_auth_url, exchange_code_for_token
import requests
import os

class InsightController:
    def __init__(self, db_manager, swapi_client):
        self.db = db_manager
        self.swapi = swapi_client
        self.nlp = NLPController(self.db)
        self.hydration_map = {
            "films": "title", "pilots": "name", "residents": "name",
            "characters": "name", "people": "name", "species": "name",
            "starships": "name", "vehicles": "name", "homeworld": "name",
            "planets": "name",
        }

    def handle_login(self):
        return redirect(get_google_auth_url())

    def handle_callback(self, request):
        code = request.args.get('code')
        if not code:
            return {"error": "No code provided"}, 400

        try:
            # A redirect_uri AQUI deve ser a do BACKEND (onde o Google te enviou)
            # E deve ser EXATAMENTE igual à cadastrada no Google Cloud Console
            token_endpoint = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": "http://localhost:8080/callback", # <--- O PONTO CRÍTICO
                "grant_type": "authorization_code",
            }

            response = requests.post(token_endpoint, data=data)
            token_data = response.json()

            if "error" in token_data:
                return {"error": f"Google API Error: {token_data.get('error_description')}"}, 400

            id_token = token_data.get("id_token")

            # --- Agora sim o Redirecionamento ---
            # Se chegamos aqui, o token é válido. Agora mandamos para o frontend.
            frontend_url = "https://lucasedson.github.io/starwars-insights-api/html_extras/playground.html"
            return redirect(f"{frontend_url}#id_token={id_token}")

        except Exception as e:
            return {"error": str(e)}, 500
    def get_user_status(self, user_data):
        is_auth = user_data is not None

        if not is_auth:
            return {"is_auth": False}, 200

        logging.info(f"🔥 [AUTH] Usuário autenticado: {user_data}")
        return user_data, 200
        
        

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
    
    
    def handle_request(self, request, user_data=None):
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
            data = self._fetch_and_learn(search_name, entity_type)
            if not data or "error" in data:
                return format_insight_response(data or {"error": "Not found"}, self._parse_filters(raw_filters), "error")
            
            data = self._hydrate_all_parallel(data)
            data['type'] = entity_type
            self._cache_new_data(entity_type, (data.get("name") or data.get("title")), data)
        else:
            data['type'] = entity_type


        if user_data:            
            self.db.create_or_update_my_search_history(user_data.get("email"), params)
            

        # Passamos a sugestão para a View formatar
        return format_insight_response(
            data, 
            self._parse_filters(raw_filters), 
            source, 
            suggestion=suggestion # <-- Enviando para a View
        )
    def _parse_filters(self, raw_filters):
        if isinstance(raw_filters, list):
            return raw_filters
        if isinstance(raw_filters, str) and raw_filters.strip():
            return [f.strip() for f in raw_filters.split(',')]
        return None


    def _fetch_and_learn(self, name, entity_type):
        pydantic_data = self.swapi.fetch_hydrated(name, entity_type)
        if not pydantic_data:
            return None
        data = pydantic_data.model_dump(by_alias=True)
        real_name = data.get("name") or data.get("title")
        metadata_map = {"people": "known_people", "planets": "known_planets", 
                        "starships": "known_starships", "films": "known_films"}
        target_list = metadata_map.get(entity_type)
        if target_list:
            self.db.add_to_metadata_list(target_list, real_name)
        return data

    def _cache_new_data(self, entity_type, name, data):
        if 'release_date' in data and isinstance(data['release_date'], date):
            data['release_date'] = data['release_date'].isoformat()
        self.db.set(entity_type, name, data)

    def _hydrate_all_parallel(self, data):
        fields_to_hydrate = [f for f in self.hydration_map.keys() if f in data]
        if not fields_to_hydrate:
            return data
            
        with ThreadPoolExecutor(max_workers=10) as executor:
            # list() força a espera de todas as threads
            list(executor.map(lambda f: self._hydrate_field(data, f, self.hydration_map[f]), fields_to_hydrate))
        return data

    def _hydrate_field(self, data: dict, field_name: str, lookup_key: str) -> dict:

        field_value = data.get(field_name)
        if not field_value:
            return data

        if isinstance(field_value, list):
            hydrated_items = []
            for item in field_value:
                if isinstance(item, str) and 'swapi.dev' in item:
                    item_data = self.swapi.get_entity_by_url(item)
                    if item_data:
                        val = getattr(item_data, lookup_key, None) or (item_data.get(lookup_key) if isinstance(item_data, dict) else None)
                        hydrated_items.append(val if val else item)
                    else:
                        hydrated_items.append(item)
                else:
                    hydrated_items.append(item)
            data[field_name] = hydrated_items

        elif isinstance(field_value, str) and 'swapi.dev' in field_value:
            item_data = self.swapi.get_entity_by_url(field_value)
            if item_data:
                val = getattr(item_data, lookup_key, None) or (item_data.get(lookup_key) if isinstance(item_data, dict) else None)
                data[field_name] = val if val else field_value
        
        return data
    
    # def _record_search(self, query, user_data=None):
    #     if not user_data:
    #         return
    #     user_email = user_data.get("email")
    #     self.db.add_to_search_history(user_email, query)