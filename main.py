import functions_framework
from app.controllers.insight_controller import InsightController
from app.models.database import FirestoreManager
from app.models.swapi import SWAPIClient

# A inicialização agora é segura para ser global porque é síncrona.
project_id = "pod-ps-backend-python"
db_manager = FirestoreManager(project_id)
swapi_client = SWAPIClient()
controller = InsightController(db_manager, swapi_client)

@functions_framework.http
def star_wars_insights(request):
    """
    Ponto de entrada único da Cloud Function, agora operando de forma síncrona.
    """
    return controller.handle_request(request)
