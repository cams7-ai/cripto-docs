# Sprint 06B — Extração de `cripto-market-data`

Detalhamento e execução: 26/10/2026. **Estado: IMPLEMENTADA E VALIDADA no escopo offline da 06B.** B-M1/B-M2/B-M3 e B01–B18 registrados no [guia](../testes/sprint-06b-validacao.md), nas [evidências](../testes/sprint-06b-evidencias.json) e no [relatório](../testes/relatorios/sprint-06b/report.html). 06C fica elegível para detalhamento/revisão; 06D e 07 continuam pendentes. As seções 2 e 13 preservam a inspeção histórica; comandos futuros das seções 10/12 foram executados conforme o registro da seção 14.

Referências: [planejamento](../planejamento.md), seções 4.5–4.10, 5, 6.5, 9.2 e 13; [agregador 06](sprint-06.md); [06A](sprint-06a.md), [guia 06A](../testes/sprint-06a-validacao.md) e [evidências 06A](../testes/sprint-06a-evidencias.json); [Sprint 02](sprint-02.md), [guia 02](../testes/sprint-02-validacao.md), [ADR 0003](../decisoes/0003-coleta-publica-e-persistencia-local.md), [mercado SQLite](../bancos/market-sqlite.md); [Sprint 05](sprint-05.md), [guia 05](../testes/sprint-05-validacao.md), [ADR 0006](../decisoes/0006-backtest-historico-e-protocolo.md) e [ADR 0008](../decisoes/0008-core-e-identidade-da-composicao.md). Também consultar [arquitetura](../arquitetura.md), [arquitetura modular](../arquitetura-modular.md), catálogos de [bancos](../bancos/README.md)/[estratégias](../estrategias/README.md) e [matriz modular](../testes/estrategias-modulares-validacao.md).

## 1. Objetivo e incremento demonstrável

Criar biblioteca/CLI Python independente de dados públicos, com fontes em `cripto-market-data/src/cripto_market_data`, consumida pelo bot por wheel identificado. Extrair coleta, parsers/qualidade, portas/DTOs de mercado, store/checkpoint e exportações, mantendo `cripto-bot collect-market` compatível por delegação e leitura dos manifestos pelo backtest existente.

A entrega deve demonstrar, sem rede real: biblioteca/CLI funcionando sem bot instalado; coleta fixture pelo bot e pela CLI própria; repetição/cruzamento entre consumidores sem duplicar candles; retomada/falhas/lock preservados; exportação consumível pelo preparo histórico, sem reavaliar a janela final real. Dados físicos continuam nos locais configurados; extrair ownership de código não significa mover bancos.

## 2. Baseline conferida e dependências

Inspeção somente leitura em 26/10/2026. Não foram executadas suítes ou abertos bancos nesta revisão.

| Dependência | Resultado observado | Exigência antes de implementar |
|---|---|---|
| D01 — 06A | Evidências com A01–A16 aprovados; **127/127 hashes de fontes/controles e 6/6 artefatos conferidos**, zero divergência | Reinspecionar mudanças posteriores e reproduzir regressões pertinentes |
| D02 — Repositórios | Bot HEAD `a9dde2e93043be3aa11c603a2b46c60a59e4a174`; core HEAD `e666e7e23dcb421177c80838a28c230d4433bdf2`; docs HEAD `edfa405aa7558d1efa3493f2f0e5f557c6999eaf`; todos limpos no início | Registrar revisões/alterações efetivamente usadas; preservar trabalho posterior |
| D03 — Projetos/layout | Bot e core existem com `src/`; `cripto-market-data` e `cripto-analytics` ainda não existem | Criar somente o projeto de dados na implementação, com Git próprio |
| D04 — Ferramentas/composição | Manifests: Python `>=3.13,<3.14`, pin 3.13.15, uv 0.12.19, setuptools 84.2.0; bot exige core 0.1.0 por wheel local | Preservar pins/versões e wheel core validado; mudança necessária exige justificativa/revalidação |
| D05 — Coleta e persistência | API pública restrita, fixture via MockTransport, store v1, hashes/manifestos e lock disponíveis | Inventariar contratos/DDL/paths/proveniência e montar oráculos sintéticos antes de mover |
| D06 — Consumidores | Backtest importa parsers do bot e verifica schema/parser e quatro arquivos exatos dos manifestos | Preservar compatibilidade e source única; não ampliar o motor histórico nesta extração |
| D07 — Limitação herdada | 06A não demonstrou instalação completa com cache frio; dependências externas foram reutilizadas após versão/RECORD conferidos | Registrar cache/origem reais e impedimentos; não presumir downloads disponíveis ou omitir adaptação de ambiente |

