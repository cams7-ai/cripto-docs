# Sprint 04 — Base modular, flags, coordenação, risco e tendência SMA

Revisão: 25/10/2026. **Estado: PLANEJADA; implementação e validação NÃO EXECUTADAS.** Detalhamento executável depende da revisão das evidências da Sprint 03. Esta solicitação autoriza somente documentação.

## Objetivo e escopo

Criar a infraestrutura mínima de módulos Python com contratos padronizados, configuração externa validada e flags por ambiente/modo/par, reutilizando ledger e risco existentes; implementar apenas `trend_sma` como primeira estratégia long-only. Não exigir a implementação do catálogo opcional. Todos os módulos, inclusive SMA, desabilitados por padrão; ausência de estratégia habilitada produz HOLD/NOOP sem intenção financeira. Comandos sintéticos históricos da Sprint 03 preservam seu contrato e não se tornam uma estratégia ativada por default.

Aplicação em `/home/cams7/Dev/Cripto/cripto-bot`; documentação em `/home/cams7/Dev/Cripto/docs`. Modo exclusivamente PAPER, validação determinística offline com fixtures; backtest completo na 05, PAPER contínuo na 06. Sem AWS, credenciais, ordens externas, novos módulos opcionais ou runtime de plugins dinâmicos.

## Entregáveis previstos

`ModuleDescriptor`, Protocols/DTOs, registro estático e schemas mínimos, loader TOML seguro, snapshot/geração de configuração, coordenador `exclusive_owner`, identificação/atribuição de instância, integração com risco/ledger e SMA20/50 em `domain/strategy`/`application`. Evoluir paths após inspeção, sem criar adapters vazios de catálogo. Relógio e dados injetáveis, efeitos somente por portas existentes. Configuração de exemplo desabilitada; fixture opt-in explícita para demonstrar BUY/SELL simulados.

## Critérios de aceite

| ID | Condição verificável |
|---|---|
| AC01 | Default sem módulos: HOLD/NOOP e nenhuma intenção; flag só ativa na combinação explícita ambiente/modo/par/tipo de avaliação |
| AC02 | Rejeitar ativação não implementada, dependência ausente, versão/parâmetro inválido, ciclo e combinação incompatível antes de efeitos; desabilitado não importa dependência opcional |
| AC03 | SMA20/50 com pelo menos 51 fechamentos, cruzamento com igualdade e warm-up; sem sinal futuro nem fill no fechamento da decisão; vender só inventário atribuído |
| AC04 | Risco obrigatório global/instância/par; testar limites combinados e reservas, sem possibilidade de desligar por flag |
| AC05 | Coordenador recebe múltiplos fakes, rejeita disputa de propriedade, serializa reservas e deduplica; resultado determinístico independente da ordem de chegada |
| AC06 | Sinal/intenção/fill/resultado registram instância, versão e hash/geração; atribuições e custos reconciliam com a carteira |
| AC07 | Mudança/desativação bloqueia novas entradas, mantém OMS monitorando pendências/posições, reconcilia cancelamento/UNKNOWN e não liquida automaticamente; reativação sem replay |
| AC08 | Configuração inválida falha atomicamente; alteração material invalida evidência/aprovação dependente, sem reset de saldo/drawdown; rede e modos privados seguem bloqueados |
| AC09 | Contratos/isolamento, regressões 01–03, Ruff/mypy/pytest e wheel aprovados; documentação distingue teste futuro de resultado observado |
| AC10 | Criar `docs/estrategias/trend_sma.md` e atualizar catálogo na mesma entrega, cobrindo conteúdo da seção 4.7 do planejamento; revisão contra código/schema/testes, exemplos fictícios coerentes e evidências reais; pendência documental bloqueia conclusão |

A política de combinação avançada é introduzida quando necessária aos incrementos opcionais; teste com fakes comprova o limite do coordenador sem exigir duas estratégias prontas. O modelo financeiro da 03 não vira multiativo implicitamente.

## Transição e recuperação

Todos os critérios aprovados e revisão do [guia 04](../testes/sprint-04-validacao.md) permitem detalhar a Sprint 05. Não iniciar Sprints futuras ou publicar. Falha preserva configuração anterior para monitoramento e bloqueia novas entradas; estado financeiro divergente exige reconciliação. Custo apenas local de CPU/disco. LIVE permanece bloqueado independentemente da flag de SMA.

Referências normativas: [arquitetura modular](../arquitetura-modular.md), [planejamento](../planejamento.md) e [guia modular](../testes/estrategias-modulares-validacao.md).

Documentação de entrega: [catálogo e conteúdo obrigatório](../estrategias/README.md). O arquivo `docs/estrategias/trend_sma.md` será criado somente junto da implementação; exemplos de SMA isolada/conjunta devem distinguir suporte real de propostas futuras.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.
