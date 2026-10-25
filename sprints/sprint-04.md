# Sprint 04 — Base modular, flags, coordenação, risco e tendência SMA

Data do detalhamento: 25/10/2026.

**Estado: IMPLEMENTADA e APROVADA na validação local offline em 25/10/2026, AC01–AC18.** Registro de execução na seção 15 e resultados no [guia 04](../testes/sprint-04-validacao.md). O detalhamento original, preservado abaixo, estabeleceu os contratos executados. A revisão documental das evidências da Sprint 03 foi realizada para este detalhamento. Os 40 hashes de fontes/configuração/manifest/lock/pin Python conferem com a aplicação consultada. A suíte anterior não foi repetida. O detalhamento original autorizou somente documentação; a implementação foi posteriormente solicitada e executada pelo responsável. Comandos/componentes descritos abaixo foram entregues no alcance registrado na seção 15.

Referências principais: [planejamento](../planejamento.md), especialmente seções 4.6–4.9, 6, 9, 10 e 13; [Sprint 03](sprint-03.md), incluindo o registro de execução; [guia 03](../testes/sprint-03-validacao.md) e [evidências 03](../testes/sprint-03-evidencias.json). Complementos: [arquitetura modular](../arquitetura-modular.md), [matriz modular](../testes/estrategias-modulares-validacao.md), [catálogo de estratégias](../estrategias/README.md), [catálogo de bancos](../bancos/README.md) e [ADR 0004](../decisoes/0004-carteira-paper-e-ledger.md).

## 1. Objetivo e incremento demonstrável

Implementar a base mínima de módulos Python e a primeira estratégia `trend_sma`, comprada ou em caixa, em `BTCUSDT`/`15m`. A estratégia calcula SMA20/SMA50 sobre candles fechados e propõe uma decisão explicada; coordenador, dimensionamento, risco, reservas e executor PAPER continuam separados e obrigatórios.

A demonstração terá três execuções: configuração padrão desabilitada, com zero intenções; configuração explicitamente habilitada, com cruzamentos de alta/baixa e dois fills simulados; repetição dessa configuração na mesma carteira, sem novas intenções, fills, taxas ou postings. Produzir evidências JSON e relatório legível que mostre candles, médias, decisões, custos, risco e reconciliação.

Esse replay curto é um teste funcional determinístico da integração. Avaliação histórica com split temporal, benchmarks e teste fora da amostra pertence à Sprint 05; processamento contínuo e modelos de fill parcial/atrasado/ausente pertencem à Sprint 06. Não atribuir validade econômica ao saldo da fixture.

## 2. Diretórios, base inspecionada e pré-requisitos

- Workspace: `/home/cams7/Dev/Cripto`.
- Aplicação e raiz dos comandos Python/uv: `/home/cams7/Dev/Cripto/cripto-bot`.
- Documentação central: `/home/cams7/Dev/Cripto/docs`, com Git independente.
- Pacote existente: `modules/trading/src/cripto_bot`, relativo à aplicação.

Subpacotes novos pertencem ao módulo existente; não criar outro repositório para a SMA ou coordenador. Módulos independentes futuros seguem a organização do planejamento. Preservar alterações anteriores, bancos e relatórios históricos.

| Dependência | Constatação em 25/10/2026 | Condição antes de implementar |
|---|---|---|
| D01 — Entrega 03 | Guia/evidências registram AC01–AC18 aprovados, 316 testes, cobertura combinada 98,12%, qualidade/build/wheel | Reproduzir regressão pertinente e registrar resultado atual |
| D02 — Integridade | 40/40 hashes de `source_sha256` conferem; nenhuma divergência | Reinspecionar divergências posteriores antes de trabalho dependente |
| D03 — Revisões | Aplicação `35be28620f4b099352e2fcffa721c7ab8c52c389`; docs `cc78f4c4b751b1a533a7c8a6f7157eb02b48589a`; sem alterações locais no início | Registrar revisões/estado efetivos, sem presumir instalação idêntica ao checkout |
| D04 — Ferramentas | Pin Python `3.13.15`, uv `0.12.19`, dependências e ferramentas definidas em manifest/lock | Confirmar versões/permissões; não atualizar dependências sem necessidade |
| D05 — Persistência | Mercado/carteira em SQLite v1 separado; adapters rejeitam schemas adicionais/incompatíveis; não há migração implementada | Aplicar compatibilidade da seção 8, sem alterar bases existentes |
| D06 — Dados | Demonstração 02 tem dois candles; demonstração 03 é roteiro manual sem sinais | Criar fixture própria com ao menos 71 candles; os dados antigos não bastam para SMA20/50 |
| D07 — Isolamento | Fluxo financeiro atual é offline, com guards e sem executor privado | Preservar nos novos comandos/subprocessos |

A revisão dos hashes/documentos não revalida o banco operacional ou o wheel instalado. Não há bloqueio conhecido para este detalhamento. Se um pré-requisito falhar na execução, registrar PENDENTE no [guia 04](../testes/sprint-04-validacao.md), preservar diagnóstico e interromper o trabalho dependente.

## 3. Escopo e limites

Incluído: registro estático, `ModuleDescriptor`, DTOs/Protocols mínimos, configuração TOML validada, flags por escopo, snapshot/geração, ciclo determinístico, SMA, coordenador `exclusive_owner`, atribuição por instância, risco global/instância/par, persistência transacional de decisões/estado e relatórios derivados. Conflitos usam módulos fake, sem exigir outra estratégia implementada.

Somente `PAPER`, ambiente `local`, par `BTCUSDT`, intervalo `15m` e avaliação `fixture` neste incremento. `fixture` identifica o ensaio offline; não cria outro modo financeiro. Habilitação futura de `backtest`/`continuous` exige as respectivas Sprints/evidências; exemplos gerais da arquitetura modular não são capacidades já implementadas.

