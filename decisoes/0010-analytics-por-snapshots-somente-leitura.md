# ADR 0010 — Analytics por snapshots e portas somente leitura

Data: 26/10/2026. Estado: implementada na Sprint 06C; resultado de validação no [guia](../testes/sprint-06c-validacao.md).

## Contexto

Publicação de relatórios e conversão DuckDB/Parquet estavam acopladas a stores e tipos financeiros do bot. Extrair essas funções com seus imports transferiria acesso ao ledger ou duplicaria regras financeiras. A 06B já separou dados públicos e preservou a identidade selada dos protocolos.

## Decisão

Criar `cripto-analytics/src/cripto_analytics`, Git/lock próprios, dependente somente de core 0.1.0 e DuckDB 1.5.6. Mover apresentação/publicação e schemas/conversão; manter summary/diagnostic, snapshot/_series, métricas Decimal, Wallet/State, risco/reconciliação e registro final no bot. `AnalyticsRows` do bot fornece linhas/contagens de uma visão reconciliada, sem passar store.db à biblioteca. Fonte única de renderers/conversão; fachadas mantêm assinaturas e hooks dos testes.

Bot conserva o perfil local padrão, substituindo DuckDB direto por analytics, que o traz transitivamente. Imports de domínio/configuração/NOOP não carregam o motor; capacidades exigidas pelos comandos são verificadas antes de mutação financeira. Falta de analytics/DuckDB retorna erro operacional fixo, sem publicar conjunto incompleto. Não criar flag de estratégia para dependência técnica.

Projeções mantêm formatos/schema1, VARCHAR financeiro exato, timestamps/export_row BIGINT, valores opcionais NULL, contagens SQL confrontadas e publicação em diretório pendente seguida de rename. Limites/guard do motor preservados: 1 thread, 256 MB internos, ZSTD, row group 8192, spill local pendente, extensões automáticas off, allowlist/acesso externo bloqueado/configuração travada. O limite interno não é teto RSS.

CLI própria check-export/query-export valida snapshots completos e consulta três views fixas readonly, com root explícito contido no workspace, hashes/schema/metadados/contagens, limit e truncated. Não oferece SQL livre, cliente Binance, abertura de SQLite, reconciliação ou reexportação de finanças. Estado selado do export não é substituído pela identidade do leitor.

Bot amplia a identidade da composição com analytics efetivamente instalado, versão/origem/RECORD/arquivos. Dependência extraída exige wheel; mudança isolada bloqueia retomada congelada. Relatório selado anterior permanece reexportável readonly com mesma identidade financeira; não reescrever protocolo ou renovar janela final já consumida.

## Consequências e limites

Fontes core/dados e schemas financeiros são preservados. Aceite concluído após o responsável confirmar reconstrução externa: quatro artefatos 06A divergiram; conteúdo/inventário/locks conferem com a composição testada. Hashes históricos/atuais e limitação de rollback exato estão no guia; não rotular o rebuild como release histórica original. Wheels/locks locais identificam a composição; sem publicação/commit automático ou imports de checkout irmão. Cache frio completo não demonstrado; dependências externas reutilizadas após lock/versão/RECORD/hash conferidos. Medições separam projeção/consulta de reconciliação; a extração não promete acelerar o replay ou produzir melhor desempenho econômico. Não implementa 06D/07 ou trilha BT. Custos, ensaios reais e rollback no guia, com relatório revisado visualmente antes do aceite.
