# ADR 0005 — Estratégia opt-in e estado modular no journal financeiro

Data: 25/10/2026. Estado: implementada na Sprint 04; aceite funcional conforme [guia 04](../testes/sprint-04-validacao.md).

## Contexto

A Sprint 03 persistia somente um roteiro financeiro manual. A SMA acrescenta decisão causal, estado de indicador, propriedade, configuração por geração e deduplicação de candle. Confirmar esses itens em outro banco antes/depois da reserva permitiria perder uma decisão ou executá-la novamente após interrupção. O adapter v1 rejeita tabelas adicionais e não oferece migração.

## Decisão

Manter registro estático, DTOs/Protocol e `trend_sma` isolada, sempre desabilitada por padrão. Domínio não acessa rede/SQLite/ambiente; TOML e fixture usam fronteiras estritas. Coordenador `exclusive_owner` e risco central não são opcionais. Novos comandos `strategy-*` separam o replay da estratégia do roteiro histórico `paper-*` e do NOOP `run-once`.

Criar carteira modular em diretório novo, arquivo `paper.sqlite3` schema v2/modelo `paper-modular-v1`. Herdar o mecanismo de journal/postings/projeção/lock/CAS e a redução financeira da 03, com hooks de schema/modelo/redução/serialização cujo default mantém v1. Não copiar capital de carteira anterior nem migrar v1 automaticamente. Fluxos incompatíveis rejeitam schema antes de produzir efeito financeiro.

`StrategyWallet` estende carteira com gerações, instâncias, candles/watermark, baselines observados, ciclos e atribuições. Um único journal encadeado reconstrói o conjunto. Tabelas adicionais são projeções verificáveis; histórico de gerações e atribuições confirmadas é imutável. HOLD confirma ciclo/estado/cursor sem posting. CYCLE confirma decisão/atribuição/reserva juntos; FILL confirma carteira/custos/estado juntos em outra transação. Recuperar RESERVED antes de novos ciclos.

Uma chave de negócio inclui ambiente/modo/carteira/instância/versão/geração/época/dataset lógico/par/intervalo/candle. Hash do prefixo e da observação de execução detecta alteração do passado; run_id e dados futuros não criam identidade. Arquivo completo continua identificado no manifesto da execução. Mudança de geração não elimina watermark, baseline, pico ou custos; posição residual fica DRAINING sem liquidação automática.

Reconstruir integralmente ao entrar e ao concluir o caso de uso. Entre commits de um escritor exclusivo, otimizar a verificação com CAS da projeção e assinatura `(versão, total_changes, data_version, schema_version)` do SQLite. Escrita fora do caminho conhecido invalida essa verificação e exige replay completo. Não substitui lock, reconstrução final, triggers ou validação de integridade; não é coordenação distribuída.

Relatório JSON/HTML é snapshot derivado publicado após os commits, com manifesto/hashes e rename local. `strategy-report` abre o banco somente leitura e pode publicar arquivos, sem decidir/operar. Falha de publicação preserva negócio. HTML tem textos escapados, CSP, sem scripts/recursos remotos e estilo de impressão; PDF adicional não é dependência do runtime.

## Consequências e limites

Não há dois ledgers para uma carteira, migração implícita, executor privado ou import dinâmico. Os novos comandos preservam os contratos da 03, e testes de corrupção/concorrência/crash verificam as fronteiras. O schema v2 não é compatível com o adapter v1; rollback de binário não converte dados modularizados. Preservar o diretório e diagnosticar em cópia em caso de incompatibilidade.

Apenas local/PAPER/fixture/BTCUSDT/15m e uma instância. Parcial/UNKNOWN/cancel_and_monitor usam somente fakes de contrato; execução contínua e privada permanecem futuras. O modelo de fill financeiro é o integral sintético da 03, com identidade/atribuição modular acrescentadas. Não há demonstração de rentabilidade ou benchmark de produção.

## Referências

[Especificação 04](../sprints/sprint-04.md), [estratégia SMA](../estrategias/trend_sma.md), [banco financeiro v1/v2](../bancos/paper-sqlite.md) e [ADR 0004](0004-carteira-paper-e-ledger.md). Fontes oficiais: [sqlite3](https://docs.python.org/3.13/library/sqlite3.html#transaction-control), [Decimal](https://docs.python.org/3.13/library/decimal.html) e [Protocol](https://docs.python.org/3.13/library/typing.html#typing.Protocol), consultadas em 25/10/2026.
