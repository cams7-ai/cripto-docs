# Validação da Sprint 06A — layout e core puro

Data: 26/10/2026. **APROVADA no alcance Python/local/PAPER/Spot/BTCUSDT/15m: M1 e M2 concluídos.** Implementação solicitada após o detalhamento. Não representa operação contínua, nova avaliação econômica ou autorização privada/AWS.

Referências: [especificação 06A](../sprints/sprint-06a.md), [agregador](../sprints/sprint-06.md), [planejamento](../planejamento.md), [ADR 0008](../decisoes/0008-core-e-identidade-da-composicao.md), [evidências estruturadas](sprint-06a-evidencias.json) e [relatório HTML](relatorios/sprint-06a/report.html). [Preview revisado](relatorios/sprint-06a/preview.png).

## Baseline, sequência e qualidade

Bot limpo no HEAD `81ec74611845950116e705c5310c19070234b1ad`; docs no HEAD `405e8a4bb572594d241cc9f67c3e6cb88ff0cba8`, com planejamento/agregador/especificação locais já modificados, preservados. Core criado com Git independente na branch main, sem commit ou remoto. A inspeção inicial conferiu 120/120 hashes da evidência analítica; o arquivo `reports/sprint06a/baseline/tracked-baseline.tar` foi novamente confrontado com os mesmos 120 hashes, todos iguais.

Primeiro baseline e oráculos; depois layout sem core, regressões/build/wheel e registro `layout/acceptance.json`; somente após M1 aprovado foram criados core e sua integração. Arquivo de fontes M1 em `reports/sprint06a/layout/layout-sources.tar`. Não houve extração antecipada ou sobrescrita dos artefatos anteriores.

| Marco | Testes aprovados | Tempo JUnit | Linhas cobertas | Ramificações cobertas | Cobertura combinada |
|---|---|---|---|---|---|
| baseline | 528 | 631.85 s | 3569/3728 | 1075/1220 | 93.86% |
| layout | 528 | 732.34 s | 3573/3733 | 1076/1222 | 93.82% |
| final | 533 | 581.65 s | 3388/3549 | 1002/1150 | 93.42% |
| core | 54 | 0.42 s | 272/282 | 87/94 | 95.48% |

Zero falhas/erros/skips nas suítes completas registradas. Os 40 contratos selecionados passaram em 0,71 s antes da suíte final; estão incluídos nos 533 testes, não devem ser somados novamente. Core tem 54 testes próprios; baseline/layout são repetições de regressão, não novas amostras de desempenho. Cobertura não é 100%; bot/core têm escopos diferentes após a extração e não são diretamente comparáveis. Ruff, formatação, mypy strict, builds e smokes passaram. Python 3.13.15, uv 0.12.19 e setuptools 84.2.0 preservados.

## Implementação e fronteiras verificadas

Bot em `cripto-bot/src/cripto_bot`; core em `cripto-core/src/cripto_core`, com manifest, lock, README/API, py.typed, testes e wheel próprios. `numeric`, `validation`, `serialization`, `contracts`, `execution`, `sizing` e `strategy.sma` contêm as regras puras compartilhadas; `errors` fornece as mesmas classes reexportadas pelo bot. Plan conserva `paper-integral-v1` na identidade do fill. `_sized_quantity` apenas passa caixa/equity explícitos ao core.

Carteira/Wallet/Intent/Posting, ledger, risco/admissão, coordenação, registro/flags, configurações, backtest e adapters permanecem no bot. Nenhum novo par, estratégia, parâmetro, custo, limite ou modo foi introduzido. Os quatro módulos SQLite têm AST idêntica à baseline; não houve alteração de DDL/schema, constraints/triggers/transações ou migração. Instalação da biblioteca não habilita flags.

O lock manteve todas as 26 versões anteriores e adicionou somente `cripto-core==0.1.0`. Fonte local explícita do wheel em `../cripto-core/dist/06a-final/cripto_core-0.1.0-py3-none-any.whl`, com SHA256 registrado. O metadata do bot declara dependência normal, sem path de checkout; core não tem dependências de produção. Os arquivos Python do wheel core conferem byte a byte com os fontes entregues; py.typed está presente.

## Wheels, identidade e compatibilidade

Ambientes novos `.venv-wheel-06a-layout` e `.venv-wheel-06a-final` preservaram `.venv-wheel` anterior. Os dois pacotes finais foram instalados por wheels e carregados de site-packages, usando Python `-I`, sem PYTHONPATH ou checkout irmão importável. Prova adicional instalou somente core, sem bot. Instalação forçada do bot sem core falhou explicitamente com `No module named 'cripto_core'`; seleção ausente/inválida de marco no harness também foi rejeitada.

