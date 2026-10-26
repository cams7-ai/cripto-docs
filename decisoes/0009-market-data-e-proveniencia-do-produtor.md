# ADR 0009 — Market-data independente e proveniência do produtor

Data: 26/10/2026. Estado: implementada na Sprint 06B; resultado do aceite no [guia](../testes/sprint-06b-validacao.md).

## Contexto

Coleta pública, parsers, DTOs e store estavam no bot; o exportador também fornecia funções de identidade usadas por paper/strategy/backtest. Mover tudo carregando esses imports criaria dependência inversa ou classificaria uma execução standalone como bot. O leitor histórico exige parser/schema e quatro arquivos exatos no manifesto.

## Decisão

Extrair biblioteca/CLI/Git independentes em `cripto-market-data/src/cripto_market_data`, dependente de core imutável, HTTPX e Pydantic. Portas/DTOs, caso de uso de paginação, workflow de coleta, cliente/fixture, store/export e MarketInput possuem fonte única. Bot conserva fachadas e adapters do consumidor; parâmetros, orçamento, guard HTTP, configuração global/diagnóstico e saída de collect-market permanecem compatíveis. Não deslocar carteira/risco/flags/backtest/análise para a biblioteca.

A API recebe MarketSettings validado e callbacks/adapters, sem descobrir diretório de dados pela instalação. CLI exige root absoluto dentro do workspace e schema mínimo PAPER/market; não aceita tabelas financeiras. O bot conserva sua descoberta/validação anterior. O mesmo diretório implica o mesmo .writer.lock e checkpoints, sem copiar/migrar/resetar banco. Store v1 e implementação das operações/DDL são preservados.

Exportador recebe contexto/package_version: wrapper do bot informa sua distribuição/revisão/fingerprint; standalone identifica market-data/core e data_root, sem usar o Git dos dados ou depender de bot. Schema/parser/files/candles hash continuam iguais; metadados variáveis não são equivalência financeira. Leitor histórico não recebe quinto arquivo ou formato alternativo.

Inspeção genérica de distribuição/RECORD vive em market-data, parametrizada por versão/importer e editables aceitos. A política e mapa da composição ficam em cada consumidor. Bot inclui controles próprios e arquivos efetivamente carregados de bot/core/market-data, rejeitando core/dados editables. CLI de desenvolvimento pode reconhecer seu próprio editable validado; os smokes de release exigem wheels. RECORD verifica consistência, não assinatura externa. Alterar apenas market-data altera fingerprint e bloqueia retomada sob protocolo antigo; report permanece somente leitura e preserva identidade selada.

Wheels/locks próprios e fonte local exata; core 06A não é reconstruído, bot e dados usam novos diretórios dist/06b-final. Não criar workspace/Git agregador ou publicar/commitar automaticamente. B-M1 baseline antes de extrair, B-M2 standalone sem bot e B-M3 integração antes da conclusão.

## Consequências e limites

Os artefatos locais precisam existir nos caminhos dos locks; não há publicação em índice. Dependências externas da baseline foram reutilizadas após versão/RECORD conferidos para manter instalação/testes offline; cache frio completo não é demonstrado. Não houve rede de mercado real, novo ativo/estratégia/modo, janela final real reaberta, AWS ou migração financeira. 06C/06D permanecem etapas futuras. Evidências e limitações no guia 06B; decisões anteriores permanecem históricas.
