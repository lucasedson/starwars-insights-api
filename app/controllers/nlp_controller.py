import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from difflib import get_close_matches

class NLPController:
    def __init__(self, db_manager):
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
        resources = ['punkt', 'punkt_tab', 'stopwords']
        for res in resources:
            try:
                nltk.download(res, download_dir=self.nltk_path, quiet=True)
            except Exception:
                pass

    def _fuzzy_correction(self, name: str) -> str:
        # Se a lista estiver vazia por erro de banco, retorna o nome original
        if not self.known_entities:
            return name
        matches = get_close_matches(name, self.known_entities, n=1, cutoff=0.6)
        corrected = matches[0] if matches else name
        return self.movie_translation.get(corrected, corrected)

    def parse_sentence(self, text: str) -> dict:
        if not text:
            return {}

        tokens = word_tokenize(text.lower(), language='portuguese')
        palavras_limpas = [
            w for w in tokens 
            if (w.isalnum() or '-' in w) and w not in self.stop_words and w not in self.ruido_extra
        ]


        intent_to_type = self.config.get("intent_to_type_map", {})

        found_filter = None
        inferred_type = "people"
        
        for palavra in palavras_limpas:
            if palavra in self.intent_map:
                found_filter = self.intent_map[palavra]
                inferred_type = intent_to_type.get(found_filter, "people")
                break

        nome_tokens = [w for w in palavras_limpas if w not in self.intent_map]
        raw_name = " ".join(nome_tokens).title()
        corrected_name = self._fuzzy_correction(raw_name)


        planetas = set(self.config.get("known_planets", []))
        naves = set(self.config.get("known_starships", []))
        especies = set(self.config.get("known_species", []))

        filmes_en = set(self.config.get("known_films", []))
        filmes_pt = set(self.movie_translation.keys())

        if corrected_name in planetas and not found_filter:
            inferred_type = "planets"
        elif corrected_name in naves:
            inferred_type = "starships"
        elif corrected_name in especies:
            inferred_type = "species"
        elif corrected_name in filmes_en or corrected_name in filmes_pt:
            inferred_type = "films"


        corrected_name = corrected_name.replace("C-3Po", "C-3PO").replace("R2-D2", "R2-D2")

        return {
            "name": corrected_name,
            "filter": found_filter,
            "type": inferred_type,
            "original_query": text
        }