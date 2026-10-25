# Sprint 02 — Coleta pública, validação e persistência de dados

Data da especificação: 24/10/2026.

**Estado em 24/10/2026: implementada; AC01–AC17 aprovados na validação local offline.** Consulte o [guia](../testes/sprint-02-validacao.md) e as [evidências](../testes/sprint-02-evidencias.json). Coleta Binance real NÃO EXECUTADA. A entrega original desta especificação era somente documental; a implementação foi solicitada posteriormente pelo responsável.

Referências: [planejamento](../planejamento.md), [arquitetura atual](../arquitetura.md), [Sprint 01](sprint-01.md), [guia 01](../testes/sprint-01-validacao.md) e [evidências 01](../testes/sprint-01-evidencias.json).

## 1. Objetivo e incremento demonstrável

Adicionar ao pacote `cripto_bot` a coleta síncrona de dados públicos Spot: candles fechados de 15 minutos, metadados do símbolo e uma observação de bid/ask. Validar os dados, guardar sua origem e conteúdo bruto, persistir candles normalizados e retomar uma coleta interrompida sem duplicação ou avanço sobre lacunas.

Ao final, uma execução com fixture deverá criar um dataset local verificável. Repetir a mesma janela não acrescentará candles duplicados; reiniciar após falha retomará o primeiro candle ainda não confirmado. Uma exportação JSONL compactada, acompanhada de manifesto e hashes, permitirá inspecionar e reproduzir os dados.

O modo continua exclusivamente `PAPER`. Coletar dados públicos não constitui execução financeira. `run-once` permanece NOOP e não passa a executar a coleta implicitamente.

## 2. Diretórios, repositórios e dependências

- Workspace: `/home/cams7/Dev/Cripto`.
- Aplicação e diretório de todos os comandos Python/uv: `/home/cams7/Dev/Cripto/cripto-bot`.
- Documentação central e repositório independente: `/home/cams7/Dev/Cripto/docs`.
- Pacote existente: `cripto-bot/modules/trading/src/cripto_bot`.

Esta Sprint estende o módulo existente. Não criar outro repositório para adapters ou subpacotes internos. Cada **novo módulo independente** futuro terá seu diretório diretamente no workspace e Git próprio, conforme a seção 5 do planejamento.

| Dependência | Verificação nesta especificação | Condição para implementar |
|---|---|---|
| D01 — Sprint 01 aprovada | Guia registra AC01–AC16 aprovados; evidências registram 79 testes, qualidade e wheel | Preservar e reproduzir a regressão antes de concluir a Sprint 02 |
| D02 — Integridade dos fontes | Os 14 hashes de fontes, manifest, lock e pin Python conferem com o JSON de evidências 01 | Se divergirem na implementação, analisar mudanças e revalidar o que foi afetado |
| D03 — Versionamento | Repositórios de aplicação e docs separados; ambos sem alterações locais no início desta inspeção | Preservar histórico e trabalho posterior do usuário |
| D04 — Revisões observadas | Aplicação `2224caf`; documentação `a36baf9` | Registrar os commits efetivos na futura validação |
| D05 — Ambiente | Python 3.13.15 e uv 0.12.19 definidos nos artefatos da Sprint 01 | Confirmar versão real via uv; não confundir aviso do pyenv com ausência do Python gerenciado pelo uv |
| D06 — Rede pública | Não testada nesta especificação; não é necessária ao aceite offline | Coleta pública somente com opt-in e acesso legítimo disponível |

A revisão das evidências e da integridade é suficiente para detalhar esta Sprint. Os testes anteriores não foram executados novamente nesta entrega documental. Não há bloqueio conhecido para a especificação; regressões ou ferramentas indisponíveis durante a implementação mantêm seu aceite pendente.

## 3. Escopo e exclusões

Incluído: HTTPX síncrono, cliente de leitura pública com rotas fechadas, fixtures determinísticas, validação temporal/decimal, SQLite local, checkpoint transacional, exportações e manifestos. Um símbolo inicial `BTCUSDT`, somente `15m`, sem generalização prematura.

Excluir carteira, saldo, reservas, ledger financeiro, estratégia, sinais, ordens simuladas ou reais, validação de quantidade de ordem, backtest, WebSocket, agendamento, notificações, AWS, boto3, SDK Binance, containers e infraestrutura. Não implementar TESTNET/LIVE, autenticação, assinatura ou endpoints privados.

A captura de filtros é necessária para conhecer e versionar os metadados; aplicar filtros a futuras ordens pertence às Sprints seguintes. Não aplicar filtros atuais retroativamente a candles históricos.

