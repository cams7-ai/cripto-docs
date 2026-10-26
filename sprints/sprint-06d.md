# Sprint 06D — PAPER contínuo local e validação operacional

Detalhamento: 26/10/2026. **Estado atual: SOFTWARE_VALIDATED/PILOT_PENDING; D-M1–D-M3 validados offline, D-M4/D-M5 pendentes.** Próxima etapa após 06A–06C aprovadas. A execução do prompt12 implementou o software offline, sem iniciar piloto, acessar conta ou enviar mensagens/ordens. As afirmações históricas de “não executado nesta revisão” nas seções1–13 referem-se ao detalhamento inicial; seção14/guia registram a execução atual.

Referências: [planejamento](../planejamento.md), seções 3, 4.5–4.10, 5, 6.5, 8–10 e 13; [agregador 06](sprint-06.md); [06C](sprint-06c.md), [guia](../testes/sprint-06c-validacao.md), [evidências](../testes/sprint-06c-evidencias.json) e [reconstrução externa verificada](../testes/sprint-06c-reconstrucao-externa.json); [05](sprint-05.md), [guia 05](../testes/sprint-05-validacao.md) e [validação analítica](../testes/duckdb-parquet-validacao.md). Consultar [arquitetura](../arquitetura.md), [arquitetura modular](../arquitetura-modular.md), [SMA](../estrategias/trend_sma.md), [catálogo](../estrategias/README.md), [matriz modular](../testes/estrategias-modulares-validacao.md), [bancos](../bancos/README.md), ADRs [0005](../decisoes/0005-estrategia-modular-e-persistencia.md), [0006](../decisoes/0006-backtest-historico-e-protocolo.md), [0007](../decisoes/0007-duckdb-parquet-analitico.md), [0008](../decisoes/0008-core-e-identidade-da-composicao.md), [0009](../decisoes/0009-market-data-e-proveniencia-do-produtor.md) e [0010](../decisoes/0010-analytics-por-snapshots-somente-leitura.md).

## 1. Objetivo e incremento demonstrável

Implementar no `cripto-bot` um processo local PAPER com dados públicos, relógio operacional, estado transacional recuperável, execução simulada parcial/versionada e notificações desacopladas. Depois de validar o software offline e congelar a composição, observar pelo menos sete dias consecutivos e 99% dos ciclos elegíveis, com relatórios diários e drills separados.

Não reduzir a entrega a um loop sobre a fixture anterior: a carteira atual aceita fill integral único e o escopo modular atual não habilita continuous. Novos contratos precisam ser implementados e validados antes do piloto. Aceite de software não equivale a sete dias observados; disponibilidade operacional não demonstra rentabilidade ou execução real na corretora.

## 2. Baseline e condições de avanço

Conferência somente leitura em 26/10/2026: **214/214 hashes de fontes/configuração/testes/controles e 16/16 arquivos de artefatos da 06C conferidos**, zero divergência; status APPROVED_OFFLINE_06C e C01–C18 aprovados. Nenhuma suíte reexecutada nesta revisão.

| Dependência | Observado | Exigência antes do marco dependente |
|---|---|---|
| P01 — Extrações | Core/dados/analytics integrados; bot 542 testes, analytics 28; quatro wheels e contratos aprovados offline | Reinspecionar hashes e reproduzir regressões afetadas |
| P02 — Git | Bot `d695e0e383f3316e74c88aaa56ed7b7586d93bb2`; core `e666e7e23dcb421177c80838a28c230d4433bdf2`; dados `1da6f4fe25c6940cc3e96416415ddf6f1ffcb4e9`; analytics `236775dd6ee84375d8dbd11e4c3fc2b11747019a`; docs `d62a4c3a84dd00edfef404f297c7febac2a6b658`; todos limpos no início | Preservar alterações posteriores; registrar revisões/estado usados |
| P03 — Artefatos | Reconstrução externa antiga esclarecida na 06C; hashes atuais/históricos separados | Usar a composição efetivamente verificada; não rotular rebuild em dist/06a-final como artefato original 06A |
| P04 — Ferramentas | Python 3.13.15, uv 0.12.19, setuptools 84.2.0; bibliotecas 0.1.0, DuckDB 1.5.6 | Preservar dependências/pins; cache frio completo ainda não comprovado |
| P05 — Capacidades ausentes | Executor integral, Wallet/Intent sem cumulativos parciais; configuração fixture/backtest, sem continuous, outbox ou clientes locais | Novo modelo/store isolado e APIs do bot; manter contratos anteriores |
| P06 — Mercado real | Somente quatro GETs públicos implementados; quote informa market_timestamp=None; elegibilidade/filtros atuais não consultados nesta revisão | Preflight autorizado verifica símbolo, clock, dados e regras; incompatibilidade mantém piloto pendente |
| P07 — Serviços | Contratos locais mail-sender/whatsapp-notify examinados por fontes, sem acessá-los | Endpoints/serviços disponíveis e destinatários de teste autorizados antes de envio efetivo; não copiar configuração alheia |
| P08 — Operação | Não existe observação contínua de sete dias comprovada | Janela/denominador/configuração/artefatos congelados antes de T0; nenhum resultado presumido |

542/28 e os 54/120 históricos de core/dados não são contagens mínimas nem execuções desta revisão. A falta de endpoint/destinatário ou de período observado não impede implementar/testar offline; impede declarar o marco externo correspondente aprovado.

## 3. Escopo, propriedade e arquivos previstos

Python/local/PAPER, Binance Spot sem alavancagem, BTCUSDT/15m, uma instância `trend_sma` 20/50 e política `exclusive_owner`. Biblioteca de dados continua aquisição/qualidade; analytics continua projeção readonly; core mantém helpers puros existentes. Bot possui execução/capital/risco, scheduler, ledger, decisões, custódia e outbox de eventos. Não criar outro projeto/Git ou transferir finanças para DuckDB.

| Local no bot, sob src/cripto_bot | Responsabilidade nova/alterada |
|---|---|
| `domain/continuous/{models,engine,execution}.py` | Estado/eventos do modelo paper-continuous-v1; pedidos, fills cumulativos, custos/risco/custódia |
| `application/continuous_{run,reconcile,control}.py` | Scheduler, recuperação, checkpoints, controle persistente e idempotência |
| `adapters/continuous_config.py`, config global e registro modular | Envelope continuous separado, strict, paths/escopos/limits e compatibilidade |
| `adapters/continuous_market.py` | Adapter do PublicSource/SQLiteMarketStore existentes; quote/filtros/relógio e budgets |
| `adapters/storage/continuous_sqlite.py` | Novo store financeiro schema1 em diretório próprio; journal/ledger/projeções/CAS/lock |
| `application/notifications.py`, `adapters/notifications/{mail,whatsapp}.py` | Porta de entrega e clientes HTTP locais; sem boto3/browser/credenciais Binance |
| `adapters/storage/notification_sqlite.py` | Fila de entrega derivada e tentativas/leases, sem saldo/execução |
| `entrypoints/continuous.py`, CLI e adapters de relatório | Comandos, guards de rede/envio, relatório diário por snapshot e analytics |

