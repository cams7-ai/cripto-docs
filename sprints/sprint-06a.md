# Sprint 06A — Layout `src` e extração de `cripto-core`

Detalhamento: 26/10/2026. **Estado: IMPLEMENTADA E VALIDADA no alcance da 06A.** Implementação posteriormente solicitada pelo responsável usando o prompt da seção 12. M1 e M2 aprovados; resultados na seção 14 e no [guia 06A](../testes/sprint-06a-validacao.md). A próxima etapa elegível para detalhamento é 06B, sem início automático.

Referências normativas: [planejamento](../planejamento.md), seções 4.7–4.10, 5, 6.5, 9.2 e 13; [agregador 06](sprint-06.md); [Sprint 05](sprint-05.md), registros de execução/ajuste analítico; [guia 05](../testes/sprint-05-validacao.md), [evidências 05](../testes/sprint-05-evidencias.json), [guia analítico](../testes/duckdb-parquet-validacao.md) e [evidências analíticas](../testes/duckdb-parquet-evidencias.json). Contratos: [arquitetura](../arquitetura.md), [arquitetura modular](../arquitetura-modular.md), [matriz modular](../testes/estrategias-modulares-validacao.md), [SMA](../estrategias/trend_sma.md), [bancos](../bancos/README.md) e ADRs [0001](../decisoes/0001-monolito-modular.md), [0002](../decisoes/0002-modos-e-decimais.md), [0005](../decisoes/0005-estrategia-modular-e-persistencia.md), [0006](../decisoes/0006-backtest-historico-e-protocolo.md) e [0007](../decisoes/0007-duckdb-parquet-analitico.md).

## 1. Objetivo e incremento demonstrável

Primeiro reorganizar e validar o bot em `src/cripto_bot`; depois extrair contratos e cálculos puros para `cripto-core/src/cripto_core`, com bot consumidor funcional instalado por wheels. Preservar valores financeiros, decisões, causalidade, erros, defaults, comandos e persistência. A entrega demonstra fonte única das regras e independência dos checkouts, sem iniciar o piloto.

Há dois marcos obrigatórios: **M1 — layout aprovado, antes de extrair**; **M2 — composição bot/core aprovada**. Falha em M1 impede iniciar M2. Registrar baseline, resultados e artefatos separadamente; a validação apenas da versão final não substitui a verificação intermediária.

## 2. Baseline inspecionada e elegibilidade

Inspeção somente leitura dos repositórios/fontes e comparação SHA256 em 26/10/2026; nenhum banco operacional aberto, teste funcional executado ou dependência instalada. Versões obtidas por `uv --version` e pelo Python existente; ajuda dos comandos consultada sem executá-los sobre os projetos.

| Item | Resultado desta inspeção | Condição antes de implementar |
|---|---|---|
| Aplicação | HEAD `81ec74611845950116e705c5310c19070234b1ad`, sem alterações locais no início | Reinspecionar estado/revisão e preservar qualquer mudança posterior |
| Documentação | HEAD `405e8a4bb572594d241cc9f67c3e6cb88ff0cba8`; `sprints/sprint-06.md` já modificado localmente antes desta entrega | Preservar o agregador local; registrar hashes finais dos documentos usados |
| Projetos existentes | Somente `cripto-bot` e `docs`; core/dados/análise ainda ausentes | Criar somente core na implementação; não criar diretórios vazios de 06B/C |
| Evidências 05 | 109/116 hashes de fontes/configuração/testes conferem; sete diferenças posteriores | Diferenças: manifest, lock, README, `.gitignore`, `backtest_report.py`, `entrypoints/backtest.py` e `tests/wheel_smoke.py`; todas cobertas pela evidência complementar |
| Evidências analíticas | **120/120 hashes conferidos**, zero divergência, incluindo manifest/lock/pin/fontes/testes | Esta é a baseline de código da extração; nova divergência exige revisão antes de avançar |
| Qualidade histórica | 521 testes na 05; 528 no ajuste analítico, com qualidade/build/wheel registrados | São resultados anteriores; reproduzir regressão atual e registrar falhas, sem impor contagem fixa |
| Ferramentas | uv `0.12.19`; Python da `.venv` `3.13.15`; backend `setuptools==84.2.0`; Python permitido `>=3.13,<3.14` | Manter pins e versões resolvidas salvo mudança necessária explicitamente documentada |
| Configuração/layout | Manifest busca `modules/trading/src`; pacote `cripto_bot`, distribuição `cripto-bot==0.1.0`, console `cripto-bot` | Alterar somente layout em M1; adicionar core em M2 |

