# Considerações Finais

Este projeto foi desenvolvido com foco na entrega de resultados práticos, alinhando-se à mentalidade de produtividade e eficiência da **PowerOfData**. A solução não busca apenas refletir dados brutos, mas transformá-los em informações úteis de forma rápida, simples e resiliente.

Durante o desenvolvimento, priorizei pilares que considero fundamentais para uma arquitetura de **Backend** robusta em um ecossistema focado em dados:

---

### Engenharia de Backend & Qualidade
Como base da solução, priorizei o uso de **Modelagem de Dados com Pydantic** e **Tipagem Estrita**, garantindo que a comunicação entre a API e as fontes de dados seja íntegra e à prova de falhas. A arquitetura foi desenhada para ser modular, facilitando a manutenção e a extensibilidade do código.

### Transformação em Valor (Data Insights)
Implementei uma camada de **Hidratação de Dados** que automatiza a conversão de referências técnicas (URLs) em informações prontas para o consumo. Isso reduz a carga cognitiva do usuário e o esforço de engenharia na ponta final, acelerando a entrega da informação.

### Performance e Escalabilidade (API Hub)
Optei por uma arquitetura *serverless* integrada ao **Google Cloud Firestore** para garantir alta disponibilidade. O sistema de cache e o uso de processamento paralelo via **Multi-threading** foram projetados para sustentar acessos em escala, mantendo a baixa latência exigida por soluções corporativas.

### Processamento de Linguagem Natural (NLTK)
A utilização da biblioteca **NLTK** permitiu decompor a linguagem humana em componentes processáveis. Através de *tokenização* e filtragem de ruídos (*stopwords*), a API isola intenções e entidades com precisão, aproximando a experiência de uso de ferramentas modernas de busca.

### Inteligência Acessível (NLP & UX)
A combinação do NLTK com algoritmos de **Fuzzy Match** reflete a busca por interfaces amigáveis. O objetivo é remover barreiras técnicas, permitindo que a descoberta de dados seja intuitiva e resiliente a erros de digitação, independentemente do perfil do usuário.


---

Repositorio: [https://github.com/lucasedson/star-wars-insights-api](https://github.com/lucasedson/star-wars-insights-api)


Tempo de desenvolvimento:
<a href="https://wakatime.com/@d8e2eed9-84de-4eac-abd2-69f82c10f1e1/projects/phmcbhslwe?start=2026-01-27&end=2026-02-02"><img src="https://wakatime.com/badge/user/d8e2eed9-84de-4eac-abd2-69f82c10f1e1/project/a6563dfc-3433-491a-afcf-8f821876456d.svg" alt="wakatime"></a>