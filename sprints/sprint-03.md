# Sprint 03 — Carteira PAPER, reservas e execução simulada

Data da especificação: 24/10/2026.

**Estado: implementada e aprovada na validação local offline em 24/10/2026.** AC01–AC18 verificados conforme o [guia 03](../testes/sprint-03-validacao.md) e as [evidências](../testes/sprint-03-evidencias.json). As seções de especificação preservam o contrato executado; a seção 13 registra a entrega. Nenhuma ordem externa ou coleta real foi executada.

Referências: [planejamento](../planejamento.md), [arquitetura](../arquitetura.md), [Sprint 02](sprint-02.md), [guia de validação 02](../testes/sprint-02-validacao.md), [evidências 02](../testes/sprint-02-evidencias.json) e [ADR 0003](../decisoes/0003-coleta-publica-e-persistencia-local.md).

## 1. Objetivo e incremento demonstrável

Implementar uma carteira local exclusivamente `PAPER`, com saldos livres/reservados, posição BTC, taxas, livro-razão por ativo e execução simulada determinística. Antes de cada compromisso, validar dados, saldo, regras sintéticas do símbolo e limites de risco. Após reinício, reconciliar o estado e retomar uma intenção pendente sem duplicar efeito.

A demonstração executará uma compra e uma venda roteirizadas com observações sintéticas, produzirá relatório auditável e repetirá o roteiro sem alterar novamente saldos, taxas ou fills. A Sprint não gera sinais nem constitui backtest de uma estratégia. As decisões de compra/venda vêm de um arquivo de cenário conhecido.

## 2. Diretórios e pré-requisitos comprovados

- Workspace: `/home/cams7/Dev/Cripto`.
- Aplicação e diretório de comandos: `/home/cams7/Dev/Cripto/cripto-bot`.
- Documentação central: `/home/cams7/Dev/Cripto/docs`, com Git independente.
- Pacote: `modules/trading/src/cripto_bot`, relativo ao repositório da aplicação.

Esta Sprint estende o módulo existente. Subpacotes de carteira, risco e execução não recebem repositório próprio. Cada novo módulo **independente** futuro terá diretório diretamente no workspace e Git próprio, conforme a seção 5 do planejamento.

| Dependência | Revisão nesta especificação | Condição de implementação |
|---|---|---|
| D01 — Sprint 02 aprovada | Guia registra AC01–AC17 aprovados offline, 204 testes, qualidade e wheel | Preservar a regressão e revalidar mudanças pertinentes |
| D02 — Integridade | Os 24 hashes de fontes, manifest, lock e pin Python conferem com as evidências 02 | Analisar qualquer divergência nova antes de trabalho dependente |
| D03 — Revisões observadas | Aplicação `a102223`; documentação `552b3f2`; ambos sem alterações locais no início da inspeção | Registrar revisões efetivas e preservar trabalho posterior |
| D04 — Ferramentas | Python 3.13.15, uv 0.12.19 e dependências definidos nos artefatos existentes | Confirmar ferramentas/permissões na implementação |
| D05 — Persistência de mercado | `market.sqlite3` usa schema v1 e rejeita tabelas adicionais | Criar store de carteira separado, sem alterar esse schema |
| D06 — Dados externos | Coleta pública real não executada na Sprint 02 | Não é bloqueante: esta Sprint usa somente cenário sintético offline |

As evidências anteriores foram revisadas e os hashes comparados; a suíte não foi executada novamente nesta entrega documental. Não há bloqueio conhecido para o detalhamento. Se um pré-requisito falhar durante a implementação, registrar PENDENTE em `docs/testes/sprint-03-validacao.md`, sem iniciar trabalho dependente.

## 3. Escopo e exclusões

Incluído: carteira BTC/USDT, saldo inicial fictício, reserva prévia ao fill, custo médio e resultado líquido, ledger balanceado por ativo, risco de admissão, executor local de fill integral, reconciliação, persistência transacional e relatório. Cenários/testes cobrem também rejeição e liberação de reserva sem fill.

Excluído: estratégia SMA, sinais automáticos, indicadores, otimização, backtest, coleta durante execução da carteira, uso de cotação pública atual, agendamento, API web, AWS, infraestrutura, notificações, TESTNET/LIVE, credenciais e qualquer ordem externa. Não instalar SDK de trading.

O simulador inicial admite somente ordens sintéticas a mercado com fill integral. Fills parciais, execução probabilística, limites de participação no volume e operação contínua ficam nas etapas previstas do roadmap. Não implementar ordem limitada nem inferir fill porque máxima/mínima de candle tocou um preço.

Taxas somente em USDT nesta etapa. Não converter automaticamente taxa em BTC/BNB ou assumir desconto. Sem margem, empréstimo, short, alavancagem, aportes/retiradas após a inicialização, pirâmide ou múltiplos pares.

## 4. Configuração e interface de execução

### 4.1 Compatibilidade e isolamento

Preservar `check-config`, `run-once` e `collect-market`, inclusive formatos, códigos existentes e opt-in de rede da coleta. `run-once` continua NOOP; não passa a negociar ou coletar implicitamente. O novo fluxo financeiro nunca instancia `PublicSource`, cliente HTTP ou executor privado, mesmo se o arquivo contiver configuração de mercado.

Adicionar tabela opcional `paper` ao TOML. Configurações anteriores continuam válidas; campos novos são permitidos somente dentro da tabela prevista. Permanecem defaults PAPER, rejeição de campos desconhecidos, credenciais, variáveis desconhecidas `CRIPTO_BOT_*` e modos proibidos. O único override de ambiente continua sendo `CRIPTO_BOT_MODE`, validado sem ocultar erro do arquivo.

