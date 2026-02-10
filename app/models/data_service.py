from concurrent.futures import ThreadPoolExecutor
from datetime import date


class DataService:
    def __init__(self, db_manager, swapi_client):
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
        if isinstance(raw_filters, list):
            return raw_filters
        if isinstance(raw_filters, str) and raw_filters.strip():
            return [f.strip() for f in raw_filters.split(",")]
        return None

    def fetch_and_learn(self, name, entity_type):
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
        if "release_date" in data and isinstance(data["release_date"], date):
            data["release_date"] = data["release_date"].isoformat()
        self.db.set(entity_type, name, data)

    def hydrate_all_parallel(self, data):
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