533 testes bot e 54 core são resultados históricos da 06A, não execuções desta revisão nem contagens mínimas fixas. As revisões Git atuais consolidam fontes que conferem com os hashes da entrega; não reescrever evidências anteriores para trocar seus HEADs. **Elegível para detalhamento/revisão de 06B**; implementação depende de solicitação e da baseline reproduzida. Falha prévia interrompe trabalho dependente.

## 3. Escopo e exclusões

Python/local/PAPER, somente Binance Spot/BTCUSDT/15m, candles fechados. Preservar APIs/rotas, custos/limites financeiros, flags, modos, defaults e resultados existentes. A biblioteca de dados não é estratégia nem gera intenção/ordem/reserva; nenhuma feature flag nova é necessária para essa dependência de dados. Instalar a biblioteca não habilita módulo ou coleta implícita.

Rede real não é necessária ao aceite desta extração. Todos os ensaios previstos usam fixtures/MockTransport e sockets bloqueados. Manter `--allow-network` como opt-in explícito do produto para a fonte pública, testado com fakes; sua implementação não autoriza coleta real nesta Sprint. Não executar rede de mercado, notificações, credenciais, endpoints privados ou `order/test`.

Fora do incremento: 06C/análises, piloto 06D, AWS/S3/DynamoDB, daemon/async/WebSocket, novos ativos/filtros/rotas, corretores externos, estratégias, parcial histórico, otimização/ranking/walk-forward e BT-A–BT-F. Não recriar `cripto-backtest` ou outras bibliotecas. DuckDB/Parquet e relatórios financeiros permanecem no bot até 06C; biblioteca de dados não os importa.

## 4. Fronteiras e inventário de extração

Dependências permitidas: `cripto-bot → cripto-market-data → cripto-core` e `cripto-bot → cripto-core`. Nenhuma dependência de market-data para bot/analytics ou de core para consumidores. Chamadas síncronas Python, sem serviço remoto, framework de plugins ou Git agregador.

| Origem no bot | Destino proposto em `cripto_market_data` | Compatibilidade/fronteira |
|---|---|---|
| `domain/market.py` | `domain/market.py`: Candle, STEP/SCHEMA/PARSER e parsers/janelas de mercado | Helpers já extraídos vêm de core; imports antigos reexportam os mesmos tipos/funções; não mover regras financeiras ou duplicar MarketError |
| `application/ports.py` | `application/ports.py`: RawResponse, MarketSource, MarketStore | Mesmos campos, Protocols e semântica de JSON/hash; bot mantém reexports para consumidores/testes |
| `application/collect_market.py` | `application/collect.py`: Progress e collect_market | Mesma paginação/checkpoint/contagens; relógio/orçamento recebidos por portas/callbacks |
| `adapters/binance/public.py` e `fixture.py` | Adapters de mesma responsabilidade | Guard, Budget, PublicSource e fixture_source preservados; sem import de logging ou settings do bot |
| `adapters/storage/market_sqlite.py` | `adapters/storage/sqlite.py` | Mesmo store v1/lock/DDL/transações; paths vêm do chamador, não de site-packages |
| Parte de `adapters/storage/market_export.py` | `adapters/storage/export.py`: exportação específica de mercado | Publicação/arquivos/hash canônico preservados; versão/proveniência do produtor recebidas explicitamente |
| `MarketSettings` em `domain/models.py` e `MarketInput` em `adapters/config.py` | DTO em `domain/settings.py` e validação compartilhada em `adapters/config.py` | Um DTO/schema de mercado, reexports no bot; Settings financeiro e configuração global continuam no consumidor |
| `entrypoints/market.py::execute_collection` | Caso de uso/composição de coleta na biblioteca + adaptadores CLI | Wrapper do bot mantém assinatura, envelope/exit codes e guard global; CLI própria não importa o bot |

**Acoplamento obrigatório a resolver:** `market_export.py` também expõe `code_revision` e `source_fingerprint`, importados pelos fluxos paper/strategy/backtest. Essas responsabilidades de identidade do consumidor ficam no bot (por exemplo, em `adapters/provenance.py`), com fachadas compatíveis. Não movê-las para a biblioteca carregando `cripto_bot` por dependência inversa. O exportador de dados recebe contexto/versão por argumento; não consulta `metadata.version("cripto-bot")` ou a raiz Git do bot por conta própria.

As funções `utc_now`/`utc_timestamp` hoje vêm do logging do bot: introduzir no projeto de dados apenas o adapter temporal necessário, com comportamento UTC equivalente e relógio substituível nos testes. Não ampliar core com filesystem, relógio implícito, Git, HTTP ou SQLite. Nenhuma mudança do wheel core 0.1.0 é prevista; necessidade imprevista requer análise antes de alterar a composição.