Exemplo futuro `config/paper.execution.example.toml`:

```toml
mode = "PAPER"

[paper]
wallet_id = "paper-demo"
data_dir = "data/paper-demo"
scenario_file = "config/fixtures/paper-roundtrip.json"
initial_usdt = "10000.00"
fee_bps = "10"
spread_bps = "10"
slippage_bps = "5"
max_entry_fraction = "0.10"
max_exposure_fraction = "0.10"
max_daily_loss_fraction = "0.01"
max_drawdown_fraction = "0.05"
max_quote_age_ms = 5000
```

Valores financeiros são strings decimais, jamais TOML float. IDs devem ter 1–64 caracteres alfanuméricos, hífen ou underscore, sem caminhos. Validar `initial_usdt > 0`, bps entre 0 e 100 e frações maiores que zero e menores ou iguais a 1. `max_quote_age_ms` é inteiro de 1 a 5000; bool não é inteiro válido. Todos os campos do exemplo devem ser aceitos; defaults, se usados, são os valores exibidos.

`data_dir` e `scenario_file` são obrigatórios para executar o roteiro. Resolver caminhos pelo cwd, como na Sprint 02, inclusive quando `--config` for absoluto. Confirmar contenção no módulo após resolver symlinks; rejeitar escape antes de efeitos. O banco, o arquivo de lock e destinos de relatório não podem ser symlinks para fora do módulo.

### 4.2 Comandos novos

| Comando | Comportamento |
|---|---|
| `cripto-bot paper-run --config CAMINHO` | Inicializa uma única vez, reconcilia, recupera pendências e executa o roteiro restante |
| `cripto-bot paper-report --config CAMINHO` | Lê carteira existente e retorna saldos, posição, custos, risco e reconciliação; não cria carteira |
| `cripto-bot paper-reconcile --config CAMINHO` | Confere invariantes e reconstrução; persiste bloqueio se detectar divergência, sem corrigir valores silenciosamente |

Nenhum aceita `--allow-network`, host, chave, modo alternativo ou opção de reset. Sem tabela `paper`, falham antes de abrir banco. `check-config` valida estrutura/caminhos sem inicializar carteira ou ler o roteiro; o executor valida seu conteúdo antes de gravar estado financeiro.

Sucesso: código 0, um JSON em stdout e eventos JSON Lines em stderr com run_id, timestamp UTC, `mode=PAPER`, `orders_sent=0` e contadores específicos `simulated_fills`, `rejected_intents`, `replayed_actions`. Separar contadores da execução atual dos totais da carteira: repetir o roteiro gera zero fills novos, mesmo que o total histórico continue sendo dois. Uma rejeição de negócio esperada pode completar o roteiro com código 0, mas precisa constar como rejeição com motivo e zero fill, nunca como negociação bem-sucedida.

Configuração/roteiro estruturalmente inválidos: código 2. Banco indisponível, conflito de identidade, divergência, lock ocupado ou execução interrompida: código 3, com progresso confirmado e diagnóstico sanitizado. Falha interna inesperada: código 1. `paper-report` pode apresentar carteira bloqueada para diagnóstico; `paper-run` não admite novos efeitos enquanto houver divergência.

## 5. Roteiro, relógio e preços sintéticos

### 5.1 Contrato de entrada

Criar `config/fixtures/paper-roundtrip.json`, com `schema_version`, `scenario_id`, símbolo fixo `BTCUSDT`, regras sintéticas do símbolo e eventos ordenados. Tipos mínimos de evento: `DAY_START`, `MARK` e `ORDER`. Cada evento tem `event_id`, timestamp UTC com precisão de milissegundos e payload validado; eventos ORDER têm `action_id`, lado BUY/SELL, quantidade BTC em string, `decision_at`, observação de preço identificada e `fill_at`.

O cenário limita-se a 1000 eventos e 1 MiB. Rejeitar eventos fora de ordem, timestamps naive, IDs duplicados com payload distinto e referências inexistentes antes da execução. Mesmo timestamp pode ter desempate pela ordem explícita de eventos, registrada no hash do cenário. O hash canônico do payload não inclui run_id ou relógio de parede.

O relógio financeiro é o relógio de replay persistido, não `datetime.now()`. Exigir `decision_at < observed_at <= fill_at`, sem executar antes da observação nem usar cotação futura na admissão. A idade do preço em `fill_at` não pode exceder `max_quote_age_ms`. Não reutilizar um preço vencido ou de outro símbolo para completar o roteiro.

O cenário é uma fonte sintética explícita; suas intenções são manuais e não dependem de uma estratégia. Reutilizar os conversores e validações úteis da Sprint 02, mas não tratar o `bookTicker` atual com `market_timestamp=null` como cotação histórica. A leitura/integração de candles para geração de sinais será tratada na Sprint 04. Não alterar ou reescrever datasets de mercado nesta Sprint.

### 5.2 Modelo de execução

Para observação `REFERENCE`, com preço de referência `p`, aplicar custos aditivos:

```text
b = spread_bps / 20000
s = slippage_bps / 10000
BUY:  preço antes do tick = p × (1 + b + s)
SELL: preço antes do tick = p × (1 - b - s)
```

Para observação `BID_ASK` sintética, usar ask na compra ou bid na venda e aplicar somente slippage adverso; o spread já está embutido. Validar preços positivos, quantidades não negativas e bid <= ask. O executor não atribui liquidez real a uma observação sintética.

