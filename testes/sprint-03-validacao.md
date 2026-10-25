# Sprint 03 — Guia e registro de validação

Data: 24/10/2026, America/Sao_Paulo.

**Resultado: APROVADA na validação local offline para AC01–AC18.** Carteira, ledger, reservas, risco e fills são simulados. Nenhuma coleta externa, ordem real, notificação, recurso AWS ou Sprint 04 foi executado.

## 1. Diretórios, revisões e dependências

- Workspace: `/home/cams7/Dev/Cripto`.
- **Diretório dos comandos Python/uv: `/home/cams7/Dev/Cripto/cripto-bot`.**
- Documentação central: `/home/cams7/Dev/Cripto/docs`, com Git independente.

Base da aplicação: `a102223e66be024f540a796c67094fcd4e6e138f`. Base da documentação: `552b3f27b5fab7edbc157308753b497028e69f82`. A aplicação estava sem alterações no início; alterações de planejamento e a especificação 03 ainda não rastreada em docs foram preservadas. Nenhum commit ou remoto foi criado nesta execução.

Os 24 hashes da Sprint 02 conferiram antes das mudanças; a regressão inicial passou com 204 testes. Os comandos anteriores permanecem na suíte final e no smoke test do wheel. O store financeiro é separado: o schema do banco de mercado não foi alterado.

Versões verificadas: Python 3.13.15, uv 0.12.19, Pydantic 2.14.1, HTTPX 0.28.1, pytest 9.1.1, pytest-cov 7.1.0, coverage 7.17.0, Ruff 0.17.2, mypy 1.20.2 e backend setuptools 84.2.0. Nenhuma dependência nova ou mudança de manifest/lock foi necessária.

A escrita no módulo fora de docs usou a escalada permitida do ambiente. A reinstalação do wheel/dependências pode acessar o índice; a execução financeira e os testes permanecem offline. O Python utilizado é descoberto pelo uv; aviso do shim pyenv não significa ausência do interpretador gerenciado pelo uv, conforme o [guia 01](sprint-01-validacao.md).

## 2. Preparação e checks executados

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR=/home/cams7/Dev/Cripto/.uv-cache
uv --version
uv sync --locked --group dev
uv run --locked python --version
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy modules/trading/src
uv run --locked pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
uv build --quiet
```

Todos retornaram 0. Resultado final: **316 testes aprovados em 14,95 s, sem avisos**, Ruff sem achados, 63 arquivos Python com formatação verificada e mypy sem problemas em 35 fontes. Sdist e wheel foram inspecionados: não incluem dados/ambientes locais; o wheel não inclui harness de testes.

Cobertura: 1631/1654 statements (**98,61%**) e 504/522 branches (**96,55%**); combinado **98,12%**, exibido como 98%. O redutor financeiro, cálculo de execução/filtros, relatório, fluxo de roteiro e reconciliação têm cobertura integral nos relatórios finais; limites de risco têm statements integrais e uma condição redundante parcial. Não há exclusões manuais novas para mascarar caminhos críticos; assinaturas Protocol mantêm as exclusões padrão da ferramenta.

As lacunas restantes incluem defesas redundantes de store/CAS/schema/modelo, variantes de corrupção antes da leitura completa, falta de metadata num banco inicializado incompleto, entrada não tipada em helpers já protegidos pela fronteira Pydantic, mais de uma pendência impossível pelo redutor, e fallbacks já existentes de descoberta de projeto/Git/transporte. Os números e linhas/ramos exatos estão nas [evidências JSON](sprint-03-evidencias.json). Não afirmar cobertura de 100% da aplicação.

Os cenários críticos de admissão, normalização, reservas, identidade, commit/rollback, concorrência e corrupção foram exercitados conforme a matriz da seção 6. A exportação de cobertura para JSON foi feita depois da suíte final; os testes não foram repetidos apenas para gerar o arquivo de evidências.

## 3. Configuração e demonstração padrão

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR=/home/cams7/Dev/Cripto/.uv-cache
uv run --locked cripto-bot check-config --config config/paper.execution.example.toml
uv run --locked cripto-bot paper-run --config config/paper.execution.example.toml
uv run --locked cripto-bot paper-reconcile --config config/paper.execution.example.toml
uv run --locked cripto-bot paper-report --config config/paper.execution.example.toml
uv run --locked cripto-bot paper-run --config config/paper.execution.example.toml
```

Configuração versionada:

```toml
mode = "PAPER"

[paper]
wallet_id = "paper-demo"
data_dir = "data/paper-demo"
scenario_file = "config/fixtures/paper-roundtrip.json"
initial_usdt = "10000.00"
fee_bps = "10"
spread_bps = "10"
slippage_bps = "5"
max_entry_fraction = "0.10"
max_exposure_fraction = "0.10"
max_daily_loss_fraction = "0.01"
max_drawdown_fraction = "0.05"
max_quote_age_ms = 5000
```

O exemplo foi executado e preservado em `data/paper-demo`. Em uma instalação nova, a primeira execução gera dois fills; no workspace atual, esse diretório já está preenchido, portanto a repetição não gera novos fills. Não apagar a carteira para fabricar uma primeira execução. Para outra experiência, criar configuração/diretório sintéticos novos dentro do módulo.

O cenário possui DAY_START à meia-noite UTC, BUY de 1 BTC e SELL de 1 BTC, com preços REFERENCE 100/110 e regras sintéticas. Decisões antecedem observações e fills; os instantes do replay são de 01/10/2026. Logs operacionais usam UTC real e podem ter data UTC distinta da data local de execução.

## 4. Verificação final em carteira nova

Para distinguir inicialização de replay, a verificação final usou uma carteira nova, sem substituir a demonstração padrão. A configuração efetivamente utilizada está em:

`/home/cams7/Dev/Cripto/cripto-bot/reports/sprint-03-_94qv2ax/execution.toml`

Ela preserva os parâmetros e o cenário do exemplo, mudando somente `data_dir` para seu subdiretório `wallet`. Paths relativos seguem o cwd; nesse arquivo, o diretório da carteira é absoluto. Arquivo e dados foram preservados para inspeção e estão fora do versionamento de fontes.

Comandos executados, todos com código 0:

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR=/home/cams7/Dev/Cripto/.uv-cache
uv run --locked cripto-bot check-config --config reports/sprint-03-_94qv2ax/execution.toml
uv run --locked cripto-bot paper-run --config reports/sprint-03-_94qv2ax/execution.toml
uv run --locked cripto-bot paper-reconcile --config reports/sprint-03-_94qv2ax/execution.toml
uv run --locked cripto-bot paper-report --config reports/sprint-03-_94qv2ax/execution.toml
uv run --locked cripto-bot paper-run --config reports/sprint-03-_94qv2ax/execution.toml
```

| Verificação | Resultado obtido |
|---|---|
| Primeira execução | 2 fills novos; reconciliação aprovada |
| Repetição | 0 fills novos, 3 eventos de origem identificados como replay |
| Total histórico | 2 intenções, 2 fills, 6 eventos de journal e 18 postings |
| USDT livre | `10009.58001000` |
| USDT reservado | `0.00000000` |
| BTC livre/reservado | `0.00000000` / `0.00000000` |
| Custo da posição | `0.00000000` |
| Taxas totais USDT | `0.20999000` |
| Resultado realizado USDT | `9.58001000` |

Preço simulado de compra: `100.10000000`, taxa `0.10010000`; venda: `109.89000000`, taxa `0.10989000`. A primeira execução, reconciliação, relatório e repetição mantiveram o mesmo hash financeiro:

```text
d4389da8aff0d298fe2ee1c049f0d0278257fd60627b754a0d2525e528338a37
```

Cada evento foi conferido com soma de postings zero separadamente em BTC e USDT, usando Decimal. Os hashes dos relatórios publicados foram comparados aos manifestos. O JSON de evidências preserva o resultado completo, contexto, ledger e eventos, além dos contadores de cada comando.

stdout é um objeto JSON; stderr contém evento JSON com o mesmo run_id. Todos os resultados financeiros identificam `mode=PAPER`, `orders_sent=0` e contadores de simulação separados do total histórico. Rejeição de risco aparece como RISK_REJECTED, não como fill.

## 5. Wheel em ambiente separado

O ambiente `.venv-wheel` existente foi reutilizado com reinstalação do wheel final e dependências exportadas do lock. Em ambiente novo, criar primeiro com `uv venv --python 3.13.15 .venv-wheel`.

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR=/home/cams7/Dev/Cripto/.uv-cache
uv build --quiet
mkdir -p .wheel-smoke
uv export --locked --no-dev --no-emit-project --format requirements-txt --output-file .wheel-smoke/requirements-sprint03.txt
uv pip install --reinstall --python .venv-wheel/bin/python --requirement .wheel-smoke/requirements-sprint03.txt dist/cripto_bot-0.1.0-py3-none-any.whl
uv run --locked python tests/wheel_smoke.py
```

