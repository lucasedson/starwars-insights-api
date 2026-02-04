import logging
from flask import redirect
from app.views.responses import format_insight_response
from app.controllers.nlp_controller import NLPController
from app.utils.auth import get_google_auth_url
import requests
import os
from app.models.data_service import DataService

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
api_gateway_url = os.getenv("API_GATEWAY_URL")
frontend_url = os.getenv("FRONTEND_URL")
class InsightController:
    def __init__(self, db_manager, swapi_client):
        self.db = db_manager
        self.swapi = swapi_client
        self.nlp = NLPController(self.db)

        self.data_service = DataService(self.db, self.swapi)

    def handle_login(self):
        '''Redireciona o usuário para a autenticação do Google.'''
        return redirect(get_google_auth_url())

    def handle_callback(self, request):
        '''Recebe o código de autenticação do Google e retorna o token de acesso ao front.'''
        code = request.args.get('code')
        if not code:
            return {"error": "No code provided"}, 400

        try:
            token_endpoint = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": f"{api_gateway_url}/callback",
                "grant_type": "authorization_code",
            }

            response = requests.post(token_endpoint, data=data)
            token_data = response.json()

            if "error" in token_data:
                return {"error": f"Google API Error: {token_data.get('error_description')}"}, 400

            id_token = token_data.get("id_token")


            return redirect(f"{frontend_url}#id_token={id_token}")

        except Exception as e:
            return {"error": str(e)}, 500
    def get_user(self, user_data):
        """
        Verifica se o usuário está autenticado e retorna o status de autenticação.
        
        Parameters
        ----------
        user_data : dict
            Dados do usuário, incluindo o e-mail.
        
        Returns
        -------
        dict
            Dicionário com o status de autenticação do usuário.
        int
            Código de status HTTP.
        """
        if user_data:
            user_data["is_auth"] = True

            if "gserviceaccount.com" in user_data.get("email", ""):
                user_data["name"] = "Usuário Cloud"
            
            logging.info(f"🔥 [AUTH] Enviando status para o front: {user_data.get('email')}")
            return user_data, 200

        return {"is_auth": False}, 401
        

    def get_known_entities(self):
        '''Retorna todas as entidades conhecidas catalogadas no sistema.'''
        settings = self.db.get_metadata("nlp_settings") or {}
        
        known_data = {
            key: value for key, value in settings.items() 
            if key.startswith("known_")
        }
        
        default_structure = {
            "known_films": [], "known_people": [], "known_planets": [],
            "known_starships": [], "known_species": [], "known_vehicles": []
        }
        
        return {**default_structure, **known_data}, 200

    def get_my_history(self, user_data=None):
        '''Retorna a lista de histórico de buscas do usuário.
        
        Parameters
        ----------
        user_data : dict
            Dados do usuário, incluindo o e-mail.
                
        Notes
        -----
        Se o usuário não estiver autenticado, retorna um erro 401.'''
    
        if not user_data:
            return {"error": "User not authenticated"}, 401
        
        user_email = user_data.get("email")
        return self.db.get_my_search_history(user_email), 200
    
    
    def handle_insight(self, request, user_data=None):
        '''Trata uma requisição de insight, podendo vir de uma busca natural ou de uma busca parametrizada.
    
        Se a requisição vier de uma busca natural, utiliza o NLP para extrair as informações necessárias.
        Se a requisição vier de uma busca parametrizada, usa as informações passadas como parâmetro.
        
        Em seguida, busca a entidade no banco de dados e, se não encontrar, tenta buscar na API do SWAPI.
        Se encontrar a entidade, a retorna com a resposta formatada.
        Caso contrário, retorna um erro ao front.
        
        Se o usuário estiver autenticado, salva a busca no banco de dados.
        
        Parameters
        ----------
        request : flask.request
            Requisição HTTP.
        user_data : dict
            Dados do usuário autenticado, se houver.  
             

    
        Returns
        -------
        dict
            Dicionário com a resposta formatada.
        
        int
            Código de status HTTP.

        Examples
        ------- 
            request.args = {
                q: "Qual a altura do Yoda?"
            }

            handle_insight(request)

        --------

        request.args = {
            name: "Darth Vader",
            type: "people",
            filter: "height"
        }
        
        handle_insight(request)


        '''
        
        params = request.args
        query_natural = params.get("q")
        
        if query_natural:
            nlp_res = self.nlp.parse_sentence(query_natural)
            search_name = nlp_res.get("name")
            display_name = nlp_res.get("raw_name")
            entity_type = nlp_res.get("type")
            raw_filters = nlp_res.get("filter")
        else:
            display_name = params.get("name")
            search_name = self.nlp._fuzzy_correction(display_name)
            entity_type = params.get("type")
            raw_filters = params.get("filter")

        suggestion = None
        if search_name.lower() != display_name.lower():
            suggestion = search_name

        data = self.db.get(entity_type, search_name)
        source = "firestore"

        if not data:
            source = "live"
            data = self.data_service.fetch_and_learn(search_name, entity_type)
            if not data or "error" in data:
                return format_insight_response(data or {"error": "Not found"}, self.data_service.parse_filters(raw_filters), "error")
            
            data = self.data_service.hydrate_all_parallel(data)
            data['type'] = entity_type
            self.data_service.cache_new_data(entity_type, (data.get("name") or data.get("title")), data)
        else:
            data['type'] = entity_type


        if user_data:            
            self.db.create_or_update_my_search_history(user_data.get("email"), params)

        return format_insight_response(
            data, 
            self.data_service.parse_filters(raw_filters), 
            source, 
            suggestion=suggestion
        )
