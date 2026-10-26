# Sprint 05 - validação e evidências

**APROVADA no alcance local/PAPER/backtest/BTCUSDT/15m.** Execução consolidada em 25/10/2026. Não autoriza LIVE, PAPER contínuo, AWS ou início automático da Sprint 06. Lucro não foi critério de engenharia.

## Base e versão avaliada

A base da 04 foi conferida antes de alterações: 87/87 hashes e regressão de 428 testes aprovados. Revisão da aplicação: `23545df1dcad76cf90dfefd29e8134558bee3f50`; docs: `c9db28c8521e47b722808bc980fe086821a7e653` (ambas com alterações locais desta entrega, sem commit). Evidências 01-04 preservadas. Python/SQLite/pacotes/lock/wheel e hashes por arquivo estão em [evidências](sprint-05-evidencias.json).

Código congelado: `d5a26f60e8f839d4c2008b52b8e67ec4678142bb0d61db236176cca29fdf54ac`. Protocolo real: `8bc553e60fea776f3528564c2c93c1a1879fd4860436d55f61282415126e2e14`. Dataset: `2827f105f2317415bea64fd91dfbfc6aa228029c421282433cf424a5b4fcbd55`. Resultado canônico: `a12de079b7ebded9037c86b1f76b7b9a9edcb37ef68603a36cd7f79b50cc2f47`.

## Qualidade e escala

- 521 testes aprovados, zero falhas/erros/avisos, em 582.158 s. Incluem as regressões anteriores e os cenários históricos.
- Cobertura: 3516/3670 linhas e 1069/1212 branches; 93,92% combinada. Caminhos não cobertos incluem falhas raras de filesystem/SQLite; não é alegação de cobertura 100%.
- Ruff, formatação, mypy strict, build e wheel reinstalado aprovados. Origem: `/home/cams7/Dev/Cripto/cripto-bot/.venv-wheel/lib/python3.13/site-packages/cripto_bot/__init__.py`. Cwd neutro `.wheel-smoke`, sem PYTHONPATH, `-I`, guard de sockets comprovado; esse diretório fica dentro do workspace, sem fonte importável pelo cwd.
- Escala sintética: 70130 candles (70080 de score), 192.73 s, RSS pico 76312 KiB, banco 282570752 bytes, checkpoint máximo 1308 bytes e janela máxima de 51 candles. SMA/base nos três segmentos; não é benchmark econômico nem SLA. As medições ocorreram durante validações locais concorrentes.

A sequência real de oito comandos levou 11.318,36 s (aproximadamente 3 h 08 min), incluindo as reconciliações e a reprodução; pico de RSS dos filhos: 111.616 KiB. O export final contém 2.244.867 registros de patrimônio, 1.121.268 decisões e 2.211 fills. Contagens e hashes dos CSVs foram confrontados com o banco. Esses tempos são observações locais, sem garantia de desempenho.

## Dados, protocolo e execução real

Coleta pública separada e autorizada via `collect-market --allow-network`, em dez exportações, sem credencial/fallback/host alternativo. Cada lote teve até 8000 candles, `page_limit=1000` e `max_pages=10` e orçamento do adapter existente. Não houve rede nos comandos backtest. Janela de score `[2024-10-25T00:00Z,2026-10-25T00:00Z)`: 70080 candles; mais 50 anteriores, total 70130. Hashes dos quatro arquivos de cada fonte, contagem/continuidade/SHA canônico/CRC/tipos foram verificados. Filtros são proxy sintético congelado, sem comprovação de exchangeInfo histórico.

Split: desenvolvimento 42048 candles (até 06/01/2026), validação 14016 (até 01/06/2026), teste 14016 (até 25/10/2026). Carteiras novas/independentes de 10000 USDT por segmento/variante/perfil; não somar patrimônios ou retornos. Aquecimento prepara indicadores, sem posição/PnL herdados. A primeira fronteira SMA ainda não dispõe de slow+1 fechamentos e não emite decisão; benchmarks fixos entram na primeira referência permitida.