Arredondar preço de compra para cima e de venda para baixo no múltiplo do tick. Quantidade é arredondada para baixo ao múltiplo do step, nunca somente pelo número de casas decimais. Se virar zero ou deixar de cumprir um filtro/limite, rejeitar. Não diminuir silenciosamente quantidade para fazê-la caber em saldo ou exposição; a única normalização automática admitida é a do step, registrada com quantidade pedida/normalizada.

O preço final e a taxa são conhecidos pelo modelo local e compõem um plano de fill determinístico, persistido antes de aplicá-lo à carteira. Essa premissa permite uma reserva exata para o simulador; não representa garantia de preço ou reserva suficiente em ordem real.

### 5.3 Precisão e exemplo obrigatório

Usar `Decimal` com `localcontext`, precisão 80 e arredondamentos explícitos, sem alterar contexto global. Limitar entradas financeiras a strings decimais finitas, sem notação exponencial, até 18 dígitos inteiros e oito fracionários; rejeitar resultados fora desse domínio. Não usar float na aritmética ou persistência financeira.

Nesta versão, BTC e USDT têm quantum contábil sintético `0.00000001`. Notional de compra e taxas são arredondados para cima nesse quantum; receita bruta de venda, para baixo. A diferença explícita de arredondamento integra o valor contabilizado; nenhum resíduo é escondido por tolerância. Preço/step dependem das regras sintéticas, não das oito casas da contabilidade.

A demonstração usa saldo inicial de 10000 USDT, compra de 1 BTC com REFERENCE=100 e venda de 1 BTC com REFERENCE=110, tick `0.01`, step `0.000001`, taxa/spread/slippage do exemplo. São preços e regras didáticos, sem associação ao preço real do BTC ou à comissão de uma conta Binance.

| Etapa | Preço final | Taxa em USDT | Saldo livre USDT após o fill |
|---|---|---|---|
| Compra | 100.10 | 0.10010000 | 9899.79990000 |
| Venda | 109.89 | 0.10989000 | 10009.58001000 |

Após a venda: BTC livre/reservado zero, USDT reservado zero, custo da posição zero e resultado líquido realizado `9.58001000 USDT`. Taxas totais `0.20999000 USDT`. Esses resultados foram conferidos aritmeticamente com Decimal nesta especificação, sem executar um simulador.

## 6. Regras sintéticas e risco antes da reserva

### 6.1 Regras do símbolo

O roteiro fornece snapshot sintético versionado de status/permissão Spot, base BTC, cotação USDT, tick, quantidade mínima/máxima, step e notional mínimo/máximo aplicáveis. A fixture positiva deve explicitar preço/tamanho e notional suficientes para as operações do exemplo, incluindo `PRICE_FILTER`, `LOT_SIZE`, `MARKET_LOT_SIZE` e pelo menos uma regra de notional.

Implementar o subconjunto usado: `PRICE_FILTER`, `LOT_SIZE`, `MARKET_LOT_SIZE`, `MIN_NOTIONAL` e `NOTIONAL`, respeitando os indicadores de aplicação a mercado. Se houver dois filtros de quantidade/notional aplicáveis, cumprir ambos. Para steps simultâneos, calcular um múltiplo comum em unidades inteiras do quantum contábil e normalizar para o maior múltiplo admissível não superior à quantidade pedida; não aplicar arredondamentos sequenciais que violem um step anterior. Step não representável nessa escala é regra não suportada, sem aproximação. Regra desabilitada por zero deve seguir seu contrato documentado; valores negativos são inválidos. Filtro desconhecido ou não suportado bloqueia a operação, sem tentar interpretá-lo por aproximação.

