# Sprint 06 — Consolidação da validação 06A–06D

Revisão: 26/10/2026. **Estado: PARCIAL — 06A/06B aprovadas; 06C aprovada; software06D validado offline; piloto/gate global pendentes.** O roteiro operacional abaixo corresponde a 06D e ainda não foi executado. A implementação 06A tem [guia próprio](sprint-06a-validacao.md) e [evidências](sprint-06a-evidencias.json).

## Preparação e execução futura

Consultar [especificação 06](../sprints/sprint-06.md) e [roteiro comum](validacao-pre-live.md). Dependências de 06D: 06A–06C aprovadas, Sprint 05/ajuste analítico revistos e composição/configuração congeladas. 06A/06B foram concluídas no escopo offline; 06C foi aprovada após esclarecer a reconstrução externa, conforme consolidação abaixo.

Modo permitido: PAPER; somente dados públicos reais; nenhuma ordem enviada à Binance. Comandos futuros executam em `/home/cams7/Dev/Cripto/cripto-bot`; evidências permanecem em `/home/cams7/Dev/Cripto/docs/testes`. Ao detalhar a implementação, preencher comandos reais, versões e resultados; não executar CLI fictícia deste planejamento.

1. Identificar revisão/release e hashes de configuração/modelo/dataset; conferir dependências e isolamento antes de iniciar.
2. Executar testes locais determinísticos com rede bloqueada, incluindo rejeições e sentinelas de transporte.
3. Quando previstos, executar ensaios externos somente após autorização específica da etapa e validação do ambiente; nunca substituir Demo/Testnet por produção.
4. Cobrir: Integral/parcial/sem fill, atraso, cancelamento restante, reinício antes/depois de persistir, duplicação, cotação inválida e falha de notificação.
5. Registrar evidência por critério, distinguir fake/injeção/API, comparar ledger/saldos e submeter a revisão do responsável.

## Matriz operacional 06D — pendente

| Critério da especificação | Resultado | Evidência |
|---|---|---|
| AC01 | NÃO EXECUTADO | Pendente |
| AC02 | NÃO EXECUTADO | Pendente |
| AC03 | NÃO EXECUTADO | Pendente |
| AC04 | NÃO EXECUTADO | Pendente |
| AC05 | NÃO EXECUTADO | Pendente |
| AC06 | NÃO EXECUTADO | Pendente |
| AC07 | NÃO EXECUTADO | Pendente |
| AC08 — contrato modular/composição | NÃO EXECUTADO | Pendente |

## Decisão e limites

Todos os critérios e a revisão das evidências permitem a Sprint 07. Piloto AWS permanece condicionado ao pacote/contratos da 07 e aos pré-requisitos da 08; nenhum gate privado é dispensado.

Dados de mercado são reais; carteira e execução são internas. Não mede fila, impacto próprio ou fills da corretora. Evidências de cenários injetados devem ser distinguidas da observação contínua.

**Registro da revisão documental original de 25/10/2026:** nenhum comando, teste funcional, chamada de API, autenticação, provisionamento ou ordem foi executado naquela revisão. Não alterar arquivos de evidência das Sprints 01–03 para representar validações novas. Custos e recursos efetivos: não aferidos; nenhum criado nesta revisão. Preservar dados/ledger e identificar ambiente/época antes de qualquer limpeza futura.

## Validação modular adicional — pendente

Executar o critério modular adicionado à especificação desta Sprint e os casos aplicáveis do [guia modular](estrategias-modulares-validacao.md), registrando instâncias/versões, flags por ambiente/modo/par, pesos, política de coordenação/desativação, algoritmo e hash/geração. Distinguir ensaio isolado, combinação real e fakes do coordenador; aceites individuais não habilitam composição sem teste conjunto. Nenhum resultado foi obtido por esta revisão; modos privados e LIVE permanecem bloqueados conforme os gates.

## Verificação da documentação técnica — pendente

Na execução futura, identificar os módulos afetados e revisar seus arquivos em `docs/estrategias/` e o catálogo segundo o [conteúdo obrigatório](../estrategias/README.md) e o caso M16 do [guia modular](estrategias-modulares-validacao.md). Conferir comportamento/parametrização/flags/risco contra código, schemas e testes, cálculos do ciclo fictício, links/versão, comandos reproduzíveis e evidências esperadas versus obtidas. Registrar APROVADA/PENDENTE por documento e revisão; pendência bloqueia conclusão da Sprint. Caso nenhum módulo seja alterado, justificar essa constatação. Estado nesta revisão: NÃO EXECUTADO, sem evidência de implementação futura.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.


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
