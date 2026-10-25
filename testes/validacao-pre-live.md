# Validação antes de Binance Spot real — roteiro comum

Data: 25/10/2026. **Estado: revisão documental concluída; validações futuras PENDENTES. LIVE bloqueado por padrão.** Este roteiro não autoriza código, autenticação, chamadas privadas ou ordens reais. Python permanece a linguagem principal; todos os módulos e documentos ficam em `/home/cams7/Dev/Cripto`.

## Sequência e rastreabilidade

| Etapa | Documento | Evidência mínima e objetivo |
|---|---|---|
| Base implementada | Sprints 01–03 e seus guias existentes | Evidências offline históricas; não equivalem a backtest ou PAPER contínuo |
| Base modular e tendência | [Sprint 04](../sprints/sprint-04.md) / [guia 04](sprint-04-validacao.md) | Contratos, flags desabilitadas por padrão, SMA opt-in, coordenação, risco e desativação |
| Backtest | [Sprint 05](../sprints/sprint-05.md) / [guia 05](sprint-05-validacao.md) | Dataset e split congelados, taxas/spread/slippage, fora da amostra, custos adversos, repetibilidade |
| PAPER local | [Sprint 06](../sprints/sprint-06.md) / [guia 06](sprint-06-validacao.md) | ≥7 dias, ≥99% dos ciclos elegíveis, zero divergências/duplicações; parcial, atraso e sem fill |
| SAM local antes da publicação | [Sprint 07](../sprints/sprint-07.md) / [guia 07](sprint-07-validacao.md) | Validação/lint, build em container e invocação local obrigatória; contratos e cenários de falha aprovados antes de publicar |
| PAPER AWS | Sprint 08 do [planejamento](../planejamento.md#9-roadmap-sequencial) | Gate SAM local aprovado, seguido de ≥30 dias, ≥99%, restauração, risco, custo e alarmes comprovados |
| Demo Spot | [Sprint 09](../sprints/sprint-09.md) / [guia 09](sprint-09-validacao.md) | Elegibilidade, order/test e ciclo virtual completo; ≥14 dias e ≥20 ciclos com os mínimos da especificação |
| Testnet complementar | [Sprint 10](../sprints/sprint-10.md) / [guia 10](sprint-10-validacao.md) | ≥10 ciclos com os mínimos da especificação, contratos/falhas e reset |
| Preparação LIVE | [Sprint 11](../sprints/sprint-11.md) / [guia 11](sprint-11-validacao.md) | Dossiê, risco real, barreiras negativas e aprovação; sem ativação |

Os números são mínimos de engenharia definidos pelo projeto, não requisitos da Binance nem prova estatística de vantagem econômica. Todos os critérios são cumulativos. A aprovação de uma etapa permite apenas o próximo planejamento/escopo autorizado, sem iniciar automaticamente código ou operações. A Sprint 04 continua sendo o próximo incremento de implementação.

## Registro obrigatório por execução

Registrar ID do ensaio, horário UTC inicial/final, responsável/revisor, commit/release, versões Python/dependências, hashes de configuração/estratégia/modelo/dataset, modo e host efetivo, identificação sanitizada de conta/ambiente/época, cenários, comandos reais e exit codes, logs/relatórios e custos. Nunca registrar chave, segredo, assinatura ou headers privados.

Cada linha da matriz deve indicar PLANEJADO, NÃO EXECUTADO, APROVADO ou REPROVADO e vincular evidência verificável. Marcar origem como fixture, falha injetada ou API observada. Ausência de conta, rede, ferramenta ou credencial de teste é pendência, sem aprovação presumida. Não executar mutações reais como requisito de CI.

## Matriz transversal de execução

| Cenário | Backtest/PAPER | Demo/Testnet | Condição de aprovação |
|---|---|---|---|
| BUY/SELL | Simulação causal com custos e carteira fictícia | Criação, consulta, fills/trades e saldos via API virtual | Quantidades, taxas e ledger conciliados por ativo |
| Parcial | Obrigatório no modelo da Sprint 06 | Observado quando possível, complementado por harness determinístico | Soma dos fills ≤ ordem, reserva só do restante, cancelamento sem desfazer fill |
| Atraso/sem fill | Cenários explícitos; ausência de cotação não fabrica fill | Ordem limitada aberta consultada e cancelada via API | Sem alteração indevida de posição e reserva liberada após confirmação |
| Timeout/reinício | Falhas antes/depois da persistência | Falha injetada antes/depois do efeito e consulta por identidade | Sem reenvio cego, duplicação ou UNKNOWN não resolvido |
| Rejeição/limites | Dados, saldo e risco inválidos | Parâmetros, assinatura/tempo, filtros/saldo, host/conta incompatíveis | Rejeição controlada, sem compromisso indevido |
| Reset | Dataset/carteira isolados, sem alteração silenciosa de contexto | Obrigatório no harness Testnet; documentar reset real se observado | Bloqueio, preservação do histórico e reconciliação em nova época |
| Interrupção | Kill switch/pausa persistentes | Guard antes do envio e recuperação sem liquidação automática | Sem nova entrada e sem perder ordens pendentes |

Fills BUY/SELL, consulta de ordens/saldos, ordem sem fill e cancelamento precisam ser demonstrados na API de cada ambiente virtual; fixtures não os substituem. Injeções cobrem cenários raros sem exigir provocar falhas ou auto-negociação no serviço externo.

## Condições de liberação real

O responsável deve aprovar previamente os limites reais e os critérios econômicos; valores didáticos PAPER não são herdados. Sem evidência suficiente fora da amostra ou com falha de qualquer gate, continuar em PAPER. Se Demo não estiver disponível para conta/região, registrar PENDENTE e manter LIVE bloqueado; Testnet e order/test não o substituem silenciosamente.

Antes de qualquer compra/venda real, exigir conjuntamente: validações concluídas/revisadas; risco monetário e operacional configurado; conta/permissões/rede e reconciliação inicial aprovadas; release/configuração identificadas; aprovação explícita válida com prazo e responsável; habilitação explícita. Ausência ou inconsistência de qualquer condição impede o executor real. Alteração material invalida a aprovação. Preparar a Sprint 11 não autoriza executar seu piloto futuro.

Resultados positivos em simulação não garantem rentabilidade real. Demo, Testnet e order/test validam aspectos diferentes e não substituem a avaliação econômica nem os controles de risco.

## Fontes e verificação realizada

Consultadas em 25/10/2026: [Demo Spot e comparação de ambientes](https://developers.binance.com/en/docs/products/spot/demo-mode/general-info), [Spot Testnet e resets](https://developers.binance.com/en/docs/products/spot/testnet/general-info) e [Test new order](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#test-new-order-trade).

Foi revisada apenas a documentação. Não foram consultadas conta/região do responsável nem executados testes de aplicação, serviços externos ou negociações. Evidências JSON das Sprints 01–03 permanecem históricas e não comprovam as validações futuras deste roteiro.

## Gate SAM local antes da publicação e das atualizações AWS

Conforme a [seção 8.1 do planejamento](../planejamento.md#81-validação-local-obrigatória-antes-de-publicar-na-aws), toda publicação ou atualização exige validação local SAM do build correspondente. Ferramentas auxiliares locais são utilizadas quando necessárias. Teste não executado mantém publicação bloqueada; teste local aprovado não comprova integração real AWS nem libera negociação real. A revisão de 25/10/2026 acrescentou apenas documentação, sem executar SAM ou publicar artefatos.

## Elegibilidade modular e combinações

A [matriz modular](estrategias-modulares-validacao.md) complementa cada gate. Validar o conjunto exato de módulos/instâncias/versões/flags/pares/pesos/algoritmo e a configuração de coordenação/desativação, com custos por estratégia e carteira reconciliados. A implementação de um módulo não exige todos os opcionais 12–21; o aceite do piloto simples não cobre futuras combinações. Novo módulo ou alteração material volta aos gates aplicáveis e invalida a aprovação afetada, sem habilitar LIVE automaticamente. Testes antigos não demonstram isolamento/combinações ainda não implementadas.

## Documentação técnica antes do aceite

Cada Sprint que implementar ou modificar um módulo exige seu documento em `docs/estrategias/<module_id>.md` e o [catálogo](../estrategias/README.md) atualizados e confrontados com código/schema/testes/artefato, conforme seção 4.7 do planejamento e M16 da matriz modular. Pendência documental bloqueia conclusão mesmo com código aprovado. Exemplos fictícios não são evidência de rentabilidade; aprovação documental não habilita módulos nem LIVE. Nesta revisão foram definidos o processo e o catálogo; os documentos individuais serão entregues junto da implementação de cada módulo.

## Documentação da persistência antes do aceite

Toda mudança de banco exige documento atualizado em `docs/bancos/` com diagrama/modelo, dicionário/DDL, versão, compatibilidade/migração ou rejeição, operação e evidências, conforme [checklist](../bancos/README.md). Conferir esquema em fixture e testes pertinentes; versão incompatível não pode ser resolvida apagando ledger ou alterando user_version manualmente. Ausência/desatualização bloqueia conclusão da Sprint. Sem impacto, registrar justificativa. Documentação não substitui teste de restauração/migração e não libera LIVE.
