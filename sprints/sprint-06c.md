# Sprint 06C — Extração de `cripto-analytics`

Detalhamento e execução: 26/10/2026. **Estado: IMPLEMENTADA E VALIDADA no escopo offline da 06C; C01–C18 aprovados.** A reconstrução externa de quatro artefatos foi confirmada pelo responsável e verificada separadamente, mantendo hashes históricos/atuais e a limitação de recuperação exata. Ver [guia](../testes/sprint-06c-validacao.md), [evidências](../testes/sprint-06c-evidencias.json) e seção 15. 06D somente elegível para detalhamento/revisão; piloto/gate global/07 pendentes. As seções 2/13/14 preservam os estados anteriores.

Referências: [planejamento](../planejamento.md), seções 4.7–4.10, 5, 6.5, 9.2 e 13; [agregador 06](sprint-06.md); [06B](sprint-06b.md), [guia](../testes/sprint-06b-validacao.md) e [evidências 06B](../testes/sprint-06b-evidencias.json); [Sprint 05](sprint-05.md), [guia 05](../testes/sprint-05-validacao.md), [validação DuckDB/Parquet](../testes/duckdb-parquet-validacao.md) e suas [evidências](../testes/duckdb-parquet-evidencias.json). Consultar [arquitetura](../arquitetura.md), [arquitetura modular](../arquitetura-modular.md), ADRs [0006](../decisoes/0006-backtest-historico-e-protocolo.md), [0007](../decisoes/0007-duckdb-parquet-analitico.md), [0008](../decisoes/0008-core-e-identidade-da-composicao.md) e [0009](../decisoes/0009-market-data-e-proveniencia-do-produtor.md), catálogos de [bancos](../bancos/README.md)/[estratégias](../estrategias/README.md), [schema analítico](../bancos/backtest-analytics.md), [SMA](../estrategias/trend_sma.md) e [matriz modular](../testes/estrategias-modulares-validacao.md).

## 1. Objetivo e incremento demonstrável

Criar biblioteca/CLI Python independente em `cripto-analytics/src/cripto_analytics`, com Git próprio. Extrair apresentação JSON/HTML/CSV e projeções DuckDB/Parquet hoje acopladas aos relatórios do bot, recebendo snapshots e fluxos reconciliados por portas somente leitura. Bot conserva os comandos, validação/configuração, reconciliação, métricas oficiais e escrita financeira. Biblioteca depende de core, sem importar bot ou market-data.

Demonstrar offline: exportação com porta sintética sem bot instalado; leitura/consulta de export concluído pela CLI própria; bot delegando publicação pelos quatro wheels instalados; equivalência de formatos/valores/contagens e falhas recuperáveis por reexportação, sem novo sinal/fill. Instalação não habilita estratégias, coleta, processo contínuo ou negociação.

## 2. Baseline conferida e dependências

Inspeção somente leitura em 26/10/2026. As evidências 06B indicam APPROVED_OFFLINE_06B e B01–B18 aprovados. **185/185 hashes de fontes/configurações/testes/controles e 12/12 arquivos registrados em artifact_sha256 conferidos**, zero divergência. Os 12 incluem dois `.gitignore` de build, além dos dez wheels/sdists 06A/06B; não representam doze wheels. Nenhuma suíte reexecutada nesta revisão.

| Dependência | Resultado observado | Exigência antes de implementar |
|---|---|---|
| D01 — 06A/06B | Core e dados integrados; bot 537 testes, dados 120; B01–B18 aprovados, artefatos compatíveis | Reinspecionar hashes/mudanças e reproduzir regressões afetadas antes de extrair |
| D02 — Repositórios | Bot `0aeb7ef236f3be1cccff8136ff3135860706b0e9`; dados `1da6f4fe25c6940cc3e96416415ddf6f1ffcb4e9`; core `e666e7e23dcb421177c80838a28c230d4433bdf2`; docs `6a40ecc7288de2ed8e746eafc6fb879e1738286d`; todos limpos no início | Registrar revisões/alterações efetivamente usadas; preservar trabalho posterior e evidências anteriores |
| D03 — Layout/composição | Três projetos com src na raiz; analytics ainda não existe; core/dados 0.1.0 por wheels locais | Criar somente analytics, sem Git/workspace agregador, remoto, publicação ou commits automáticos |
| D04 — Pins | Python 3.13.15, uv 0.12.19, setuptools 84.2.0; DuckDB 1.5.6 no bot | Preservar pins/versões/artefatos existentes; nenhuma atualização lateral de dependência |
| D05 — Implementação analítica | backtest_analytics usa BacktestStore.db para contagens; backtest_report mistura snapshot financeiro, fluxos e apresentação | Criar adapter de leitura no bot; não levar Store/Wallet/State/SQLite ou cálculo oficial para analytics |
| D06 — Escala/formato | Schema analítico 1, VARCHAR exato, 256 MB internos, um thread, row group 8192 e publicação por diretório | Reproduzir precisão, contagens, vazio/parcial/concluído, restrições e teste largo de 150 mil decisões |
| D07 — Preservação | Relatório de protocolo antigo permanece legível; registro final comum pertence ao bot | Nenhuma migração/reset ou nova execução da janela final real para testar extração |
| D08 — Cache | 06B reutilizou distribuições da baseline após lock/versão/RECORD/hash conferidos; cache frio completo não demonstrado | Registrar instalação real e impedimentos; reutilização verificável não equivale a cache frio |

