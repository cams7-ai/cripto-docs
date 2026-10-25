# ADR 0004 — Carteira PAPER e ledger por ativo

Data: 24/10/2026. Estado: adotada e validada offline na Sprint 03.

## Contexto

A aplicação já coleta e valida dados públicos/sintéticos, mas a simulação financeira precisa de reservas, custos, idempotência e recuperação. O store de mercado v1 rejeita tabelas adicionais; acrescentar dados financeiros nele quebraria um contrato aprovado. A Sprint 03 não introduz estratégia, ordens externas ou operação contínua.

## Decisão

Estender o repositório `cripto-bot`, mantendo subpacotes de domínio/aplicação/adapters. `paper-run`, `paper-report` e `paper-reconcile` são comandos separados. `run-once` continua NOOP e os comandos financeiros não constroem clientes HTTP, inclusive com configuração `market` presente.

Usar `paper.sqlite3` independente, schema v1, para uma carteira vinculada a parâmetros, modelo `paper-integral-v1`, regras e hash de cenário imutáveis. O roteiro tem observações inline sintéticas, eventos DAY_START/MARK/ORDER e relógio de replay; nenhuma cotação atual é buscada para recuperar um plano.

Os valores financeiros usam strings e Decimal com contexto local de precisão 80. Quantum contábil BTC/USDT de oito casas; preço ajustado adversamente ao tick; quantidade arredondada para baixo no passo comum dos filtros aplicáveis. Notional/taxa de compra são arredondados para cima; receita bruta de venda e custo proporcional baixado, para baixo. A última baixa absorve todo o custo remanescente. Operações que arredondem para preço/notional/receita líquida não positivos são rejeitadas.

Cada evento gera postings cuja soma é zero separadamente em BTC e USDT. A carteira livre/reservada não pode ficar negativa; contas técnicas de capital, mercado e taxas fornecem as contrapartidas. Postings guardam carteira, instante UTC do replay, referência de evento/intenção/fill, ativo, conta e quantidade original.

O journal é a fonte de verdade. O mesmo redutor puro reconstrói saldos, posição, custo, taxas, marcação, baseline, pico, travas e intenções. Projeção, postings, planos e fills armazenados são comparados ao resultado reconstruído; divergência não é corrigida por diferença. Triggers impedem UPDATE/DELETE comuns em journal/postings/fills. Hashes encadeados e constraints complementam a validação local.

Transação A confirma decisão/plano/reserva/ledger; transação B confirma fill, consumo/liberação, posição, risco e estado juntos. Cada append verifica a reconstrução e o token/estado da carteira dentro de uma transação imediata. Flock exclusivo impede escritores cooperantes simultâneos. Identidades de cenário/ação e fill independem do run_id; repetição devolve o resultado anterior.

Uma pendência RESERVED só é retomada após reconciliação, usando o plano persistido e relógio sintético original. Cancelamento/rejeição local libera a reserva e impede fill posterior; essa transição é exercitada pelas APIs internas/testes, sem comando administrativo novo. Não existem estados de envio remoto.

Baseline diário nasce uma vez em DAY_START à meia-noite UTC. Perda diária/drawdown consideram custos e marcação, com travas persistentes. A trava de drawdown não se desfaz por recuperação de preço ou mudança de dia. SELL de redução continua possível com dados/saldo íntegros; não há liquidação automática.

`paper-report` abre snapshot SQLite somente para leitura. Pode exibir reconstrução confiável do journal marcada como divergente da projeção; sem histórico válido, retorna indisponibilidade, sem inventar saldo zero. `paper-reconcile` e `paper-run` persistem bloqueio em divergência quando o banco permite; não há reset/desbloqueio automático.

## Consequências e limites

Journal e projeções duplicam informação deliberadamente para detectar divergências. A reconstrução antes dos commits prioriza verificabilidade, sem benchmark de alto volume. O limite de cenário é 1000 eventos; o incremento demonstrado é pequeno e local.

O modelo é integral, determinístico e tem taxas somente em USDT. REFERENCE inclui metade do spread por lado e slippage; BID_ASK inclui apenas slippage adicional. A reserva exata deriva de preço conhecido no modelo e não comprova reserva suficiente ou execução em corretora real.

Relatórios são derivados e publicados por rename de diretório temporário no mesmo filesystem. Falha de exportação preserva os fills já confirmados; replay recompõe a saída. Não existe transação distribuída entre banco e relatório. Perda de energia/dispositivo, filesystem remoto e recuperação de produção não foram ensaiados.

Nenhuma nova dependência foi necessária; manifest/lock da Sprint 02 foram preservados. Carteiras novas para cenários/configurações diferentes devem usar diretório próprio; não reutilizar uma carteira alterando seu contexto para apagar perdas.

## Evidências e fontes

Ver [guia da Sprint 03](../testes/sprint-03-validacao.md), [evidências](../testes/sprint-03-evidencias.json) e [especificação](../sprints/sprint-03.md).

Fontes oficiais reconfirmadas em 24/10/2026: [Decimal](https://docs.python.org/3.13/library/decimal.html), [sqlite3](https://docs.python.org/3.13/library/sqlite3.html) e [filtros Spot](https://github.com/binance/binance-spot-api-docs/blob/master/filters.md). Taxas, capital, preços e limites usados na demonstração são decisões sintéticas de teste.
