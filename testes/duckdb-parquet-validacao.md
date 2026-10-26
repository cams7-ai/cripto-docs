# Validação complementar — DuckDB + Parquet

**APROVADA no alcance da camada analítica local do backtest.** Consolidação em 2026-10-26T02:59:04.136199+00:00. Evidências originais das Sprints 01–05 preservadas. Não constitui uma nova avaliação econômica nem reabre o teste final.

## Implementação e compatibilidade

DuckDB 1.5.6 foi adicionado ao manifest/lock Python. `backtest-run` e `backtest-report` publicam três Parquets ZSTD, `analytics.duckdb` e `analytics.json`, além dos cinco arquivos de dados/relatório anteriores e seu manifesto. O HTML contém links para os novos formatos; a CLI retorna `analytics_database` e `analytics_manifest`.

SQLite continua sendo o ledger autoritativo, com o mesmo schema, transações, locks, CAS, checkpoints e recuperação. Métricas oficiais permanecem no núcleo Decimal. Valores financeiros e JSONs são VARCHAR exatos nos Parquets; timestamps numéricos são BIGINT, `as_of` mantém ISO UTC e `export_row` conserva a ordem de exportação. Nenhum parâmetro, regra ou versão da SMA foi alterado.

A exportação usa um thread DuckDB, limite interno de 256 MB, spill local, extensões automáticas desabilitadas e acesso externo bloqueado fora do diretório temporário de publicação. Resumos SQL leem os Parquets e confrontam contagens com SQLite e acumuladores oficiais. Só depois de fechar o catálogo e gerar os hashes o diretório é publicado por rename.

## Qualidade e testes

- **528 testes aprovados**, zero falhas/erros/skips/avisos, em 624.654 s. Incluem os 521 testes anteriores e sete casos novos.
- Cobertura combinada: 93.86%; 3569/3728 linhas e 1075/1220 branches. Não é cobertura integral; caminhos defensivos raros permanecem sem execução.
- Ruff, formatação, mypy strict e build aprovados. Wheel reinstalado em ambiente separado, origem `/home/cams7/Dev/Cripto/cripto-bot/.venv-wheel/lib/python3.13/site-packages/cripto_bot/__init__.py`, sem PYTHONPATH e com guard de sockets comprovado. O smoke exercitou os comandos anteriores e os novos formatos automáticos em fixture.
- HTML revisado em Chrome isolado sem rede, incluindo os links DuckDB/Parquet no rodapé, sem sobreposição ou truncamento.

| Caso | Esperado | Obtido |
|---|---|---|
| Protocolo sem curvas | Parquets vazios tipados e catálogo sem curvas | Aprovado |
| Snapshot parcial | Dados até o checkpoint; sem conclusão inventada | Aprovado |
| Snapshot concluído e reexportação | CSV e Parquet equivalentes; catálogo coerente; ledger idêntico | Aprovado |
| Valores acima de 38 dígitos e JSON | Strings exatas, sem float; timestamps inteiros | Aprovado |
| Divergência de contagem | Exit 3, publicação cancelada e carteira preservada | Aprovado |
| Falha do motor | Exit 3, publicação cancelada e carteira preservada | Aprovado |
| 150 mil decisões de payload largo | Conversão dentro do orçamento interno; grupos Parquet pequenos (`ROW_GROUP_SIZE=8192`, com arredondamento do motor) | Aprovado |

A conversão inicial em volume real excedeu o limite interno de memória ao usar grupos de 122880 linhas. A causa foi reproduzida nos CSVs reais; a correção configurou `ROW_GROUP_SIZE=8192`, respeitando o arredondamento por vetores do motor e a conversão integral passou. Um teste de 150 mil decisões largas foi acrescentado para cobrir esse caso. O ledger permaneceu com SHA256 idêntico inclusive durante a falha. A primeira sessão longa também foi interrompida antes de publicação; logs das tentativas estão preservados no arquivo local.

O controle de precisão também comprovou rejeição de leitura fora do diretório permitido e de instalação de extensão. As mortes reais antes/depois de rename, já existentes na suíte, passaram com os novos arquivos. O teste de reexportação incluiu um caminho contendo apóstrofo.

## Reexportação do histórico existente

Comando efetivo, somente leitura do ledger:

```bash
uv run --locked cripto-bot backtest-report --config config/backtest.sma.public.local.toml
```

