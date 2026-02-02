import os
from google.cloud import firestore

def bootstrap_nlp_config():
    project_id = "pod-ps-backend-python"
    db = firestore.Client(project=project_id)

    print(f"🛰️ Conectando ao projeto: {project_id}...")

    nlp_ref = db.collection("metadata").document("nlp_settings")

    nlp_data = {
        "intents": {
            "diretor": "director",
            "dirigiu": "director",
            "filmes": "films",
            "participou": "films",
            "naves": "starships",
            "pilotou": "starships",
            "planeta": "homeworld",
            "origem": "homeworld",
            "residentes": "residents",
            "habitantes": "population",
            "populacao": "population",
            "pilotos": "pilots",
            "especies": "species"
        },
        "intent_to_type_map": {
            "director": "films",
            "films": "people",  
            "starships": "people",
            "homeworld": "people",
            "residents": "planets",
            "population": "planets",
            "pilots": "starships",
            "species": "people"
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
        nlp_ref.set(nlp_data)
        print("✅ Documento 'metadata/nlp_settings' sincronizado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    bootstrap_nlp_config()