# ADR 0011 — PAPER contínuo e entrega local independente

Data: 26/10/2026. Decisão implementada no recorte offline da 06D; aceite operacional pendente. Complementa ADRs 0005–0010.

`cripto-bot` continua proprietário de carteira, decisões, risco e reconciliação. `paper-continuous-v1` usa `continuous.sqlite3`, schema 1, separado de `paper-integral-v1`, `paper-modular-v1` e backtest. Reutiliza Decimal80, SMA20/50, sizing, precificação, filtros e limites do core. Uma instância BTCUSDT/15m, Spot, `exclusive_owner`, executor `paper_bounded`; habilitação em `[continuous]` e no módulo, ambas desabilitadas por padrão.

Ordens têm quantidade solicitada/cumulativa, reservas, custo, taxas por fill, IDs e estados terminais. Cada poll considera no máximo 10% da quantidade oposta exibida, limitada ao restante e saldo reservado. Conteúdo de livro já consumido ou ID repetido não cria capacidade. Cap adverso, latência mínima 1s, poll 5s, quote ≤5s e TTL 60s. Isso é uma hipótese conservadora local, sem promessa de fila, execução ou liquidez real. LIMIT é drill de fixture. UNKNOWN preserva reserva; somente cancelamento explícito reconciliado resolve o compromisso. Pause/kill/disable não liquidam inventário.

Journal, partidas balanceadas por ativo, projeções, ordens, fills, configuração, controles e eventos de notificação têm um commit financeiro. WAL/FULL/FK, flock, versão e hash encadeado protegem o writer; replay verifica projeções e eventos. Leitores usam transação readonly consistente. Inbox de controle com fsync/link exclusivo permite solicitar pausa enquanto o daemon detém o writer; ACCEPTED não significa aplicado. O reconhecimento está no journal.

Entrega usa `notifications.sqlite3`, lock e leases próprios. Importa eventos financeiros imutáveis por leitura, confirma tentativa antes de HTTP, transmite fora de transação e registra resultado depois. Crash após envio deixa UNKNOWN, com possibilidade explícita de duplicação; não se promete exactly-once. Rate global 1 tentativa/s, lease 60s, até três por canal, espera 60/300s e fallback WhatsApp→mail. Serviços loopback e contratos estritos; somente LOCAL, sem AWS ou sessão/QR/browser. Processo filho isolado com timeout total de 10s complementa timeouts de connect/pool 1s e read/write 3s, que isoladamente não limitam a duração total.

Calendário: T0 é a próxima meia-noite UTC com ≥15min; Tend=T0+7 dias; 672 slots, ≥666 válidos dentro de C+2s…C+90s. Falhas/indisponibilidade/kill/atrasos não saem do denominador; não executar sinais vencidos. Clock wall e monotonic, server-time a cada 5min, RTT/offset ≤1s, metadados ≤1h. Não relaxar filtros Binance para iniciar piloto.

**Esclarecimento causal do warmup:** o preflight antes de T0 valida 50 candles já fechados e congela a janela futura. No primeiro slot, buscar novamente 51 candles consecutivos até o score fechado em T0. Os 50 anteriores ao score são [T0−51×STEP,T0−STEP). Não exigir que o candle que fecha em T0−STEP já esteja disponível ≥15min antes de T0; nunca consultar informação futura. A confirmação final acontece antes de qualquer sinal/compromisso.

Analytics 0.1.1 acrescenta somente renderer de snapshot; publicação genérica já existente. Nenhuma nova tabela DuckDB ou cálculo financeiro foi introduzido. Relatório distingue marca atual indisponível/última marca, fixture/observação prospectiva e software/piloto. `pilot_approved` nunca é atribuído automaticamente.

Alternativas recusadas: adaptar silenciosamente o modelo integral; HTTP sob lock financeiro; otimizar parâmetros no piloto; usar suíte acelerada como sete dias; liberar modo real a partir do relatório. Não é necessária nova dependência de runtime além da versão do renderer. Cache frio integral permanece não demonstrado.

Fontes oficiais reconferidas em 26/10/2026: [HTTPX/timeouts](https://www.python-httpx.org/advanced/timeouts/) (read timeout limita espera por chunk; daí o deadline externo) e [Python3.13/sqlite3](https://docs.python.org/3.13/library/sqlite3.html) (transações explícitas, URI readonly e backup). Regras de liquidez/calendário são decisões deste projeto, sem garantia da corretora.
