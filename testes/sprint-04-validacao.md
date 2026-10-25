# Sprint 04 — Guia e registro de validação modular/SMA

Data: 25/10/2026, America/Sao_Paulo. **Resultado: APROVADA no escopo local/PAPER/fixture/BTCUSDT/15m, AC01–AC18.** Nenhuma liberação de backtest econômico, execução contínua, AWS ou negociação privada. Default da instalação permanece desabilitado.

Especificação: [Sprint 04](../sprints/sprint-04.md). Evidência estruturada: [sprint-04-evidencias.json](sprint-04-evidencias.json). Estratégia/documentação: [trend_sma](../estrategias/trend_sma.md), [ADR 0005](../decisoes/0005-estrategia-modular-e-persistencia.md) e [banco v1/v2](../bancos/paper-sqlite.md). Os resultados abaixo correspondem à implementação solicitada, não ao detalhamento documental anterior.

## 1. Base, pré-requisitos e versões

Workspace `/home/cams7/Dev/Cripto`; comandos Python/uv executados em `/home/cams7/Dev/Cripto/cripto-bot`; documentos em `/home/cams7/Dev/Cripto/docs`, Git independente. Base da aplicação `35be28620f4b099352e2fcffa721c7ab8c52c389`; base de docs `cc78f4c4b751b1a533a7c8a6f7157eb02b48589a`. Aplicação estava limpa; a especificação 04 já tinha alteração documental local, preservada. Não foi criado commit/remoto.

Os 40 hashes das evidências 03 conferiram antes da implementação. Regressão inicial: **316 testes aprovados em 11,79 s**. A implementação preserva comandos/configurações/financeiro v1 e não modifica schema/datasets de mercado. Os testes históricos voltaram a passar na suíte ampliada. Evidências JSON 01–03 foram preservadas.

Python 3.13.15/uv 0.12.19, dependências do lock existente, sem nova dependência. Pydantic 2.14.1, HTTPX 0.28.1; versões completas e backend fixado estão no JSON de evidências. O backend setuptools é isolado pelo build; não presumir que esteja instalado no ambiente de desenvolvimento. O shim pyenv local não possui o pin; uv encontrou o Python gerenciado e executou os comandos. Scripts auxiliares de preparação usaram `/usr/bin/python3`.

A gravação na aplicação e execução de testes fora de docs utilizaram a escalada permitida do ambiente. Instalação final do wheel foi offline, sem reinstalar dependências já conformes ao lock, e `uv pip check` passou. Testes/aplicação financeira executaram com rede bloqueada; não houve coleta ou trading externo.