**Decisão histórica do detalhamento: elegível para revisão da especificação 06A.** Não foi encontrada divergência frente à entrega analítica que bloqueie esse detalhamento. Implementação permanece pendente de solicitação e da reprodução da baseline; esta inspeção não é aprovação nova dos testes. 06B–06D continuam dependentes e não serão detalhadas agora.

## 3. Escopo e exclusões

Somente Python/local/PAPER/Spot/BTCUSDT/15m. Não mudar SMA20/50, igualdade de cruzamentos, precisão, arredondamentos, custos, limites ou modelo financeiro. Não habilitar módulos por instalar core. Nenhuma flag nova é necessária para uma biblioteca obrigatória: permanecem os opt-ins de estratégia por instância/ambiente/modo/tipo de avaliação/par; defaults desabilitados e NOOP preservados.

Não extrair rede/mercado persistido ou análise nesta etapa; não criar `cripto-market-data`, `cripto-analytics`, `cripto-backtest` ou outras bibliotecas. Não incluir continuous, outbox, mensagens, AWS, modos privados, novas estratégias, multiativo, ranking/Sortino, walk-forward, otimização ou recursos BT-A–BT-F. Não reavaliar janela final real, coletar dados ou alterar projetos de referência.

Preservar todos os comandos existentes, formatos/configurações, código de saída e diagnóstico sanitizado. Imports antigos usados pelos consumidores/testes do bot podem permanecer como fachadas/reexports explícitos, sem implementação duplicada ou alias por manipulação de `sys.modules`.

## 4. Fronteiras e inventário de extração

A inspeção encontrou acoplamentos que impedem mover diretórios inteiros sem separar responsabilidades: `domain/models.py` contém configuração com paths; `portfolio/models.py` mistura números/DTOs com Wallet/postings; `risk/execution.py` usa helpers de `domain/market.py`; a SMA importa `PaperError`; `_sized_quantity` recebe `StrategyWallet`. Separar esses elementos sem mover carteira/risco operacional para core.

| Origem atual dentro de `cripto_bot` | Destino previsto / contrato | O que permanece no bot |
|---|---|---|
| `domain/models.py::parse_decimal` | `cripto_core.numeric.parse_decimal`, mesma assinatura/validação | `Settings`, `MarketSettings`, `PaperSettings`, paths e composição |
| `domain/portfolio/models.py`: `PaperError`, Q/ZERO, `number`, `text`, `bounded`, `money`, `Plan` | `cripto_core.errors`, `numeric`, `contracts`; mesmos códigos, assinaturas e campos serializados | MODEL, Wallet/Intent/Posting, ledger, validação de lançamentos, estado/identidade de carteira |
| `domain/market.py`: helpers comuns estritamente necessários a números/execução | `cripto_core.validation` e `serialization` para helpers puros, `canonical`/`digest`; manter os tipos de erro existentes | Candle/parsers Binance e regras de ingestão, SCHEMA/PARSER, fonte/dataset e aquisição; extração de dados é 06B |
| `domain/risk/execution.py`: filtros/observação e preço/plano sintéticos | `cripto_core.execution`, mesmas funções públicas `observation`, `filters`, `range_check`, `quantity_step`, `execution_price`, `make_plan`; DTO `Plan` importado do core | Executor, persistência, admissão central e decisão de executar; não ampliar pares/filtros/modelos suportados |
| `domain/strategy/sma.py`: Snapshot/Decision/Strategy/TrendSMA | `cripto_core.strategy.sma`, mesmas assinaturas e regras causais; exceção compartilhada vem do core | Registro/flags, configuração, coordenação, gerações e redução da carteira modular |
| `domain/strategy/engine.py::_sized_quantity` | Extrair a aritmética para `cripto_core.sizing.sized_quantity`, recebendo `usdt_free`/`equity` como Decimal e module/quote/at/parameters/rules como hoje; wrapper passa os valores explícitos | Acesso ao Wallet, seleção da instância, risco/admissão e mutações de estado; não passar StrategyWallet ao core |

