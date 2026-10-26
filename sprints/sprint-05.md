# Sprint 05 — Backtesting e avaliação fora da amostra

Data do detalhamento: 25/10/2026.

**Estado: IMPLEMENTADA E VALIDADA no alcance local/PAPER/backtest/BTCUSDT/15m.** O registro seguinte descreve o detalhamento anterior; resultados da execução corrente foram consolidados na seção 15 e no guia 05.

**Registro original do detalhamento:** Revisadas a entrega e as evidências da Sprint 04: 87/87 hashes dos arquivos consultados conferem com a aplicação atual. Os 428 testes anteriores são resultado histórico; não foram repetidos nesta atualização. A solicitação do detalhamento original autorizava somente documentação, sem coleta, backtest ou alteração de carteiras.

Referências principais: [planejamento](../planejamento.md), seções 4.6–4.9, 6.2–6.4, 9, 10 e 13; [Sprint 04 e seu registro de execução](sprint-04.md#15-registro-de-execução-em-25102026), [guia 04](../testes/sprint-04-validacao.md) e [evidências 04](../testes/sprint-04-evidencias.json). Complementos: [trend_sma](../estrategias/trend_sma.md), [arquitetura modular](../arquitetura-modular.md), [matriz modular](../testes/estrategias-modulares-validacao.md), [bancos](../bancos/README.md), [ADR 0005](../decisoes/0005-estrategia-modular-e-persistencia.md) e [guia 05](../testes/sprint-05-validacao.md).

## 1. Objetivo e incremento demonstrável

Avaliar a estratégia SMA20/50 em dados históricos de BTCUSDT/15m, com carteira fictícia, decisões causais, custos e regras de risco, separando desenvolvimento, validação e teste final intocado. Produzir resultado reproduzível e comparável a caixa e buy-and-hold, independentemente de lucro ou prejuízo.

A entrega demonstra: preparação/verificação do dataset; congelamento do protocolo antes de calcular resultados; execução separada dos três segmentos; matriz de custos/atraso definida antecipadamente; benchmarks com capital independente; repetição sem duplicação; relatório HTML para leitura humana e arquivos estruturados de auditoria. A fixture curta prova o software; uma avaliação histórica real precisa identificar sua própria origem, janela e limitações.

Não transformar o replay de 71 candles da 04 em evidência econômica. Esta Sprint não entrega PAPER contínuo, parcial/UNKNOWN operacional, novas estratégias, infraestrutura ou negociação privada. Ao final, revisar as evidências para detalhar a Sprint 06; não iniciá-la automaticamente.

## 2. Diretórios e pré-requisitos conferidos

- Workspace: `/home/cams7/Dev/Cripto`.
- Aplicação/raiz Python e uv: `/home/cams7/Dev/Cripto/cripto-bot`.
- Documentação: `/home/cams7/Dev/Cripto/docs`, Git independente.
- Pacote: `modules/trading/src/cripto_bot`, no repositório existente.

Subpacotes históricos continuam dentro desse pacote; não criar outro Git para backtest/indicadores. Preservar trabalho, dados e os dois históricos. Caminhos `docs/...` são relativos ao workspace; os demais, salvo indicação, à aplicação.

| Dependência | Inspeção deste detalhamento | Condição antes de implementar |
|---|---|---|
| D01 — Entrega 04 | AC01–AC18 aprovados no alcance offline; 428 testes; cobertura combinada 96,52%; qualidade/build/wheel e HTML registrados | Reproduzir regressão pertinente e registrar o resultado atual |
| D02 — Integridade | 87/87 hashes de fontes/configuração/fixtures/testes/manifest/lock/pin conferem; zero divergência | Rever mudanças posteriores antes de trabalho dependente |
| D03 — Revisões | Aplicação `23545df1dcad76cf90dfefd29e8134558bee3f50`; docs `c9db28c8521e47b722808bc980fe086821a7e653`; ambos limpos no início | Registrar revisões e estado efetivamente usados, preservando trabalho posterior |
| D04 — Ferramentas | Python 3.13.15, uv 0.12.19 e dependências do lock existente | Confirmar ambiente/permissões; não atualizar dependências sem necessidade |
| D05 — Base financeira | Mercado v1; carteira manual v1; modular v2, sem migração; redução financeira/risco e SMA pura disponíveis | Reutilizar regras e preservar seus contratos; aplicar separação da seção 8 |
| D06 — Limites atuais | Fixture limitada a 4 MiB/1.000 candles; estado modular mantém histórico e faz reconstruções completas | Criar caminho histórico com leitura/estado limitados; não apenas aumentar o limite da fixture |
| D07 — Dados de avaliação | Evidências demonstram dois candles de coleta fixture e 71 candles sintéticos; não comprovam histórico real de 24 meses disponível | Verificar/preparar dataset real antes da avaliação econômica; não inventar disponibilidade ou cotações |
| D08 — Documentação | SMA, schema v1/v2 e ADR 0005 entregues | Atualizá-los conforme o comportamento efetivo da 05, incluindo o novo store histórico |

Não foram abertos bancos operacionais nem reexecutados testes nesta revisão. A ausência de histórico real já validado não impede detalhar/implementar os componentes e seus testes. Impede apresentar uma fixture como avaliação histórica real concluída. Se um pré-requisito de código falhar, registrar PENDENTE no guia 05 e interromper o trabalho dependente.

## 3. Escopo, módulos e compatibilidade

Somente `mode=PAPER`, ambiente `local`, avaliação `backtest`, BTCUSDT/15m, Spot long-only, uma instância SMA proprietária por avaliação. Reutilizar `TrendSMA`, coordenação exclusiva, dimensionamento e risco; nenhum catálogo opcional é requisito.

Separar modo financeiro de avaliação: backtest não é outro modo nem permissão de trading. Acrescentar capacidade backtest ao registro/configuração somente no fluxo histórico. Parametrizar a seleção de escopo sem alterar a semântica de `.active`/fixture da 04 ou herdar permissão para continuous/DEMO/TESTNET/LIVE. Sem módulo habilitado, execução histórica retorna NOOP sem carteira.

Preservar check-config, run-once NOOP, collect-market, paper-* e strategy-*, suas configurações, limites e resultados. O banco/dataset da 04 não é convertido em histórico nem reprocessado silenciosamente. SMA mantém as regras 20/50 e de igualdade; alterações materiais de regra exigem versão/evidência próprias.

Fora do incremento: busca automática de parâmetros, walk-forward/ML, composição weighted_targets/segregated_budgets, multiativo, novas estratégias, OMS remoto, ordens limitadas, liquidez real, fill parcial/probabilístico, daemon, notificações, AWS, credenciais, modos privados, margem/short/alavancagem e aportes. Fakes verificam conflitos/limites de composição; combinações reais não implementadas continuam rejeitadas.

## 4. Dataset, proveniência e divisão cronológica

### 4.1 Preparação e validação integral

Importar exportações locais imutáveis da Sprint 02, por seus manifestos e candles JSONL gzip. Verificar hashes dos bytes, hash canônico quando disponível, schema/parser, fonte, símbolo/intervalo, contagem e janelas. Unir somente trechos compatíveis e contíguos; duplicata idêntica pode ser deduplicada com contador, conflito é erro, sem sobrescrita. Ler SQLite de mercado diretamente não é necessário para o incremento; não abrir o store operacional para escrita.

`backtest-prepare` publica candles normalizados JSONL e manifesto de dataset com origem fixture/pública, fontes e hashes, dataset lógico, hash completo, UTC inicial/final, quantidade, lacunas/duplicatas, hipótese de disponibilidade, versão de filtros, licença/condições de uso quando aplicáveis e limites conhecidos. Publicar por temporário/rename após validar o conjunto inteiro; dados inválidos não criam carteira financeira.

Limites iniciais: 200.000 candles, 256 MiB descompactados por dataset e 16 KiB por registro; validar tamanho descompactado, contagem/CRC e limites por linha durante streaming, sem carregar o gzip inteiro. Campos financeiros seguem strings/Decimal, sem float, expoente, NaN/infinito ou bool disfarçado de inteiro. Validar OHLC, volumes, ordenação, alinhamento 15m, disponibilidade/fechamento e continuidade, incluindo warm-up. Não preencher gaps ou interpolar preços. Rejeitar outros pares/intervalos/versões antes de efeitos.

Se faltar dado real na implementação, a preparação pode usar o collect-market público já existente, em operação separada e explícita com `--allow-network`, configuração binance_public, janelas limitadas e checkpoints. Somente GETs públicos permitidos pelo adapter, sem credencial, proxy/fallback para contornar acesso ou mudança de host. Registrar comandos/limites/429/deadline e retomar trechos faltantes; não fazer rede dentro do backtest. Indisponibilidade/acesso não permitido mantém a avaliação correspondente PENDENTE, sem substituir dados reais por fixture.

Snapshots atuais de exchangeInfo não comprovam filtros históricos. Preferir snapshots históricos disponíveis; quando inexistirem, congelar um conjunto sintético/proxy claramente identificado e registrar a limitação. Não consultar regras atuais durante replay para completar uma operação nem afirmar simulação fiel de admissão histórica.

### 4.2 Janela e split

Meta do planejamento: 24 meses fechados, condicionada à qualidade/disponibilidade. Referência para esta data, ainda não coletada/validada: `[2024-10-25T00:00:00Z, 2026-10-25T00:00:00Z)`, 70.080 candles de 15m, mais warm-up anterior. Datas calculadas documentalmente:

| Segmento | Janela de aberturas de candles, fim exclusivo | Quantidade se completo |
|---|---|---|
| Desenvolvimento, 60% | 25/10/2024 00:00 UTC até 06/01/2026 00:00 UTC | 42.048 |
| Validação, 20% | 06/01/2026 00:00 UTC até 01/06/2026 00:00 UTC | 14.016 |
| Teste final, restante | 01/06/2026 00:00 UTC até 25/10/2026 00:00 UTC | 14.016 |

Para outra janela real, registrar datas/motivo antes do congelamento. Calcular `n_dev=floor(0.60*N)`, `n_val=floor(0.20*N)` e `n_test=N-n_dev-n_val` sobre os candles de score; não incluir warm-up nessa razão. Cada segmento deve permitir ao menos `slow_window+2` candles de score para o ensaio técnico; isso não é tamanho estatístico suficiente nem autorização econômica. Não impor número mínimo de trades ou fabricar sinais para completar a amostra.

Cada segmento inicia carteira independente de 10000 USDT, em caixa, risco e instância novos, sem carregar posição, PnL, reservas ou seleção de parâmetros de outro segmento. Esse reinício é parte do protocolo comparável, não recuperação de carteira contínua. Não somar retornos/patrimônios independentes para fingir um único portfólio contínuo.

Aquecimento: até slow_window fechamentos anteriores ao segmento (50 nos defaults), com disponibilidade até seu início. Dados anteriores só preparam as duas médias; não geram ordens, taxas, PnL, métricas ou posição herdada. Primeiro segmento exige prefixo anterior ao início; na janela de referência, warm-up começa em 24/10/2024 11:30 UTC. Segmentos seguintes podem usar o prefixo temporal anterior, sem consultar candles futuros.

## 5. Experimento congelado e teste final

Antes de calcular PnL de qualquer segmento, `backtest-freeze` registra protocolo imutável: dataset/hash completo, datas/split/warm-up, versão/hash de código/módulo, parâmetros/flags/coordenação/limites, capital, modelo de execução/filtros/disponibilidade, política terminal, benchmarks, variantes e fórmulas de métricas. Campos incompletos impedem congelamento; não usar defaults ocultos que mudem depois.

Executar desenvolvimento e validação antes do teste, com a mesma versão congelada. Nesta Sprint usar SMA20/50 fixada, sem otimização. Se uma correção material exigir mudar código, parâmetros ou dados antes do teste, preservar o experimento anterior, criar outro protocolo e repetir desenvolvimento/validação. O teste final só aceita o protocolo que completou essas fases sem divergência.

Primeiro processamento do teste registra consumo da janela final para aquele protocolo/versão. Repetir exatamente a mesma execução é reprodução, sem novo efeito ou nova alegação de amostra intocada. Mudança após observar resultado final invalida a elegibilidade afetada: marcar o experimento como revisado/contaminado e exigir novo conjunto final não usado para nova avaliação econômica. Trocar experiment_id ou diretório não torna os mesmos dados intocados.

A verificação de integridade do arquivo completo pode ler seus bytes/validar OHLC antes do congelamento; não deve calcular métricas/sinais/PnL de teste para orientar escolhas. O registro local de uso e a declaração do responsável documentam o processo; software/hash não provam ausência de conhecimento humano prévio. Sem workflow de aprovação adicional: o congelamento é uma operação técnica reproduzível e o teste é uma seleção explícita de segmento.

## 6. Relógio histórico, execução e risco

### 6.1 Decisão e observação posterior

O código da 04 junta decisão e execução numa CYCLE, usa evaluation_type fixture e validade de até 5 s. Não reutilizar esse evento fingindo que um atraso de 15 minutos cabe na validade antiga. Implementar modelo histórico próprio, reutilizando a SMA pura e as transições financeiras, com decisão agendada e admissão financeira separadas.

Para candle t: disponível no fechamento inclusivo +1 ms, coincidente com a abertura nominal do próximo candle. Decisão usa só o prefixo disponível. No cenário-base, referência de execução = open de t+1; disponibilidade sintética dessa referência = abertura nominal de t+1 +1 ms, fill = +2 ms. É convenção de simulação para preservar `decision_at < observed_at <= fill_at`, sem alegar tick/cotação real ou preenchimento no fechamento do sinal. Nunca usar high/low/close futuros para determinar essa execução.

Na variante de atraso de um candle, mesma decisão agenda referência open de t+2, com os mesmos deslocamentos de 1/2 ms. Validade do sinal histórico cobre apenas até abertura agendada +5 s; freshness da observação continua separada, no máximo 5 s entre observação e fill. Não ampliar max_quote_age_ms para 15 minutos nem reexecutar estratégia para escolher retrospectivamente a referência mais favorável.

Decisão direcional guarda alvo, envelope, horário agendado e teto de orçamento calculável com dados da decisão, sem quantidade baseada em preço futuro. Estado SCHEDULED é pendência lógica; não constitui reserva de caixa/ativo ou fill. Uma única pendência por instância/carteira bloqueia novo compromisso; novos sinais durante a espera são registrados, sem substituir silenciosamente o plano ou reenviar cruzamentos depois.

Quando a referência se torna disponível, dimensionar com o menor teto da decisão e orçamento/caixa/risco atuais; normalizar step e revalidar custos/filtros/limites. Só então persistir intenção/plano/reserva atômicos (A) e depois fill (B), com preço agora conhecido pelo replay. Rejeição/missing data/expiração encerra a pendência com motivo; não inventar preço nem aumentar quantidade para atingir mínimo.

Ordem temporal em fronteira de candle: disponibilizar fechamento anterior; DAY_START se novo dia UTC; marcar carteira e avaliar sinal/pendências; disponibilizar open sintético em +1 ms; admitir/reservar/fill em +2 ms. A pendência antiga mantém a prioridade de slot; não gastar o mesmo caixa num sinal novo antes de resolvê-la. O relógio é de eventos, nunca de parede.

### 6.2 Janelas, marcação e custos

Em segmento `[A,B)`, permitir decisões com `A <= as_of < B` e fills somente antes de B. O último candle, disponível em B, serve à marcação terminal e não cria nova ordem. Pendência cujo horário de referência/fill cai fora da janela termina END_OF_WINDOW, sem consultar outro segmento. Não transportar ordem/posição entre segmentos ou usar candle do teste para executar ordem da validação.

DAY_START usa referência de meia-noite já disponível (fechamento anterior sob a convenção histórica), antes das ordens do dia; nunca open/close ainda não disponível. Sem marcação necessária validada, falhar a avaliação, sem inventar baseline. Preservar entrada/exposição 10%, peso 10%, uma posição/pendência, perda diária 1% e drawdown 5%, com overrides somente mais restritivos; sem reset dentro do segmento. SELL de redução respeita dados/inventário/filtros, mesmo sob trava de entrada; trava não liquida automaticamente.

Reutilizar Decimal local precisão 80, quantum BTC/USDT 1e-8, tick adverso, step comum para baixo, notional/taxa arredondados como na 03/04, ledger balanceado por ativo e custo médio incluindo taxa. Taxas só em USDT, sem desconto presumido. Para REFERENCE: metade do spread total por lado + slippage adverso; para BID_ASK histórico válido, spread já embutido, aplicar somente slippage. Histórico apenas OHLC usa proxy de open, identificado como tal; nenhuma garantia de liquidez/fill integral real.

Matriz congelada obrigatória: base 10/10/5 bps; custos dobrados 20/20/10 bps; atraso de um candle com custos-base; custos dobrados + atraso. Não alterar quantidade do caso-base apenas subtraindo taxas: cada variante refaz o dimensionamento causal com o próprio custo, mantendo capital/janela/regras. Não escolher retrospectivamente a variante mais favorável como resultado principal.

Política terminal única nesta Sprint: mark_to_market. Posição restante fica aberta e marcada pelo último fechamento disponível; não criar SELL fictício nem declarar saldo livre como patrimônio. Relatório distingue realizado/não realizado, custo remanescente e ausência de liquidação. Pode mostrar estimativa de custo de encerramento separada, sem posting/fill ou promessa de preço executável.

## 7. Benchmarks e métricas verificáveis

Para cada segmento/variante, comparar curvas independentes com mesmo capital inicial 10000, janela, referência temporal, custos/filtros e política terminal:

- Caixa em USDT, juros zero; explicitar risco da moeda de cotação, sem presumir equivalência garantida a dólar/real.
- Buy-and-hold com orçamento de 100% do capital incluindo taxa, comprado na primeira referência disponível do segmento e mantido até a marcação final.
- Buy-and-hold com orçamento de 10% e caixa residual, para comparação adicional com o teto inicial de capital da SMA.

Benchmarks são políticas de referência fixas, não novos módulos do catálogo. Usam carteiras/ledgers isolados. O perfil buy-and-hold 100% declara limites de entrada/exposição 1 nesse comparador; não oferece bypass ou alteração dos limites da SMA. Todos os fills passam pelos mesmos filtros, caixa, taxas e contabilidade. Falha de admissão é registrada, sem aporte implícito. Não somar capital das curvas nem alegar risco/exposição iguais entre SMA e referência 100%.

| Métrica | Definição exigida |
|---|---|
| Patrimônio E | USDT livre + reservado + BTC total marcado, sem contar reservas duas vezes |
| Retorno líquido | E_final / E_inicial - 1; usar patrimônio, não saldo livre; sem anualização nesta Sprint |
| PnL | Realizado/não realizado e taxas separados, reconciliados com custo e ledger |
| Drawdown máximo observado | Maior `(pico_anterior - E)/pico_anterior`, incluindo E inicial, marcas e fills; não usar só o drawdown final da 04; sem inferência intrabar |
| Exposição média/máxima | Fração marcada por evento; média ponderada pelo tempo em ms, máximo no conjunto de eventos; incluir compromissos sem dupla contagem |
| Tempo em posição | Duração com BTC >0 dividida pela janela; sem contar aquecimento |
| Turnover | Soma dos notionals absolutos de fills BUY e SELL / patrimônio inicial; declarar denominador |
| Operações | Decisões, pendências/expirações, propostas/recusas por motivo, fills, trades encerrados e posição residual; não confundir fills com trades |
| Taxas e impacto | Taxas USDT; impacto adverso do preço contra a referência, com spread/slippage/tick identificados, sem subtrair custos duas vezes do PnL |
| Subperíodos | Resultado/curva por segmento e mês UTC disponível, sem resetar a carteira dentro do segmento ou somar percentuais de forma incorreta |

Comparações de métricas usam Decimal em precisão 80, sem arredondar antes de atualizar pico/máximo. Quantidades/valores contábeis mantêm oito casas; razões derivadas usam strings com arredondamento determinístico documentado (16 casas, ROUND_HALF_EVEN), distinguindo cálculo de apresentação.

Reportar ausência de trades como dado válido; métricas sem denominador/amostra aparecem N/A/null, não como rentabilidade comprovada. Alta/baixa/lateral devem ter cenários sintéticos identificados e análise histórica descritiva sem seleção retroativa de trechos para promover o resultado. Não exigir Sharpe, otimização ou pacote estatístico para concluir o incremento.

## 8. Persistência histórica, escala e recuperação

Não elevar simplesmente a capacidade da fixture 04 nem gravar 70.080 snapshots com todos os candles/ciclos anteriores em StrategyWallet. Manter a interface fixture/schema v2 compatível. Criar store isolado `backtest.sqlite3`, schema inicial `1`, modelo `paper-backtest-v1`, em backtest.data_dir novo; não é migração de paper.sqlite3 ou market.sqlite3.

O store registra protocolo congelado/estado de uso do teste, execuções por segmento/variante/perfil, journal/postings/intents/fills/decisions, agendamentos, checkpoints e curva. Definir DDL/PK/FK/UNIQUE/triggers e documentar antes dos testes persistentes. IDs de execução lógica incluem experimento/segmento/variante/perfil/carteira; run_id operacional é apenas tentativa/exportação. Mesmo conteúdo devolve o confirmado; conteúdo diferente na mesma identidade falha antes de novos efeitos.

Estado de trabalho limitado: janela slow+1 (até 501 fechamentos), patrimônio/posição/custo/risco, pendência atual, acumuladores de métricas, cursor e hash incremental do prefixo. Histórico e intenções terminais ficam em tabelas/arquivos auditáveis, não duplicados integralmente em cada projeção. Reutilizar transições financeiras com estado ativo limitado e arquivo durável de terminais; o índice persistente mantém deduplicação mesmo quando uma intenção sai do estado em memória.

Hash incremental de prefixo deve ser determinístico e independente de dados futuros, com seed/modelo documentados; não recalcular todo o prefixo a cada candle. O identificador de conteúdo de uma decisão é causal; chave persistente também vincula o experimento/variante, sem confundir avaliações independentes. O protocolo preserva hash completo do dataset; os dois hashes têm finalidades diferentes.

Uma transação local confirma cada decisão/estado/cursor/agendamento; A confirma plano/reserva/atribuição; B confirma fill/posição/custos/risco. Não avançar checkpoint antes do commit nem manter transação aberta durante rede/HTML. Lock/CAS e reconciliação de journal/projeções/atribuições continuam obrigatórios. Reconstrução integral em streaming na entrada/final, com validação entre commits do escritor exclusivo; sem replay integral do passado em cada candle.

Morte antes/depois de cada fronteira deixa rollback ou efeito íntegro. Recuperar SCHEDULED no seu relógio congelado; RESERVED com plano/geração/preço já persistidos; FILLED sem nova contabilização. Alteração de fonte/manifesto/protocolo/estado detectada ao retomar bloqueia, sem reset. Corrupção preserva originais e diagnóstico em cópia. Relatório falho é reexportado a partir do banco, sem recalcular sinais ou abrir outro teste final.

Provar leitura e estado limitados com fixture de escala de ao menos 70.080 candles mais warm-up: registrar tempo, pico de memória, tamanho do banco/relatórios e quantidade máxima de elementos do estado. O objetivo é ausência de crescimento quadrático por guardar prefixos completos, não SLA/p95 de produção. Não impor benchmark arbitrário não aferido nem esconder custo em arquivo ignorado.

## 9. Configuração e CLI planejadas

Adicionar tabela backtest e seleção de avaliação backtest, com schema estrito, paths contidos no módulo após symlinks, IDs validados, strings financeiras e rejeição de credenciais/variáveis desconhecidas. Snapshot financeiro/modelo/dataset é imutável após freeze. Não sobrepor paper/strategy/backtest em mesmo diretório. Exemplos abaixo ainda não são aceitos pela CLI atual.

`config/backtest.sma.example.toml`, default desabilitado, para fixture técnica de dez dias; criar arquivo opt-in separado `config/backtest.sma.fixture.toml`, sem alterar o default:

```toml
mode = "PAPER"

[backtest]
experiment_id = "sma-fixture-v1"
environment = "local"
evaluation_type = "backtest"
source_manifests = ["config/fixtures/backtest-sma/manifest.json"]
dataset_dir = "data/backtest-fixture-dataset"
data_dir = "data/backtest-example-v1"
start = "2026-10-01T00:00:00Z"
end = "2026-10-11T00:00:00Z"
initial_usdt = "10000.00"
fee_bps = "10"
spread_bps = "10"
slippage_bps = "5"
max_entry_fraction = "0.10"
max_exposure_fraction = "0.10"
max_daily_loss_fraction = "0.01"
max_drawdown_fraction = "0.05"
max_quote_age_ms = 5000
split_percentages = [60, 20, 20]
variants = ["base", "double_costs", "delay_1candle", "double_costs_delay"]
benchmarks = ["cash", "buy_hold_100pct", "buy_hold_10pct"]
terminal_policy = "mark_to_market"

[modules.trend_btc]
module_id = "trend_sma"
version = "1"
enabled = false
environments = ["local"]
modes = ["PAPER"]
evaluation_types = ["backtest"]
symbols = ["BTCUSDT"]
capital_weight = "0.10"
execution = "immediate"
on_disable = "hold_and_monitor"

[modules.trend_btc.params]
fast_window = 20
slow_window = 50
interval = "15m"

[coordination]
policy = "exclusive_owner"
```

O enum immediate mantém o fill integral quando chega a referência agendada; o atraso histórico pertence ao modelo/variante, não habilita TWAP/VWAP. Fixar os limites de entrada/arquivos da seção 4 no adapter, sem permitir desativá-los por configuração. Datas alinhadas a 15m/UTC, start<end; split exatamente 60/20/20 neste incremento; enums fechados e bool rejeitado como inteiro. Overrides por instância/par continuam somente mais restritivos como na 04.

| Comando futuro | Contrato |
|---|---|
| backtest-prepare --config CAMINHO | Verifica fontes e publica dataset/manifesto, sem PnL ou teste final |
| backtest-freeze --config CAMINHO | Com instância opt-in, sela protocolo completo; idêntico é idempotente, incompatível gera conflito; não avalia estratégia |
| backtest-run --config CAMINHO --segment development\|validation\|test --variant all | Executa/retoma só as variantes congeladas e benchmarks desse segmento; teste exige fases anteriores coerentes; sem habilitados retorna NOOP sem carteira |
| backtest-report --config CAMINHO | Snapshot só leitura, relatório agregado/detalhado; não avalia dados nem cria carteira |
| backtest-reconcile --config CAMINHO | Confere journal/checkpoints/atribuições/métricas e persiste bloqueio quando possível, sem reparo |

Defaults de seleção: segment=development e variant=all; test exige seleção explícita. Sem tabela backtest, backtest-run retorna NOOP; comandos que precisam identificar dataset/experimento falham com configuração ausente. check-config valida estrutura/registro/paths sem preparar dataset, abrir teste ou criar banco. Nenhum backtest-* aceita allow-network, endpoint, credencial, reset ou modo alternativo. Coleta pública separada mantém seu opt-in histórico.

stdout JSON, stderr JSON Lines sanitizados com run_id/UTC/PAPER/orders_sent=0. Estados planejados BACKTEST_NOOP/PREPARED/FROZEN/COMPLETED/REPORTED/RECONCILED/BLOCKED/FAILED; contadores atuais separados dos totais. Códigos 0 sucesso ou resultado financeiro negativo, 2 configuração/dataset inválido, 3 conflito/lock/persistência/protocolo não elegível/publicação/retomada bloqueada, 1 inesperado. Nunca converter erro em retorno de estratégia zero para produzir relatório favorável.

## 10. Fixtures, demonstração e relatórios

Fixture técnica: 960 candles de score (dez dias), mais 50 de warm-up, em 15m; total 1.010, maior que o limite da fixture 04. Split 576/192/192, limites 01→07→09→11/10/2026 00:00 UTC. Usar padrão determinístico de fechamentos: 50 warm-up a 100; em cada um dos dez dias, `[100]×50 + [110] + [100]×45`. Construir OHLC/volumes coerentes e documentar geração, filtros e hashes. Não declarar esses preços como mercado real; fixar contagens/métricas esperadas por cálculo independente antes de comparar o produto.

Casos financeiros pequenos adicionais isolam uma compra/venda com capital 10000, orçamento 10%, referência posterior de compra 110/venda 100, custos 10/10/5 bps, tick 0.01/step 0.000001: quantidade 9.072754 BTC, preços 110.11/99.90, taxas 0.99900095/0.90636813, resultado -94.53818742 e saldo 9905.46181258 USDT. São expectativas herdadas/conferidas, não PnL já obtido pela 05. Acrescentar caso positivo e casos sem cruzamento/sem trade/rejeição/fim de janela.

Publicar por execução e no agregado do experimento: report.json, report.html autocontido, equity.csv, trades.csv, decisions.csv e manifest.json com hashes/modelos/protocolo/fontes. HTML profissional é obrigatório; PDF adicional é permitido quando útil, com revisão visual. Não entregar somente JSONs.

O HTML apresenta resumo, origem e janela/split/warm-up, protocolo congelado/uso do teste final, curvas e drawdown, métricas por segmento/variante/SMA/benchmarks, custos, risco, trades/recusas/posição residual e limitações. Identificar referências 100% versus 10%, resultados esperados/obtidos dos controles sintéticos, amostra curta e filtros proxy. Curvas de avaliações independentes não são somadas; dados reais e fixtures não compartilham rótulo de evidência econômica.

Separar dados completos de apresentação: CSV/JSONL em streaming, HTML com tabelas resumidas e gráfico reduzido por regra determinística, preservando mínimos/máximos e links aos dados completos; não inserir milhões de células/snapshots no DOM. Dados financeiros e métricas oficiais são calculados na série completa, nunca na curva reduzida. Escapar textos/CSP, sem scripts/recursos remotos. Repetição/reexportação mantém hash canônico de resultados, excluindo run_id/timestamp real, e não refaz fills.

## 11. Entregáveis e critérios de aceite

Sequência futura: regressão 04 → fontes/fixture/manifesto → contrato temporal/split/freeze → motor/estado histórico limitado → persistência/recuperação → métricas/benchmarks/variantes → CLI → escala/wheel → avaliação real/relatórios/documentação. Executar o teste final só depois de congelar a versão validada em desenvolvimento/validação.

| Caminhos previstos | Responsabilidade |
|---|---|
| domain/backtest/, application/backtest_*.py e portas | Protocolo, eventos/agendamento, métricas/benchmarks e fluxo histórico causal |
| adapters/backtest_dataset.py e configuração/entrypoints/backtest.py | Leitura limitada, validação, preparo e comandos sem rede |
| adapters/storage/backtest_sqlite.py, backtest_report.py | Store histórico isolado, checkpoints/arquivo de terminais e exportação JSON/HTML/CSV |
| config/backtest.sma.example.toml, backtest.sma.fixture.toml e fixtures de fonte | Default false, opt-in técnico, padrões/controles versionados |
| tests/unit/test_backtest_*.py, tests/integration/test_backtest_*.py; wheel_smoke.py | Causalidade, split/métricas, persistência/crash, isolamento, escala e pacote |
| README/.gitignore; manifest/lock só se necessário | Comandos reais e retenção de evidências sem versionar bancos/datasets operacionais |
| docs/estrategias/trend_sma.md e catálogo | Capacidade histórica/flags/tempo/risco e exemplos atualizados na implementação |
| docs/bancos/backtest-sqlite.md, catálogo e ADR histórico | DDL/modelo real, constraints/diagrama, operação, compatibilidade/rejeição e limites |
| Guia/evidências 05, arquitetura/planejamento e esta especificação | Resultados reais, hashes, relatório legível e decisão dos gates |

Paths de código são internos a modules/trading/src/cripto_bot; config/tests pertencem à aplicação; docs ao workspace. Os arquivos novos só serão criados na implementação. Preferir biblioteca padrão/SQLite/Decimal/Pydantic atuais, sem exigir pandas/NumPy/ORM. Dependência nova exige necessidade concreta, compatibilidade com Python fixado e lock atualizado.

IDs AC01–AC07 preservam os temas do contrato anterior; AC08–AC18 detalham aceite verificável. No detalhamento, todos constavam como não executados; os resultados atuais estão no guia05. Expandir o guia 05 antes dos ensaios, sem reescrever evidências 01–04. M01–M16 aplicam-se no alcance histórico escolhido; capacidades ausentes permanecem inelegíveis com ativação rejeitada.

| ID | Cenário obrigatório | Resultado exigido |
|---|---|---|
| AC01 | Freeze/split/aquecimento e uso do teste | Datas/60-20-20/capital/código/custos definidos antes de PnL; aquecimento sem efeito; teste após dev/val; mudança não reutiliza amostra como intocada |
| AC02 | Prefixo e relógio/fill | Futuro não altera decisão passada; next open com disponibilidade posterior; atraso usa t+2 e validade própria; sem preço futuro no dimensionamento prévio |
| AC03 | Custos/precisão/ledger | 10/10/5 e matriz dobrada, BID_ASK sem spread duplo, tick/step/notional/taxa, dinheiro por ativo e controles aritméticos exatos |
| AC04 | Repetição/dados inválidos | Hashes/versões/resultado estáveis, zero efeitos duplicados; gap/float/bool/NaN/CRC/hash/schema/proveniência conflitantes rejeitados |
| AC05 | OOS/benchmarks/sensibilidade | Teste final separado, caixa/BH100/BH10, quatro variantes, subperíodos/regimes/posição residual e limitações explícitas |
| AC06 | Isolamento | Backtest sem HTTP/credencial/privado/AWS; guard em pytest/filhos/wheel; coleta pública só pelo comando separado explícito |
| AC07 | Módulo/composição/capital | SMA opt-in isolada, mesmas janelas/custos/capital; atribuição reconciliada; múltiplos donos/combinações não suportadas rejeitados |
| AC08 | Regressão/defaults | Contratos 01–04 preservados; backtest sem habilitados NOOP, capacidades não herdadas e configuração estrita |
| AC09 | Fronteiras de segmentos | Nenhuma ordem cruza partição; prefixo só aquece; último candle marca sem nova decisão, sem liquidação implícita |
| AC10 | Pendência e risco | SCHEDULED não reserva caixa em dobro; uma pendência; admissão revalidada no evento, expiração/ausência sem fill inventado; limites e travas persistem |
| AC11 | UTC e métricas | DAY_START antes de decisão/fill do novo dia, baseline causal; retorno/equity/MDD/tempo/exposição/turnover por fórmulas e série completa |
| AC12 | Crash/reinício | Morte real antes/depois de decisão/agendamento/A/B/checkpoint/publicação; rollback ou recuperação única, sem perda/duplo efeito |
| AC13 | Concorrência/corrupção | Lock/CAS, índice de deduplicação de terminais, dados/protocolo alterados na retomada bloqueados, divergência durável sem reparo por diferença |
| AC14 | Escala e compatibilidade | Pelo menos 70.080+50 candles em teste, estado limitado e medição de tempo/memória/tamanho; stores antigos preservados, sem migração implícita |
| AC15 | Relatório/auditoria | HTML/JSON/CSV/manifesto conferidos, gráfico não altera métricas, expected/obtained e revisão visual; reexportação só leitura sem reabrir teste |
| AC16 | Qualidade e wheel | Ruff/formatação/mypy strict/pytest com branches/build e wheel neutro aprovados, origem site-packages/guard e versões/hashes registrados |
| AC17 | Documentação incremental | trend_sma/catálogo, banco/DDL/pragmas/diagrama/catálogo/ADR e exemplos coerentes; pendência documental bloqueia conclusão |
| AC18 | Avaliação e decisão | Dataset real verificado ou pendência explícita; resultados não promovem LIVE; zero bypass/duplicação/saldo negativo/divergência inexplicada |

Cobrir inclusive zero trades, dataset constante, gaps, igualdade de médias, cruzamento no limite de split, última referência ausente, preço inválido, custo que inviabiliza mínimo/entrada, retorno negativo e ganho aparente apenas por não contabilizar taxa/posição residual. Mortes de processo e corrupção só em fixtures/cópias identificadas; testar invariantes e valores calculados independentemente, não apenas a forma de chamar a implementação.

### Comandos previstos no detalhamento e implementados nesta execução

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked --group dev
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy modules/trading/src
uv run --locked pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
uv build
uv run --locked cripto-bot check-config --config config/backtest.sma.example.toml
uv run --locked cripto-bot backtest-run --config config/backtest.sma.example.toml --segment development --variant all
uv run --locked cripto-bot backtest-prepare --config config/backtest.sma.fixture.toml
uv run --locked cripto-bot backtest-freeze --config config/backtest.sma.fixture.toml
uv run --locked cripto-bot backtest-run --config config/backtest.sma.fixture.toml --segment development --variant all
uv run --locked cripto-bot backtest-run --config config/backtest.sma.fixture.toml --segment validation --variant all
uv run --locked cripto-bot backtest-run --config config/backtest.sma.fixture.toml --segment test --variant all
uv run --locked cripto-bot backtest-reconcile --config config/backtest.sma.fixture.toml
uv run --locked cripto-bot backtest-report --config config/backtest.sma.fixture.toml
uv run --locked cripto-bot backtest-run --config config/backtest.sma.fixture.toml --segment test --variant all
uv run --locked python tests/wheel_smoke.py
```

Repetir o protocolo em configuração/diretório próprios para histórico real, somente depois de verificar os dados e congelar datas efetivas; o exemplo acima é sintético. Wheel deve ser reinstalado em ambiente separado, cwd neutro sem PYTHONPATH, paths absolutos, origem em site-packages e guard comprovado. Registrar os comandos reais/exit codes, SHA do artefato e default/prepare/freeze/segmentos/report/replay, preservando smoke histórico.

## 12. Evidências, custos e conclusão

Guia/JSON 05 registram base e revisões efetivas dos dois repositórios, ferramentas/lock/wheel, hashes dos fontes/datasets/configuração/protocolo/modelo, datas e natureza real/fixture, comandos/saídas sanitizadas, AC/M aplicáveis, cobertura/lacunas, tempos/memória, fontes/preparo e resultado de cada segmento/variante/benchmark. Separar efeito novo, histórico e reprodução; não duplicar snapshots completos no JSON central quando arquivos com hashes podem preservar a evidência integral.

Falha de dado/protocolo preserva artefatos e impede novos compromissos; falha financeira exige reconciliação, sem excluir lançamentos ou ajustar critérios para passar. Recuperar execução confirmada pelo checkpoint/modelo, nunca pela configuração nova incompatível. Falha de HTML/CSV permite reexportar de snapshot, sem reset de capital ou teste final. Sem migração entre bancos; backup consistente/pausa e diagnóstico em cópia antes de qualquer recuperação manual futura.

Custo AWS zero; sem capital/taxas reais. CPU/disco locais e eventual rede de dados públicos na preparação explícita. Estimativa orientativa 5–8 dias úteis, revisável após medir streaming/recuperação; volume/limites de coleta e disponibilidade podem ampliar a avaliação. Ignorar dados/bancos/locks/relatórios operacionais, preservar fixtures/TOMLs/manifestos/evidências selecionadas. Limpeza somente de artefatos sintéticos identificados, sem apagar perdas ou histórico.

Concluir a Sprint apenas com todos os critérios obrigatórios aprovados, relatório fora da amostra de dados históricos reais identificado/reproduzível e documentação atualizada. Lucro não é requisito de engenharia; amostra curta/resultado negativo mantém as limitações econômicas explícitas, sem liberar LIVE. Se dados reais estiverem indisponíveis, concluir o trabalho independente de software/testes e registrar aceite parcial de infraestrutura + avaliação/gate PENDENTES, sem declarar a Sprint concluída nem detalhar a 06 como liberada. Meta de 24 meses pode ser ajustada antes do freeze por disponibilidade documentada; não ocultar amostra curta.

## 13. Prompt autossuficiente para implementação futura

```text
Implemente somente a Sprint 05 — Backtesting e avaliação fora da amostra,
conforme docs/sprints/sprint-05.md integralmente.

Workspace /home/cams7/Dev/Cripto; raiz Python/uv/aplicação:
/home/cams7/Dev/Cripto/cripto-bot. Docs/Git independente:
/home/cams7/Dev/Cripto/docs. Paths docs/... são do workspace; código/config/
testes pertencem à aplicação. Preserve alterações/históricos/carteiras;
não altere projetos de referência ou leia credenciais.

Leia instruções locais, planejamento (4.6–4.9, 6.2–6.4, 9, 10 e 13), Sprint 04,
seu guia/evidências, arquitetura modular, trend_sma, bancos/ADR 0005 e matriz
modular. Inspecione configuração/flags, pure SMA, ciclos/TTL/fixture limitada,
redução financeira, stores v1/v2, relatórios, CLI/manifest/lock/testes.

Pré-requisitos: (1) 04 revista/hashes conferidos e regressão reproduzida,
(2) Python/uv/dependências/permissões confirmados, (3) dados reais/fixture
separados e plano de preparo, (4) compatibilidade financeira/temporal e limites
de estado compreendidos. Os 428 testes são históricos. Falha bloqueia trabalho
dependente, com PENDENTE no guia 05. Reconfirme APIs/fontes oficiais utilizadas.

Somente PAPER/local/backtest/BTCUSDT/15m, SMA20/50 opt-in e exclusive_owner.
Não implemente outro módulo, composição, modo privado, AWS, daemon, notificação,
short ou fill parcial real. Preserve todos os comandos/configs/resultados
01–04 e defaults false; não aumente simplesmente o limite de fixture da 04.

Prepare dataset via manifestos/exportações locais, streaming limitado e hashes/
qualidade/continuidade/proveniência antes de efeitos. Se for necessária coleta,
use só collect-market público existente, separadamente, com allow-network
explícito, limites/checkpoints/GETs permitidos, sem credencial ou contorno de
restrição. O motor histórico nunca faz rede. Ausência de histórico real não
pode ser mascarada por fixture; registre a avaliação/gate PENDENTES e complete
o software/testes independentes. Não afirme coleta inexistente.

Janela ideal 24 meses, referência 25/10/2024 a 25/10/2026 UTC, 70080 candles
mais warm-up. Verifique disponibilidade; ajuste datas antes de freeze se
necessário, com motivo/amostra curta. Split 60/20/20 por candles de score,
50 anteriores só aquecem nos defaults. Cada segmento/variante/benchmark inicia
capital independente 10000 USDT; não carregar posição/PnL ou somar curvas.

Congele dataset/datas/código/params/flags/risco/custos/modelo/métricas/benchmarks
antes do PnL. Execute development/validation antes de test; registre primeiro
uso final. Rerun igual é reprodução sem efeitos; mudança material não torna
o mesmo teste intocado por trocar ID. Sem otimização automática.

Use SMA e financeiro compartilhados, mas novo modelo histórico de eventos:
decisão no fechamento disponível, referência open t+1 observável +1ms e fill
+2ms; atraso 1 candle usa t+2. Hipótese sintética, sem fill no close decisor
ou preços futuros no orçamento. SCHEDULED é slot lógico, não reserva; admissão
atômica com preço conhecido/risco atualizado, depois fill em outra transação.
Validade histórica cobre horário agendado +5s; freshness da observação segue
5s, sem ampliar TTL da fixture. Um pendente bloqueia novo compromisso. Não
cruzar partições, negociar aquecimento ou inventar fill na última referência.
DAY_START usa dado disponível à meia-noite antes das ordens, sem reset de perda
ou drawdown dentro do segmento. Terminal mark_to_market, sem SELL implícito.

Matriz fixa: base10/10/5bps, custos20/20/10, atraso1candle e combinado. Decimal
local80, quantum1e-8, tick/step/taxas/filtros/ledger como 03/04; no BID_ASK não
duplicar spread. Filtros históricos ausentes viram proxy declarado, sem buscar
regras atuais no replay. Risco/atribuição sem bypass ou capital duplicado.

Benchmarks caixa/BH100/BH10 em carteiras isoladas, mesmas datas/custos/terminal.
BH100 é perfil de referência com orçamento/limites próprios, nunca bypass
para SMA. Calcule E/retorno/PnL/MDD desde pico inicial, exposição ponderada pelo
tempo, tempo em posição, turnover, trades/fills/recusas/custos/subperíodos na
série completa. Sem trades ou denominador válido: N/A, sem anualização.

Crie backtest.sqlite3 schema1/modelo paper-backtest-v1 em diretório novo,
sem converter paper/market. Journal/projeções/checkpoints/agendamentos e arquivo
de intenções terminais preservam deduplicação. Estado limitado à janela,
financeiro/risco/pendência/acumuladores/hash incremental; não duplicar prefixos
completos nem replay do passado a cada candle. A/B/checkpoint e gerações sob
lock/CAS; retome plano confirmado no relógio congelado. Reconcile inicial/final
streaming, detecte corrupção/mudança de dados/protocolo, sem correção/reset.

Implemente backtest-prepare/freeze/run/report/reconcile e TOMLs/fixtures da
seção 9; argumentos/estados/exit codes conforme contrato, sem rede/credenciais.
Fixture técnica1010 candles, split576/192/192 e controles financeiros exatos;
escala >=70080+50 com tempo/memória/tamanho/estado máximo registrados.
Execute AC01–AC18 e M aplicáveis, regressão, causality/prefixo/split/UTC/
benchmarks/métricas/risco, mortes reais nos commits, corrupção/lock/CAS,
publicação e guards nos filhos. Expanda guia 05 antes de registrar resultados.

Rode uv sync --locked --group dev, Ruff check/format --check, mypy strict,
pytest com branches, uv build, comandos default/prepare/freeze/dev/val/test/
reconcile/report/replay. Verifique wheel reinstalado em ambiente separado/cwd
neutro/site-packages, sem PYTHONPATH, paths absolutos, hashes e guard testado.

Gere HTML profissional/JSON/CSV/manifesto por execução e agregado, sem calcular
métricas na curva reduzida do gráfico. Confira dados e revisão visual; PDF é
adicional se útil. Report é snapshot só leitura, sem novos sinais/fills/teste.
Na mesma entrega atualize trend_sma/catálogo, crie documento de banco histórico
com DDL/diagrama/pragmas/constraints/compatibilidade/recuperação e catálogo/ADR;
README/arquitetura/planejamento/especificação e guia/evidências05 com esperado/
obtido, revisões/versões/hashes, cobertura/lacunas, custos e limitações.
Não altere evidências01–04. Sem critérios/documentos/dados necessários,
PENDENTE, sem declarar aprovação pela fixture. Lucro não é gate de engenharia.
Não inicie06, faça commit/deploy/publique remotos ou envie mensagens/ordens.
```

## 14. Fontes e registro desta atualização

Fontes oficiais consultadas em 25/10/2026: [Binance — dados públicos/kline](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market), para distinguir OHLC histórico de execução/cotação; [Decimal](https://docs.python.org/3.13/library/decimal.html), [sqlite3/transações](https://docs.python.org/3.13/library/sqlite3.html#transaction-control) e [deque](https://docs.python.org/3.13/library/collections.html#collections.deque), para precisão, atomicidade e janela limitada. Reconfirmar contratos/versionamento antes da implementação; nenhuma nova dependência obrigatória ou API privada é introduzida.

Splits, custos, disponibilidade +1/+2ms, benchmarks, agendamento, nomes de CLI/schema e gates são decisões do projeto; não são garantias de execução Binance. Nesta revisão foram lidos planejamento/entrega 04/guia/evidências e componentes pertinentes de configuração, fixture, relógio/motor e módulos; conferidos 87 hashes e calculadas datas/contagens de split. Alterado somente este documento. Nenhum teste de aplicação, backtest, coleta, abertura/migração de banco, implementação ou relatório operacional foi executado. Esse era o estado do detalhamento; o aceite atual está na seção 15.

## 15. Registro da execução em 25/10/2026

O prompt 13 foi executado por solicitação posterior ao detalhamento. O caminho histórico isolado avaliou 24 meses de dados públicos: 70.080 candles de score e 50 de aquecimento, com protocolo congelado e 48 curvas independentes. Desenvolvimento e validação precederam o teste final. Relatórios HTML/JSON/CSV/manifestos e os dois PDFs foram conferidos; a reprodução retornou o mesmo hash e zero novos fills.

Os critérios AC01–AC18 foram aprovados no alcance do [guia 05](../testes/sprint-05-validacao.md), que registra hashes, custos, limitações, cobertura e evidências observadas. A SMA no cenário-base do teste final terminou com 9.494,48742537 USDT fictícios, retorno líquido de −5,0551%; lucro não foi critério de aceite de engenharia. O registro anterior desta especificação descreve o estado do detalhamento.

O núcleo financeiro/SMA e os contratos das Sprints 01–04 foram preservados. O novo `backtest.sqlite3`, schema 1, mantém ledger, atribuição e checkpoints auditáveis, com estado limitado e sem migração dos bancos anteriores. Foram ensaiadas recuperação de agendamento/reserva/fill e falhas de publicação. Execução contínua, módulos futuros e modos privados continuam inelegíveis. A Sprint 06 não foi iniciada; não houve commit ou deploy.


## 16. Ajuste analítico posterior — DuckDB + Parquet

Por solicitação posterior à entrega original, a aplicação acrescenta DuckDB 1.5.6 embutido e séries Parquet ZSTD às exportações do backtest. O SQLite continua como ledger, com schema, transações e recuperação preservados. Catálogo, tipos, validação de contagens, falhas e exemplos estão no [documento analítico](../bancos/backtest-analytics.md) e na [ADR 0007](../decisoes/0007-duckdb-parquet-analitico.md). O [guia complementar](../testes/duckdb-parquet-validacao.md) registra a versão/testes atuais e a reexportação em leitura; não substitui as evidências da avaliação original nem reabre o teste final. Este ajuste não inicia a Sprint 06.
