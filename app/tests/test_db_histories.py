import os

import dotenv

from app.models.database import FirestoreManager

dotenv.load_dotenv()
project_id = os.getenv("GCP_PROJECT_ID")
db_manager = FirestoreManager(project_id)

user = "test@test.com"


def test_create_history():

    db_manager.create_or_update_my_search_history(user, "Altura do Yoda")
    history = db_manager.get_my_search_history(user)

    assert "queries" in history
    assert any(q["query"] == "Altura do Yoda" for q in history["queries"])


def test_update_history():
    db_manager.create_or_update_my_search_history(user, "Altura do Yoda")
    db_manager.create_or_update_my_search_history(user, "Altura do Darth Vader")
    history = db_manager.get_my_search_history(user)

    assert "queries" in history
    assert any(q["query"] == "Altura do Darth Vader" for q in history["queries"])


def test_delete_history():
    db_manager.delete_history(user)
    history = db_manager.get_my_search_history(user)
    assert history is None