`MarketError` e helpers de tempo/JSON necessários à cadeia acima podem ser compartilhados no core, preservando identidade da classe via reexport e sem transportar configurações. A implementação deve registrar o mapa final símbolo → fonte única; helpers não usados por essa cadeia permanecem no bot. Não criar uma API genérica de mercado futuro. Não confundir preço/plano puro com serviço de risco: `risk/limits.py`, `portfolio/engine.py`, `strategy/engine.py`, `domain/backtest` e todos os casos de uso/adapters continuam no bot.

Core depende somente da biblioteca padrão em produção. Não importa `cripto_bot`, HTTPX, Pydantic, SQLite, DuckDB, ambiente, paths operacionais ou relógio de parede. Timestamp recebido explicitamente e cálculo Decimal local são permitidos; não modificar contexto Decimal global ao importar. Classes de exceção e DTOs compartilhadas são reexportadas com identidade preservada; não criar subclasses incompatíveis para simular compatibilidade.

## 5. Layout, distribuição, versões e locks

Em M1, mover fontes para `/home/cams7/Dev/Cripto/cripto-bot/src/cripto_bot`, configurar descoberta setuptools `where=["src"]`, `include=["cripto_bot*"]`, `namespaces=false`. Atualizar mypy, testes/fixtures e comandos ativos para `src`; preservar referências históricas em evidências e ADRs por adendo, sem reescrevê-las como se já usassem o novo layout.

Em M2, criar `/home/cams7/Dev/Cripto/cripto-core`, Git independente e `src/cripto_core` com `__init__.py`/`py.typed`, README, manifest, pin Python, lock, `.gitignore`, testes e build próprios. Distribuição inicial proposta `cripto-core==0.1.0`, Python `>=3.13,<3.14`, uv `==0.12.19`, backend `setuptools==84.2.0`. Core usa grupo dev com ferramentas compatíveis às resolvidas no bot; não acrescentar framework de plugins/DI/ORM. Não configurar remoto/publicação ou executar commit como consequência automática.

| Marco | Composição a validar | Artefatos |
|---|---|---|
| Baseline | Bot 0.1.0 atual, lock existente, sem core | Hashes, versões, regressões e resultados sintéticos guardados em diretório de execução identificado |
| M1 | Bot 0.1.0 com layout novo, ainda sem core | Wheel/sdist e evidências separados em `cripto-bot/dist/06a-layout/` |
| M2 | Bot 0.1.0 + core 0.1.0, dependência declarada exatamente `cripto-core==0.1.0` | Artefatos em `cripto-core/dist/06a-final/` e `cripto-bot/dist/06a-final/`, hashes e locks dos dois projetos |

As versões iguais do bot não tornam builds equivalentes: não sobrescrever artefatos anteriores; identificar cada marco por hash/revisão. Uma alteração posterior do conteúdo de core requer nova identidade/versionamento e atualização deliberada do lock, sem substituir wheel sob o mesmo hash.

Para integração local reproduzível, construir core antes de resolver o bot. Proposta concreta de fonte local no manifest do bot:

```toml
# project.dependencies inclui "cripto-core==0.1.0"
[tool.uv.sources]
cripto-core = { path = "../cripto-core/dist/06a-final/cripto_core-0.1.0-py3-none-any.whl" }
```

É referência explícita ao artefato, não import de checkout/editable. O lock do bot deve fixar essa resolução e sua integridade; verificar o comportamento com uv fixado antes de aceitar. O wheel do bot declara dependência normal `cripto-core==0.1.0`, sem path absoluto/checkout em seus metadados. CI/smoke recebem os dois wheels identificados. O local source exige disponibilizar esse artefato no caminho documentado para `uv sync --locked`; registrar essa limitação, sem tratá-lo como pacote publicado em índice. Não criar uv workspace agregador. Atualizar lock somente para mudança declarada, preservando as demais versões quando possível.

## 6. Fingerprints, retomada e estados anteriores

`adapters/storage/market_export.py::source_fingerprint` enumera hoje o caminho antigo fixo. Sua correção é obrigatória em M1: detectar fontes efetivamente usados no novo layout, sem hash vazio silencioso. Em M2, a identidade experimental deve incluir bot, core, lock/pin/manifest e modo de instalação. Não basta versão `0.1.0`: alteração em função extraída precisa modificar identidade e impedir retomar execução sob código diferente.