Nomes indicam contratos futuros, não arquivos já existentes. Reutilizar funções financeiras puras/SMA do core; não modificar sem necessidade os reducers/DDL antigos. A extensão de relatório contínuo deve consumir snapshots prontos. Se analytics precisar renderer novo, adicionar capacidade/versionamento compatível e testar ambos os projetos; preservar renderers/formato antigos. Mudança material de biblioteca exige wheel novo identificado e lock atualizado, nunca sobrescrever artefato anterior para manter hash aparente.

Fora: AWS/SAM/Terraform, cliente privado ou order/test, Demo/Testnet/LIVE, novos ativos/estratégias, ranking/Sortino/seleção/walk-forward/ML/BT-A–BT-F, OMS remoto, validação de fila/impacto real, novos endpoints Binance/WebSocket, alterações nos serviços externos e novo teste final histórico. Nenhum ganho financeiro mínimo é critério desta etapa.

## 4. Configuração, flags e comandos

Novo `[continuous]`, sem reutilizar `[strategy]` fixture como configuração de produção. Envelope mínimo: environment=local, evaluation_type=continuous, enabled=false, wallet_id, data_dir, market_data_dir, notification_data_dir, initial_usdt="10000.00", parâmetros financeiros atuais como strings decimais e símbolo/intervalo fixos. Paths resolvem cwd e ficam na raiz funcional do bot; rejeitar symlinks/traversal fora dela e colisão com diretórios anteriores. Arquivos locais com destinatários não entram nos relatórios/Git.

Flags exigem simultaneamente continuous.enabled e instância habilitada com environments=[local], modes=[PAPER], evaluation_types=[continuous], symbols=[BTCUSDT], dependências válidas e versão registrada. `.active` e fixture/backtest mantêm a semântica anterior. Nova capacidade não habilita outro escopo. Para continuous, execution=paper_bounded; fixture mantém immediate. `capital_weight=0.10`, max_entry_fraction/max_exposure_fraction=0.10, max_daily_loss_fraction=0.01, max_drawdown_fraction=0.05, fee_bps=10 e slippage_bps=5. Spread vem do bid/ask observado; não somar novamente um spread sintético ao book. Custos/regras ficam congelados antes do piloto.

Sem habilitados e sem store existente: continuous-run retorna NOOP antes de banco/cliente; não inicializa capital. Com store/posições existentes e módulos desabilitados, deve haver custódia/reconciliação; entradas bloqueadas, sem NOOP que esconda posição. Sem origem de preço autorizada, reportar preço indisponível/estado pausado, sem fabricar marcação.

Comandos implementados no recorte offline (uso externo depende dos gates específicos):

| Comando | Contrato |
|---|---|
| `continuous-prepare --config FILE` | Valida composição/settings, cria store vazio com identidade e estado PREPARED; não coleta, envia ou inicia a janela; só após opt-ins válidos |
| `continuous-run --config FILE [--once] [--allow-network]` | Continua PREPARED/RUNNING, processa slots/pedidos/custódia; source pública exige opt-in; once limita a um passo do scheduler, não acelera calendário |
| `continuous-reconcile --config FILE` | Replay/auditoria locais, sem rede/envios; não corrige por reset nem inventa cotação |
| `continuous-report --config FILE [--day YYYY-MM-DD]` | Exportação readonly de snapshot confirmado; diário UTC/total, sem completar dias ausentes |
| `continuous-control --config FILE --action pause\|resume\|kill\|disable\|reload\|cancel --reason TEXT [--order-id ID]` | Pedido de controle persistido/idempotente, sem envio; cancel exige ID; resume/reload têm gates descritos abaixo |
| `notify-drain --config FILE [--once] [--allow-send]` | Worker independente da negociação; lê eventos locais e trata outbox; envio real exige opt-in e autorização do destinatário |

Preservar comandos/defaults anteriores e check-config sem efeitos. Códigos: 0 sucesso/NOOP/pausa solicitada, 2 config/escopo/argumentos/opt-in inválidos, 3 operação incompleta/bloqueada/corrupção/busy, 1 interno. JSON/status/eventos sanitizados com run_id/mode=PAPER/orders_sent=0; fills são simulated_fills, nunca orders_sent. Execução interrompida não vira período aprovado por exit0. SIGTERM solicita parada segura e registra PAUSED quando possível; SIGKILL é recuperado pelo journal. Control/status não exigem cliente Binance.

## 5. Dados, relógio e scheduler

### 5.1 Aquisição permitida e elegibilidade

Reutilizar PublicSource e store de mercado, sem ampliar rotas: GET time, exchangeInfo(symbol=BTCUSDT), klines(15m/timeZone0) e ticker/bookTicker(symbol=BTCUSDT) no host HTTPS data-api.binance.vision. TLS, no-proxy/no-redirect, headers sem auth/chaves e budgets/retries/429/418/not_before permanecem. Clientes de notificações têm allowlist separada; não afrouxar guard Binance para permitir seus POSTs.

Preflight: TRADING, isSpotTradingAllowed, base BTC/quote USDT, candles fechados/contínuos, cotação válida e filtros suportados. Core atual rejeita filtros não suportados; não remover/ignorar filtros recebidos para conseguir operar. Mapear regras efetivamente usadas e rejeitar hipóteses não verificáveis; se o exchangeInfo atual exigir regra sem dados/capacidade disponíveis nas quatro rotas, bloquear preparação operacional e registrar incompatibilidade. Resolver por decisão técnica explícita/revalidação antes do piloto; este documento não autoriza ampliar endpoints ou substituir filtro real por proxy silencioso. Disponibilidade atual de BTCUSDT não foi verificada nesta revisão.

Guardar resposta bruta/hashes, metadata original/normalização e recebimento UTC de cada observação usada. bookTicker não traz timestamp de mercado: freshness é tempo desde recebimento local sincronizado, com market_timestamp=None, não idade comprovada no servidor. Validar bid/ask/quantidades finitos, não negativos e book não cruzado. Não inferir negócio executado a partir de livro exibido.

### 5.2 Temporização causal

