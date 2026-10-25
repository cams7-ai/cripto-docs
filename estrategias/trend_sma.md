# trend_sma — Tendência por cruzamento de médias simples

Sprint de origem: 04. Revisão: 25/10/2026. Implementação Python versão `1`, schema de parâmetros/estado `1`, modelo financeiro modular `paper-modular-v1`. Estado de aceite e resultados efetivos: [guia 04](../testes/sprint-04-validacao.md). **Desabilitada por padrão; suporte somente local/PAPER/fixture/BTCUSDT/15m.** Backtest, operação contínua e execução privada permanecem inelegíveis até seus gates.

## 1. Objetivo, papel e conceitos

Estratégia de negociação que tenta acompanhar movimentos de tendência, alternando entre BTC comprado e caixa USDT. SMA significa média móvel simples: soma dos últimos N fechamentos dividida por N. A média curta reage mais rapidamente que a longa; seu cruzamento é um critério explicável de entrada/saída, sem garantir previsão ou rentabilidade.

Este módulo produz alvo e motivo. Não lê arquivos, não acessa rede/banco, não reserva saldo nem envia ordens. Coordenador, dimensionamento, risco e executor local decidem se o alvo pode virar um compromisso financeiro.

Código: [SMA pura](../../cripto-bot/modules/trading/src/cripto_bot/domain/strategy/sma.py), [contratos e registro](../../cripto-bot/modules/trading/src/cripto_bot/domain/modules/models.py), [transições modulares](../../cripto-bot/modules/trading/src/cripto_bot/domain/strategy/engine.py) e [caso de uso](../../cripto-bot/modules/trading/src/cripto_bot/application/strategy_run.py).

## 2. Regimes, entradas, saídas e inatividade

Pode permanecer comprada quando há cruzamento de alta e depois nenhum novo cruzamento. Mercados laterais podem provocar alternância frequente entre compra e venda, acumulando custos; mudanças bruscas produzem atraso de resposta. Não há stop intrabar, short, pirâmide, martingale ou compra adicional em queda.

| Condição | Decisão |
|---|---|
| Menos de `slow_window + 1` fechamentos | HOLD/WARMUP, sem intenção |
| Curta anterior ≤ longa anterior; curta atual > longa atual; posição zero | LONG/CROSS_UP, propor compra limitada |
| Mesmo cruzamento, já com BTC | HOLD/ALREADY_LONG |
| Curta anterior ≥ longa anterior; curta atual < longa atual; BTC próprio disponível | CASH/CROSS_DOWN, propor encerramento |
| Mesmo cruzamento sem inventário | HOLD/NO_INVENTORY |
| Igualdade atual ou ausência de cruzamento | HOLD/NO_CROSS |
| Módulo desabilitado em carteira existente | HOLD/DISABLED; custódia/monitoramento mantidos |

HOLD não cria intenção. Recusa ou ausência de preço não reenvia o cruzamento em outro candle; é necessário novo cruzamento. BUY/SELL externos nunca são emitidos nesta versão.

## 3. Dados, tempo e precisão

Candles fechados, contíguos, ordenados e com OHLC/volume válidos. `15m` significa 900.000 ms entre aberturas. Fechamento inclusivo = abertura + 900.000 - 1 ms; disponibilidade = fechamento + 1 ms. A estratégia recebe apenas fechamentos disponíveis até `as_of`; observações de execução não entram em seu snapshot.

Médias usam Decimal em contexto local de precisão 80, sem arredondamento de apresentação antes da comparação. Representações das médias podem ter mais de oito casas; valores contábeis mantêm o quantum BTC/USDT `0.00000001`. Preço e quantidade obedecem tick/step das regras sintéticas. Nenhum float participa da aritmética financeira.

O sinal expira em `as_of + max_quote_age_ms` neste ensaio; observação e fill precisam ser posteriores à decisão e respeitar essa validade e a idade da cotação. Falta de observação válida registra NOT_EXECUTED, sem preço inventado. Custo/execução e preço de fechamento têm papéis distintos.

O relógio é de replay. DAY_START explícito inicializa cada dia UTC antes das decisões daquele dia, inclusive quando o candle abriu no dia anterior e fecha à meia-noite. Marcas posteriores não alteram baselines passados. Adicionar dados futuros preserva identidade, médias e motivos do prefixo já processado; modificar candle, cotação de execução ou baseline confirmado é conflito.

## 4. Parâmetros, configuração e flags

| Campo | Default | Validação / unidade |
|---|---|---|
| `fast_window` | 20 | Inteiro estrito ≥1 e menor que slow; bool rejeitado |
| `slow_window` | 50 | Inteiro estrito ≤500; warm-up derivado slow+1 |
| `interval` | 15m | Único intervalo suportado |
| `capital_weight` | `"0.10"` | Fração positiva até 1; teto adicional de capital, sem aporte |
| `execution` | immediate | Único caminho disponível; fill integral PAPER |
| `on_disable` | hold_and_monitor | Não liquida posição nem abandona pendências |
| `enabled` | false | Opt-in explícito; ausência/lista vazia não ativa |
| Escopos | Listas explícitas | local/PAPER/fixture/BTCUSDT; wildcard e capacidades futuras habilitadas rejeitados |

