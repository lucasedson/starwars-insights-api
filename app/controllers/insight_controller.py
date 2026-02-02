from concurrent.futures import ThreadPoolExecutor
from datetime import date
from app.models.swapi import SWAPIClient
from app.models.database import FirestoreManager
from app.views.responses import format_insight_response

class InsightController:
    def __init__(self, db_manager: FirestoreManager, swapi_client: SWAPIClient):
        self.db = db_manager
        self.swapi = swapi_client

    def _hydrate_field(self, data: dict, field_name: str, lookup_key: str) -> dict:
        """
        Hidrata um campo de dados, seja ele uma lista de URLs ou uma única URL.
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

        # Caso 2: O campo é uma única URL
        elif isinstance(field_value, str) and 'swapi.dev' in field_value:
            item_data = self.swapi.get_entity_by_url(field_value)
            if item_data and hasattr(item_data, lookup_key):
                data[field_name] = getattr(item_data, lookup_key)
        
        return data

    def handle_request(self, request):
        """
        Orquestra o fluxo de busca, cache, hidratação e formatação dos dados.
        """
        params = request.args
        name = params.get("name")
        entity_type = params.get("type")
        filters_str = params.get("filter")

        if not all([name, entity_type]):
            return ("Missing required query parameters: name, type", 400)

        filter_fields = filters_str.split(',') if filters_str else None

        # 1. Tenta buscar do cache
        data = self.db.get(entity_type, name)
        source = "firestore" if data else "live"

        # 2. Se não tem no cache, busca na API
        if not data:
            pydantic_data = self.swapi.fetch_hydrated(name, entity_type)
            if pydantic_data:
                data = pydantic_data.model_dump(by_alias=True)
        
        # 3. Hidrata os dados, se existirem, independentemente da fonte
        if data:
            hydration_map = {
                "films": "title", "pilots": "name", "residents": "name",
                "characters": "name", "people": "name", "species": "name",
                "starships": "name", "vehicles": "name", "homeworld": "name",
                "planets": "name",
            }
            for field, lookup_key in hydration_map.items():
                # A reatribuição é crucial para garantir que a modificação seja mantida
                data = self._hydrate_field(data, field, lookup_key)

            # 4. Se os dados vieram da API, salva a versão hidratada no cache
            if source == 'live':
                # Converte campos de data para string antes de salvar no Firestore
                if 'release_date' in data and isinstance(data['release_date'], date):
                    data['release_date'] = data['release_date'].isoformat()
                
                self.db.set(entity_type, name, data)

            data['type'] = entity_type

        # 5. Formata a resposta
        return format_insight_response(data, filter_fields, source)