No instalado, usar metadados/arquivos da distribuição para identificar conteúdo efetivamente importado, sem depender de checkout irmão. Associar hash do wheel ao inventário de arquivos e instalação validada; se desenvolvimento editable for suportado posteriormente, identificar fontes reais e registrar modo explicitamente. Ausência/inconsistência de identidade é erro antes de freeze/retomada, não fallback para `unversioned` apresentado como prova suficiente. Documentar algoritmo/versionamento e testar diferenças no core mantendo bot/config/dataset constantes.

`application/backtest_run.py::verify_protocol` compara protocolo calculado ao selado; uma mudança de fonte exige rejeitar a retomada de execução, sem regravar protocolo antigo. `entrypoints/backtest.py` já permite `backtest-report` somente leitura sobre identidade selada: preservar esse caminho, sem exigir nova avaliação. Não alterar journal, dinheiro, fingerprints históricos ou registro `data/backtest-usage/test-usage.sqlite3` para obter compatibilidade.

Nenhum schema/DDL financeiro precisa mudar por esta extração. Manter mercado v1, carteira manual v1, modular v2 e histórico schema1/modelo próprio. Se surgir mudança de formato indispensável, registrar impedimento e plano específico antes de adotá-la. Compatibilidade de reexportação é verificada em fixtures/copias sintéticas do modelo anterior, preservando arquivos base; bancos reais não são material de teste destrutivo. Novos protocolos sintéticos usam diretórios próprios. Reorganização não transforma o período final real da 05 em amostra independente.

## 7. Sequência de implementação futura

1. Reinspecionar dependências/revisões, conferir hashes, preparar guia de validação com status pendentes e registrar baseline; executar regressões offline em diretórios sintéticos isolados.
2. Executar apenas mudança de layout, corrigir descoberta/fingerprints/paths e documentação ativa; construir/instalar wheel e concluir M1. Não extrair core antes desse aceite.
3. Criar core e seus testes; separar primitivas/DTOs, depois execução/sizing/SMA na ordem das dependências. Integrar bot por fachadas/reexports, removendo a cópia anterior somente após validação do consumidor.
4. Construir core, declarar dependência/fonte do wheel e atualizar locks deliberadamente; instalar composição, executar qualidade, contratos e regressões do bot/core.
5. Validar identidade de código, rejeição de retomada incompatível, reexportação de snapshots antigos e guards; conferir distribuição instalada, incluindo falta/troca de core.
6. Gerar relatório técnico legível de equivalência e resultados sintéticos, conferir dados e revisar visualmente. Atualizar README/API, arquitetura/ADRs, SMA/catálogo e documentos de bancos conforme impacto real.
7. Consolidar evidências/limitações e decisão M1/M2. Somente etapa aprovada permite planejar 06B; não iniciá-la automaticamente.

## 8. Matriz de aceite e testes

No detalhamento, todos os casos abaixo estavam **NÃO EXECUTADOS**; na implementação posterior, **A01–A16 foram aprovados**, conforme o guia/evidências 06A. Relacionam-se principalmente a AC09/10/14–17 do agregador, com AC06/15/17 comuns. Os demais aceites do piloto permanecem para 06D.