`runtime-composition-v1` inclui manifest/lock/pin do consumidor, inventário/hash dos arquivos carregados, versão e instalação. Core wheel precisa conferir com RECORD; extra/ausente/alterado, versão incompatível e core editable são rejeitados. Bot editable só é aceito com origem correspondente ao seu src. Alterar apenas o core mudou o fingerprint e bloqueou verify_protocol com `FROZEN_PROTOCOL_CHANGED`. RECORD verifica consistência local, não assinatura externa.

A nova composição reexportou o banco sintético criado pela baseline, com zero fill novo, mesmo resultado selado e SHA256 SQLite `5f7b33a6fc7ada2f9c3476415decbe579c208f2d597cb81b0728e1c2db4c2279`. Retomar o mesmo protocolo sob código novo foi rejeitado com exit 3, sem mudar esse hash. O registro real `data/backtest-usage/test-usage.sqlite3` manteve SHA256 `af7ee92659cb1be9c4e322daeba997755430a040faec4b1342c1cabf082810bd`. Nenhuma janela final real foi reavaliada ou registro reinicializado.

## Oráculos e demonstração

Os três smokes executaram 22 fluxos cada, incluindo CLI/config/default NOOP, duas coletas fixture, roteiro manual/replay, SMA/reconcile/report/replay e histórico sintético prepare/freeze/development/validation/test/reconcile/report/replay. O harness final copia controles e fixtures para uma raiz sintética própria; não usa o registro real para consumo de teste sintético. Audit hook e probe demonstram sockets bloqueados.

| Controle | Esperado e obtido na baseline, M1 e M2 |
|---|---|
| Manual | Dois fills, saldo 10009.58001000 USDT; replay zero novos fills |
| SMA | 71 ciclos, dois fills, saldo 9905.46181258 USDT; replay zero novos fills |
| Histórico fixture | 48 curvas com métricas/séries/motivos/resultados equivalentes |
| Efeitos externos | orders_sent=0 em todos os comandos permitidos; LIVE rejeitado |

A comparação das curvas exclui apenas run_key e tamanho de checkpoint. Todos os demais campos são iguais; os hashes globais de resultado/protocolo mudam legitimamente pela identidade do código. Não usar essa mudança para alegar retorno financeiro diferente nem nova amostra fora da amostra. Os smokes não reexecutam o teste final real da 05.

## Critérios A01–A16

| Critério | Evidência obtida | Decisão |
|---|---|---|
| A01 | Baseline 120/120 hashes + arquivo Git; M1 aprovado antes de criar core | APROVADO |
| A02 | Layout/discovery/paths testados por regressões e wheel M1 | APROVADO |
| A03 | 54 testes core, grafo transitivo de imports e wheel core sozinho sem bot | APROVADO |
| A04 | Identidade de Plan/PaperError/Snapshot/TrendSMA e make_plan reexportados | APROVADO |
| A05 | Vetores exatos de Decimal/tick/step/notional/custos/BID_ASK e negativos | APROVADO |
| A06 | Sizing com saldos explícitos e regressões de risco/reserva no bot | APROVADO |
| A07 | Warm-up/igualdade/cross/inventário/prefixo e contexto Decimal local | APROVADO |
| A08 | 533 testes bot; 22 fluxos em cada smoke e 48 curvas equivalentes | APROVADO |
| A09 | Alterar somente core muda fingerprint; RECORD inválido e retomada divergente rejeitados | APROVADO |
| A10 | Locks separados; seis artefatos identificados; bot/core instalados por wheels | APROVADO |
| A11 | Core sozinho passa; bot sem core falha; versão/core editable incompatíveis rejeitados | APROVADO |
| A12 | Banco sintético antigo reexportado com SHA SQLite e resultado idênticos; retomada rejeitada | APROVADO |
| A13 | Suíte existente de mortes/rollback/CAS/locks/publicação preservada | APROVADO |
| A14 | Audit hook/probe de sockets e rejeição de LIVE/credenciais/composição inválida | APROVADO |
| A15 | README/API, arquitetura/ADRs, SMA/catálogos/bancos atualizados; HTML conferido visualmente | APROVADO |
| A16 | M1/M2 aprovados no escopo; evidências/rollback/limitações registrados; 06B não iniciada | APROVADO |

## Reprodução e limitação do cache

A instalação completa com cache frio **não foi demonstrada**. O primeiro pip offline não conseguiu resolver todos os binários, inclusive pydantic-core; copiar o cache já existente não bastou. Para evitar downloads/upgrades, os ambientes novos reutilizaram as distribuições externas da baseline instalada após conferir versões do export e todos os hashes presentes em RECORD, zero divergência. Scripts de ferramentas dev foram rebaseados para o Python do ambiente destino e seus RECORDs atualizados. Bot/core foram construídos e instalados separadamente por wheels. Logs das tentativas e JSON de dependências reutilizadas foram preservados; essa limitação não deve ser apresentada como instalação limpa completa via índice/cache.

