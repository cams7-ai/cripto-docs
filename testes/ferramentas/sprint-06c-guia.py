"""Write actual suite/scale results into the validation guide, without executing products."""
from pathlib import Path
import json
import xml.etree.ElementTree as E
DOCS=Path(__file__).resolve().parents[2];ROOT=DOCS.parent
BOT=ROOT/'cripto-bot/reports/sprint06c';AN=ROOT/'cripto-analytics/reports/sprint06c'
def load(p):return json.loads(p.read_text())
suites=[('Baseline bot',BOT/'baseline'),('Analytics standalone',AN/'standalone'),('Bot integrado',BOT/'final')]
rows=[]
for name,path in suites:
 t=E.parse(path/'pytest.xml').getroot()[0].attrib;c=load(path/'coverage.json')['totals']
 rows.append(f"| {name} | {t['tests']} | {t['time']} s | {c['percent_covered']:.2f}% |")
scale=load(AN/'scale-preserved.json');synthetic=load(AN/'scale-synthetic.json')
text='''# Validação da Sprint 06C

Execução: 26/10/2026. **APROVADA no escopo offline: C01–C18 e revisão visual registrados nas [evidências](sprint-06c-evidencias.json), com reconstrução externa esclarecida e verificada.** Roteiro inicialmente pendente criado antes dos ensaios. [Especificação](../sprints/sprint-06c.md), [ADR 0010](../decisoes/0010-analytics-por-snapshots-somente-leitura.md) e [relatório legível](relatorios/sprint-06c/report.html).

## Baseline e marcos

Bot HEAD 0aeb7ef236f3be1cccff8136ff3135860706b0e9, core e666e7e23dcb421177c80838a28c230d4433bdf2, dados 1da6f4fe25c6940cc3e96416415ddf6f1ffcb4e9, docs 6a40ecc7288de2ed8e746eafc6fb879e1738286d. Alterações documentais preexistentes preservadas. Analytics com Git main próprio, sem commit/remoto; nenhum commit nesta execução.

185/185 hashes e 12/12 arquivos de artifact_sha256 da 06B conferidos antes de executar. Archive Git do bot preserva a fonte versionada da baseline, conferida novamente ao consolidar JSON; configuração local ignorada pelo Git é conferida diretamente pelo hash anterior, sem copiar seu conteúdo para docs. Core/dados permanecem com Git limpo e fontes/controles iguais. Na conferência final, quatro artefatos 06A divergiram da baseline; ver esclarecimento da reconstrução externa abaixo. Seus 54/120 testes são históricos, não reexecuções desta etapa. Os 12 arquivos anteriores incluem dois .gitignore de build, além de dez wheels/sdists.

C-M1 aprovado antes de criar analytics: qualidade/regressão completa e 22 comandos do smoke 06B, store/export sintéticos preservados. C-M2 aprovado antes de integrar: biblioteca, CLI, qualidade/testes/build e wheel core+analytics sem bot/dados/HTTPX/Pydantic, cinco checks e sockets bloqueados. C-M3: bot por adapters/fachadas, quatro wheels, 22 comandos, contratos e compatibilidade/escala/documentação. Datas e decisões nos arquivos acceptance.json dos marcos e no JSON central.

| Suíte | Testes sem falhas/erros | Tempo XML | Cobertura combinada |
|---|---|---|---|
'''+ '\n'.join(rows)+'''

Ruff, formatação e mypy aprovados: 14 fontes analytics, 61 bot. Cobertura por pacote, com denominadores alterados pela extração; não inclui automaticamente código do wheel externo no bot. Contratos direcionados: 130 testes; composição nova: cinco testes; já contidos na suíte completa, não somados como funcionalidades novas.

## Ownership, precisão e formatos

Biblioteca depende somente de core==0.1.0 e duckdb==1.5.6. Bot mantém summary/diagnostic de paper/strategy e snapshot/_series histórico: AST dessas seis funções idêntico. Stores paper_sqlite/strategy_sqlite/backtest_sqlite byte a byte idênticos. Nenhuma migração ou mudança de métricas/risco/SMA/flags/ledger/registro final. AnalyticsRows fornece fluxos/contagens de visão reconciliada; biblioteca não recebe conexão ou estado financeiro. Fachadas preservam assinaturas e hooks de falha; uma implementação dos schemas/renderers/conversão.

Backtest mantém dez arquivos em files, mais manifesto; manual JSON e modular JSON/HTML. VARCHAR financeiro/JSON/as_of exato, inclusive >38 dígitos; NULL/BIGINT/UTC/export_row e ordem preservados. Limites DuckDB 1.5.6/1 thread/256MB internos/ZSTD/row group 8192, spill pendente, extensões off/acesso externo bloqueado/allowlist/configuração travada.

CLI nova check-export/query-export valida schema/modelo/hashes/metadata/contagens e consulta três views fixas, limit 1–1000/default1000, ordem/truncated explícitos. Root absoluto existente contido no workspace e independente da instalação; pending/paths/URLs/symlinks externos/manifestos inválidos rejeitados. Catálogo read_only e nenhuma alteração/criação de arquivo na entrada. Sem SQL livre ou abertura de SQLite. Sockets bloqueados por audit hook/probe nos smokes; testes usam fixtures e fakes. Não houve rede real.

## Compatibilidade e falhas observadas

48 curvas sintéticas equivalentes, excluídos somente run_key/checkpoint_bytes ligados à identidade; demais campos/métricas/chart/motivos/períodos iguais. Oito respostas financeiras com hashes anteriores: manual 10009.58001000, SMA 9905.46181258/71 ciclos, replay sem novos fills. Resultado retrospectivo sintético comprova regressão técnica; não representa nova evidência econômica fora da amostra nem garantia futura.

Reexportação readonly do store sintético selado 06B preserva protocol_hash/result_sha256 e bytes SQLite. Seis arquivos exatos à baseline: report.json/report.html/equity.csv/trades.csv/decisions.csv/analytics.json; linhas tipadas completas dos três Parquets iguais em export_row. DuckDB/Parquet têm hashes de cada publicação, sem exigir igualdade dos bytes internos do motor. Retomada antiga rejeitada com exit3/FROZEN_PROTOCOL_CHANGED. Registro final real conserva SHA256 af7ee92659cb1be9c4e322daeba997755430a040faec4b1342c1cabf082810bd.

Conteúdo/versão/RECORD/editable incompatíveis testados; alterar somente analytics muda fingerprint/bloqueia retomada. Ambientes negativos reais: sem analytics, check-config/NOOP funcionam e paper-run falha fixo antes de criar store; com analytics mas sem DuckDB, backtest-run falha antes de criar store. Domínio/CLI defaults não carregam DuckDB.

Vazio/parcial/concluído, divergência de contagem, OOM injetado, erro de porta/disco/publicação, corrupção/path/schema inválidos: sem sucesso parcial e com retry. Duas mortes reais independentes antes/depois de rename e dois publicadores concorrentes: um sucesso/uma colisão, manifesto íntegro, temporário não anunciado como publicação. Testes financeiros existentes de crash/publicação também passaram. Nenhum erro exigiu alteração de regra financeira.

## Comandos e instalação reproduzível

Python 3.13.15, uv 0.12.19, setuptools 84.2.0. Locks próprios. Bot preserva versões dos 28 pacotes anteriores, acrescenta analytics0.1.0 e deixa DuckDB1.5.6 transitivo. Metadata dos wheels usa versões normais, sem path absoluto; fonte local no lock aponta aos artefatos dos marcos. Bot/analytics foram construídos em dist/06c-final. Quatro artefatos antigos 06A foram encontrados substituídos na conferência final; sua origem externa foi confirmada pelo responsável, com conteúdo/locks verificados e hashes históricos preservados no registro.

```bash
# Na raiz do projeto pertinente:
export UV_CACHE_DIR=/home/cams7/Dev/Cripto/cripto-bot/.uv-cache
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
# Analytics:
uv run --locked --offline pytest -q --cov=cripto_analytics --cov-branch --cov-report=json:reports/sprint06c/standalone/coverage.json --junitxml=reports/sprint06c/standalone/pytest.xml
uv build --offline --out-dir dist/06c-final
# Bot:
uv run --locked --offline pytest -q --cov=cripto_bot --cov-branch --cov-report=json:reports/sprint06c/final/coverage.json --junitxml=reports/sprint06c/final/pytest.xml
uv build --offline --out-dir dist/06c-final
```

uv lock --offline foi deliberado ao criar analytics e atualizar o grafo do bot; demais execuções locked. Primeira tentativa com cache novo falhou por metadata DuckDB ausente, preservada em lock.log. Cache existente do bot permitiu resolver os mesmos pins. Dependências externas foram reutilizadas da baseline após versão/RECORD/hash conferidos pelo helper 06A, com zero divergência. **Cache frio completo não demonstrado; nenhum download.** Export de requisitos/reutilização/instalação em logs reais; ambientes .venv-standalone-06c e .venv-wheel-06c novos. uv pip install --offline --no-deps recebe wheels próprios, após preparar dependências externas travadas.

```bash
# Em cripto-analytics, após instalar core+analytics no ambiente standalone:
.venv/bin/python tests/wheel_smoke.py
.venv/bin/python ../docs/testes/ferramentas/sprint-06c-publicacao.py
.venv-standalone-06c/bin/python -I tests/offline_runner.py ../docs/testes/ferramentas/sprint-06c-escala.py synthetic
.venv-standalone-06c/bin/python -I tests/offline_runner.py ../docs/testes/ferramentas/sprint-06c-escala.py preserved
# Em cripto-bot, após instalar os quatro wheels no ambiente final:
WHEEL_SMOKE_STAGE=06c uv run --locked --offline python tests/wheel_smoke.py
.venv/bin/python ../docs/testes/ferramentas/sprint-06c-compatibilidade.py
# Em docs, consolidar sem executar produtos:
python testes/ferramentas/sprint-06c-guia.py
python testes/ferramentas/sprint-06c-evidencias.py
python testes/ferramentas/sprint-06c-relatorio.py
```

Provas usam python -I, cwd neutro/raiz explícita, sem PYTHONPATH/import de checkout irmão. Origens e RECORD dos quatro pacotes instalados registrados. Dados sintéticos/controles/registro de uso isolados; nunca copiar registro final real para liberar nova execução. Logs/archives em cripto-bot/reports/sprint06c e cripto-analytics/reports/sprint06c.

## Escala, consultas e custos

'''
text+=f"Ensaio sintético de 150.000 decisões largas: publicação {synthetic['phases']['publish_seconds']:.3f}s, pico RSS {synthetic['peak_rss_kib']} KiB; spill observado {synthetic['peak_spill_bytes_observed']} bytes.\n\n"
text+=f"Volume já publicado: {scale['rows']['equity']:,} equity, {scale['rows']['trades']:,} fills e {scale['rows']['decisions']:,} decisões. Origem CSV/report com hashes conferidos antes/depois; nenhum ledger aberto. Publicação {scale['phases']['publish_seconds']:.3f}s; render {scale['phases']['render_seconds']:.3f}s, leitura/reescrita CSV {scale['phases']['csv_seconds']:.3f}s, análise {scale['phases']['analytics_seconds']:.3f}s. RSS {scale['peak_rss_kib']} KiB; spill observado {scale['peak_spill_bytes_observed']} bytes; export {scale['published_bytes']} bytes. Tempos de publicação incluem hashing/finalização além das fases; preparação/verificação de origem e reconciliação não estão incluídas.\n\n"
text+='| Série | CSV bytes | Parquet bytes | CSV mediana s | Parquet mediana s |\n|---|---|---|---|---|\n'
for name,item in scale['queries'].items():text+=f"| {name} | {item['csv']['bytes']} | {item['parquet']['bytes']} | {item['csv']['median_seconds']:.6f} | {item['parquet']['median_seconds']:.6f} |\n"
text+='''
Mesma consulta GROUP BY run_key/count, resultados iguais, três repetições CSV seguidas por três Parquet, mesmo processo/1thread/256MB; cache frio não controlado. Não extrapolar ganho de consulta para replay/reconciliação. Limite interno DuckDB difere de RSS do processo; amostragem de spill 20ms é observação, não garantia absoluta de pico. Resultado anterior de performance mantém contexto histórico.

Custo externo zero; CPU/disco local e aproximadamente 2,38GB para a publicação de volume, além da origem preservada, ensaios e ambientes. Espaço disponível conferido antes (~666GiB). Preservar evidências/artefatos/exports válidos; limpeza somente de temporários/caches descartáveis sem escritores ativos. Nenhuma eliminação de dados únicos.

## Documentação, recuperação e continuidade

README/API/consumidor, arquitetura/ADRs, bancos/catálogos e SMA atualizados; relatório derivado do JSON e revisão visual registrada. Matriz C01–C18 aponta provas reais, sem converter resultados da 05/06B em novas execuções. Pendências/limitações explícitas, sem ocultar tentativa de cache malsucedida ou diferenças de denominador.

Rollback restaura composição/manifest/lock/wheels compatíveis 06B após revisar trabalho posterior; sem reset amplo. Ledger/locks/checkpoints/registro final/exports permanecem. Falha em projeção permite reexportação readonly, nunca refazer sinais para corrigir relatório. Artefatos locais compartilham versões 0.1.0, portanto selecionar também caminho/hash; não substituir wheels antigos silenciosamente.

06D somente elegível para detalhamento/revisão depois do aceite completo C01–C18/documentação; piloto/gate global/07 e trilha BT não iniciados. Sem commit/remoto/publicação, rede real, credenciais/ordens, mensagens/AWS ou nova avaliação da janela final real.

Fontes primárias reconfirmadas em 26/10/2026: [DuckDB DB API](https://duckdb.org/docs/1.5/clients/python/dbapi), [segurança/configuração](https://duckdb.org/docs/1.5/operations_manual/securing_duckdb/overview) e [uv/dependências](https://docs.astral.sh/uv/concepts/projects/dependencies/). Mantidos os pins validados, sem upgrade lateral.
'''
text+='''

## Reconstrução externa esclarecida e verificada

O responsável confirmou: “Sim, houve reconstrução externa”. A divergência inicialmente bloqueou C01/C12/C18; foi resolvida por identificação da alteração externa e verificação complementar, sem restaurar/apagar arquivos ou modificar evidências 06A/06B. [Prova estruturada](sprint-06c-reconstrucao-externa.json) e [ferramenta](ferramentas/sprint-06c-reconstrucao-externa.py).

Os wheels/sdists atuais de bot/core sob dist/06a-final têm hashes próprios e não são os artefatos históricos originais. Inventários/conteúdos da biblioteca (11 arquivos incluindo py.typed) e bot (59 arquivos) conferem com fontes validadas 06B; README/pyproject dos sdists também conferem. Em particular, o bot reconstruído no caminho 06a-final contém fontes 06B, não a release 06A original. Não usar o nome desse diretório para atribuir-lhe identidade histórica.

As 214 fontes/configurações/testes/controles e 16 hashes de artefatos da composição registrada continuam iguais aos usados na validação concluída. Locks do bot/analytics apontam ao SHA do core reconstruído disponível. Portanto, não houve mudança de runtime após os testes; a verificação adicional limitou-se a conteúdo/inventário/controles/identidade, sem repetir suítes sem alteração. C01/C12/C18 aprovados com essa ressalva explícita; hashes anteriores permanecem em prior_artifact_expected_sha256, divergências e origem em campos separados. Isso não afirma imutabilidade binária dos quatro arquivos antigos.

Rollback exato da release 06A exige obter os artefatos com seus hashes históricos; eles não foram recuperados nesta execução. Não prometer que o antigo lock 06B aceita o core reconstruído sob hash diferente. Recuperação compatível com fontes 06B pode usar bot/dados 06B preservados e o core reconstruído verificado, identificando deliberadamente o novo SHA no lock e repetindo os checks pertinentes se essa recuperação for executada. Não reescrever identidades seladas para retomar protocolos antigos; leitura histórica permanece disponível. A limitação de recuperação exata fica documentada, sem impedir o aceite técnico da composição 06C efetivamente testada.

06D fica somente elegível para detalhamento/revisão após este aceite; piloto/gate global/07 e BT continuam pendentes.
'''
(DOCS/'testes/sprint-06c-validacao.md').write_text(text)
print('Wrote actual validation guide')
