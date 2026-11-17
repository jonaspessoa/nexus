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

## Demonstração

Abra a [demo pública](https://jonaspessoa.github.io/nexus/) ou o arquivo `prototype/index.html` no navegador. Em **Serviços**, selecione **Ver histórico** e crie uma tarefa a partir da falha fictícia do portfólio. Confira se ela aparece em **Tarefas** com o vínculo ao serviço. Depois de salvar, selecione **Simular recuperação** no histórico. A tarefa permanece na lista neste navegador mesmo após recarregar. Use **Reiniciar demonstração** para voltar à queda inicial.

## Aplicação local

Com Docker Compose instalado, copie `.env.example` para `.env` e troque a senha do banco. Defina também NEXUS_OPERATOR_PASSWORD com pelo menos 16 caracteres para entrar no Workspace. Por enquanto, use letras, números e hífens na senha porque ela também faz parte da URL de conexão.

```sh
docker compose up --build -d
docker compose exec api python seed.py
```

Abra http://127.0.0.1:3000 para conferir a conexão da interface com a API. A API aplica a migração ao iniciar. O comando de carga pode ser repetido e mantém um único projeto de exemplo. Para parar a aplicação e preservar os dados, rode `docker compose down`.

## Atividade do GitHub

Defina `NEXUS_GITHUB_REPOSITORY=usuario/repositorio` no arquivo `.env` e rode `docker compose up -d` para aplicar a configuração. No Workspace, selecione **Sincronizar** para consultar os 30 itens atualizados mais recentemente. A consulta funciona para repositórios públicos, sem token. O horário indica a última atualização bem-sucedida.

## Monitoramento com Sentinel

Depois da carga de exemplo, o Sentinel verifica o site do portfólio. A primeira leitura pode levar até cinco minutos. Abra **Histórico de verificações** no Workspace para ver o código HTTP, a latência e as transições entre queda e recuperação. Use **Investigar** para registrar uma tarefa ligada ao serviço.

O worker faz requisições HEAD às portas padrão de HTTP e HTTPS. Endereços locais e privados são bloqueados. Redirecionamentos são registrados pelo código retornado, sem uma segunda requisição. Alguns serviços não dão suporte a HEAD e podem aparecer como indisponíveis mesmo quando aceitam GET.

Para alterar a frequência, defina `NEXUS_CHECK_INTERVAL_SECONDS` no `.env` (mínimo de 30 segundos) e rode `docker compose up -d`. A página indica atraso quando o último resultado tem mais de dois intervalos. Para investigar um worker parado, use `docker compose logs sentinel`.

Veja também [backup e restauração](docs/backup.md).
