# Catálogo e documentação técnica dos módulos

Atualizado em 25/10/2026. Documentação em `/home/cams7/Dev/Cripto/docs/estrategias/`; implementação Python em `/home/cams7/Dev/Cripto/cripto-bot`. Público: desenvolvedor com boa experiência DevOps e conhecimentos básicos de criptomoedas. Explicar siglas, unidades, estados, causalidade e efeitos operacionais usando exemplos do projeto.

## Estado do catálogo

A Sprint 04 entregou a base modular e trend_sma em fixture offline; a 05 acrescenta o caminho histórico, com resultados e limites no [guia 05](../testes/sprint-05-validacao.md); os demais módulos abaixo continuam planejados, sem implementação/validação. A base e o simulador sintético das Sprints 01–03 não constituem implementação dessas estratégias. Todos permanecem desabilitados por padrão; implementação, documentação e elegibilidade operacional são estados distintos. Nenhum documento ou flag autoriza negociação real.

| ID | Categoria | Sprint prevista | Arquivo a criar na implementação | Implementação / documentação individual | Elegibilidade |
|---|---|---|---|---|---|
| trend_sma | Estratégia: tendência | 04 | [trend_sma.md](trend_sma.md) | Versão 1 implementada / documentada | Fixture validada no guia 04; caminho histórico local/PAPER/BTCUSDT/15m validado na 05, conforme guia 05; default desabilitado; contínuo/privado inelegíveis |
| mean_reversion | Estratégia: reversão à média | 12 | `mean_reversion.md` | Planejada / pendente | Não validada; desabilitada |
| breakout | Estratégia: rompimento | 13 | `breakout.md` | Planejada / pendente | Não validada; desabilitada |
| dca | Gestão de carteira: compras periódicas | 14A | `dca.md` | Planejada / pendente | Não validada; desabilitada |
| rebalance | Gestão de carteira: rebalanceamento | 14B | `rebalance.md` | Planejada / pendente | Não validada; desabilitada |
| relative_momentum | Seleção e gestão de carteira | 14C | `relative_momentum.md` | Planejada / pendente | Não validada; desabilitada |
| twap | Algoritmo de execução por tempo | 15A | `twap.md` | Planejada / pendente | Não validada; desabilitada |
| vwap | Algoritmo de execução por volume | 15B | `vwap.md` | Planejada / pendente | Não validada; desabilitada |
| grid | Estratégia: escada de ordens | 16 | `grid.md` | Planejada / pendente | Não validada; desabilitada |
| arbitrage | Estratégia: arbitragem triangular Spot | 17 | `arbitrage.md` | Planejada / pendente | Não validada; desabilitada |
| market_making | Estratégia: cotações e inventário | 18 | `market_making.md` | Planejada / pendente | Não validada; desabilitada |
| pairs | Estratégia: rotação de inventários Spot | 19 | `pairs.md` | Planejada / pendente | Não validada; desabilitada |
| news_sentiment | Fonte de sinais: notícias/sentimento | 20 | `news_sentiment.md` | Planejada / pendente | Não validada; desabilitada |
| ml_signal | Fonte de sinais/modelo: aprendizado de máquina | 21 | `ml_signal.md` | Planejada / pendente | Não validada; desabilitada |

Não criar antecipadamente documentos individuais, rascunhos detalhados ou placeholders de módulos ainda não implementados; sua descrição e previsão permanecem no planejamento. Este README contém apenas catálogo de estado e orientações gerais. Arquivos individuais são criados na Sprint que entregar o módulo, um Markdown por ID, sem duplicar por par, instância ou ambiente. Até lá, os nomes acima são destinos previstos, não links para documentação existente. Quando criado, substituir o nome por link e atualizar estado, versão da implementação, revisão da documentação e evidências de elegibilidade por modo/ambiente/par, sem presumir que “implementado” significa “habilitado em LIVE”. Implementação parcial deve listar exatamente o que falta. Descontinuação mantém documento/histórico, sem apagar evidência.

Referências atuais: [planejamento](../planejamento.md), [contratos e catálogo técnico](../arquitetura-modular.md), [Sprint 04](../sprints/sprint-04.md), [Sprints opcionais](../sprints/estrategias-opcionais.md) e [guia modular](../testes/estrategias-modulares-validacao.md).

## Conteúdo obrigatório por módulo

Cada arquivo deve cobrir os tópicos abaixo, com caminhos e nomes efetivos do projeto. Separar visivelmente **implementado**, **planejado**, **pendente** e **não suportado**. Não apresentar regra proposta como comportamento existente ou teste planejado como aprovado. “Não se aplica” exige explicar o limite do papel e apontar o componente responsável.

