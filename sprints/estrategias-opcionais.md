# Sprints opcionais 12–21 — catálogo modular

Revisão: 25/10/2026. **Estado: PLANEJADAS; implementação, testes e ativação NÃO EXECUTADOS.** Cada seção é um incremento opcional selecionável, a detalhar quando suas dependências reais estiverem aprovadas. Os números ordenam complexidade sugerida, não criam uma cadeia obrigatória.

Workspace `/home/cams7/Dev/Cripto`, Python como linguagem principal, Binance Spot sem margem/empréstimos/alavancagem. Reutilizar contratos da [arquitetura modular](../arquitetura-modular.md), sem copiar risco, ledger, indicadores, avaliação ou transporte. Todos os módulos e combinações começam desabilitados. Nenhuma etapa exige concluir todos os outros módulos opcionais.

## Dependências e entregáveis comuns

Implementação isolada requer base modular 04 e infraestrutura de avaliação/execução PAPER 05–06 revisadas. Capacidades novas (multiativo, OMS de grupo, fontes de livro, estado de pai/filho) podem ser incrementos pequenos separados dentro da Sprint escolhida, com teste contratual antes do consumidor. Compartilhar essas capacidades não obriga implementar a estratégia que também as utiliza.

Entregar descriptor/schema, módulo Python, configuração de exemplo desabilitada, estado versionado, testes independentes, compatibilidades declaradas, evidências por ID/versão/configuração e `docs/estrategias/<module_id>.md` com atualização do catálogo na mesma Sprint, conforme [conteúdo obrigatório](../estrategias/README.md). Documentação ausente/desatualizada bloqueia conclusão. Não criar pacotes vazios ou instalar bibliotecas de módulos não escolhidos. A linguagem de contratos define alvos, planos e features; cada tipo usa apenas o consumidor adequado. Falta de uma capacidade mantém apenas o módulo dependente inelegível.

Para ativar isoladamente em simulação, exigir todos os casos obrigatórios do módulo e da matriz comum aprovados, zero bypass de risco, duplicação, saldo negativo ou divergência inexplicada; avaliação causal fora da amostra com custos e relatório revisado. Para combinar, validar dependências/manifesto, orçamento, propriedade e a combinação exata no teste conjunto. Para promover modo, repetir os gates 05–11 aplicáveis à nova versão/composição, com habilitação explícita separada por ambiente/modo/par. Aprovação LIVE antiga não cobre módulo novo. Antes de publicação AWS, gate SAM local obrigatório; LIVE permanece bloqueado.

## Sprint 12 — Reversão à média

- Módulo: `mean_reversion`. Documento a criar e revisar nesta Sprint: `docs/estrategias/mean_reversion.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06 e estatísticas causais; independente de breakout.
- Aceite específico obrigatório: Z-score em fronteiras, variância zero, regime persistente adverso e expiração; zero venda sem inventário.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `mean_reversion`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 13 — Rompimento — breakout

- Módulo: `breakout`. Documento a criar e revisar nesta Sprint: `docs/estrategias/breakout.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06 e janelas/volatilidade; independente de reversão.
- Aceite específico obrigatório: Faixa calculada sem candle futuro, confirmação/expiração e falso rompimento com custos; queda só reduz posição possuída.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `breakout`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 14A — DCA

- Módulo: `dca`. Documento a criar e revisar nesta Sprint: `docs/estrategias/dca.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06, calendário e orçamento por período.
- Aceite específico obrigatório: Disparo único por janela, reinício/atraso sem compra acumulada implícita, caixa insuficiente rejeitado; comparação com mesmos fluxos.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `dca`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 14B — Rebalanceamento

- Módulo: `rebalance`. Documento a criar e revisar nesta Sprint: `docs/estrategias/rebalance.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06 e capacidade multiativo/subledger; independente de DCA.
- Aceite específico obrigatório: Pesos não negativos/soma ≤1, bandas e mínimos de ordem; sequência de venda/compra não usa saldo ainda não confirmado.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `rebalance`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 14C — Momentum relativo

- Módulo: `relative_momentum`. Documento a criar e revisar nesta Sprint: `docs/estrategias/relative_momentum.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06, universo histórico e subledger multiativo; independente de 14B.
- Aceite específico obrigatório: Ranking determinístico com empates, ativo deslistado, dados ausentes e universo point-in-time; caixa quando nenhum ativo elegível.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `relative_momentum`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 15A — TWAP

- Módulo: `twap`. Documento a criar e revisar nesta Sprint: `docs/estrategias/twap.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06, OMS pai/filho, relógio/reservas; independente de VWAP.
- Aceite específico obrigatório: Divisão temporal, fill parcial, deadline, cancelamento e reinício; soma de filhos/fills não supera pai nem reserva.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `twap`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 15B — VWAP