O bot continua dono de `Settings`, modo/credenciais, configuração de estratégias, carteira/ledger, risco, backtest e registro final. O schema MarketInput deve ter fonte única; os entrypoints continuam responsáveis pela validação dos seus próprios arquivos/namespaces, resolução segura de paths e mapeamento para diagnóstico sanitizado. Não extrair configuração financeira para a biblioteca de dados nem criar módulo genérico antecipado para todos os projetos.

## 5. Configuração, raízes e CLI

A API recebe `MarketSettings` já validado, com raiz explícita, paths resolvidos e contexto do chamador. Não descobrir a raiz pela instalação do wheel, importar checkout irmão ou alterar paths para fazer testes passarem. No bot, preservar a descoberta de raiz atual pelo manifest e a resolução relativa ao cwd, incluindo `contained`/symlinks dos demais módulos. Erros do schema de mercado continuam mapeados para ConfigError/exit 2, sem traceback/valores arbitrários em diagnósticos.

CLI própria proposta, **a implementar**, console script `cripto-market-data`:

- `check-config --root <diretório-absoluto> --config <arquivo>`: somente validação, sem banco/cliente/rede.
- `collect-market --root <diretório-absoluto> --config <arquivo> --start <UTC/offset> --end <UTC/offset> [--allow-network]`: mesma coleta por delegação à API.

`--root` é a raiz explícita de contenção dos dados, existente dentro de `/home/cams7/Dev/Cripto`, independente do diretório instalado; não precisa coincidir com o repositório do pacote. Permite, por escolha explícita, apontar a CLI para os datasets existentes dentro do bot, sem mover arquivos. Não é endpoint nem override de mercado. Paths relativos de fixture/data_dir continuam relativos ao cwd; após resolver symlinks, precisam estar contidos em root e não podem ser a própria raiz. Configuração/raiz inválidas falham antes de criar store/cliente; não criar raiz por fallback.

A CLI própria aceita TOML mínimo `mode="PAPER"` e tabela `market`, com os campos/defaults atuais. Campos financeiros/estratégicos não são interpretados; rejeitar extras em vez de ativar funções do bot. Preservar rejeição de credenciais Binance, modo não PAPER e configuração inválida; não carregar .env. Não introduzir namespace de overrides novo. O bot conserva seu contrato global, incluindo CRIPTO_BOT_MODE e rejeição de variáveis desconhecidas. A CLI de dados não herda flags de estratégias nem se torna outro modo financeiro.

Defaults de mercado: source fixture/binance_public explícito, símbolo BTCUSDT e intervalo 15m, page_limit 1–1000 (default 1000), max_pages 1–10 (default 10); fixture exige arquivo e fonte pública o proíbe. Janela fechada/alinhada, capacidade limitada por página×paginação, UTC/offset explícito, sem aceitar candle aberto. Sem configuração de mercado, falhar claramente; não iniciar coleta porque core/market-data foram instalados.

Exit codes/envelope: 0 sucesso, 2 argumentos/configuração/janela/opt-in inválidos, 3 falha operacional/coleta incompleta, 1 falha interna. Um JSON de resultado por sucesso/falha operacional e evento JSON sanitizado em stderr, com run_id/instante e `mode=PAPER`, `orders_sent=0`; `--help` textual. Preservar resultado de `cripto-bot collect-market`, inclusive status, manifest, complete e contagens. Formato/nomes específicos da CLI própria serão confrontados com este contrato na implementação, sem atribuir existência aos comandos nesta revisão.

## 6. Rede, qualidade e orçamento preservados

Manter host fixo `https://data-api.binance.vision` e somente os GETs `/api/v3/time`, `/api/v3/exchangeInfo`, `/api/v3/klines`, `/api/v3/ticker/bookTicker`, seus parâmetros exatos, par/intervalo e timezone 0 atuais. HTTPS/TLS verificado, `trust_env=False`, sem redirects, autenticação, headers de credencial, proxy herdado ou URL arbitrária. Guard antes do transporte; nenhuma rota privada ou mutação, inclusive `order/test`.

Não alterar limite de corpo/fixture de 5 MiB, validação dos campos/OHLC/volumes/ordenação, tratamento de candle aberto, duplicata igual, conflito/lacuna e falta de progresso. Conservar RawResponse bruto/hash, metadados extras e distinção entre horários de mercado/recebimento/processamento. Não inventar timestamp de mercado no bookTicker ou aplicar metadados atuais como prova de regras históricas.