1. **Identificação, objetivo e conceitos.** ID, categoria, estado, versão/schema/revisão do código e data da revisão; finalidade, lógica e conceitos financeiros indispensáveis. Explicar como participa do projeto, sem presumir conhecimentos avançados de trading.
2. **Condições de mercado e inatividade.** Regimes pretendidos e adversos; dados insuficientes/vencidos, janela de aquecimento, liquidez e indisponibilidade que geram HOLD, bloqueio ou pausa; comportamento em condições não observadas.
3. **Regras efetivamente implementadas.** Critérios de entrada, saída, manutenção e não operação, fronteiras/igualdades e ordem de avaliação. Para fonte de sinais, documentar emissão/validade e consumidor; para execução, admissão do pai, geração/cancelamento de filhos e término; para carteira, calendário/pesos e caixa necessário.
4. **Dados e parâmetros.** Fonte/endpoints e disponibilidade temporal, indicadores/features, periodicidade, unidades e precisão; tabela de cada parâmetro com nome exato, tipo, default efetivo, faixa/validação e erro. Informar parâmetros obrigatórios sem default e valores ainda não definidos. Explicar uso de dados ausentes, warm-up e causalidade.
5. **Integração e estado.** Paths reais de módulos/interfaces/testes, entradas e saídas do contrato, dependências, persistência/schema/migrações e fluxo dados → sinais/alvos → coordenação → risco → execução/ledger. Indicar proprietário de reservas e o que acontece em falha/reinício.
6. **Feature flags e configuração.** Exemplo desabilitado por padrão e exemplos opt-in isolado e conjunto somente para schemas/combinações realmente suportados. Incluir ambiente, modo, par, instância, pesos, algoritmo, geração/hash e política de desativação. Não antecipar exemplos detalhados de funcionalidades ainda não implementadas; registrar a limitação e remeter a evolução prevista ao planejamento. Não inventar CLI ou TOML aceito. Quando não houver combinação implementada, registrar essa limitação e a rejeição esperada.
7. **Coordenação e risco.** Orçamento, propriedade de saldo/inventário, conflitos/ordens duplicadas, limites globais/por módulo/par e dependência do risco central. Documentar estados de pausa/desativação, ordens abertas/parciais/UNKNOWN e posições remanescentes, sem liquidação ou transferência automática.
8. **Exemplo prático fictício.** Percorrer dados, sinal ou plano, risco, reserva, execução/fills e estado final, com unidades e taxas/spread/slippage explícitos e consistentes com o modelo implementado. Mostrar desfechos positivo e negativo, além de não operar quando relevante; separar ganho/perda do custo. Se o módulo não negocia, mostrar sua saída e o consumidor responsável: uma fonte não recebe PnL de ordem própria e TWAP/VWAP não são apresentados como sinais de entrada. Valores didáticos não são resultado observado nem parâmetro real da conta.
9. **Testes e avaliação.** Pré-requisitos, versões, comandos reais reproduzíveis desde a raiz da aplicação, fixtures/dataset/modelo/hash, saídas esperadas versus obtidas, métricas específicas e comparáveis, critérios de aceite e links a guias/evidências. Distinguir fake/injeção/API e não executado/reprovado/aprovado. Medir custos/drawdown e consolidado quando aplicáveis, com mesma janela/capital; não alegar validade estatística sem evidência.
10. **Limitações e operação segura.** Premissas, riscos, regimes não cobertos, inventário financiado em Binance Spot, restrições de short/margem/derivativos/outras corretoras; diferenças entre backtest, PAPER, Demo, Testnet e produção. Resultados simulados não garantem rentabilidade. Flags não autorizam LIVE nem dispensam validação SAM antes de publicação AWS.
11. **Referências e histórico incremental.** Links para código/testes/configuração/guia realmente existentes, commit/release/versão de implementação e hashes relevantes; fontes oficiais utilizadas e data da consulta. Registrar em tabela cada alteração de regra/interface/parâmetro/flag/risco, Sprint, revisão e evidência atualizada, indicando evidências/aprovações invalidadas.

## Adaptação ao papel do módulo

| Papel | Ênfase do documento | Limite a deixar explícito |
|---|---|---|
| Estratégia de negociação | Sinal/alvo/plano, regime, entrada/saída e inventário | Não acessa corretora nem contorna risco; SELL somente com inventário permitido |
| Gestão de carteira | Calendário, pesos/ranking, fluxos de capital e rebalanceamento | Não cria dinheiro, não usa caixa não confirmado, não duplica ordem do consumidor |
| Fonte de sinal/modelo | Origem point-in-time, disponibilidade, score/validade/qualidade, treino/drift e consumidor | Não emite ordem própria; contribuição à carteira depende do consumidor e da avaliação conjunta |
| Algoritmo de execução | Ordem pai aprovada, tempo/volume, filhos/restante, deadline e benchmark | Não escolhe tese de compra/venda; risco por filho e reservas/limites do pai permanecem obrigatórios |

## Critério de conclusão e manutenção

O documento individual e este catálogo devem ser criados/atualizados **na mesma Sprint que implementa ou modifica o módulo**, antes do aceite. Mudança em regra, interface/dependência/estado, dados/parâmetro/default/validação, flag/composição, coordenação ou risco exige revisão do documento, exemplos, catálogo e evidências afetadas. Mudança de comportamento não pode encerrar Sprint com documentação antiga ou pendência documental adiada.

Na revisão, confrontar texto e exemplos com schemas, código, testes e artefato/versionamento efetivos. Verificar links, contas do exemplo, defaults desabilitados, comandos reproduzíveis e estado das evidências. Registrar documentação APROVADA ou PENDENTE no guia da Sprint; pendência documental bloqueia sua conclusão, sem reescrever resultados históricos. Não criar documentos individuais dos demais módulos opcionais antes de sua implementação.

A projeção [DuckDB + Parquet](../bancos/backtest-analytics.md) acrescentada após a Sprint 05 afeta somente a exportação histórica de `trend_sma`. Não muda algoritmo, configuração, versão, elegibilidade ou risco da estratégia. A validação da alteração está no [guia complementar](../testes/duckdb-parquet-validacao.md); resultados históricos originais permanecem preservados.


Revisão 06A (26/10/2026): `trend_sma` passa a ser fornecida pelo core com fachada de compatibilidade no bot, sem mudança de versão da estratégia/regras/flags ou autorização de continuous. A composição instalada e sua identidade são verificadas separadamente no [guia 06A](../testes/sprint-06a-validacao.md); bibliotecas não recebem documentos fictícios de estratégia.
