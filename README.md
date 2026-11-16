# Nexus

Quero abrir uma tela de manhã e saber se algum dos meus projetos precisa de atenção. Se um site estiver fora do ar, quero conseguir registrar o que preciso investigar sem perder a referência ao serviço.

## Primeiro cenário

1. Abro o Nexus e vejo que o site do meu portfólio está indisponível.
2. Abro o detalhe e vejo quando a falha foi detectada.
3. Crio uma tarefa de investigação vinculada ao site.
4. Volto à lista e encontro a tarefa que acabei de criar.

O primeiro rascunho vai usar uma falha fictícia. Quero conferir se consigo percorrer essas quatro ações e entender a diferença entre o estado do site e o andamento da tarefa.

## Roadmap

O [roadmap](ROADMAP.md) detalha a ordem das entregas, os critérios de conclusão e as releases do Nexus.

## Protótipo local

Abra `prototype/index.html` no navegador. Em **Serviços**, selecione **Ver histórico** e crie uma tarefa a partir da falha fictícia do portfólio. Confira se ela aparece em **Tarefas** com o vínculo ao serviço. As tarefas existem durante a sessão da página.

## Aplicação local

Com Docker Compose instalado, copie `.env.example` para `.env` e troque a senha do banco. Defina também NEXUS_OPERATOR_PASSWORD com pelo menos 16 caracteres para entrar no Workspace. Por enquanto, use letras, números e hífens na senha porque ela também faz parte da URL de conexão.

```sh
docker compose up --build -d
docker compose exec api python seed.py
```

Abra http://127.0.0.1:3000 para conferir a conexão da interface com a API. A API aplica a migração ao iniciar. O comando de carga pode ser repetido e mantém um único projeto de exemplo. Para parar a aplicação e preservar os dados, rode `docker compose down`.