Estimativa orientativa: 2–5 dias úteis, revisável pelo executor conforme os resultados reais, sem reduzir o aceite para caber no prazo. AWS zero; somente CPU, disco e eventual tráfego local.

## 4. Contratos de configuração e CLI

### 4.1 Compatibilidade com a Sprint 01

Preservar `check-config`, `run-once`, defaults PAPER, rejeição de credenciais e sanitização. O arquivo existente com somente `mode="PAPER"` continua válido. `run-once` continua retornando `NOOP/PAPER/orders_sent=0` sem rede ou banco, inclusive quando um arquivo de coleta é fornecido.

Introduzir somente os campos definidos nesta Sprint. Ajustar testes antigos de campos extras para distinguir os novos campos permitidos dos que permanecem desconhecidos. Não afrouxar a validação global para acomodar qualquer configuração.

Exemplo proposto `config/market.fixture.example.toml`:

```toml
mode = "PAPER"

[market]
source = "fixture"
symbol = "BTCUSDT"
interval = "15m"
fixture_file = "config/fixtures/market-sample.json"
data_dir = "data/market-fixture"
page_limit = 1000
max_pages = 10
```

O exemplo público `config/market.public.example.toml` usa `source="binance_public"`, `data_dir="data/market-public"` e omite `fixture_file`; os demais campos são iguais. Não incluir URL, chave, secret, proxy ou opção de assinatura.

Regras:

1. Sem tabela `market`, `check-config` e `run-once` mantêm os defaults da Sprint 01; `collect-market` exige configuração de coleta explícita.
2. Somente `fixture` e `binance_public` são fontes válidas. Arquivo fixture é obrigatório para a primeira e proibido para a segunda. Não inferir fonte pública pela falta de fixture.
3. Fixar a allowlist de símbolo em `BTCUSDT` e intervalo em `15m`; rejeitar grafias diferentes e outros ativos nesta etapa. A existência e a permissão Spot serão confirmadas pelos metadados.
4. `page_limit` inteiro de 1 a 1000, default 1000; `max_pages` inteiro de 1 a 10, default 10. Booleanos não são inteiros válidos na fronteira.
5. Resolver caminhos relativos ao diretório de trabalho da aplicação, inclusive com `--config` absoluto. Resolver paths e symlinks; fixture e dados precisam permanecer dentro do repositório `cripto-bot`. Rejeitar escape por `..`/symlink antes de abrir dados ou rede. Documentar essa convenção no README.
6. Somente `CRIPTO_BOT_MODE` continua sendo override por ambiente. Campos extras, variáveis desconhecidas `CRIPTO_BOT_*`, credenciais e modos proibidos continuam falhando. Validar o arquivo antes de aplicar override.
7. `check-config` valida estrutura e caminhos sem criar diretórios, abrir banco ou iniciar rede. A existência/leitura da fixture é verificada no comando de coleta.

### 4.2 Comando novo

```text
cripto-bot collect-market --config CAMINHO --start UTC --end UTC [--allow-network]
```

`--start` e `--end` são obrigatórios, em ISO 8601 com `Z` ou offset explícito, convertidos para UTC. Definem uma janela **[start, end)** de aberturas de candles, ambos alinhados a 15 minutos, com start < end. Não aceitar timestamps naive, milissegundos arbitrários ou end futuro em relação ao último fechamento disponível. Fixar no início o tempo de referência obtido pela fonte; nenhuma página aumenta a janela durante o comando.

Limitar a janela a `page_limit × max_pages` candles esperados. Se os limites ou o tempo disponível impedirem a conclusão, reportar coleta incompleta e preservar o progresso confirmado; não retornar sucesso sobre dataset parcial.

Fonte fixture funciona com sockets bloqueados e não aceita `--allow-network`, para identificar uso acidental do opt-in. Fonte pública exige `--allow-network` a cada execução; sua ausência falha **antes de construir o cliente de rede ou criar o banco**. Nenhum teste automático usa esse opt-in para sair à internet.

Resultados JSON em stdout incluem `run_id`, UTC, `mode=PAPER`, `orders_sent=0`, fonte, dataset, símbolo, intervalo, janela, contadores de candles inseridos/duplicados/ignorados, `next_open_time` e `complete`. Logs JSON Lines continuam em stderr, sem dumps de configuração ou corpo de erro remoto.

| Situação | Exit code e resultado |
|---|---|
| Janela inteiramente disponível e exportada | 0, `status=COLLECTED`, `complete=true` |
| Argumentos/configuração inválidos, inclusive opt-in ausente | 2, erro sanitizado, sem coleta |
| Falha de rede/dados/banco/exportação ou coleta incompleta | 3, `status=COLLECTION_FAILED`, `complete=false`, progresso confirmado quando disponível |
| Falha interna inesperada | 1, diagnóstico sanitizado |