Preservar orçamento monotônico de 90 s, timeouts/tentativas transitórias existentes, rejeição sem retry de contrato e tratamento de 429/418/Retry-After, inclusive fallback numérico já implementado. `not_before` persistido continua global aos datasets do mesmo banco, não de todo IP/host. Fixture usa os mesmos parsers/rotas via MockTransport, rejeita `--allow-network`; fonte pública sem esse opt-in falha antes de criar cliente/store. Testar ambos os entrypoints com transporte falso, sem transformar consulta de documentação em teste de acesso Binance.

## 7. Store, exportações e proveniência

Preservar `market.sqlite3` v1, DDL/constraints/índices, writer flock, foreign_keys, FULL, transações explícitas e confirmação atômica de bruto/candles/checkpoint por página. Prefixo é verificado antes de retomar; conflito não sobrescreve candle. Banco incompatível/corrompido falha sem reset. O caminho/arquivo de lock é o mesmo quando CLI e bot apontam para o mesmo diretório; escritores concorrentes devem competir pelo mesmo lock.

IDs não mudam: fonte pública `binance_public:https://data-api.binance.vision:v1`; fixture `fixture:<sha256-do-arquivo>:v1`. A localização do pacote e seu nome não criam dataset novo. Não deslocar diretórios, copiar banco para o novo repositório, reiniciar checkpoint/bloqueio ou mover dados financeiros. Testar retomada de store sintético criado pela baseline antes da extração, depois acesso alternado pelos consumidores.

Exportar o conjunto atual: `manifest.json`, `candles.jsonl.gz`, `raw.jsonl.gz`, `snapshots.json`, `provenance.json`, em diretório temporário no mesmo filesystem e rename final após hashes/fsync existentes. O campo `files` do manifesto mantém **exatamente os quatro arquivos de dados atuais**: o leitor histórico `_source` rejeita outro conjunto. Preservar schema 1, parser spot-market-v1, complete, par/intervalo/janela, source, contagem e hashes; nenhum Parquet/DuckDB nesta extração.

Hash canônico dos candles exclui relógios/run_id/proveniência; permanece igual para mesmas entradas. Manifesto inteiro e arquivos com tempos/IDs podem ter hashes distintos, que não significam alteração dos candles. Não exigir igualdade de bytes brutos HTTP entre fontes diferentes; comparar conteúdo bruto/hash da mesma resposta fixture e campos normalizados, distinguindo metadados de aquisição.

Versão/proveniência do produtor são explícitas: wrapper do bot conserva semântica de `package_version`, configuração e revisão do bot; CLI própria identifica sua distribuição/composição. Não rotular uma execução standalone como se o bot estivesse instalado. Adições de proveniência devem preservar o leitor atual e ser documentadas/testadas sem alterar schema silenciosamente. Falha após commit preserva banco; repetir pode reexportar sem duplicar candles. Exportação não reexecuta estratégia ou gera fill.

No bot, ampliar identidade da 06A com `cripto_market_data==0.1.0` efetivamente instalado, inventário/RECORD e hash do wheel no lock. Mudança apenas no pacote de dados deve mudar fingerprint e impedir retomada sob protocolo congelado diferente. Não substituir a identidade histórica para fazê-lo passar; `backtest-report` mantém leitura/reexportação selada. Na CLI própria, identificar arquivos instalados de market-data/core, configuração e raiz explícita; não depender do Git ou código do bot na raiz que contém os dados. Não mover lógica de inspeção de pacotes/locks para core.

## 8. Empacotamento, versões e marcos

Novo projeto `/home/cams7/Dev/Cripto/cripto-market-data`, Git independente, sem commit/remoto/publicação implícitos. Pacote `src/cripto_market_data`, py.typed, README/API, manifest/lock/pin, testes e build próprios; não criar analytics. Distribuição inicial proposta 0.1.0, Python `>=3.13,<3.14`, pin 3.13.15, uv 0.12.19 e backend setuptools 84.2.0.

Dependências de produção: `cripto-core==0.1.0`, HTTPX no intervalo já usado `>=0.28,<0.29` e Pydantic `>=2.12,<3` para schema de fronteira compartilhado. Não adicionar ORM, pandas, NumPy, DuckDB ou SDK. Preservar resoluções da baseline quando compartilhadas; explicar alterações necessárias. Core permanece puro/invariante. Bot pode remover dependência HTTPX direta somente se não houver uso direto remanescente e testes/lock comprovarem a composição; não fazê-lo apenas por organização estética.

Fonte local planejada do core no novo projeto: o wheel já validado em `../cripto-core/dist/06a-final/cripto_core-0.1.0-py3-none-any.whl`. Construir market-data antes de declarar no bot a dependência exata `cripto-market-data==0.1.0` e fonte:

```toml
# Fragmento proposto do manifest do bot; ainda não aplicado
[tool.uv.sources]
cripto-core = { path = "../cripto-core/dist/06a-final/cripto_core-0.1.0-py3-none-any.whl" }
cripto-market-data = { path = "../cripto-market-data/dist/06b-final/cripto_market_data-0.1.0-py3-none-any.whl" }
```

Validar metadados normais de dependências nos wheels, sem paths absolutos/editable/checkouts. Guardar os novos artefatos em `cripto-market-data/dist/06b-final/` e `cripto-bot/dist/06b-final/`, preservando 06A e core. Cada projeto tem lock próprio; nenhuma resolução normal atualiza lock automaticamente, usar `--locked`. Fonte local exige artefato disponível, não equivale a publicação em índice.

Marcos de implementação: **B-M1**, baseline/oráculos/banco sintético e inventário; **B-M2**, biblioteca/CLI standalone com wheel/core e contratos sem bot; **B-M3**, bot delegando à biblioteca, identidade ampliada e regressões da composição. Não aposentar a implementação anterior antes de validar consumidor/fachadas; a entrega final mantém uma única implementação. Core/dados devem importar/testar sem bot, inclusive em ambiente com somente esses wheels.

## 9. Matriz de aceite

Todos os casos abaixo estão **NÃO EXECUTADOS** para 06B. Cobrem AC11 e os casos comuns aplicáveis do agregador, sem declarar aceites de 06C/06D.

| ID | Cenário | Resultado obrigatório |
|---|---|---|
| B01 | Baseline e marcos | Hashes/revisões, oráculos e store sintético anterior preservados; validação standalone antes da conclusão da integração |
| B02 | Dependências/DTOs | Sem imports de bot/analytics em market-data ou consumidores no core; RawResponse/Candle/MarketSettings/MarketError e imports legados compatíveis, sem cópias divergentes |
| B03 | Configuração/raiz | Extra/tipo/credencial/modo/par/janela inválidos, fixture/source inconsistente e paths/symlinks fora da raiz falham antes de efeitos; root explícito da CLI não depende de instalação |
| B04 | Opt-in/guard HTTP | Ambas as CLIs preservam opt-in; fakes comprovam rejeição de mutações/rotas/hosts/auth/redirect/proxy e ausência de cliente/store na rejeição antecipada |
| B05 | Qualidade | Mesmo parser/DTO/valores normalizados e contagens; candle aberto, OHLC inválido, corpo excessivo, duplicata conflitante, lacuna/ordem/falta de progresso rejeitados |
| B06 | Paginação/retomada | 2 candles na primeira fixture e 0 na repetição; prefixo/checkpoint/limite de páginas e retomada equivalentes à baseline; IDs de dataset preservados |
| B07 | Transações/concorrência | Bruto+candles+checkpoint atômicos, rollback/morte/falha sem avanço indevido; bot e CLI própria no mesmo diretório usam o mesmo lock |
| B08 | Throttle/tempo | Orçamento/timeout/retry, 429/418/Retry-After e not_before persistidos conforme baseline; outro dataset do mesmo banco respeita bloqueio, sem alegação distribuída |
| B09 | Manifestos | Mesmos quatro arquivos em files, parser/schema/candles hash e qualidade; hashes de arquivos/proveniência consistentes e produtor corretamente identificado |
| B10 | Publicação/falha | Falha antes/depois de commit/publicação preserva estado confirmado; snapshot parcial não é sucesso, repetir reexporta sem duplicação |
| B11 | Compatibilidade do store | Store sintético criado pelo código anterior abre/retoma sob pacote novo, sem DDL/migração/reset; schema/corrupção incompatíveis continuam rejeitados |
| B12 | Consumidor histórico | Novo manifesto passa pelo prepare/validação de dados atual; fixture histórica/regressões iguais, sem mudança no motor ou janela final real |
| B13 | Proveniência | Alterar somente market-data muda fingerprint; versão/RECORD/instalação incompatível é rejeitada; biblioteca não busca bot para obter identidade |
| B14 | Retomada/relatório | Protocolo selado sob composição antiga rejeita nova execução, mas reexporta snapshot anterior em leitura sem fills ou alteração do SQLite/registro final |
| B15 | Wheel/CLI isolados | Core+market-data sem bot executam check-config/fixture; integração instala três wheels em ambiente novo, sem editable/PYTHONPATH/checkout irmão; falta/troca da dependência falha claramente |
| B16 | Regressões/flags | CLI/defaults paper/strategy/backtest, oráculos financeiros, causalidade, risco/replay/guards preservados; nenhuma ativação implícita ou private/continuous |
| B17 | Documentação/relatório | README/API, exemplos/CLI, arquitetura/ADRs, bancos/catálogos e SMA quando afetada confrontados com código/testes; relatório legível derivado e revisado visualmente |
| B18 | Conclusão | B01–B17 e evidências por composição aprovados, limitações/custos/rollback explícitos; 06C apenas elegível para detalhamento, 06D/07 pendentes |

