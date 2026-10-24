Atue como arquiteto de software sênior, engenheiro DevOps especializado em AWS e desenvolvedor Python de sistemas automatizados de negociação de criptomoedas.

## 1. Contexto e referências

Planeje o desenvolvimento incremental de um robô de negociação de criptomoedas na Binance, utilizando os seguintes projetos como referência:

- `/home/cams7/Dev/LotoBot/mail-sender-aws`
- `/home/cams7/Dev/LotoBot/gmail-reader-aws`
- `/home/cams7/Dev/LotoBot/whatsapp-notify`
- `/home/cams7/Dev/LotoBot/loto-bot`
- `/home/cams7/Dev/LotoBot/loto-scheduler-aws`
- `/home/cams7/Dev/LotoBot/loto-infra-terraform`

Antes de propor a arquitetura, analise a organização dos repositórios, as tecnologias, a infraestrutura, as integrações, o agendamento, a observabilidade e os processos de implantação existentes.

Identifique padrões e componentes reutilizáveis. Considere esses projetos como referências arquiteturais e operacionais, sem exigir a reprodução de tecnologias incompatíveis com Python.

Os projetos de referência deverão ser apenas consultados. Não altere seus arquivos sem solicitação explícita.

Caso não tenha acesso aos diretórios, informe a limitação e solicite os arquivos necessários, sem presumir seu conteúdo.

O desenvolvedor possui bons conhecimentos de DevOps e conhecimentos básicos de negociação de criptomoedas. Explique os conceitos financeiros necessários de forma objetiva, relacionando-os às decisões de implementação.

## 2. Diretório raiz obrigatório

Todos os módulos, códigos, testes, configurações, scripts, arquivos de infraestrutura e documentos produzidos para este projeto deverão ser criados dentro de:

`/home/cams7/Dev/Cripto`

Considere esse caminho como a raiz do projeto e como diretório de trabalho para os comandos documentados.

Organize os componentes em subdiretórios dessa raiz. Mesmo que sejam adotados múltiplos módulos ou repositórios, todos deverão permanecer dentro de `/home/cams7/Dev/Cripto`.

Antes de criar arquivos, verifique o conteúdo existente. Preserve trabalhos anteriores e não sobrescreva arquivos sem analisar seu conteúdo e a necessidade da alteração.

A estrutura definitiva deverá ser proposta no planejamento. Utilize inicialmente a seguinte referência:

- `README.md`: apresentação e instruções gerais.
- `docs/planejamento.md`: planejamento e roadmap.
- `docs/arquitetura.md`: arquitetura e fluxos.
- `docs/decisoes/`: registros de decisões arquiteturais.
- `docs/sprints/`: especificações e prompts de execução.
- `docs/testes/`: guias e evidências de validação.
- `modules/`: módulos da aplicação.
- `infra/`: infraestrutura como código.
- `scripts/`: automação de desenvolvimento e operação.
- `tests/`: testes compartilhados ou de integração.

Todos esses caminhos são relativos a `/home/cams7/Dev/Cripto`. Crie os diretórios somente quando necessários à etapa em execução.

## 3. Objetivo e escopo

Construir um sistema modular em Python, executado na AWS, capaz de coletar dados de mercado, avaliar estratégias, gerenciar risco e, futuramente, executar compras e vendas na Binance.

O objetivo é buscar resultados consistentes ajustados ao risco, considerando taxas, spread, slippage e limitações operacionais. Não prometa rentabilidade nem considere resultados históricos uma garantia de desempenho futuro.

O escopo inicial será exclusivamente Binance Spot, sem margem, empréstimos ou alavancagem.

A avaliação de derivativos deverá constar apenas como possibilidade futura no roadmap, condicionada à maturidade operacional, à análise específica de riscos e à aprovação explícita do responsável. Não implemente componentes de derivativos antecipadamente.

## 4. Linguagem e ferramentas

Utilize Python como linguagem principal.

Selecione uma versão estável e compatível com o ambiente de execução escolhido na AWS. Justifique as ferramentas de gerenciamento de dependências, empacotamento, testes, análise estática e formatação.

Priorize:

- Tipagem explícita e validação nas fronteiras do sistema.
- Precisão decimal para preços, quantidades, taxas e saldos.
- Dependências necessárias e com manutenção adequada.
- Ambiente local reproduzível em Linux.
- Separação entre regras de negócio e integrações externas.
- Configuração externa ao código e ausência de segredos no repositório.

Não adote frameworks web ou processamento assíncrono sem necessidade concreta.

## 5. Evolução operacional

O sistema deverá começar obrigatoriamente no modo `PAPER`:

- Saldos, posições, taxas e execuções simulados.
- Nenhum envio de ordens reais à corretora.
- Dados de mercado reais ou históricos, conforme a etapa.
- Premissas de execução explícitas, configuráveis e documentadas.
- Bloqueios técnicos que impeçam o envio acidental de ordens reais.

Planeje a evolução gradual:

1. Estrutura básica e execução local.
2. Coleta, validação e persistência de dados.
3. Carteira e execução simuladas.
4. Estratégia inicial simples, explicável e testável.
5. Backtesting e avaliação fora da amostra.
6. Operação `PAPER` contínua com monitoramento.
7. Integração com ambiente de testes da Binance, quando disponível e compatível.
8. Operação real em Spot com capital e exposição limitados.

Diferencie backtesting, `PAPER`, ambiente de testes da corretora e operação real.

A mudança de modo deverá exigir configuração explícita e validação dos pré-requisitos. A ativação da operação real dependerá de critérios previamente definidos, evidências de validação e aprovação explícita do responsável.

## 6. Arquitetura

Proponha uma arquitetura modular, separando:

- Integração com a Binance e coleta de dados.
- Estratégias e geração de sinais.
- Gestão de risco.
- Execução simulada e execução real.
- Carteira, posições e reconciliação.
- Persistência, auditoria e relatórios.
- Notificações e observabilidade.
- Infraestrutura e implantação.

Evite fragmentação prematura em microsserviços. Justifique a organização dos módulos conforme as necessidades de cada fase.

Utilize interfaces que permitam compartilhar regras de estratégia e risco entre backtesting, `PAPER` e operação real, preservando as diferenças de execução.

Avalie os serviços AWS conforme frequência das operações, duração dos processos, necessidade de conexões persistentes, disponibilidade e custo. Não presuma que todos os componentes devem executar em AWS Lambda.

Priorize testes locais em Linux com AWS SAM, containers e outras ferramentas quando adequados. Explique as limitações da emulação local e quais testes exigem recursos reais da AWS.

Utilize Terraform quando compatível com os projetos de referência. Caso combine Terraform e SAM, delimite suas responsabilidades e evite gerenciamento duplicado de recursos.

## 7. Segurança e confiabilidade

Inclua requisitos para:

- Isolamento entre desenvolvimento, simulação e produção.
- Armazenamento seguro de credenciais e permissões mínimas.
- Chaves de negociação sem permissão de saque.
- Idempotência e prevenção de ordens duplicadas.
- Tratamento de timeouts, falhas parciais e limites da API.
- Reconciliação antes de repetir ordens com resultado desconhecido.
- Validação de precisão, quantidade mínima e demais filtros da corretora.
- Recuperação de estado após reinicializações.
- Logs estruturados, métricas, alertas e trilha de auditoria.
- Bloqueio diante de dados desatualizados ou inconsistentes.
- Limites de exposição, tamanho de posição, perdas e drawdown.
- Interrupção de emergência e procedimento de recuperação.

Diferencie limites controlados pelo sistema de resultados que não podem ser garantidos durante falhas ou movimentos bruscos de mercado.

Consulte a documentação oficial vigente antes de definir APIs, bibliotecas, serviços e restrições. Registre fontes e decisões relevantes.

## 8. Estratégias e avaliação

Comece com uma estratégia simples, cujas regras possam ser compreendidas e verificadas pelo desenvolvedor.

Defina uma metodologia de avaliação que considere:

- Taxas, spread e slippage.
- Qualidade e disponibilidade dos dados.
- Separação temporal entre desenvolvimento e validação.
- Prevenção de uso de informações futuras no backtesting.
- Risco de sobreajuste.
- Retorno líquido, drawdown, exposição e número de operações.
- Comparação com referências adequadas ao período analisado.