Falha com páginas já confirmadas precisa informar esse progresso. Zero candles novos é sucesso somente se a janela já estiver integralmente persistida e verificada. Não confundir ausência de resposta com ausência de dados esperados.

## 5. Fonte pública e transporte

### 5.1 Superfície permitida

Usar host fixo HTTPS `data-api.binance.vision`, dedicado a dados públicos e sem autenticação, conforme a [documentação oficial](https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md). Somente as quatro leituras necessárias:

| Rota GET | Uso nesta Sprint |
|---|---|
| `/api/v3/time` | Tempo de referência para o limite de candles fechados |
| `/api/v3/exchangeInfo` com símbolo explícito | Snapshot de metadados e filtros |
| `/api/v3/klines` com símbolo, intervalo, início/fim e limite | Páginas de candles |
| `/api/v3/ticker/bookTicker` com símbolo explícito | Observação atual de bid/ask e quantidades |

Referências: [endpoints gerais](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general) e [dados de mercado](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market). A API identifica klines pela abertura e permite até 1000 por página; os parâmetros temporais são UTC. O contrato da aplicação será mais restrito que o catálogo público.

O adapter expõe métodos específicos, sem `request(method, url)` acessível à aplicação. Proibir métodos de mutação, rotas privadas, headers de autenticação e parâmetros de assinatura. Não configurar base URL pelo arquivo/ambiente. Sem redirects, sem fallback de host, sem proxies herdados (`trust_env=False`), com TLS verificado.

A fixture contém `server_time`, `exchange_info`, `klines` e `book_ticker`, com payloads sintéticos no formato das respostas esperadas. O adapter fixture usa MockTransport ou transporte equivalente injetado para percorrer os mesmos parsers e a mesma paginação. Não distribuir um cliente de produção com caminhos especiais de falha para testes.

### 5.2 Falhas, limites e tempo

Definir orçamento monotônico de 90 segundos por comando. Timeouts iniciais propostos: connect/pool 5 s, read/write 10 s, sempre limitados ao orçamento restante. Timeouts HTTPX por fase não substituem um orçamento total; verificar tempo restante antes/depois de cada chamada e espera. Limitar também bytes por resposta a 5 MiB, consumindo o corpo dentro do orçamento. Relógio monotônico, espera e jitter devem ser substituíveis nos testes.

No máximo três tentativas por leitura (a inicial e duas repetições), apenas para timeout/transporte transitório ou 5xx. Backoff inicial de 0,5 s e 1 s com jitter limitado. Não sobrepor retries do HTTPTransport aos da aplicação. Erros de parse, contrato, 4xx ordinários ou símbolo inválido não são repetidos.