Slot de decisão é o fechamento UTC C, múltiplo de 900000 ms. Candle de score abre em C−900000 e termina em C−1; disponibilidade somente depois de C, confirmado pelo server time. Acordar em C+2s, deadline de processamento C+90s; nenhum fill antes de observação posterior à decisão e de atraso mínimo de 1s. Poll de OMS a cada 5s, com budget de requisição de quote≤5s, sem esperar o candle seguinte para cancelar expiração. Um novo slot nunca usa candle aberto/futuro.

Warmup: 50 candles anteriores ao primeiro score, range de opens [T0−51×STEP,T0−STEP), sem ordens/PnL. SMA20/50 recebe o candle novo depois do warmup; restarts reconstroem janela e watermark a partir de dados/journal, sem repetir sinal. Lacuna bloqueia decisão até recuperar sequência; backfill recupera indicador, nunca executa sinais de slots vencidos.

UTC para identidades e dias; monotonic para prazos/sleep. Sincronizar server time no início e a cada 5min; aceitar somente amostras com RTT≤1s e offset estimado absoluto≤1s. Salto de relógio/discrepância wall versus monotonic >1s bloqueia novos compromissos até nova amostra válida. Recebimento da quote precisa ter idade≤5s no evento de admissão/fill; renovar quote vencida ou não executar. Não atribuir horário futuro para aparentar freshness.

Budget total de decisão≤90s; aquisição por adapter usa Budget com no máximo30s/restante disponível, sem mudar default standalone. Risco/commit têm prioridade sobre relatório e mensagens. Persistir not_before no mesmo store de mercado; backoff não apaga prazo do slot. Cache de metadata por no máximo1h, renovar antes de admissão se vencido; mudança de regras cancela compromissos incompatíveis e pausa até revalidação, sem trocar protocolo congelado silenciosamente. Um pedido/poll por vez e zero busy-loop; registrar tentativas/peso/429, interromper chamadas sob bloqueio. Nenhuma chamada HTTP dentro de transação financeira.

Se processo atrasar além de C+90s, registrar MISSED para esse slot e não executar o sinal antigo. Recuperação registra todos os slots vencidos com causa; somente slot atual ainda dentro do prazo pode avaliar. Error/data unavailable/stale são falhas do ciclo no denominador, não HOLD para melhorar disponibilidade.

## 6. Modelo de execução simulada `paper-continuous-v1`

Novo reducer no bot, sem ampliar silenciosamente paper-integral-v1/paper-modular-v1 ou reutilizar suas carteiras. Mesma precisão Decimal80, quantização de moeda e steps/ticks existentes; cálculos oficiais nunca por float. Reutilizar sizing/preço adverso/filtros/risco puros onde aplicáveis. Um compromisso ativo por carteira/símbolo; reservas/posições pertencem à instância, sem empréstimo ou venda a descoberto.

### 6.1 Pedidos, preços e disponibilidade simulada

A decisão gera pedido MARKET_PROXY limitado por preço (paper_bounded), ou LIMIT para drills explicitamente configurados. TTL60s e atraso mínimo1s; preço máximo BUY/mínimo SELL fixado na admissão, usando quote bid/ask e slippage5bps, arredondado de forma conservadora ao tick. Para cada fill posterior, custo adverso calculado a partir de quote nova não pode violar o cap/limit; caso contrário, nenhum fill, mantendo pedido até expirar. LIMIT não melhora artificialmente para preço não observado.

Preço tocado/cruzado não garante execução. A cada observação elegível, quantidade máxima é floor_step(min(restante, 10% da quantidade exibida do lado consumido, capacidade financeira admitida)); zero/dust/cap insuficiente significa sem fill. Não consumir mais de uma vez o mesmo quote_id; quotes com mesmo conteúdo de preços/quantidades não reabrem capacidade enquanto não houver alteração observada. Isso é hipótese conservadora local, não modelo de fila/liquidez real ou garantia de execução Spot. Nunca usar volume de candle que ainda não fechou para aumentar fill.

Nos drills, roteiro determinístico injeta disponibilidade/latência/ausência de fill e snapshots sequenciados, com modelo/seed/limites fixados; não sobrepor esse roteiro à observação pública nem apresentar preenchimentos forçados como mercado observado. Não adicionar heurística aleatória não registrada. Parâmetros de fill pertencem ao modelo de execução, não a uma flag de estratégia.

### 6.2 Transições e finanças

Estados: CREATED → RESERVED → OPEN → PARTIALLY_FILLED → FILLED; terminais alternativos REJECTED, CANCELED e EXPIRED. UNKNOWN é estado de recuperação que impede novos compromissos até replay/resolução, sem liberar reserva. Eventos ADMIT/OPEN/PARTIAL_FILL/CANCEL/EXPIRE têm IDs persistidos; repetição de mesmo ID/payload é NOOP, ID com conteúdo diferente é corrupção. Fill_id único e sequência por pedido; cumulative_qty cresce monotonamente e nunca supera requested_qty.

BUY reserva capital para quantidade solicitada no cap mais taxa, arredondado para cima à precisão de moeda; cada fill confirma seu notional/taxa e mantém cobertura do restante. SELL reserva BTC próprio. Nunca consumir saldo de outra instância, liberar capital ainda comprometido ou aceitar notional acima do reservado. Taxa10bps por fill, paga em USDT; custo médio/realizado/fees/atribuição acumulados com as regras de precisão atuais e tratamento explícito do último resíduo, sem arredondamento duplicado. Redução de posição conserva custo proporcional; zerar custo somente quando inventário zera.

Cancelamento/expiração só libera reserva não consumida e termina o restante; corrida fill/cancel serializada por journal/CAS, sem fill depois do evento terminal. Após restart, CANCEL_REQUESTED/UNKNOWN não autoriza reemitir fill: reconstruir eventos e concluir cancelamento local identificado. Sem quote válida não fabricar fill, mesmo em saída; cancelamento local de restante não exige preço e não vende o inventário já adquirido.

Risco global/instância permanece obrigatório: entrada/exposição10%, perda diária1%, drawdown5%, peso0.10 e política exclusiva. Reserva conta na exposição; parcial não abre orçamento novo. Reavaliar risco/filtros/limites antes de cada incremento; redução de limites pausa/cancela restante incompatível sem liquidar posição. Novo pedido só após terminal/reconciliação do anterior. Posição residual é mark-to-market; nenhum fechamento forçado para melhorar relatório.