Parâmetros 20/50, custos, risco, disponibilidade e fórmulas foram congelados antes do PnL de cada protocolo. Protótipos interrompidos durante desenvolvimento foram preservados; correções repetiram fases sob novo hash antes de qualquer teste real. Não foram usados sinais/PnL do teste real para selecionar parâmetros. Integridade dos bytes/OHLC completos foi conferida antes, conforme o contrato. O registro local documenta o primeiro processamento final e rejeita janelas reais sobrepostas com outro protocolo; não prova ausência de conhecimento humano prévio.

| Segmento / perfil (base) | Patrimônio final USDT | Retorno líquido | MDD | Trades / fills |
| --- | ---: | ---: | ---: | ---: |
| development / sma | 9696.56184956 | -3.0344% | 5.0429% | 121 / 242 |
| development / cash | 10000.00000000 | 0.0000% | 0.0000% | 0 / 0 |
| development / buy_hold_100pct | 13735.27357643 | 37.3527% | 35.7631% | 0 / 1 |
| development / buy_hold_10pct | 10373.50693766 | 3.7351% | 6.0812% | 0 / 1 |
| validation / sma | 9495.56161784 | -5.0444% | 5.0864% | 97 / 194 |
| validation / cash | 10000.00000000 | 0.0000% | 0.0000% | 0 / 0 |
| validation / buy_hold_100pct | 7833.74508063 | -21.6625% | 38.3147% | 0 / 1 |
| validation / buy_hold_10pct | 9783.39284388 | -2.1661% | 3.9639% | 0 / 1 |
| test / sma | 9494.48742537 | -5.0551% | 5.0719% | 163 / 326 |
| test / cash | 10000.00000000 | 0.0000% | 0.0000% | 0 / 0 |
| test / buy_hold_100pct | 10957.21374417 | 9.5721% | 21.3496% | 0 / 1 |
| test / buy_hold_10pct | 10095.72066778 | 0.9572% | 2.1385% | 0 / 1 |

### Sensibilidade SMA

| Segmento / variante SMA | Retorno | MDD | Taxas USDT | BTC residual |
| --- | ---: | ---: | ---: | ---: |
| development / base | -3.0344% | 5.0429% | 240.58871252 | 0.00000000 |
| development / double_costs | -3.8195% | 5.0774% | 280.47165716 | 0.00000000 |
| development / delay_1candle | -3.2147% | 5.0005% | 240.91920624 | 0.00000000 |
| development / double_costs_delay | -3.9005% | 5.0087% | 319.32585756 | 0.00000000 |
| validation / base | -5.0444% | 5.0864% | 188.04150352 | 0.00000000 |
| validation / double_costs | -5.0233% | 5.0463% | 193.99801649 | 0.00000000 |
| validation / delay_1candle | -4.8840% | 5.1195% | 137.92459414 | 0.00000000 |
| validation / double_costs_delay | -4.9896% | 5.0069% | 170.75834389 | 0.00000000 |
| test / base | -5.0551% | 5.0719% | 315.25891476 | 0.00000000 |
| test / double_costs | -5.0194% | 5.0341% | 220.27110089 | 0.00000000 |
| test / delay_1candle | -4.5554% | 4.6365% | 307.64548679 | 0.01184000 |
| test / double_costs_delay | -4.9761% | 5.0129% | 228.10150068 | 0.00000000 |

Cenário-base 10/10/5 bps; custos dobrados 20/20/10 bps; atraso adicional de um candle; combinado. Cada variante refaz o dimensionamento causal. Referência open OHLC observada em +1 ms, fill em +2 ms; nenhum high/low/close futuro escolhe execução. Sinal vence na abertura agendada +5 s; freshness da referência é separada e suporta 1 ms no caso de controle. Terminal mark_to_market: BTC residual não é vendido implicitamente.

Os meses UTC e sua direção descritiva constam no JSON completo/selecionado, sem escolha retrospectiva de trechos. MDD e exposição usam a série completa, não o gráfico reduzido. Impacto e taxas já integram o PnL; não subtrair novamente. Limites de entrada/exposição são verificados na admissão; a exposição marcada pode variar com o preço. Travas bloqueiam novas entradas, sem garantir que drawdown observado nunca ultrapasse o limiar.

## Fixture e oráculos independentes

Fixture versionada com 1010 candles (960 score), split 576/192/192, 50 candles de aquecimento a 100 e dez repetições `[100]x50+[110]+[100]x45`. Não é mercado real. Matriz: 56 fills em desenvolvimento, 24 na validação e 24 no teste; replay 0. SMA/base: 9976.07182114 / 9992.01757038 / 9992.01757038 USDT. Essas curvas compram o open posterior e não são o controle isolado abaixo.

