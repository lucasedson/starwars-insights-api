import os
from google.cloud import firestore

def bootstrap_nlp_config():
    project_id = "pod-ps-backend-python"
    db = firestore.Client(project=project_id)

    print(f"🛰️ Conectando ao projeto: {project_id}...")

    nlp_ref = db.collection("metadata").document("nlp_settings")

    nlp_data = {

        "intents": {
            # Relacionados a Filmes (FilmSchema)
            "director": "director",
            "diretor": "director",
            "dirigiu": "director",
            "producer": "producer",
            "produtor": "producer",
            "produtora": "producer",
            "release date": "release_date",
            "release_date": "release_date",
            "lancamento": "release_date",
            "episode": "episode_id",
            "episodio": "episode_id",
            "opening crawl": "opening_crawl",
            "abertura": "opening_crawl",

            # Relacionados a Personagens (CharacterSchema / SpeciesSchema)
            "films": "films",
            "movies": "films",
            "filmes": "films",
            "participou": "films",
            "starships": "starships",
            "spaceships": "starships",
            "flying": "starships",
            "naves": "starships",
            "pilotou": "starships",
            "vehicles": "vehicles",
            "veiculos": "vehicles",
            "homeworld": "homeworld",
            "birth world": "homeworld",
            "planets": "homeworld",
            "planeta": "homeworld",
            "origem": "homeworld",
            "gender": "gender",
            "genero": "gender",
            "birth year": "birth_year",
            "birth_year": "birth_year",
            "nascimento": "birth_year",
            "species": "species",
            "especie": "species",
            "height": "height",
            "altura": "height",
            "mass": "mass",
            "weight": "mass",
            "peso": "mass",
            "massa": "mass",
            "language": "language",
            "idioma": "language",

            # Relacionados a Planetas (PlanetSchema)
            "residents": "residents",
            "residentes": "residents",
            "population": "population",
            "habitantes": "population",
            "populacao": "population",
            "climate": "climate",
            "clima": "climate",
            "terrain": "terrain",
            "terreno": "terrain",
            "diameter": "diameter",
            "diametro": "diameter",
            "gravity": "gravity",
            "gravidade": "gravity",
            "surface water": "surface_water",
            "agua": "surface_water",

            # Relacionados a Naves e Veículos (StarshipSchema / VehicleSchema)
            "pilots": "pilots",
            "pilotos": "pilots",
            "model": "model",
            "modelo": "model",
            "manufacturer": "manufacturer",
            "fabricante": "manufacturer",
            "cost": "cost_in_credits",
            "price": "cost_in_credits",
            "custo": "cost_in_credits",
            "passengers": "passengers",
            "passageiros": "passengers",
            "crew": "crew",
            "tripulacao": "crew",
            "speed": "max_atmosphering_speed",
            "velocidade": "max_atmosphering_speed",
            "cargo": "cargo_capacity",
            "capacidade": "cargo_capacity",
            "class": "starship_class",
            "classe": "starship_class"
        },
        "intent_to_type_map": {
            "director": "films",
            "producer": "films",
            "release_date": "films",
            "episode_id": "films",
            "opening_crawl": "films",
            "starships": "people",
            "vehicles": "people",
            "homeworld": "people",
            "gender": "people",
            "birth_year": "people",
            "height": "people",
            "mass": "people",
            "residents": "planets",
            "population": "planets",
            "climate": "planets",
            "terrain": "planets",
            "diameter": "planets",
            "pilots": "starships",
            "model": "starships",
            "manufacturer": "starships",
            "starship_class": "starships",
            "language": "species",
            "classification": "species"
        },
        "translations": {
            "A Ameaça Fantasma": "The Phantom Menace",
            "Ataque dos Clones": "Attack of the Clones",
            "A Vingança dos Sith": "Revenge of the Sith",
            "Uma Nova Esperança": "A New Hope",
            "O Império Contra-Ataca": "The Empire Strikes Back",
            "O Retorno de Jedi": "Return of the Jedi"
        },
        "known_films": ["The Phantom Menace", "Attack of the Clones", "Revenge of the Sith", "A New Hope", "The Empire Strikes Back", "Return of the Jedi"],
        "known_planets": ["Tatooine", "Alderaan", "Hoth", "Dagobah", "Bespin", "Endor", "Naboo", "Coruscant"],
        "known_starships": ["Millennium Falcon", "X-Wing", "TIE Fighter", "Death Star", "Snowspeeder"],
        "known_people": ["Luke Skywalker", "Yoda", "Darth Vader", "Obi-Wan Kenobi"],
        "kwown_species": [],
        "known_vehicles": []
    }

    try:
        nlp_ref.set(nlp_data, merge=True)
        print("✅ Documento 'metadata/nlp_settings' sincronizado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    bootstrap_nlp_config()