Oráculo obrigatório de parcial: capital10000, BUY solicitado1BTC/cap100USDT/taxa0,1%, reserva100,10. Fill0,4 a100 consome40,04; fill0,3 consome30,03; cancelar0,3 libera30,03. Resultado livre USDT9929,93, BTC0,7, custo70,07, fees0,07; reservas zero. Na venda de0,2 a110: receita líquida21,978, custo liberado20,02, realizado1,958, posição0,5/custo50,05. Confirmar em Decimal/ledger e testes de duplicação/crash; não usar exemplo como previsão de resultado.

## 7. Controles, posições e reconfiguração

Controles entram por inbox durável `data_dir/control-requests/`, com request_id/pilot_id/ação/argumentos/hash e escrita fsync+rename atômico, sem disputar o writer flock financeiro do daemon. Comando retorna ACCEPTED/PENDING, não afirma aplicação imediata. O único escritor consome requests, valida, grava evento/controle e acknowledgment no journal; repetição idêntica é NOOP, conflito é erro. Consultar aplicação no relatório/status local, com request_id/seq. Processar inbox antes de construir cliente ao retomar, antes de admissão/fill e a cada tick fora de I/O; registrar latência e priorizar controle ao retornar de chamada bloqueante. Nunca tratar request sem ack como kill já aplicado. Se daemon não responder, runbook usa parada do processo e conserva inbox para aplicação antes da retomada; não há execução remota a cancelar.

pause/kill são persistentes e verificados antes de cada admissão/fill, não simples variável de processo. pause bloqueia novas entradas e cancela restante aberto de forma local auditada; kill adiciona trava de segurança sem resume automático. Inventário permanece, com custódia/monitoramento/risco/relatórios; nenhuma liquidação automática. Saída deliberada exige nova autorização/decisão admissível, quote válida e limites, nunca venda inventada por desligamento.

disable de módulo mantém proprietário/custo e estado DRAINING se houver posição/pedido; não redistribui capital ou inventário. UNKNOWN bloqueia compromissos afetados. Reload incrementa geração e registra config_hash; parâmetros financeiros/modelo/dataset/composição não mudam durante a janela congelada. Desativar/pausar/kill por segurança é permitido e observado, sem remover slots do denominador. Reativação exige reconciliação, autorização operacional e incremento de epoch; não executa decisões antigas. Ações de controle determinísticas usadas em drills têm diretório/período separados.

Composição permanece exclusiva: segunda instância ativa, política ponderada/segregada ou capacidade ausente é configuração rejeitada antes de efeitos. Orçamentos/conflitos com fakes são contratos, não validação de combinações reais inexistentes.

## 8. Persistência e compatibilidade

Novo diretório configurado, sugerido `cripto-bot/data/continuous-<pilot_id>/`, com continuous.sqlite3 schema1/modelo paper-continuous-v1. Não abrir/inicializar em diretórios de paper/strategy/backtest anteriores. Store de mercado separado; journal e ledger financeiro na mesma transação dos efeitos, sem dependência de commit atômico entre bancos de mercado e financeiro: eventos financeiros referenciam observações imutáveis/hashes já confirmados.

| Tabela/registro financeiro previsto | Chaves/invariantes |
|---|---|
| journal/postings | seq crescente, event_key único, payload/hash encadeados; postings balanceados por ativo e FK ao journal; história imutável |
| orders/fills | order_id PK; fill_id PK/order_id FK; cumulativos/estados como projeções reconstruíveis; qty/taxa/notional exatos e seq causador |
| cycles/configurations/instances | (pilot_id,close_time) único; decision_id/config_generation/owner registrados; versões de configuração imutáveis |
| wallet/checkpoint/control | CAS por version/seq, watermark de decisão/OMS e travas persistentes; nenhuma projeção substitui replay |
| notification_events | event_id único vinculado ao journal/slot/relatório, payload canônico imutável, criado atomicamente com evento a notificar |

FKs ligadas, SQLite WAL/synchronous FULL, transações curtas e writer flock local único/CAS; readers readonly e backup consistente por API apropriada, sem copiar somente .sqlite3 enquanto WAL está ativo. Validar schema/modelo/inventário de objetos na abertura; incompatibilidade/corrupção falha sem reset. Detalhar DDL real/índices/constraints/triggers e dicionário durante a implementação em docs/bancos/continuous-sqlite.md, com catálogo/diagrama/testes. Não criar esse documento vazio nesta revisão.

Fila de entrega em notifications.sqlite3/schema1, diretório próprio e lock próprio: eventos derivados por event_id/source_hash, tentativas (event_id,canal,attempt_no) únicas, estado/retry_at/lease_until/last_outcome; sem ativos/saldos/fills. Journal financeiro contém notification_events imutáveis; worker copia via UPSERT idempotente e pode reconstruir faltantes após crash. Não exigir escrita do worker no banco financeiro ou lock exclusivo mantido pelo daemon. Relação entre bancos é lógica, sem FK cruzada/transação distribuída; duplicação de entrega continua possível. Criar docs/bancos/notification-sqlite.md e catálogo na implementação.

Registro final histórico `data/backtest-usage/test-usage.sqlite3` permanece intacto. Nenhum backtest final real será executado para testar continuous. Identidade runtime inclui bot/core/dados/analytics efetivos, locks/pins, modelo, configuração e fontes; mudança de identidade bloqueia retomada automática do piloto selado. Relatório antigo preserva identidade selada e não migra carteira; recuperação necessita versão compatível ou plano explícito.

## 9. Notificações locais e autorização de efeitos

Porta NotificationSender retorna CONFIRMED, FAILED ou UNKNOWN, distinguindo aceite do serviço de recebimento humano. Dados de destinatário/URLs locais são configuração, não copiados do LotoBot. INTEGRATION_MODE aceita somente LOCAL nesta etapa; mail-sender-aws/boto3 pertencem à 07/08, sem fallback oculto.

| Serviço | Contrato inspecionado nas fontes locais | Confirmação |
|---|---|---|
| mail-sender | POST /api/v1/mail/send; to, subject, body, message_type opcional | HTTP200 e JSON message de sucesso conforme contrato do serviço; 2xx genérico/payload inválido não basta |
| whatsapp-notify | GET /whatsapp/session/status; POST /whatsapp/messages/send com contact/message | Sessão SESSAO_ABERTA; envio com status=enviado; demais estados não confirmam |

URLs configuradas explicitamente em MAIL_SENDER_URL/WHATSAPP_NOTIFY_URL, inicialmente loopback localhost/127.0.0.1/::1, portas informadas pelo operador. MAIL_TO/MAIL_CONTENT_TYPE; WHATSAPP_ENABLED=false default, WHATSAPP_CONTACT e WHATSAPP_TIMEOUT_SECONDS quando habilitado. Rejeitar userinfo, redirect/proxy herdado, host/path/método fora da allowlist e payload extra; credenciais Binance continuam proibidas. Não iniciar/parar sessão ou browser/QR, nem alterar serviços compartilhados. WhatsApp não habilitado não é requisito para simular negociação.

