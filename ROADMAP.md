# Roadmap do Nexus

A primeira instalação é pessoal, em Docker Compose. A demo pública usa dados fictícios. O cenário de referência é detectar que meu portfólio caiu, abrir uma tarefa e voltar ao histórico para confirmar a recuperação após o deploy.

Trabalho em etapas pequenas. Cada issue descreve uma tarefa de usuário e o comportamento esperado. Cada PR fecha uma parte demonstrável. Ao terminar uma etapa, registro o teste que rodei, o que observei e o que precisa mudar no backlog.

## 01. Definir o problema — concluída

**Entrega.** README com o problema e o primeiro percurso.

**Conclui quando.** Consigo explicar quem usa a ferramenta, em que momento e qual tarefa ela resolve. O README atual cobre esse ponto.

## 02. Entender a rotina

**Trabalho.** Escolher um projeto próprio com repositório e site. Anotar como verifico o deploy, descubro uma falha e acompanho uma correção. Pedir a outro desenvolvedor que descreva como faz o mesmo.

**Entrega.** Uma nota curta com exemplos observados e um backlog separado em v0.1, v0.2 e v1.0.

**Conclui quando.** Cada item da v0.1 ajuda na primeira jornada. As dúvidas sobre status, origem do alerta e vínculo com a tarefa estão anotadas.

## 03. Desenhar e testar o percurso

**Trabalho.** Rascunhar dashboard, detalhe do serviço, formulário da tarefa e quadro. Em seguida, montar um protótipo clicável. Incluir estados de carregamento, erro, lista vazia e serviço sem verificação recente. Testar no celular e no desktop.

**Entrega.** Protótipo com o portfólio fictício e uma rodada de revisão.

**Conclui quando.** Outro dev encontra a falha, identifica quando ocorreu e cria uma tarefa sem instruções. Registro o que confundiu a pessoa e ajusto o desenho.

## 04. Montar a base local

**Trabalho.** Criar web com Next.js e TypeScript e API com FastAPI. Adicionar PostgreSQL, migrações, Docker Compose, configuração de exemplo e carga de dados fictícios. Registrar a divisão dos módulos em uma decisão de arquitetura. Configurar CI para lint, testes e build.

**Entrega.** Um ambiente local com uma página inicial que consulta a API.

**Conclui quando.** A partir de um clone limpo, consigo subir a aplicação, aplicar migrações, carregar os dados de demo e executar as verificações.

## 05. Entregar Workspace e Projects

**Trabalho.** Implementar login de operador, lista de projetos, quadro de tarefas e dashboard. Tarefas têm título, situação e vínculo opcional ao serviço. O dashboard deve separar a situação do serviço da situação da tarefa.

**Entrega.** Primeira jornada navegável com dados de demo e tarefas persistidas.

**Conclui quando.** O operador cria uma tarefa a partir de um alerta fictício, muda sua situação e recupera o vínculo após recarregar. A API exige sessão para leitura e edição dos dados do operador.

## 06. Integrar DevHub

**Trabalho.** Conectar repositórios selecionados com permissão de leitura. Sincronizar PRs e issues e exibir a última atualização. Tratar integração desconectada, lista vazia, limite de requisições e falha temporária. Manter credenciais no servidor e protegê-las em repouso.

**Entrega.** Lista de atividade do GitHub com links para os itens originais e vínculo de PR em uma tarefa.

**Conclui quando.** Um repositório próprio sincroniza. Repetir a execução não duplica registros. Se a sincronização falhar, os dados anteriores continuam visíveis com a data da última atualização.

## 07. Ativar Sentinel

**Trabalho.** Agendar verificações HTTP de serviços próprios. Registrar resultado, horário e latência. Mostrar histórico, queda, recuperação e verificação atrasada. Aplicar timeout, limites de resposta e proteção contra SSRF, inclusive ao seguir redirecionamentos.

**Entrega.** Painel e detalhe de serviço com verificações agendadas e atalho para abrir tarefa.

**Conclui quando.** Um serviço controlado passa por falha e recuperação. O histórico mostra as transições, e a tarefa mantém o vínculo mesmo após a recuperação. Testes defensivos verificam que destinos internos são bloqueados no modo público.

## 08. Validar e lançar v0.1.0

**Trabalho.** Usar a instalação pessoal em um projeto próprio por uma semana. Rodar testes de API e da jornada no Playwright. Revisar teclado, foco e estados de erro. Documentar instalação, backup, atualização, contribuição e deploy. Escolher a licença após revisar as dependências.

**Entrega.** Release pública, demo com dados fictícios, licença, README, CONTRIBUTING, changelog, CI e decisões arquiteturais.

**Conclui quando.** Uma pessoa instala pelo README e outra reproduz na demo a jornada de falha, tarefa e recuperação. A release registra as limitações encontradas durante o piloto.

## 09. Entregar Automations e incidentes na v0.2

**Trabalho.** Separar o worker da API. Adicionar fila com Redis e Celery para tarefas agendadas e eventos. Começar com ações predefinidas, como criar tarefa após indisponibilidade confirmada e avisar quando o serviço voltar. Agrupar falhas consecutivas no mesmo incidente. Adicionar webhooks autenticados e atualização do painel em tempo real.

**Entrega.** Fluxos com histórico de execução, tentativas, falhas e trilha de auditoria.

**Conclui quando.** Uma queda abre um incidente e cria uma tarefa. A repetição do mesmo evento não duplica a tarefa. Uma falha de execução fica visível e pode ser reprocessada. A recuperação encerra o incidente e atualiza o painel.

## 10. Ampliar o Workspace rumo à v1.0

**Trabalho.** Melhorar Projects com backlog, prioridades, sprints e milestones. Adicionar widgets configuráveis ao Workspace. Validar o módulo Personal com uma rotina semanal de estudos e lembretes. Avaliar calendário, hábitos e metas financeiras a partir do uso da primeira rotina.

**Entrega.** Workspace configurável, quadro com planejamento de entregas e primeiro fluxo pessoal opcional.

**Conclui quando.** Consigo planejar uma semana, relacionar uma tarefa a um milestone e montar a tela inicial com os widgets que uso. Uma instalação com o módulo pessoal desativado continua funcionando.

## 11. Publicar a v1.0 extensível

**Trabalho.** Documentar a interface de extensão e implementar um plugin de exemplo com permissões explícitas. Validar atualização das versões publicadas, restauração do PostgreSQL e instalação com módulos opcionais. Documentar métricas, logs e diagnóstico. Preparar o estudo de caso.

**Entrega.** Release v1.0 com guia de instalação Docker, documentação para contribuidores, plugin de referência e uma demo atualizada.

**Conclui quando.** Uma pessoa consegue instalar, atualizar e restaurar a aplicação seguindo a documentação. Outra consegue ativar o plugin de exemplo e entender quais dados ele acessa. O estudo de caso mostra uma alteração de interface observada no teste de uso e uma decisão técnica com verificação reproduzível.

A v1.0 mantém a instalação pessoal. SaaS multiusuário exigiria um plano próprio de autorização, isolamento entre contas e operação.