- Módulo: `vwap`. Documento a criar e revisar nesta Sprint: `docs/estrategias/vwap.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06, OMS pai/filho e perfil causal de volume; independente de TWAP.
- Aceite específico obrigatório: Volume zero/ausente, participação máxima e deadline; sem uso de volume futuro, benchmark e shortfall reproduzíveis.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `vwap`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 16 — Grid Trading

- Módulo: `grid`. Documento a criar e revisar nesta Sprint: `docs/estrategias/grid.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06 e capacidade OMS multiordem/inventário; não exige implementar market making.
- Aceite específico obrigatório: Níveis e arredondamentos sem ordens duplicadas, reservas agregadas, reancoragem, parcial e cancelamento com saída da faixa.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `grid`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 17 — Arbitragem triangular Spot

- Módulo: `arbitrage`. Documento a criar e revisar nesta Sprint: `docs/estrategias/arbitrage.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06, multiativo, cotações sincronizadas, profundidade e OMS de grupo.
- Aceite específico obrigatório: Edge após custos de todas as pernas, rejeição de cotação velha, falha/parcial em uma perna e plano limitado de exposição residual; nenhum lucro garantido por cálculo teórico.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `arbitrage`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 18 — Market making Spot financiado

- Módulo: `market_making`. Documento a criar e revisar nesta Sprint: `docs/estrategias/market_making.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06, livro/latência e OMS multiordem; feed/runtime reavaliados.
- Aceite específico obrigatório: Inventário em ambos os lados, prevenção de ordens próprias opostas, STP conforme suporte, cancelamento atrasado, desconexão e adverse selection; benchmark de latência antes de habilitar.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `market_making`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 19 — Pairs trading com inventário Spot

- Módulo: `pairs`. Documento a criar e revisar nesta Sprint: `docs/estrategias/pairs.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06, séries multiativo, estatística point-in-time e OMS de grupo.
- Aceite específico obrigatório: Estabilidade fora da amostra, correlação espúria/regime, falha de perna e limites residuais; rejeitar necessidade de short, sem declarar neutralidade da rotação Spot.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `pairs`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 20 — Notícias e sentimento

- Módulo: `news_sentiment`. Documento a criar e revisar nesta Sprint: `docs/estrategias/news_sentiment.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06, adapter de dados licenciado e consumidor explicitamente implementado.
- Aceite específico obrigatório: Publicação versus recebimento, atraso, duplicata, fonte ausente e texto malicioso; nenhum comando/ordem originado do texto, score expirado bloqueia consumidor.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `news_sentiment`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Sprint 21 — Sinais com aprendizado de máquina

- Módulo: `ml_signal`. Documento a criar e revisar nesta Sprint: `docs/estrategias/ml_signal.md`, com atualização de `docs/estrategias/README.md`. Contrato específico, parâmetros, estado, métricas e compatibilidade Spot: linha correspondente do [catálogo](../arquitetura-modular.md#catálogo-contratos-específicos-e-compatibilidade-spot).
- Dependências de implementação: 04–06, features/treino/versionamento e consumidor implementado; notícias não obrigatórias.
- Aceite específico obrigatório: Split temporal/embargo quando rótulos se sobrepõem, transformações ajustadas só no treino, vazamento, drift, modelo ausente/incompatível e inferência reproduzível; treino não altera modelo ativo implicitamente.
- Aceite transversal: habilitar/desabilitar isoladamente, risco central, rastreabilidade, reinício e comparação de custos conforme [guia modular](../testes/estrategias-modulares-validacao.md); registrar resultado específico pelo ID `ml_signal`.
- Restrições: variantes que exijam short, derivativos, margem, outras corretoras ou empréstimos permanecem futuras, com nova análise/decisão. Nenhuma dependência fora do Spot é ativada implicitamente.

## Recuperação, estimativas e autorização

Falha pausa o módulo e seus dependentes; falha financeira compartilhada bloqueia a carteira afetada. Preservar estado/ledger e seguir ciclo DRAINING da arquitetura. Não liquidar posição automaticamente. Capacidade de feed/latência não comprovada impede ativar grid/market making/arbitragem na cadência existente. Estimar cada capacidade após seleção, incluindo armazenamento, dados/licenças, compute e rede; sem custo fixo presumido nem prazo obrigatório para módulo opcional.

Estes documentos não são prompts de implementação nem autorização de operação. A escolha/detalhamento de um módulo não promove seu modo nem muda defaults. Critérios econômicos e de risco são fixados antes da avaliação final; ajustar estratégia após olhar teste exige nova evidência intocada.

## Impacto em bancos nos incrementos opcionais

Cada incremento escolhido que alterar estrutura/formato persistido/versão de estado, reservas, subledger multiativo, OMS pai/filho ou outbox deve atualizar o documento do banco em `docs/bancos/` e o [catálogo](../bancos/README.md) na própria Sprint, conforme seção 4.8 do planejamento. Incluir diagrama/modelo e dicionário efetivos, constraints/índices, compatibilidade/migração/recuperação e evidências. Atualização documental é critério de conclusão; não criar antecipadamente schemas para módulos ausentes.
