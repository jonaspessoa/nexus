# Backup e restauração

O PostgreSQL guarda projetos, tarefas, sessões, atividade do GitHub e histórico do Sentinel. Guarde o arquivo de backup em um local privado. Ele contém dados da instalação.

Com o banco em execução, gere um arquivo no formato do pg_restore e copie-o para o computador. Usar o arquivo dentro do contêiner evita redirecionar dados binários pelo terminal.

```sh
docker compose exec -T db pg_dump -U nexus -d nexus -Fc -f /tmp/nexus.dump
docker compose cp db:/tmp/nexus.dump ./nexus.dump
docker compose exec -T db rm /tmp/nexus.dump
```

Teste a recuperação em um banco separado:

```sh
docker compose cp ./nexus.dump db:/tmp/nexus.dump
docker compose exec -T db createdb -U nexus nexus_restore
docker compose exec -T db pg_restore --exit-on-error -U nexus -d nexus_restore /tmp/nexus.dump
docker compose exec -T db psql -U nexus -d nexus_restore -c 'SELECT * FROM alembic_version'
docker compose exec -T db psql -U nexus -d nexus_restore -c 'SELECT slug, name FROM projects'
```

Use um nome novo se `nexus_restore` já existir. Confira também algumas tarefas e verificações esperadas antes de usar o banco restaurado. A configuração do `.env` fica fora do dump. Para restaurar uma instalação, mantenha API e Sentinel parados até concluir a importação para o banco vazio da nova instalação.

Antes de atualizar, gere e verifique um backup. Depois de trocar para a versão desejada, rode `docker compose up --build -d`. A API aplica as migrações pendentes. Consulte `docker compose logs api` se o Workspace não iniciar.