Helper: [reutilização verificada de dependências](ferramentas/sprint-06a-reuse-dependencies.py), executado com o Python do bot (packaging já está no grupo dev). Ele respeita marcadores de plataforma, exige paths dentro de Cripto, verifica a entrada antes de copiar e não inclui bot/core. Usado somente em ambientes novos de teste; não é uma rotina de atualização de produção.

Comandos efetivos, adaptando o marco conforme a especificação (cache da entrega em cripto-bot/.uv-cache):

```bash
# core: lock e instalação runtime; ferramentas dev ausentes vieram da baseline verificada
cd /home/cams7/Dev/Cripto/cripto-core
UV_CACHE_DIR=/home/cams7/Dev/Cripto/cripto-bot/.uv-cache uv sync --locked --group dev --offline
UV_CACHE_DIR=/home/cams7/Dev/Cripto/cripto-bot/.uv-cache uv run --locked --offline pytest -q --cov=cripto_core --cov-branch
UV_CACHE_DIR=/home/cams7/Dev/Cripto/cripto-bot/.uv-cache uv build --offline --out-dir dist/06a-final

cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
uv run --locked --offline pytest -q --cov=cripto_bot --cov-branch
uv build --offline --out-dir dist/06a-final
uv export --locked --offline --no-dev --no-emit-project --no-emit-package cripto-core --format requirements.txt --output-file reports/sprint06a/final/requirements.txt
# Após criar ambiente novo, preencher apenas dependências externas da baseline verificada:
.venv/bin/python ../docs/testes/ferramentas/sprint-06a-reuse-dependencies.py .venv-wheel .venv-wheel-06a-final reports/sprint06a/final/requirements.txt
uv pip install --offline --no-deps --python .venv-wheel-06a-final/bin/python ../cripto-core/dist/06a-final/cripto_core-0.1.0-py3-none-any.whl dist/06a-final/cripto_bot-0.1.0-py3-none-any.whl
WHEEL_SMOKE_STAGE=final uv run --locked --offline python tests/wheel_smoke.py
```

Não reconstruir/sobrescrever artefato identificado para retomar experimento congelado. Arquivar nova tentativa por hash e atualizar lock deliberadamente; a instalação locked exige o wheel local disponível no caminho declarado. Ambientes anteriores não foram removidos; os comandos de criação devem usar destino novo quando já existir estado a preservar.

## Artefatos, documentação e revisão visual

Logs integrais e JSONs operacionais em `/home/cams7/Dev/Cripto/cripto-bot/reports/sprint06a/`: baseline/layout/final (JUnit, cobertura, instalação, builds, smokes), financial-equivalence.json, artifacts-proof, negative-installation e previous-model-compatibility. Core: `/home/cams7/Dev/Cripto/cripto-core/reports/sprint06a/`. Os hashes dos seis wheels/sdists, fontes e controles estão nas evidências centrais. Scripts temporários de transformação foram arquivados nos logs, sem manter cópias ativas das regras em docs.

Atualizados README/API, arquitetura modular/central, ADR 0001/adendo e ADR 0008, SMA/catálogo e bancos/catálogo. A ausência de DDL alterado foi registrada com comparação AST dos quatro stores. Relatório HTML derivado das evidências, sem novo replay, conferido em Chrome headless com rede bloqueada/resolver indisponível; screenshot completo inspecionado: tabelas, valores, artefatos e limitações legíveis, sem truncamento/sobreposição. O [gerador](ferramentas/sprint-06a-relatorio.py) só lê as evidências e produz HTML. PDF adicional dispensado por ser revisão técnica local; HTML e preview atendem à leitura/revisão desta entrega.

## Recuperação e conclusão

Baseline versionada e fontes M1 arquivadas; restaurar somente composição/locks compatíveis, preservando trabalho posterior e dados. Não usar reset destrutivo, regravar protocolo selado, remover ledger ou registro final para aceitar hash novo. Protocolo antigo exige composição correspondente para retomada; reexportação em leitura permanece disponível.

M1/M2 e A01–A16 aprovados no escopo descrito. Sem commits/remotos/publicação, rede de mercado, notificações, AWS, ordens privadas ou migração operacional. **06B está elegível somente para detalhamento/revisão**; 06B–06D não foram iniciadas. Não se conclui desempenho futuro, lucro ou prontidão LIVE a partir desta extração técnica.
