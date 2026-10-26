# Limpeza de artefatos — 26/10/2026

Executada a pedido do usuário em 26/10/2026 00:13:41 (America/Sao_Paulo). Removidos 559 alvos regeneráveis, sem alteração de código, configuração, fixtures ou dados principais da aplicação.

## Remoções

- Temporários gerados em `.pytest-tmp`: resultados locais e carteiras sintéticas de testes.
- 18 diretórios de smoke sem referência direta nos documentos/evidências.
- Duas cópias de diagnóstico `reports/duckdb-large-probe-*`, incluindo links locais aos CSVs de origem, sem remover os originais.
- Caches de pytest, Ruff, mypy e bytecode Python fora dos ambientes virtuais.

Estimativa dos blocos recuperáveis, considerando hardlinks: **7.10 GiB** (7.62 GB). O espaço livre do filesystem aumentou 7.67 GB durante a operação; essa medição global também pode refletir metadados e atividade de outros processos.

## Preservação e verificação

- Todo o diretório `data/`: bancos da aplicação, datasets, manifestos de origem, exportações finais CSV/JSON/HTML/Parquet e catálogos DuckDB.
- Controle de consumo da janela final: `data/backtest-usage/test-usage.sqlite3`, com SHA256 inalterado.
- Arquivos finais dos relatórios e evidências das Sprints 01–05 e da integração DuckDB/Parquet, incluindo os arquivos de auditoria em `reports/`.
- Quatro diretórios de smoke referenciados nas evidências, ambientes `.venv`/`.venv-wheel`, cache de dependências e wheel em `dist/`.

Os hashes de **103 arquivos de código/manifest/lock** permaneceram idênticos; o estado Git da aplicação também permaneceu igual. Foram conferidos tamanho e mtime de 94 arquivos de dados/manifests protegidos. `check-config` retornou `VALID` e `run-once` retornou `NOOP/PAPER/orders_sent=0` após a limpeza. Não foi necessária uma nova execução da simulação financeira.

A limpeza trata materializações temporárias; os comandos de teste podem recriá-las em execuções futuras. A lista exata dos caminhos removidos, referências preservadas e resultados das verificações está no [registro JSON](limpeza-artefatos-2026-10-26.json).