Outbox: PENDING → IN_FLIGHT/lease60s → CONFIRMED ou RETRY_WAIT/UNKNOWN/FAILED. Timeout após POST pode ter enviado: persistir UNKNOWN, não confirmar nem repetir imediatamente. Após60s, política permite nova tentativa identificada com aviso de duplicação possível; total máximo3 tentativas por canal, backoff60s/300s. Sem garantia exactly-once do serviço. WhatsApp fechado/erro/unknown aciona e-mail configurado, registrando que ambos podem chegar; não repetir negociação. Erro de configuração/permanente mantém falha para intervenção; não mover destinatário para outro canal sem configuração autorizada.

Worker separado, prioridade financeira preservada. Deadline monotonic de10s por tentativa, connect/pool≤1s, read/write≤3s/restante, resposta≤16KiB; fechar stream/cliente ao exceder limite e registrar resultado desconhecido quando aplicável. Timeout de inatividade HTTPX não é deadline total: implementar controle explícito do orçamento. No máximo uma tentativa por segundo por worker; coalescer alarmes repetidos em janela5min sem perder eventos financeiros, startup/diário/encerramento com IDs determinísticos. Após3 falhas manter pendência visível, sem retry ilimitado. Confirmar worker lease recuperado após morte.

Eventos: início, bloqueio/kill/dados indisponíveis, alteração de custódia, relatório diário e encerramento. Não enviar um alerta por poll/quote/HOLD. Fallback/double failure aparecem nos relatórios e em diagnóstico local independente; não afirmar monitor externo configurado nesta Sprint.

**Autorizações separadas:** testes de contrato usam MockTransport/fakes, sem mensagens. Envio efetivo requer instrução explícita do responsável, endpoints e destinatários de teste declarados e --allow-send; o flag sozinho não concede autorização. E-mail de teste real deve usar mail-sender local. WhatsApp real só quando habilitado/autorizado, sempre whatsapp-notify. Não usar ferramentas desta revisão para enviar mensagens. Piloto só alcança aceite global após ensaio real autorizado do e-mail mínimo e dos canais efetivamente habilitados; falta de autorização/serviço mantém esse caso pendente, sem falsificar confirmação.

## 10. Protocolo de observação e aceites operacionais

### 10.1 Congelamento e duração

Depois de marcos offline aprovados, preflight autorizado e definição dos canais, congelar pilot_id, hashes dos quatro projetos/wheels/locks/pins, configuração/modelo financeiro/execução/filtros, flags/owner, capital10000 e orçamento. Manifesto local imutável inclui timezone UTC, T0/Tend, cronograma, controle de integridade e regras desta seção. Credenciais/contatos não entram no manifesto público; registrar referência/hash da configuração privada.

T0 é a próxima meia-noite UTC com pelo menos15min de antecedência após preflight/warmup prontos; se esse prazo não couber, a meia-noite seguinte. Tend=T0+7×24h. Preflight pode ser repetido antes de T0, registrando entradas; nenhum resultado observado permite escolher outra janela favorável. Criar nova janela após correção é tentativa nova e mantém a anterior com causa/falhas; não apagar evidência nem selecioná-la por PnL.

**Denominador fixo: 672 slots**, fechamentos T0+i×15min, i=0..671, intervalo UTC [T0,Tend). Nenhuma manutenção programada excluída nesta primeira janela. Downtime/restart/kill/disable/stale/429/erro de commit ocupam seus slots e não reduzem o denominador. Warmup/preflight estão antes de T0; drills têm pilot_id/diretório separados e não contaminam amostra.

Warmup inesperado dentro da janela conta como falha. O numerador conta somente decisão processada/recusa válida por risco/posição/custódia, persistida até C+90s, com dados íntegros e frescos, reconciliação/checkpoint coerentes e nenhuma divergência inexplicada. HOLD ou rejeição legítima de risco não exige fill; slot sem dados não é recusa válida de estratégia. Evidenciar categorias separadamente, incluindo faltantes/atrasados, e rastrear atraso de outbox/relatórios à parte.

Aceite disponibilidade: n/672≥0,99, isto é, **pelo menos666 slots válidos** (máximo6 não processados no prazo), e sete dias completos de parede. Período menor é INCOMPLETE, mesmo com100%; crash/falha não é excluído retroativamente. Módulo inicialmente desabilitado não inicia janela; desativação de segurança durante a janela mantém denominador e custódia. Zero fills espontâneos não reprova por si só: cobertura de execução vem dos drills obrigatórios, sem forçar trades.

### 10.2 Relatórios e drills

Sete relatórios diários UTC, dias completos [T0+d×24h,T0+(d+1)×24h), mais consolidado. Cada um contém saldo livre/reservado/inventário/custo/fees/PnL/risco/posições/pedidos, clock/data freshness, ciclos elegíveis/processados/faltantes e causas, uptime/restart/latência/custos, outbox/tentativas/canal e UNKNOWN, versões/hashes/contexto e limitações. Relatório atrasado deve indicar atraso, sem completar dados ausentes. Snapshot reconciliado, publicação atômica via analytics e revisão visual; falha de export não refaz estratégia. Fechamento é Tend com posição residual marcada somente por preço válido e idade registrada; sem marca válida, valor indisponível, não inventar zero. Não liquidar para encerrar.

Drills offline obrigatórios e isolados: fill integral; dois parciais; cap tocado sem disponibilidade; limite nunca executado; expiração/cancelamento de restante; quote futura/vencida/zero qty; dados faltantes/ordem/candle aberto; offset/jump de relógio; queda antes/depois de reserva/fill/commit/rename; repetição/ID conflitante; concorrência writer/CAS e corrida cancel/fill; saldo/filtro/risco bloqueando; UNKNOWN; pause/kill/reload/disable com posição; perda de canal/session fechada/timeout após POST/fallback e lease do worker. Falha de cada serviço e ambos, resposta inválida, ausência de opt-in, destinatário inválido e URLs/mutações Binance bloqueados. Evidenciar injeções, não classificá-las como eventos do mercado observado.

### 10.3 Matriz D01–D22

