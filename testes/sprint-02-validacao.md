# Sprint 02 — Guia e registro de validação

Data: 24/10/2026, America/Sao_Paulo.

**Resultado: APROVADA na validação local offline para AC01–AC17. Coleta pública real: NÃO EXECUTADA.** A Sprint 03 não foi iniciada. Nenhuma ordem, notificação ou operação AWS foi realizada.

## 1. Diretórios e base inspecionada

- Workspace: `/home/cams7/Dev/Cripto`.
- **Diretório de execução de todos os comandos Python/uv: `/home/cams7/Dev/Cripto/cripto-bot`.**
- Documentação central: `/home/cams7/Dev/Cripto/docs`, repositório independente.

Revisões de base: aplicação `2224caf97d694fb0fe9fca78c29b14c8e44c7b06`; documentação `a36baf95828692b24a3f256590060a6bd2f1d2ed`. A aplicação estava sem alterações no início; `planejamento.md` alterado e `sprints/sprint-02.md` ainda não rastreado em docs foram preservados. Nenhum commit foi criado nesta execução.

Os 14 hashes registrados nas evidências 01 conferiram antes da implementação. A regressão inicial passou com 79 testes. As alterações desta Sprint acrescentam transporte, configuração de mercado, coleta, SQLite e exportação ao mesmo módulo; não criam repositório adicional.

As [evidências JSON](sprint-02-evidencias.json) registram comandos, resultados, versões, estado local da aplicação, hashes dos fontes, relatórios de cobertura, manifestos e resultados do wheel. Os testes finais foram registrados a partir de sua execução real; a suíte não foi repetida apenas para gerar o JSON.

## 2. Ambiente e preparação

| Componente | Versão verificada |
|---|---|
| Python | 3.13.15 |
| uv | 0.12.19 |
| setuptools no build | 84.2.0 |
| HTTPX / httpcore | 0.28.1 / 1.0.9 |
| anyio | 4.15.1 |
| Pydantic | 2.14.1 |
| pytest / pytest-cov | 9.1.1 / 7.1.0 |
| coverage | 7.17.0 |
| Ruff / mypy | 0.17.2 / 1.20.2 |

Foram acrescentadas seis entradas ao lock: HTTPX e cinco dependências, sem atualizar as versões anteriores. Demais pins e hashes estão em `uv.lock`. A compatibilidade foi demonstrada no Linux/Python local, sem teste de runtime AWS.

São necessárias permissões de escrita na aplicação e em docs. A implementação usou a escalada permitida para escrever no módulo fora de docs. Dependências foram baixadas do índice; isso não equivale a uma coleta Binance.

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR=/home/cams7/Dev/Cripto/.uv-cache
uv --version
uv sync --locked --group dev
uv run --locked python --version
```

O cache acima é local ao workspace e já existia; ambientes ficam no módulo. O lock foi atualizado deliberadamente com `uv lock` após adicionar HTTPX. Para repetir os testes, manter `--locked`; não regenerar o lock sem necessidade. Caso o pyenv avise que 3.13.15 não está instalado nele, conferir o interpretador usado pelo uv conforme o [guia 01](sprint-01-validacao.md), sem alterar o pin automaticamente.

## 3. Verificações de qualidade executadas

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR=/home/cams7/Dev/Cripto/.uv-cache
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy modules/trading/src
uv run --locked pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
uv build --quiet
```

Todos retornaram 0. Resultado final: **204 testes aprovados em 8,00 s**, Ruff sem achados, 40 arquivos Python formatados e mypy sem problemas em 21 fontes. O build gerou sdist e wheel; os arquivos foram inspecionados e não contêm ambientes/cache/datasets locais nem harness de testes no wheel.

Cobertura da aplicação: 729 de 736 statements (**99,05%**), 196 de 200 branches (**98%**), combinado **98,82%**, exibido como **99%** no relatório. Não confundir o arredondamento com cobertura total.

Os parsers/fluxo de coleta têm os cenários exigidos exercitados; aplicação e CLI de coleta possuem cobertura integral nos relatórios finais. As sete linhas não exercitadas são: fallback defensivo após o laço de retries, tratamento de manifest de projeto ilegível/malformado na descoberta da raiz, fallback Git ausente, resultado não-ok do quick_check e conversor auxiliar de milissegundos para texto UTC. A corrupção real simulada foi detectada pelo SQLite antes do quick_check; a perda de Git não afeta a integridade do dataset. Os quatro ramos parciais pertencem a essas defesas e ao fechamento de um store não aberto; não são exclusões de rejeição de modo, credenciais, conflitos, rollback ou retry.

