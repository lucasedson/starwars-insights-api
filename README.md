# Star Wars Insigth API.

Este é um projeto de API para o processo seletivo da empresa [Power of Data](https://www.powerofdata.ai/) para a vaga de Desenvolvedor Backend Junior.

Veja a [DOCUMENTAÇÃO COMPLETA](https://lucasedson.github.io/starwars-insights-api) para saber mais.



## Requisitos minimos para executar a API:

- Python 3.11+
- [Google Cloud Functions](https://cloud.google.com/functions)
- [Google Cloud Firestore](https://cloud.google.com/firestore)


## Requisitos recomendados para colocar em produção:

- [Google API Gateway](https://cloud.google.com/api-gateway)

## Baixando e instalando o projeto:

```bash
git clone https://github.com/lucasedson/starwars-insights-api.git
pip install -r requirements.txt # uv install -r requirements.txt
```

## Configurando as variáveis de ambiente:

Crie um arquivo .env na raiz do projeto com as seguintes variáveis:

```bash
GCP_PROJECT_ID= # Project ID do GCP
GCP_REGION= # Região do GCP

GOOGLE_CLIENT_ID= # Client ID do GCP
GOOGLE_CLIENT_SECRET= # Client Secret do GCP
REDIRECT_URI= # URI de redirecionamento

FRONTEND_SHORT_URL= # URL curta do frontend
FRONTEND_URL= # URL do frontend
FUNCTION_URL= # URL da função
API_GATEWAY_URL= # URL do API Gateway


E2E_TESTS=true # true ou false - Habilita ou desabilita os testes E2E
```

## Executando a API:

```bash
python dev.py # uv run dev.py
```
