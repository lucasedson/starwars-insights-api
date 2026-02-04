import os
import sys

import dotenv

from app.models.database import FirestoreManager
from app.models.nlp_service import NLPService

dotenv.load_dotenv()
project_id = os.getenv("GCP_PROJECT_ID")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


def test_parse_sentence():
    db = FirestoreManager(project_id)
    nlp = NLPService(db)

    q = nlp.parse_sentence("Quem dirigiu a New Hope?")

    assert q["name"] == "A New Hope"
    assert q["type"] == "films"
    assert q["filter"] == "director"
