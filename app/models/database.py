import logging
from datetime import date, datetime

from google.cloud import firestore


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

    def delete_document(self, collection: str, doc_id: str):
        doc_ref = self.db.collection(collection).document(doc_id)
        doc_ref.delete()

    def get_metadata(self, doc_name: str) -> dict:
        """Busca documentos de configuração na coleção 'metadata'."""
        try:
            doc_ref = self.db.collection("metadata").document(doc_name)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else {}
        except Exception as e:
            print(f"Erro ao buscar metadados: {e}")
            return {}

    def add_to_metadata_list(self, list_name: str, item: str):
        """Adiciona um novo item a uma lista de metadados (ex: known_people)."""
        try:
            doc_ref = self.db.collection("metadata").document("nlp_settings")
            doc_ref.update({list_name: firestore.ArrayUnion([item])})
        except Exception as e:
            print(f"Erro ao atualizar metadados: {e}")
            return

    def check_and_update_quota(self, identifier: str, limit: int) -> bool:
        """
        Verifica se o usuário atingiu a cota.
        Retorna True se puder prosseguir, False se excedeu.
        """
        today = date.today().isoformat()
        doc_ref = self.db.collection("usage_stats").document(identifier)

        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set({"count": 1, "last_reset": today})
            return True

        data = doc.to_dict()

        # Reset diário
        if data.get("last_reset") != today:
            doc_ref.set({"count": 1, "last_reset": today})
            return True

        if data.get("count") >= limit:
            return False

        # Incrementa o contador atomicamente
        doc_ref.update({"count": firestore.Increment(1)})
        return True

    def check_quota(self, identifier: str, limit: int) -> bool:
        today = date.today().isoformat()
        doc_ref = self.db.collection("usage_stats").document(identifier)

        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set({"count": 1, "last_reset": today})
            return True

        data = doc.to_dict()
        if data.get("last_reset") != today:
            doc_ref.set({"count": 1, "last_reset": today})
            return True

        if data.get("count") >= limit:
            return False

        doc_ref.update({"count": firestore.Increment(1)})
        return True

    def create_or_update_my_search_history(self, identifier: str, query: str):
        doc_ref = self.db.collection("search_histories").document(identifier)
        doc_ref.set(
            {
                "queries": firestore.ArrayUnion(
                    [
                        {
                            "query": query,
                            "timestamp": str(
                                datetime.now()
                            ),  # firestore.SERVER_TIMESTAMP
                        }
                    ]
                )
            },
            merge=True,
        )
        logging.info(f"🔥 [HISTORY] '{query}' adicionado ao histórico.")

    def get_my_search_history(self, identifier: str):
        doc_ref = self.db.collection("search_histories").document(identifier)
        doc = doc_ref.get()
        return doc.to_dict()

    def delete_history(self, identifier: str):
        doc_ref = self.db.collection("search_histories").document(identifier)
        doc_ref.delete()