Não introduza inteligência artificial, aprendizado de máquina ou otimização complexa sem justificativa e sem uma base de comparação previamente validada.

## 9. Desenvolvimento por Sprints

Organize o projeto em Sprints pequenas, sequenciais e verificáveis. Cada Sprint deverá produzir um incremento funcional e depender de entregáveis efetivamente concluídos nas anteriores.

Para cada Sprint, especifique:

- Objetivo, escopo e exclusões.
- Dependências e pré-requisitos.
- Entregáveis e caminhos dos arquivos afetados.
- Tarefas de implementação.
- Critérios de aceite objetivos.
- Testes necessários e evidências esperadas.
- Riscos, limitações e recuperação.
- Custos envolvidos, quando aplicável.
- Prompt completo para execução da Sprint.

Cada prompt de execução deverá ser autossuficiente e informar explicitamente:

- A raiz obrigatória `/home/cams7/Dev/Cripto`.
- Os documentos e módulos que precisam ser consultados.
- As dependências das Sprints anteriores.
- O modo operacional permitido.
- Os entregáveis, testes e critérios de conclusão.

Oriente o agente a analisar o estado atual do projeto, verificar os pré-requisitos, implementar somente o escopo definido, executar os testes e atualizar a documentação.

Caso uma dependência esteja incompleta, registre o impedimento antes de iniciar o trabalho dependente.

## 10. Documentação e validação

Escreva toda a documentação em português e Markdown, dentro de `/home/cams7/Dev/Cripto/docs`.

Utilize os seguintes padrões:

- `docs/planejamento.md`
- `docs/arquitetura.md`
- `docs/decisoes/`
- `docs/sprints/sprint-XX.md`
- `docs/testes/sprint-XX-validacao.md`

O planejamento deverá conter visão do produto, arquitetura proposta, roadmap, dependências, riscos, estimativas de custos AWS e prompts para detalhar e revisar as próximas Sprints.

Após implementar cada Sprint, produza um guia de validação contendo:

- Preparação do ambiente e pré-requisitos.
- Comandos reproduzíveis, com indicação do diretório de execução.
- Configurações e dados de teste sem segredos.
- Resultados esperados e critérios de aprovação.
- Cenários de falha e diagnóstico.
- Limpeza dos recursos e possíveis custos.
- Registro do que foi testado e do que permanece pendente.

Não apresente testes não executados como aprovados.

## 11. Primeira entrega

Nesta primeira etapa, produza somente:

`/home/cams7/Dev/Cripto/docs/planejamento.md`

Crie apenas os diretórios necessários para salvar esse documento. Não implemente código, não provisione infraestrutura e não envie ordens.

O documento deverá apresentar:

1. Análise dos projetos de referência e oportunidades de reutilização.
2. Requisitos funcionais e não funcionais.
3. Arquitetura inicial em Python e justificativas.
4. Estrutura de diretórios dentro da raiz obrigatória.
5. Fluxos de dados e limites dos módulos.
6. Estratégia de desenvolvimento e testes locais.
7. Roadmap de Sprints e suas dependências.
8. Critérios de evolução entre os modos operacionais.
9. Riscos, premissas e estimativas de custos.
10. Primeira Sprint detalhada, incluindo seu prompt de execução.
11. Prompts para detalhar e revisar as Sprints seguintes.

Mantenha as Sprints futuras em nível suficiente para orientar o roadmap. Seu detalhamento deverá considerar os resultados reais das etapas anteriores.

Faça perguntas interativas apenas sobre decisões pendentes que alterem significativamente a arquitetura ou o risco e que não possam ser inferidas dos repositórios. Para decisões secundárias, registre uma premissa justificada.

Considere como decisões já estabelecidas:

- Python como linguagem principal.
- Desenvolvimento local em Linux.
- Implantação na AWS.
- Modo inicial `PAPER`.
- Mercado inicial Spot.
- Avaliação de derivativos somente em fases futuras.
- Todos os módulos e documentos dentro de `/home/cams7/Dev/Cripto`.

