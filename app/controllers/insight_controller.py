from concurrent.futures import ThreadPoolExecutor
from datetime import date
from app.models.swapi import SWAPIClient
from app.models.database import FirestoreManager
from app.views.responses import format_insight_response
from app.controllers.nlp_controller import NLPController

import logging



class InsightController:
    def __init__(self, db_manager: FirestoreManager, swapi_client: SWAPIClient):
        self.db = db_manager
        self.swapi = swapi_client
        self.nlp = NLPController(self.db)

    def _hydrate_field(self, data: dict, field_name: str, lookup_key: str) -> dict:
        """
        Busca e hidrata um campo da entidade
        """
        if field_name not in data:
            return data

        field_value = data[field_name]

        if isinstance(field_value, list):
            if not field_value or not isinstance(field_value[0], str) or 'swapi.dev' not in field_value[0]:
                return data

            hydrated_items = []
            for url in field_value:
                item_data = self.swapi.get_entity_by_url(url)
                if item_data and hasattr(item_data, lookup_key):
                    hydrated_items.append(getattr(item_data, lookup_key))
                else:
                    hydrated_items.append(url)
            data[field_name] = hydrated_items

        elif isinstance(field_value, str) and 'swapi.dev' in field_value:
            item_data = self.swapi.get_entity_by_url(field_value)
            if item_data and hasattr(item_data, lookup_key):
                data[field_name] = getattr(item_data, lookup_key)
        
        return data

    def handle_request(self, request):
        """
        Orquestra o fluxo. Suporta ?name=...&type=... OU ?q=... (NLP)
        """
        params = request.args
        query_natural = params.get("q")

        if query_natural:
            # Traduz: "Quais naves Luke pilotou?" -> {name: "Luke Skywalker", type: "people", filter: "starships"}
            nlp_data = self.nlp.parse_sentence(query_natural)
            name = nlp_data.get("name")
            entity_type = nlp_data.get("type")
            filters_str = nlp_data.get("filter")
            
            if not name or len(name) < 2:
                return ({"error": f"Não consegui identificar o alvo na frase: '{query_natural}'"}, 400)
        else:
            
            name = params.get("name")
            entity_type = params.get("type")
            filters_str = params.get("filter")

        
        if not all([name, entity_type]):
            return ({"error": "Missing required query parameters: name, type (or 'q' for natural language)"}, 400)


        if isinstance(filters_str, list):
            filter_fields = filters_str
        else:
            filter_fields = [f.strip() for f in filters_str.split(',')] if filters_str else None

        # busca firestore
        data = self.db.get(entity_type, name)
        source = "firestore" if data else "live"

        if not data:
            pydantic_data = self.swapi.fetch_hydrated(name, entity_type)
            if pydantic_data:
                data = pydantic_data.model_dump(by_alias=True)
                
                # --- LÓGICA DE APRENDIZADO ---
                real_name = data.get("name")
                metadata_map = {
                    "people": "known_people",
                    "planets": "known_planets",
                    "starships": "known_starships",
                    "films": "known_films",
                    # "species": "known_species",
                }
                
                target_list = metadata_map.get(entity_type)
                known_list = self.nlp.config.get(target_list, [])
                
                if target_list and real_name not in known_list:
                    self.db.add_to_metadata_list(target_list, real_name)
                    log_message = f"Novo conhecimento: {real_name} ({entity_type})"
                    logging.info(log_message)
            else:
                data = {"error": f"Entidade '{name}' não encontrada no universo Star Wars."}
                return format_insight_response(data, filter_fields, "error")

        
        if data:
            hydration_map = {
                "films": "title", "pilots": "name", "residents": "name",
                "characters": "name", "people": "name", "species": "name",
                "starships": "name", "vehicles": "name", "homeworld": "name",
                "planets": "name",
            }
            for field, lookup_key in hydration_map.items():
                data = self._hydrate_field(data, field, lookup_key)

            if source == 'live':
                if 'release_date' in data and isinstance(data['release_date'], date):
                    data['release_date'] = data['release_date'].isoformat()
                
                self.db.set(entity_type, name, data)

            data['type'] = entity_type

        return format_insight_response(data, filter_fields, source)