Excluídos: outros módulos do catálogo, multiativo/subcarteiras concorrentes, `weighted_targets`, `segregated_budgets`, TWAP/VWAP, imports dinâmicos/plugins, otimização, backtest completo, daemon/agendamento, coleta durante execução da estratégia, rede privada, AWS, notificações, credenciais, DEMO/TESTNET/LIVE, margem/short/alavancagem, aportes e liquidação automática. Reutilizar fill integral determinístico e taxas em USDT; não antecipar OMS remoto completo.

`run-once` permanece NOOP; `paper-run` mantém o roteiro manual da 03. Configurações antigas, códigos de saída, opt-in de rede de `collect-market` e resultados financeiros históricos mantêm seus contratos. Nenhum desses comandos ativa SMA implicitamente.

## 4. Contratos e fluxo entre componentes

Fluxo: fixture validada → snapshot temporal → módulo habilitado → decisão → coordenador → dimensionamento/risco → reserva persistida → fill PAPER → atualização/atribuição → reconciliação → relatórios. HOLD não cria intenção financeira.

| Componente | Contrato mínimo |
|---|---|
| `ModuleDescriptor` | ID/versão/tipo, schemas de parâmetros/estado, capacidades, dependências, escopos e recursos exclusivos; registro fechado com `trend_sma` versão `1` |
| `Strategy.evaluate` | Snapshot imutável, parâmetros e estado anterior → `Decision` e novo estado; sem HTTP, banco, reserva ou cliente de execução |
| `Decision` | HOLD, alvo comprado ou alvo caixa, motivo, médias anterior/atual, candle, validade e envelope; sem ordem irrestrita |
| `Coordinator.resolve` | Decisões e versão de snapshot/configuração → plano atribuído ou recusa; política única `exclusive_owner` |
| Dimensionamento / `RiskPolicy.assess` | Alvo, orçamento, carteira/pendências e regras → quantidade inicial e admissão; sem bypass por flag |
| Portas de estado e execução | CAS, identidade durável, reserva e fill por plano puro/local; reaproveitar contabilidade/execução da 03 |

Implementar somente contratos utilizados. Protocolos de fonte, alocação e algoritmos do catálogo continuam como desenho; não criar classes/adapters vazios para eles. Protocol auxilia tipagem, mas não substitui validação nas fronteiras.

Envelope obrigatório em decisão, intenção e fill: `decision_id`, `module_id`, `instance_id`, versão da implementação/schema, `config_hash`, `config_generation`, `state_version`, ambiente, modo, tipo de avaliação, carteira, símbolo/intervalo, `dataset_id`, hash do prefixo utilizado, `as_of`/`valid_until`, candle e motivo. Relacionar fill/intenção à decisão/atribuição; `run_id` não substitui identidade de negócio.

## 5. Configuração, flags e CLI planejadas

### 5.1 Contrato TOML

Adicionar tabelas opcionais `strategy`, `modules` e `coordination`; ausência de módulos habilitados equivale a desativação global. Schema estrito, rejeitando campos desconhecidos, credenciais e variáveis `CRIPTO_BOT_*` não permitidas. O override existente de modo não oculta erro de arquivo. Nenhum endpoint, import Python ou executor arbitrário é configurável.

Exemplo futuro `config/strategy.sma.example.toml`, desabilitado por padrão:

```toml
mode = "PAPER"

[strategy]
environment = "local"
evaluation_type = "fixture"
wallet_id = "sma-demo"
data_dir = "data/sma-demo"
fixture_file = "config/fixtures/strategy-sma-crossings.json"
initial_usdt = "10000.00"
fee_bps = "10"
spread_bps = "10"
slippage_bps = "5"
max_entry_fraction = "0.10"
max_exposure_fraction = "0.10"
max_daily_loss_fraction = "0.01"
max_drawdown_fraction = "0.05"
max_quote_age_ms = 5000

[modules.trend_btc]
module_id = "trend_sma"
version = "1"
enabled = false
environments = ["local"]
modes = ["PAPER"]
evaluation_types = ["fixture"]
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

Valores financeiros seguem strings decimais finitas, até 18 dígitos inteiros/oito fracionários, sem expoente. Bps/frações e IDs seguem restrições da 03. Pesos positivos até 1, soma dos habilitados ≤1; orçamento não utilizado fica em caixa. Janelas inteiras estritas, `1 <= fast_window < slow_window <= 500`, nunca bool; defaults 20/50. Warm-up mínimo = `slow_window + 1`, derivado e não reduzível. Criar `config/strategy.sma.fixture.toml` separado com opt-in true e diretório próprio; não mudar o default de instalação.

Ativação exige enabled e correspondência explícita de todas as listas de ambiente/modo/avaliação/par; lista ausente/vazia não concede permissão e wildcard não é aceito. Escopos sem capacidade no descriptor falham antes de efeitos. Rejeitar módulo habilitado sem implementação, dependência ausente/cíclica, versão/params inválidos, recurso disputado ou política não suportada. Item de catálogo desabilitado não exige importar bibliotecas futuras; ativação não implementada é rejeitada.

O perfil inicial herda limites globais da 03. Overrides opcionais ficam em `[modules.trend_btc.limits]` e `[coordination.symbol_limits.BTCUSDT]`, aceitando somente `max_entry_fraction`, `max_exposure_fraction`, `max_daily_loss_fraction` e `max_drawdown_fraction`, com os mesmos tipos/domínios e valores menores ou iguais aos globais. Ausência herda o global, sem desativá-lo; proibir campos desconhecidos e overrides de outro par. No piloto com proprietário exclusivo, as frações conservam os denominadores da carteira global da 03 (patrimônio, baseline diário e pico); o orçamento da instância limita adicionalmente seu uso de capital. Não introduzir um baseline inicial fictício independente por instância. Validar todos os overrides antes de abrir carteira para escrita e cobrir exemplos nos testes/documentação.

Resolver paths pelo cwd, exigir contenção no módulo após symlinks. Banco, lock, fixture e relatório não podem escapar. Quando `paper` e `strategy` coexistirem, selecionar fluxo explicitamente pelo comando; rejeitar compartilhamento de diretório financeiro entre modelos.

### 5.2 Comandos a implementar

| Comando futuro | Comportamento exigido |
|---|---|
| `cripto-bot strategy-run --config CAMINHO` | Valida configuração/fixture; sem habilitados e sem carteira, retorna NOOP sem criar carteira/intenção; com opt-in, reconcilia, recupera e processa ciclos novos |
| `cripto-bot strategy-report --config CAMINHO` | Snapshot somente leitura de carteira existente/decisões/atribuições; JSON em stdout e exportação JSON/HTML derivada, sem criar carteira ou operações |
| `cripto-bot strategy-reconcile --config CAMINHO` | Reconstrói financeiro/modular; persiste bloqueio quando possível, sem corrigir por diferença |

Nenhum aceita `--allow-network`, host, credencial, reset ou modo alternativo. `check-config` valida schema/paths/registro sem inicializar banco ou ler toda fixture. Ramo sem módulos habilitados pode dispensar leitura de mercado; carteira modular existente continua reconciliada/monitorada mesmo com flag false, conforme seção 9.

stdout: um JSON; stderr: eventos JSON Lines sanitizados com UTC, run_id, PAPER e `orders_sent=0`. Estados: `STRATEGY_NOOP`, `STRATEGY_COMPLETED`, `STRATEGY_REPORTED`, `STRATEGY_RECONCILED`, `STRATEGY_BLOCKED`/`STRATEGY_FAILED`. Separar contadores novos de ciclos/decisões/fills/rejeições/replays dos totais históricos. HOLD/rejeição não são fill. Códigos: 0 sucesso/rejeição de negócio esperada; 2 configuração/fixture inválida; 3 persistência, lock, contexto incompatível, divergência ou publicação falha; 1 falha interna inesperada.

## 6. Dados, relógio, SMA e exemplo verificável

### 6.1 Fixture e causalidade

Fixture JSON versionada com `dataset_id`, símbolo/intervalo, regras sintéticas, candles OHLCV fechados, observações de execução identificadas e marcações/baselines DAY_START. Reutilizar modelos/validações de mercado por adapter offline; não construir `PublicSource` nem consultar `exchangeInfo`. Limitar entrada a 4 MiB, 1.000 candles e 1.000 observações/eventos auxiliares. Ela não contém ordens BUY/SELL roteirizadas: estas resultam da SMA.

Rejeitar antes de efeitos: JSON/tipos/IDs inválidos, duplicatas conflitantes, lacunas, desordem, OHLC incoerente, volume negativo, timestamps naive, candle aberto, outro par ou regras incompatíveis. Cada candle tem abertura, fechamento e disponibilidade. Para `15m`, fechamento inclusivo = abertura + 900.000 ms - 1 ms; primeira disponibilidade = fechamento + 1 ms. Decidir em `as_of` igual ou posterior à disponibilidade, nunca com candle aberto.

O domínio recebe só o prefixo disponível em `as_of`; o financeiro usa relógio de replay, sem `datetime.now()`. Observações de execução não entram na estratégia. Exigir `decision_at < observed_at <= fill_at`, preço fresco até 5 s, sem fill no fechamento da decisão. Sem cotação posterior válida, registrar sinal não executado/motivo; não buscar rede nem inventar preço. DAY_START inicializa dia UTC antes das ordens; marcação/risco e travas persistentes seguem a 03.

Hash completo identifica dataset no manifesto; cada decisão registra hash do prefixo consumido. Acrescentar candles futuros não pode alterar valores, motivos ou identidades de decisões passadas. Não usar hash do arquivo completo na chave de ciclo já confirmado. Snapshot de carteira usa apenas marcas disponíveis naquele instante.

### 6.2 Regras exatas e dimensionamento

Médias aritméticas dos fechamentos com Decimal em `localcontext(prec=80)`. Comparar valores internos sem arredondar para apresentação. Registrar representação determinística das médias, distinguindo-a dos valores financeiros de oito casas. Sem float ou mudança de contexto global.

- Antes de 51 fechamentos válidos nos defaults: HOLD/`WARMUP`, sem intenção.
- Alta: `fast[t-1] <= slow[t-1]` e `fast[t] > slow[t]`. Em caixa, propor alvo comprado limitado pelo orçamento; com posição, HOLD sem pirâmide.
- Baixa: `fast[t-1] >= slow[t-1]` e `fast[t] < slow[t]`. Propor alvo caixa vendendo só BTC livre atribuído à instância; sem BTC, HOLD.
- Igualdade atual não cruza; sem cruzamento, HOLD. Rejeição/falta de preço não reenvia o cruzamento em candle posterior; novo sinal exige novo cruzamento elegível.

BUY: orçamento = menor entre caixa disponível, orçamento da instância e limites globais/instância/par de entrada/exposição, considerando posições e reservas uma vez. Com preço de fill sintético e taxa, calcular quantidade inicial, normalizar para baixo no step comum e revalidar reserva/filtros/limites após arredondar. Plano que excede limite é rejeitado, sem redução silenciosa de intenção já fixada. SELL encerra inventário próprio livre, sujeito a filtros; notional mínimo não atendido gera recusa, sem aumentar quantidade.

### 6.3 Demonstração funcional com perda financeira esperada

Fixture: 71 candles contíguos de 01/10/2026, começando às 00:00 UTC, com fechamentos `[100] × 50 + [110] + [100] × 20`. Definir open/high/low/volume coerentes e regras sintéticas tick `0.01`, steps `0.000001`, mínimo de notional `10`, com o subconjunto de filtros da 03. DAY_START às 00:00, patrimônio inicial 10000 e referência 100. Atualizar marcação sem dados futuros.

| Ponto | Esperado, ainda não executado |
|---|---|
| Candle 50 | HOLD/WARMUP; não há duas janelas consecutivas completas |
| Candle 51, disponível 12:45 UTC | Médias anteriores 100/100; atuais 100.5/100.2; alta |
| Candles 52–70 | Sem novo cruzamento/compra adicional |
| Candle 71, disponível 17:45 UTC | Médias anteriores 100.5/100.2; atuais 100/100.2; baixa |
| Observações/fills | BUY REFERENCE 110 às 12:45:01, fill 12:45:01.001; SELL REFERENCE 100 às 17:45:01, fill 17:45:01.001; UTC |

Com capital/peso/limites do exemplo e custos 10/10/5 bps, orçamento inicial = 1000 USDT. Quantidade inicial = orçamento / (preço final de compra × (1 + taxa)), depois normalizar por step e revalidar. Valores conferidos somente com Decimal no detalhamento; não são evidências de execução da 04.

| Resultado financeiro esperado | Valor |
|---|---|
| BTC comprado e depois vendido | `9.07275400` |
| Preço final BUY / SELL USDT/BTC | `110.11000000` / `99.90000000` |
| Notional BUY / taxa BUY USDT | `999.00094294` / `0.99900095` |
| Custo da posição após BUY USDT | `999.99994389` |
| Notional SELL / taxa SELL USDT | `906.36812460` / `0.90636813` |
| Taxas totais USDT | `1.90536908` |
| Realizado líquido USDT | `-94.53818742` |
| Saldo final USDT; BTC/reservas/custo zerados | `9905.46181258` |

Primeira passagem: 71 avaliações, 50 HOLD/WARMUP, 19 outros HOLD, 2 decisões direcionais, 2 fills e nenhuma rejeição. Não incluir inicialização/DAY_START na contagem de avaliações. Replay: zero novos ciclos financeiros/intenções/fills, mesmo hash financeiro e estado modular. Testar também fixture de resultado positivo, fronteiras de risco, baixa sem posição e observação ausente/vencida; não exigir lucro para aprovar engenharia.

## 7. Coordenação, atribuição e risco obrigatório

`exclusive_owner` admite uma instância proprietária do par/carteira. Duas habilitadas disputando o recurso invalidam a configuração integralmente. Nos testes com fakes, usar ordem estável de IDs, rejeitar disputa independentemente da chegada e serializar reserva por lock/CAS. Isso valida o limite do coordenador, sem aprovar combinações futuras de módulos reais.

Peso é teto, não aporte. Posição e custos pertencem à instância que abriu o compromisso; flag não troca propriedade. Na configuração isolada, inventário/custo/resultado atribuídos coincidem com o consolidado. Caixa não alocado permanece identificado. Não implementar repartição multiativo ou preenchimentos internos fictícios.

Preservar entrada/exposição 10%, uma posição/pendência, perda diária 1% e drawdown 5%, incluindo taxas e marcação não realizada. Aplicar mínimo entre limites globais e overrides mais restritivos por instância/par; nenhuma flag desliga risco/filtros/reconciliação. SELL de redução permanece possível sob trava com dados/saldo/estado confiáveis; trava não liquida automaticamente.

Falha de módulo/dados pausa consumidor afetado; divergência financeira, reserva desconhecida ou estado compartilhado incerto bloqueia novos compromissos da carteira. Não remover custos, redefinir baseline ou relaxar limites para transformar demonstração negativa em aprovação.

## 8. Persistência, identidade e compatibilidade

### 8.1 Separação dos modelos

Não adicionar tabelas a `market.sqlite3` v1 ou anexar estado modular à carteira `paper.sqlite3` v1 em uso. A demonstração usa diretório próprio e **carteira modular em `paper.sqlite3` schema v2**, modelo `paper-modular-v1`. Reutilizar invariantes/redução financeira da 03, sem segundo ledger independente para a mesma carteira.

Comandos históricos mantêm leitura/escrita v1; novos comandos exigem v2 e rejeitam v1 antes de efeitos. Comandos históricos rejeitam v2 sem interpretá-lo como v1 ou criar substituto silencioso. Criar v2 somente em diretório vazio: **sem upgrade automático de carteiras v1**. Rejeitar versões futuras/objetos inesperados; preservar carteiras e hashes históricos.

V2 armazena núcleo financeiro mais gerações de configuração, instâncias/estado, ciclos/decisões e atribuições. Definir DDL, PK/UNIQUE/FK, versão e formatos no adapter/documentação antes dos testes persistentes. Ciclo e intenção ligados por identidade única; fill atribuído a uma instância nesta política. Hashes/projeções incluem metadados auditáveis, sem apresentar hash antigo como se incluísse atribuição modular.

### 8.2 Transações e recuperação

Chave de ciclo: ambiente + modo + carteira + instância + versão + geração + época de ativação + dataset lógico + par/intervalo + candle. Decisão/ação deriva do ciclo. Persistir hash do prefixo/payload; mesma chave/conteúdo retorna resultado anterior; divergência bloqueia. `run_id`/horário real não criam identidade. Não incrementar época por reinício.

HOLD/recusa: decisão/motivo, médias, estado e cursor confirmados juntos; HOLD não cria posting financeiro. Transação A: decisão, atribuição, plano, reserva/ledger e estado do ciclo juntos sob a mesma conexão/lock/CAS da carteira. Transação B: fill, consumo de reserva, carteira/risco/custos atribuídos e conclusão do ciclo juntos. Não usar dois bancos com commits independentes para decidir e reservar a mesma intenção.

Morte antes de A não confirma decisão financeira; após A, retomar plano/geração persistidos antes de avaliar candles novos; durante B, rollback ou fill integral. Não recalcular médias para substituir plano reservado. Janela/cursor refletem ciclo confirmado, inclusive sem intenção. Marcas/DAY_START conservam identidade e reconciliação.

Reconciliar financeiro, ciclos, instâncias, propriedade, reservas, fills e custos antes de novos efeitos. Histórico/atribuições confirmados imutáveis, projeções verificáveis sem correção silenciosa. Divergência persiste bloqueio quando possível; diagnóstico só leitura indica indisponibilidade quando a reconstrução segura falhar. Falha de relatório não desfaz commits ou refaz fills.

## 9. Gerações, desativação e reativação

Validar snapshot inteiro antes de aplicar geração em fronteira de ciclo com hash/CAS. Contexto inicial de carteira/modelo/dataset é imutável; mudanças de flags/parâmetros são registros novos, sem reescrever metadata histórica. Configuração idêntica não cria geração. Alterar diretório não importa capital de outra carteira.

Estados mínimos: DISABLED, READY/ACTIVE, DRAINING, PAUSED/ERROR. Desativar bloqueia novas decisões/entradas; serviço compartilhado mantém recuperação/monitoramento. Política suportada no produto: `hold_and_monitor`; `cancel_and_monitor` apenas contrato com fakes, com ativação real rejeitada enquanto a capacidade não existir. Sem cancelamento remoto.

RESERVED local continua resolvido pelo serviço financeiro independente da estratégia. Cancelamento local já suportado pela 03 pode ser testado no domínio e libera exatamente a reserva sem fill posterior. Com BTC residual, manter DRAINING, marcação/custos/consumo de limites; não vender, transferir dono ou declarar DISABLED sem política de custódia residual auditada. Saída explícita de redução segue risco/executor autorizado; não criar CLI de liquidação nesta Sprint.

Reload inválido conserva snapshot anterior para recuperação e bloqueia novas entradas; sem aplicação parcial. Mudança material com posição/pendência exige drenagem/reconciliação e é rejeitada enquanto incompatível. Reativação em caixa só avalia candles posteriores ao watermark confirmado; históricos podem aquecer médias, sem negociar cruzamentos perdidos. Não zerar drawdown/baseline/deduplicação/custos por flag ou geração.

Testar ordem aberta/parcial/UNKNOWN com fakes para provar monitoramento não abandonado. Isso não implementa fill parcial/transporte remoto: ativação permanece bloqueada até Sprints pertinentes. Mudanças materiais invalidam evidências de elegibilidade afetadas; flag PAPER não concede permissão privada.

## 10. Relatórios e entregáveis

Há necessidade de apresentação legível nesta Sprint, conforme seção 4.9 do planejamento: compreender por que a SMA ficou inativa, decidiu ou foi recusada. Gerar **`report.html` autocontido**, UTF-8, tabelas e estilo de impressão, além de `report.json`/`manifest.json`. PDF pode ser adicional, renderizado/revisado; HTML atende o formato não JSON sem impor dependência de renderização ao runtime financeiro.

`strategy-run` publica os três arquivos ao concluir execução habilitada; `strategy-report` reexporta de snapshot só leitura, sem avaliar sinais ou operar. Default desabilitado sem carteira exige apenas NOOP em stdout; o relatório de validação da Sprint reúne também esse caso. Falha de publicação retorna 3/progresso confirmado, permitindo reexportação segura.

Conteúdo: configuração/geração, origem/hash/período dos dados, regras/custos sintéticos, candles/warm-up/HOLD/cruzamentos, médias/motivos, propostas/recusas, quantidades/fills/custos, realizado/não realizado, saldo/posição, risco/travas/reconciliação. Separar efeitos atuais de histórico e esperado de obtido. Identificar teste funcional, sem anualização/inferência de rentabilidade.

Publicar em `<strategy.data_dir>/reports/<run_id>/` com manifesto/hashes de arquivos e snapshot/modelo/fontes. Dado técnico permanece string canônica; apresentação pode usar vírgula decimal. Escapar textos HTML não confiáveis, sem scripts/recursos remotos. Temporário/rename após commits, sem transação de escrita durante renderização. Conferir dados e apresentação em navegador ou PDF renderizado, sem cortes/sobreposição; registrar caminho do artefato revisado no guia.

| Caminhos previstos | Responsabilidade |
|---|---|
| `domain/modules/`, `domain/strategy/` | Descriptors/DTOs/registro, estado e SMA pura; ajustar nomes sem mudar contratos |
| `application/strategy_run.py`, `strategy_reconcile.py` e portas | Ciclo/coordenação, dimensionamento, geração, recuperação e atribuição |
| Configuração/modelos existentes; `entrypoints/strategy.py` e CLI | Schema opcional, comandos e composição offline |
| `adapters/strategy_fixture.py` | Validação limitada e snapshots temporais |
| `adapters/storage/strategy_sqlite.py`, `strategy_report.py` | Modular v2, snapshots, JSON/HTML e manifestos |
| `config/strategy.sma.example.toml`, `strategy.sma.fixture.toml`, `config/fixtures/strategy-sma-crossings.json` | Defaults, opt-in e fixture causal |
| `tests/unit/test_strategy_sma.py`, `test_module_config.py`, `test_coordinator.py` | Cruzamentos, contratos, escopos, conflitos e limites |
| `tests/integration/test_strategy_storage.py`, `test_strategy_cli.py`; harness/smoke | Atomicidade, recuperação, compatibilidade, relatório e wheel |
| README, .gitignore; manifest/lock se necessário | Comandos reais, artefatos ignorados sem ignorar fixtures |
| `docs/estrategias/trend_sma.md` e catálogo | Documento individual junto da implementação, seção 4.7 do planejamento |
| `docs/bancos/paper-sqlite.md`, catálogo e ADR da persistência modular | V1/v2, DDL/modelo real, rejeição sem migração, compatibilidade e operação |
| Guia/evidências 04, arquitetura, especificação e planejamento | Resultados, comandos/hashes, revisão documental e limites |

Paths de código `domain/`, `application/`, `adapters/`, `entrypoints/` são internos a `modules/trading/src/cripto_bot`; config/tests pertencem à raiz da aplicação e docs ao workspace. Preferir biblioteca padrão, Pydantic e ferramentas existentes, sem pandas/NumPy/ORM/framework de plugins. Dependência nova exige necessidade demonstrada/lock atualizado. Não criar `trend_sma.md` ou adapters antes da implementação solicitada.

## 11. Sequência e critérios de aceite

Sequência futura: revalidar 03 → contratos/configuração → fixture/indicadores → coordenador/risco → persistência/recuperação → CLI → geração/reativação → testes/wheel → relatórios/documentos. Preservar regressão em cada fronteira.

AC01–AC10 preservam os temas da especificação resumida anterior; AC11–AC18 detalham o contrato novo. A matriz expandida foi executada e está aprovada no alcance registrado no guia 04, sem herdar aprovação da 03. Aplicar M01–M16 da matriz modular no alcance desta Sprint; capacidades futuras ficam fora do escopo, com prova de rejeição da ativação.

| ID | Cenário obrigatório | Resultado exigido |
|---|---|---|
| AC01 | Defaults, ausência e listas de escopo | HOLD/NOOP, nenhuma intenção/carteira nova; opt-in na combinação explícita, sem herança para outro modo/ambiente |
| AC02 | Registro, dependências, versão, params e composição | Rejeição atômica de ativação inválida/ciclo/disputa; desabilitado não importa dependência opcional |
| AC03 | SMA, igualdade, warm-up e inventário | Seção 6 reproduzida, inclusive 50/51 fechamentos, baixa sem BTC e ausência de pirâmide/short |
| AC04 | Risco e arredondamentos | Limite global/instância/par mais restritivo, custos/reservas uma vez; sem bypass; fronteiras 10%/1%/5% |
| AC05 | Coordenador com fakes e chegada invertida | Determinismo, conflito rejeitado, lock/CAS sem gasto duplicado |
| AC06 | Envelope/atribuição | Instância/versão/geração/prefixo em decisão/intenção/fill; custos/inventário/resultado reconciliados |
| AC07 | Desativação/pendência/reativação | Entradas bloqueadas, monitoramento/recuperação mantidos, DRAINING com BTC, sem liquidação/reset/replay; parcial/UNKNOWN só em fakes identificados |
| AC08 | Geração inválida/concorrente/material | Aplicação atômica, bloqueio de novas entradas em erro, estado antigo recuperável, watermark/risco preservados; privado rejeitado |
| AC09 | Regressão, qualidade e wheel | Contratos 01–03, Ruff/formatação, mypy strict, pytest/branches, build e wheel sob guard aprovados |
| AC10 | Documento de estratégia | `trend_sma.md`/catálogo completos e conferidos contra código, exemplos/cálculos; pendência documental bloqueia aceite |
| AC11 | Prefixo, fechamento, futuro e gap | Futuro não altera passado; sem fill retroativo; inválido falha antes de efeito; preço ausente/vencido gera motivo |
| AC12 | Opt-in/repetição | 71 avaliações/2 fills e valores exatos da seção 6.3; replay zero efeitos/hash estável; cenário positivo separado |
| AC13 | Morte real antes/depois de A/B e em HOLD | Atomicidade financeira/modular, retomada única, cursor/deduplicação corretos, lock liberado |
| AC14 | Persistência compatível | V1 preservada, v2 nova; fluxo/modelo incompatível rejeitado, sem migração/reset implícitos |
| AC15 | Corrupção/concorrência | Divergência de journal/projeção/estado/atribuição bloqueia duravelmente, diagnóstico seguro, sem reparo por diferença |
| AC16 | Relatório/publicação | JSON/HTML/manifesto conferidos, snapshot consistente, revisão visual, reexportação sem sinais/fills novos |
| AC17 | Segurança | Sem cliente HTTP/privado; sockets bloqueados nos filhos/wheel; credenciais/flags/paths/symlinks proibidos rejeitados; sanitização |
| AC18 | Banco/evidências | Documento/catálogo/ADR confrontados com DDL/pragmas/fixture; matriz, hashes, limitações e estado real registrados |

Morte exige processos filhos reais/SQLite, não só exceção em memória. Corromper apenas fixtures/cópias identificadas, com injeção explícita. Cobrir ramificações novas de causalidade, flags, dimensionamento, gerações, atribuição e commits; registrar lacunas justificadas sem exclusões artificiais ou percentual global como substituto de cenários.

### Comandos planejados, ainda não executados

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
uv run --locked cripto-bot check-config --config config/strategy.sma.example.toml
uv run --locked cripto-bot strategy-run --config config/strategy.sma.example.toml
uv run --locked cripto-bot check-config --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-run --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-reconcile --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-report --config config/strategy.sma.fixture.toml
uv run --locked cripto-bot strategy-run --config config/strategy.sma.fixture.toml
uv run --locked python tests/wheel_smoke.py
```

