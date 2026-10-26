# Validação da Sprint 06B

Execução: 26/10/2026. **APROVADA no escopo offline: B01–B18, documentação e revisão visual registrados nas [evidências](sprint-06b-evidencias.json).** O roteiro foi criado pendente antes dos testes; B-M1 precedeu extração, B-M2 precedeu integração. [Especificação](../sprints/sprint-06b.md), [ADR 0009](../decisoes/0009-market-data-e-proveniencia-do-produtor.md) e [relatório legível](relatorios/sprint-06b/report.html).

## Composição e baseline

Raiz `/home/cams7/Dev/Cripto`; projetos Git independentes. Bot HEAD `a9dde2e93043be3aa11c603a2b46c60a59e4a174`; core HEAD `e666e7e23dcb421177c80838a28c230d4433bdf2`; docs HEAD `edfa405aa7558d1efa3493f2f0e5f557c6999eaf`. Alterações documentais anteriores preservadas. Novo market-data com branch main, sem commit/remoto. Esta execução não fez commits em nenhum projeto.

Os 127 hashes de fontes/controles e seis artefatos da 06A foram conferidos antes de extrair. O archive Git do bot preserva aquela fonte; conferência final repete seus hashes no archive e verifica diretamente os arquivos do core. Core permanece limpo, inclusive wheel/lock/pins; seus 54 testes são resultado histórico 06A, não reexecução nesta etapa. Novos fontes, testes, controles, artefatos e provas possuem hashes no JSON.

Python 3.13.15, uv 0.12.19, setuptools 84.2.0. Core e market-data exatos 0.1.0; bot continua 0.1.0 com artefato distinto em `dist/06b-final`. Todos os 27 pacotes da composição anterior mantêm versão no lock do bot; somente market-data foi acrescentado. Não substituir wheels 06A por arquivos 06B, embora as versões dos pacotes sejam iguais; selecionar composição por caminho e hash.

## Execuções e resultados

| Marco | Evidência efetivamente obtida | Resultado |
|---|---|---|
| B-M1 | Ruff/check-format/mypy; bot 533 testes, 565,318 s; smoke anterior 22 comandos, archive/store sintéticos preservados | Aprovado às 13:33:52 UTC |
| B-M2 | Ruff/check-format/mypy (21 fontes); market-data 120 testes, 3,887 s; wheel/CLI sem bot ou DuckDB, cinco comandos e probe de sockets; store anterior e lock cruzado | Aprovado às 13:44:18 UTC |
| B-M3 | Ruff/check-format/mypy (59 fontes); bot 537 testes, 561,849 s; build e smoke 22 comandos com três wheels, provas adicionais de compatibilidade/CLIs | Aprovado; revisão documental/visual no JSON |

Cobertura combinada de linhas/ramificações: baseline bot 93,42%; bot final 92,63%; market-data 95,79%. Os denominadores mudaram com a extração; a cobertura do bot não inclui o código do wheel de dados. Não somar suítes nem atribuir os testes duplicados de contratos a funcionalidades novas. Ensaios direcionados de contratos (130 testes) e composição (9 testes) precederam a suíte completa; já estão nela incluídos.

Logs em `cripto-bot/reports/sprint06b/{baseline,final}` e `cripto-market-data/reports/sprint06b/standalone`; resultados XML/JSON preservados. B01–B18 possuem matriz de provas com caminhos relativos ao workspace no JSON. O relatório deriva desses resultados; não recalcula estratégia.

## Reprodução offline e instalação

Na raiz de cada projeto, comandos de qualidade utilizados:

```bash
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
```

`uv lock --offline` foi executado deliberadamente para criar o lock da biblioteca e incorporar sua dependência no bot. Depois, comandos locked. Suítes finais:

```bash
# Em cripto-market-data
uv run --locked --offline pytest -q --cov=cripto_market_data --cov-branch --cov-report=json:reports/sprint06b/standalone/coverage.json --junitxml=reports/sprint06b/standalone/pytest.xml
uv build --offline --out-dir dist/06b-final
# Em cripto-bot
uv run --locked --offline pytest -q --cov=cripto_bot --cov-branch --cov-report=json:reports/sprint06b/final/coverage.json --junitxml=reports/sprint06b/final/pytest.xml
uv build --offline --out-dir dist/06b-final
```

O wheel market-data foi construído/validado antes de entrar no manifest/lock do bot. Smokes: `.venv-standalone-06b` em dados e `.venv-wheel-06b` no bot, sem reutilizar o ambiente final 06A. Criados com `uv venv --offline`; requisitos exportados dos locks excluindo distribuições próprias. O cache externo completo não estava disponível: utilizou-se [helper verificado da 06A](ferramentas/sprint-06a-reuse-dependencies.py), com argumentos ambiente fonte, ambiente destino e arquivo de requisitos. Fonte: bot `.venv-wheel-06a-final`; requisitos/saídas RECORD e versões em `runtime-reuse.json`/logs dos dois projetos. O helper copia apenas distribuições travadas, verifica hashes e ajusta shebang/RECORD dos scripts copiados. Wheels próprios instalados com `uv pip install --offline --no-deps --python <ambiente>/bin/python <wheels>`. Instalação completa com cache frio **não demonstrada**.

```bash
# Em cripto-market-data, após preparar o ambiente e instalar core+dados:
.venv/bin/python tests/wheel_smoke.py --python .venv-standalone-06b/bin/python
# Em cripto-bot, após instalar core+dados+bot:
WHEEL_SMOKE_STAGE=06b uv run --locked --offline python tests/wheel_smoke.py
# Provas adicionais, em cripto-bot:
.venv/bin/python ../docs/testes/ferramentas/sprint-06b-compatibilidade.py
.venv/bin/python ../docs/testes/ferramentas/sprint-06b-clis.py
# Consolidar evidências/relatório, em docs:
python testes/ferramentas/sprint-06b-evidencias.py
python testes/ferramentas/sprint-06b-relatorio.py
```