Wheel final: `cripto_bot-0.1.0-py3-none-any.whl`.

```text
SHA-256: 2597958d3edc3eefb996a580040273fcf9815d438419e09149fe6610d3bc1637
```

Importação confirmada em `/home/cams7/Dev/Cripto/cripto-bot/.venv-wheel/lib/python3.13/site-packages/cripto_bot/__init__.py`. O smoke test executou em diretório neutro `.wheel-smoke`, com `-I`, sem PYTHONPATH do checkout, paths absolutos e audit hook de sockets. Criou carteira nova por execução, conferiu os saldos e repetiu o roteiro nessa mesma carteira.

Foram aprovados `check-config`, `run-once`, duas coletas fixture e os quatro comandos da sequência PAPER (run/reconcile/report/run). O probe do guard foi bloqueado e LIVE permaneceu rejeitado com código 2. Dados do roteiro não foram confundidos com a instalação anterior do wheel. Rebuilds podem mudar o hash; comparar o artefato exato validado.

## 6. Matriz AC01–AC18

| Critério | Evidência executada | Resultado |
|---|---|---|
| AC01 | 204 testes anteriores preservados, comandos antigos e coleta fixture no wheel | Aprovado |
| AC02 | Compra/venda padrão e carteira nova com saldos/taxas exatos | Aprovado |
| AC03 | Replay de eventos/ações/fill, mesmo hash e nenhum aporte/posting novo | Aprovado |
| AC04 | Conflito de contexto, payload e append com identidade confirmada | Aprovado |
| AC05 | Reserva/consumo/liberação, sobra contábil e rejeição/cancelamento sem fill | Aprovado |
| AC06 | Ledger por ativo, taxas separadas, custo parcial e última baixa sem resíduo | Aprovado |
| AC07 | Decimal estrito, limites, overflow, tick adverso, step comum e receita não positiva | Aprovado |
| AC08 | Status/Spot/símbolo/filtros desconhecidos, mínimos/máximos e flags de notional | Aprovado |
| AC09 | Falta de saldo/short, posição já aberta, pendência e fronteiras de entrada/exposição | Aprovado |
| AC10 | DAY_START, perda/drawdown nas fronteiras, risco realizado/não realizado e virada UTC persistidos | Aprovado |
| AC11 | SELL sob trava sem venda automática; recuperação de preço não libera BUY | Aprovado |
| AC12 | Preço temporal, idade exata de 5 s e vencimento, REFERENCE/BID_ASK sem spread duplicado | Aprovado |
| AC13 | Morte real do processo antes/depois de A e B, seguida de reconciliação e replay único | Aprovado |
| AC14 | Flock entre stores, liberação após morte e rejeição de versão/estado obsoleto | Aprovado |
| AC15 | Projeção, intenção, fill, journal, postings e contexto corrompidos; histórico ausente; bloqueio durável | Aprovado |
| AC16 | Relatório somente leitura, falha de rename/publicação, banco preservado e reexportação sem fills | Aprovado |
| AC17 | Configuração/roteiro/paths/credenciais/flags proibidos; sentinelas em HTTPX/PublicSource e guard de sockets | Aprovado |
| AC18 | Qualidade, 316 testes, build e wheel neutro com carteira nova/replay | Aprovado |

Os testes de corrupção removeram triggers somente no harness, de modo deliberado, para injetar falhas que a API normal rejeita. O produto não fornece esse procedimento como recuperação. As mortes usaram processos filhos reais sob audit hook, encerrados antes/depois do commit; a reabertura comprovou rollback ou reserva/fill integral e liberação do lock.

## 7. Diagnóstico, correções e limites

Durante o desenvolvimento, foram corrigidos os metadados explícitos de proveniência nos postings, o relatório de exposição de compromisso ainda reservado e a propagação dos contadores em falha após efeitos confirmados. Também foram corrigidos achados de estilo/tipagem e o fechamento de uma conexão SQLite do harness de testes; a suíte final não emitiu avisos. Resultados intermediários não foram tratados como aprovação final.

| Situação | Conduta implementada |
|---|---|
| Exit 2 / INVALID_CONFIG | Corrigir campos, paths, cenário ou flags; nenhuma carteira é criada por roteiro estruturalmente inválido |
| Falha após reserva | Reabrir/reconciliar; retomar o plano persistido, sem buscar cotação nova |
| Falha após fill confirmado | Retornar progresso histórico; replay não reaplica o fill |
| Divergência | Bloquear novos efeitos, preservar banco/ledger e diagnosticar em cópia |
| WRITER_BUSY | Aguardar o escritor; não remover o arquivo de lock de processo vivo |
| Contexto/modelo incompatível | Rejeitar mudança; sem reset ou nova carteira silenciosa no mesmo diretório |
| Falha de exportação | Banco permanece confirmado; repetição publica novo relatório |
| Histórico inválido | Relatório indisponível, sem inventar saldos nem corrigir por diferença |