Primeira validação opt-in usa carteira nova. Se já existir, identificar replay e criar outro TOML/diretório sintético, sem apagar o anterior. Estender smoke test para wheel reinstalado em ambiente separado, cwd neutro sem PYTHONPATH, caminhos absolutos, origem site-packages e guard de sockets testado. Registrar instalação real, versão/hash do wheel e default/opt-in/replay, além dos contratos históricos.

## 12. Evidências, recuperação, custo e conclusão

Registrar no guia/evidências 04: revisões/estado dos dois repositórios, versões, hashes de fontes/lock/configuração/fixture/modelo/wheel, comandos/exit codes/stdout/stderr sanitizados, esperado/obtido por AC, alcance M01–M16, cobertura/lacunas, médias/decisões, gerações, ledger/atribuições e reconciliação. Não alterar evidências JSON 01–03 para representar testes novos. HTML/PDF é apresentação derivada, sem substituir evidência estruturada.

| Falha | Recuperação |
|---|---|
| Configuração/fixture inválida | Corrigir entrada, sem carteira nova/aplicação parcial |
| Interrupção após reserva | Reconciliar/retomar plano e geração persistidos antes de novo ciclo |
| Interrupção após fill | Devolver confirmado, sem repetir efeito |
| Projeção/atribuição/estado divergente | Bloquear/preservar/diagnosticar em cópia, sem ajuste por diferença |
| Schema/modelo incompatível | Rejeitar, sem mudar user_version ou apagar estado |
| Publicação falha | Preservar commits, reexportar por strategy-report |
| Desativação com posição | DRAINING/custódia/monitoramento/risco, sem venda automática |

