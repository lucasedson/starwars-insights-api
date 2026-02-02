import sys
import os

# Garante que a raiz do projeto esteja no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.controllers.nlp_controller import NLPController

def run_nlp_integration_test():
    nlp = NLPController()
    
    # Casos de teste focados em diferentes entidades e erros de digitação
    test_cases = [
        "Quais filmes Luke Skywalker participou?",
        "Qual o planeta de origem do C3PO?",
        "Quem mora em Tatoine?",
        "Me dê informações da nave Millenium Falcon",
        "Quais os residentes de Alderan?"
    ]
    
    print("\n" + "="*50)
    print("🚀 TESTE DE INTEGRAÇÃO: LINGUAGEM NATURAL -> QUERY")
    print("="*50 + "\n")
    
    for phrase in test_cases:
        # O 'parse_sentence' simula o que o Controller fará
        query_params = nlp.parse_sentence(phrase)
        
        print(f"💬 Entrada: '{phrase}'")
        print(f"🛠️  Query Gerada:")
        print(f"    - Nome:   {query_params['name']}")
        print(f"    - Filtro: {query_params['filter']}")
        print(f"    - Tipo:   {query_params['type']}")
        
        # Simulação da URL que seria montada internamente
        filter_str = f"&filter={query_params['filter']}" if query_params['filter'] else ""
        mock_url = f"/insights?name={query_params['name']}&type={query_params['type']}{filter_str}"
        print(f"🔗 URL Mock: {mock_url}")
        print("-" * 50)

if __name__ == "__main__":
    run_nlp_integration_test()