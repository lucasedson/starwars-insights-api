from google.cloud import firestore

class MetadataSyncer:
    def __init__(self):
        self.db = firestore.Client()
        self.settings_ref = self.db.collection('metadata').document('nlp_settings')
        
        # Mapeamento: Coleção no Firestore -> Campo na lista de conhecidos
        self.collection_map = {
            "people": "known_people",
            "planets": "known_planets",
            "films": "known_films",
            "starships": "known_starships",
            "vehicles": "known_vehicles",
            "species": "known_species"
        }

    def sync(self):
        print("🚀 Iniciando sincronização de metadados...")
        
        updates = {}

        for collection_name, metadata_key in self.collection_map.items():
            print(f"--- Processando coleção: {collection_name} ---")
            
            # Busca todos os documentos da coleção
            docs = self.db.collection(collection_name).stream()
            
            names = []
            for doc in docs:
                data = doc.to_dict()
                # Filmes usam 'title', o resto usa 'name'
                name = data.get("name") or data.get("title")
                if name:
                    names.append(name)
            
            if names:
                # Usamos array_union para não duplicar nomes que já existem lá
                updates[metadata_key] = firestore.ArrayUnion(names)
                print(f"✅ Encontrados {len(names)} itens para {metadata_key}")

        if updates:
            self.settings_ref.update(updates)
            print("\n✨ Firestore atualizado com sucesso!")
        else:
            print("\nNenhum dado novo encontrado para sincronizar.")

if __name__ == "__main__":
    syncer = MetadataSyncer()
    syncer.sync()