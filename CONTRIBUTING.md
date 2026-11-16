# Contribuir com o Nexus

Para começar, suba a aplicação seguindo o [README](README.md) e carregue o projeto de exemplo. Se você encontrar um problema, abra uma issue com os passos, o resultado esperado e o que apareceu. Em problemas do Sentinel, inclua o código HTTP e o horário da verificação. Use dados fictícios nas capturas e retire senhas, cookies e URLs privadas dos logs.

## Antes de abrir um PR

1. Rode `python -m unittest api.test_devhub api.test_sentinel` na raiz.
2. Com a aplicação local em execução e o projeto de exemplo carregado, rode `npm ci` e `npx playwright install chromium` em `web/`.
3. Defina no terminal a mesma `NEXUS_OPERATOR_PASSWORD` usada no Compose e execute `npx playwright test`. O teste de GitHub também precisa de `NEXUS_GITHUB_REPOSITORY`. O cenário de recuperação usa o servidor HTTP de teste da CI e exige um banco descartável.
4. Descreva no PR como reproduzir a mudança e quais verificações você executou. Para alterações de tela, uma captura do estado afetado ajuda na revisão.

Alterações no esquema ganham uma nova revisão em `api/migrations/versions/`. A aplicação roda as migrações pendentes ao iniciar.