Não foram acrescentados pragmas ou regras manuais de exclusão de código. O relatório mantém as exclusões padrão do coverage, incluindo assinaturas de Protocol com `...`; os totais estão no JSON. `.pytest-tmp` foi configurado dentro do módulo para dados temporários dos testes e ignorado pelo Git/Ruff.

## 4. Coleta sintética e repetição

Exemplo executado, sem `--allow-network`:

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR=/home/cams7/Dev/Cripto/.uv-cache
uv run --locked cripto-bot check-config --config config/market.fixture.example.toml
uv run --locked cripto-bot collect-market --config config/market.fixture.example.toml --start 2026-10-01T00:00:00Z --end 2026-10-01T00:30:00Z
uv run --locked cripto-bot collect-market --config config/market.fixture.example.toml --start 2026-10-01T00:00:00Z --end 2026-10-01T00:30:00Z
```

Configuração versionada:

```toml
mode = "PAPER"

[market]
source = "fixture"
symbol = "BTCUSDT"
interval = "15m"
fixture_file = "config/fixtures/market-sample.json"
data_dir = "data/market-fixture"
page_limit = 1000
max_pages = 10
```

Paths relativos são resolvidos pelo diretório de execução, mesmo com `--config` absoluto. O root do módulo é descoberto pelo manifest nos ancestrais do cwd. Paths resolvidos, inclusive symlinks, precisam permanecer no módulo. `check-config` não cria banco, abre fixture ou acessa rede.

| Execução real | Exit | Inseridos | Próxima abertura | Resultado |
|---|---|---|---|---|
| `28466e9f-82ab-481c-9b1b-14e868befa1e` | 0 | 2 | `1790814600000` / 01/10/2026 00:30 UTC | COLLECTED, complete=true |
| `f0b9c64b-dd5a-457b-afe9-7c86a107e8f6` | 0 | 0 | mesmo valor | COLLECTED, complete=true |

Ambas retornaram `mode=PAPER`, `orders_sent=0`, símbolo/intervalo/janela, dataset e manifesto, com `run_id` correlacionado entre stdout/stderr. Cada stdout é um objeto JSON; eventos JSON Lines ficam em stderr. O resultado atual ao repetir novamente será zero inseridos, porque o dataset foi preservado.

Identidade da fixture: `15e238d7bac0bd9dd2d004dec2c0e82078aec4f0b30a60e916778f124bf0d426` (SHA-256). O banco `data/market-fixture/market.sqlite3`, schema v1, tem dois candles. O checkpoint da janela passou de abertura 00:00 para 00:30 UTC.

Hash canônico dos candles em ambas as exportações:

```text
fec39ffcbf53d685fcd5606a51585e364c6dbecd06b991d0dabc4722e04aa74d
```

Os manifestos permanecem em `data/market-fixture/exports/<run_id>/manifest.json`, com cópias no JSON de evidências. Todos os hashes dos arquivos exportados foram conferidos, e cada corpo bruto Base64 foi decodificado e comparado ao seu SHA-256.

O hash canônico cobre candles ordenados e strings decimais normalizadas. Tempos de recebimento/processamento, raw_id e run_id ficam fora dele, em `provenance.json`, nos registros brutos e nos metadados do manifesto. Assim, é possível comparar os dados sem exigir o mesmo relógio ou identidade de execução.

## 5. Wheel instalado em ambiente separado

O ambiente `.venv-wheel` da Sprint 01 foi reutilizado com **reinstalação** do wheel final; não foi usada sua instalação anterior. Dependências de produção foram exportadas do lock e conferidas na instalação.

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR=/home/cams7/Dev/Cripto/.uv-cache
uv build --quiet
mkdir -p .wheel-smoke
uv export --locked --no-dev --no-emit-project --format requirements-txt --output-file .wheel-smoke/requirements-sprint02.txt
uv pip install --reinstall --python .venv-wheel/bin/python --requirement .wheel-smoke/requirements-sprint02.txt dist/cripto_bot-0.1.0-py3-none-any.whl
uv run --locked python tests/wheel_smoke.py
```

Para ambiente novo, executar antes `uv venv --python 3.13.15 .venv-wheel`. O comando de criação não foi repetido nesta Sprint porque o ambiente já existia.

