# Sprint 06 — Consolidação da validação 06A–06D

Revisão: 26/10/2026. **Estado: PARCIAL — 06A–06C aprovadas; software 06D validado offline; piloto e aceite global pendentes.** D-M1–D-M3 concluídos no recorte offline; D-M4 não executado e D-M5 pendente. Esta revisão corrige a consolidação documental, sem nova execução de testes ou operações.

Referências atuais: [agregador 06](../sprints/sprint-06.md), [especificação 06D](../sprints/sprint-06d.md), [guia 06D](sprint-06d-validacao.md), [evidências](sprint-06d-evidencias.json), [relatório](relatorios/sprint-06d/report.html), [API](../api/continuous.md), [runbook](../operacao/continuous-runbook.md) e [pré-protocolo não armado](sprint-06d-pre-protocolo.json). Os registros de consolidação ao final preservam os estados históricos; suas antigas indicações de “próxima ação” não substituem o estado atual.

## Software validado e operação restante

As especificações, guias, comandos e artefatos de 06A–06D já existem. A implementação offline da 06D registra 642 testes na confirmação completa, 108 casos sobrepostos na revisão final, 30 testes de analytics e 31 comandos por wheels. Esses números são resultados da execução documentada, não testes reexecutados por esta atualização editorial. Core/dados, modelos anteriores, 16 artefatos e registro final foram preservados conforme o guia.

O modo permanece PAPER/Spot/BTCUSDT/15m, sem alavancagem ou ordens privadas. Até agora foram usados dados sintéticos e transports/senders simulados para validar o software. Dados públicos reais e entregas efetivas pertencem a D-M4, após autorização/configuração específicas; flags técnicas não concedem essa autorização.

## Matriz consolidada AC01–AC08

A coluna offline registra provas já obtidas; a coluna operacional registra a evidência ainda ausente. Nenhuma linha aprova o piloto globalmente antes de D-M4/D-M5. Critérios D01–D22 e casos detalhados estão no [guia 06D](sprint-06d-validacao.md).

| Critério | Resultado offline documentado | Operação/fechamento ainda pendente |
|---|---|---|
| AC01 — duração e disponibilidade | Calendário, prazo e denominador fixo testados; ensaio acelerado não comprova duração real (D04/D17) | Sete dias UTC completos, 672 slots e ≥666 válidos no prazo; sem excluir downtime, manutenção ou falhas |
| AC02 — execução simulada | Integral, múltiplos parciais, atraso, LIMIT sem fill e cancelamento validados em drills (D05/D06) | Revisão integrada dos drills e da observação; não forçar trades para obter cobertura |
| AC03 — integridade financeira | Cumulativos, taxas, custo, saldos, reservas e partidas conciliados nos oráculos (D03/D05/D07) | Reconciliação da carteira do piloto durante a janela e no encerramento |
| AC04 — recuperação e controles | Crash, duplicação, conflitos/CAS, UNKNOWN e controles persistentes validados offline (D08/D09) | Evidência de retomadas/controles aplicáveis no ambiente operacional e revisão final |
| AC05 — dados e risco | Freshness, lacunas, relógio/deadline, saldo, filtros e limites testados por fixtures/mocks (D04/D07/D11) | Preflight elegível e qualidade dos dados públicos na janela real; regras incompatíveis mantêm o piloto bloqueado |
| AC06 — guards | Rejeições de credenciais/mutações privadas, opt-ins e bloqueio de sockets validados no software (D02/D11/D15) | Evidência do uso somente das leituras públicas autorizadas durante D-M4 |
| AC07 — entrega | Contratos, falhas, fallback, lease/retry/UNKNOWN e não repetição financeira validados por fakes (D12/D13) | Entrega efetiva autorizada dos canais habilitados, e-mail mínimo e revisão dos resultados (D14) |
| AC08 — módulos e custódia | Flags, owner exclusivo, composição inválida, orçamento, reload/desativação e preservação de posição validados offline (D07/D09/D10) | Conferência da configuração congelada e da custódia/controles durante o piloto |

AC09–AC13 permanecem cumpridos pelas extrações 06A–06C. AC14–AC17 têm verificações de composição, integridade e documentação no alcance das entregas, incluindo os artefatos offline da 06D; mudanças posteriores exigem revisão proporcional. AC18 e o aceite integrado continuam pendentes.

## Próxima ação e condições de encerramento

1. Revisar artefatos, configuração, supervisão, orçamento de recursos e backups usando o pré-protocolo/runbook existentes. Não criar nova etapa ou repetir extrações já aprovadas.
2. Obter instrução explícita para dados públicos e serviços/destinatários de teste; confirmar a disponibilidade dos serviços. Não copiar contatos ou configurar um monitor externo como se já estivesse autorizado.
3. Executar preflight e entrega autorizados, verificar elegibilidade/filtros/clock/dados e congelar a composição e T0/Tend antes da observação. O pré-protocolo atual mantém T0/Tend nulos.
4. Observar sete dias UTC reais, manter todos os 672 slots no denominador, produzir sete diários e consolidado e registrar recursos, falhas, outbox e recuperação. Drills e FakeSender permanecem separados dessa evidência.
5. Em D-M5, revisar D01–D22 e AC01–AC18 aplicáveis, conciliar resultados e registrar a decisão e as pendências remanescentes.

**Atualmente a Sprint 07 não está liberada.** Somente após concluir e revisar os critérios da Sprint 06 será possível declarar a 07 elegível para detalhamento/revisão, sem execução automática. SAM/piloto AWS e gates privados conservam suas dependências próprias. Disponibilidade do PAPER não comprova rentabilidade ou fills na corretora.

