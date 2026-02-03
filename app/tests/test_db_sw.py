import pytest
from app.models.database import FirestoreManager
import os
project_id = os.getenv("GCP_PROJECT_ID")
db_manager = FirestoreManager(project_id)

def test_set():
    """Testa se o documento foi criado com sucesso."""
    db_manager.set("new_colection", "new_document", {"key": "value"})
    doc = db_manager.get("new_colection", "new_document")
    assert doc["key"] == "value"

def test_sobrescrita():
    """Testa se o documento foi sobrescrito com sucesso."""
    db_manager.set("new_colection", "new_document", {"key": "value2"})
    doc = db_manager.get("new_colection", "new_document")
    assert doc["key"] == "value2"

def test_delete():
    """Testa se o documento foi deletado com sucesso."""
    db_manager.delete_document("new_colection", "new_document")
    doc = db_manager.get_document("new_colection", "new_document")
    assert doc is None

