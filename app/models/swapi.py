import logging
from types import SimpleNamespace
from typing import Optional

import requests

from app.models.entities import (
    CharacterSchema,
    FilmSchema,
    PlanetSchema,
    SpeciesSchema,
    StarshipSchema,
    VehicleSchema,
)


class SWAPIClient:
    def __init__(self):
        """
        Inicializa o cliente da API do SWAPI.

        Attributes
        ----------
        base_url : str
            URL base da API do SWAPI.
        """
        self.base_url = "https://swapi.dev/api"

    def _get_request(self, url: str) -> Optional[dict]:
        """
        Faz uma requisição GET para a URL especificada e retorna o resultado em formato JSON.

        Parameters
        ----------
        url : str
            A URL a ser buscada.

        Returns
        -------
        Optional[dict]
            O resultado da requisição em formato JSON ou None se a requisição falhar.
        """
        try:
            response = requests.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Erro ao buscar URL {url}: {e}")
            return None

    def get_person(self, name: str) -> Optional[CharacterSchema]:
        data = self._get_request(f"{self.base_url}/people/?search={name}")
        return (
            CharacterSchema(**data["results"][0])
            if data and data.get("count", 0) > 0
            else None
        )

    def get_movie(self, title: str) -> Optional[FilmSchema]:
        data = self._get_request(f"{self.base_url}/films/?search={title}")
        return (
            FilmSchema(**data["results"][0])
            if data and data.get("count", 0) > 0
            else None
        )

    def get_starship(self, name: str) -> Optional[StarshipSchema]:
        data = self._get_request(f"{self.base_url}/starships/?search={name}")
        return (
            StarshipSchema(**data["results"][0])
            if data and data.get("count", 0) > 0
            else None
        )

    def get_planet(self, name: str) -> Optional[PlanetSchema]:
        data = self._get_request(f"{self.base_url}/planets/?search={name}")
        return (
            PlanetSchema(**data["results"][0])
            if data and data.get("count", 0) > 0
            else None
        )

    def get_vehicle(self, name: str) -> Optional[VehicleSchema]:
        data = self._get_request(f"{self.base_url}/vehicles/?search={name}")
        return (
            VehicleSchema(**data["results"][0])
            if data and data.get("count", 0) > 0
            else None
        )

    def get_species(self, name: str) -> Optional[SpeciesSchema]:
        data = self._get_request(f"{self.base_url}/species/?search={name}")
        return (
            SpeciesSchema(**data["results"][0])
            if data and data.get("count", 0) > 0
            else None
        )

    def fetch_hydrated(self, name: str, entity_type: str):
        """
        Busca uma entidade na API do SWAPI com base em nome e tipo.

        Parameters
        ----------
        name : str
            Nome da entidade a ser buscada.
        entity_type : str
            Tipo da entidade a ser buscada.

        Returns
        -------
        Optional[dict]
            O resultado da busca em formato JSON ou None se a busca falhar.
        """
        method_map = {
            "people": "get_person",
            "planets": "get_planet",
            "films": "get_movie",
            "species": "get_species",
            "vehicles": "get_vehicle",
            "starships": "get_starship",
        }
        method_name = method_map.get(entity_type)
        if not method_name:
            logging.error(f"Invalid entity_type: {entity_type}")
            return None

        param_name = "title" if entity_type == "films" else "name"
        method_to_call = getattr(self, method_name, None)
        if not method_to_call:
            logging.error(
                f"Internal error: Method {method_name} not found in SWAPIClient"
            )
            return None
        return method_to_call(**{param_name: name})

    def get_entity_by_url(self, url: str):
        """
        Busca qualquer entidade diretamente pela URL fornecida pela SWAPI.
        """
        data = self._get_request(url)
        return SimpleNamespace(**data) if data else None