## Validação modular e documentação técnica

A capacidade continuous da SMA e os contratos de owner/risco/flags/custódia foram implementados e testados offline. Os casos com fakes não validam combinações reais inexistentes. Consultar a [matriz modular](estrategias-modulares-validacao.md), a [SMA](../estrategias/trend_sma.md), o [catálogo](../estrategias/README.md) e o [módulo contínuo](../modulos/paper-continuous.md).

A documentação de módulo, API, arquitetura, ADR, runbook, estratégias/catálogos e bancos foi criada/atualizada na implementação e revisada no recorte offline (D20). A conferência de links, hashes e relatórios consta nas evidências 06D. Não permanece como tarefa de implementação futura; qualquer evolução posterior deve manter esses documentos atualizados. Evidências operacionais e relatórios reais ainda precisam ser incorporados em D-M4/D-M5.

## Estrutura dos bancos e aceite documental

A 06D criou `continuous.sqlite3` e `notifications.sqlite3`, ambos schema 1, separados dos modelos anteriores. [Financeiro](../bancos/continuous-sqlite.md), [fila](../bancos/notification-sqlite.md), [catálogo](../bancos/README.md) e [introspecção](sprint-06d-schema.json) documentam os objetos reais. DDL/constraints/índices/triggers, replay, backup/restauração em scratch e rejeição de schemas incompatíveis foram verificados offline; não houve migração dos bancos históricos.

Recursos medidos em drills pequenos não demonstram capacidade ou disponibilidade durante sete dias. Medições de rede/serviços, crescimento por hora, supervisão e aplicação operacional dos procedimentos permanecem pendentes. Preservar dados/ledger e os registros históricos, sem reset ou limpeza destrutiva para obter aceite.

## Registros históricos das etapas

Os registros abaixo descrevem o estado observado em cada entrega; o resumo e a matriz acima prevalecem para a situação atual.

**Registro da revisão documental original de 25/10/2026:** nenhum comando, teste funcional, chamada de API, autenticação, provisionamento ou ordem foi executado naquela revisão. Não alterar arquivos de evidência das Sprints 01–03 para representar validações novas. Custos e recursos efetivos: não aferidos; nenhum criado nesta revisão. Preservar dados/ledger e identificar ambiente/época antes de qualquer limpeza futura.

## Consolidação 06A em 26/10/2026

M1/M2 aprovados: layout src antes do core, 533 testes bot + 54 core, qualidade/build/wheels, 22 fluxos por smoke e equivalência de 48 curvas sintéticas. AC09/10 concluídos; guards/AC14–17 verificados somente no alcance core/consumidor, a repetir nas próximas etapas. Relatório técnico e limitações de cache no [guia 06A](sprint-06a-validacao.md). Isso não executa o piloto, seus sete dias ou os casos de parcial/contínuo/notificações. AC18 e a transição para 07 permanecem pendentes; próxima ação é detalhar 06B.


## Consolidação 06B — 26/10/2026

B01–B18 aprovados offline conforme [guia 06B](sprint-06b-validacao.md), [evidências](sprint-06b-evidencias.json) e [relatório](relatorios/sprint-06b/report.html). Baseline bot 533 testes, biblioteca standalone 120, bot integrado 537; qualidade/build/wheels e regressões sintéticas/locks/manifestos/identidade aprovados. Cache frio completo não demonstrado. AC11 cumprido; critérios comuns verificados somente para composição 06B e deverão acompanhar 06C/06D. Nenhum critério do piloto operacional acima foi executado por essa extração. Próxima etapa elegível: detalhar/revisar 06C; 06D/gate global/07 pendentes.


## Registro inicial 06C — aceite então pendente

Bot 542 testes e analytics 28, qualidade/build/quatro wheels/22 comandos e compatibilidade selada aprovados tecnicamente. Ver [guia](sprint-06c-validacao.md), [evidências](sprint-06c-evidencias.json), [relatório](relatorios/sprint-06c/report.html). Quatro artefatos 06A divergiram dos hashes esperados após baseline íntegra; C01/C12/C18 pendentes de esclarecimento/recuperação ou decisão explícita de baseline revisada. AC12/AC13 têm provas técnicas; aceite integrado depende da resolução. Nenhum critério operacional do piloto foi executado; 06D/gate global/07 não liberados.


## Consolidação final 06C

Reconstrução externa confirmada e verificada por conteúdo/inventário/locks; composição já testada permanece igual. C01–C18 aprovados offline conforme [prova complementar](sprint-06c-reconstrucao-externa.json), [guia](sprint-06c-validacao.md), [evidências](sprint-06c-evidencias.json) e [relatório](relatorios/sprint-06c/report.html). Hashes históricos e atuais distintos, com limitação de rollback exato registrada; evidências anteriores e arquivos externos preservados. AC12/AC13 cumpridos. 06D somente elegível para detalhamento/revisão; nenhum critério operacional do piloto executado e gate global/07 pendentes.


## Consolidação offline 06D

D-M1–D-M3 aprovados no recorte offline, SOFTWARE_VALIDATED/PILOT_PENDING. [Guia06D](sprint-06d-validacao.md), [evidências](sprint-06d-evidencias.json), [relatório](relatorios/sprint-06d/report.html), [pré-protocolo não armado](sprint-06d-pre-protocolo.json).642 testes na suíte completa e108 na revisão focada sobreposta; analytics30 e31 comandos por wheels. Critérios de operação do roteiro acima continuam NÃO EXECUTADOS; nenhuma suíte acelerada equivale a sete dias/canais reais. D-M4/D-M5/gate global/07 pendentes.
