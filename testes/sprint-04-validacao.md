# Sprint 04 — Guia de validação da base modular e SMA

Revisão: 25/10/2026. **Estado: NÃO EXECUTADO / gate PENDENTE.** Nenhum código ou teste foi executado nesta revisão documental.

## Preparação e execução futura

Exigir evidências da 03 revisadas, preservar histórico e consultar [especificação 04](../sprints/sprint-04.md) e [matriz modular](estrategias-modulares-validacao.md). Workspace `/home/cams7/Dev/Cripto`; comandos Python futuros em `cripto-bot`, evidências em `docs/testes`. Não inventar comandos de CLI antes da implementação/detalhamento.

Usar relógio/mercado/transportes falsos e sockets bloqueados. Executar configuração padrão e opt-in sintético da SMA, rejeições de configuração, múltiplos módulos fake no coordenador, risco compartilhado e desativação com pendências. Regressões existentes, lint/tipos e wheel devem ser registrados com comandos reais, versões, hashes, stdout/stderr sanitizados e exit codes.

## Matriz de resultado

| Critério da especificação | Resultado | Evidência |
|---|---|---|
| AC01 | NÃO EXECUTADO | Pendente |
| AC02 | NÃO EXECUTADO | Pendente |
| AC03 | NÃO EXECUTADO | Pendente |
| AC04 | NÃO EXECUTADO | Pendente |
| AC05 | NÃO EXECUTADO | Pendente |
| AC06 | NÃO EXECUTADO | Pendente |
| AC07 | NÃO EXECUTADO | Pendente |
| AC08 | NÃO EXECUTADO | Pendente |
| AC09 | NÃO EXECUTADO | Pendente |
| AC10 | NÃO EXECUTADO | Documentação individual e catálogo pendentes da implementação |

## Decisão

Só aprovar com todos os critérios obrigatórios aprovados e zero ativação implícita, duplicação, divergência inexplicada ou bypass de risco. Flags de módulos desabilitadas por padrão e LIVE bloqueado. Não repetir ou alterar evidências JSON históricas para representar esses testes futuros. Falha mantém gate pendente, sem avançar implementação dependente.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.