Riscos: dados futuros, duas avaliações do candle, geração que duplica intenção, estado sem reserva correspondente, caixa contado duas vezes, venda de inventário alheio, monitoramento abandonado e histórico apresentado como efeito novo. A matriz deve provar barreiras, sem depender de lucro.

AWS zero, sem serviços/recursos externos ou capital real; CPU/disco locais. Estimativa orientativa 4–7 dias úteis, revisável após medir persistência/recuperação/regressão. Não retirar testes para cumprir prazo. Ignorar bancos/locks/ambientes/relatórios operacionais no Git da aplicação, mantendo fixtures/TOMLs/evidências selecionadas versionáveis. Limpeza só de artefatos sintéticos identificados após preservar revisão.

Concluir somente com AC01–AC18 obrigatórios aprovados, zero duplicação/bypass/saldo negativo/divergência inexplicada, wheel verificado, relatório legível revisado e documentação de estratégia/banco atualizada. Caso contrário, PENDENTE com diagnóstico. A conclusão permite revisar evidências para detalhar 05; não iniciar automaticamente, criar commits, publicar remotos ou liberar privado.

## 13. Prompt autossuficiente para implementação futura

```text
Implemente somente a Sprint 04 — Base modular, flags, coordenação, risco
e tendência SMA, conforme docs/sprints/sprint-04.md integralmente.

Workspace: /home/cams7/Dev/Cripto. Aplicação/raiz Python/uv:
/home/cams7/Dev/Cripto/cripto-bot. Docs:
/home/cams7/Dev/Cripto/docs, Git independente. Paths docs/... relativos ao
workspace; demais caminhos da especificação pertencem à aplicação.

Leia instruções locais, planejamento (4.6–4.9, 6, 9, 10 e 13), arquitetura,
arquitetura modular, ADRs, catálogos/matriz modular, bancos e guia/evidências
03. Inspecione manifest, lock, configuração, CLI, domínio financeiro,
adapters e testes. Preserve trabalho/históricos. Não altere referências
externas nem leia credenciais.

Pré-requisitos: (1) 03 revista/hashes conferidos, (2) regressão reproduzida,
(3) ferramentas/permissões confirmadas, (4) compatibilidade v1/v2 entendida.
Falha mantém PENDENTE no guia 04 e impede trabalho dependente. Os 316 testes
são históricos, não resultado atual. Reconfirme fontes oficiais utilizadas.

Somente PAPER/local/BTCUSDT/15m/fixture offline. Implemente trend_sma e base
usada: registro estático/descriptor, DTOs/Protocols, TOML/escopos opt-in,
exclusive_owner, dimensionamento/risco, atribuição, estado/geração,
recuperação e relatório. Todos desabilitados por padrão; sem habilitados e
sem carteira, NOOP sem efeito; carteira anterior mantém monitoramento.
Sem placeholders, plugins, demais estratégias, multiativo, backtest completo,
daemon, AWS, notificações ou trading privado. Preserve run-once NOOP,
collect-market e paper-* históricos; adicione strategy-run/report/reconcile
com códigos/saídas da seção 5, sem HTTP ou --allow-network.

Adicione configurações desabilitada/opt-in e fixture limitada, validada antes
de efeitos. SMA20/50 exige 51 fechamentos; alta de <= para >, baixa de >=
para <; igualdade atual não cruza. Snapshot disponível até as_of, Decimal
local precisão 80, sem float. Execução só com observação posterior/fresca;
ausência não inventa fill. Futuro não altera decisões/identidades passadas.
Dimensione centralmente incluindo custos/step/limites, sem reduzir intenção
fixada em silêncio. Sem pirâmide/short; SELL só inventário próprio. Limite
global/instância/par mais restritivo; preserve DAY_START/pico/baseline/travas.

Carteira modular schema v2/modelo paper-modular-v1 em diretório novo, sem
converter v1. Transação A une decisão/estado/cursor/atribuição/reserva/ledger;
B une fill/carteira/risco/custos/ciclo. HOLD também deduplicado. Sem bancos
com commits independentes para decidir e reservar. Reconcile antes de novos
efeitos; retome plano/geração persistidos, sem novo preço. Hash/ID sem run_id
ou futuro do dataset. Rejeite schema/modelo incompatível, sem reset.

Gerações inteiras por CAS; desativação bloqueia entradas e mantém recuperação
independente/DRAINING com BTC, sem liquidação. Reativação não negocia cruzamento
antigo nem zera risco/custos. Parcial/UNKNOWN/cancel_and_monitor são fakes de
contrato, sem runtime privado; rejeite ativação de capacidades ausentes.

Demonstração: 71 fechamentos [100]x50+[110]+[100]x20, baseline 10000/peso 10%,
observações posteriores 110/100, custos 10/10/5 bps, tick 0.01/step 0.000001.
Espere 71 avaliações (50 warm-up/19 outros HOLD/2 direcionais), 2 fills de
9.072754 BTC, preços 110.11/99.90, taxas 0.99900095/0.90636813, resultado
-94.53818742 e saldo 9905.46181258 USDT, sem BTC/reservas/custo final.
Replay zero efeitos. São expectativas; registre os resultados obtidos.

Execute AC01–AC18 e M01–M16 no alcance definido: contratos/configuração,
fakes/conflitos, risco, causalidade, geração, atribuição, mortes reais/CAS,
corrupção em fixtures, relatório e regressão 01–03. Expanda matriz do guia 04.
Rode uv sync --locked --group dev, Ruff check/format --check, mypy em
modules/trading/src, pytest com branches, uv build e CLI da seção 11.
Estenda/execute wheel_smoke com wheel reinstalado, cwd neutro, sem PYTHONPATH,
origem site-packages, paths absolutos, hash e guard nos filhos comprovados.

Publique report.json/report.html autocontido/manifesto após commit e confira
valores/renderização visual; registre caminho no guia. strategy-report
reexporta snapshot sem novos sinais/fills. PDF é adicional se útil. Separe
efeitos atuais/histórico e esperado/obtido; não chame fixture de backtest.

Crie docs/estrategias/trend_sma.md e atualize catálogo na implementação.
Documente v1/v2/rejeição sem migração em docs/bancos/paper-sqlite.md,
catálogo/ADR, conferindo DDL/pragmas/fixture. Atualize README, arquitetura,
especificação, planejamento e guia/evidências 04 com revisões/versões/hashes,
comandos/exit codes, resultados, cobertura/lacunas, limites/recuperação/
custos/limpeza. Não altere evidências 01–03. Sem documentação/testes completos,
PENDENTE. Não inicie 05, faça commit/deploy/publique remotos, envie mensagens
ou libere privado automaticamente.
```

