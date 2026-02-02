from google.cloud import firestore
import logging

class FirestoreManager:
    def __init__(self, project_id: str):
        self.project_id = project_id

        self.db = firestore.Client(project=project_id)

    def get(self, collection: str, name: str):
        """Busca um documento pelo nome na coleção especificada."""
        doc_id = name.lower().replace(" ", "_")
        doc_ref = self.db.collection(collection).document(doc_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None

    def set(self, collection: str, name: str, data: dict):
        """Salva (ou sobrescreve) um documento na coleção."""
        doc_id = name.lower().replace(" ", "_")
        self.db.collection(collection).document(doc_id).set(data)
        logging.info(f"🔥 [CACHE SET] '{name}' salvo na coleção '{collection}'.")

    def get_document(self, collection: str, doc_id: str):
        """Busca direta por ID do documento."""
        doc_ref = self.db.collection(collection).document(doc_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
