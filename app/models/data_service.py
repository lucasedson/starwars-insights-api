from concurrent.futures import ThreadPoolExecutor
from datetime import date


class DataService:
    def __init__(self, db_manager, swapi_client):
        """
        Inicializa o serviço de dados.

        Parameters
        ----------
        db_manager : app.models.database.FirestoreManager
            Gerenciador de banco de dados do Firebase.
        swapi_client : app.models.swapi.SWAPIClient
            Cliente da API do SWAPI.

        Attributes
        -------
        db : app.models.database.FirestoreManager
            Gerenciador de banco de dados do Firebase.
        swapi : app.models.swapi.SWAPIClient
            Cliente da API do SWAPI.
        hydration_map : dict
            Mapa de entidades para palavras-chave.
        """
        self.db = db_manager
        self.swapi = swapi_client
        self.hydration_map = {
            "films": "title",
            "pilots": "name",
            "residents": "name",
            "characters": "name",
            "people": "name",
            "species": "name",
            "starships": "name",
            "vehicles": "name",
            "homeworld": "name",
            "planets": "name",
        }

    def parse_filters(self, raw_filters):
        '''
        Parseia os filtros recebidos e retorna uma lista de strings

        Parameters
        ----------
        raw_filters : str or list
            Filtros recebidos.

        '''

        if isinstance(raw_filters, list):
            return raw_filters
        if isinstance(raw_filters, str) and raw_filters.strip():
            return [f.strip() for f in raw_filters.split(",")]
        return None

    def fetch_and_learn(self, name, entity_type):
        
        '''
        Busca uma entidade na API do SWAPI com base em nome e tipo, e aprender com o resultado.

        Parameters
        ----------
        name : str
            Nome da entidade a ser buscada.
        entity_type : str
            Tipo da entidade a ser buscada.

        Returns
        -------
        dict
            Dicionário com a entidade formatada.

        Notes
        -----
        Se a entidade for encontrada, adiciona ao banco de dados como conhecida.
        '''
        pydantic_data = self.swapi.fetch_hydrated(name, entity_type)
        if not pydantic_data:
            return None
        data = pydantic_data.model_dump(by_alias=True)
        real_name = data.get("name") or data.get("title")
        metadata_map = {
            "people": "known_people",
            "planets": "known_planets",
            "starships": "known_starships",
            "films": "known_films",
            "species": "known_species",
            "vehicles": "known_vehicles",
        }
        target_list = metadata_map.get(entity_type)
        if target_list:
            self.db.add_to_metadata_list(target_list, real_name)
        return data

    def cache_new_data(self, entity_type, name, data):
        '''
        Adiciona novos dados ao cache, formatando a data se necessário.

        Parameters
        ----------
        entity_type : str
            Tipo da entidade (Ex: "people", "planets", etc.).
        name : str
            Nome da entidade.
        data : dict
            Dicionário com a entidade formatada.

        Returns
        -------
        None

        Notes
        -----
        Se a data conter a chave "release_date" e o valor for uma instancia de datetime.date, converte para string no formato ISO 8601.
        '''
        if "release_date" in data and isinstance(data["release_date"], date):
            data["release_date"] = data["release_date"].isoformat()
        self.db.set(entity_type, name, data)

    def hydrate_all_parallel(self, data):
        '''
        Hidrata todos os campos possíveis em uma estrutura de dados.

        Parameters
        ----------
        data : dict
            Dicionário com a estrutura de dados a ser hidratada.

        Returns
        -------
        dict
            Dicionário com a estrutura de dados hidratada.

        Notes
        -----
        Utiliza o módulo concurrent.futures para executar a hidratação de forma paralela.
        '''
        fields_to_hydrate = [f for f in self.hydration_map.keys() if f in data]
        if not fields_to_hydrate:
            return data

        with ThreadPoolExecutor(max_workers=10) as executor:
            list(
                executor.map(
                    lambda f: self.hydrate_field(data, f, self.hydration_map[f]),
                    fields_to_hydrate,
                )
            )
        return data

    def hydrate_field(self, data: dict, field_name: str, lookup_key: str) -> dict:

        '''
        Hidrata um campo em uma estrutura de dados.

        Parameters
        ----------
        data : dict
            Dicionário com a estrutura de dados a ser hidratada.
        field_name : str
            Nome do campo a ser hidratado.
        lookup_key : str
            Chave a ser utilizada para a busca da entidade hidratada.

        Returns
        -------
        dict
            Dicionário com a estrutura de dados hidratada.

        Notes
        -----
        Se o valor do campo for uma lista, iterará sobre a lista e hidratará cada item.
        Se o valor do campo for uma string, tentará hidratar a string como se fosse uma URL da SWAPI.
        '''
        field_value = data.get(field_name)
        if not field_value:
            return data

        if isinstance(field_value, list):
            hydrated_items = []
            for item in field_value:
                if isinstance(item, str) and "swapi.dev" in item:
                    item_data = self.swapi.get_entity_by_url(item)
                    if item_data:
                        val = getattr(item_data, lookup_key, None) or (
                            item_data.get(lookup_key)
                            if isinstance(item_data, dict)
                            else None
                        )
                        hydrated_items.append(val if val else item)
                    else:
                        hydrated_items.append(item)
                else:
                    hydrated_items.append(item)
            data[field_name] = hydrated_items

        elif isinstance(field_value, str) and "swapi.dev" in field_value:
            item_data = self.swapi.get_entity_by_url(field_value)
            if item_data:
                val = getattr(item_data, lookup_key, None) or (
                    item_data.get(lookup_key) if isinstance(item_data, dict) else None
                )
                data[field_name] = val if val else field_value

        return data