Para 429, respeitar `Retry-After`, sem tentar antes do prazo; se a espera não couber no orçamento, encerrar e registrar o próximo instante permitido. 418 interrompe imediatamente, sem retries no comando. Persistir no store, quando disponível, o `not_before` global da fonte pública para que um reinício não ignore o bloqueio conhecido. Nunca dormir sem limite ou contornar restrição por outro host/IP. Esses comportamentos derivam dos [limites REST oficiais](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#limits); as quantidades e deadlines são decisões locais desta especificação.

Registrar headers de peso e metadados de limite permitidos; não tratar limites como constantes universais. Informar falhas por códigos locais, sem copiar arbitrariamente mensagens remotas aos logs. A falta de acesso legítimo à fonte mantém a demonstração offline e o teste público pendente.

## 6. Modelo e qualidade dos dados

### 6.1 Candles

Modelo mínimo: origem/dataset, símbolo, intervalo, abertura/fechamento UTC, OHLC, volumes base/cotação, número de negócios, instante de recebimento, instante de processamento e referência/hash do bruto. Decimais partem de strings; timestamps e contadores usam inteiros validados, rejeitando bool. Nunca converter valores financeiros por float.

- Preços finitos e estritamente positivos; volumes finitos não negativos; número de negócios inteiro não negativo.
- `low <= min(open, close) <= max(open, close) <= high`.
- Abertura alinhada; fechamento compatível com o intervalo de 900.000 ms e menor que o tempo de referência da fonte. O próximo candle começa em `open_time + 900000`.
- Descartar candles ainda abertos da coleção normalizada e contar a exclusão; preservar a resposta bruta. Uma exclusão não pode completar artificialmente a janela pedida.
- Comparar o conjunto retornado com a janela solicitada. Dados fora de ordem, lacunas, horários desalinhados e progresso estacionado são erros explícitos, nunca interpolação ou ordenação silenciosa para esconder contrato violado.
- Duplicata com mesma chave e conteúdo normalizado é idempotente. Mesma chave com conteúdo diferente é conflito: preservar a evidência e interromper, sem sobrescrever o dado confirmado.
- Snapshot/filtro atual não comprova regras históricas. A coleta não quantiza OHLC por tick atual.

Fixar o limite exclusivo de aberturas encerradas como `floor(server_time_ms / 900000) × 900000`. Exigir `end` menor ou igual a esse limite. Converter sem aritmética financeira em float. No cenário fixture, `server_time` é sintético e independe do relógio de parede; logs de execução mantêm UTC real/injetável.

### 6.2 Metadados e cotação

Exigir símbolo retornado igual ao solicitado, `status=TRADING`, `isSpotTradingAllowed=true` e ativos base/cotação coerentes com BTC/USDT. Preservar snapshot bruto de `exchangeInfo`, filtros e campos novos, sem mapear a resposta inteira para um schema que rejeite toda evolução aditiva. Campos mínimos usados devem continuar estritamente validados. Não antecipar motor de validação de ordens.

Normalizar bid, ask e quantidades por Decimal; preços positivos, quantidades não negativas e bid <= ask. O snapshot `bookTicker` consultado não fornece horário do evento de mercado: registrar recebimento local e `market_timestamp=null`, sem inventar esse instante nem aplicar a cotação atual como preço histórico. Nesta Sprint ele serve para inspeção, não autoriza fill.

## 7. Persistência, paginação e recuperação

### 7.1 SQLite como fonte durável

Usar `sqlite3` da biblioteca padrão, com esquema versionado e transações explícitas. Escrever decimais como TEXT canônico e timestamps UTC como inteiros em milissegundos ou texto padronizado, com conversões testadas. Não usar REAL para dinheiro nem pickle. Consultas parametrizadas e constraints para identidades únicas.

Isolar dados fixture dos públicos por namespace/dataset: fixture incorpora SHA-256 do conteúdo do arquivo, fonte pública incorpora host e versão do schema. O checkpoint é identificado por dataset, símbolo, intervalo e início da janela; ele representa a **próxima abertura ainda não confirmada**. Permitir estender `end` mantendo o mesmo início, sem confundir checkpoint de outra janela/origem.

Persistir no banco respostas brutas como bytes, SHA-256, rota/parâmetros permitidos, código HTTP, recebimento e versão do parser. Os bytes brutos são o conteúdo recebido pelo parser, antes da normalização, não uma alegação de captura do tráfego TLS. Snapshots de metadados/cotação e dados normalizados mantêm referência a esses registros.

Para cada página válida, uma transação grava bruto, candles e checkpoint. Um erro invalida a página inteira; páginas anteriores confirmadas permanecem utilizáveis. Respostas inválidas podem ser guardadas como diagnóstico em transação separada, sem tocar candles/checkpoint. Não manter transação aberta durante chamada HTTP ou espera.

### 7.2 Algoritmo de coleta

1. Validar modo/configuração/janela e opt-in antes dos adapters com efeitos. Abrir store e verificar schema/bloqueio persistido da fonte.
2. Obter tempo de referência e snapshots de metadados/cotação. Falha nesses pré-requisitos impede coletar páginas nessa execução.
3. Carregar checkpoint da janela e confirmar integridade/continuidade dos registros já existentes. Não confiar apenas no maior timestamp armazenado.
4. Pedir a próxima página com `startTime=next_open_time`, fim limitado a `end - 1 ms`, intervalo UTC e limite validado.
5. Validar toda a página e seu alinhamento com a próxima abertura esperada. Somente um prefixo contínuo pode avançar o checkpoint; uma página com lacuna é rejeitada integralmente. Página vazia antes de end, duplicatas conflitantes e ausência de progresso encerram como incompleto.
6. Confirmar a transação; retomar do checkpoint confirmado. Se o orçamento ou máximo de páginas se esgotar, sair com código 3, sem perder progresso já confirmado.
7. Somente após cobertura integral da janela e exportação válida retornar COLLECTED.

Um escritor por dataset durante todo o comando, incluindo a exportação, com lock local exclusivo de sistema operacional e liberação após morte do processo; erro de concorrência tem espera limitada. A transação SQLite continua protegendo cada commit. Não implementar lease distribuído nesta etapa.

### 7.3 Exportação reproduzível

Em `data_dir`, manter `market.sqlite3` e snapshots exportados por identidade única de execução. Ao concluir uma janela, produzir `candles.jsonl.gz` ordenado, `raw.jsonl.gz` com conteúdo bruto codificado sem perda, snapshots e `manifest.json`. O manifesto inclui fonte, símbolo, intervalo, janela, contagem, estado completo, hashes de arquivos/dados, versão de schema/parser/código/configuração/fixture e tempos da execução.

Reprodução significa mesmos candles normalizados e hash canônico para as mesmas entradas; não exigir o mesmo run_id, tempo de recebimento ou bytes gzip variáveis. Fixar a serialização/hash dos campos determinísticos e documentar o que é excluído do hash.

Escrever exportação em diretório temporário dentro de `data_dir`, finalizar por rename atômico no mesmo filesystem e publicar manifesto somente do snapshot concluído. SQLite é a fonte de verdade; não prometer transação entre banco e filesystem. Falha depois do commit, antes da exportação, retorna código 3; próxima execução recompõe a exportação dos dados confirmados sem duplicar candles. Snapshots incompletos/temporários nunca são anunciados como completos.

## 8. Entregáveis e tarefas

Caminhos da aplicação abaixo são relativos a `/home/cams7/Dev/Cripto/cripto-bot`; caminhos `docs/...` são relativos ao workspace. Os arquivos desta tabela foram entregues na implementação; consultar o guia para a verificação do estado real.

| Caminhos | Entrega |
|---|---|
| `modules/trading/src/cripto_bot/domain/market.py` | Modelos, invariantes temporais e decimais |
| `modules/trading/src/cripto_bot/application/ports.py` | Portas mínimas usadas pela coleta e persistência |
| `modules/trading/src/cripto_bot/application/collect_market.py` | Caso de uso, progresso, deadline e resultados |
| `modules/trading/src/cripto_bot/adapters/binance/public.py` | GETs fechados, parsers e falhas públicas |
| `modules/trading/src/cripto_bot/adapters/binance/fixture.py` | Fonte determinística sem rede, reaproveitando parsers |
| `modules/trading/src/cripto_bot/adapters/storage/market_sqlite.py` | Schema, transações, deduplicação, checkpoint e lock local |
| `modules/trading/src/cripto_bot/adapters/storage/market_export.py` | JSONL gzip e manifesto verificável |
| `adapters/config.py`, `domain/models.py`, `entrypoints/cli.py`, `observability/logging.py` no pacote | Configuração/composição/eventos da coleta, preservando contratos anteriores |
| `pyproject.toml`, `uv.lock`, `.gitignore`, `README.md` | HTTPX resolvido no lock, instruções e exclusão de dados/artefatos locais |
| `config/market.fixture.example.toml`, `config/market.public.example.toml`, `config/fixtures/market-sample.json` | Exemplos e fixture sintética pública |
| `tests/unit/test_market.py`, `test_collect_market.py`, `test_binance_public.py`, alterações em `test_config.py` | Fronteiras, transporte e fluxo com falhas |
| `tests/integration/test_market_storage.py`, `test_collect_cli.py`, harness e smoke test do wheel | SQLite real local, reinício, CLI offline e pacote instalado |
| `docs/arquitetura.md`, `docs/decisoes/0003-coleta-publica-e-persistencia-local.md` | Decisões e diferenças entre fonte bruta, banco e exportação |
| `docs/testes/sprint-02-validacao.md`, `docs/planejamento.md`, `docs/sprints/sprint-02.md` | Resultados reais, estado e limitações |

Sequência de implementação: conferir dependências → adicionar HTTPX compatível e resolver lock → modelos/parsers → fixture/transporte público → store e testes de falha → caso de uso → CLI → exportação → regressão/wheel → documentação. Criar apenas pacotes realmente usados. Não atualizar indiscriminadamente dependências existentes.

## 9. Critérios de aceite e testes planejados

A matriz abaixo define o contrato de aceite. Os cenários obrigatórios foram executados e aprovados na implementação; os resultados reais e limitações estão no [guia de validação](../testes/sprint-02-validacao.md#6-matriz-ac01ac17).

| ID | Cenário | Evidência exigida |
|---|---|---|
| AC01 | Regressão da Sprint 01 | Defaults, NOOP, help, decimais, logs e rejeições preservados; testes ajustados somente aos campos novos |
| AC02 | Coleta fixture pela CLI e wheel | Janela completa, dois candles sintéticos de 00:00 e 00:15 em 01/10/2026 UTC, JSON correto e zero ordens, sob guard de sockets |
| AC03 | Fonte pública sem opt-in; modo/credencial/host/path proibido | Falha antes de criar cliente/banco; sentinelas comprovam ordem dos efeitos |
| AC04 | Paginação maior que 1000 registros | Pelo menos 1001 candles, parâmetros e fronteiras corretos, nenhuma perda/repetição |
| AC05 | Candle aberto e limite de fechamento exato | Aberto não normalizado; janela futura rejeitada; fronteira UTC correta |
| AC06 | Precisão e payloads inválidos | Float/bool/NaN, OHLC incoerente, preço/volume inválido, schema/truncamento e timestamp naive rejeitados |
| AC07 | Lacuna, desordem, página vazia e sem progresso | Exit 3; página inválida não avança; não preencher preços artificialmente |
| AC08 | Duplicação e conflito | Repetição sem novas linhas; conflito preserva valor confirmado e produz erro |
| AC09 | Morte/falha antes e depois do commit | Antes: rollback integral; depois: retoma próximo candle, sem duplicação |
| AC10 | Falha de exportação/manifesto e reinício | Banco íntegro, snapshot incompleto não publicado; reexportação bem-sucedida |
| AC11 | Duas execuções e isolamento de fontes/janelas | Lock impede escritores concorrentes; checkpoint fixture não contamina público ou outro início |
| AC12 | Timeouts, 5xx, 429, 418 e deadline | Tentativas limitadas, Retry-After respeitado, bloqueio conhecido preservado, espera simulada sem teste lento |
| AC13 | Contrato do cliente público | Só quatro GETs e host permitido; redirect, POST/DELETE, auth e proxy herdado impedidos |
| AC14 | Metadados/filtros e bid/ask | Símbolo Spot válido, snapshots versionados, timestamp de mercado ausente não inventado |
| AC15 | Manifesto e dados brutos | Hashes conferem, bruto recuperável, Decimal em strings e repetibilidade canônica |
| AC16 | Banco indisponível/corrompido/schema incompatível | Erro sanitizado, nenhum avanço nem recriação destrutiva |
| AC17 | Qualidade e distribuição | Ruff, mypy strict, pytest com branches e build aprovados; wheel isolado coleta fixture |

Testes de HTTP usam MockTransport e sockets bloqueados, inclusive nos filhos da CLI/wheel. Testar o próprio guard deliberadamente. Banco SQLite real é local; falhas de disco/commit/exportação são injetadas de forma determinística. Não instalar/usar SDK AWS para simulação desta etapa.

Cobrir todas as ramificações de segurança, avanço de checkpoint, deduplicação, rollback e retry; apresentar relatório e justificar lacunas não críticas, sem exclusões para esconder caminhos financeiros/temporais. A cobertura de 100% da Sprint 01 não vira requisito percentual cego da Sprint 02.

### Comandos de validação previstos

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked --group dev
uv run --locked python --version
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy modules/trading/src
uv run --locked pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
uv build
uv run --locked cripto-bot check-config --config config/market.fixture.example.toml
uv run --locked cripto-bot collect-market --config config/market.fixture.example.toml --start 2026-10-01T00:00:00Z --end 2026-10-01T00:30:00Z
uv run --locked cripto-bot collect-market --config config/market.fixture.example.toml --start 2026-10-01T00:00:00Z --end 2026-10-01T00:30:00Z
```

A fixture deve fornecer tempo de referência posterior a 00:30 UTC e metadados/cotação sintéticos coerentes. A primeira execução insere dois candles; a segunda insere zero, confirma a continuidade e pode gerar outro snapshot com o mesmo hash de dados canônicos. A geração/atualização deliberada do lock precede `--locked` quando HTTPX for adicionado.

Atualizar o smoke test para instalar o wheel exato em ambiente separado no módulo, executar em diretório neutro com paths absolutos de config/fixture, sem PYTHONPATH do checkout e com guard de sockets. Registrar origem em site-packages, nome/hash do wheel e teste do comando novo, além dos comandos antigos. Evitar reaproveitar silenciosamente um wheel anterior.

O teste real público é **opcional e separado**, com `--allow-network`, janela pequena já fechada e diretório de dados distinto. Só executar se explicitamente incluído no pedido de implementação e permitido pelo ambiente. Falta desse teste não reprova os contratos offline; registrar `NÃO EXECUTADO` e não alegar acesso regional comprovado.

## 10. Evidências, recuperação e conclusão

O guia 02 deverá registrar preparação/versões, commits dos dois repositórios, alterações locais relevantes, comandos/exit codes, testes e cobertura, matriz AC01–AC17, hash do wheel, contagem de candles, checkpoint antes/depois, dump sintético sanitizado, hashes de manifesto/dados e ensaios de falha. Separar teste planejado, executado, aprovado e pendente.

Rede/dados inválidos não eliminam páginas válidas anteriores. Reexecução usa o mesmo namespace/início e verifica o prefixo. Banco corrompido ou schema incompatível interrompe; preservar cópia para diagnóstico, sem recriar sobre o original. Exportação é regenerável a partir do banco; conteúdo bruto e checkpoints são evidências, não cache descartável durante investigação.

Ignorar pelo Git os diretórios gerados `data/`, relatórios locais, bancos e arquivos de lock de execução, preservando fixtures sintéticas em `config/fixtures` e testes. Limpeza exige identificar o dataset criado pela execução; não apagar outros datasets, `.git`, documentação ou artefatos anteriores. Não enviar dados gerados para remotos nesta tarefa.

Concluir a Sprint somente com todos os critérios obrigatórios offline atendidos, documentação atualizada e evidências revisáveis. Se um deles falhar, marcar PENDENTE e registrar correção; não iniciar a Sprint 03. A implementação não autoriza rede pública, infraestrutura, notificações ou negociação por implicação.

## 11. Prompt autossuficiente de execução

```text
Implemente somente a Sprint 02 — Coleta pública, validação e persistência.

Workspace obrigatório: /home/cams7/Dev/Cripto.
Aplicação e diretório dos comandos: /home/cams7/Dev/Cripto/cripto-bot.
Documentação central: /home/cams7/Dev/Cripto/docs, com Git independente.
Caminhos docs/... são relativos ao workspace; demais caminhos desta Sprint
são relativos ao módulo cripto-bot. Leia as instruções locais aplicáveis,
docs/planejamento.md, docs/sprints/sprint-02.md integralmente,
docs/sprints/sprint-01.md, docs/testes/sprint-01-validacao.md e suas evidências,
docs/arquitetura.md e docs/decisoes/. Inspecione README, manifest, lock,
modules/trading/src/cripto_bot e testes antes de editar. Preserve mudanças.

Dependências numeradas:
1. Sprint 01 aprovada, com contratos de configuração, CLI, decimais e logs.
2. Código/lock conferidos contra revisões/evidências; divergências analisadas.
3. Python 3.13.15, uv 0.12.19 e escrita permitida no módulo/docs.
4. Documentação oficial da API pública e HTTPX reconfirmada na execução.
Se requisito indispensável falhar, registre o impedimento em
docs/testes/sprint-02-validacao.md e não avance o trabalho dependente.

Somente PAPER Spot, BTCUSDT e candles 15m. Estenda o repositório existente;
não crie Git para subpacotes internos. Cada novo módulo independente futuro
deve nascer diretamente na raiz do workspace com seu próprio Git.
Não implemente carteira, estratégia, execução financeira, Testnet/LIVE,
WebSocket, notificações, AWS, boto3, infraestrutura ou Sprint 03.
Não leia credenciais nem altere projetos LotoBot.

Siga os contratos das seções 4–7 desta especificação: novos exemplos TOML,
fixtures e comando collect-market com janela UTC [start,end), mantendo
check-config/run-once compatíveis e NOOP offline. Fonte fixture sem rede;
binance_public exige --allow-network e host HTTPS fixo data-api.binance.vision.
Só GET /api/v3/time, /exchangeInfo, /klines e /ticker/bookTicker, todos sob
/api/v3, com parâmetros validados. Sem URL arbitrária, auth, assinatura,
redirect ou proxy herdado. Não execute coleta real nesta implementação
salvo se explicitamente solicitada separadamente no pedido do responsável.

Adicione HTTPX síncrono compatível no manifest e lock sem atualizar tudo.
Implemente domain/market.py, application/ports.py e collect_market.py,
adapters/binance/public.py e fixture.py, adapters/storage/market_sqlite.py
e market_export.py. Atualize configuração, modelos, CLI e logs existentes.
Use parsers comuns nas fontes, Decimal de strings e UTC, rejeite dados
incoerentes, preserve snapshots de metadados e bruto com origem/hash.
Não invente timestamp de mercado para bookTicker ou preços históricos.

SQLite é fonte durável: bruto, candles e checkpoint na mesma transação por
página; identidade isola fixture/público e início da janela. Valide prefixo
contínuo, deduplique iguais e rejeite conflitos. Não avance sobre lacunas,
respostas vazias ou páginas inválidas. Lock local impede dois escritores.
Exporte JSONL gzip e manifesto em snapshot finalizado atomicamente; falha
de exportação preserva banco e permite reexportar sem duplicar candles.
Implemente deadline monotônico de 90s, timeouts e tamanho de resposta
limitados, no máximo três tentativas por GET transitório, Retry-After em
429 e interrupção em 418. Não repita erros de contrato ou contorne bloqueio.

Entregue exemplos config/market.fixture.example.toml e
config/market.public.example.toml, config/fixtures/market-sample.json,
testes unitários/integração e regressão AC01–AC17. Reaproveite o guard de
sockets e aplique-o aos subprocessos; HTTPX MockTransport sem rede real.
Cubra >1000 candles, fronteiras temporais, duplicação, conflitos, gaps,
rollback, reinício, exportação, concorrência, limites, 429/418 e sanitização.

Execute da raiz do módulo uv sync --locked --group dev, uv run --locked
ruff check ., ruff format --check ., mypy modules/trading/src e pytest -q
--cov=cripto_bot --cov-branch --cov-report=term-missing, com uv run --locked
em cada ferramenta. Execute uv build, check-config e duas collect-market
com a fixture, start 2026-10-01T00:00:00Z e end 2026-10-01T00:30:00Z.
Primeira coleta insere 2 candles; repetição insere 0 e mantém dados íntegros.
Teste o wheel instalado em ambiente separado dentro do módulo, diretório
neutro, origem site-packages, sem PYTHONPATH e com sockets bloqueados.
Registre hash do wheel e comandos exatos; adapte somente com justificativa.

Atualize README e .gitignore sem ignorar fixtures. Documente em português
docs/arquitetura.md, docs/decisoes/0003-coleta-publica-e-persistencia-local.md,
docs/testes/sprint-02-validacao.md, docs/sprints/sprint-02.md e planejamento.
Registre versões, revisões dos dois repositórios, resultados reais,
contagens/checkpoints/hashes, cobertura, limites, diagnóstico, recuperação,
limpeza e AWS zero. Teste público não executado deve permanecer declarado
como não executado. Não trate mock como comprovação de acesso Binance.

Conclua somente com AC01–AC17 obrigatórios aprovados e evidências locais
reproduzíveis. Caso contrário, registre PENDENTE e ações necessárias.
Não inicie Sprint 03, publique remotos, envie mensagens ou ordens.
```

## 12. Fontes e verificação desta especificação

Fontes oficiais consultadas em 24/10/2026:

- [Binance — host somente de mercado](https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md), para a escolha do host e disponibilidade das rotas sem chave.
- [Binance — endpoints gerais](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general), para tempo e metadados Spot.
- [Binance — mercado](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market), para candles e bid/ask.
- [Binance — REST e limites](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#limits), para rate limit, 429 e 418.
- [Binance — filtros](https://github.com/binance/binance-spot-api-docs/blob/master/filters.md), para distinguir captura de regras atuais da futura admissão de ordens.
- [HTTPX — transportes](https://www.python-httpx.org/advanced/transports/) e [timeouts](https://www.python-httpx.org/advanced/timeouts/), para injeção de transporte e limites por fase.
- [Python 3.13 — sqlite3](https://docs.python.org/3.13/library/sqlite3.html), para persistência local e controle transacional explícito.

Os limites de janela, esquema, CLI, defaults e estratégias de persistência acima são decisões de projeto. Reconfirmar versões e contratos externos na implementação; não presumir compatibilidade apenas por constarem nesta especificação.

Na entrega original da especificação houve leitura do planejamento, código e testes pertinentes, revisão das evidências 01, comparação de 14 hashes, inspeção dos dois repositórios e consulta às fontes oficiais, sem implementação naquela etapa. A execução posterior está registrada a seguir.

## 13. Registro da execução — 24/10/2026

Implementação e validação offline concluídas: 204 testes, Ruff, formatação, mypy strict, build e wheel instalado aprovados. Coleta fixture repetida insere 2 e 0 candles, mantém checkpoint e hash canônico; testes de morte de processo, rollback, retomada, conflito e exportação são reproduzíveis. HTTPX 0.28.1 foi acrescentado ao lock sem atualização indiscriminada das dependências existentes.

Detalhes explicitados durante a implementação: a composição fica em `entrypoints/market.py`, e a exportação inclui `provenance.json` além dos arquivos inicialmente enumerados. Erros de janela estáticos retornam 2; end ainda não fechado, detectado após obter o horário da fonte, retorna 3 (`WINDOW_NOT_CLOSED`). O not_before é global aos datasets do mesmo banco, sem coordenação entre data_dirs/hosts. Símbolo/intervalo continuam fixos no schema desta Sprint.

As métricas exatas, lacunas de cobertura, hashes e comandos estão no guia/evidências. Coleta pública real, AWS, ordens e notificações NÃO EXECUTADOS. A Sprint 03 não foi iniciada nem houve publicação/commit automático.