537/120 e os 54 testes históricos do core são resultados anteriores, não contagens mínimas fixas nem execuções desta revisão. Pré-requisito divergente bloqueia o marco dependente, com pendência/correção registradas; não marcar pronto por proximidade de planejamento.

## 3. Escopo, flags e exclusões

Somente Python/local/PAPER, Spot sem alavancagem, BTCUSDT/15m e fixtures já disponíveis. Preservar CLI/configuração/defaults de check-config, run-once, collect-market, paper-*, strategy-* e backtest-*. Biblioteca analítica não é estratégia; nenhuma feature flag nova. Flags de módulos, modo financeiro e configurações do mecanismo analítico são conceitos distintos. Memória/threads/row groups/paths permanecem configurações técnicas internas com os limites atuais; não virar parâmetro de risco ou permissão de execução.

Fora: novos ativos/estratégias, ranking/Sortino/seleção/otimização/walk-forward e BT-A–BT-F; métricas novas; reavaliação econômica; migração de SQLite para DuckDB; daemon/piloto/mensagens/AWS; rede real, credenciais, private/order/test, DEMO/TESTNET/LIVE, margem/short. Nenhum cliente Binance na análise. Não criar cripto-backtest nem novas bibliotecas auxiliares.

## 4. Ownership e inventário de extração

Caminhos da primeira coluna são relativos a `cripto-bot/src/cripto_bot`. Estrutura de destino é um contrato desta especificação, ainda não implementado.

| Origem atual | Destino/responsabilidade | Fronteira preservada |
|---|---|---|
| `adapters/storage/backtest_analytics.py`: COLUMNS, conversão, catálogo, consultas de contagens | `cripto_analytics/adapters/duckdb_export.py`, schemas em `domain/contracts.py` | Recebe contagens esperadas/fluxos por porta; não acessa store.db |
| `adapters/storage/backtest_report.py`: document e publicação CSV/JSON/HTML/manifesto | `cripto_analytics/presentation/backtest.py`, `application/publish.py` e adapters de arquivos | Recebe report pronto e ordem de segmentos explícita; preserva report/model/result_sha256 e arquivos |
| `adapters/storage/strategy_report.py`: render_html e publicação | `cripto_analytics/presentation/strategy.py` e publicação parametrizada | Modelo/proveniência/snapshot vêm do bot; nenhuma referência a StrategyWallet/StrategyStore |
| `adapters/storage/paper_report.py`: publicação JSON/manifesto | Publicação da biblioteca, preservando o conjunto atual de arquivos | PAPER manual não ganha HTML/Parquet implicitamente |
| summary/diagnostic de paper/strategy; snapshot/_series de backtest | **Continuam no bot**, com adapters de leitura estreitos em `adapters/storage/analytics_source.py` | Reconciliação, métricas, agregações mensais, redução visual e fingerprint financeiro não são reimplementados |
| `domain/backtest/metrics.py`, Wallet/State/risco e stores | **Continuam no bot**; helpers puros já extraídos continuam no core | Metrics ainda depende do estado financeiro do bot; não confundir sua localização real com o core já extraído |
| `adapters/provenance.py` | Continua política do consumidor, acrescentando analytics carregado | Inspeção existente de pacotes/RECORD reutilizada pelo bot; não copiar inspector para analytics nem criar analytics → market-data |
| Entry points e imports legados dos quatro relatórios | Wrappers/fachadas no bot | Mesmas assinaturas públicas, patch hooks usados pelos testes, status/JSON/exit codes e paths |

Dependências de código: bot → core/dados/análise; dados → core; análise → core. DuckDB entra por adapter com import tardio. Importar domínio/core ou executar check-config/NOOP não importa DuckDB; provar isso em subprocesso. Análise não importa settings/logging/Git/metadata do bot, nem SQLite/engine/métricas financeiras para calcular resultados.

As poucas constantes de apresentação necessárias, como ordem de segmentos, são fornecidas pelo bot ao renderer, evitando duplicar registro de variantes/perfis ou regras de benchmark. Schemas de arquivos pertencem à análise, não regras de seleção de estratégias. Preservar o uso atual de float apenas para coordenadas visuais de SVG; isso não transforma valores oficiais em float nem permite usá-los nas métricas/hashes.

### 4.1 Contratos de leitura e publicação

Definir tipos/protocolos em `cripto_analytics/domain/contracts.py` e `application/ports.py`, usando biblioteca padrão/core. API pública mínima documentada no README:

- `ReadonlyRows.iter_rows(table)` recebe somente `equity`, `trades` ou `decisions` e fornece mappings em ordem estável atual (`run_key,rowid`), com flatten de plan feito pelo adapter do bot e data_json original preservado. Consumo incremental; não materializar séries completas para converter.
- `ReadonlyRows.counts(table)` fornece mapa run_key → contagem da mesma visão reconciliada. Adapter do bot traduz trades para fills; nomes de tabelas físicas/SQL ficam no bot, sem parâmetro SQL livre na porta.
- `publish_backtest(report, rows, data_dir, run_id, *, segments)` recebe snapshot pronto, porta de leitura e raiz de publicação explícita; retorna Path do manifesto. Confere contagens SQL/relatório/porta e só publica o conjunto completo. A porta não oferece execute, commit, replay, wallet ou conexão mutável.
- Publicação de paper/strategy recebe report, data_dir/run_id e proveniência/modelo explícitos; renderizadores recebem somente o snapshot. Wrappers mantêm assinaturas antigas que recebem store, sem repassar o store concreto à biblioteca.

Bot reconcilia antes de criar a porta e mantém a proteção/visão consistente já usada durante snapshot/fluxos/contagens. Não liberar lock ou consultar contagens de geração diferente para acelerar exportação. Export não atualiza checkpoint financeiro. Testar porta fake independente e adapter contra stores reais sintéticos; type hints não provam ausência de efeitos por si só.

Lib usa PaperError do core para falhas de contrato/conversão; erros operacionais atuais são preservados. Ausência do pacote exigido pelo comando deve produzir diagnóstico fixo `ANALYTICS_DEPENDENCY_UNAVAILABLE`, exit 3, sem traceback/paths sensíveis nem publicação parcial. Falhas internas permanecem exit 1; configurações/argumentos inválidos exit 2. Não mascarar bug interno ou divergência financeira como dependência ausente.

## 5. CLI própria e caminhos

Console futuro `cripto-analytics`, sem dependência de bot/dados ou TOML financeiro. Dois comandos somente leitura de **exports históricos com camada analítica schema 1**; não abrem SQLite, reconciliam carteira ou reexportam a janela final. Renderização/publicação é API usada pelo bot e pela prova standalone com porta sintética; não criar um segundo motor de reconstrução de carteira na CLI.

| Comando planejado | Entrada | Saída/efeitos |
|---|---|---|
| `check-export --root ABS --manifest FILE` | Manifesto concluído de backtest e seus arquivos locais | Valida schema/modelo, paths, conjunto de arquivos, hashes e coerência de metadata/report/catálogo; JSON VALID, sem escrita |
| `query-export --root ABS --manifest FILE --view VIEW [--limit N]` | Mesmo export validado; VIEW entre curve-summary, decisions-counts e trades-counts | SELECT fixo sobre tabelas existentes; linhas com nomes de coluna, inteiros/boolean/NULL e strings exatas; sem cálculo financeiro novo |

Root obrigatório, absoluto, existente dentro de `/home/cams7/Dev/Cripto`; não precisa conter o pacote instalado. Manifest resolve a partir do cwd e precisa ficar na root, assim como todos os arquivos referidos. Rejeitar traversal, URLs, symlinks que escapem da raiz, arquivos ausentes/adulterados e diretórios `.pending-*`; nomes em files são basenames locais do contrato, nunca SQL/caminhos arbitrários. Não criar root, banco inexistente, diretório temporário ou cache na entrada ao validar/consultar. As configurações do bot e sua descoberta de raiz permanecem inalteradas.

Queries têm ordenação determinística pelas chaves das tabelas; limit inteiro 1–1000, default 1000; informar `truncated` se houver mais linhas, sem indicar conclusão de todas elas. Sem `--sql`, extensões, ATTACH, COPY, instalação ou override de engine/memória/risco. Catálogo aberto com `read_only=True`; restrições de rede/extensões aplicadas antes das consultas, sem spill/escrita no export. Teste deve detectar qualquer alteração/criação de arquivo durante ambas as operações.

Stdout JSON, stderr evento sanitizado, run_id correlacionado, mode=PAPER/orders_sent=0. Códigos: 0 sucesso, 2 argumento/root/view/limit inválidos, 3 export incompatível/incompleto/hash divergente/motor ou dependência indisponível, 1 interno. Identidade selada do protocolo/resultado é a do export, sem substituí-la por identidade do leitor. CLI não declara validação financeira independente: verifica consistência do snapshot publicado. Relatórios antigos sem arquivos analíticos continuam legíveis por seus consumidores anteriores; estes dois comandos os rejeitam explicitamente como formato não suportado, sem conversão automática.

## 6. Precisão, formatos e limites preservados

Schema analítico 1 e DDL conforme banco analítico existente. Valores financeiros/razões/IDs/data_json/as_of continuam VARCHAR; timestamps numéricos/export_row BIGINT, contagens inteiras; opcionais vazios do CSV tornam-se NULL. CSVs mantêm colunas/ordem, export_row começa em 1 por série. Nenhum cast financeiro silencioso para float ou DECIMAL(38), nem recálculo SQL de PnL/drawdown/retorno. Métricas oficiais usam o domínio Decimal de precisão 80 já existente; cálculos compartilhados do core não mudam.

Backtest mantém exatamente os dez arquivos em files: report.json, report.html, equity.csv, trades.csv, decisions.csv, equity.parquet, trades.parquet, decisions.parquet, analytics.duckdb e analytics.json. Manifesto permanece fora de sua própria lista. Catálogo: metadata, curve_summary, decisions_counts, trades_counts; PKs/tipos/nulabilidade e metadados preservados. Não adicionar proveniência como um décimo primeiro arquivo sem decisão de formato.

