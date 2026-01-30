# Solução: Star Wars Insights API

## Visão Geral
O Star Wars Insights API pretende ser uma solução inteligente, escalável e de alto desempenho para transformar a forma como exploramos o universo de Star Wars. Ela tem como objetivo de ser mais do que um simples espelho do SWAPI (Star Wars API), este projeto funciona como uma camada de valor que processa, limpa e correlaciona dados brutos para entregar respostas prontas para o consumo.

Por exemplo, se quiser relacionar dados de um personagem com um filme, a API pode fornecer uma correlação entre eles junto com Insights.

## Busca Híbrida
A API elimina a barreira técnica entre o fã da saga e a informação, oferecendo dois caminhos:

### Query Estruturada
Aceita filtros tradicionais para buscar dados de personagens, filmes, planetas e naves. Ideal para integrações de sistemas e Dashboards.
### Linguagem Natural
Através do processamento de texto, o usuário pode fazer perguntas diretas como: "Quais filmes o Darth Vader atuou." ou "Quem pilota a nave X-wing?" A API entende as perguntas e busca os dados correspondentes.

## Sinergia com PowerOfData
...

## Stack Tecnológica
- Python: 3.11+:
  - Pydantic: Para modelagem de dados
  - Pytest: Para testes unitários
  - NLTK: Para processamento de texto natural

- Google Cloud Platform (GCP):
  - Cloud Functions (Gen2): Escolhida pela suporte a concorrência e execução assíncrona (asyncio), essencial para resolver correlações de dados rapidamente.
  - API Gateway: Para criação de APIs RESTful
  - Cloud Storage: Utilizado para implementar um cache de alta disponibilidade e baixo custo, garantindo que a API respeite o rate limit da SWAPI e reduza a latência para o usuário final.
