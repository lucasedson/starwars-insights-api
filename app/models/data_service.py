import asyncio
import logging
from typing import Optional, Dict, List
from .mapping import ENTITY_MAP, TYPE_MAP

class DataService:
    def __init__(self, db_manager, swapi_client):
        self.db = db_manager      # FirestoreManager
        self.swapi = swapi_client # SWAPIClient

    async def get_processed_insight(self, name: str, entity_type: str, fields: str = None) -> dict:
        """
        Orquestra a busca, hidratação e filtragem.
        Atua como a regra de negócio do Model.
        """
        try:
            # 1. Obtenção do dado completo (Cache-Aside Logic)
            full_data = await self._get_base_data(name, entity_type)
            
            if not full_data:
                return {"error": "Entidade não encontrada"}

            # 2. Se não houver campos específicos, retorna o objeto base
            if not fields:
                return full_data

            # 3. Preparação para Hidratação Paralela
            field_list = [f.strip() for f in fields.split(",")]
            response = {"name": full_data.get("name") or full_data.get("title")}
            
            tasks = []
            task_fields = []

            for field in field_list:
                value = full_data.get(field)
                # Verifica se o campo contém URLs que precisam ser "resolvidas" (Hidratação)
                if isinstance(value, list) and value and isinstance(value[0], str) and "http" in value[0]:
                    tasks.append(self.hydrate_collection(value))
                    task_fields.append(field)
                else:
                    response[field] = value if value is not None else "N/A"

            # 4. Execução Assíncrona da Hidratação
            if tasks:
                results = await asyncio.gather(*tasks)
                for i, hydrated_list in enumerate(results):
                    response[task_fields[i]] = hydrated_list

            return response

        except Exception as e:
            logging.error(f"Erro no DataService: {str(e)}")
            return {"error": "Falha no processamento interno", "details": str(e)}

    async def _get_base_data(self, name: str, entity_type: str) -> Optional[dict]:
        """Lógica de Cache-Aside: Firestore (L2) -> SWAPI"""
        collection = ENTITY_MAP.get(entity_type)
        if not collection: return None

        # Tenta recuperar do Firestore (Cache Hit)
        cached = await self.db.get_by_name(collection, name)
        if cached:
            logging.info(f"⚡ [HIT] {name} recuperado do Firestore.")
            return cached

        # Busca na SWAPI (Cache Miss)
        logging.info(f"🌐 [MISS] {name} buscando na API Externa...")
        fetch_method = getattr(self.swapi, f"get_{entity_type}")
        result_model = await fetch_method(name)

        if result_model:
            data = result_model.model_dump(mode='json')
            data["type"] = entity_type # Tag para facilitar a View
            # Persiste no Firestore para futuras consultas
            await self.db.save(collection, data)
            return data
            
        return None

    async def hydrate_collection(self, urls: List[str]) -> List[str]:
        """Resolve uma lista de URLs em uma lista de nomes amigáveis."""
        tasks = []
        for url in urls:
            # Extrai o tipo da URL (ex: .../people/1/ -> people)
            raw_type = url.strip("/").split("/")[-2]
            target_type = TYPE_MAP.get(raw_type, "person")
            tasks.append(self._get_by_url_with_cache(url, target_type))

        results = await asyncio.gather(*tasks)
        return [res.get("name") or res.get("title") for res in results if res]

    async def _get_by_url_with_cache(self, url: str, entity_type: str) -> dict:
        """Busca uma URL específica com suporte a cache."""
        collection = ENTITY_MAP.get(entity_type)
        swapi_id = url.strip("/").split("/")[-1]
        doc_id = f"{entity_type}_{swapi_id}"
        
        cached = await self.db.get_document(collection, doc_id)
        if cached: return cached

        data_obj = await self.swapi.get_entity_by_url(url)
        if data_obj:
            data = data_obj.model_dump(mode='json')
            await self.db.save_with_id(collection, doc_id, data)
            return data
        return {}