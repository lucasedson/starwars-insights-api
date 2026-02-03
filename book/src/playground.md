# 🚀 Playground Interativo

O Playground é um ambiente de exploração projetado para que desenvolvedores possam experimentar os recursos da **Star Wars Insights API** em tempo real. Aqui você pode testar consultas estruturadas e o motor de Processamento de Linguagem Natural (NLP).

> ### Nota sobre Autenticação
> Para utilizar autenticar-se no Playground é necessário que seja acessado em uma janela independente. Isso garante que o fluxo de autenticação via **Google OAuth2** ocorra com segurança e que o `id_token` seja capturado corretamente pelo seu navegador.

---

## Histórico de Consultas (Auditlog)

Ao realizar o login, a API ativa a persistência de atividades no **Google Cloud Firestore**. Esta funcionalidade permite um acompanhamento cronológico das interações:

* **Rastreabilidade:** Cada busca realizada por um usuário autenticado é registrada com seu respectivo **carimbo de data e hora (timestamp)**.
* **Monitoramento de Uso:** O histórico exibe exatamente o que foi consultado e quando, oferecendo uma visão clara da jornada de exploração de dados do usuário.
* **Persistência:** Os registros são vinculados à sua conta Google, permanecendo disponíveis em futuras sessões de uso.



---

## Como acessar

Você pode visualizar o Playground abaixo, mas para uma experiência completa com autenticação com conta Google e visualização do seu **Histórico de Buscas**, recomendamos o acesso externo:

* <a href="./html_extras/playground.html" target="_blank">Abrir o Playground em uma nova aba</a>


---

## Uso Rápido

<iframe src="./html_extras/playground.html" style="width: 100%; height: 600px; border: 2px solid #f0f0f0; border-radius: 8px;"></iframe>

---

## O que testar?

Para validar o processamento e o registro em log, sugerimos:

1.  **Linguagem Natural:** Pergunte *"Qual a altura do Darth Vader?"*.
2.  **Fuzzy Match:** Erre a grafia, ex: `Darth Vaderr`, e veja a API encontrar o resultado correto.
3.  **Verificação de Log:** Após realizar uma busca logado, observe a atualização do histórico no painel, confirmando o registro preciso do **momento da consulta**.

---