- Wheel validado: `cripto_bot-0.1.0-py3-none-any.whl`.
- SHA-256 final: `310377e7b0ed88ed1754963e39a529ba241e4aa101effa5c866c7b0f0133e008`.
- Importação: `/home/cams7/Dev/Cripto/cripto-bot/.venv-wheel/lib/python3.13/site-packages/cripto_bot/__init__.py`.
- Execução em `.wheel-smoke`, sem PYTHONPATH do checkout, com `-I`, paths absolutos de fixture/dados e audit hook de sockets.
- `check-config` e `run-once` preservados; duas coletas inseriram 2 e 0 candles; LIVE rejeitado com código 2; probe de socket bloqueado com `NETWORK_BLOCKED`.

O smoke test cria diretório novo a cada execução, preservando sua inspeção e evitando interpretar uma coleta antiga como a primeira. Ele usa arquivos de configuração/fixture externos ao wheel, com paths explícitos. Não importa fontes por PYTHONPATH. Rebuilds futuros podem mudar o hash; registrar o wheel exato usado.

## 6. Matriz AC01–AC17

| Critério | Evidência executada | Resultado |
|---|---|---|
| AC01 | 79 testes anteriores preservados na suíte de 204; NOOP com configuração de mercado também testado | Aprovado |
| AC02 | CLI em subprocesso e wheel sob guard, com janela de dois candles e repetição | Aprovado |
| AC03 | Sentinelas em cliente/store, opt-in ausente, fixture com opt-in, modo/credenciais e paths proibidos | Aprovado |
| AC04 | Fixture de 1001 candles; duas páginas, cursor e limite de página conferidos | Aprovado |
| AC05 | Aberto descartado, fechamento exato aceito e janela futura rejeitada | Aprovado |
| AC06 | Decimal/float/bool/NaN, schema, JSON inválido, encoding, OHLC e UTC/offset/alinhamento | Aprovado |
| AC07 | Lacuna, desordem, vazio, dado fora da janela e página maior que o limite não avançam | Aprovado |
| AC08 | Duplicatas dentro da página e entre janelas, repetição completa e conflito sem sobrescrita | Aprovado |
| AC09 | Processo morto antes do commit da página: zero raw/candles/checkpoint; depois: página recuperada inteira | Aprovado |
| AC10 | Falha de rename e escrita de manifesto, limpeza de temporário, banco preservado e reexportação | Aprovado |
| AC11 | Dois stores simultâneos rejeitados pelo flock; namespaces/inícios distintos; liberação por morte real | Aprovado |
| AC12 | Timeout/5xx limitados, 429 com espera simulada, 418 sem retry, ban persistido e deadline | Aprovado |
| AC13 | Host/método/rota/assinatura/auth/símbolo proibidos barrados antes do transporte; redirects rejeitados | Aprovado |
| AC14 | Metadados Spot/filtros aditivos, quote validada e market_timestamp=null | Aprovado |
| AC15 | Hashes de bruto/candles/arquivos, proveniência e hash canônico igual na repetição | Aprovado |
| AC16 | Banco corrompido/schema estranho sem recriação, registros/checkpoint inconsistentes, symlink rejeitado | Aprovado |
| AC17 | Ruff, formatação, mypy strict, 204 testes, build e wheel isolado | Aprovado |

Os testes HTTP utilizam MockTransport. O fixture autouse bloqueia sockets no pytest; o harness bloqueia eventos `socket.*` nos filhos, incluindo probes e processos mortos deliberadamente. O opt-in usado no teste do adapter público tem transporte em memória, sem acesso real.

## 7. Falhas, diagnóstico e recuperação

Durante a implementação, uma consulta de integridade SQLite tinha coluna `sha256` ambígua entre tabelas e fez a primeira coleta sintética falhar com código 3. A coluna foi qualificada; testes de persistência, integridade e CLI passaram após a correção. A falha inicial não foi contada como aprovação e não havia confirmado candles naquela tentativa. Achados de tipagem/formatação também foram corrigidos antes dos checks finais.

| Sintoma | Ação |
|---|---|
| Exit 2 / INVALID_CONFIG | Conferir modo, campos, janela UTC, caminhos e opt-in; não tentar outro host/modo |
| Exit 3 / DATA_GAP, conflito ou NO_PROGRESS | Preservar bruto de rejeição e checkpoint; investigar, sem inventar candle ou sobrescrever |
| Falha após páginas confirmadas | Repetir mesma fonte/início; verificar prefixo e retomar próximo candle |
| Falha de exportação | Preservar banco; reexportar pela repetição da janela; não anunciar diretório temporário como completo |
| WRITER_BUSY | Aguardar o escritor terminar; não remover lock de um processo vivo |
| IP_BANNED / SOURCE_BLOCKED | Respeitar not_before; não usar outro diretório/host/IP para contornar bloqueio |
| Banco corrompido ou schema incompatível | Preservar cópia para diagnóstico; interromper sem recriar no mesmo caminho |

