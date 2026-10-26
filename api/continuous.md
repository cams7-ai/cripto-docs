# API e comandos do PAPER contínuo

Estado da entrega: software validado offline (SOFTWARE_VALIDATED/PILOT_PENDING); marcos externos permanecem pendentes. Fonte: entrypoints/continuous.py, adapters/continuous_config.py, application/continuous_* e notifications.py no bot. Detalhamento do [módulo e ciclo](../modulos/paper-continuous.md). Contratos e persistência: [ADR0011](../decisoes/0011-paper-continuous-e-entrega-local.md), [bancos](../bancos/README.md).

| Comando (todos com --config FILE) | Resultado / efeitos |
|---|---|
| continuous-prepare | PREPARED com identidade; zero capital até ARM. Desabilitado/sem banco: CONTINUOUS_NOOP, sem cliente/diretório |
| continuous-run [--once] [--allow-network] | Um passo ou daemon; público exige opt-in e wheels. Fixture rejeita opt-in de rede. Não inicia serviço de notificações |
| continuous-reconcile | Snapshot readonly, replay completo, versão/pending_order; sem reparo |
| continuous-report [--day YYYY-MM-DD] | JSON/HTML/manifest por analytics0.1.1; diário UTC dentro da janela ou consolidado; não completa observação |
| continuous-control --action ACTION --reason TEXT [--order-id ID] [--request-id ID] | ACCEPTED/PENDING em inbox; ACTION pause/resume/kill/disable/reload/cancel. cancel exige ID; reason 1…256 sem controles; ack em journal |
| notify-drain [--once] [--allow-send] | Fila independente; desabilitado: NOTIFICATIONS_DISABLED. Habilitado sem opt-in: erro antes da fila/HTTP |

Saída JSON/log sanitizado com run_id, mode=PAPER e orders_sent=0. Exit0: sucesso/NOOP/pausa; 2: configuração/argumentos/opt-in; 3: bloqueio, dados, busy ou corrupção; 1: falha interna. Nenhum exit0 aprova piloto. Uso de dados reais e entrega exige autorização humana separada; flags são guards técnicos.

Configuração estrita: mode=PAPER; [continuous] não coexiste com paper/strategy/backtest. `environment=local`, `evaluation_type=continuous`, symbol BTCUSDT e interval15m. source explícito fixture/binance_public; fixture requer caminho interno, schema1/exchange_info/frames com at/server_time/klines/book_ticker e relógio correspondente. Fixture não recebe timestamps novos para aparentar frescor. Três diretórios internos distintos, sem ancestralidade ou banco histórico protegido. Defaults e caps estão no exemplo do bot.

Estratégia: única trend_sma20/50, environments local, modes PAPER, evaluation_types continuous, execution paper_bounded, on_disable hold_and_monitor, capital_weight≤0.10. Alterar flag não altera ownership; inexistência de ativos elegíveis, saldo, preço ou filtro suportado bloqueia efeitos. Resume/reload exige flags ativas explícitas, contexto congelado e nenhuma ordem UNKNOWN/trava de risco.

Notifications: enabled=false, integration_mode=LOCAL e whatsapp_enabled=false por padrão. Quando habilitado, mail_sender_url/mail_to obrigatórios; WhatsApp habilitado também exige whatsapp_notify_url/whatsapp_contact. Tipos mail TEXT/HTML. Env mapeado: INTEGRATION_MODE, MAIL_SENDER_URL, MAIL_TO, MAIL_CONTENT_TYPE, WHATSAPP_ENABLED (true/false), WHATSAPP_NOTIFY_URL, WHATSAPP_CONTACT, WHATSAPP_TIMEOUT_SECONDS(1…3). Não copiar destinatários de outro projeto. URLs http/https somente localhost/127.0.0.1/::1, porta explícita, sem credenciais/query/fragment/path adicional.

| Serviço | Contrato aceito |
|---|---|
| mail-sender | POST /api/v1/mail/send; JSON to,subject,body,message_type; HTTP200 e message exatamente E-mail enviado com sucesso. |
| whatsapp-notify | GET /whatsapp/session/status com HTTP200/status SESSAO_ABERTA; depois POST /whatsapp/messages/send contact,message, HTTP200/status enviado |

Não iniciar/parar sessão, browser, QR, autenticação ou endpoints alternativos. Timeout após POST/resultado sem confirmação semântica é UNKNOWN; falha antes de POST é FAILED; HTTP4xx falha conhecida. Resultados e fallback em banco separado. Sem retries de ordens por falha de entrega. Limite total por tentativa10s com isolamento de processo, resposta16KiB, payload64KiB, rate1/s, lease60s e até3 por canal.

Pontos de extensão internos: Clock/Feed injetáveis; Frame normalizado; reducer puro reduce(state,kind,payload); ContinuousStore.append/reconcile/backup; Sender.send. Esses pontos não permitem desativar risco/clock/freshness em configurações operacionais. Testes usam clocks sintéticos/MockTransport e bloqueio global de sockets.