## 2. Qualidade e suíte final

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
uv sync --locked --group dev
uv --version
uv run --locked python --version
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy modules/trading/src
uv run --locked pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing --cov-report=json:/tmp/cripto-sprint04/coverage.json
uv build --quiet
```

Resultado final: **428 testes aprovados, sem avisos**. Ruff sem achados, formatação de 81 arquivos verificada, mypy strict aprovado em 47 fontes. A duração e saídas exatas estão nas evidências. Não somar 316 e 428: a suíte final já inclui as anteriores.

Cobertura combinada **96,52%**; linhas executáveis **2432/2490 (97,67%)** e ramificações **732/788 (92,89%)**. SMA pura tem cobertura integral de linhas/ramificações. O percentual global não é 100% nem substitui a matriz funcional. Foram preservadas exclusões padrão de Protocol/ferramenta; não se adicionaram exclusões manuais para mascarar caminhos críticos.

Lacunas incluem guards redundantes protegidos pela configuração/fixture (múltiplos módulos chegando ao redutor, modelo/ID/tempo de ciclo inválidos por chamada interna), variantes de corrupção/fallback sem reconstrução, filtros/precificação já cobertos pelo motor 03 mas não todos os guards duplicados do dimensionamento, e ramos de erro de configuração/empacotamento anteriores. Linhas/ramos exatos por arquivo estão no JSON. A verificação de risco, reserva, geração, prefixo, replay, commit/rollback e schema tem cenários explícitos abaixo.

Durante o desenvolvimento foram corrigidos imports/tipos/formatação e o fechamento de conexões SQLite do harness de adulteração de schema. A passagem intermediária com ResourceWarning não foi usada como resultado final. Também se cobriram default sem arquivo, alteração de cotação já confirmada, orçamento por instância e virada UTC no fechamento de candle. Não se alteraram custos/limites para fazer o exemplo lucrar.

## 3. Demonstração final e relatório legível

Configuração default: `config/strategy.sma.example.toml`, enabled=false. Configuração opt-in: `config/strategy.sma.fixture.toml`, enabled=true, diretório `data/sma-fixture-v1`. A carteira final foi nova na primeira passagem; repetições seguintes não apagam/reinicializam o estado. Artefatos anteriores de desenvolvimento não constituem aceite da versão final e não foram substituídos para ocultar divergências.

Comandos reais, todos com código 0, executados pela CLI sob `tests/offline_runner.py` com audit hook de sockets:

```bash
uv run --locked cripto-bot strategy-run
uv run --locked cripto-bot check-config --config config/strategy.sma.example.toml
uv run --locked cripto-bot strategy-run --config config/strategy.sma.example.toml
uv run --locked cripto-bot check-config --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-run --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-reconcile --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-report --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-run --config config/strategy.sma.fixture.toml
```

A evidência JSON registra os argumentos exatos do runner, run_id, eventos, resumos e hashes dos stdout completos. Estes e stderr foram preservados em `reports/sprint04-validation-g1ovme3s/`, relativo à aplicação. O comando final de replay reconheceu 71 ciclos, com zero avaliações/fills novos e o mesmo hash financeiro da primeira execução.

| Verificação | Esperado | Obtido |
|---|---|---|
| Instalação sem arquivo / exemplo false | NOOP, sem carteira/intenção | Conforme |
| Avaliações | 71: 50 warm-up, 19 outros HOLD, 2 direcionais | Conforme |
| Fills / rejeições | 2 / 0 | Conforme |
| Quantidade BTC em cada fill | `9.07275400` | Conforme |
| Preço final BUY / SELL | `110.11000000` / `99.90000000` | Conforme |
| Taxa BUY / SELL USDT | `0.99900095` / `0.90636813` | Conforme |
| Taxas totais USDT | `1.90536908` | Conforme |
| Realizado líquido USDT | `-94.53818742` | Conforme |
| Saldo final USDT | `9905.46181258` | Conforme |
| BTC/reservas/custo remanescente | Zero | Conforme |
| Reconciliação / bloqueio | true / false | Conforme |
| Replay | Zero novos fills; hash estável | Conforme |

Hash financeiro modular preservado:

```text
df4351017b8df7e8a7979adc0ceb93dc55dcbd22f3b4f2a0e5041a3e8d989005
```

Primeiro relatório exportado: `data/sma-fixture-v1/reports/cc59ff78-a261-412b-aa4c-c2d15fa0bb15/`, com report.json/report.html/manifest.json. [Cópia HTML para leitura](../output/html/relatorio-sprint-04.html), idêntica ao arquivo exportado. Os hashes do manifesto foram comparados aos arquivos. `fixture_sha256` identifica o snapshot normalizado completo; os hashes dos bytes da fixture/TOMLs estão em `source_sha256` nas evidências. O config_hash identifica o snapshot modular; parâmetros financeiros imutáveis são identificados/comparados separadamente no contexto.

Revisão visual em Chrome headless, perfil temporário sem extensões/perfil do usuário e resolução externa bloqueada. Conferidos resumo, curva, decisões, preços/taxas, risco e rodapé sem cortes/sobreposições. Capturas preservadas no diretório de evidências locais acima. O browser foi usado somente para apresentação, sem operar a carteira. Não foi necessário PDF adicional: o HTML é autocontido, imprimível e atende à seção 4.9 do planejamento.

## 4. Matriz AC01–AC18

| Critério | Evidência executada | Resultado |
|---|---|---|
| AC01 | CLI sem arquivo, exemplo false, fixture ausente dispensada, listas de escopo vazias | Aprovado |
| AC02 | ID/versão/params/capacidades inválidos, dependência ausente/cíclica, pesos e disputa de propriedade | Aprovado |
| AC03 | 50/51 fechamentos, igualdade, alta/baixa, ausência de inventário, já comprado e contexto Decimal local | Aprovado |
| AC04 | Limites instância/par restritivos, plano incluindo taxas, perda/drawdown travando entradas e permitindo redução; regressão do risco 03 | Aprovado |
| AC05 | Fakes iguais/opostos/chegada invertida, conflito rejeitado, flock/CAS e invalidação de verificação por mutação | Aprovado |
| AC06 | Envelopes, geração/prefixo, planos/atribuições/custos, reconstrução exata e 18 postings | Aprovado |
| AC07 | DRAINING com posição, sem liquidação, pendência local cancelada uma vez, fill posterior proibido; parcial/UNKNOWN em fakes | Aprovado no alcance definido |
| AC08 | Mudança material com posição recusada, geração anterior preservada, disable/reativação em caixa sem replay/reset, CAS | Aprovado |
| AC09 | Suíte acumulada, Ruff/formatação/mypy/build e wheel em site-packages sob guard | Aprovado |
| AC10 | Documento trend_sma e catálogo confrontados com config/contratos/código/testes, exemplos positivo/negativo e links | Aprovado |
| AC11 | Prefixo acrescido, candle/execução passada conflitante, gaps/futuro/naive/OHLC inválidos, preço ausente/vencido e fechamento à meia-noite | Aprovado |
| AC12 | Demonstração 71 ciclos, valores exatos, cenário positivo separado e replay sem efeito | Aprovado |
| AC13 | Morte real antes/depois de A/B e em HOLD, rollback/reserva/cursor/fill único e liberação de lock | Aprovado |
| AC14 | V1/v2 em diretórios separados; abertura incompatível, versão futura/objeto extra/trigger ausente rejeitados sem reescrever DB | Aprovado |
| AC15 | Projeção/instância/ciclo/intenção/atribuição adulterados em fixtures, diagnóstico só leitura e bloqueio persistente | Aprovado |
| AC16 | JSON/HTML/manifesto, hashes, revisão visual, falha de rename sem perda/duplicação e reexportação somente leitura | Aprovado |
| AC17 | Sentinelas HTTPX/PublicSource, sockets no pytest/filhos/wheel, flags/credenciais/paths/symlinks proibidos e sanitização | Aprovado |
| AC18 | DDL/schema/pragmas/índices/FKs/triggers, constraints e dicionário/diagrama/catalogo/ADR atualizados | Aprovado |

Fakes de contratos não comprovam runtime parcial/UNKNOWN/TWAP/VWAP ou combinações reais. Corrupção usou apenas carteiras temporárias identificadas. No teste específico de atribuição, o harness removeu deliberadamente um trigger após abrir a fixture para injetar a falha; a API normal rejeita a mutação. O produto não oferece isso como reparo/migração.

## 5. Matriz modular M01–M16 e alcance

M01–M04: defaults/escopos/registro/dependências/isolamento aprovados. M05–M07: fakes de coordenação, reserva/CAS e risco global/instância/par aprovados; sem habilitar combinação ou multiativo. M08: fora do incremento, ativação TWAP/VWAP rejeitada. M09–M12: contrato de monitoramento com fakes mais reserva/fill/cancelamento local, geração, falha de módulo/dado e atribuição única aprovados. M13: causalidade/prefixo e custos sintéticos aprovados; backtest econômico/contínuo/parcial permanecem pendentes para 05/06. M14: exclusividade/conflito de composição aprovados; STP privado e grupos multiativo não implementados. M15: modos privados rejeitados; nenhum gate AWS/SAM/Demo/Testnet executado. M16: documentação individual e catálogo revisados.

A [matriz geral](estrategias-modulares-validacao.md) conserva o alcance futuro obrigatório; a aprovação desta Sprint não promove módulos/ambientes adicionais. Alteração material de regra/params/custos/composição invalida evidência afetada e exige nova validação.

## 6. Persistência e revisão documental

Carteira v2: 10 tabelas, 10 triggers; 76 eventos de journal, 18 postings, 71 ciclos, 1 geração/instância e 2 intenções/fills/atribuições. `integrity_check=ok`, `foreign_key_check` vazio. DDL/table_info/FKs/index_list/index_info/triggers e contagens constam no JSON de evidências, obtidos por conexão somente leitura na demonstração final, além dos testes em fixture.

A carteira v1 permanece no adapter histórico, sem migração. V2 nova usa o mesmo motor financeiro por hooks; decisões/estado/atribuição não ficam em banco com commit independente. Replay inicial/final é completo; a assinatura de versão/changes/data_version/schema_version e CAS evita replay integral repetido entre commits do escritor exclusivo. Escrita desconhecida invalida essa verificação.

Documentação conferida: regras/flags/janelas/limites e comandos em trend_sma; catálogo e alcance modular; schema v1/v2, DDL/constraints/diagrama/dicionário e ausência de migração; ADR 0005 e arquitetura. Exemplos/cálculos conferidos com Decimal. Sem documentação antecipada dos outros módulos.

## 7. Wheel e limites de empacotamento

Build com backend fixado e wheel `cripto_bot-0.1.0-py3-none-any.whl`; SHA-256 e origem exatos no JSON de evidências. Artefato final reinstalado em `.venv-wheel` via `uv pip install --offline --no-deps --reinstall --python .venv-wheel/bin/python dist/cripto_bot-0.1.0-py3-none-any.whl`. Dependências runtime já instaladas foram confrontadas com requirements exportados do lock; `uv pip check` aprovado.

Smoke em `.wheel-smoke`, Python `-I`, sem PYTHONPATH, importação de site-packages, paths absolutos e audit hook de sockets. Incluiu check-config/run-once, coleta fixture 2/0, carteira manual run/reconcile/report/replay e estratégia default/opt-in/reconcile/report/replay. Nova carteira por smoke, hash financeiro estável por replay, manifestos conferidos, LIVE rejeitado com 2 e probe de socket bloqueado. O wheel não inclui testes ou dados/ambientes operacionais. Hash de rebuild pode mudar; vincular aceite ao artefato exato registrado.

## 8. Recuperação, limpeza, custos e conclusão

Configuração/fixture inválida falha antes de efeitos; estado incerto/financeiro divergente bloqueia; não há comando de reset/repair/migração. Interrupção após A retoma o plano antigo; após B devolve o confirmado. Falha de exportação preserva os commits e `strategy-report` recompõe os arquivos sem avaliação. Desativação não liquida inventário nem apaga drawdown. Relatórios diferenciam novos efeitos de totais históricos.

Foram preservadas carteira final, exportações, stdout/stderr e capturas para revisão; bancos/locks/reports locais estão ignorados no Git da aplicação. Fixtures/TOMLs/fontes/testes e evidências selecionadas são versionáveis. Remover apenas artefatos sintéticos cuja origem esteja identificada; nunca apagar histórico para resolver divergência. Custo AWS zero, sem capital/taxas reais; uso local de CPU/disco.

Não foram executados coleta pública real, AWS/SAM/Docker, notificações, Demo/Testnet/LIVE, backtest fora da amostra, PAPER contínuo, parcial real, benchmark de alto volume, NFS ou perda de energia/disco. Aprovação é de engenharia offline e não depende de lucro. **Próximo passo: revisar as evidências 04 antes de detalhar a Sprint 05.** Nenhuma Sprint futura, commit, deploy ou publicação de remoto foi iniciada automaticamente.
