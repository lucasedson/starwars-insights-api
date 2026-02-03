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
        matches = get_close_matches(name, self.known_entities, n=1, cutoff=0.7)
        corrected = matches[0] if matches else name
        return self.movie_translation.get(corrected, corrected)
    
    def _fuzzy_intent(self, word: str) -> str:
        """Tenta encontrar a intenção correta mesmo com erro de digitação."""
        # Pegamos todas as palavras que disparam intenções (diretor, naves, etc)
        intent_keywords = list(self.intent_map.keys())
        
        # Procuramos o match mais próximo
        matches = get_close_matches(word, intent_keywords, n=1, cutoff=0.9)
        
        if matches:
            # Se achou (ex: 'diretorr' -> 'diretor'), retorna o valor real ('director')
            return self.intent_map[matches[0]]
        
        return None

    def parse_sentence(self, text: str) -> dict:
        if not text:
            return {}

        tokens = word_tokenize(text.lower(), language='portuguese')
        palavras_limpas = [
            w for w in tokens 
            if (w.isalnum() or '-' in w) and w not in self.stop_words and w not in self.ruido_extra
        ]

        # 1. IDENTIFICAÇÃO DE INTENÇÃO (Com Fuzzy Match)
        found_filter = None
        palavra_intencao_original = None

        for palavra in palavras_limpas:
            # Tenta match exato primeiro (performance)
            if palavra in self.intent_map:
                found_filter = self.intent_map[palavra]
                palavra_intencao_original = palavra
                break
            
            # Tenta fuzzy match (tolerância a erros de digitação)
            intent_fuzzy = self._fuzzy_intent(palavra)
            if intent_fuzzy:
                found_filter = intent_fuzzy
                palavra_intencao_original = palavra
                break

        # 2. IDENTIFICAÇÃO E CORREÇÃO DO NOME (Entidade)
        # Removemos apenas a palavra que foi identificada como intenção para isolar o nome
        nome_tokens = [w for w in palavras_limpas if w != palavra_intencao_original]
        raw_name = " ".join(nome_tokens).title()
        corrected_name = self._fuzzy_correction(raw_name)

        # 3. INFERÊNCIA DE TIPO BASEADA NA ENTIDADE
        category_map = {
            "planets": set(self.config.get("known_planets", [])),
            "starships": set(self.config.get("known_starships", [])),
            "vehicles": set(self.config.get("known_vehicles", [])),
            "species": set(self.config.get("known_species", [])),
            "films": set(self.config.get("known_films", [])).union(set(self.movie_translation.keys())),
            "people": set(self.config.get("known_people", []))
        }

        inferred_type = "people" # Fallback padrão
        for category, entities in category_map.items():
            if corrected_name in entities:
                inferred_type = category
                break

        # 4. TRATAMENTO ESPECIAL PARA FILMES / ENTIDADES
        # Se eu busco "A New Hope" (tipo filme) e a intenção é "filmes" (films),
        # limpamos o filtro para que a API traga o objeto completo do filme.
        if inferred_type == "films" and found_filter == "films":
            found_filter = None

        return {
            "name": corrected_name,
            "raw_name": raw_name,
            "filter": found_filter,
            "type": inferred_type,
            "original_query": text
        }