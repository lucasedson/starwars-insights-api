from datetime import date
from typing import Annotated, Any, List, Optional

from pydantic import BaseModel, BeforeValidator


def parse_swapi_numeric(v: Any) -> Optional[float]:
    """Converte strings da SWAPI ('unknown', '1,000') em float ou None.

    Se o valor for None ou uma das strings 'unknown', 'n/a', 'none', 'indefinite' ou 'unknown', retorna None.
    Se o valor for uma string, remove as vírgulas e tente converter para float.
    Se a convers o falhar, retorna None.

    Parameters
    ----------
    v : Any
        O valor a ser convertido.

    Returns
    -------
    Optional[float]
        O valor convertido ou None se a conversão falhar.
    """

    if v in [None, "unknown", "n/a", "none", "indefinite", "unknown"]:
        return None
    try:
        if isinstance(v, str):
            v = v.replace(",", "")
        return float(v)
    except (ValueError, TypeError):
        return None


def parse_swapi_int(v: Any) -> Optional[int]:
    """Converte valores para int após passar pelo parse de float."""
    res = parse_swapi_numeric(v)
    return int(res) if res is not None else None


SwapiFloat = Annotated[Optional[float], BeforeValidator(parse_swapi_numeric)]
SwapiInt = Annotated[Optional[int], BeforeValidator(parse_swapi_int)]


class CharacterSchema(BaseModel):
    name: str
    birth_year: str
    eye_color: str
    gender: str
    hair_color: str
    skin_color: str
    height: SwapiInt
    mass: SwapiFloat
    homeworld: str
    films: List[str]
    species: List[str]
    starships: List[str]
    vehicles: List[str]
    url: str
    created: str
    edited: str


class FilmSchema(BaseModel):
    title: str
    episode_id: int
    opening_crawl: str
    director: str
    producer: str
    release_date: date
    characters: List[str]
    planets: List[str]
    starships: List[str]
    vehicles: List[str]
    species: List[str]
    created: str
    edited: str
    url: str


class StarshipSchema(BaseModel):
    name: str
    model: str
    manufacturer: str
    cost_in_credits: SwapiFloat
    length: SwapiFloat
    max_atmosphering_speed: SwapiInt
    crew: str  # Mantido str pois pode ser "1-5"
    passengers: SwapiInt
    cargo_capacity: SwapiFloat
    consumables: str
    hyperdrive_rating: str
    MGLT: str
    starship_class: str
    pilots: List[str]
    films: List[str]
    created: str
    edited: str
    url: str


class VehicleSchema(BaseModel):
    name: str
    model: str
    manufacturer: str
    cost_in_credits: SwapiFloat
    length: SwapiFloat
    max_atmosphering_speed: SwapiInt
    crew: SwapiInt
    passengers: SwapiInt
    cargo_capacity: SwapiFloat
    consumables: str
    pilots: List[str]
    films: List[str]
    created: str
    edited: str
    url: str


class SpeciesSchema(BaseModel):
    name: str
    classification: str
    designation: str
    average_height: SwapiFloat
    average_lifespan: SwapiInt
    hair_colors: str
    eye_colors: str
    skin_colors: str
    language: str
    homeworld: Optional[str]
    people: List[str]
    films: List[str]
    created: str
    edited: str
    url: str


class PlanetSchema(BaseModel):
    name: str
    rotation_period: SwapiInt
    orbital_period: SwapiInt
    diameter: SwapiInt
    climate: str
    gravity: str
    terrain: str
    surface_water: SwapiFloat
    population: SwapiFloat
    residents: List[str]
    films: List[str]
    created: str
    edited: str
    url: str