Arquivos completos: [default desabilitado](../../cripto-bot/config/strategy.sma.example.toml) e [opt-in sintético](../../cripto-bot/config/strategy.sma.fixture.toml). `depends_on` permite declarar IDs de instância para validação de dependência; a SMA isolada não possui dependências modulares. Dependência ausente/desabilitada/cíclica falha antes de efeitos. O registro é estático; listar um módulo ausente com flag false não importa bibliotecas nem implementa seu runtime.

Limites opcionais mais restritivos: `[modules.trend_btc.limits]` e `[coordination.symbol_limits.BTCUSDT]`, aceitando apenas `max_entry_fraction`, `max_exposure_fraction`, `max_daily_loss_fraction`, `max_drawdown_fraction`. Strings decimais positivas, não superiores aos globais. Denominadores são patrimônio/baseline/pico da carteira global no piloto de proprietário único; orçamento da instância limita adicionalmente a entrada.

## 5. Interfaces, estado e persistência

`TrendSMA.evaluate(Snapshot, fast, slow, instance)` retorna `Decision` imutável. Snapshot contém fechamentos, instante e posição própria; Decision contém alvo/motivo e médias atual/anterior. `ModuleDescriptor` registra versão, schemas, capacidades e recurso exclusivo. O domínio usa biblioteca padrão; Pydantic valida a fronteira TOML/fixture.

O envelope adiciona carteira/instância/versão/geração/época, par/intervalo, candle, as_of/valid_until, dataset lógico/hash do prefixo, hash da observação de execução e limites efetivos. Identidade do ciclo deriva desse contexto, sem run_id ou hash de dados futuros. Gerar relatório não gera uma nova decisão.

Um único journal do [SQLite financeiro v2](../bancos/paper-sqlite.md) reconstrói carteira, gerações, ciclos e atribuições. HOLD confirma estado/cursor sem postings. A transação A une ciclo/decisão/reserva/atribuição; B confirma fill/custos/posição/estado. Morte entre A/B deixa plano RESERVED recuperável; retomada usa o plano persistido antes de avaliar novos candles. Lock/CAS impedem dois escritores cooperantes. Projeções e atribuições são confrontadas com a reconstrução, sem correção automática.

## 6. Coordenação, capital e risco

Somente `exclusive_owner`: uma instância pode possuir BTCUSDT/carteira. Duas ativas disputando o recurso são rejeitadas, independentemente da ordem de chegada. Testes com fakes não aprovam uma combinação real de estratégias. `weighted_targets`, `segregated_budgets`, multiativo, TWAP/VWAP, notícias e ML continuam ausentes/desabilitados.

Antes de BUY, orçamento é limitado por caixa, peso e limites globais/instância/par. Preço/taxa determinísticos permitem calcular quantidade inicial; step arredonda para baixo e o plano definitivo é revalidado. Custos/arredondamentos que ultrapassem o limite geram recusa, sem reduzir intenção fixada em silêncio. SELL usa apenas inventário próprio livre e continua sujeito a dados/filtros/estado confiáveis.

Limites didáticos globais: entrada/exposição 10%, uma posição/pendência; perda diária 1% e drawdown 5% bloqueiam entradas, incluindo taxas e marcação não realizada. Overrides somente restringem; flag não desliga risco. Reserva é transferência interna, não gasto nem resultado. Trava não dispara venda automática. Os valores não são limites aprovados para capital real.

## 7. Desativação, geração e falhas

Snapshot inteiro validado e aplicado por CAS em fronteira de ciclo. Configuração idêntica não cria geração; mudança material com posição/pendência é recusada enquanto incompatível. Alterações invalidam evidências de elegibilidade afetadas, sem apagar custos, pico, baseline ou deduplicação.

Desativar impede novas entradas e mantém serviço financeiro independente resolvendo RESERVED. BTC residual permanece em DRAINING, marcado e consumindo orçamento/risco. Não há CLI de liquidação ou transferência automática de propriedade. Reativação em caixa incrementa época quando aplicável e só considera candles posteriores ao watermark; históricos aquecem médias sem reenviar cruzamentos.

`cancel_and_monitor`, fills parciais e UNKNOWN não são capacidades operacionais desta versão. Contratos de monitoramento são testados com fakes; cancelamento local de reserva é testado por API interna, com liberação única e fill posterior rejeitado. Falha de avaliação encerra o ciclo sem confirmar seu estado/ordem; a CLI sanitiza o diagnóstico. Estado compartilhado divergente bloqueia a carteira quando possível. Falha de relatório preserva os commits e permite reexportação.