| Controle | Esperado | Obtido |
|---|---:|---:|
| Quantidade BUY referência 110 |9.072754 BTC|9.072754 BTC|
| Preços BUY/SELL |110.11/99.90|110.11/99.90|
| Taxas BUY/SELL |0.99900095/0.90636813|0.99900095/0.90636813|
| PnL negativo | -94.53818742 USDT| -94.53818742 USDT|
| Saldo após o ciclo |9905.46181258 USDT|9905.46181258 USDT|
| Controle positivo: saída referência 120 |10086.55416388 USDT|10086.55416388 USDT|

Alta/baixa/lateral sintéticas, igualdade, zero cruzamentos/trades, mínimos, preço/custos inválidos, orçamento, risco e expiração foram exercitados. Primeira execução sem fills é identificada por eventos confirmados, e não confundida com reprodução.

## Aceite

| ID | Tema | Resultado |
| --- | --- | --- |
| AC01 | Protocolo/split/consumo final | APROVADO - 3 segmentos, mesmo hash; dev/val completos antes do teste; reprodução sem novos efeitos |
| AC02 | Causalidade e relógio | APROVADO - Prefixo independente do futuro; referência posterior +1 ms e fill +2 ms; atraso de um candle |
| AC03 | Precisão/custos/ledger | APROVADO - Oráculos exatos negativos/positivos; núcleo financeiro e BID_ASK compartilhados; quatro variantes |
| AC04 | Integridade/idempotência | APROVADO - Hashes/CRC/gaps/duplicatas/limites/tipos; resultado canônico estável no replay |
| AC05 | OOS/benchmarks | APROVADO - 48 curvas reais e 48 técnicas, capital independente, quatro variantes e três referências |
| AC06 | Isolamento | APROVADO - Guards em pytest/filhos/wheel; transporte público não construído pelo backtest |
| AC07 | Propriedade/risco | APROVADO - Opt-in exclusivo; contexto financeiro derivado do protocolo; benchmarks sem bypass da SMA |
| AC08 | Regressão/defaults | APROVADO - 428 históricos preservados; NOOP sem carteira; configuração estrita e diretórios separados |
| AC09 | Fronteiras | APROVADO - Aquecimento sem posição herdada; END_OF_WINDOW; terminal marcado sem venda implícita |
| AC10 | Pendência/admissão | APROVADO - Slot lógico sem reserva; prioridade, orçamento/filtros/risco revalidados; A e B separados |
| AC11 | UTC/métricas | APROVADO - Baseline causal antes do novo open; MDD integral e exposição/posição ponderadas em ms |
| AC12 | Recuperação | APROVADO - Mortes reais no agendamento, A/B, início/fim e publicação; retry equivale à execução íntegra |
| AC13 | Concorrência/corrupção | APROVADO - Flock/CAS/PK/FK/triggers; divergência duravelmente bloqueada, sem reparo por diferença |
| AC14 | Escala/compatibilidade | APROVADO - 70130 candles; janela máxima de 51 candles; medições preservadas; bancos anteriores rejeitados sem migração |
| AC15 | Relatórios | APROVADO - HTML/JSON/CSV/manifestos conferidos; risco/recusas/parciais/N/A; PDFs revisados; exportação em leitura |
| AC16 | Qualidade/pacote | APROVADO - Ruff/format/mypy strict/pytest branches/build/wheel site-packages/guard aprovados |
| AC17 | Documentação | APROVADO - SMA/catálogos, banco/DDL/ER/ADRs, arquitetura/planejamento e evidências alinhados |
| AC18 | Gate da avaliação | APROVADO - Histórico real verificado e teste separado; sem liberação LIVE ou início da 06 |