Para notional nesta simulação usar o preço do plano de fill e declarar essa escolha: não reproduz médias de referência ou toda a admissão da corretora. Filtros do cenário são sintéticos contemporâneos ao replay; regras atuais da Binance não comprovam filtros históricos. A implementação não deve consultar exchangeInfo pela rede para completar um roteiro incompleto. Referência técnica: [filtros oficiais](https://github.com/binance/binance-spot-api-docs/blob/master/filters.md).

### 6.2 Limites e marcação

Antes de cada novo BUY, exigir carteira reconciliada, observação válida/fresca, dia de risco inicializado, nenhum compromisso pendente e nenhuma posição já aberta. A entrada, incluindo notional e taxa, não pode superar `max_entry_fraction` do patrimônio anterior à intenção (default 10%); a exposição projetada, incluindo o compromisso reservado, não pode superar `max_exposure_fraction` (default 10%). Usar a quantidade normalizada e revalidar após arredondamentos. Os limites configuráveis precisam ser identificados no resultado da decisão.

Patrimônio = USDT livre + reservado + BTC total marcado por referência sintética válida. Se a observação for BID_ASK, usar bid para a marcação da posição comprada. Reserva é transferência interna, não despesa ou posição adicional: não contar o mesmo compromisso duas vezes. Na admissão, usar o maior entre valor marcado e custo reservado para a nova entrada como avaliação conservadora de exposição.

Perda diária de `max_daily_loss_fraction` (default 1%) ou drawdown de `max_drawdown_fraction` (default 5%), atingidos ou ultrapassados, suspendem novas entradas. Incluir taxas e marcação não realizada. Persistir pico de patrimônio, baseline diário e travas; reinício ou replay não os zera. A trava de drawdown permanece até procedimento futuro explícito, não desaparece porque o preço recuperou. Trava diária permanece no dia correspondente.

O evento `DAY_START` inicializa a referência do dia UTC uma vez, no instante 00:00:00Z desse dia, com marcação sintética válida/fresca e patrimônio antes das ordens. Exigir um novo DAY_START para cada dia do roteiro, antes de ordens desse dia; rejeitar tentativa de substituir o baseline existente. O cenário positivo começa com DAY_START em 01/10/2026 às 00:00 UTC, sem BTC e com patrimônio 10000 USDT. Não inventar preço de meia-noite nem deduzir um baseline novo a partir do saldo após a perda.

SELL exige BTC livre suficiente, nenhum short e estado/dados confiáveis. Pode reduzir/encerrar posição mesmo com trava diária/drawdown, sujeita a saldo, precisão e regras do símbolo. Não vender automaticamente como efeito colateral de uma trava. Posição, perdas e custos são exclusivamente simulados; o limite dispara bloqueio de admissão, sem garantir perda máxima em movimentos de preço.

## 7. Livro-razão, posição e transações

### 7.1 Contabilidade por ativo

Registrar eventos imutáveis e postings assinados com identidade de carteira, sequência, UTC do replay, ativo, conta, quantidade Decimal em string e referência de intenção/fill. Para cada evento contábil, a soma dos postings é **zero separadamente em BTC e USDT**. Não somar BTC e USDT como unidades equivalentes.

Contas mínimas: carteira livre/reservada por ativo e contrapartidas técnicas de capital inicial, mercado e taxas. Contrapartidas técnicas podem ter sinal negativo; saldos livres/reservados da carteira nunca podem ficar negativos. A inicialização gera um único lançamento de capital sintético, não um saldo avulso fora do ledger.

Reserva move livre → reservado no mesmo ativo. Na compra, consumir USDT reservado para notional/taxa e creditar BTC livre, com contrapartidas de mercado/taxa. Na venda, consumir BTC reservado e creditar receita USDT líquida. Liberação move reservado → livre; sobra de reserva não é receita. Persistir taxa como componente separado, com ativo USDT e quantidade original.

Custo médio inclui notional e taxa da compra. Venda parcial reduz o custo proporcional à quantidade, com custo baixado arredondado para baixo a oito casas; a última venda absorve todo o custo remanescente para zerar o lote, sem resíduo oculto. Resultado realizado = receita líquida da venda − custo baixado. Resultado não realizado e patrimônio dependem da última marcação válida. Não tratar transferência de reserva como lucro/prejuízo.

### 7.2 Identidade e estados

Identidade de negócio: carteira + scenario_id + action_id. Guardar hash do payload canônico e do modelo/configuração. Mesma identidade e conteúdo devolve o resultado anterior; conteúdo diferente gera conflito antes de qualquer novo efeito. Um novo run_id não cria nova intenção. IDs de fill derivam da intenção/plano/modelo e são únicos no banco; fill repetido não gera novos postings.

Estados mínimos persistidos: `RISK_REJECTED`, `RESERVED`, `FILLED`, `REJECTED` e `CANCELED`. A proposta inicial pode existir somente em memória até sua primeira gravação. Não criar estados de transporte externo ou prometer exactly-once entre serviços: não existe envio remoto nesta Sprint.

Transação A: conferir versão/limites, persistir decisão, plano determinístico e reserva/ledger juntos em RESERVED; rejeição de risco persiste RISK_REJECTED sem reserva/fill. Transação B: aplicar fill, consumir/liberar reservas, gravar postings, posição, custos, risco e estado FILLED atomicamente. Uma rejeição/cancelamento local de uma intenção ainda não preenchida libera sua reserva em transação própria e impede fill posterior. Testar essa transição sem exigir novo comando administrativo nesta Sprint.

Não manter transação aberta durante geração de relatório ou operações de filesystem. O executor é puro/local, recebe somente plano e não consegue enviar ordens HTTP. No retorno normal, nenhuma intenção deve permanecer RESERVED; uma morte entre as duas transações pode deixar uma pendência recuperável.

### 7.3 Store independente e recuperação

Criar `data_dir/paper.sqlite3`, schema financeiro v1, separado do `market.sqlite3`. Não adicionar tabelas ao store de mercado, cujo contrato atual as rejeita. Reutilizar padrões de transação, flock, parametrização e validação de paths, sem importar pressupostos do schema de candles.

O banco da carteira contém identidade/configuração imutável, eventos, postings, projeções de saldos/posição, intenções/planos/fills, baseline/pico/travas e progresso do cenário. Restrições únicas protegem eventos, intenções, fills e inicialização. Uma versão da carteira deve proteger atualizações contra estado obsoleto, além do flock exclusivo durante todo o comando mutável.

Ao reabrir: verificar schema e integridade, reconstruir saldos/posição e risco a partir do histórico, comparar com projeções e conferir se toda reserva corresponde a intenção pendente. Só depois recuperar plano RESERVED. A retomada usa o plano persistido, o relógio de replay e a mesma versão/hash de modelo; não busca preço novo nem usa o relógio real para executar retroativamente. Bloquear mudanças de configuração/modelo/roteiro incompatíveis com a carteira existente; sem reset automático.

Morte antes do commit A: nenhum efeito. Depois de A e antes de B: reserva íntegra, ainda sem fill; retomada confirma o mesmo plano uma vez. Antes do commit B: rollback do fill inteiro. Depois de B: repetição devolve o fill registrado. Marcas, DAY_START e cursor também têm identidade e confirmação atômica, sem aplicar um evento duas vezes.

Divergência contábil bloqueia novos efeitos e é registrada de forma durável quando o banco permite. Não ajustar saldos por diferença, excluir lançamento ou reconstruir sobre o banco original silenciosamente. Relatório continua disponível para diagnóstico. Schema incompatível/corrupção interrompe; preservar cópia e orientar restauração de snapshot sintético verificado em outro diretório.

## 8. Relatórios e entregáveis

`paper-report` e o relatório do roteiro devem conter: configuração/modelo/roteiro identificados, saldos livres/reservados por ativo, BTC em posição, custo total/médio, taxas, resultados realizado/não realizado, patrimônio, pico, baseline/perda diária/drawdown, exposição, limites/travas, intenções/fills e resultado da reconciliação.

JSON financeiro usa strings decimais. Relatório exportado é derivado do banco, publicado com manifesto/hashes em diretório de execução único. Hash canônico financeiro exclui run_id e timestamps reais, mas inclui eventos e instantes do replay, quantidades, custos e estados. Falha de exportação não refaz fills: retorna erro operacional com progresso confirmado, e a repetição recompõe o relatório.

Caminhos abaixo são relativos ao módulo da aplicação, exceto `docs/...`, relativo ao workspace. São entregáveis futuros, ainda não implementados nesta especificação.

| Caminhos | Responsabilidade |
|---|---|
| `modules/trading/src/cripto_bot/domain/portfolio/` | Saldos, postings, posição, custo e invariantes |
| `modules/trading/src/cripto_bot/domain/risk/` | Admissão, exposição, marcação, baseline/pico/travas e regras sintéticas |
| `modules/trading/src/cripto_bot/adapters/execution/paper.py` | Plano/fill determinístico integral, sem rede |
| `modules/trading/src/cripto_bot/application/paper_run.py`, `paper_reconcile.py` e portas necessárias | Fluxo, idempotência, recuperação e reconciliação |
| `modules/trading/src/cripto_bot/adapters/storage/paper_sqlite.py`, `paper_report.py` | Store transacional e relatório derivado |
| `modules/trading/src/cripto_bot/adapters/paper_scenario.py` | Leitura e validação do roteiro sintético |
| Configuração, modelos e CLI existentes; `entrypoints/paper.py` | Composição dos comandos e contratos compatíveis |
| `config/paper.execution.example.toml`, `config/fixtures/paper-roundtrip.json` | Demonstração positiva e regras sintéticas completas |
| `tests/unit/test_portfolio.py`, `test_risk.py`, `test_paper_execution.py`, `test_paper_scenario.py` | Aritmética, invariantes, regras e cenários negativos |
| `tests/integration/test_paper_storage.py`, `test_paper_cli.py`; harness/smoke test existentes | Transações, morte de processo, replay e distribuição |
| `README.md`, `.gitignore`, `pyproject.toml`/`uv.lock` se necessário | Instruções e artefatos; não acrescentar dependências sem uso justificado |
| `docs/arquitetura.md`, `docs/decisoes/0004-carteira-paper-e-ledger.md` | Decisões e limites do simulador |
| `docs/testes/sprint-03-validacao.md`, `docs/sprints/sprint-03.md`, `docs/planejamento.md` | Evidências, estado e limitações |

Manter biblioteca padrão, Pydantic já presente e ferramentas existentes. Não exigir ORM ou biblioteca financeira. Hypothesis pode ser acrescentado somente se os testes gerativos de conservação justificarem a dependência; cenários determinísticos continuam obrigatórios.

## 9. Sequência de implementação e critérios de aceite

Sequência: revalidar base → definir aritmética/modelos → ledger/reconciliação → regras/risco → plano simulado → store e falhas transacionais → roteiro/CLI → relatório/wheel → documentação. Criar apenas componentes usados.

A tabela abaixo define os resultados exigidos pelo contrato original. Todos foram exercitados na implementação; a [matriz executada](../testes/sprint-03-validacao.md#6-matriz-ac01ac18) registra evidências e resultados.

| ID | Cenário | Resultado exigido |
|---|---|---|
| AC01 | Regressão Sprints 01/02 | CLI anterior, coleta offline, guards e stores de mercado preservados |
| AC02 | Roteiro positivo BUY/SELL | Dois fills, taxas e saldo final exatos da seção 5.3; reservas e posição zeradas |
| AC03 | Repetição do roteiro e eventos/fills | Nenhum novo aporte/fill/posting; mesmo hash financeiro; resultados anteriores identificados |
| AC04 | Mesma identidade, payload/modelo/config incompatível | Conflito sem novo efeito; não criar carteira nova silenciosamente |
| AC05 | Reserva, consumo, sobra e liberação | Saldos não negativos, nenhum gasto duplicado, reserva coerente com a intenção |
| AC06 | Ledger e custo | Soma zero por ativo, taxas separadas, reconstrução exata; venda parcial/última baixa sem resíduo |
| AC07 | Precisão e arredondamento | Float/bool/NaN/expoente rejeitados; step não decimal simples, tick adverso e notional revalidados |
| AC08 | Regras Spot sintéticas | Símbolo/permissão/filtro desconhecido, tamanho e notional inválidos rejeitados antes da reserva |
| AC09 | Saldo, short e exposição | Sem BTC para SELL, sem USDT para BUY, segunda posição/pirâmide/pendência e excesso de 10% rejeitados |
| AC10 | Risco temporal e drawdown | DAY_START único, perda de 1%/drawdown de 5% nas fronteiras, persistência de pico/travas e virada UTC |
| AC11 | Saídas sob trava | SELL de redução aceita com dados íntegros; trava não provoca venda automática nem libera entrada |
| AC12 | Preço e tempo | Observação posterior à decisão, idade de até 5 s, sem futuro/reordenação; BID_ASK não cobra spread novamente |
| AC13 | Morte antes/depois de A e B | Rollback íntegro ou pendência recuperável; nunca meio fill ou lançamento duplicado |
| AC14 | Concorrência e versão obsoleta | Um escritor por carteira/store; atualização com versão errada rejeitada |
| AC15 | Reconciliação e corrupção | Projeção/ledger/reserva/fill divergentes bloqueiam; nenhuma correção silenciosa ou recriação destrutiva |
| AC16 | Relatório/exportação e reinício | Leitura coerente, falha de exportação preserva fills; repetição só recompõe saída |
| AC17 | Segurança offline e sanitização | Modos/credenciais/path/flags proibidos falham antes dos efeitos; nenhum cliente HTTP/privado construído |
| AC18 | Qualidade e wheel | Ruff, mypy strict, pytest com branches, build e wheel neutro executando roteiro sob guard aprovados |

Testes de falha usam fixtures e injeção determinística; mortes de processo precisam comprovar persistência real SQLite e liberação de lock. Bloquear sockets no pytest e nos filhos, testar o próprio bloqueio e usar apenas segredos sintéticos. Testar variantes de regras/risco em stores temporários novos, sem alterar carteiras já confirmadas para fazer o gate passar.

Exigir cobertura das ramificações de admissão, reserva, identidade, arredondamento e commit/rollback; apresentar lacunas com justificativa. Não impor percentual global como substituto desses cenários nem excluir caminhos críticos para elevar cobertura.

### Comandos previstos

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
uv run --locked cripto-bot check-config --config config/paper.execution.example.toml
uv run --locked cripto-bot paper-run --config config/paper.execution.example.toml
uv run --locked cripto-bot paper-reconcile --config config/paper.execution.example.toml
uv run --locked cripto-bot paper-report --config config/paper.execution.example.toml
uv run --locked cripto-bot paper-run --config config/paper.execution.example.toml
```

O executor deve registrar os comandos exatos de instalação do wheel e o seu SHA-256. O smoke test usa ambiente separado dentro do módulo, diretório neutro, origem em site-packages, paths absolutos de cenário/dados e ausência de PYTHONPATH do checkout. Criar uma carteira temporária nova por smoke test; repetir o roteiro nessa mesma carteira para provar idempotência. Não confundir dados de execução anterior com uma primeira compra/venda.

## 10. Evidências, riscos, custos e conclusão

O guia 03 registra revisões dos dois repositórios, versões, hashes dos fontes/configuração/modelo/roteiro/wheel, comandos/exit codes, saídas esperadas/obtidas, AC01–AC18, cobertura, saldos e ledger por ativo, planos/fills, baseline/pico/travas, resultados de reconciliação e ensaios de falha. Informar o que foi de fato executado; teste planejado não é aprovação.

Riscos principais: arredondamento que cria resíduo, reserva insuficiente/contada em dobro, idempotência vinculada só ao run_id, reavaliação com preço novo após crash e alteração do baseline que apaga perdas. As decisões desta especificação e seus testes devem demonstrar essas barreiras. Não confundir integridade da simulação com evidência de rentabilidade ou qualidade de execução real.

Em corrupção/divergência: parar novos efeitos, preservar banco e logs, diagnosticar/reconciliar em cópia. Restaurar somente snapshot sintético identificado em novo diretório; nunca substituir a carteira original automaticamente. Se o relatório falhar, reexportar sem refazer fills. Em conflito de versão de modelo, manter bloqueio até decisão registrada, sem reset.

AWS zero: não há serviço ou recurso provisionado, taxa real ou capital real. Uso somente local de disco/CPU. Estimativa orientativa de 2–5 dias úteis, revisável pela execução; contabilizar complexidade real dos invariantes sem retirar testes para cumprir o prazo.

Ignorar carteiras/relatórios gerados, bancos, locks e temporários; preservar exemplos e fixtures versionáveis. Limpeza deve identificar precisamente a carteira de teste. Não apagar outros datasets/carteiras, histórico Git ou evidências para resolver erro. Não publicar remotos ou criar commit por implicação desta Sprint.

Concluir somente com AC01–AC18 aprovados, pacote/wheel funcionais e evidências auditáveis. Caso contrário, registrar PENDENTE e correção necessária. Revisar a entrega antes de detalhar a Sprint 04; não iniciá-la nem promover modo automaticamente.

## 11. Prompt autossuficiente de execução

```text
Implemente somente a Sprint 03 — Carteira PAPER, reservas e execução simulada.

Workspace: /home/cams7/Dev/Cripto. Aplicação e diretório de comandos:
/home/cams7/Dev/Cripto/cripto-bot. Documentação central:
/home/cams7/Dev/Cripto/docs, repositório independente. Caminhos docs/... são
relativos ao workspace; demais entregáveis pertencem ao módulo cripto-bot.
Leia instruções locais, docs/planejamento.md, docs/sprints/sprint-03.md na
íntegra, docs/arquitetura.md, docs/decisoes/, Sprint 02 e guia/evidências 02.
Inspecione README, manifest, lock, código e testes atuais antes de editar.
Preserve alterações anteriores e os dois históricos Git. Não crie outro
repositório para subpacotes; novos módulos independentes futuros nascerão
diretamente no workspace com Git próprio.

Dependências:
1. Sprint 02 aprovada offline, com evidências e integridade verificadas.
2. Python 3.13.15, uv 0.12.19 e escrita permitida no módulo/docs.
3. Contratos e invariantes AC01–AC18 desta especificação compreendidos.
4. Documentação oficial Decimal/sqlite3/filtros reconfirmada na implementação.
Se requisito indispensável falhar, registre em docs/testes/sprint-03-validacao.md
e não avance trabalho dependente. Não apresente teste não executado como aprovado.

Somente PAPER offline Spot BTCUSDT. Não implemente estratégia/sinais, backtest,
rede de negociação, SDK Binance, boto3, AWS, infraestrutura, notificações,
Testnet/LIVE, margin/short ou Sprint 04. Não leia credenciais, não colete
preços externos e não altere projetos LotoBot. Preserve comandos check-config,
run-once NOOP e collect-market. Os novos comandos financeiros não constroem
cliente HTTP e rejeitam --allow-network.

Crie a tabela opcional paper e config/paper.execution.example.toml conforme
a seção 4. Paths ficam no módulo após resolver symlinks; variáveis, campos,
credenciais e modos desconhecidos continuam rejeitados antes dos efeitos.
Exponha paper-run, paper-report e paper-reconcile. JSON em stdout, logs
sanitizados em stderr, UTC/run_id/PAPER/orders_sent=0 e contadores separados
de fills simulados. Exit codes: 0 sucesso/roteiro concluído, 2 configuração,
3 falha operacional/divergência/conflito, 1 falha inesperada. Rejeição de risco
deve constar como rejeição e nunca como fill bem-sucedido.

Entregue domain/portfolio e domain/risk, adapters/execution/paper.py,
application/paper_run.py e paper_reconcile.py, portas mínimas usadas,
adapters/paper_scenario.py, adapters/storage/paper_sqlite.py e paper_report.py,
entrypoints/paper.py e integração com configuração/modelos/CLI existentes.
Não crie framework ou adapters vazios. Prefira dependências já disponíveis.

Use roteiro config/fixtures/paper-roundtrip.json com DAY_START, MARK e ORDER,
relógio de replay, identidades estáveis e regras sintéticas versionadas.
Decisão deve preceder observação e fill; preço fresco até 5 s. Implemente
REFERENCE com metade do spread por lado mais slippage, e BID_ASK sem cobrar
spread novamente. Aritmética Decimal local precisão 80, strings limitadas,
BTC/USDT quantum 1e-8, tick adverso, quantidade para baixo no step e taxa
para cima. Revalide filtros e risco após normalização. Sem float financeiro.

Implemente ledger balanceado por ativo, saldos livres/reservados não negativos,
custo médio incluindo taxa, resultado realizado/não realizado e contrapartidas.
Taxas só em USDT. Admissão: entrada/exposição até 10%, uma posição/pendência,
sem pirâmide/short. Perda diária de 1% e drawdown de 5% bloqueiam entradas;
DAY_START, pico e travas persistem. Saídas de redução sob trava exigem dados,
saldo e estado confiáveis; não liquidar automaticamente. Siga a seção 6.

SQLite financeiro separado paper.sqlite3: não altere schema/tabelas de
market.sqlite3. Lock exclusivo, versão da carteira e constraints de identidade.
Transação A grava plano/decisão/reserva/ledger juntos; B confirma fill,
saldos, posição, custos, risco e estado atomicamente. Rejeição/cancelamento
local sem fill libera a reserva. Recupere RESERVED usando o plano e relógio
persistidos, sem novo preço; eventos/fills repetidos não geram lançamentos.
Mesmo ID com outro payload/modelo/config gera conflito, sem reset silencioso.

Reconcile ao abrir antes de qualquer novo efeito: reconstrua histórico,
compare projeções, reservas, posição, custos, risco e fills. Divergência
bloqueia duravelmente quando possível, sem corrigir por diferença. Relatório
é derivado; erro de exportação preserva fills e permite reexportar. Registre
hash financeiro canônico, proveniência, modelo/configuração e estado real.

Exemplo obrigatório: iniciar 10000 USDT, comprar 1 BTC com REFERENCE 100 e
vender 1 BTC com REFERENCE 110, tick 0.01/step 0.000001, fee/spread/slippage
10/10/5 bps. Preços finais 100.10 e 109.89; taxas 0.10010000 e 0.10989000.
Saldo final 10009.58001000 USDT, BTC e reservas zero; lucro líquido realizado
9.58001000, taxas totais 0.20999000. São números sintéticos de teste.

Crie testes unitários e integração de AC01–AC18: regressão, repetição,
conflitos, reservas, venda parcial, arredondamentos/filtros, fronteiras de
risco/dia, preço temporal, rollback/morte antes/depois dos dois commits,
concorrência/versão e reconciliação/corrupção/exportação. Bloqueie sockets
no pytest e filhos, incluindo wheel, e teste o guard. Use segredos sintéticos.

Execute na raiz do módulo uv sync --locked --group dev; uv run --locked
ruff check .; uv run --locked ruff format --check .; uv run --locked mypy
modules/trading/src; uv run --locked pytest -q --cov=cripto_bot --cov-branch
--cov-report=term-missing; uv build; check-config, paper-run, paper-reconcile,
paper-report e nova paper-run com o exemplo, cada CLI via uv run --locked.
Teste wheel reinstalado em ambiente separado dentro do módulo, diretório
neutro sem PYTHONPATH do checkout, paths absolutos, carteira nova e replay
na mesma carteira. Registre origem em site-packages e hash do wheel.

Atualize README e .gitignore sem ignorar fixtures. Documente em português
docs/arquitetura.md, docs/decisoes/0004-carteira-paper-e-ledger.md,
docs/testes/sprint-03-validacao.md, docs/sprints/sprint-03.md e planejamento.
Registre commits dos dois repositórios, versões, comandos/exit codes,
resultados, cobertura/lacunas, hashes e ledger/reconciliação, falhas e
recuperação, limpeza e AWS zero. Conclua somente com todos os critérios
obrigatórios aprovados; caso contrário, marque PENDENTE e descreva a correção.
Não inicie Sprint 04, faça deploy, publique remotos ou envie mensagens/ordens.
```

## 12. Fontes e verificação desta especificação

Fontes oficiais consultadas em 24/10/2026: [Python 3.13 — Decimal](https://docs.python.org/3.13/library/decimal.html), para contexto local e arredondamentos; [sqlite3](https://docs.python.org/3.13/library/sqlite3.html), para controle transacional; [Binance — filtros](https://github.com/binance/binance-spot-api-docs/blob/master/filters.md), para distinguir regras de preço/quantidade/notional do modelo sintético.

Limites de risco, ledger, escala, taxas sintéticas, CLI e estados descritos aqui são decisões de projeto, não afirmações sobre tarifas ou execução de uma conta real. Nenhuma nova API externa é introduzida. O executor deve reconfirmar contratos e ferramentas antes da implementação.

No detalhamento original foram lidos o planejamento, evidências/guia 02, ADRs e componentes pertinentes; conferidos 24 hashes e as revisões dos dois repositórios; consultadas fontes oficiais e calculado o exemplo com Decimal. Não foram executados testes da aplicação, instaladas dependências, implementados componentes, alterado o módulo cripto-bot ou enviada qualquer ordem.

## 13. Registro da execução em 24/10/2026

Implementação solicitada e concluída no repositório `/home/cams7/Dev/Cripto/cripto-bot`, a partir do commit `a102223`; documentação baseada em `552b3f2`, preservando as alterações anteriores. O módulo mantém Git independente e os comandos anteriores. Não houve alteração de dependências, schema de mercado, commits ou remotos.

Entregues os componentes da seção 8, configuração/fixture positivas, comandos `paper-run`, `paper-report`, `paper-reconcile`, testes, README, arquitetura e [ADR 0004](../decisoes/0004-carteira-paper-e-ledger.md). O store financeiro schema v1 usa modelo `paper-integral-v1`, journal/postings imutáveis, projeções verificáveis e duas transações recuperáveis. Relatórios são derivados e a leitura não cria carteira. Divergências bloqueiam quando possível e não são corrigidas por diferença.

Decisões concretizadas: observações identificadas inline, roteiro limitado a 1 MiB/1000 eventos, IDs de ação únicos dentro do roteiro, schema inteiro estrito e rejeição de receita/preço normalizados não positivos. A repetição do roteiro persistido é idempotente; a duplicação estrutural de IDs no arquivo é rejeitada antes da execução. Cancelamento/rejeição de reserva são operações internas testadas, sem CLI administrativa. Venda parcial de uma posição usa fill integral de quantidade menor; fill parcial não integra este modelo.

Validação final aprovada: **316 testes**, cobertura de statements **98,61%**, branches **96,55%**, combinado **98,12%**; Ruff/formatação/mypy strict, build e wheel reinstalado em ambiente neutro aprovados. Interrupções reais antes/depois de A/B, rollback, concorrência, corrupção, bloqueios de risco, guard de sockets e reexportação foram exercitados. Cobertura restante e limites não testados estão explicitados no guia, sem alegação de cobertura integral da aplicação.

O ciclo check-config → paper-run → paper-reconcile → paper-report → paper-run foi executado tanto no checkout quanto no wheel. Em carteira nova, confirmou 2 fills e saldo final `10009.58001000` USDT; replay gerou zero fills novos e preservou o hash financeiro. Posição/reservas/custo finais zerados, taxas `0.20999000` e resultado realizado `9.58001000`. Postings balanceados separadamente em BTC/USDT e hashes de exportação conferidos.

Comandos, versões, hashes, origem do wheel, ledger completo, matriz AC01–AC18, diagnóstico e limpeza estão no [guia 03](../testes/sprint-03-validacao.md) e nas [evidências JSON](../testes/sprint-03-evidencias.json). Somente simulação local; AWS zero. Nenhuma estratégia, coleta externa ou ordem real. Próxima ação: revisão das evidências antes do detalhamento da Sprint 04, sem iniciá-la automaticamente.

## Adendo documental de 25/10/2026 — validações antes de LIVE

O aceite registrado neste documento permanece restrito ao escopo histórico executado. Ele não comprova backtest fora da amostra, PAPER contínuo, Demo Spot, Spot Testnet ou `POST /api/v3/order/test`. A sequência e os gates atualizados estão no [planejamento, seção 10](../planejamento.md#10-gates-entre-ambientes-e-modos) e no [roteiro de validação](../testes/validacao-pre-live.md). Demo passa à Sprint 09, Testnet complementar à 10 e preparação LIVE à 11, sem ativação. A implementação desta Sprint continua exclusivamente PAPER; DEMO/TESTNET/LIVE não são liberados por esta revisão.

Nenhum teste foi repetido e nenhuma evidência JSON foi alterada por este adendo. A solicitação atual autoriza somente revisão documental. LIVE permanece bloqueado por padrão e exige validações concluídas, limites de risco reais e aprovação explícita vigente do responsável.

O fill integral sintético desta Sprint não cobre execuções parciais, atrasos ou ordens sem fill do PAPER contínuo; venda de parte da posição não é fill parcial de uma ordem. Esses cenários são obrigatórios na [Sprint 06](../sprints/sprint-06.md) antes da integração privada.

## Referência documental do banco — revisão de 25/10/2026

O DDL existente foi documentado em [bancos/paper-sqlite.md](../bancos/paper-sqlite.md), com diagrama relacional, constraints, operação e rejeição de schemas incompatíveis. Esta revisão foi leitura de fonte, sem abrir bancos, executar migrations ou repetir testes; não amplia o aceite histórico. Qualquer futura mudança estrutural exige atualização desse documento e do [catálogo](../bancos/README.md), com verificação/evidências na Sprint responsável, conforme seção 4.8 do planejamento.
