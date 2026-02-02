import functions_framework
from app.controllers.insight_controller import InsightController
from app.models.database import FirestoreManager
from app.models.swapi import SWAPIClient

# Singleton das dependências para Warm Start
project_id = "pod-ps-backend-python"
db_manager = FirestoreManager(project_id)
swapi_client = SWAPIClient()
controller = InsightController(db_manager, swapi_client)

@functions_framework.http
def star_wars_insights(request):
    """
    Entry point da Cloud Function.
    Aceita: 
    - GET /?q=Quais filmes Luke participou?
    - GET /?name=Luke Skywalker&type=people
    """
    return controller.handle_request(request)