| ID | Condição/prova exigida | Estado após execução offline |
|---|---|---|
| D01 | Baseline/hashes/ordem de marcos e fontes anteriores preservados | Aprovado offline |
| D02 | Escopos/defaults/NOOP/config inválida sem efeitos, sem import privado | Aprovado offline |
| D03 | Store/modelo novo e rejeição de carteiras/schemas antigos, CAS/lock/replay | Aprovado offline |
| D04 | Dados públicos/clock/50 warmup/causalidade/freshness e slots vencidos | Offline validado; operação pendente |
| D05 | Fill integral/parcial múltiplo, cumulativos/fees/postings/reservas e oráculo | Aprovado offline |
| D06 | Limite tocado sem fill, ausência de qty, TTL/cancel e residual/dust | Aprovado offline |
| D07 | Risco global/instância, filtros/capital/posição própria, nenhuma alavancagem | Aprovado offline |
| D08 | Crash/duplicação/ID conflitante/CAS/corrida fill-cancel/UNKNOWN | Aprovado offline |
| D09 | Pause/kill/reload/disable/reativação, custódia e gerações sem liquidação | Aprovado offline |
| D10 | Exclusive_owner, conflitos/orçamentos com fakes; composições ausentes rejeitadas | Aprovado offline |
| D11 | Guards de quatro GETs, credenciais/private/order/test/redirect/proxy bloqueados | Offline validado; operação pendente |
| D12 | Outbox durável derivada do evento financeiro, dedupe/leases/timeout/fallback | Offline validado; operação pendente |
| D13 | Contratos locais de mensagens por fakes, sem repetir negociação | Offline validado; operação pendente |
| D14 | Entrega efetiva autorizada de e-mail/canais habilitados, separada dos fakes | Não executado; requer autorização/configuração/período real |
| D15 | Wheels/locks/identidade instalados, regressões anteriores e snapshot selado/registro final | Aprovado offline |
| D16 | Preflight real elegível, configuração/modelo/janela/canais congelados antes de T0 | Não executado; requer autorização/configuração/período real |
| D17 | Sete dias consecutivos, 672 denominador e ≥666 válidos, causas/reinícios sem exclusões | Não executado; requer autorização/configuração/período real |
| D18 | Sete diários/consolidado e drills distintos, valores conciliados/revisão visual | Offline validado; operação pendente |
| D19 | Recursos/latência/RSS/disco/bruto/HTTP/outbox medidos; orçamento/timeouts respeitados | Offline validado; operação pendente |
| D20 | README/API/arquitetura/ADRs, bancos/catálogos/SMA/runbook/guia/evidências atuais | Aprovado offline |
| D21 | Pausa/custódia/backup/restauração e rollback compatível ensaiados sem reset | Offline validado; operação pendente |
| D22 | D01–D21 e AC01–AC18 aplicáveis aprovados/revistos antes de 07 elegível | Pendente — aceite global/D-M4–D-M5 |

D04/D11/D12/D13 têm casos offline e operacionais distintos; aprovação do fake não preenche rede/entrega efetiva. Registar NÃO EXECUTADO quando recurso/período/autorização ausente; não marcar não aplicável para remover um requisito. WhatsApp desabilitado pode ter ensaio externo não aplicável justificado, mantendo seu contrato offline testado.

## 11. Marcos, comandos, custos e documentação

### 11.1 Execução incremental

1. **D-M1 — baseline:** criar guia pendente antes de testar; reconferir 214 hashes/16 artefatos (ou mudanças justificadas), qualidade/suíte/smoke 06C; guardar archive e stores/oráculos sintéticos, hashes de bancos/registro final sem abrir contas.
2. **D-M2 — software offline:** reducer/modelo/store/config/relógio/OMS/controle/outbox/workers/clientes e reports; fixtures/MockTransport, testes de crash/concorrência/precisão e regressões. Documentos técnicos reais na mesma entrega; não executar rede ou envio para suprir teste.
3. **D-M3 — release/preparo:** build bot em dist/06d-final e wheels novos somente de bibliotecas alteradas, novos locks identificados; instalação neutra/teste defaults/CLI por quatro projetos. Snapshot/modelo/documentação/runbook e pré-protocolo prontos. Estado SOFTWARE_VALIDATED/PILOT_PENDING, não Sprint06D aprovada.
4. **D-M4 — operação autorizada:** depois de instrução explícita sobre coleta pública e serviços/destinatários de teste, realizar preflight/entrega, congelar janela e iniciar piloto; observar sete dias, relatórios e controles operacionais. Drills offline isolados já aprovados não substituem espera. Interrupção material registra resultado real e avaliação de continuidade/nova tentativa.
5. **D-M5 — fechamento/revisão:** reconciliar, verificar D01–D22/AC01–AC18, relatório/custos/runbook/rollback e documentação; somente então declarar 07 elegível para detalhamento, sem implementá-la.

