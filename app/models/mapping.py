"""
Centraliza o mapeamento de entidades da SWAPI para coleções do Firestore.
"""

ENTITY_MAP = {
    "person": "people",
    "film": "films",
    "starship": "starships",
    "planet": "planets",
    "vehicle": "vehicles",
    "species": "species"
}

TYPE_MAP = {
    "people": "person",
    "films": "film",
    "starships": "starship",
    "planets": "planet",
    "vehicles": "vehicle",
    "species": "species"
}