## 14. Fontes e registro desta atualização

Fontes oficiais consultadas em 25/10/2026: [Python 3.13 — Protocol](https://docs.python.org/3.13/library/typing.html#typing.Protocol), para contratos tipados; [Decimal/localcontext](https://docs.python.org/3.13/library/decimal.html#decimal.localcontext), para precisão/contexto local; [sqlite3 — controle transacional](https://docs.python.org/3.13/library/sqlite3.html#transaction-control), para atomicidade; [Pydantic — modo estrito](https://docs.pydantic.dev/latest/concepts/strict_mode/), para validação nas fronteiras. Páginas atuais não alteram pins do projeto; confirmar compatibilidade com lock na implementação.

Janelas, limites, comandos, schema/modelo modular, fixture e estados são decisões de projeto, não contratos da corretora. Nenhuma nova API externa ou dependência obrigatória introduzida nesta especificação.

No detalhamento original, anterior à implementação registrada abaixo, foram lidos planejamento, Sprint 03, guia/evidências anteriores, arquitetura/catálogos/matriz modular, manifest/modelos/CLI/portas/adapters pertinentes. Conferidos 40 hashes e valores esperados calculados com Decimal. Alterado somente este documento; nenhum código, teste, carteira, migração, relatório operacional, credencial, recurso AWS ou ordem foi executado/alterado. Naquele momento, a Sprint 04 permanecia sem implementação e sem aceite funcional.


## 15. Registro de execução em 25/10/2026

Implementação solicitada e concluída no repositório existente, base `35be286`, com documentação baseada em `cc78f4c`. Preservada a alteração documental prévia desta especificação e os contratos/evidências históricos. Conferidos 40 hashes e reproduzidos os 316 testes da base antes da implementação. Sem nova dependência/alteração de lock, credencial, serviço externo, AWS, commit ou remoto.

Entregues registro estático/DTOs/Protocol, TOML com escopos/limites restritivos, SMA20/50, coordenador exclusive_owner, dimensionamento/risco, carteira modular v2, gerações/watermark/atribuições, recuperação, comandos strategy-run/report/reconcile e exportação JSON/HTML/manifesto. Sem configuração e com exemplo false, NOOP sem carteira; opt-in em fixture é explícito e não muda defaults. Fluxos paper-* v1 e run-once NOOP permanecem preservados.

Demonstração confirmou 71 avaliações (50 warm-up/19 outros HOLD/2 direcionais), dois fills de 9.072754 BTC, taxas 1.90536908 USDT, realizado -94.53818742 e saldo final 9905.46181258 USDT. BTC/reservas/custo encerrados. Reconcile/report/replay mantiveram o hash; replay reconheceu 71 ciclos, sem novos fills ou custos. O resultado negativo é o esperado do teste funcional, sem avaliação econômica.

Validação final: **428 testes aprovados, sem avisos**, Ruff/formatação/mypy strict, build e wheel instalado em ambiente neutro aprovados. Cobertura combinada 96,52% (linhas 97,67%; ramificações 92,89%), com lacunas registradas e sem exclusões novas para elevar percentual. Foram verificados crash real antes/depois de A/B/HOLD, CAS/lock, schema/constraints, corrupção, geração/reativação, prefixo/cotação passada e fechamento à meia-noite UTC. Parcial/UNKNOWN são somente fakes de contrato, sem runtime privado implementado.

Schema v2 em diretório novo, sem migração v1 e sem alteração do banco de mercado. Revisados DDL/diagrama/dicionário e pragmas de fixture/demonstração; journal/atribuições/projeções reconciliados. Criados documento [trend_sma](../estrategias/trend_sma.md) e [ADR 0005](../decisoes/0005-estrategia-modular-e-persistencia.md), atualizados catálogos/arquitetura/README. [Relatório HTML](../output/html/relatorio-sprint-04.html) conferido contra o manifesto e revisado visualmente; PDF adicional não foi necessário.

Decisões concretizadas: avaliação fixture isolada; dependências explícitas por depends_on sem imports dinâmicos; fingerprint da configuração modular separado do contexto financeiro imutável; ciclo registra hash da observação para detectar alteração do passado; validade do sinal limitada a max_quote_age_ms após as_of; baselines explícitos antes de candle que fecha em novo dia UTC; assinatura de mudanças SQLite/CAS entre commits do escritor exclusivo, mantendo replay integral inicial/final.

Comandos/versões/hashes, cobertura/lacunas, matrices AC/M, wheel, artefatos e limitações estão no [guia 04](../testes/sprint-04-validacao.md) e nas [evidências 04](../testes/sprint-04-evidencias.json). Próximo passo: revisar as evidências antes de detalhar a Sprint 05. Backtest, contínuo, AWS, Demo/Testnet/LIVE e demais módulos não foram executados/liberados.
