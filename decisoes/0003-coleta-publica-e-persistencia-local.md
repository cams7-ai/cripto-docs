# ADR 0003 — Coleta pública e persistência local

Data: 24/10/2026. Estado: adotada e validada offline na Sprint 02.

## Contexto

A base PAPER precisa coletar dados de mercado, verificar qualidade e retomar trabalhos interrompidos. Esta etapa ainda não possui carteira, estratégia ou execução financeira. A documentação e a aplicação continuam em repositórios independentes, conforme a seção 5 do [planejamento](../planejamento.md).

## Decisão

Estender o pacote existente em `/home/cams7/Dev/Cripto/cripto-bot`. Domínio e caso de uso recebem dados e portas; adapters implementam transporte, armazenamento e exportação. A composição do comando fica em `entrypoints/market.py`. Não criar outro Git para subpacotes internos.

Usar HTTPX 0.28.1 síncrono. O adapter expõe quatro leituras específicas e um guard valida método, host, rota, parâmetros e ausência de autenticação antes do transporte. HTTPS, TLS verificado, sem redirects e `trust_env=False`. A fonte pública exige `--allow-network` no comando; fixture rejeita esse flag. Os comandos anteriores continuam offline e `run-once` permanece NOOP.

A fixture usa MockTransport e os mesmos parsers/rotas. Sua identidade incorpora SHA-256 do arquivo. A fonte pública incorpora host e versão do parser/schema. Metadados extras são preservados; campos mínimos usados são validados estritamente. Não aplicar filtros atuais a candles históricos nem inventar timestamp de mercado para bookTicker.

Usar SQLite da biblioteca padrão, schema v1, foreign keys, transações explícitas e `synchronous=FULL`. Cada página confirma bruto, candles e checkpoint juntos. Dinheiro permanece em strings canônicas dentro de TEXT JSON; o único REAL do schema é o instante operacional `not_before`, que não representa valor financeiro.

O checkpoint é a próxima abertura não confirmada, identificado por dataset e início da janela; símbolo e intervalo são fixos nesta Sprint. Verificar todo o prefixo antes da retomada. Duplicatas iguais são idempotentes; divergências interrompem sem sobrescrever. Páginas inválidas ficam como evidência de rejeição, sem avançar o checkpoint.

Um flock exclusivo imediato protege cada diretório de dados durante o comando inteiro, inclusive exportação. Isso é mais restritivo que um escritor por dataset dentro do mesmo banco. O sistema operacional libera o lock após morte do processo; não apagar o arquivo do lock como mecanismo de recuperação.

Exportações derivam do banco. Um diretório temporário no mesmo filesystem contém JSONL gzip, snapshots, proveniência e manifesto; rename publica o snapshot finalizado. Banco e filesystem não formam uma transação única: erro após commit retorna falha e a próxima execução reexporta os dados confirmados. Não anunciar snapshot incompleto como sucesso.

## Alternativas e consequências

SQLite evita um serviço adicional ou ORM para a base local. Guardar bruto como BLOB no mesmo banco permite atomicidade com a normalização e o checkpoint; JSONL/gzip é a interface de inspeção/exportação, não a fonte transacional. DynamoDB e exportações S3 permanecem etapas futuras.

O hash canônico cobre somente candles ordenados, com decimais normalizados. Recebimento, processamento, raw_id e run_id ficam na proveniência e não alteram esse hash. O manifesto guarda também revisão Git, fingerprint dos fontes, configuração, parser/schema, fixture e hashes dos arquivos exportados.

O orçamento monotônico limita chamadas e esperas, com três tentativas máximas por GET transitório e sem retry de contrato. 429 preserva o prazo conhecido; 418 interrompe. A restrição persistida é global aos datasets do **mesmo banco**; não há coordenação entre bancos distintos, hosts ou outros consumidores do mesmo IP. Não alegar que esse mecanismo garante respeito aos limites de toda uma rede compartilhada.

A implementação usa Linux/flock e arquivo de dados local. Rename atômico protege a publicação perante falha de processo; não foi ensaiada perda de energia, falha física do dispositivo, NFS ou durabilidade distribuída. A coleta pública real não foi executada.

## Fontes e evidências

Contratos oficiais reconfirmados em 24/10/2026: [host público Binance](https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md), [mercado](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market), [endpoints gerais](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general), [limites REST](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#limits), [HTTPX transportes](https://www.python-httpx.org/advanced/transports/), [timeouts](https://www.python-httpx.org/advanced/timeouts/) e [sqlite3](https://docs.python.org/3.13/library/sqlite3.html).

Ver [guia de validação 02](../testes/sprint-02-validacao.md) e [evidências](../testes/sprint-02-evidencias.json).


## Adendo — extração 06B, 26/10/2026

O responsável solicitou executar a 06B após a 06A: coleta/parsers/portas/store/export foram extraídos para biblioteca/CLI `cripto-market-data`, em Git irmão. O registro histórico acima descreve a decisão da Sprint 02. Bot conserva facade/delegação compatível; core é dependência pura, sem import inverso. Rotas/guard, budgets/retries, store v1 e dados/checkpoints/lock continuam com a mesma semântica. Proveniência é fornecida pelo produtor, e a CLI tem root explícito independente da instalação. Detalhes no [ADR 0009](0009-market-data-e-proveniencia-do-produtor.md) e [guia 06B](../testes/sprint-06b-validacao.md).