## 8. Ciclos fictícios e custos

Demonstração de 71 fechamentos `[100]×50 + [110] + [100]×20`: 50 warm-up, 19 outros HOLD e dois cruzamentos. Saldo inicial 10000 USDT, peso 10%, taxa/spread/slippage 10/10/5 bps; tick 0.01/step 0.000001. Observações posteriores à decisão são 110 na compra e 100 na venda.

| Operação | BTC | Preço USDT/BTC | Notional USDT | Taxa USDT |
|---|---|---|---|---|
| BUY | 9.07275400 | 110.11000000 | 999.00094294 | 0.99900095 |
| SELL | 9.07275400 | 99.90000000 | 906.36812460 | 0.90636813 |

Resultado líquido `-94.53818742 USDT`, saldo final `9905.46181258`, taxas `1.90536908`; BTC/reservas/custo encerrados. Resultado negativo é válido para engenharia.

Teste separado com janelas 1/2 e observações 100/110, mesmos custos/peso: quantidade `9.98002900 BTC`, preços 100.10/109.89, taxas 0.99900091/1.09670539, resultado positivo calculado `95.60877761 USDT`, saldo `10095.60877761`. O teste automatizado verifica resultado positivo; a conferência aritmética detalhada é explicação fictícia, sem equivaler a uma avaliação econômica fora da amostra.

## 9. Testes, comandos e relatórios

Testes: [SMA](../../cripto-bot/tests/unit/test_strategy_sma.py), [configuração](../../cripto-bot/tests/unit/test_module_config.py), [coordenador](../../cripto-bot/tests/unit/test_coordinator.py), [CLI/relatórios](../../cripto-bot/tests/integration/test_strategy_cli.py), [persistência/crash](../../cripto-bot/tests/integration/test_strategy_storage.py). Comandos a partir de `/home/cams7/Dev/Cripto/cripto-bot`:

```bash
uv run --locked cripto-bot strategy-run
uv run --locked cripto-bot strategy-run --config config/strategy.sma.example.toml
uv run --locked cripto-bot strategy-run --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-reconcile --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-report --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-run --config config/strategy.sma.fixture.toml
```

Primeiras duas chamadas: NOOP sem carteira; opt-in novo: dois fills; replay: zero. Se o diretório já tiver execução, não apagar para fabricar primeira passagem; usar outra configuração/carteira sintética identificada. Report não inicializa carteira. run/report publicam JSON, HTML autocontido e manifesto por run_id; erro de exportação não refaz fills.

Métricas disponíveis: ciclos/warm-up/HOLD/cruzamentos, médias/motivos, fills/recusas/replays, posição/custos/taxas/PnL/patrimônio/risco e atribuição. O HTML mostra evolução de patrimônio por ciclo e distingue histórico de efeito novo. Não são métricas de avaliação estatística: turnover, tempo em tendência, whipsaws, comparação com benchmarks e retorno fora da amostra serão definidos na Sprint 05. Resultados, hashes, cobertura e aceite real estão no guia/evidências 04, sem inferir aprovação pelo exemplo.

## 10. Limitações e elegibilidade

Somente Spot financiado em BTC/USDT sintético; sem short, margem, derivativos ou capital externo. Fill integral local não modela fila, impacto, liquidez real ou probabilidades. Não há rede de execução, notificações ou recursos AWS. Opção de flag não habilita LIVE, Demo ou Testnet; não dispensa gates por módulo/configuração/ambiente.

Operação contínua, parcial/atraso/sem fill, backtest econômico, benchmark de alto volume, filesystem remoto e perda de energia/disco permanecem não comprovados. O critério de conclusão desta Sprint é integridade/reprodutibilidade, independentemente do sinal do PnL.

## 11. Referências e histórico

[Especificação 04](../sprints/sprint-04.md), [planejamento](../planejamento.md), [ADR modular](../decisoes/0005-estrategia-modular-e-persistencia.md), [guia 04](../testes/sprint-04-validacao.md) e [evidências 04](../testes/sprint-04-evidencias.json). Fontes oficiais reconfirmadas em 25/10/2026: [Decimal](https://docs.python.org/3.13/library/decimal.html), [Protocol](https://docs.python.org/3.13/library/typing.html#typing.Protocol), [sqlite3](https://docs.python.org/3.13/library/sqlite3.html#transaction-control) e [Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/). Implementação usa versões fixadas pelo lock, sem novas dependências.

| Revisão | Mudança | Evidências afetadas |
|---|---|---|
| 25/10/2026 / Sprint 04 | Primeira implementação, fixtures/flags, ciclos atômicos, monitoramento e relatório legível | Aceite restrito ao ensaio offline registrado no guia 04; nenhuma liberação operacional herdada |