Paper manual mantém report.json e manifesto; strategy mantém report.json/report.html e manifesto. Manifestos preservam modelo, identidade financeira, contexto/proveniência e semântica complete atual. Pacote analítico não passa a produzir arquivos do exportador de mercado.

DuckDB **1.5.6**, um thread, memory_limit **256 MB**, Parquet ZSTD, ROW_GROUP_SIZE **8192** (alvo sujeito ao arredondamento do motor), spill somente no diretório pendente na exportação. Extensões automáticas desabilitadas; allowed_directories configurado antes de enable_external_access=false e lock_configuration=true. Query de catálogo é somente leitura e não pode ampliar permissões. Manter paths com apóstrofo por bindings, não concatenar valores recebidos em SQL. Esses controles não são promessa de sandbox para executar SQL arbitrário, que permanece fora da CLI.

## 7. Atomicidade, compatibilidade e proveniência

Fluxo: reconciliação/snapshot do bot → fluxos/CSVs → Parquet → contagens/resumos SQL confrontados → fechar catálogo/remover spill → analytics.json e hashes → manifesto → rename do diretório pendente. Preservar flush/fsync e restrições de run_id/colisão já aplicáveis a cada exportador; extração não deve reduzir durabilidade nem substituir export existente. Não alegar garantias novas de crash/power loss sem teste específico.

Falha de memória/conversão/contagem/escrita/publicação não altera journal/reserva/fill/checkpoint; não publica sucesso parcial. Export confirmado permanece intacto; `.pending-*` não é publicação. Reexportação gera diretório novo, sem reavaliar sinais. Morte antes/depois de rename e limpeza segura de temporário precisam ser testadas. Não apagar banco ou export único para recuperar.

Core e dados permanecem com wheels/locks/pins atuais. Bot acrescenta `cripto_analytics==0.1.0` à identidade runtime-composition-v1 com versão/origem/arquivos carregados/RECORD, sem editable para a dependência extraída. Alterar apenas analytics deve mudar fingerprint e bloquear nova execução sob protocolo congelado. Não copiar inspeção de RECORD para o projeto analítico: a política do bot já reutiliza o inspector existente de market-data.

Reexportação somente leitura de protocolo sintético selado na composição 06B preserva protocol_hash/result_sha256 e banco byte a byte. Se incluir informação do produtor atual, manter separada da identidade selada e dentro do formato compatível existente; não reescrever protocolo para esconder mudança. Bytes DuckDB/Parquet podem variar entre exports: comparar valores/tipos/ordem/contagens e hashes de cada publicação, não exigir igualdade financeira por hash binário do motor. A nova avaliação sintética usa novos diretórios/protocolos; não tocar a janela final real nem copiar/recriar seu registro em outro projeto.

Regressão financeira: preservar saldos/custos/decisões/causalidade e as 48 curvas da fixture. Diferenças legítimas de code_sha256/run_key/checkpoint_bytes devem ser enumeradas, sem remover métricas ou períodos da comparação. Resultados retrospectivos sintéticos provam compatibilidade; não constituem nova evidência econômica fora da amostra nem garantem desempenho futuro.

## 8. Empacotamento, versões e marcos

| Projeto/perfil | Composição prevista | Aceite |
|---|---|---|
| core e dados existentes | 0.1.0, artefatos 06A/06B imutáveis, próprios locks/pins preservados | Fontes/controles/artefatos conferidos; sem dependência inversa |
| analytics standalone | 0.1.0, Python >=3.13,<3.14/pin 3.13.15, uv 0.12.19, setuptools 84.2.0; produção core==0.1.0 + duckdb==1.5.6 | Git/src/py.typed/README/API/tests/lock; wheel sem bot/dados/HTTPX/Pydantic |
| bot integrado | core/dados atuais + analytics==0.1.0 por wheel local em dist/06c-final | Perfil local mantém comandos/defaults; quatro wheels instalados; apenas mudança necessária no grafo do lock |

Retirar dependência direta DuckDB do bot após delegação; ela passa a transitiva via analytics, sem alterar versão. Não inventar extra/flag obrigatória para comandos que já funcionavam na instalação padrão local. Dependência instalada não exige import antecipado: wrappers/imports tardios preservam core/domínio/check-config/NOOP sem carregar DuckDB. Separação de perfis mínimos de deployment, se necessária na 07, será validada naquela etapa.

Fonte local do novo projeto aponta para wheel core 06A; bot aponta para analytics wheel `../cripto-analytics/dist/06c-final/cripto_analytics-0.1.0-py3-none-any.whl`, além dos wheels core/dados atuais. Metadata de distribuição declara dependências normais por versão, sem paths absolutos. Não atualizar core/dados para acomodar um import indevido. Se contrato compartilhado realmente exigir mudança de core, registrar decisão/impacto e revalidar antes do marco dependente, sem presumir autorização para ampliar escopo.

Marcos obrigatórios, cada um com aceite registrado antes do seguinte:

1. **C-M1 — baseline:** guia pendente criado antes dos ensaios; regressões/qualidade/smoke 06B reproduzidos; preservar store/export sintético anterior, estados vazio/parcial/concluído e oráculos de tipos/contagens/valores. Reconfirmar integridade dos artefatos e do registro final sem abrir banco operacional.
2. **C-M2 — analytics independente:** portas/renderer/publicação/CLI/README/testes/build; wheel core+analytics sem bot/dados; fake de leitura exporta e CLI valida/consulta, incluindo falhas/paths/rede/precisão/escala. Só declarar dependência do bot depois de construir/validar o wheel.
3. **C-M3 — consumidor integrado:** adapters/fachadas/lazy imports/identidade/lock do bot, build novo e quatro wheels; regressões e compatibilidade do store selado, documentação/relatório/revisão visual C01–C18. Implementação única antes de aposentar corpos antigos; não manter cópias divergentes.

## 9. Matriz de aceite

| ID | Contrato | Prova planejada; todos pendentes nesta revisão |
|---|---|---|
| C01 | Baseline e ordem | Hashes/revisões e C-M1/C-M2 aprovados antes dos respectivos dependentes; oráculos/store/export anteriores preservados |
| C02 | Fronteiras/portas | Analytics sem imports de bot/dados/SQLite/estado financeiro; porta fake sem mutação; adapter bot preserva visão reconciliada e ordem |
| C03 | Valores oficiais | Saldo/custos/métricas/causalidade iguais; nenhuma conversão financeira para float; limites/flags não alterados |
| C04 | Formatos | CSV/JSON/HTML e Parquet equivalentes; >38 dígitos, JSON exato, NULL/UTC/BIGINT/export_row e ordem preservados |
| C05 | Catálogo/contagens | Vazio/parcial/concluído, PKs/tipos/metadados; SQL/porta/relatório concordam; divergência/curva desconhecida bloqueiam publicação |
| C06 | Segurança do motor | Rede/sockets/extensões/paths externos rejeitados; configuração travada, bindings e apóstrofo; query fixa sem SQL arbitrário |
| C07 | Limites/escala | 150 mil decisões largas e volume representativo disponível, row groups preservados; tempo/memória/spill/bytes medidos por fase |
| C08 | Falhas parciais | Injetar OOM/conversão/erro de porta/disco/publicação; nenhum journal/checkpoint/fill alterado e nenhum sucesso parcial |
| C09 | Atomicidade/concorrência | Crash antes/depois de rename, colisão/run_id/path/symlink e escritores concorrentes; publicação anterior intacta e reexportação segura |
| C10 | CLI standalone | check-export/query-export por wheel, sem bot/dados, leitura sem criar/alterar arquivo, root independente da instalação |
| C11 | Rejeições CLI | Argumentos/view/limit/root inválidos, pending/manifesto/schema/hash/catálogo ausente/corrompido, traversal/URL e dependência faltante |
| C12 | Instalação/composição | Core+analytics isolados e quatro wheels no bot, origens site-packages/RECORD; falta/versão/conteúdo/editable incompatíveis falham claramente |
| C13 | Lazy imports | Domínio/core/check-config/NOOP não carregam DuckDB; comandos válidos de relatório não perdem dependência por extra não declarado |
| C14 | Identidade | Mudar somente analytics muda fingerprint e bloqueia retomada antiga, sem reescrever protocolo/registro final |
| C15 | Histórico selado | backtest-report sob composição nova preserva identidade financeira 06B e bytes SQLite/registro final; nenhum novo sinal/fill |
| C16 | Regressões do consumidor | Cli/defaults/flags/config/locks/guards de coleta e finanças preservados; 48 curvas sintéticas e replay sem efeitos |
| C17 | Documentação e visual | README/API/exemplos, arquitetura/ADRs, bancos/catálogos/SMA quando afetados e guia/JSON com resultados reais; relatório derivado/revisado visualmente |
| C18 | Conclusão | C01–C17, marcos/composição aprovados, custos/limites/rollback explícitos; somente 06D elegível para detalhamento, 07 ainda pendente |

## 10. Sequência e comandos previstos