`paper-report` é somente leitura e não persiste bloqueio. Se a projeção divergir, pode retornar saldos reconstruídos do journal com `reconciled=false` e `blocked=true`; isso é diagnóstico, não reparação. `paper-run` e `paper-reconcile` persistem o bloqueio quando possível. Não existe comando de reset/desbloqueio nesta Sprint.

Cancelamento/rejeição local de uma reserva é testado nas APIs de domínio/aplicação, sem CLI administrativa. Não há fill parcial; venda parcial de uma posição é uma ordem integral de quantidade menor. São conceitos distintos, e só o segundo integra esta implementação.

Não foram executados coleta de mercado real, ordens externas, AWS, Testnet, notificações, estratégia ou backtest. Não houve teste de perda de energia/disco, NFS, coordenação distribuída, benchmark de alto volume ou comissão real da Binance. A reconstrução completa favorece auditoria local; não comprova capacidade de processamento contínuo. O relógio de replay não é o relógio de uma sessão de negociação real.

## 8. Limpeza, custos e conclusão

Custo AWS zero, sem recursos criados ou capital/taxas reais. Uso apenas local de disco/CPU e reinstalação de dependências de empacotamento.

Foram preservados exemplos, carteira padrão, carteira da verificação final e diretórios do smoke test para inspeção. Bancos, `.paper.lock`, relatórios e temporários estão ignorados pelo Git; fixtures e TOML de exemplo continuam versionáveis. Somente remover uma carteira sintética após identificar sua origem e preservar as evidências necessárias. Não apagar outros datasets, fontes, lock de dependências ou histórico Git; não substituir banco original para esconder divergência.

A implementação atende à matriz offline com as limitações registradas. Próximo passo: revisão das evidências antes do detalhamento da Sprint 04. Esta entrega não a inicia, não promove modo, não cria commit e não publica remotos.

Fontes oficiais reconfirmadas em 24/10/2026: [Decimal](https://docs.python.org/3.13/library/decimal.html), [sqlite3](https://docs.python.org/3.13/library/sqlite3.html) e [filtros Spot](https://github.com/binance/binance-spot-api-docs/blob/master/filters.md). Ver [ADR 0004](../decisoes/0004-carteira-paper-e-ledger.md), [especificação](../sprints/sprint-03.md) e [evidências completas](sprint-03-evidencias.json).

## Adendo documental de 25/10/2026 — validações antes de LIVE

O aceite registrado neste documento permanece restrito ao escopo histórico executado. Ele não comprova backtest fora da amostra, PAPER contínuo, Demo Spot, Spot Testnet ou `POST /api/v3/order/test`. A sequência e os gates atualizados estão no [planejamento, seção 10](../planejamento.md#10-gates-entre-ambientes-e-modos) e no [roteiro de validação](../testes/validacao-pre-live.md). Demo passa à Sprint 09, Testnet complementar à 10 e preparação LIVE à 11, sem ativação. A implementação desta Sprint continua exclusivamente PAPER; DEMO/TESTNET/LIVE não são liberados por esta revisão.

Nenhum teste foi repetido e nenhuma evidência JSON foi alterada por este adendo. A solicitação atual autoriza somente revisão documental. LIVE permanece bloqueado por padrão e exige validações concluídas, limites de risco reais e aprovação explícita vigente do responsável.

O fill integral sintético desta Sprint não cobre execuções parciais, atrasos ou ordens sem fill do PAPER contínuo; venda de parte da posição não é fill parcial de uma ordem. Esses cenários são obrigatórios na [Sprint 06](../sprints/sprint-06.md) antes da integração privada.

## Referência documental do banco — revisão de 25/10/2026

O DDL existente foi documentado em [bancos/paper-sqlite.md](../bancos/paper-sqlite.md), com diagrama relacional, constraints, operação e rejeição de schemas incompatíveis. Esta revisão foi leitura de fonte, sem abrir bancos, executar migrations ou repetir testes; não amplia o aceite histórico. Qualquer futura mudança estrutural exige atualização desse documento e do [catálogo](../bancos/README.md), com verificação/evidências na Sprint responsável, conforme seção 4.8 do planejamento.