Comandos de referência da baseline inicial; execuções efetivas na seção14/guia:

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked --group dev --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
uv run --locked --offline pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
WHEEL_SMOKE_STAGE=06c uv run --locked --offline python tests/wheel_smoke.py
```

Após implementação, mesmos comandos de qualidade/testes e `uv build --offline --out-dir dist/06d-final`; acrescentar estágio smoke06d/env `.venv-wheel-06d` com cópias sintéticas próprias, preservando 06A–06C. Não mudar pins ou refazer wheels de bibliotecas intactas. Se analytics mudar, construir novo artefato antes de declará-lo no bot e testar standalone/consumidor. Metadata de distribuição por versão, fonte local/lock com hash exato; sem editable/PYTHONPATH/checkout irmão no smoke. Reutilização de distribuições externas só após lock/versão/RECORD/hash conferidos; registrar limitação real do cache, sem downloads silenciosos ou alegação de cache frio.

Os comandos continuous-* e notify-drain da seção4 foram implementados offline; invocações completas e resultados constam no guia. Não fornecer um comando de início com destinatário fictício ou horário passado como se já fosse executável. O manifesto gravará T0/Tend reais, computados pela regra da seção10, antes de começar. Não iniciar daemon durante build/teste.

### 11.2 Evidência, recursos e recuperação

Criar `docs/testes/sprint-06d-validacao.md` na implementação, inicialmente pendente, e `sprint-06d-evidencias.json` com D01–D22, comandos reais/versões/revisões/hashes, cenário/horário/esperado/obtido/falhas/limitações. Logs/archives sintéticos em reports/sprint06d e evidências operacionais separadas por pilot_id/data. Esta revisão define os caminhos sem criar guias vazios. Atualizar guia agregador 06 e matriz modular, sem atribuir fakes ao piloto real.

Criar documentação de modelo/ciclo/outbox e runbook no bot; atualizar README/arquitetura/ADRs, bancos novos/catálogo e SMA/catálogo/matriz afetados. Modelos/DDL/dicionários/índices/constraints/triggers/migrações reais na mesma entrega; ausência bloqueia aceite. Relatório legível deriva das evidências/snapshots, com números conferidos e revisão visual. Não reabrir backtest econômico para produzir gráfico.

Orçamento inicial a medir: processo financeiro e worker cada um RSS≤512MiB como alvo operacional, ciclo≤90s, fills/polls≤5s de cadência nominal, reports fora do caminho de admissão. Reservar5GiB de disco livre antes do piloto; alertar abaixo de2GiB e pausar novas entradas abaixo de1GiB, conservando espaço para cancelamento/controle/checkpoint. Mensurar crescimento/hora de bruto/journal/exports e ajustar orçamento **antes de T0**, nunca apagar história no meio para cumprir meta. Limites DuckDB256MB/1thread mantidos; RSS não é o mesmo limite. Custo AWS zero; consumo local/energia/disco/rede e serviços de e-mail/WhatsApp próprios, sem presumir custo externo zero ou iniciar serviços alheios.

Reter toda a janela, tentativas abortadas, journals/observações/relatórios/leases até revisão e backup verificado; nenhuma limpeza automática destrutiva na primeira entrega. Sanitizar contatos/conteúdo/URLs privadas dos logs compartilhados e excluir config privada do Git; hashes e referências permitem auditoria. Criar backup consistente/manifesto e ensaiar restauração em diretório sintético, nunca sobre carteira original.

Falha: bloquear novas entradas, cancelar restante local de modo idempotente, preservar inventário/risco/UNKNOWN e reconciliar. Rollback de código não desfaz fills simulados ou entrega de mensagem; nova carteira incompatível não é reaberta pelo modelo antigo. Retornar à release anterior para comandos anteriores preserva dados continuous para inspeção, sem converter/resetar store. Recuperação do piloto exige versão/configuração compatíveis ou plano explícito testado. A reconstrução externa registrada na 06C limita rollback exato06A: selecionar artefatos por hash real; não substituir novamente arquivos antigos.

## 12. Prompt autossuficiente para implementação futura

Solicitação posterior de implementação deve executar o contrato abaixo. **Executado posteriormente no recorte offline; registro na seção14.** Código/validação offline e observação externa são marcos separados; não fingir completar sete dias numa sessão de desenvolvimento.

```text
Implemente somente a Sprint06D em /home/cams7/Dev/Cripto, no projeto existente
/home/cams7/Dev/Cripto/cripto-bot/src/cripto_bot. Bibliotecas existentes:
/home/cams7/Dev/Cripto/cripto-core, cripto-market-data e cripto-analytics;
docs centrais em /home/cams7/Dev/Cripto/docs. Não crie projetos/Git novos,
remotos/publicação/commits ou altere referências de LotoBot.

Leia/verifique nesta ordem:
1. docs/planejamento.md (3,4.5–4.10,5,6.5,8–10,13).
2. docs/sprints/sprint-06.md e sprint-06d.md integralmente.
3. Sprint06C/guia/evidências/reconstrucao-externa; 06A/06B e guias para
contratos, artefatos, cache e identidade; Sprint05/ajuste analítico/ADRs0005–0010.
4. Arquitetura central/modular, SMA/catálogos/matriz modular e bancos;
fontes/testes/manifests/locks/pins/READMEs dos quatro projetos existentes.
5. Contratos das fontes mail-sender/whatsapp-notify locais somente leitura;
não consultar segredos ou copiar destinatários/endpoints/credenciais alheios.

No detalhamento, 214 hashes e16 artefatos atuais da06C conferiam, C01–C18
aprovados; bot d695e0e383f3316e74c88aaa56ed7b7586d93bb2,
core e666e7e23dcb421177c80838a28c230d4433bdf2,
dados 1da6f4fe25c6940cc3e96416415ddf6f1ffcb4e9,
analytics 236775dd6ee84375d8dbd11e4c3fc2b11747019a,
docs d62a4c3a84dd00edfef404f297c7febac2a6b658, limpos no início.
Reinspecione, preserve trabalho/artefatos/dados e evidências anteriores.
Rebuild externo06A já esclarecido não é artefato histórico original; use
hash atual verificado e registre qualquer nova mudança, sem substituição muda.

Execute D-M1→D-M2→D-M3 das seções11/4–9: guia pendente antes de testes,
baseline offline preservada, novo paper-continuous-v1/store isolado, reducer
parcial/ordens/reservas/cancelamento/UNKNOWN, clock/scheduler/controles,
adapter de mercado existente, outbox durável/workers/clientes locais,
relatórios por snapshot. Reuse Decimal80/SMA/sizing/preço/filtros/risco;
carteira/estado/reconciliação continuam no bot. Nenhuma alteração silenciosa
de modelos/DDL antigos ou duplicação de regras em analytics/DuckDB.

Implemente comandos/config/flags previstos na seção4, defaults desabilitados,
NOOP sem módulos/store/cliente, custódia se existir posição, escopo continuous
separado de fixture/backtest, exclusive_owner e rejeição de capacidades ausentes.
Risco/clock/freshness/kill não são opcionais. Preservar comandos antigos.

Implemente quatro GETs públicos existentes, guards/budgets/backoff/not_before,
50 warmup e slots UTC/monotonic/deadline; não operar candle aberto ou sinal
vencido. Sem quote válida/filtro suportado/saldo/capacidade, bloquear efeitos;
não relaxar filtros ou ampliar rotas para conseguir iniciar o piloto.
Implementação/testes usam fixtures/MockTransport e sockets bloqueados.

Pedidos/fills por eventos/IDs idempotentes, cumulativos≤solicitado, fees por
fill, reservas/custo/inventário próprios, terminal/cancel liberando só restante.
Teste oráculo da seção6, sem fill garantido por toque, caps, TTL60s/polls5s,
quote≤5s e UNKNOWN/restart/corridas/crash/duplicação/risco. Controle persistente
pause/kill/disable/reload preserva posições/owner/risco, sem liquidação automática.

Store financeiro novo: journal/postings/ordens/fills/ciclos/config/controle e
notification_events atômicos; FK/WAL/FULL/flock/CAS e projeções reconstruíveis.
Worker lê eventos readonly e mantém fila/tentativas/lease em banco de entrega
separado, sem mutar finanças/segurar writer financeiro. HTTP fora de transação;
sem promessa exactly-once ou retry de negociação por falha de canal.

