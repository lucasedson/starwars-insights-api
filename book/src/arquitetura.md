# Arquitetura de Software (C4 Model)

Esta seção detalha a estrutura técnica da **Star Wars Insights API**, utilizando a metodologia **C4 Model** para fornecer uma visão clara desde o contexto de negócio até os componentes internos de execução.

## Diagrama Interativo

O diagrama abaixo é multinível. Ele permite visualizar a orquestração entre os serviços do **GCP (Cloud Functions, Firestore e API Gateway)** e a integração com provedores externos como **Google Auth** e **SWAPI**.

<a href="./html_extras/arch.html" target="_blank">Abrir o Diagrama em uma nova aba</a>

<iframe src="./html_extras/arch.html" style="width: 100%; height: 700px; border: 2px solid #f0f0f0; border-radius: 8px;"></iframe>

### Manual de Navegação
* **Visualização de Detalhes:** Clique em um **Nó (Node)** para expandir sua descrição técnica e tecnologias envolvidas.
* **Navegação de Nível:** Caso o componente possua subníveis (como o `Star Wars Insights Platform`), clique para entrar no contexto de containers e componentes.
* **Relacionamentos:** As setas indicam o fluxo de dados entre os nós.

---

## Decisões de Arquitetura

A escolha dessa estrutura foi pautada em três pilares fundamentais:

1.  **Escalabilidade Serverless:** A arquitetura baseada em **Cloud Functions** garante que a API suporte picos de tráfego sem a necessidade de gerenciamento de infraestrutura. Em conjunto com o API Gateway, ela oferece escalabilidade e flexibilidade para atender aos requisitos de escala da API.
2.  **Resiliência com Cache-Aside:** O uso do **Firestore** como camada de persistência e cache garante que a aplicação continue funcional e rápida mesmo em momentos de instabilidade na API de origem (SWAPI).
3.  **Autenticação e Autorização:** O uso de **Google Auth** garantem a autenticação e autorização de usuários, permitindo o acesso aos recursos da API.