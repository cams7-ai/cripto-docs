# Catálogo e documentação dos bancos

Revisão: 25/10/2026. Documentos mantidos em `/home/cams7/Dev/Cripto/docs/bancos/`. Aplicação Python em `/home/cams7/Dev/Cripto/cripto-bot`.

| Banco lógico / tecnologia | Documento | Estado constatado | Sprint de origem |
|---|---|---|---|
| Mercado / SQLite | [market-sqlite.md](market-sqlite.md) | Schema v1 definido no código; leitura documental do DDL | 02 |
| Backtest histórico / SQLite | [backtest-sqlite.md](backtest-sqlite.md) | Schema1/modelo paper-backtest-v1 independente; aceite registrado no guia 05; sem migração | 05 |
| Análises históricas / DuckDB + Parquet | [backtest-analytics.md](backtest-analytics.md) | Projeção derivada, schema analítico 1; ledger preservado em SQLite; validação complementar | Ajuste posterior à 05 |
| Carteira PAPER / SQLite | [paper-sqlite.md](paper-sqlite.md) | V1 histórica preservada; v2 modular implementada e confrontada com fixtures/demonstração, sem migração | 03 / 04 |

A revisão documental inicial inspecionou os fontes, sem abrir arquivos SQLite de dados, executar aplicação ou migrations. Na Sprint 04, houve validação funcional/introspecção somente leitura do banco v2 sintético; os resultados e o escopo constam no [guia 04](../testes/sprint-04-validacao.md). Os diagramas representam o DDL consultado, não atestam o estado de uma instalação existente. Evidências funcionais continuam nos guias históricos, sem reexecução ou aprovação retroativa.

## Regra de manutenção por Sprint

Toda Sprint que criar ou alterar estrutura, constraints, índices, triggers, views, relações, formato persistido, versão, política de acesso ou migração de um banco deve criar/atualizar seu documento e este catálogo na mesma entrega. Documentação ausente/desatualizada bloqueia a conclusão da Sprint. Se não houver alteração, registrar no guia a ausência de impacto, com justificativa.

Um documento por banco lógico/tecnologia, sem duplicar por ambiente ou arquivo de carteira; separar versões/ambientes quando divergirem. Estruturas apenas propostas permanecem no planejamento até serem implementadas. Não criar documentação antecipada de tabelas/migrações inexistentes. Para DynamoDB futuro, documentar chaves PK/SK, índices, item types, padrões de acesso, condições/transações e TTL se efetivos; não representar relações lógicas como foreign keys inexistentes.

## Conteúdo obrigatório

1. Finalidade, proprietário, arquivo/tabela, configuração de caminho, tecnologia, versão do schema e código/revisão/hash consultados; distinguir esquema implementado, proposta e instalação não inspecionada.
2. Diagrama Mermaid ER do modelo relacional SQLite, com entidades, PK/FK, unicidade e cardinalidades reais. Indicar relações apenas lógicas, colunas JSON/BLOB e ausência de FK entre bancos; não inventar tabelas para objetos embutidos em JSON.
3. Dicionário de tabelas/colunas, tipos, nulabilidade, defaults, constraints, índices/uniqueness, triggers/views e significado/unidades dos campos; DDL versionado ou link preciso para sua fonte. Documentar também formato e versão dos JSON relevantes no código de domínio.
4. Fluxos de escrita/leitura, fonte de verdade versus projeção, limites transacionais, deduplicação, locks/concorrência, pragmas efetivos, retenção/limpeza e fronteiras entre bancos; impacto na integridade financeira quando aplicável.
5. Histórico de mudanças: Sprint, versão anterior/nova, diferença, artefatos e testes. Criação inicial é diferente de migração de dados existentes. Explicar compatibilidade e rejeição de versões não suportadas.
6. Se houver migração: pré-condições, pausa de escritores/agendamentos, backup consistente e verificação, comandos realmente existentes, conversões/backfill, invariantes antes/depois, transação/recuperação, impacto operacional e restauração/rollback ou irreversibilidade. Não inventar uma migration onde o código apenas rejeita schema antigo; não editar `user_version` para simular compatibilidade.
7. Procedimentos de inspeção/teste reproduzíveis em fixture/cópia isolada, comandos, versões, resultados esperados/obtidos e limitações; validação de constraints/índices/relacionamentos, migração se existente e reconciliação. Referenciar guias/evidências efetivos, sem declarar teste novo a partir da leitura do DDL.
8. Referências de código/testes/ADRs e, quando usadas, fontes oficiais datadas. Não incluir dados pessoais, credenciais ou dumps de produção.

Mermaid pode resumir atributos para legibilidade; o dicionário/DDL deve preservar os detalhes. Diagramas e SQL devem corresponder ao mesmo schema/revisão. Relações extras do domínio devem ser explicitamente separadas de vínculos impostos pelo banco.

## Aceite e operação

Revisão documental confronta o diagrama/dicionário/DDL com schema efetivo criado em fixture pela suíte da Sprint ou introspecção read-only de cópia autorizada: `sqlite_schema`, `PRAGMA table_info`, `foreign_key_list`, `index_list`/`index_info` e triggers quando aplicáveis. Registrar discrepâncias e decisão no guia; não executar inspeção mutável em carteira real. Para migrações implementadas, testar base nova e upgrade de versões suportadas, falha/recuperação, integridade e reconciliação; rollback só quando suportado e ensaiado.

Backup de SQLite ativo exige mecanismo consistente ou pausa controlada; copiar apenas o arquivo principal sem considerar journal/WAL não é procedimento de backup aprovado. Documentar a política concreta ao implementá-la. Histórico/ledger não é apagado para resolver conflito de schema. Nenhuma revisão de banco ou documento libera negociação LIVE.


Sprint 06A: layout e origem de helpers atualizados nos documentos técnicos. Nenhum DDL/schema/constraint/transação foi alterado ou banco migrado; identidade do código agora inclui o core instalado. [Compatibilidade e evidências](../testes/sprint-06a-validacao.md).


Sprint 06B: implementação do mercado SQLite v1 extraída para `cripto-market-data`; classe/DDL e dados físicos preservados, sem migração. Store antigo sintético e lock entre consumidores verificados. Leitor histórico mantém o contrato de quatro arquivos do manifesto. [Guia 06B](../testes/sprint-06b-validacao.md).


Sprint 06C: [projeção analítica](backtest-analytics.md) extraída para cripto-analytics por snapshots/portas readonly; stores financeiros e reconciliação permanecem no bot. [ADR 0010](../decisoes/0010-analytics-por-snapshots-somente-leitura.md).