Os smokes executam console scripts sob `python -I`, cwd neutro e audit hook que rejeita eventos socket; probe comprova bloqueio. Origem efetiva dos três pacotes é site-packages, validada via RECORD. Standalone comprova ausência de bot/DuckDB. Ambiente negativo instala apenas core+bot sem dependências: import do mercado falha explicitamente por `cripto_market_data` ausente. Versão errada, editable e conteúdo/RECORD alterado são rejeitados nos testes de composição.

## Dados, invariantes e falhas

Fonte única para DTOs/MarketSettings/MarketInput/portas/paginação/workflow/store/export; bot conserva aliases e seu wrapper/configuração global. Nenhuma migração física. Comparação AST do DDL e classe SQLiteMarketStore: idênticos à baseline. Arquivos paper_sqlite/strategy_sqlite/backtest_sqlite: bytes idênticos. IDs de dataset, schema v1, parser e quatro arquivos de dados do manifesto preservados. Proveniência de bot e standalone identifica cada produtor; schema financeiro/ledger/flags permanecem no bot.

Fixture: primeira coleta insere dois candles; repetição insere zero. Hash normalizado `fec39ffcbf53d685fcd5606a51585e364c6dbecd06b991d0dabc4722e04aa74d`. Store criado pelo código anterior abre com biblioteca nova, preservando schema/candles/checkpoint. Três replays alternados bot → dados → bot mantêm dataset/hash e zero inserções; lock mantido por store bloqueia ambas as CLIs com saída 3/WRITER_BUSY. Testes incluem concorrência, rollback/morte de processo, publicação incompleta, repetição, orçamento/retry/429/418 e restrição not_before; rejeições usam fixtures/MockTransport, sem rede real.

Root da CLI de dados é absoluto, existente e contido no workspace; caminhos resolvem o cwd e precisam ficar na raiz, inclusive symlinks. `check-config` não cria store/cliente; tabelas extras, credenciais (mesmo vazias), modos/par/intervalo e paths inválidos são rejeitados. Fonte pública sem opt-in e fixture com opt-in falham antes de efeitos. Apenas quatro GETs já previstos; HTTPX mantém TLS/no-proxy/no-redirect, orçamento e guard de método/host/auth.

Novo manifesto coletado com 1.010 candles passa no prepare existente (50 warmup + 960 score). Sem alteração de motor/limites/estratégia. O teste de composição incluiu ajuste na preparação da fixture, que inicialmente não cobria o warmup e falhou corretamente com DATASET_GAP; o produto não foi flexibilizado.

Oito respostas PAPER/SMA mantêm hashes financeiros anteriores. Saldo manual `10009.58001000`, SMA `9905.46181258`, 71 ciclos, replay sem novos fills. As 48 curvas sintéticas completas têm igualdade de métricas, chart, limites, motivos e períodos; excluídos somente `run_key` e `checkpoint_bytes`, afetados pela identidade. Hash global de protocolo/resultado muda legitimamente. Esses resultados retrospectivos sintéticos comprovam regressão técnica; não representam nova evidência econômica fora da amostra ou garantia futura.

Alterar somente market-data muda fingerprint e impede verify/resume do protocolo congelado. Protocolo sintético anterior reexporta em backtest-report com mesmo result_sha256 e SQLite byte a byte intacto; tentativa de executar retorna 3/FROZEN_PROTOCOL_CHANGED. Registro final real preservado: SHA-256 `af7ee92659cb1be9c4e322daeba997755430a040faec4b1342c1cabf082810bd`. Nenhuma janela final real foi consumida novamente.

## Custos, limites e recuperação

Suítes principais: aproximadamente 9min25s baseline, 9min22s bot final e 3,9s biblioteca. Medição `du -sk` antes do fechamento documental: reports bot 3.056 KiB, dados 344 KiB; artefatos bot 180 KiB, dados 68 KiB. Stores/exports sintéticos isolados do smoke não estão incluídos nesses reports. Pico de memória não instrumentado; não é benchmark de throughput. Custo externo zero; CPU/disco locais, sem AWS, mensagens, coleta real ou operações privadas.

Preservar archives, stores sintéticos, wheels/locks e logs de cada marco. Rollback deve restaurar arquivos/manifest/lock compatíveis da composição bot+core anterior e seu wheel, com revisão do trabalho posterior; não executar reset amplo. Dados/store/checkpoints/locks/ledger e registro final permanecem. Identidades seladas antigas não autorizam execução sob código novo; leitura histórica continua possível. Não apagar bancos para contornar rejeição.

A documentação de biblioteca/bot, arquitetura/ADRs, catálogos/bancos e SMA foi atualizada nesta entrega. Revisão visual, hashes e decisão B17/B18 constam nas evidências. 06C fica elegível somente para detalhamento/revisão; 06D, gate global 06, 07 e trilha BT continuam pendentes. Nenhuma autorização de implantação ou operação real resulta deste aceite.

Fontes primárias reconfirmadas em 26/10/2026: [HTTPX/MockTransport](https://www.python-httpx.org/advanced/transports/), [uv/dependency sources](https://docs.astral.sh/uv/concepts/projects/dependencies/), [Python 3.13/sqlite3](https://docs.python.org/3.13/library/sqlite3.html), [Binance/data-only host](https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md). Não houve consulta à API de mercado.