| ID | Caso | Resultado obrigatório |
|---|---|---|
| A01 | Baseline e sequência | Hashes/revisões e regressões atuais registrados; evidências distintas de layout e extração, com M1 concluído antes de M2 |
| A02 | Descoberta e paths | Imports/console funcionam em `src`, sem dependência do antigo diretório; config/dados mantêm regras de raiz/symlink e localização |
| A03 | Pureza e imports | Core importável sozinho sem bot; testes de grafo de imports inclusive TYPE_CHECKING e transitivos; zero dependência externa de runtime/I/O/contexto global alterado |
| A04 | Contratos e exceções | Plan/Snapshot/Decision, códigos e identidades das classes reexportadas preservados; serialização igual e ausência de cópias de regras |
| A05 | Decimal/execução | Oráculos independentes de `0.1+0.2`, precisão 80 local, limites/quantização; rejeição de float/NaN/infinito; tick/step/notional/taxa, compra/venda e BID_ASK sem spread duplo |
| A06 | Sizing/risco | Mesmas quantidades com mesmo caixa/equity/orçamento; wrapper não passa carteira ao core; admissão, reservas, limites e replay permanecem no bot, sem bypass |
| A07 | SMA e causalidade | Mesmos cruzamentos/igualdade, warm-up, HOLD, posições e erros; anexar futuro não altera decisões anteriores |
| A08 | Regressões funcionais | Todos os comandos existentes e fixtures, default NOOP e opt-in separados, retornos e diagnóstico mantidos; papel/estratégia/histórico reconciliados e replay sem novos efeitos |
| A09 | Fingerprint M1/M2 | Layout e conteúdo efetivos identificados; mudar apenas core altera identidade; fonte ausente/instalação inconsistente falha; retomar protocolo sob outra composição é rejeitado |
| A10 | Pacotes e locks | Core/bot com manifests/locks próprios e build reproduzível identificado; metadados normais, dependência exata; smoke por wheels sem editable/PYTHONPATH/checkouts |
| A11 | Dependência ausente/trocada | Instalação sem core não resolve; execução forçada sem dependência falha claramente; versão/conteúdo divergente não é aceito como composição congelada |
| A12 | Estado e relatórios anteriores | Schema/ledger/registro final preservados; fixtures antigas reexportáveis em leitura com identidade selada; não reexecutar real/test para reparar relatório |
| A13 | Falhas/recuperação | Contratos de crash/rollback/conflito/lock/publicação existentes continuam aprovados; falha de pacote/relatório não grava novo fill ou apaga estado |
| A14 | Guards | Sockets bloqueados em testes/smoke, modo/credenciais rejeitados, nenhuma mutação privada/coleta implícita; probe demonstra guard ativo |
| A15 | Relatórios e documentação | Equivalência numérica/causal e formatos confrontados, HTML legível revisado; README/API/ADRs/SMA/catálogos/bancos conforme impacto atualizados |
| A16 | Conclusão por composição | Revisões/hashes/locks, limitações e rollback reunidos; todos os casos obrigatórios aprovados ou etapa pendente; sem promover modo ou iniciar 06B |

Oráculos mínimos já documentados a preservar: cenário manual com saldo `10009.58001000 USDT`, replay zero fill; fixture SMA com 71 ciclos, dois fills, saldo `9905.46181258 USDT`; histórico sintético com 1.010 candles/960 de score, carteiras independentes e custos base/dobrados/atraso, conforme guias 03–05. Não comparar hashes globais que incluem código reorganizado como se fossem invariantes financeiras: confrontar também valores e decisões exatas. Não somar capitais/retornos de segmentos independentes.

## 9. Comandos e demonstração previstos

Os comandos uv/Python e opções abaixo foram conferidos nos arquivos existentes/ajuda da versão local; **não foram executados como validação de 06A**. Core, novos paths e wheels só existirão após implementação. Usar cache local por projeto e dados sintéticos exclusivos sob o workspace; ausência de cache/dependência deve produzir impedimento explícito, sem liberar rede para testes. Instalação/build com downloads, se necessários, são ação separada do runtime offline.

Baseline no bot, antes de editar:

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy modules/trading/src
uv run --locked --offline pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
```

Depois da mudança de layout, executar qualidade/regressões trocando o alvo do mypy para `src`; construir M1 com `uv build --offline --out-dir dist/06a-layout`. Em M2, na raiz do core:

```bash
cd /home/cams7/Dev/Cripto/cripto-core
export UV_CACHE_DIR="$PWD/.uv-cache"
uv lock --offline
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
uv run --locked --offline pytest -q --cov=cripto_core --cov-branch --cov-report=term-missing
uv build --offline --out-dir dist/06a-final
```

Após declarar a dependência/fonte no bot, rodar `uv lock --offline` uma vez para registrar a mudança deliberada; operações seguintes usam `--locked`. Na raiz do bot:

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
uv run --locked --offline pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
uv build --offline --out-dir dist/06a-final
```

Para M1 e M2, usar ambiente neutro com wheels identificados, sem resolver core pelo checkout. Preparar `.venv-wheel` sem destruir ambiente existente: registrar/reter a instalação anterior e recriar o ambiente de teste apenas quando comprovadamente descartável; caso contrário ajustar harness para ambiente novo dentro do projeto. Em M2, exportar as dependências externas do lock separadamente de core:

```bash
uv export --locked --offline --no-dev --no-emit-project --no-emit-package cripto-core --format requirements.txt --output-file .wheel-smoke/requirements-06a.txt
uv venv --python 3.13.15 --offline .venv-wheel
uv pip install --offline --python .venv-wheel/bin/python --requirement .wheel-smoke/requirements-06a.txt ../cripto-core/dist/06a-final/cripto_core-0.1.0-py3-none-any.whl dist/06a-final/cripto_bot-0.1.0-py3-none-any.whl
WHEEL_SMOKE_STAGE=final uv run --locked --offline python tests/wheel_smoke.py
```

Criar `.wheel-smoke` se ainda não existir. Atualizar o harness **existente** `tests/wheel_smoke.py` para selecionar explicitamente o wheel do marco em validação: hoje presume único wheel em `dist/`, e só comprova origem do bot. Acrescentar comprovação da origem `site-packages/cripto_core`, versão/identidade e ausência de checkout/editable; não usar seleção por “arquivo mais novo”. Em M1 instalar somente bot/dependências com o wheel `dist/06a-layout`; em M2 instalar os dois wheels acima. O comando do harness permanece o existente; acrescentar ao harness o seletor de teste `WHEEL_SMOKE_STAGE=layout|final`, rejeitando ausência/valor desconhecido e mapeando exclusivamente para `dist/06a-layout` ou `dist/06a-final`. Em M1, usar `WHEEL_SMOKE_STAGE=layout uv run --locked --offline python tests/wheel_smoke.py`; em M2, usar o comando `final` acima. Esse seletor pertence ao harness a implementar, não é configuração da aplicação nem capacidade já disponível.

O harness atual usa cwd neutro, Python `-I`, `tests/offline_runner.py` com audit hook e cria configurações/diretórios temporários sintéticos. Já demonstra coleta fixture, roteiro manual, SMA, histórico sintético prepare/freeze/development/validation/test/reconcile/report/replay, bloqueio LIVE e probe de socket. Adaptá-lo conservando isolamento, sem apontar para configuração/dataset real ou alterar registro real consumido. Resultados esperados: sucesso dos fluxos permitidos, `orders_sent=0`, replay sem novos fills e falha controlada de modo/guard. Smoke sintético no segmento `test` não é reutilização da janela final real.

## 10. Entregáveis, evidências e documentação

Na implementação, criar `docs/testes/sprint-06a-validacao.md` como roteiro inicialmente pendente e registrar ao executar; gerar evidências estruturadas em `docs/testes/sprint-06a-evidencias.json` somente com resultados efetivamente obtidos. Este detalhamento define esses caminhos, sem criar placeholders ou inventar execuções. Logs/builds/oráculos podem ficar em diretórios identificados de `cripto-bot/reports/` e `cripto-core/reports/`, sem sobrescrever artefatos antigos. Manter os dados dentro do workspace.

Entregar inventário de símbolos, API/README do core, manifests/locks, fontes/testes, wheel/sdist dos marcos, relatório técnico de equivalência, hashes de dados/config/artefatos e revisões locais dos repositórios. Atualizar READMEs do bot/core e comandos ativos, arquitetura central, adendo ao ADR 0001 e decisão da extração/identidade em ADR pertinente, preservando histórico. Atualizar SMA/catálogo pela mudança de interfaces/dependências; não criar documento de estratégia para a biblioteca core. Bancos/catálogo: registrar ausência de DDL alterado e atualizar operação/proveniência quando afetadas; documento desatualizado bloqueia aceite.

Relatório humano deve derivar de snapshots/oráculos já produzidos, sem repetir avaliação econômica. Conferir valores e revisar visualmente HTML ou formato equivalente; PDF adicional não é exigido. Registrar casos positivos/negativos, cobertura efetiva sem alegar 100% por meta, limitações e bloqueios. Aprovar M1/M2 somente após todos os testes obrigatórios/documentação; então 06B se torna elegível para detalhamento, não para início automático. O guia geral 06 consolida esse resultado posteriormente, sem alterar seus aceites do piloto para “executados”.

## 11. Custos, retenção e rollback

