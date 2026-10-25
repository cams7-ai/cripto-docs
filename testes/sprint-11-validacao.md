# Sprint 11 — Guia de validação: Preparação de LIVE limitado e aprovação do responsável

Data: 25/10/2026. **Estado: NÃO EXECUTADO / gate PENDENTE.** Roteiro planejado; nenhuma aprovação funcional ou externa decorre da criação deste arquivo.

## Preparação e execução futura

Consultar [especificação 11](../sprints/sprint-11.md) e [roteiro comum](validacao-pre-live.md). Dependências: Sprints 05–10 aprovadas e revisadas, sem cenários obrigatórios pendentes; configuração e release identificadas.

Modo permitido: Preparação com LIVE bloqueado; ensaios sem ordens reais. Operação real exige solicitação e aprovação posteriores específicas. Comandos futuros executam em `/home/cams7/Dev/Cripto/cripto-bot`; evidências permanecem em `/home/cams7/Dev/Cripto/docs/testes`. Ao detalhar a implementação, preencher comandos reais, versões e resultados; não executar CLI fictícia deste planejamento.

1. Identificar revisão/release e hashes de configuração/modelo/dataset; conferir dependências e isolamento antes de iniciar.
2. Executar testes locais determinísticos com rede bloqueada, incluindo rejeições e sentinelas de transporte.
3. Quando previstos, executar ensaios externos somente após autorização específica da etapa e validação do ambiente; nunca substituir Demo/Testnet por produção.
4. Cobrir: Todas as barreiras negativas com transporte fake/sentinela; aprovação válida em ensaio ainda sem socket/ordem real; mudança material invalida aprovação.
5. Registrar evidência por critério, distinguir fake/injeção/API, comparar ledger/saldos e submeter a revisão do responsável.

## Matriz de resultados

| Critério da especificação | Resultado | Evidência |
|---|---|---|
| AC01 | NÃO EXECUTADO | Pendente |
| AC02 | NÃO EXECUTADO | Pendente |
| AC03 | NÃO EXECUTADO | Pendente |
| AC04 | NÃO EXECUTADO | Pendente |
| AC05 | NÃO EXECUTADO | Pendente |
| AC06 | NÃO EXECUTADO | Pendente |
| AC07 — contrato modular/composição | NÃO EXECUTADO | Pendente |

## Decisão e limites

Preparação concluída não ativa LIVE. Primeira compra/venda real exige nova autorização explícita do responsável para o escopo do piloto, gates aprovados, limites válidos, aprovação vigente e habilitação explícita; padrão continua bloqueado. Ampliação exige nova aprovação.

Resultados positivos em simulação não garantem rentabilidade. Gates reduzem falhas conhecidas, sem assegurar preço, liquidez ou perda máxima; não há promoção automática por prazo ou lucro.

Nenhum comando, teste funcional, chamada de API, autenticação, provisionamento ou ordem foi executado nesta revisão documental. Não alterar arquivos de evidência das Sprints 01–03 para representar validações novas. Custos e recursos efetivos: não aferidos; nenhum criado nesta revisão. Preservar dados/ledger e identificar ambiente/época antes de qualquer limpeza futura.

## Validação modular adicional — pendente

Executar o critério modular adicionado à especificação desta Sprint e os casos aplicáveis do [guia modular](estrategias-modulares-validacao.md), registrando instâncias/versões, flags por ambiente/modo/par, pesos, política de coordenação/desativação, algoritmo e hash/geração. Distinguir ensaio isolado, combinação real e fakes do coordenador; aceites individuais não habilitam composição sem teste conjunto. Nenhum resultado foi obtido por esta revisão; modos privados e LIVE permanecem bloqueados conforme os gates.

## Verificação da documentação técnica — pendente

Na execução futura, identificar os módulos afetados e revisar seus arquivos em `docs/estrategias/` e o catálogo segundo o [conteúdo obrigatório](../estrategias/README.md) e o caso M16 do [guia modular](estrategias-modulares-validacao.md). Conferir comportamento/parametrização/flags/risco contra código, schemas e testes, cálculos do ciclo fictício, links/versão, comandos reproduzíveis e evidências esperadas versus obtidas. Registrar APROVADA/PENDENTE por documento e revisão; pendência bloqueia conclusão da Sprint. Caso nenhum módulo seja alterado, justificar essa constatação. Estado nesta revisão: NÃO EXECUTADO, sem evidência de implementação futura.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.
