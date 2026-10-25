# Sprint 06 — PAPER contínuo com dados reais e execução interna

Revisão: 25/10/2026. **Estado: PLANEJADA; implementação e validação NÃO EXECUTADAS.** Este contrato atualiza o roadmap, sem autorizar execução antecipada. O detalhamento executável de interfaces/comandos depende da conclusão e revisão das Sprints anteriores.

## Objetivo, escopo e dependências

Acompanhar mercado real, simular ordens, saldos, reservas e posições, e ensaiar operação e recuperação.

Dependências: Sprint 05 aprovada, relatório fora da amostra revisado e configuração congelada.

Modo: PAPER; somente dados públicos reais; nenhuma ordem enviada à Binance.

Workspace exclusivo: `/home/cams7/Dev/Cripto`; aplicação Python em `cripto-bot`, documentação em `docs`. Mercado inicial: Spot, sem margem, alavancagem ou derivativos. Não modificar projetos LotoBot nem ativar produção.

## Entregáveis previstos

Modelo de execução ampliado e versionado em `adapters/execution`, coordenação/CLI, roteiro determinístico de falhas, outbox e clientes locais conforme seção 4.5, relatórios diários e runbook de pausa/retomada.

## Critérios objetivos de aceite

| ID | Condição verificável |
|---|---|
| AC01 | Observar ao menos 7 dias consecutivos, com ≥99% dos ciclos elegíveis; registrar numerador/denominador e manutenções pré-declaradas. |
| AC02 | Simular fill integral, múltiplos fills parciais, atraso configurado, ordem limitada sem fill e cancelamento do restante; tocar o preço não garante execução. |
| AC03 | Conferir quantidade cumulativa ≤ solicitada, taxas por fill, saldo livre/reservado e liberação somente da quantidade restante cancelada; zero divergência inexplicada. |
| AC04 | Simular timeout, reinício e repetição de evento; zero fill/ledger duplicado; kill switch bloqueia novas entradas sem liquidar automaticamente. |
| AC05 | Bloquear ordem por dados atrasados/lacunas, saldo insuficiente ou limite de risco; sem preço válido não fabricar fill. |
| AC06 | Guards rejeitam credenciais e toda mutação de negociação Binance, inclusive order/test; testes de execução não constroem cliente privado. |
| AC07 | Ensaiar falha/fallback de mensagens e recuperação da outbox sem repetir negociação, conforme seção 4.5. |
| AC08 | Testar isolamento e combinações declaradas, conflito de sinais, saldo concorrente, risco global/instância e desativação/reload com ordens/posições; flags não liberam negociação privada. |

## Evidência e decisão de transição

Todos os critérios e a revisão das evidências permitem a Sprint 07. Piloto AWS permanece condicionado ao pacote/contratos da 07 e aos pré-requisitos da 08; nenhum gate privado é dispensado.

Registrar versões, revisão do código, hash de configuração/modelo/dataset, intervalos UTC, execução dos casos, logs sanitizados, métricas, custos e decisão do revisor no [guia 06](../testes/sprint-06-validacao.md). Qualquer caso obrigatório não executado mantém o aceite pendente. Não inventar comandos ou resultados de implementação futura.

## Limitações, recuperação e custos

Dados de mercado são reais; carteira e execução são internas. Não mede fila, impacto próprio ou fills da corretora. Evidências de cenários injetados devem ser distinguidas da observação contínua.

Em falha, preservar evidências, interromper novos compromissos e reconciliar; não remover ledger ou alterar critério para obter aprovação. Em ambiente virtual, separar épocas de reset e configurações. Na etapa histórica/local, custo de disco/CPU/rede; nas etapas remotas, recotar infraestrutura/rede e dependências, sem pressupor gratuidade. Preparação LIVE não consome capital real.

Referências normativas: [planejamento, seções 6–10](../planejamento.md#10-gates-entre-ambientes-e-modos) e [roteiro comum de validação](../testes/validacao-pre-live.md). Esta revisão autoriza somente documentação.

## Contrato modular aplicável — revisão de 25/10/2026

Adotar a [arquitetura modular](../arquitetura-modular.md) e os casos aplicáveis do [guia modular](../testes/estrategias-modulares-validacao.md). Todos os módulos começam desabilitados; ensaios habilitam explicitamente somente instâncias implementadas por ambiente/modo/par. A elegibilidade é da versão/configuração/composição testada, sem exigir todo o catálogo. Esta atualização é documental, não implementa o schema nem altera evidências históricas.

## Documentação técnica como critério de conclusão

Se esta Sprint implementar ou alterar módulo, regra, interface/dependência/estado, dado/parâmetro/default/validação, flag/composição ou controle de risco, atualizar `docs/estrategias/<module_id>.md` e `docs/estrategias/README.md` na mesma entrega, conforme o [conteúdo obrigatório](../estrategias/README.md). Revisar exemplos, comandos, versões e evidências; separar efetivamente implementado de planejado/pendente. Registrar a decisão documental no guia desta Sprint; ausência/desatualização bloqueia conclusão. Se nenhum módulo for afetado, registrar essa conclusão e sua justificativa sem criar documento de módulo futuro.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.
