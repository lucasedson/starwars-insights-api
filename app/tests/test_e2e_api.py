import requests
import pytest

import os
import dotenv

dotenv.load_dotenv()
E2E_TESTS = os.getenv("E2E_TESTS", "false").lower()

if E2E_TESTS == "false":
    pytest.skip("Teste de E2E desabilitado", allow_module_level=True)
# URL base do servidor de desenvolvimento local
BASE_URL = "http://localhost:8080"

# --- Testes para a entidade 'people' ---

def test_get_person_full_data():
    """
    Testa a busca por uma pessoa sem filtros, esperando todos os dados hidratados.
    """
    params = {"name": "Luke Skywalker", "type": "people"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["entity"] == "Luke Skywalker"
    assert data["category"] == "people"
    assert data["insight_value"]["name"] == "Luke Skywalker"
    assert data["insight_value"]["homeworld"] == "Tatooine"  # Campo hidratado
    assert "A New Hope" in data["insight_value"]["films"]  # Campo de lista hidratado
    assert data["insight_value"]["height"] == 172  # Checagem de tipo numérico
    assert data["insight_value"]["mass"] == 77  # Checagem de tipo numérico

def test_get_person_single_filter():
    """
    Testa a busca por uma pessoa com um único filtro.
    """
    params = {"name": "Leia Organa", "type": "people", "filter": "height"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["entity"] == "Leia Organa"
    assert "height" in data["insight_value"]
    assert data["insight_value"]["height"] == 150 # Corrigido para número

def test_get_person_multiple_filters():
    """
    Testa a busca por uma pessoa com múltiplos filtros, incluindo campos hidratados.
    """
    params = {"name": "Darth Vader", "type": "people", "filter": "homeworld,films,height"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["entity"] == "Darth Vader"
    insight = data["insight_value"]
    assert sorted(list(insight.keys())) == sorted(["homeworld", "films", "height"])
    assert insight["homeworld"] == "Tatooine"
    assert "Revenge of the Sith" in insight["films"]
    assert insight["height"] == 202  # Checagem de tipo numérico

# --- Testes para a entidade 'starships' ---

def test_get_starship_full_data():
    """
    Testa a busca por uma nave, esperando todos os dados hidratados.
    """
    params = {"name": "Millennium Falcon", "type": "starships"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["entity"] == "Millennium Falcon"
    assert "Chewbacca" in data["insight_value"]["pilots"] # Lista hidratada
    assert "The Empire Strikes Back" in data["insight_value"]["films"]

def test_get_starship_multiple_filters():
    """
    Testa a busca por uma nave com múltiplos filtros.
    """
    params = {"name": "X-wing", "type": "starships", "filter": "model,manufacturer"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["entity"] == "X-wing"
    insight = data["insight_value"]
    assert "model" in insight
    assert "manufacturer" in insight
    assert insight["model"] == "T-65 X-wing"

def test_get_starship_hydrated_list_filter():
    """
    Testa o filtro por um campo de lista que deve ser hidratado.
    """
    params = {"name": "Death Star", "type": "starships", "filter": "films"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "A New Hope" in data["insight_value"]["films"]

# --- Testes para a entidade 'planets' ---

def test_get_planet_full_data():
    """
    Testa a busca por um planeta, esperando todos os dados hidratados.
    """
    params = {"name": "Hoth", "type": "planets"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["entity"] == "Hoth"
    # Hoth não tem residentes conhecidos na API, então a lista deve estar vazia
    assert data["insight_value"]["residents"] == []
    assert "The Empire Strikes Back" in data["insight_value"]["films"]

def test_get_planet_single_filter():
    """
    Testa a busca por um planeta com um único filtro.
    """
    params = {"name": "Tatooine", "type": "planets", "filter": "climate"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["insight_value"]["climate"] == "arid"

def test_get_planet_hydrated_residents():
    """
    Testa a busca por um planeta com residentes, esperando a hidratação da lista.
    """
    params = {"name": "Alderaan", "type": "planets", "filter": "residents"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    residents = data["insight_value"]["residents"]
    assert "Leia Organa" in residents
    assert "Bail Prestor Organa" in residents

# --- Testes para a entidade 'films' ---

def test_get_film_full_data():
    """
    Testa a busca por um filme, esperando todos os dados hidratados.
    """
    params = {"name": "A New Hope", "type": "films"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["entity"] == "A New Hope"
    assert data["insight_value"]["director"] == "George Lucas"
    assert "Luke Skywalker" in data["insight_value"]["characters"] # Lista hidratada

def test_get_film_single_filter():
    """
    Testa a busca por um filme com um único filtro.
    """
    params = {"name": "The Empire Strikes Back", "type": "films", "filter": "episode_id"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["insight_value"]["episode_id"] == 5

def test_get_film_multiple_filters():
    """
    Testa a busca por um filme com múltiplos filtros e hidratação.
    """
    params = {"name": "Return of the Jedi", "type": "films", "filter": "planets,director"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    insight = data["insight_value"]
    assert "Tatooine" in insight["planets"]
    assert insight["director"] == "Richard Marquand"

# --- Testes para a entidade 'vehicles' ---

def test_get_vehicle_full_data():
    """
    Testa a busca por um veículo com todos os dados.
    """
    params = {"name": "Sand Crawler", "type": "vehicles"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["entity"] == "Sand Crawler"
    assert data["insight_value"]["model"] == "Digger Crawler"
    # O Sand Crawler não tem pilotos conhecidos na API
    assert data["insight_value"]["pilots"] == []

def test_get_vehicle_single_filter():
    """
    Testa a busca por um veículo com um único filtro.
    """
    params = {"name": "Snowspeeder", "type": "vehicles", "filter": "crew"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["insight_value"]["crew"] == 2

def test_get_vehicle_multiple_filters():
    """
    Testa a busca por um veículo com múltiplos filtros.
    """
    params = {"name": "TIE bomber", "type": "vehicles", "filter": "model,films"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    insight = data["insight_value"]
    assert insight["model"] == "TIE/sa bomber"
    assert "The Empire Strikes Back" in insight["films"]
    assert "Return of the Jedi" in insight["films"]

# --- Testes para a entidade 'species' ---

def test_get_species_full_data():
    """
    Testa a busca por uma espécie com todos os dados.
    """
    params = {"name": "wookie", "type": "species"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["entity"] == "Wookie"
    assert data["insight_value"]["language"] == "Shyriiwook"
    assert data["insight_value"]["homeworld"] == "Kashyyyk" # Campo único hidratado

def test_get_species_single_filter():
    """
    Testa a busca por uma espécie com um único filtro.
    """
    params = {"name": "droid", "type": "species", "filter": "classification"}
    response = requests.get(BASE_URL, params=params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["insight_value"]["classification"] == "artificial"