## 10. Sequência e comandos previstos

1. Reinspecionar baseline, preparar guia pendente, executar qualidade/regressões offline e capturar store/exports sintéticos antes de extrair.
2. Criar apenas o projeto de dados, extrair domínio/portas/caso de uso/adapters/schema de mercado; eliminar dependências inversas de logging/settings/proveniência.
3. Implementar CLI própria com root/config/opt-in explícitos; construir wheel e validar standalone com core, sem bot.
4. Integrar bot por delegação/fachadas, declarar wheel/dependência/lock e ampliar identidade; verificar processos alternados/concorrentes e consumidores do manifesto.
5. Executar contratos, falhas, regressões financeiras/históricas sintéticas, builds e smoke da composição; confrontar banco/DDL/proveniência/registro final preservados.
6. Gerar relatório técnico, conferir dados e visual, atualizar documentação/evidências e registrar decisão por marco. Não iniciar 06C/D automaticamente.

Comandos **já existentes**, para a baseline futura no bot; não executados nesta revisão:

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
uv run --locked --offline pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
WHEEL_SMOKE_STAGE=final uv run --locked --offline python tests/wheel_smoke.py
```

Preservar configuração/ambientes do smoke 06A; o último comando pressupõe seus artefatos e ambiente existentes. Nova implementação deve acrescentar seleção explícita de artefatos/ambiente 06B ao harness, sem reciclar o marco final da 06A ou apagar seus resultados. Criar teste standalone para o novo console com `-I`, cwd neutro, sentinel/probe de sockets e diretório de dados sintético dentro da raiz declarada.

Após existir o novo projeto, comandos **planejados** de build/qualidade:

```bash
cd /home/cams7/Dev/Cripto/cripto-market-data
export UV_CACHE_DIR="$PWD/.uv-cache"
uv lock --offline
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
uv run --locked --offline pytest -q --cov=cripto_market_data --cov-branch
uv build --offline --out-dir dist/06b-final
```

A mudança declarada no bot exige um `uv lock --offline` deliberado; depois sync/run locked. Build final do bot: `uv build --offline --out-dir dist/06b-final`. Instalação de teste recebe explicitamente core 06A, market-data 06B e bot 06B; dependências externas vêm dos locks. Documentar criação de ambiente **novo**, export de requisitos, invocação do harness, códigos/saídas e hashes reais antes de declarar aprovação. Não sobrescrever artefato sob identidade antiga.

Cache frio pode estar indisponível, como na 06A. Em falta de pacote, registrar tentativa/impedimento e usar somente alternativa verificável autorizada, como distribuições locais da baseline após versão/RECORD conferidos, sem upgrade silencioso. Se houver reutilização, distinguir de instalação completa com cache frio. Testes/CLI desta etapa permanecem offline; nenhuma falha de instalação libera rede de mercado.

## 11. Evidências, documentação, custos e recuperação

Na implementação, criar `docs/testes/sprint-06b-validacao.md` como roteiro inicialmente pendente e preencher resultados efetivos; gerar `docs/testes/sprint-06b-evidencias.json` com execuções observadas. Esta revisão define os caminhos, sem criar placeholders. Logs/oráculos/archives em diretórios identificados `reports/sprint06b/` dos projetos, com fontes/configs/locks/revisões e hashes de wheels, schema/manifestos e dados sintéticos. Não versionar bases operacionais/credenciais nem reescrever evidências 01–06A.

Criar README/API do novo projeto e atualizar bot, exemplos/comandos, arquitetura central/modular e ADRs de extração/identidade, com adendo ao ADR 0003 preservando sua decisão histórica. Atualizar documento/catálogo de mercado e compatibilidade do leitor histórico; ausência de DDL alterado precisa de comprovação e registro. Qualquer mudança de schema/formato exige decisão/plano antes de aplicá-la, sem migração automática. Se interfaces/dependências da SMA forem afetadas, atualizar seu documento/catálogo; não criar documento fictício de estratégia para biblioteca de dados ou módulos futuros.

Relatório HTML ou formato equivalente derivado de evidências: dados coletados sintéticos/contagens/hash, retomada, rejeições/erros, limites/rede/lock, metadados do produtor e resultados do consumidor. Conferir números/manifestos e revisar visualmente. Não repetir backtest econômico para montar relatório. PDF adicional só se necessário à apresentação; não é dependência do runtime.

Custos: CPU/disco/cache local, armazenamento de bruto/SQLite/exports e testes de falha; sem AWS ou nova coleta de mercado. Medir tempo/memória/volume pertinente sem prometer desempenho melhor por separar pacotes. Preservar artefatos 06A e baseline 06B; limpar somente cache/ambiente comprovadamente descartável, sem apagar dados únicos.

Rollback restaura a composição bot/core anterior e locks compatíveis, sem reset destrutivo ou sobrescrita de trabalho posterior. Dados físicos, checkpoints, bloqueios e registro final permanecem. Conferir backups sintéticos consistentes e compatibilidade de leitura; incompatibilidade inesperada mantém a etapa pendente, não autoriza copiar/reiniciar bancos. Somente após B01–B18/documentação aprovados, 06C torna-se elegível para detalhamento/revisão; o piloto requer 06C e o gate da 07 requer 06D.

## 12. Prompt autossuficiente para implementação futura

O bloco é um contrato para solicitação posterior, **não executado por esta criação documental**.

```text
Implemente somente a Sprint 06B em /home/cams7/Dev/Cripto, criando apenas
/home/cams7/Dev/Cripto/cripto-market-data, com src/cripto_market_data e Git
independente. Consumidor: /home/cams7/Dev/Cripto/cripto-bot; biblioteca pura
existente: /home/cams7/Dev/Cripto/cripto-core; docs centrais em
/home/cams7/Dev/Cripto/docs. Não crie analytics/backtest/outros projetos,
remoto/publicação/commits ou altere referências externas automaticamente.