Comandos existentes de baseline do bot, **não executados neste detalhamento**:

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
uv run --locked --offline pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
WHEEL_SMOKE_STAGE=06b uv run --locked --offline python tests/wheel_smoke.py
```

O smoke pressupõe ambiente/artefatos 06B existentes. Preservar seleção/resultados 06A/06B; criar estágio explícito `06c`, `.venv-wheel-06c`, `dist/06c-final` e diretórios sintéticos próprios ao implementar. Harness final inclui os comandos existentes de paper/strategy/backtest e novos formatos/queries, todos sob `python -I`, cwd neutro, sem PYTHONPATH e com probe de sockets bloqueado. Não reutilizar registro final real para gerar fixture.

Após criar analytics, comandos **planejados** na raiz do novo projeto:

```bash
cd /home/cams7/Dev/Cripto/cripto-analytics
export UV_CACHE_DIR="$PWD/.uv-cache"
uv lock --offline
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
uv run --locked --offline pytest -q --cov=cripto_analytics --cov-branch --cov-report=term-missing
uv build --offline --out-dir dist/06c-final
```

Na integração: `uv lock --offline` deliberado do bot para nova dependência/fonte e retirada da dependência direta DuckDB; demais comandos locked; `uv build --offline --out-dir dist/06c-final`. Registrar diff do grafo: versões de terceiros preservadas, DuckDB transitivo e analytics acrescentado. Sync/build não devem sobrescrever wheels 06A/06B.

Smokes de instalação futura: criar `.venv-standalone-06c` no analytics com `uv venv --offline`; exportar requisitos externos do lock e instalar core+analytics, excluindo bot/dados. Criar `.venv-wheel-06c` no bot e instalar core 06A, dados 06B, analytics 06C e bot 06C. Usar `uv pip install --offline --no-deps --python <ambiente>/bin/python <wheels>` após preparar dependências externas verificadas; registrar comandos/caminhos completos efetivos no guia. Helper 06A de reutilização da baseline é alternativa verificável se o cache for insuficiente; registrar versão/RECORD/hash e não alegar cache frio. Falta de artefato impede marco, não autoriza imports de checkout.

Novos comandos do console só serão executáveis depois da implementação. A demonstração usará manifesto sintético gerado pelo harness como argumento, com root/cwd explícitos, para check-export e cada uma das três views de query-export; nenhuma consulta livre ou relatório econômico será executado nesta criação documental.

## 11. Evidências, documentação, custos e recuperação

Criar `docs/testes/sprint-06c-validacao.md` inicialmente pendente **durante a implementação**, antes dos testes, com preparação/comandos reais/versões/revisões/esperado/obtido/falhas/limitações. Criar `sprint-06c-evidencias.json` com C01–C18/marcos/arquivos/hashes e execuções reais. Esta especificação define caminhos sem criar guias vazios ou inventar resultados. Logs/configs/archives/oráculos em `reports/sprint06c/` dos projetos; preservar evidências anteriores, sem versionar SQLite operacional/segredos.

Documentar biblioteca e CLI no README/API do analytics, consumidor no bot, arquitetura central/modular e decisão de extração; adendar ADR 0007/0008 preservando contexto. Atualizar bancos/backtest-analytics.md, backtest-sqlite.md e catálogo; confirmar ausência de DDL financeiro alterado por comparação. Atualizar SMA/catálogo quando suas interfaces/proveniência/relatórios forem afetados; não inventar documento de estratégia para biblioteca. Relatório legível gerado das evidências, com qualidade/contagens/hashes/retomada/rejeições/custos/proveniência e resultados do consumidor; conferir valores e revisar visualmente antes do aceite. Não repetir avaliação econômica para montar o relatório.

Custos: CPU/disco locais. Medir separadamente reconciliação, snapshot/CSV, conversão/publicação e consultas; registrar pico RSS do processo e uso de spill/bytes, distinguindo-os do limite interno de 256 MB. Repetir ensaio largo existente e um volume representativo disponível sem coletar dados novos. Preferir CSVs/exportações preservados e portas sintéticas; leitura de ledger real para reexportar volume só se necessária, identificada previamente no guia e estritamente readonly, sem execução do período final ou mudança do registro. Comparar SQL por formato com as mesmas consultas/ordem/contagens, registrando número de repetições e condição de cache; não prometer ganho no replay. O resultado local anterior de milhões de linhas é histórico, não nova medição 06C.

Reservar espaço medido para CSV+Parquet+temporário+catálogo antes de ensaio largo; se insuficiente, registrar bloqueio/ajuste sem apagar dados únicos. Retenção: preservar baseline/artefatos/exports válidos/evidências; remover somente temporários/caches comprovadamente descartáveis e sem escritores ativos. Não iniciar rede de mercado/mensagens/AWS para suprir falta de cache ou dados.

Rollback restaura composição/manifest/lock e wheels compatíveis 06B, com revisão do trabalho posterior, sem reset amplo. Stores/schema/checkpoints/ledger/registro final e exports publicados permanecem. Catálogo/Parquet são derivados; falha neles permite nova publicação readonly, não correção financeira ou replay. Incompatibilidade persistida requer plano específico. Após C01–C18 e documentação aprovados, 06D fica somente elegível para detalhamento/revisão com composição congelada e critérios de sete dias/drills; não executar piloto nem liberar 07 automaticamente.

## 12. Prompt autossuficiente para implementação futura

Contrato para solicitação posterior; **não executado por esta criação documental**.

```text
Implemente somente a Sprint 06C em /home/cams7/Dev/Cripto. Crie apenas
/home/cams7/Dev/Cripto/cripto-analytics com Git próprio e src/cripto_analytics.
Bot consumidor: /home/cams7/Dev/Cripto/cripto-bot; core/dados existentes:
/home/cams7/Dev/Cripto/cripto-core e /home/cams7/Dev/Cripto/cripto-market-data;
documentação: /home/cams7/Dev/Cripto/docs. Não crie outros projetos, remotos,
commits ou publicação automática, nem altere projetos de referência.

Leia/verifique nesta ordem:
1. docs/planejamento.md (4.7–4.10, 5, 6.5, 9.2 e 13).
2. docs/sprints/sprint-06.md e sprint-06c.md integralmente.
3. docs/sprints/sprint-06b.md, docs/testes/sprint-06b-validacao.md e
sprint-06b-evidencias.json; 06A/guia/evidências para core e cache.
4. Sprint 05/guia/evidências, duckdb-parquet-validacao.md e evidências,
ADRs 0006–0009, arquitetura central/modular, bancos/catálogos, SMA e matriz
modular; confira funções e testes efetivamente existentes.
5. Manifests/locks/pins/README/fontes/testes/revisões/alterações locais dos
três projetos existentes e docs. Confirme fontes oficiais das APIs alteradas.

