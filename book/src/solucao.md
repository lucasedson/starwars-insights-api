# Solução: Star Wars Insights API

## Visão Geral
A Star Wars Insights API é uma solução de engenharia de dados inteligente, escalável e de alto desempenho, projetada para transformar a exploração do universo Star Wars.

Diferente de um simples proxy ou espelhamento da SWAPI, este projeto atua como uma camada de inteligência. Ela processa, higieniza e correlaciona dados brutos para entregar insights prontos para o consumo, eliminando a necessidade de múltiplas requisições e tratamentos manuais no lado do cliente.

## Busca Híbrida
A API elimina a barreira técnica entre o fã da saga e a informação, oferecendo dois caminhos:

### Query Estruturada
Focada em precisão e performance, esta modalidade aceita filtros técnicos tradicionais para buscar dados de personagens, filmes, planetas e naves.

Ideal para: Dashboards de Business Intelligence, integrações B2B e sistemas que exigem alta previsibilidade de resposta.

### Linguagem Natural
Utilizando o motor NLTK, a API permite que o usuário interaja com o ecossistema Star Wars de forma intuitiva. Através de tokenização e análise de intenção, é possível fazer perguntas diretas:

- "Quais filmes o Darth Vader atuou?"
- "Qual a altura do Yoda?"
- "Qual o diretor do filme 'A New Hope'?"
  
Ideal para: Chatbots e interfaces de usuários.


----

## Stack Tecnológica
- Python: 3.11+:
  - Pydantic: Para modelagem de dados
  - Pytest: Para testes unitários
  - NLTK: Para processamento de texto natural
  - Requests: Para consumo de APIs externas
  - Diff: Para comparação de textos

- Google Cloud Platform (GCP):
  - Cloud Functions (Gen2): Essencial para resolver correlações de dados rapidamente.
  - API Gateway: Para criação de APIs RESTful
  - Cloud Firestore: Utilizado para implementar um cache persistente, metadata e historico de pesquisa de usuarios autenticados.
  - Google Auth: Para autenticação e autorização de usuários.

- Git: Para controle de versões
- GitHub: Para hospedar o repositório.
- GitHub Actions: Para construção e entrega contínua dessa documentação.
- MdBook: Para construção e entrega contínua dessa documentação.
- VSCode: IDE de desenvolvimento.
