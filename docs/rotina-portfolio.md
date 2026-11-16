# Como investigar uma queda do portfólio

O projeto de referência é [jonaspessoa.github.io](https://github.com/jonaspessoa/jonaspessoa.github.io). Uma consulta HTTP à [página publicada](https://jonaspessoa.github.io/) retornou 200 em 16 de novembro de 2026. A queda mostrada no protótipo é fictícia.

## Percurso de referência

1. Abrir o endereço publicado para saber se está acessível naquele momento.
2. Abrir o repositório para conferir o deploy. O resultado de um deploy e a resposta atual do site são informações diferentes.
3. Registrar a investigação com o endereço do serviço e o horário da falha.
4. Consultar o serviço de novo depois da correção.

Uma verificação isolada responde como o site está agora. Para saber quando ele deixou de responder e quando voltou, o Nexus precisa guardar o histórico. A tarefa deve continuar ligada ao serviço mesmo depois que ele voltar.

## O que observar no próximo teste

Entregar o protótipo a um desenvolvedor com uma tarefa curta: descobrir quando o portfólio caiu e registrar o que precisa investigar. Observar onde procura primeiro, se encontra o horário e se entende que «A fazer» é o estado da tarefa. O resultado desse teste fica na [issue #3](https://github.com/jonaspessoa/nexus/issues/3).
