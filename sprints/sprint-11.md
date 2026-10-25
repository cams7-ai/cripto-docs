# Sprint 11 — Preparação de LIVE limitado e aprovação do responsável

Revisão: 25/10/2026. **Estado: PLANEJADA; implementação e validação NÃO EXECUTADAS.** Este contrato atualiza o roadmap, sem autorizar execução antecipada. O detalhamento executável de interfaces/comandos depende da conclusão e revisão das Sprints anteriores.

## Objetivo, escopo e dependências

Produzir um dossiê revisável de prontidão e comprovar que nenhuma compra/venda real pode ocorrer sem todos os requisitos.

Dependências: Sprints 05–10 aprovadas e revisadas, sem cenários obrigatórios pendentes; configuração e release identificadas.

Modo: Preparação com LIVE bloqueado; ensaios sem ordens reais. Operação real exige solicitação e aprovação posteriores específicas.

Workspace exclusivo: `/home/cams7/Dev/Cripto`; aplicação Python em `cripto-bot`, documentação em `docs`. Mercado inicial: Spot, sem margem, alavancagem ou derivativos. Não modificar projetos LotoBot nem ativar produção.

## Entregáveis previstos

Checklist de risco e prontidão, registro de aprovação com validade, configuração de exemplo desabilitada, matriz de barreiras negativas, runbooks, plano de piloto limitado e rollback que não apague ledger nem presuma reversão de ordens.

## Critérios objetivos de aceite

| ID | Condição verificável |
|---|---|
| AC01 | Revisar todos os gates e evidências; separar aprovação de engenharia da econômica. Registrar critérios econômicos antes da avaliação final, inclusive retorno líquido fora da amostra e drawdown com custos dobrados. |
| AC02 | Configurar capital máximo, tamanho máximo por ordem, exposição total, perda diária monetária e percentual, drawdown, ordens/posições simultâneas, freshness, taxas/slippage tolerados e resposta a incidente; valores reais aprovados, sem herdar limites didáticos. |
| AC03 | Confirmar elegibilidade Spot de conta/região, permissões sem saque/margem/derivativos, restrição de IP suportada, saída estável, segredo/role exclusivos e saldo/ordens reconciliados antes do piloto futuro. |
| AC04 | Testar ausência de habilitação, aprovação ausente/expirada, conta/release/estratégia/hash divergentes, limite ausente/inválido, gate pendente e kill switch ativo; cada caso impede construir/enviar pelo executor real. |
| AC05 | Aprovação deve conter responsável, data/validade, conta, release, estratégia, hash dos limites/configuração e escopo do piloto; qualquer mudança material invalida. Habilitação explícita sozinha não basta. |
| AC06 | Plano de operação e recuperação revisado; UNKNOWN ou divergência bloqueiam novas ordens; retomada requer resolução e decisão registrada. Nenhum POST/DELETE de negociação real no ensaio desta Sprint. |
| AC07 | Aprovação identifica conjunto de módulos/instâncias/versões, pesos, composição, pares, algoritmos e hashes validados; módulo novo, flag, modelo ou mudança material invalida aprovação afetada; LIVE continua bloqueado por padrão. |

## Evidência e decisão de transição

Preparação concluída não ativa LIVE. Primeira compra/venda real exige nova autorização explícita do responsável para o escopo do piloto, gates aprovados, limites válidos, aprovação vigente e habilitação explícita; padrão continua bloqueado. Ampliação exige nova aprovação.

Registrar versões, revisão do código, hash de configuração/modelo/dataset, intervalos UTC, execução dos casos, logs sanitizados, métricas, custos e decisão do revisor no [guia 11](../testes/sprint-11-validacao.md). Qualquer caso obrigatório não executado mantém o aceite pendente. Não inventar comandos ou resultados de implementação futura.

## Limitações, recuperação e custos

Resultados positivos em simulação não garantem rentabilidade. Gates reduzem falhas conhecidas, sem assegurar preço, liquidez ou perda máxima; não há promoção automática por prazo ou lucro.

Em falha, preservar evidências, interromper novos compromissos e reconciliar; não remover ledger ou alterar critério para obter aprovação. Em ambiente virtual, separar épocas de reset e configurações. Na etapa histórica/local, custo de disco/CPU/rede; nas etapas remotas, recotar infraestrutura/rede e dependências, sem pressupor gratuidade. Preparação LIVE não consome capital real.

Referências normativas: [planejamento, seções 6–10](../planejamento.md#10-gates-entre-ambientes-e-modos) e [roteiro comum de validação](../testes/validacao-pre-live.md). Esta revisão autoriza somente documentação.

## Contrato modular aplicável — revisão de 25/10/2026

Adotar a [arquitetura modular](../arquitetura-modular.md) e os casos aplicáveis do [guia modular](../testes/estrategias-modulares-validacao.md). Todos os módulos começam desabilitados; ensaios habilitam explicitamente somente instâncias implementadas por ambiente/modo/par. A elegibilidade é da versão/configuração/composição testada, sem exigir todo o catálogo. Esta atualização é documental, não implementa o schema nem altera evidências históricas.

## Documentação técnica como critério de conclusão

Se esta Sprint implementar ou alterar módulo, regra, interface/dependência/estado, dado/parâmetro/default/validação, flag/composição ou controle de risco, atualizar `docs/estrategias/<module_id>.md` e `docs/estrategias/README.md` na mesma entrega, conforme o [conteúdo obrigatório](../estrategias/README.md). Revisar exemplos, comandos, versões e evidências; separar efetivamente implementado de planejado/pendente. Registrar a decisão documental no guia desta Sprint; ausência/desatualização bloqueia conclusão. Se nenhum módulo for afetado, registrar essa conclusão e sua justificativa sem criar documento de módulo futuro.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.