M01-M04: defaults, escopos, validação e isolamento aprovados no alcance histórico. M05-M07: propriedade exclusiva, conflitos/peso/reserva/CAS/risco, incluindo fakes e regressões 04; não aprova composição real. M08: TWAP/VWAP rejeitados, pais/filhos pendentes. M09-M10: sem desativação operacional/hot reload; flags não criam liquidação/reset, mudança de snapshot/protocolo é rejeitada, contratos 04 preservados. M11-M12: dados indisponíveis/corrompidos abortam e atribuição por carteira/instância reconcilia. M13: causalidade/atraso/custos/OOS aprovados; parcial/UNKNOWN real permanece futuro. M14-M15: combinações/modos privados/AWS não habilitados. M16: estratégia/catálogos/DDL/ADR atualizados. Nenhum item futuro foi aprovado a partir de fixture.

## Relatórios, reprodução e operação

[PDF histórico](../output/pdf/sprint-05-avaliacao-historica.pdf), [PDF técnico](../output/pdf/sprint-05-ensaio-tecnico.pdf), [HTML histórico](relatorios/sprint-05/public/report.html), [HTML técnico](relatorios/sprint-05/fixture/report.html) e [índice dos artefatos](relatorios/sprint-05/README.md). HTML/JSON/CSV/manifesto são publicados automaticamente após cada segmento; report reexporta snapshot reconciliado em leitura, sem novos sinais/fills. PDFs adicionais foram produzidos com ReportLab fora das dependências do bot e revisados por renderização Poppler. O [gerador](ferramentas/sprint-05-relatorio-pdf.py) é reproduzível a partir do report.json original.

Comandos efetivos e saídas integrais: `/home/cams7/Dev/Cripto/cripto-bot/reports/sprint05-delivery-xbna6gyh`. Configuração real preservada em `/home/cams7/Dev/Cripto/cripto-bot/reports/sprint05-public-k65d2lo0/config.toml`. Export final real: `/home/cams7/Dev/Cripto/cripto-bot/data/backtest-btc-audit-v1/exports/2423b43c-ead9-4937-8b93-f41e423a9cd1`. JSON/equity/trades/decisions completos permanecem nesse export; a cópia documental mantém links relativos para os arquivos operacionais, evitando versionar bancos ou CSVs de grande volume. Manifestos documentais distinguem o hash da cópia do HTML do hash original; conteúdo de métricas/gráficos não foi alterado. O result_sha256 identifica o JSON canônico completo, não o subconjunto documental sem chart.

```bash
uv sync --locked --group dev
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy modules/trading/src
uv run --locked pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
uv build
uv run --locked python tests/wheel_smoke.py
uv run --locked cripto-bot backtest-prepare --config config/backtest.sma.fixture.toml
uv run --locked cripto-bot backtest-freeze --config config/backtest.sma.fixture.toml
uv run --locked cripto-bot backtest-run --config config/backtest.sma.fixture.toml --segment development --variant all
uv run --locked cripto-bot backtest-run --config config/backtest.sma.fixture.toml --segment validation --variant all
uv run --locked cripto-bot backtest-run --config config/backtest.sma.fixture.toml --segment test --variant all
uv run --locked cripto-bot backtest-reconcile --config config/backtest.sma.fixture.toml
uv run --locked cripto-bot backtest-report --config config/backtest.sma.fixture.toml
```

O teste final foi repetido exatamente com zero novos fills e mesmo hash; não é nova amostra intocada. Depois de mudança material, não tentar consumir novamente a mesma janela real com novo ID. Relatórios parciais mostram checkpoint/PARCIAL e denominadores ausentes como N/A/null. Corrupção bloqueia; não excluir ledger ou ajustar saldos para passar.

SQLite histórico schema 1/modelo paper-backtest-v1, FULL/WAL, 18 triggers e três índices de sequência foram confrontados com a introspecção real: 48 curvas completas, FKcheck/quick_check sem divergência e fill=atribuição. A conexão de leitura usa foreign_keys=ON e snapshot; pragmas e DDL detalhados em [banco](../bancos/backtest-sqlite.md). HOLDs/marcações podem compartilhar até 64 eventos com journal/cursor/projeção juntos. SCHEDULED/A/B/END confirmados separadamente; nenhum resultado é publicado antes do commit.

CPU/disco/rede pública locais; AWS: zero, sem capital/taxas reais. Sem commit, staging, deploy, publicação remota ou mensagens. Limites econômicos: uma estratégia/par/intervalo, janela de 24 meses, filtros e fill integral proxy, sem liquidez intrabar ou garantias futuras. Bibliotecas opcionais, execução contínua/privada, migração e novas estratégias permanecem fora da entrega.