Sem custo AWS, rede de mercado ou capital real. Custos de CPU/disco/cache para baseline, dois builds do bot e core, suítes e exportação sintética. Registrar duração/RSS e volume quando pertinente; não repetir o replay de dois anos para demonstrar movimentação de fontes. Retenção: preservar evidências/documentação e artefatos identificados da baseline/M1/M2; caches/ambientes descartáveis só podem ser limpos após confirmar que não contêm dados únicos, sem apagar journals/exports/registros anteriores.

Rollback M1 restaura fontes/manifest/comandos da baseline preservada; rollback M2 restaura a composição bot/core e locks compatíveis. Não usar reset destrutivo ou sobrescrever trabalho posterior. Preservar fontes extraídos até validar o consumidor; falha em integração pode exigir manter fachada de delegação, nunca segunda implementação financeira divergente. Protocolo antigo não é reescrito para aceitar hash novo; reinstalar a composição correspondente quando retomar for necessário. Compatibilidade persistida inesperada mantém etapa pendente e exige análise específica, sem reset/migração implícita.

## 12. Prompt autossuficiente para implementação futura

O bloco abaixo foi preparado no detalhamento e executado por solicitação posterior, conforme seção 14. Preserva o contrato original; a execução documental anterior não implementou a etapa.

```text
Implemente somente a Sprint 06A em /home/cams7/Dev/Cripto, usando
/home/cams7/Dev/Cripto/cripto-bot como consumidor e criando apenas
/home/cams7/Dev/Cripto/cripto-core como biblioteca/Git independente.
A documentação fica em /home/cams7/Dev/Cripto/docs. Preserve trabalho,
dados, configurações e históricos; não crie remoto, publicação ou commits
sem instrução correspondente. Respeite as permissões do ambiente.

Dependências de leitura e verificação, nesta ordem:
1. docs/planejamento.md, seções 4.7–4.10, 5, 6.5, 9.2 e 13.
2. docs/sprints/sprint-06.md e sprint-06a.md integralmente.
3. docs/sprints/sprint-05.md; docs/testes/sprint-05-validacao.md e
sprint-05-evidencias.json; duckdb-parquet-validacao.md/evidencias.json.
4. docs/arquitetura.md, arquitetura-modular.md, decisoes/0001, 0002,
0005, 0006 e 0007; docs/estrategias/trend_sma.md, catálogo/matriz modular,
docs/bancos e contratos afetados.
5. Fontes/testes/manifests/locks/pins atuais dos projetos existentes.

Reinspecione revisões/alterações e hashes. A baseline detalhada foi bot
81ec74611845950116e705c5310c19070234b1ad, docs
405e8a4bb572594d241cc9f67c3e6cb88ff0cba8 com agregador já modificado;
120/120 hashes analíticos conferiam. Não sobrescreva mudanças posteriores.
Se houver divergência ou regressão não explicada, registre impedimento e
não avance ao trabalho dependente. Prepare o guia 06A com casos pendentes
antes dos ensaios; use os comandos e aceites das seções 7–10.

Execute primeiro M1: mover modules/trading/src/cripto_bot para src/cripto_bot,
corrigir discovery/paths/fingerprint/comandos e validar regressões/wheel
antes de extrair qualquer regra. Registre artefatos do marco separadamente.
Só depois execute M2: criar core 0.1.0 em src/cripto_core com contratos,
Decimal, custos/sizing e SMA puros conforme mapa da seção 4. Core não
importa bot nem carrega HTTP/SQLite/DuckDB/ambiente/relógio implícito.
Estado da carteira, risco operacional, coordenação, backtest e persistência
continuam no bot. Preserve identidades de tipos/erros por reexports;
fonte única de regras, sem cópias divergentes ou import via sys.path.

Mantenha Python 3.13.15, uv 0.12.19, backend pinado e dependências mínimas.
Construa core antes de declarar fonte local do wheel; declare dependência
exata cripto-core==0.1.0 e atualize locks deliberadamente, sem upgrades laterais.
Use manifests/locks separados, sem workspace/Git agregador. Valide metadados
e instalação por wheels identificados, sem editable/PYTHONPATH/checkouts.
Execute qualidade/regressões da baseline, M1 e M2 conforme seção 9,
adaptando harness existente para seleção explícita de artefato e origem
de ambos os pacotes, sem apagar builds/ambientes/dados anteriores.

Somente local/PAPER/Spot/BTCUSDT/15m; nenhuma rede de mercado, mensagem,
AWS, credencial, modo privado, nova estratégia ou evolução BT-A–BT-F.
Testes usam sockets bloqueados, fixture e diretórios sintéticos únicos.
Não executar teste final real da 05, recriar registro final, converter
bancos ou regravar protocolo para aceitar novo fingerprint. Composição
alterada deve impedir retomada incompatível; relatório antigo permanece
somente leitura e conserva identidade selada. Novo hash inclui o core
realmente usado, não apenas versão de pacote ou fontes do bot.

Comprove A01–A16 com oráculos exatos, causalidade, limites, defaults,
replay e falhas/crash/publicação/locks aplicáveis; registrar resultados reais,
comandos, revisões, hashes, composição/locks e limitações em
/home/cams7/Dev/Cripto/docs/testes/sprint-06a-validacao.md e evidências JSON.
Gere relatório técnico legível, confira valores e revise visualmente.
Atualize README/API, arquitetura/ADRs, SMA/catálogo e bancos conforme impacto,
além do agregador/planejamento com estado verdadeiro. Documentação pendente
bloqueia conclusão. Termine com decisão por marco e rollback; não inicie
06B–06D nem promova modo automaticamente.
```