No detalhamento, 185 hashes e 12 arquivos do campo artifact_sha256 da 06B
conferiam; B01–B18 aprovados. Bot 0aeb7ef236f3be1cccff8136ff3135860706b0e9,
dados 1da6f4fe25c6940cc3e96416415ddf6f1ffcb4e9,
core e666e7e23dcb421177c80838a28c230d4433bdf2,
docs 6a40ecc7288de2ed8e746eafc6fb879e1738286d, limpos no início.
Reinspecione, preserve trabalho/dados/segredos; não presuma baseline igual.
Crie guia 06C pendente antes de executar. Falha de pré-requisito bloqueia
marco dependente. Execute C-M1 -> C-M2 -> C-M3 da seção 8.

Extraia apresentação/publicação paper/strategy/backtest e DuckDB/Parquet
conforme seção 4, recebendo snapshots prontos e ReadonlyRows sem store.db.
Mantenha summary/diagnostic/snapshot/_series, métricas oficiais/Decimal,
Wallet/State/ledger/risco/reconciliação/registro final e engine no bot;
core e dados não mudam. Adapter bot fornece linhas/contagens consistentes,
plan flatten e data_json exato. Biblioteca não importa bot/dados/SQLite,
logging/settings ou regras financeiras. Preserve fachadas/assinaturas e
patch hooks do consumidor, uma fonte dos schemas/renderers/conversão.

Implemente CLI check-export/query-export da seção 5: root absoluto local,
manifesto completo com hashes, três views fixas, limit 1–1000/default1000,
ordem/truncated explícitos, catálogo read_only e nenhuma escrita/SQL livre.
Não abrir banco inexistente/SQLite; não derivar root de site-packages.
Valide paths/symlinks/pending/schema/modelo/metadata/contagens; JSON/eventos
sanitizados e exit codes especificados. CLI não recalcula finanças.

Preserve contratos dos dez arquivos do backtest e exports paper/strategy,
VARCHAR exato/>38 dígitos, JSON, NULL/BIGINT/UTC/export_row, modelo/schema1,
contagens SQL versus fonte/relatório, manifesto e publicação atômica.
DuckDB1.5.6,256MB/1thread/ZSTD/rowgroup8192, spill local pendente,
extensões automáticas off, acesso externo bloqueado/allowlist antes do lock.
Teste rede bloqueada/paths externos/INSTALL, OOM/conversão/contagens,
falhas/morte/colisão antes/depois do rename e reexportação sem novos fills.
Não reduzir reconciliação/durabilidade nem mover/migrar/resetar banco.

Somente Python/local/PAPER/Spot/BTCUSDT/15m, fixtures/MockTransport e sockets
bloqueados. Sem rede real, credenciais/ordens/order/test, mensagens, AWS,
continuous, novos ativos/estratégias/métricas, ranking/otimização/walk-forward,
BT-A–BT-F ou avaliação da janela final real. Flags/defaults/limites financeiros
continuam os mesmos; configurações analíticas não são flags de estratégias.

Manifest/lock/README/API/py.typed/tests/build próprios, Python3.13.15,
uv0.12.19/setuptools84.2.0, core0.1.0 e DuckDB1.5.6. Construa/valide wheel
analytics antes de declará-lo no bot. Bot depende do wheel analytics0.1.0
local dist/06c-final e deixa DuckDB transitivo, sem upgrade lateral/extra
obrigatório para comandos antes disponíveis. Preserve core/dados e artefatos
06A/06B. Use comandos da seção10, locked/offline após lock deliberado.
Registre cache real; reutilização só após lock/versão/RECORD/hash conferidos,
sem alegar cache frio. Não depender de editable/PYTHONPATH/checkout irmão.

Adapte smoke para estágio06c/env/dados próprios, preservando anteriores;
prove core+analytics sem bot/dados e integração pelos quatro wheels.
Domínio/check-config/NOOP não carregam DuckDB; dependência faltante/versão/
conteúdo/editable incompatível falha explicitamente, sem publicação parcial.
Inclua analytics efetivamente carregado na identidade do bot: mudança isolada
bloqueia retomada antiga. backtest-report do protocolo sintético 06B preserva
identidade selada, result_sha256 e bytes SQLite/registro final, sem sinal/fill.
Compare oráculos financeiros e 48 curvas sintéticas, enumerando diferenças
legítimas de identidade sem excluir métricas/períodos.

Execute C01–C18 e qualidade/testes/build/smokes conforme seções9/10.
Meça tempo por fase, RSS/spill/bytes e escala de150mil decisões largas;
volume representativo por export/porta já disponível, sem novo backtest real.
Registre comandos/versões/revisões/hashes/esperado/obtido/falhas/custos/limites
em docs/testes/sprint-06c-validacao.md e sprint-06c-evidencias.json.

