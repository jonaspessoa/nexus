# Interface e API na instalação local

A interface roda em Next.js e consulta uma API FastAPI pela rede interna do Compose. Só a porta da interface fica disponível no computador. A API concentra as operações do Nexus, e o PostgreSQL preserva os dados quando os contêineres são recriados.

Essa divisão permite desenvolver a interface e os serviços Python no mesmo repositório. Em troca, o ambiente tem três processos desde o início. Para diagnosticar a inicialização, a página distingue uma API conectada de uma API indisponível.

A primeira migração cria a tabela de projetos. A carga do portfólio é um comando separado, porque a instalação pessoal começa vazia. A carga usa um identificador fixo e pode ser repetida.
