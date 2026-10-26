# ADR 0007 — DuckDB + Parquet como projeção analítica do backtest

Decisão posterior à Sprint 05, autorizada pelo pedido de integrar DuckDB + Parquet à aplicação.

Manter SQLite como fonte financeira autoritativa e acrescentar uma projeção analítica descartável. DuckDB 1.5.6 opera embutido em Python, converte CSVs integrais em Parquet ZSTD e calcula resumos SQL com contagens confrontadas com o ledger reconciliado. O catálogo contém resumos, sem duplicar as séries completas. A publicação mantém a atomicidade do diretório e o SHA256 de cada artefato.

Não transferir o ledger para um motor orientado a análise, remover reconciliações ou reduzir durabilidade como atalho de desempenho. Métricas oficiais continuam no núcleo Decimal existente; valores exatos ficam VARCHAR no formato analítico, evitando conversão silenciosa para float ou redução à precisão 38. Timestamps numéricos e contagens têm tipos inteiros. CSV/HTML/JSON permanecem disponíveis.

Consequências: nova dependência binária no lock e custo adicional na primeira exportação; consultas seguintes podem ler colunas dos Parquets comprimidos sem desserializar todos os JSONs. A integração não comprova, por si só, redução no tempo total do replay. Artefatos da avaliação original são preservados; validações novas usam evidências complementares, sem reabrir o teste final para seleção de parâmetros.

[Schema, operação e exemplos](../bancos/backtest-analytics.md), [guia complementar](../testes/duckdb-parquet-validacao.md) e [ADR 0006](0006-backtest-historico-e-protocolo.md).


## Adendo 06C

Conversão/catálogo/publicação extraídos para cripto-analytics, com porta de linhas/contagens reconciliadas no bot; nenhum acesso direto a store.db pela biblioteca. DDL/tipos/precisão/limites/restrições e resultado selado preservados. CLI nova somente leitura de exports. Mantém-se a decisão original de SQLite/Decimal autoritativos e projeções derivadas. [ADR 0010](0010-analytics-por-snapshots-somente-leitura.md).
