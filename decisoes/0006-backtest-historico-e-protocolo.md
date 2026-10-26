# ADR 0006 — Backtest com protocolo congelado e estado limitado

Data: 25/10/2026. Implementação da Sprint 05; aceite conforme [guia 05](../testes/sprint-05-validacao.md).

A fixture modular da 04 retém histórico no estado e usa execução imediata com validade de cinco segundos. Simular meses elevando esse limite confundiria relógio de decisão com referência futura e teria custo crescente por candle.

Criar `domain/backtest` e store schema1/modelo paper-backtest-v1 independentes, com janela limitada, prefixo incremental, um slot agendado e arquivo SQL de terminais. Reutilizar a SMA pura, redução de carteira/risco, filtros, preço adverso e step comuns. Não converter bancos anteriores. `.active` continua selecionando fixture; `active_for("backtest")` exige capacidade e escopo históricos explícitos.

Preparar fontes em streaming antes da carteira e congelar dataset/código/configuração/modelos/split/custos/benchmarks/métricas antes de PnL. Cada segmento/variante/perfil tem capital próprio. Development e validation completos precedem test. Um registro local comum impede reutilizar janelas finais reais sobrepostas em outro protocolo; não prova desconhecimento humano prévio.

Decisão usa fechamento disponível na fronteira; open posterior é observado +1 ms e fill ocorre +2 ms. Atraso adicional de um candle pertence ao protocolo, sem ampliar freshness de cinco segundos. SCHEDULED não reserva; admissão A confirma plano/reserva e B confirma fill em transações diferentes. Decisão e checkpoint são atômicos. HOLDs e marcadores sem novo agendamento/reserva podem compartilhar até 64 eventos no mesmo commit, sempre com journal/projeção/cursor juntos. SCHEDULED força confirmação antes de A; não há rede/HTML dentro de transação. Terminal mark_to_market não inventa saída.

Pragmas FULL/WAL, lock local, CAS e reconstrução streaming inicial/final protegem o journal e as projeções. A assinatura entre commits é otimização do escritor conhecido; não substitui reconciliação. HTML e CSV são derivados do snapshot confirmado, com gráfico limitado e métricas integrais. Falha de exportação permite nova publicação sem reabrir avaliação.

Consequências: mais disco para auditoria, replay linear ao entrar/sair e hipóteses explícitas de execução integral/sem liquidez/filtros proxy. Não implementa continuous, fill parcial, serviço remoto, novas estratégias ou autorização LIVE. Ver [DDL e operação](../bancos/backtest-sqlite.md) e [SMA](../estrategias/trend_sma.md).