## 13. Fontes e registro do detalhamento original

Fontes oficiais consultadas em 26/10/2026: [setuptools — descoberta e layout src](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html), [uv — fontes de dependência](https://docs.astral.sh/uv/concepts/projects/dependencies/), [uv — lock/sync](https://docs.astral.sh/uv/concepts/projects/sync/) e [Python 3.13 — importlib.metadata](https://docs.python.org/3.13/library/importlib.metadata.html). Apoiam descoberta explícita, fonte local de distribuição, resolução locked e identificação de pacotes instalados; não exigem novas bibliotecas. A compatibilidade dos comandos/artefatos futuros com os pins locais será demonstrada na implementação, sem atualizar ferramentas pela versão corrente dessas páginas.

Nesta entrega: inspeção estática, conferência de hashes e versões/ajuda, especificação da etapa e atualização dos documentos de acompanhamento. Não houve implementação, build/sync, regressão, consulta de banco, nova avaliação financeira ou liberação do piloto. Próxima ação: revisão desta especificação antes de solicitar sua implementação.


## 14. Registro da implementação em 26/10/2026

Implementação posteriormente autorizada: baseline limpa do bot e 120/120 hashes analíticos conferidos. Baseline: 528 testes em 631,85 s. M1: layout `src/cripto_bot`, fingerprint/paths/harness corrigidos, qualidade/build/wheel e 528 testes em 732,34 s; aceite arquivado antes da criação do core. M2: core puro em Git independente, bot consumidor por wheel/lock, qualidade e 533 testes do bot em 581,65 s; core isolado com 54 testes em 0,42 s. Os 40 contratos selecionados passaram antes da suíte final, sem somá-los novamente ao total.

Três smokes de 22 fluxos cada mantiveram os saldos manual/SMA e as 48 curvas sintéticas. Origens bot/core em site-packages, core sozinho sem bot, falta/versão/conteúdo incompatível e retomada divergente testados. Reexportação do modelo sintético anterior preservou SQLite/resultado selado; registro real da janela final com hash inalterado. AST dos quatro stores SQLite idêntica à baseline; sem migração/DDL alterado.

A01–A16 aprovados no alcance técnico descrito, com [guia](../testes/sprint-06a-validacao.md), [evidências](../testes/sprint-06a-evidencias.json), [HTML revisado](../testes/relatorios/sprint-06a/report.html) e [ADR 0008](../decisoes/0008-core-e-identidade-da-composicao.md). Cache frio completo não demonstrado: dependências externas instaladas da baseline foram reutilizadas após versão/RECORD conferidos, sem downloads; bot/core foram construídos e instalados por wheels. Artefato local precisa estar disponível para sync locked.

Fontes/artefatos anteriores preservados, sem commit/remoto/publicação. Sem rede de mercado, mensagens, AWS, operação privada, nova avaliação final real ou implementação de 06B–06D. 06B fica elegível para detalhamento/revisão; o piloto continua dependendo das extrações seguintes.