Leia/verifique as dependências nesta ordem:
1. docs/planejamento.md (4.7–4.10, 5, 6.5, 9.2 e 13).
2. docs/sprints/sprint-06.md e sprint-06b.md integralmente.
3. docs/sprints/sprint-06a.md, docs/testes/sprint-06a-validacao.md e
sprint-06a-evidencias.json, incluindo limitação de cache e artefatos.
4. docs/sprints/sprint-02.md, guia/evidências 02, ADR 0003 e bancos/market-sqlite.md;
Sprint 05/guia, backtest-sqlite e analytics, ADRs 0006/0007/0008;
arquitetura central/modular, SMA/catálogos e matriz modular aplicável.
5. Fontes/testes/manifests/locks/pins atuais dos três projetos existentes.

Reinspecione revisões/alterações e preserve trabalho/dados/segredos. No
detalhamento, bot a9dde2e93043be3aa11c603a2b46c60a59e4a174, core
e666e7e23dcb421177c80838a28c230d4433bdf2 e docs
edfa405aa7558d1efa3493f2f0e5f557c6999eaf estavam limpos; 127 hashes e seis
artefatos 06A conferiam. Não presuma nova baseline igual sem verificar.
Crie o guia 06B com casos pendentes antes de executar. Reproduza regressões
offline e preserve store/export sintético anterior à extração para comparar.
Divergência/falha de pré-requisito bloqueia trabalho dependente.

Execute B-M1 -> B-M2 -> B-M3 da seção 8. Extraia domínio/DTOs/portas,
paginação, cliente público/fixture, store/checkpoint/exportação e schema de
mercado conforme seção 4. Core continua puro/invariante; mercado depende
somente de core e adapters próprios, sem importar bot/analytics. Carteira,
risco, coordenação, flags, backtest, registros e configuração financeira
continuam no bot. Preserve classes/reexports e mantenha uma fonte das regras.

Separe o exportador de dados das funções code_revision/source_fingerprint
usadas por paper/strategy/backtest. A biblioteca recebe proveniência/versão
do produtor; não consulta metadata do bot ou importa seu logging/settings.
Implemente CLI própria check-config/collect-market com --root absoluto e
TOML mínimo da seção 5, sem banco/rede na validação. Wrapper do bot conserva
assinatura, JSON/status/exit codes/configuração e validação de credenciais.
Não derive raiz de dados de site-packages ou mova diretórios para facilitar
imports. Mesma pasta de dados exige mesmo writer lock nas duas CLIs.

Somente Python/local/PAPER/Spot/BTCUSDT/15m. Não executar rede real, mensagens,
AWS, credenciais, private/order/test, continuous, novos ativos/estratégias,
ranking/otimização/walk-forward ou BT-A–BT-F. Preserve guard HTTP, rotas,
HTTPS/TLS/no-proxy/no-redirect, orçamento/retry/429/418, not_before e limites.
Use fixtures/MockTransport/sockets bloqueados e diretórios sintéticos próprios.