Atualize README/API/consumidor, arquitetura/ADRs, bancos/catálogos/SMA
quando afetados. Gere relatório a partir das evidências, confira números e
revise visualmente; documentação pendente impede conclusão. Atualize
planejamento/agregador com estado verdadeiro e rollback sem reset de dados.
Somente após C01–C18 aprovados 06D fica elegível para detalhamento/revisão;
não implementar/iniciar piloto ou liberar07/modos privados automaticamente.
```

## 13. Fontes e registro do detalhamento

Fontes primárias consultadas em 26/10/2026: [DuckDB 1.5/Python DB API](https://duckdb.org/docs/1.5/clients/python/dbapi), [restrições de acesso/configuração](https://duckdb.org/docs/1.5/operations_manual/securing_duckdb/overview), [Parquet](https://duckdb.org/docs/1.5/data/parquet/overview) e [uv/fontes de dependências](https://docs.astral.sh/uv/concepts/projects/dependencies/). Fundamentam conexão readonly, configuração do motor, formatos e dependência por artefato; não autorizam atualização de versões. As decisões de CLI/portas acima são desenho do projeto, não funcionalidades já existentes do DuckDB ou do bot.

Registro histórico do detalhamento, antes da implementação: inspeção de planejamento/agregador/05/06B, guias/evidências, arquitetura/ADRs/bancos e código/testes/manifests/locks/pins; conferência de 185 hashes/12 arquivos e revisões/estados Git; especificação desta etapa. Não houve criação de analytics/guia vazio, instalação/build/suíte, abertura de banco, relatório/coleta/otimização, movimento de dados ou execução de 06D. Próxima ação: revisar esta especificação antes de solicitar sua implementação.


## 14. Registro inicial da implementação — antes do esclarecimento externo

Prompt da seção 12 executado após solicitação posterior. C-M1 baseline 537 testes/22 comandos e qualidade antes de criar projeto; C-M2 28 testes/qualidade/build e wheel core+analytics sem bot/dados, aprovado antes de integrar. C-M3 técnico: bot 542 testes/qualidade/build, quatro wheels e 22 comandos; 130 contratos e cinco testes novos já incluídos na suíte. Biblioteca/CLI/readme/API, adapters/fachadas e identidade implementados; documentação/relatório revisados conforme evidências.

48 curvas/oito respostas financeiras equivalentes; seis arquivos selados exatos e linhas Parquet tipadas iguais. AST das funções financeiras de snapshot/summary/diagnostic e bytes dos três stores preservados. Relatório antigo readonly conserva SQLite/result_sha256; retomada antiga rejeitada, registro final real intacto. Publicação/crash/concorrência/precisão/paths/dependências ausentes aprovados. Medição de 150 mil decisões largas e nova projeção de CSVs já publicados, sem abrir ledger ou avaliar estratégia. Cache frio completo não demonstrado; distribuições locais conferidas reutilizadas.

**Pendência material:** apesar de 12/12 artefatos conferidos inicialmente, na conferência final wheel/sdist de bot e core em dist/06a-final divergiram dos hashes 06A/06B. Modificações observadas às 12:20–12:22 locais; origem ainda não esclarecida. Fontes core/dados continuam iguais e dez arquivos Python do wheel core atual conferem, mas artefato não é idêntico. Arquivos atuais preservados, sem restauração/eliminação ou reescrita de evidência anterior. Hashes esperados/observados no JSON; C01/C12/C18 pendentes. Confirmar origem e recuperar backups exatos ou decidir explicitamente baseline revisada/revalidação, sem aceitação silenciosa.

Nenhum commit/remoto/publicação, rede de mercado, credenciais/ordens, mensagens/AWS, 06D/07 ou BT-A–BT-F. Próxima ação: resolver a pendência de artefatos e revisar aceite 06C; 06D não é liberada enquanto persistir.


## 15. Aceite após confirmação da reconstrução externa

O responsável confirmou que houve reconstrução externa. A [verificação complementar](../testes/sprint-06c-reconstrucao-externa.json) comprovou inventário/conteúdo dos wheels e sdists atuais contra as fontes 06B, incluindo README/manifest dos sdists, e hashes do core nos locks. As 214 fontes/controles/testes/configurações e 16 arquivos de artefatos da composição 06C não mudaram após as execuções aprovadas; não houve necessidade de repetir testes de runtime sem alteração.

C01/C12/C18 resolvidos com rastreabilidade explícita; C01–C18 e C-M1–C-M3 aprovados offline, com revisão visual atualizada. A divergência binária continua registrada: não se afirma que os quatro arquivos sob dist/06a-final sejam os artefatos históricos originais. O bot reconstruído ali contém fontes 06B. Nenhum arquivo externo foi restaurado/apagado, nem evidência 06A/06B reescrita. Esta é a exceção documentada à preservação binária prevista nas seções 7/8, motivada por alteração externa confirmada; fontes e regras foram preservadas.

Rollback exato 06A exige recuperar os artefatos com hashes históricos. Para recuperação compatível com fontes 06B, usar composição identificada com core reconstruído verificado e lock deliberadamente correspondente, repetindo checks se executada; não presumir compatibilidade de hash com o lock antigo. Guia registra o limite, sem impedir o aceite da composição 06C efetivamente testada. Próxima ação elegível: detalhar/revisar 06D; não iniciar piloto, 07 ou trilha BT automaticamente.