Convenções explicitadas na implementação: erro de formato/alinhamento/capacidade da janela retorna 2 antes dos adapters; janela que excede o fechamento conhecido só pode ser detectada após consultar a fonte e retorna 3 (`WINDOW_NOT_CLOSED`). O registro da restrição pública vale para o mesmo SQLite/data_dir, sem coordenação distribuída. O schema mantém símbolo/intervalo fixos da Sprint e por isso sua chave não aceita generalização para outros pares sem nova decisão.

## 8. Limites e verificações não executadas

**Coleta pública real: NÃO EXECUTADA**, pois não foi solicitada separadamente. Não foi comprovada conectividade regional ou elegibilidade de uso a partir da máquina/conta. Isso não reprova os contratos offline desta Sprint.

Não foram executados AWS, Testnet, ordens, notificações, estratégia ou carteira. O orçamento é verificado antes/depois de chamadas e durante leitura/esperas; não constitui SLA contra travamento do sistema operacional/disco. Os ensaios de morte são de processo, não de perda de energia, dispositivo físico ou filesystem remoto. O audit hook não é um firewall para programas arbitrários.

Raw/snapshots exportados incluem o histórico capturado do dataset no banco; candles e proveniência são limitados à janela do manifesto. Um diretório pode conter datasets distintos e restrição de fonte compartilhada. Exportar novamente pode acrescentar snapshots de metadados e recebimentos diferentes, mantendo idêntico o hash dos candles.

## 9. Limpeza e custos

AWS: **zero recursos criados e custo AWS zero**. Houve apenas uso local de disco/CPU e downloads de dependências.

Os dados de demonstração, temporários e ambientes foram preservados para inspeção. `data/`, `reports/`, `.pytest-tmp/`, bancos/locks e artefatos locais estão ignorados pelo Git; fixtures em `config/fixtures` continuam versionáveis.

Após inspecionar o que foi criado, podem ser removidos datasets sintéticos específicos, diretórios `.wheel-smoke/market-*`, cache/temporários e relatórios gerados. Banco/bruto/checkpoint são evidência durante diagnóstico; não os apagar como primeira recuperação. Não remover outros datasets, `.git`, fontes, lock de dependências, fixtures ou documentos. Nenhum commit, remoto ou publicação foi feito nesta execução.

## 10. Fontes e conclusão

Os contratos oficiais foram reconfirmados em 24/10/2026: [Binance host público](https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md), [mercado](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market), [gerais](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general), [limites](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#limits), [HTTPX transportes](https://www.python-httpx.org/advanced/transports/), [timeouts](https://www.python-httpx.org/advanced/timeouts/) e [sqlite3](https://docs.python.org/3.13/library/sqlite3.html). Ver [ADR 0003](../decisoes/0003-coleta-publica-e-persistencia-local.md).

Implementação local concluída e matriz offline aprovada com as limitações registradas. A revisão de entrega pode usar os fontes, as evidências JSON e este guia. A próxima ação é revisar essas evidências antes de detalhar a Sprint 03; esta entrega não a inicia nem promove qualquer modo operacional.

## Adendo documental de 25/10/2026 — validações antes de LIVE

O aceite registrado neste documento permanece restrito ao escopo histórico executado. Ele não comprova backtest fora da amostra, PAPER contínuo, Demo Spot, Spot Testnet ou `POST /api/v3/order/test`. A sequência e os gates atualizados estão no [planejamento, seção 10](../planejamento.md#10-gates-entre-ambientes-e-modos) e no [roteiro de validação](../testes/validacao-pre-live.md). Demo passa à Sprint 09, Testnet complementar à 10 e preparação LIVE à 11, sem ativação. A implementação desta Sprint continua exclusivamente PAPER; DEMO/TESTNET/LIVE não são liberados por esta revisão.

Nenhum teste foi repetido e nenhuma evidência JSON foi alterada por este adendo. A solicitação atual autoriza somente revisão documental. LIVE permanece bloqueado por padrão e exige validações concluídas, limites de risco reais e aprovação explícita vigente do responsável.

## Referência documental do banco — revisão de 25/10/2026

O DDL existente foi documentado em [bancos/market-sqlite.md](../bancos/market-sqlite.md), com diagrama relacional, constraints, operação e rejeição de schemas incompatíveis. Esta revisão foi leitura de fonte, sem abrir bancos, executar migrations ou repetir testes; não amplia o aceite histórico. Qualquer futura mudança estrutural exige atualização desse documento e do [catálogo](../bancos/README.md), com verificação/evidências na Sprint responsável, conforme seção 4.8 do planejamento.