Resultado: `BACKTEST_REPORTED`, zero novos fills, 48 curvas e mesmo resultado canônico `a12de079b7ebded9037c86b1f76b7b9a9edcb37ef68603a36cd7f79b50cc2f47`. SHA256 do arquivo SQLite antes e depois: `7f79aca8f4fb96b718fca41482cc6bf03345ee8169c4933496e5bd8ed477a22a`. A execução levou 1198.74 s, incluindo reconciliação integral, snapshot, CSVs e conversão analítica; não é um benchmark isolado do banco.

Export novo: `/home/cams7/Dev/Cripto/cripto-bot/data/backtest-btc-audit-v1/exports/97f4c02a-872f-4640-baf9-2645ad73cade`. Artefatos e SHA256 estão no `manifest.json` desse diretório e nas [evidências complementares](duckdb-parquet-evidencias.json). Nenhum export original foi substituído. A identidade financeira continua sendo o resultado canônico original; os arquivos DuckDB/Parquet têm hashes próprios de publicação.

[Relatório HTML atualizado](../../cripto-bot/data/backtest-btc-audit-v1/exports/97f4c02a-872f-4640-baf9-2645ad73cade/report.html) · [Catálogo DuckDB](../../cripto-bot/data/backtest-btc-audit-v1/exports/97f4c02a-872f-4640-baf9-2645ad73cade/analytics.duckdb) · [Manifesto do export](../../cripto-bot/data/backtest-btc-audit-v1/exports/97f4c02a-872f-4640-baf9-2645ad73cade/manifest.json). Estes arquivos operacionais são locais e não são versionados em docs.

## Medições de consulta e armazenamento

| Série | Registros | CSV (MiB) | Parquet (MiB) | CSV mediana (s) | Parquet mediana (s) |
|---|---:|---:|---:|---:|---:|
| equity | 2244867 | 495.46 | 40.48 | 1.153641 | 0.035409 |
| trades | 2211 | 4.66 | 0.73 | 0.221440 | 0.001331 |
| decisions | 1121268 | 1494.55 | 226.86 | 2.639050 | 0.020468 |

Consulta comparada: `SELECT run_key,count(*) FROM read_csv/read_parquet GROUP BY run_key ORDER BY run_key`. Três execuções por formato, CSV seguido de Parquet, mesmo processo DuckDB, um thread e limite interno de 256 MB. Todas retornaram exatamente os mesmos grupos/contagens. Medianas e bytes são observações locais; cache frio não foi controlado, e reconciliação/conversão ficaram fora desses tempos. A consulta mede agregação/pruning de colunas, não todo o replay nem todos os relatórios. Não extrapolar o fator observado para a simulação completa.

O catálogo é pequeno e armazena resumos, não cópias integrais das séries. Os CSVs foram mantidos por compatibilidade; a inclusão de Parquet aumenta o tamanho total do export atual, embora forneça uma representação colunar comprimida para consultas. A primeira publicação tem custo adicional de conversão.

## Reprodução e operação

```bash
uv sync --locked --group dev
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy modules/trading/src
uv run --locked pytest -q --cov=cripto_bot --cov-branch
uv build
```

Para uma carteira histórica já existente, `backtest-report --config ...` acrescenta os formatos em um novo export. Não repetir `backtest-run` de protocolo antigo após mudança de código/lock. Para um experimento novo, utilizar um diretório novo e seguir prepare/freeze/development/validation/test, respeitando o consumo da janela final. Docker é opcional para consultas, sem servidor ou porta exigidos pelo bot. Exemplos SQL e Docker estão no [documento de banco](../bancos/backtest-analytics.md).

Revisões base: aplicação `377df63e1cca2661f60e35fae446f06075d9fc63` e docs `850d0652163aac06989375996a1650b118b3eed1`, com alterações locais desta entrega. Runtime atual: `c6b78b36cf3520bca647678219b8c5c85215ed75534aeb12675875e7823a3b75`. Logs, scripts de verificação, wheel e fontes congeladas: `/home/cams7/Dev/Cripto/cripto-bot/reports/duckdb-parquet-delivery-sntkif29`. Limites: sem promessa de aceleração total, sem migração financeira, sem infraestrutura remota, sem commit/staging/deploy e sem início da Sprint 06. Custos: CPU/disco locais e instalação da dependência pública; sem ordens/taxas reais ou recursos AWS.

[Schema e DDL](../bancos/backtest-analytics.md) · [ADR 0007](../decisoes/0007-duckdb-parquet-analitico.md) · [Guia original da Sprint 05](sprint-05-validacao.md).
