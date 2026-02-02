import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from difflib import get_close_matches

class NLPController:
    def __init__(self):

        self.nltk_path = os.path.join("/tmp", "nltk_data")
        if not os.path.exists(self.nltk_path):
            os.makedirs(self.nltk_path)
        
        nltk.data.path.append(self.nltk_path)


        self._setup_nltk_resources()


        self.stop_words = set(stopwords.words('portuguese')).union(set(stopwords.words('english')))
        self.ruido_extra = {'quais', 'quem', 'qual', 'quanto', 'quantos', 'o', 'a', 'os', 'as', 'de', 'do', 'da'}
        
        # mapeamento de intenções (Filters)
        self.intent_map = {
            "filmes": "films", "participou": "films", "apareceu": "films",
            "naves": "starships", "pilotou": "starships", "nave": "starships",
            "planeta": "homeworld", "origem": "homeworld", "terra": "homeworld",
            "residentes": "residents", "mora": "residents", "habitantes": "population", "populacao": "population",
            "pilotos": "pilots", "pilota": "pilots",

            "especies": "species", "espécie": "species"
        }

        # entidades conhecidas
        self.known_entities = [
            "Luke Skywalker", "C-3PO", "R2-D2", "Darth Vader", "Leia Organa",
            "Tatooine", "Alderaan", "Hoth", "Dagobah", "Coruscant",
            "Millennium Falcon", "X-Wing", "TIE Fighter", "Snowspeeder"
        ]

    def _setup_nltk_resources(self):
        """Garante que os recursos existam sem travar a execução."""
        resources = ['punkt', 'punkt_tab', 'stopwords']
        for res in resources:
            try:
                nltk.download(res, download_dir=self.nltk_path, quiet=True)
            except Exception:
                pass

    def _fuzzy_correction(self, name: str) -> str:
        """Corrige erros de digitação usando difflib."""
        matches = get_close_matches(name, self.known_entities, n=1, cutoff=0.6)
        return matches[0] if matches else name

    def parse_sentence(self, text: str) -> dict:
        """
        Traduz linguagem natural para parâmetros de busca Star Wars.
        Resolve o bug de tipo inferindo a categoria pelo filtro ou entidade.
        """
        if not text:
            return {}


        tokens = word_tokenize(text.lower(), language='portuguese')
        palavras_limpas = [
            w for w in tokens 
            if (w.isalnum() or '-' in w) and w not in self.stop_words and w not in self.ruido_extra
        ]


        intent_to_type = {
            "films": "people",      # Quem participou de filmes? (Pessoa)
            "starships": "people",  # Quem pilotou naves? (Pessoa)
            "homeworld": "people",  # Qual planeta de origem de alguém? (Pessoa)
            "residents": "planets", # Quais residentes de um lugar? (Planeta)
            "population": "planets",# Quais habitantes de um lugar? (Planeta)
            "pilots": "starships",  # Quem são os pilotos desta nave? (Nave)
            "species": "people",     # Qual a espécie de alguém? (Pessoa)
            "vehicles": "people",    # Quem pilotou veículos? (Pessoa)
            
        }

       
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


        planetas = {"Tatooine", "Alderaan", "Hoth", "Dagobah", "Bespin", "Endor", "Naboo"}
        naves = {"Millennium Falcon", "X-Wing", "TIE Fighter", "Death Star", "Snowspeeder"}

        if corrected_name in planetas and not found_filter:
            inferred_type = "planets"
        elif corrected_name in naves:

            inferred_type = "starships" 

        corrected_name = corrected_name.replace("C-3Po", "C-3PO").replace("R2-D2", "R2-D2")

        return {
            "name": corrected_name,
            "filter": found_filter,
            "type": inferred_type,
            "original_query": text
        }