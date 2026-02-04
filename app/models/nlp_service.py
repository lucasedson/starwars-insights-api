import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from difflib import get_close_matches

class NLPService:
    def __init__(self, db_manager):
        
        '''
        Inicializa o serviço de NLP.

        Parameters
        ----------
        db_manager : app.models.database.FirestoreManager
            Gerenciador de banco de dados do Firebase.

        Attributes
        -------
        db : app.models.database.FirestoreManager
            Gerenciador de banco de dados do Firebase.
        nltk_path : str
            Caminho para o diretório de dados do NLTK.
        config : dict
            Configura es do servi o de NLP.
        intent_map : dict
            Mapa de inten es para palavras-chave.
        movie_translation : dict
            Mapa de tradu es de filmes.
        known_entities : list
            Lista de entidades conhecidas.
        stop_words : set
            Conjunto de palavras que devem ser ignoradas pt/br.
        ruido_extra : set
            Conjunto de palavras ruidosas extras.
        '''
        self.db = db_manager
        self.nltk_path = os.path.join("/tmp", "nltk_data")
        
        if not os.path.exists(self.nltk_path):
            os.makedirs(self.nltk_path)
        
        nltk.data.path.append(self.nltk_path)
        self._setup_nltk_resources()


        self.config = self.db.get_metadata("nlp_settings") or {}


        self.intent_map = self.config.get("intents", {})
        self.movie_translation = self.config.get("translations", {})

        self.known_entities = (
            self.config.get("known_films", []) +
            self.config.get("known_people", []) + 
            self.config.get("known_planets", []) + 
            self.config.get("known_starships", []) + 
            self.config.get("known_species", []) +
            list(self.movie_translation.keys())
        )

        self.stop_words = set(stopwords.words('portuguese')).union(set(stopwords.words('english')))
        self.ruido_extra = {'quais', 'quem', 'qual', 'quanto', 'quantos', 'o', 'a', 'os', 'as', 'de', 'do', 'da'}

    def _setup_nltk_resources(self):
        '''
        Configura os recursos do NLTK.
        '''
        resources = ['punkt', 'punkt_tab', 'stopwords']
        for res in resources:
            try:
                nltk.download(res, download_dir=self.nltk_path, quiet=True)
            except Exception:
                pass

    def _fuzzy_correction(self, name: str) -> str:
        """Correção de erros de digitação."""
        if not self.known_entities:
            return name
        matches = get_close_matches(name, self.known_entities, n=1, cutoff=0.7)
        corrected = matches[0] if matches else name
        return self.movie_translation.get(corrected, corrected)
    
    def _fuzzy_intent(self, word: str) -> str:
        """Tenta encontrar a intenção correta mesmo com erro de digitação."""

        intent_keywords = list(self.intent_map.keys())

        matches = get_close_matches(word, intent_keywords, n=1, cutoff=0.9)
        
        if matches:
            return self.intent_map[matches[0]]
        
        return None

    def parse_sentence(self, text: str) -> dict:
        """Analisa uma frase e retorna um dicionário com os dados extraidos.

        Parameters
        ----------
        text : str
            Frase a ser analisada.

        Returns
        -------
        dict
            Dicionário com os dados extraidos.
        """
        if not text:
            return {}

        tokens = word_tokenize(text.lower(), language='portuguese')
        palavras_limpas = [
            w for w in tokens 
            if (w.isalnum() or '-' in w) and w not in self.stop_words and w not in self.ruido_extra
        ]


        found_filter = None
        palavra_intencao_original = None

        for palavra in palavras_limpas:
            if palavra in self.intent_map:
                found_filter = self.intent_map[palavra]
                palavra_intencao_original = palavra
                break

            intent_fuzzy = self._fuzzy_intent(palavra)
            if intent_fuzzy:
                found_filter = intent_fuzzy
                palavra_intencao_original = palavra
                break

        nome_tokens = [w for w in palavras_limpas if w != palavra_intencao_original]
        raw_name = " ".join(nome_tokens).title()
        corrected_name = self._fuzzy_correction(raw_name)


        category_map = {
            "planets": set(self.config.get("known_planets", [])),
            "starships": set(self.config.get("known_starships", [])),
            "vehicles": set(self.config.get("known_vehicles", [])),
            "species": set(self.config.get("known_species", [])),
            "films": set(self.config.get("known_films", [])).union(set(self.movie_translation.keys())),
            "people": set(self.config.get("known_people", []))
        }

        inferred_type = "people"
        for category, entities in category_map.items():
            if corrected_name in entities:
                inferred_type = category
                break

        if inferred_type == "films" and found_filter == "films":
            found_filter = None

        return {
            "name": corrected_name,
            "raw_name": raw_name,
            "filter": found_filter,
            "type": inferred_type,
            "original_query": text
        }