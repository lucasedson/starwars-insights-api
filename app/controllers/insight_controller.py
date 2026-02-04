from app.models.data_service import DataService
from app.models.nlp_service import NLPService
from app.views.responses import format_insight_response


class InsightController:
    def __init__(self, db_manager, swapi_client):
        """
        Inicializa o controlador de insights.

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
        np : app.controllers.nlp_controller.NLPController
            Controlador de entidades nomeadas.
        data_service : app.models.data_service.DataService
            Servi o de dados do Star Wars.
        """
        self.db = db_manager
        self.swapi = swapi_client
        self.nlp = NLPService(self.db)

        self.data_service = DataService(self.db, self.swapi)

    def get_known_entities(self):
        """Retorna todas as entidades conhecidas catalogadas no sistema."""
        settings = self.db.get_metadata("nlp_settings") or {}

        known_data = {
            key: value for key, value in settings.items() if key.startswith("known_")
        }

        default_structure = {
            "known_films": [],
            "known_people": [],
            "known_planets": [],
            "known_starships": [],
            "known_species": [],
            "known_vehicles": [],
        }

        return {**default_structure, **known_data}, 200

    def get_my_history(self, user_data=None):
        """Retorna a lista de histórico de buscas do usuário.

        Parameters
        ----------
        user_data : dict
            Dados do usuário, incluindo o e-mail.

        Notes
        -----
        Se o usuário não estiver autenticado, retorna um erro 401."""

        if not user_data:
            return {"error": "User not authenticated"}, 401

        user_email = user_data.get("email")
        return self.db.get_my_search_history(user_email), 200

    def handle_insight(self, request, user_data=None):
        """Trata uma requisição de insight, podendo vir de uma busca natural ou de uma busca parametrizada.

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


        """

        params = request.args

        if not params:
            return {
                "error": "No query provided",
                "message": "See the documentation: https://lucasedson.github.io/starwars-insights-api/",
            }, 400
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
                return format_insight_response(
                    data or {"error": "Not found"},
                    self.data_service.parse_filters(raw_filters),
                    "error",
                )

            data = self.data_service.hydrate_all_parallel(data)
            data["type"] = entity_type
            self.data_service.cache_new_data(
                entity_type, (data.get("name") or data.get("title")), data
            )
        else:
            data["type"] = entity_type

        if user_data:
            self.db.create_or_update_my_search_history(user_data.get("email"), params)

        return format_insight_response(
            data,
            self.data_service.parse_filters(raw_filters),
            source,
            suggestion=suggestion,
        )