Mantenha schema/store/IDs/checkpoints, quatro arquivos no campo files do
manifesto, parser e hash canônico dos candles; trate proveniência variável
separadamente. Não converter/mover/resetar bancos, alterar ledger ou recriar
registro final. Valide manifesto novo no preparo histórico existente, sem
reavaliar a janela final real. Amplie identidade instalada com market-data;
alteração isolada nele deve bloquear retomada congelada, sem impedir
backtest-report somente leitura da identidade selada anterior.

Crie manifest/lock/README/API/py.typed/tests/build do novo projeto, com pins
Python 3.13.15/uv 0.12.19/setuptools 84.2.0, core exato 0.1.0 e dependências
mínimas da seção 8. Construa wheel market-data antes de declará-lo no bot;
fonte local explícita, sem editable/PYTHONPATH/checkouts e sem upgrades
laterais. Preserve wheel/lock core e artefatos 06A. Registre cache real e
adaptações verificadas; falta de cache não autoriza downloads de mercado.

Execute qualidade/testes/build/smokes conforme seção 10 e comprove B01–B18.
Adapte harness para marco/ambiente 06B explícito sem reutilizar final 06A;
teste core+market-data sem bot e integração pelos três wheels instalados.
Inclua falta/versão/conteúdo incompatível, dataset/manifesto inválidos,
concorrência/rollback/morte/publicação, bot/CLI alternados no mesmo store,
regressões financeiras e preservação dos dados/registro final. Registre
comandos/saídas/versões/hashes/revisões e custos/limitações reais em
docs/testes/sprint-06b-validacao.md e sprint-06b-evidencias.json.

Atualize README/API, arquitetura/ADRs, bancos/catálogos e SMA se afetada;
gere relatório legível a partir das evidências, confira valores e revise
visualmente. Documentação pendente bloqueia conclusão. Atualize agregador/
planejamento com estado verdadeiro e rollback. Não inicie 06C/06D ou libere
07/modos privados automaticamente.
```

## 13. Fontes e registro do detalhamento

Fontes primárias consultadas em 26/10/2026: [HTTPX — transportes/MockTransport](https://www.python-httpx.org/advanced/transports/), [Binance — host de dados públicos](https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md), [Python 3.13 — sqlite3](https://docs.python.org/3.13/library/sqlite3.html) e [uv — fontes de dependências](https://docs.astral.sh/uv/concepts/projects/dependencies/). Sustentam os mecanismos já adotados; não autorizam ampliar rotas, trocar pins ou alegar teste real de conectividade. Reconfirmar a documentação das APIs efetivamente alteradas na implementação.

Registro histórico do detalhamento, anterior à implementação: leitura do planejamento/agregador/contratos e código atual, conferência dos 127 hashes e seis artefatos, estado/revisões Git e definição desta etapa. Não houve criação de projeto/guia vazio, movimentação de fontes/dados, instalação/build/suíte, abertura de banco, coleta ou nova avaliação econômica. Próxima ação: revisar esta especificação antes de solicitar sua implementação.


## 14. Registro da implementação em 26/10/2026

Prompt da seção 12 executado mediante solicitação posterior. B-M1 aprovado antes da extração: bot 533 testes/22 comandos, fontes e store sintético preservados. B-M2 aprovado antes de integrar: projeto Git/src independente, 120 testes, qualidade/build e CLI por wheels core+dados sem bot/analytics. B-M3: bot por fachadas/delegação, somente dependência market-data acrescentada sem mudar versões anteriores, 537 testes, qualidade/build e 22 comandos com três wheels instalados.

B01–B18 aprovados no escopo offline, com provas detalhadas no guia/JSON e relatório revisado visualmente. Store/DDL/checkpoints/IDs/parser/quatro arquivos e hash dos candles preservados, mesmo lock entre CLIs, novo manifesto aceito pelo prepare. Oito respostas financeiras e 48 curvas sintéticas equivalentes; identidade incorpora o conteúdo de market-data. Retomada do protocolo antigo rejeitada; relatório antigo reexportado somente leitura, sem alterar SQLite ou registro final real. Core/artefatos 06A preservados. São evidências técnicas de regressão, sem nova conclusão econômica fora da amostra.

Biblioteca e bot têm README/API atualizados; arquitetura, ADRs 0003/0008/0009, bancos/catálogos e SMA refletem a extração. Cache frio completo não demonstrado: dependências externas da baseline reutilizadas após versão/RECORD/hash conferidos; wheels próprios novos instalados offline. Comandos, hashes, custos medidos, falhas de ensaio e rollback sem reset de dados constam no guia. Nenhum commit/remoto/publicação, rede de mercado, credenciais/ordens, mensagens ou AWS. 06C/06D e trilha BT não foram implementadas; não liberar 07 pelo aceite parcial.