Clientes locais: e-mail mail-sender POST/api/v1/mail/send; WhatsApp status e
send via whatsapp-notify, nunca browser/QR/session-start-stop. Strict payload,
confirmação semântica, deadlines/limites/retries/UNKNOWN/fallback conforme9.
Somente INTEGRATION_MODE=LOCAL, sem boto3/Lambda/AWS. Testes sem envio real.

Rode qualidade/testes/build/smokes da seção11; novos artefatos/env/stage06d,
quatro wheels instalados -I/cwd neutro/sem checkout/editable/PYTHONPATH.
Preserve pins Python3.13.15/uv0.12.19/setuptools84.2.0 e bibliotecas intactas.
Se mudar analytics para renderer, versionar/construir antes de integrar e
revalidar standalone/consumidor/identidade. Sem upgrades laterais. Limitação
de cache registrada; reutilização só após lock/versão/RECORD/hash conferidos.

D-M4/D-M5 não estão executados por uma suíte acelerada. Antes de acessar rede
pública ou enviar mensagens, exigir instrução explícita do responsável para
aquela fase, endpoints/destinatários de teste e autorização de serviços.
Flags --allow-network/--allow-send são guards técnicos, não autorização por
si sós. Se faltarem, conclua todo trabalho offline e registre SOFTWARE_VALIDATED/
PILOT_PENDING com preparo concreto e condições faltantes, sem aprovação global.
Não acessar conta/chaves Binance, private/order/test ou executar ordens reais.

Após autorização/configuração e preflight elegível, congele protocolo/T0/Tend
pela regra da seção10 antes de observar: sete dias UTC completos/672slots,
≥666 válidos no prazo, sem excluir downtime/kill/stale. Não comprimir espera,
executar sinais atrasados, forçar trades ou reiniciar para escolher PnL.
Diários/consolidado e drills separados, carteira/reserva/fills/outbox conciliados.
Se recurso/período ausente, marque NÃO EXECUTADO/PENDENTE, nunca aprovado.

Meça latência/RSS/disco/bruto/rede/serviços e orçamento; backup/restauração/
rollback em diretórios sintéticos sem reset/cópia destrutiva. Preserve registro
final histórico, modelos/artefatos e identidade selada; sem novo backtest real,
novos ativos/estratégias, ranking/walk-forward/BT ou AWS/07/modos privados.

Atualize README/API/runbook, arquitetura/ADRs, documentos técnicos reais de
continuous/outbox/bancos e catálogos/SMA/matriz afetados. Guia/evidências06D
com comandos/versões/hashes/revisões/intervalos/esperado/obtido/falhas/custos/
limitações verdadeiros. Relatório legível derivado, valores conferidos e
revisão visual. Documentação pendente bloqueia aceite.

Só concluir06D quando D01–D22/AC01–AC18 aplicáveis e sete dias/canais realmente
observados aprovados/revistos. Atualize agregador/planejamento com estado real;
07 fica somente elegível para detalhamento/revisão, sem implementá-la ou
promover modo automaticamente. Sem commits/remotos/publicação implícitos.
```

## 13. Fontes e registro do detalhamento

Fontes primárias consultadas em 26/10/2026: [Binance/host somente dados públicos](https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md), [REST/market data](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md), [HTTPX/timeouts](https://www.python-httpx.org/advanced/timeouts/) e [Python3.13/sqlite3](https://docs.python.org/3.13/library/sqlite3.html). Fundamentam capacidades dos adapters; políticas de simulação/participação, calendário, fill/risco e autorização são decisões deste projeto, não garantias da corretora. Reconfirmar APIs efetivamente alteradas antes da implementação, sem atualizar pins por acompanhar documentação mais recente.

Fontes locais consultadas somente leitura: clients mail_sender/whatsapp_notify do loto-bot e rotas/schemas dos respectivos serviços em `/home/cams7/Dev/LotoBot`; nenhum projeto externo alterado ou chamado, nenhum destinatário/configuração privada copiado.

Registro do detalhamento inicial (anterior à implementação): inspeção das dependências/documentação/fontes/testes/manifestos/locks, conferência de214 hashes/16 arquivos, revisões/estado Git e especificação desta etapa. Não houve instalação/build/suíte, abertura de banco, coleta/relatório econômico, mensagens/piloto ou alteração de fontes dos projetos. Próxima ação: revisar esta especificação antes de solicitar implementação; autorizações e observação externa permanecem separadas.

## 14. Execução do prompt12 — 26/10/2026

D-M1→D-M2→D-M3 implementados/validados offline, estado SOFTWARE_VALIDATED/PILOT_PENDING. Baseline542 testes; suíte completa642; revisão final108 testes sobrepostos após ajustes de preparo/pausa/entrega/snapshot; analytics30; qualidade/build/31 comandos por quatro wheels e compatibilidade48 curvas/6 arquivos exatos/Parquet.16 artefatos anteriores, modelos/DDL e registro final preservados. Nenhum commit ou alteração da staged area preexistente.

Software real: domínio continuous, stores schema1 isolados, reservas/fills parciais, clock/scheduler/controles/inbox, outbox/fila/leases/clientes locais e renderer analytics0.1.1. Documentos técnicos criados durante a implementação: [módulo](../modulos/paper-continuous.md), [API](../api/continuous.md), [bancos](../bancos/README.md), [ADR0011](../decisoes/0011-paper-continuous-e-entrega-local.md), [runbook](../operacao/continuous-runbook.md). [Guia](../testes/sprint-06d-validacao.md), [evidências](../testes/sprint-06d-evidencias.json) e [relatório](../testes/relatorios/sprint-06d/report.html) registram casos/falhas/limites/revisões/hashes/revisão visual.

Esclarecimento causal do warmup: preflight antes deT0 valida50 candles correntes já fechados e congela calendário futuro; antes do primeiro score reconfirma51 candles causais deT0. Não exigir, ≥15min antes deT0, um candle que ainda não fechou. Mantém range do warmup final e proíbe informação futura. Inbox usa fsync/link exclusivo em vez de rename com substituição: publicação atômica, sem sobrescrever request-id existente. Custódia válida com dados íntegros pode contar como processada; todos os slots continuam no denominador.

D-M4/D-M5 NÃO EXECUTADOS. Faltam instrução explícita para rede pública/serviços/destinatários de teste, preflight elegível/supervisão/recursos e sete dias reais completos. Pré-protocolo [não armado](../testes/sprint-06d-pre-protocolo.json) mantém T0/Tend nulos. Zero horas/requests/recibos reais; fixtures e FakeSender não suprem D14/D16/D17/partes operacionais nem aceite global.07/BT não implementados/liberados; nenhuma operação privada, coleta econômica nova, otimização, AWS ou promoção automática.
