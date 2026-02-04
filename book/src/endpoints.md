# 🛰️ Documentação da API (Endpoints)

A **Star Wars Insights API** oferece uma interface híbrida e resiliente, permitindo consultas via parâmetros estruturados ou processamento de linguagem natural (NLP).

URL no API Gateway: [https://sw-gateway-aaqxefvm.ue.gateway.dev/](https://sw-gateway-aaqxefvm.ue.gateway.dev/)

---

## 1. Motor de Busca e Insights (Principal)
Este é o orquestrador inteligente que integra o motor de NLP, correção fonética (Fuzzy Match) e a hidratação de dados em tempo real.

* **URL:** `/`
* **Método:** `GET`
* **Autenticação:** Opcional (Usuários autenticados têm suas buscas registradas no histórico).

### Parâmetros de Query
| Parâmetro | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `q` | `string` | Não* | Pergunta em linguagem natural (Ex: "Qual a altura do Yoda?"). |
| `name` | `string` | Não* | Nome da entidade (Ex: "R2-D2"). |
| `type` | `string` | Não* | Categoria: `people`, `films`, `planets`, `starships`, `vehicles`, `species`. |
| `filter` | `string` | Não | Filtra campos específicos na resposta (Ex: `name,climate`). |

> \* **Nota:** Utilize o parâmetro `q` para perguntas livres ou a combinação `name` + `type` para buscas estruturadas.

### Exemplos de Resposta

#### A. Linguagem Natural com Correção (Fuzzy Match)
**Request:** `GET`
<a href="https://sw-gateway-aaqxefvm.ue.gateway.dev/?q=Quais filmes o Luke Skiwalke atuou?" target="_blank">?q="Quais filmes o Luke Skiwalke atuou?"</a>

*(Note o erro proposital no nome)*

```json
{
  "status": "success",
  "entity": "Luke Skywalker",
  "category": "people",
  "insight_value": {
    "films": ["A New Hope", "The Empire Strikes Back", "Return of the Jedi", "Revenge of the Sith"]
  },
  "source": "firestore",
  "suggestion": "Luke Skywalker"
}
```

#### B. Parâmetros Estruturados
**Request:** GET 
<a  href="https://sw-gateway-aaqxefvm.ue.gateway.dev/?name=Yoda&type=people&filter=films" target="_blank">?name=Yoda&type=people&filter=films</a>

```JSON

{
  "status": "success",
  "entity": "Yoda",
  "category": "people",
  "insight_value": {
    "films": ["The Empire Strikes Back", "Return of the Jedi", "The Phantom Menace", "Attack of the Clones", "Revenge of the Sith"]
  },
  "source": "firestore",
  "suggestion": null
}

```

## 2. Autenticação e Perfil
Endpoints responsáveis pelo ciclo de vida do usuário e integração com Google OAuth2.

**Login & Callback** URL: `/login` e `/callback`

Descrição: Inicia o fluxo de autorização e processa o código retornado pelo Google para gerar o id_token.

**Perfil do Usuário** URL: `/me`

Método: `GET`

Headers: `Authorization: Bearer <id_token>`

Descrição: `Retorna os dados do perfil autenticado (Nome, E-mail, Foto).`

## 3. Gestão de Dados e Histórico
Recursos para auditoria de consultas e descoberta de entidades.

**Histórico de Consultas** URL: `/history`

Método: `GET` 

Autenticação: `Obrigatória`

Descrição: `Retorna o log cronológico de todas as buscas realizadas pelo usuário.`

Exemplo de Resposta:

```JSON

[
  {
    "query": "?q=Qual a altura do Darth Vader?",
    "timestamp": "2026-02-03T14:30:05.123Z"
  },
  {
    "query": "?name=Darth Vader&type=people&filter=height",
    "timestamp": "2026-02-03T14:35:10.000Z",
  }
]
```
## 4. Metadados
**Metadados (Entidades Conhecidas)** URL: `/metadata`

Método: GET

Descrição: Lista todas as entidades (personagens, planetas, etc.) atualmente indexadas no cache do sistema. Útil para alimentar componentes de autocomplete. Além disso é onde é configurado os intents para o motor de NLP.