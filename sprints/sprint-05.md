# Sprint 05 — Backtesting e avaliação fora da amostra

Revisão: 25/10/2026. **Estado: PLANEJADA; implementação e validação NÃO EXECUTADAS.** Este contrato atualiza o roadmap, sem autorizar execução antecipada. O detalhamento executável de interfaces/comandos depende da conclusão e revisão das Sprints anteriores.

## Objetivo, escopo e dependências

Simular compras e vendas históricas com carteira fictícia e produzir avaliação reproduzível, sem look-ahead.

Dependências: Sprint 04 implementada e revisada; ledger da 03 e coleta da 02 preservados.

Modo: PAPER histórico, sem rede de negociação ou credenciais.

Workspace exclusivo: `/home/cams7/Dev/Cripto`; aplicação Python em `cripto-bot`, documentação em `docs`. Mercado inicial: Spot, sem margem, alavancagem ou derivativos. Não modificar projetos LotoBot nem ativar produção.

## Entregáveis previstos

Dataset/manifesto com hashes, datas e origem; split cronológico 60/20/20; modelo de custos versionado; relatório em `reports/` com patrimônio, retorno líquido, drawdown, exposição, taxas, fills e benchmarks.

## Critérios objetivos de aceite

| ID | Condição verificável |
|---|---|
| AC01 | Congelar dataset, split, parâmetros e custos antes de abrir o teste final; registrar datas e uso separado do aquecimento. |
| AC02 | Decidir em t e executar somente após t; teste de prefixo prova que dados futuros não alteram sinais passados. |
| AC03 | Aplicar taxas, spread e slippage conforme seção 6.3; não cobrar spread duas vezes ao usar bid/ask; ledger fecha por ativo. |
| AC04 | Repetir a execução com hashes/versões iguais e obter resultados iguais; rejeitar lacunas ou dados inválidos. |
| AC05 | Reportar fora da amostra, caixa e buy-and-hold; custos dobrados, atraso de um candle e subperíodos/regimes. Documentar amostra pequena e limitações de filtros históricos. |
| AC06 | Rejeitar DEMO/TESTNET/LIVE e credenciais; testes com sockets bloqueados; nenhum POST/DELETE externo. |
| AC07 | Avaliar módulo isolado e composição explicitamente permitida com flags opt-in; mesmo dataset/janela/capital/custos, métricas por instância e consolidado reconciliadas, sem duplicar capital nem usar dados futuros. |

## Evidência e decisão de transição

Todos os critérios aprovados e relatório revisado permitem planejar PAPER contínuo; retorno negativo não impede aprender sem capital. Não liberar LIVE por lucro histórico. Mudança após olhar o teste exige novo conjunto final intocado.

Registrar versões, revisão do código, hash de configuração/modelo/dataset, intervalos UTC, execução dos casos, logs sanitizados, métricas, custos e decisão do revisor no [guia 05](../testes/sprint-05-validacao.md). Qualquer caso obrigatório não executado mantém o aceite pendente. Não inventar comandos ou resultados de implementação futura.

## Limitações, recuperação e custos

A execução depende das hipóteses de liquidez e fill. O resultado não comprova rentabilidade futura. Fill integral do modelo da Sprint 03 é simplificação a identificar; a Sprint 06 deve cobrir parcial, atraso e ausência de fill.

Em falha, preservar evidências, interromper novos compromissos e reconciliar; não remover ledger ou alterar critério para obter aprovação. Em ambiente virtual, separar épocas de reset e configurações. Na etapa histórica/local, custo de disco/CPU/rede; nas etapas remotas, recotar infraestrutura/rede e dependências, sem pressupor gratuidade. Preparação LIVE não consome capital real.

Referências normativas: [planejamento, seções 6–10](../planejamento.md#10-gates-entre-ambientes-e-modos) e [roteiro comum de validação](../testes/validacao-pre-live.md). Esta revisão autoriza somente documentação.

## Contrato modular aplicável — revisão de 25/10/2026

Adotar a [arquitetura modular](../arquitetura-modular.md) e os casos aplicáveis do [guia modular](../testes/estrategias-modulares-validacao.md). Todos os módulos começam desabilitados; ensaios habilitam explicitamente somente instâncias implementadas por ambiente/modo/par. A elegibilidade é da versão/configuração/composição testada, sem exigir todo o catálogo. Esta atualização é documental, não implementa o schema nem altera evidências históricas.

## Documentação técnica como critério de conclusão

Se esta Sprint implementar ou alterar módulo, regra, interface/dependência/estado, dado/parâmetro/default/validação, flag/composição ou controle de risco, atualizar `docs/estrategias/<module_id>.md` e `docs/estrategias/README.md` na mesma entrega, conforme o [conteúdo obrigatório](../estrategias/README.md). Revisar exemplos, comandos, versões e evidências; separar efetivamente implementado de planejado/pendente. Registrar a decisão documental no guia desta Sprint; ausência/desatualização bloqueia conclusão. Se nenhum módulo for afetado, registrar essa conclusão e sua justificativa sem criar documento de módulo futuro.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.
