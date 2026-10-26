# Arquitetura modular de estratégias, carteira, sinais e execução

Revisão: 25/10/2026. **Estado: base mínima/trend_sma em fixture (04) e caminho histórico isolado (05) implementados para local/PAPER. Aceite por fluxo nos guias 04/05; demais capacidades continuam propostas.** Complementa o [planejamento](planejamento.md). Aplicação Python em `/home/cams7/Dev/Cripto/cripto-bot`; documentos em `/home/cams7/Dev/Cripto/docs`. Binance Spot sem margem, empréstimos, short ou alavancagem é o escopo inicial. As Sprints 01–03 continuam com seu contrato histórico.

## Papéis e componentes compartilhados

| Papel | Módulos previstos | Responsabilidade |
|---|---|---|
| Estratégias de negociação | tendência, reversão à média, breakout, grid, arbitragem, market making, pairs | Propor alvos de posição ou planos de ordens explicados; nunca acessar corretora ou reservar saldo diretamente |
| Gestão de carteira | DCA, rebalanceamento, momentum relativo | Propor aportes periódicos limitados ao caixa ou pesos/alocações; sujeitos ao mesmo coordenador e risco |
| Fontes de sinais/modelos | notícias/sentimento, ML, indicadores | Produzir features/previsões temporais; não são autorização de negociar nem enviam ordens |
| Algoritmos de execução | TWAP, VWAP | Dividir intenção previamente aprovada em ordens filhas; não definem tese de investimento |
| Infraestrutura transversal | registro, configuração/flags, dados, relógio, indicadores, coordenador, alocador, risco, ledger, OMS, avaliação | Implementar invariantes uma vez para todos os módulos |

Momentum relativo também é uma regra de seleção; tendência também é chamada momentum temporal. A versão inicial do primeiro ranqueia ativos, a do segundo usa SMA no tempo. Breakout reaproveita janelas, volatilidade e confirmação da tendência; reversão, grid e pairs compartilham estatísticas de desvio, mas possuem políticas/estado distintos. Grid e market making compartilham gestão de ordens limitadas, inventário e cancelamento, sem usar o mesmo sinal. Arbitragem determinística de preços difere da convergência estatística de pairs. DCA pode usar TWAP; rebalanceamento pode usar TWAP/VWAP. Notícias e ML podem alimentar qualquer estratégia compatível; não duplicar coleta, execução, risco ou relatórios dentro deles.

## Contratos padronizados

Interfaces Python propostas como `Protocol` e DTOs versionados; sem imports dinâmicos arbitrários, framework de plugins ou dependências opcionais carregadas no caminho desabilitado. A infraestrutura mínima e SMA foram entregues na Sprint 04; detalhes concretos, alcance e testes estão em [trend_sma](estrategias/trend_sma.md) e no [guia 04](testes/sprint-04-validacao.md). Demais implementações só quando escolhidas.

| Contrato | Entradas | Saída e limite |
|---|---|---|
| `ModuleDescriptor` | registro estático de implementação | ID/versão/tipo, schemas de parâmetros/estado, capacidades, dependências mínimas, modos/mercados/dados suportados, recursos exclusivos e compatibilidades declaradas |
| `SignalSource.compute(context, params, state)` | dados com instante de disponibilidade, relógio, estado anterior | `FeatureBatch` imutável com origem, versão, as_of, validade, qualidade e novo estado; sem ordens |
| `Strategy.evaluate(context, params, state)` | snapshot de mercado/carteira, orçamento atribuído, features e relógio injetado | `Decision`: HOLD, alvo não negativo ou plano de ordens; justificativa, validade e novo estado; sem I/O financeiro |
| `PortfolioPolicy.allocate(context, params, state)` | saldos, pesos, calendário e universo elegível | Mesma `Decision` de alocação/compra periódica, com fonte de capital e limites, sem aporte implícito |
| `Coordinator.resolve(decisions, snapshot, config)` | decisões válidas e versões de carteira/configuração | Plano consolidado, contribuições por instância, decisões recusadas e motivo |
| `RiskPolicy.assess(plan, snapshot, limits)` | plano, reservas/ordens pendentes, dados e limites | Admitido/reduzido/rejeitado com motivos; obrigatório, independente das flags |
| `ExecutionAlgorithm.plan(parent, context, state)` | intenção aprovada, deadline, política de execução, cotação/volume | Ordens filhas limitadas ao restante e orçamento do pai; sem escolha de destino ou bypass do risco |
| `ExecutionPort` e OMS | ordem filha revalidada e identidade persistida | Confirmação/fills/rejeição/UNKNOWN, consulta e cancelamento pelo adapter permitido no modo |
| `StateStore` / unidade de trabalho | ID instância, versão/schema e estado esperado | Atualização compare-and-swap e outbox atômicas; mudança incompatível exige migração explícita |

`context` usa snapshot imutável com `as_of`, watermark, dados fechados, saldo livre/reservado por ativo, posições/ordens por proprietário, limites e orçamento de tempo. Nenhum módulo recebe credenciais ou cliente de negociação. Decimais são strings validadas/Decimal, timestamps UTC, estados serializáveis e versionados. Quantidade de venda nunca supera inventário próprio disponível. HOLD não cria intenção.

Envelope obrigatório: `decision_id`, `module_id`, `instance_id`, versão da implementação, `config_hash`/geração, `state_version`, ambiente, modo, tipo de avaliação (backtest/contínuo), carteira, par/conjunto de pares, as_of/valid_until, dataset/features/modelo/treino quando aplicável, motivo, alvos/limites e causalidade. Todo pai/filho/fill referencia esse envelope e os IDs de contribuição. Identidade determinística por instância, geração, época, ciclo e ação, persistida antes de efeito externo; `run_id` não substitui deduplicação.

## Catálogo: contratos específicos e compatibilidade Spot

Todos os itens começam desabilitados. trend_sma possui implementação para fixture e backtest local/PAPER, com configuração e estado separados; os demais continuam não implementados. Dependências listadas são capacidades necessárias, não obrigação de implementar outros itens do catálogo. Métricas comuns de custo/risco são adicionais às específicas abaixo.

| ID / papel / Sprint | Entradas → saída | Parâmetros e estado | Dependências / métricas específicas | Compatibilidade inicial e restrições |
|---|---|---|---|---|
| `trend_sma` / estratégia / 04 | candles fechados → alvo comprado/caixa | janelas 20/50, timeframe, warm-up; último cruzamento/ciclo | indicadores/SMA, risco; turnover, tempo em tendência, whipsaws | Spot long-only; SELL só inventário da instância; sem short |
| `mean_reversion` / estratégia / 12 | preço/desvio/volatilidade → alvo comprado/caixa | janela, z de entrada/saída, horizonte e teto; média/desvio e posição atribuída | estatística causal; tempo de convergência e perdas por regime | Spot long-only; reversão vendida fica futura |
| `breakout` / estratégia / 13 | faixa anterior/volume → alvo comprado/caixa | lookback, buffer, confirmação, expiração; faixa/ciclo | janelas/volatilidade; falsos rompimentos e atraso | Spot comprado/caixa; rompimento para baixo apenas reduz inventário |
| `dca` / carteira / 14A | calendário UTC e caixa → compra periódica | periodicidade, valor/teto por período, política de disparo perdido; próxima janela e gastos | relógio/idempotência; aderência ao calendário, preço médio, capital empregado | Spot com caixa previamente disponível; sem crédito, aportes externos ou martingale implícitos |
| `rebalance` / carteira / 14B | pesos-alvo e inventário → alvos por ativo | bandas, periodicidade, turnover/notional mínimo; última revisão | universo multiativo/avaliação comum; tracking error, drift e custo | Spot sem pesos negativos; vende ativos possuídos antes de usar caixa confirmado |
| `relative_momentum` / carteira e seleção / 14C | retornos históricos de universo → pesos top-k/caixa | janela, k, filtro liquidez, limite por ativo; ranking/seleção | universo sincronizado sem viés de sobrevivência; turnover/ranking e concentração | Spot long-only, caixa se nenhum elegível; não depende de implementar rebalanceamento |
| `twap` / execução / 15A | intenção pai aprovada e relógio → filhos por tempo | duração, intervalos, limites de preço/participação; quantidade restante e filhos | OMS/relógio/reservas; implementation shortfall, atraso e completion | Spot BUY/SELL com caixa/inventário reservados; não garante execução; não depende de VWAP |
| `vwap` / execução / 15B | pai aprovado e perfil de volume disponível → filhos proporcionais | perfil causal, janela, participação máxima, deadline; volume/filhos/restante | OMS e volume confiável; desvio ao benchmark VWAP, shortfall/completion | Spot; volume futuro observado não pode orientar decisão passada; não depende de TWAP |
| `grid` / estratégia / 16 | preço/faixa e inventário → escada limitada | níveis, espaçamento, faixa/teto, reancoragem; níveis/ordens e inventário | OMS multiordem/parcial/cancelamento; inventário, ocupação e PnL líquido da escada | Spot financiado em caixa e ativo; grid neutro alavancado/short fica futuro; sem lucro garantido em tendência |
| `arbitrage` / estratégia / 17 | cotações sincronizadas de ciclo de pares → plano de pernas | edge líquido mínimo, idade máxima, capital/perna/deadline; grupo e exposição residual | multiativo/OMS de grupo e profundidade; edge realizado, fill conjunto e risco de perna | Variante triangular na mesma Binance Spot, apenas se símbolos/permissões existirem; execução não atômica, sem supor lucro travado. Outras corretoras/transferências ficam futuras |
| `market_making` / estratégia / 18 | bid/ask, profundidade, inventário → cotações limitadas | spread mínimo, skew, limites/cancelamento/idade; cotações e inventário | feed de livro, OMS, controle de latência, filtros/STP; adverse selection, spread líquido e estoque | Spot com ambos os lados financiados; sem vender inventário inexistente. Requer reavaliar runtime/feeds; 15 min/Lambda não é capacidade presumida |
| `pairs` / estratégia / 19 | séries sincronizadas e relação estatística → realocação conjunta | janela, hedge ratio, z/bandas, estabilidade/deadline; modelo/spread/pernas | multiativo/estatística/OMS de grupo; estabilidade, convergência, exposição e custos | Somente rotação entre inventários prefinanciados em Spot, sem presumir neutralidade. Long-short clássico exige margem/empréstimo/derivativos e fica fora do escopo |
| `news_sentiment` / fonte / 20 | notícias com publicação/recebimento e origem → score/qualidade/validade | fontes/licenças, idioma, janela, thresholds; deduplicação e watermark | adapter externo independente; cobertura, atraso, calibração e dados ausentes | Compatível como sinal Spot; não gera ordem sozinho. Dados externos são não confiáveis, nunca instruções executáveis; API/custo/licença a verificar |
| `ml_signal` / fonte/modelo / 21 | features point-in-time → previsão/score e incerteza | features, artefato/treino/versionamento/threshold; modelo/calibração/drift | pipeline de dataset/modelo isolado; erro/calibração/drift e contribuição fora da amostra | Compatível como sinal Spot sem alavancagem; requer consumidor explicitamente configurado; não depende de notícias nem de outro módulo opcional |

## Flags e configuração externa validada

Exemplo arquitetural **desabilitado**. O caminho backtest da 05 tem configuração própria; continuous permanece inelegível. O TOML executável da Sprint 04 inclui a tabela strategy e escopo fixture; consulte [configuração completa](../cripto-bot/config/strategy.sma.example.toml). Para backtest, consulte também [exemplo 05](../cripto-bot/config/backtest.sma.example.toml). O fragmento abaixo não é arquivo executável completo:

```toml
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

[coordination]
policy = "exclusive_owner"
configuration_generation = 1
```

Ativação efetiva exige simultaneamente `enabled=true`, ambiente, modo, tipo de avaliação e par explicitamente autorizados, implementação registrada, dependências presentes, compatibilidade/risco válidos e evidências daquele escopo. Ausência de flag/lista/par mantém desabilitado; não herdar LOCAL/PAPER para AWS/DEMO/TESTNET/LIVE, nem usar wildcard implícito. Desativação global prevalece sobre autorizações mais específicas. Overrides, se introduzidos, passam pelo mesmo schema e produzem novo hash; não ocultam erro no arquivo.

Validar antes de compor módulos com efeitos: ID/versão/schema desconhecido; ativação não implementada; parâmetro/tipo/faixa inválidos; dependência ausente ou ciclo; modo/mercado/par não suportado; feature/modelo vencido; política de desativação inválida; orçamento/risco ausente; pesos negativos ou soma >1; mais de um planejador de execução para o mesmo pai; seleção sem consumidor; disputa de saldo/ordens ou combinação sem regra de compatibilidade. Falhar atomicamente, sem ativação parcial. Catálogo de roadmap não conta como implementação. Dependência opcional desabilitada não bloqueia outro módulo independente; módulo sem implementação e desabilitado pode ser apenas listado pelo catálogo, sem importar suas bibliotecas. Nenhum fallback silencioso para outra estratégia, algoritmo ou modo.

## Coordenação, capital e risco centralizados

Na Sprint 04, política `exclusive_owner`: uma instância por par/subcarteira, com SMA como primeiro consumidor. As interfaces já permitem IDs múltiplos e testes de coordenador com fakes; não é necessário implementar os módulos futuros. Combinações posteriores exigem manifesto explícito validado e, quando necessário, capacidade de subledger multiativo. O universo inicial continua BTCUSDT; capacidade multiativo só surge nas etapas que a exigem.

Duas políticas de combinação propostas, introduzidas apenas quando necessárias: `segregated_budgets` (subcarteiras e pares/reservas independentes) e `weighted_targets` (alvos normalizados por instância com pesos fixados antes da avaliação). Na segunda, somar contribuições para obter um alvo líquido por ativo; sinais opostos podem reduzir o alvo ou cancelar-se, com motivo registrado. Não usar a ordem de chegada para decidir prioridade. Planos de cotações/grid/pernas não podem ser misturados automaticamente com alvos; exigem exclusividade ou coordenador de grupos declarado. Prioridade explícita de risco/saída não autoriza uma estratégia a vender inventário de outra.

DCA, rebalanceamento e momentum podem operar isoladamente. Sobre o mesmo saldo, não combinar políticas de alocação concorrentes sem escolher precedência ou composição explícita; seleção momentum pode alimentar alocação sem gerar uma segunda ordem. Notícias/ML apenas alteram o consumidor nomeado; não criar negociação duplicada a partir do mesmo evento. Uma ordem pai usa `immediate` como caminho básico, ou um único algoritmo TWAP/VWAP explicitamente habilitado; não encadear ambos no mesmo pai por default.

Capital por instância é um teto de orçamento, sem garantia de uso; pesos totais ≤1 e caixa não alocado permanece caixa. Reservas/ordens abertas entram no consumo antes de novas intenções. Um escritor por carteira, compare-and-swap, reserva atômica por ativo e ID de negócio persistente impedem duas instâncias de gastar o mesmo saldo. Alvo consolidado gera uma intenção externa com atribuições imutáveis; repartir fills/custos proporcionalmente aos compromissos atribuídos e distribuir resíduo Decimal por regra determinística (ordem estável de IDs). Sem cruzamentos internos fictícios a preço arbitrário. Vendas respeitam inventário atribuído; realocação de propriedade exige evento auditável e revisão, nunca simples troca de flag.

Risco é serviço central obrigatório: mínimos entre limites globais e por instância/par, incluindo exposição, caixa, concentração, perda diária/drawdown, ordens abertas, volume/participação, preço/freshness, prazo e orçamento de chamadas. Avaliar no consolidado e em cada atribuição, tanto no pai quanto antes de cada filho/envio; reserva do pai impede dupla contagem com seus filhos. Nenhuma flag permite desligar risco, filtros, kill switch, reconciliação ou autorização LIVE. Falha/UNKNOWN de estado compartilhado bloqueia novos compromissos de todos os módulos afetados; uma fonte independente indisponível pausa apenas consumidores dependentes, sem consumir dados vencidos ou acionar fallback não aprovado.

Prevenir ordens próprias opostas antes do envio. Consultar suporte/configuração de STP e filtros no símbolo/ambiente e testar cancelamentos/rejeições correspondentes; STP da corretora complementa o coordenador, sem substituir isolamento/idempotência. Fontes oficiais consultadas em 25/10/2026: [STP](https://developers.binance.com/en/docs/products/spot/faqs/stp_faq) e [filtros](https://developers.binance.com/en/docs/products/spot/filters). Reconfirmar detalhes antes de qualquer implementação privada.

## Desativação e mudança de configuração

Estados previstos por instância: DISABLED → READY → ACTIVE → DRAINING → DISABLED, com PAUSED/ERROR para incidentes. Desabilitar impede novos sinais/entradas e novos filhos de TWAP/VWAP; gerenciar pendências continua pelo OMS/serviço de risco independente do módulo. Não descarregar monitoramento porque a flag está false.

`on_disable` deve ser explícito ao habilitar: `hold_and_monitor` mantém ordens existentes sob monitoramento, ou `cancel_and_monitor` solicita cancelamento somente das ordens de propriedade da instância e reconcilia até estado terminal. Posições restantes ficam registradas, marcadas a mercado e consumindo limites e orçamento; não são liquidadas, transferidas ou abandonadas automaticamente. Intenção pai conserva reservas até filhos/cancelamentos reconciliados. Se posição ou ordem continuar, instância permanece DRAINING com entradas bloqueadas; conclusão depende de política de custódia residual explícita e auditada. Venda de saída requer plano e autorização do modo, mesmo com a fonte estratégica desativada.

Configuração nova é validada integralmente e aplicada em fronteira de ciclo com hash/geração compare-and-swap; operação em curso permanece vinculada à geração antiga até resolução. Mudança de parâmetros/algoritmo com pendências exige pausa/drenagem, reconciliação e eventual migração explícita de estado; sem reset automático de capital, pico de drawdown ou deduplicação. Reativação não reenvia sinais anteriores e exige estado reconciliado. Configuração inválida mantém bloqueadas novas entradas; OMS continua monitorando a configuração anterior, sem aceitar alteração parcial. Mudanças materiais invalidam evidências/aprovações dependentes.

## Avaliação e liberação por módulo e combinação

Medir por instância/versão/configuração e carteira: retorno líquido, taxas/spread/slippage, PnL realizado/não realizado, drawdown, exposição, turnover, fills/rejeições e latência, em mesma janela/dados/capital/modelo de custo e mesmas hipóteses de liquidação. Relatórios isolados e combinados não podem reutilizar ficticiamente o capital total para cada estratégia. Contribuições, custos e caixa residual devem reconciliar com o consolidado; transferências internas/aportes não são lucro. DCA com fluxos aprovados exige comparar fluxos iguais e reportar retorno ajustado a fluxos; sem aportes no escopo inicial. Ranking e seleção exigem universo histórico point-in-time; ML e notícias exigem instante de disponibilidade para evitar vazamento futuro.

Cada módulo tem aceite técnico separado e estado de elegibilidade por ambiente/modo/par. Exigir todos os casos obrigatórios do [guia modular](testes/estrategias-modulares-validacao.md), contratos e custos reproduzíveis. Combinação só se habilita após teste conjunto daquela composição, pesos, versão e algoritmo; soma de aceites individuais não prova compatibilidade. Lucro não é requisito para aprender em PAPER, mas gate econômico de LIVE permanece obrigatório e previamente definido.

Módulo novo ou combinação alterada volta aos gates aplicáveis de backtest → PAPER → Demo → Testnet, com evidência correspondente e aprovação real nova; aprovação antiga não cobre o catálogo inteiro. Antes de publicar alteração AWS, repetir gate SAM local da seção 8.1 do planejamento. Nenhuma Sprint opcional é pré-requisito universal do piloto simples. Todas permanecem desabilitadas por padrão, inclusive SMA; exemplo de teste com opt-in não altera defaults de instalação.

## Documentação técnica vinculada ao módulo

Cada implementação/modificação mantém `docs/estrategias/<module_id>.md` e o [catálogo](estrategias/README.md) na própria Sprint. O documento acompanha comportamento entregue, contratos/estado, dados/parâmetros/defaults/validações, flags, combinações, risco/desativação, ciclo fictício e testes/evidências/versionamento, adaptado ao papel. Não atribuir ordens a fontes de sinal nem decisões de investimento a algoritmos de execução. Critério M16 e seção 4.7 do planejamento bloqueiam conclusão se faltar atualização; exemplos propostos e recursos pendentes devem ser explícitos. A documentação de todos os opcionais ausentes não é dependência do módulo escolhido.

## Extensão histórica — Sprint 05

A SMA pura e a redução financeira/risco são compartilhadas; o caso de uso histórico tem configuração, relógio de eventos e store próprios. `domain/backtest` mantém apenas janela slow+1, pendência, carteira ativa, acumuladores e prefixo SHA incremental. Terminais e séries completas ficam no journal/projeções SQL. A fixture/schema v2 da 04 não é convertida ou ampliada para comportar meses de dados.

`backtest-prepare/freeze/run/report/reconcile` separam preparo sem PnL, protocolo imutável, execução causal, exportação em leitura e auditoria. `.active` preserva fixture e `active_for("backtest")` exige opt-in histórico. Não há dependência de módulos opcionais, rede dentro do motor ou coordenação com private/AWS. O snapshot completo vincula fonte/código/configuração/split/custos/benchmarks/métricas. Development/validation precedem test; registro local impede outra alegação de amostra intocada em janela real sobreposta.

Decision no close disponível; referência open observada +1 ms; plano/reserva A; fill B +2 ms. SCHEDULED não é reserva; pendência única impede gasto duplicado. Variantes não alteram a validade da fixture. Terminal mark_to_market não inventa liquidação. Benchmark 100% tem carteira e limites explícitos independentes, sem bypass da SMA.

Persistência: [schema histórico 1](bancos/backtest-sqlite.md), FULL/WAL, lock/CAS, eventos e projeções encadeados, reconstrução streaming inicial/final e validação incremental entre commits conhecidos. Documentação e escolha de transações em [ADR 0006](decisoes/0006-backtest-historico-e-protocolo.md). Resultados/escala/limites e gates no [guia 05](testes/sprint-05-validacao.md); nenhum incremento autoriza execução contínua ou LIVE automaticamente.


## Projeção analítica DuckDB + Parquet

Após a entrega da Sprint 05, a exportação histórica passa a produzir séries Parquet ZSTD e catálogo DuckDB, conforme [ADR 0007](decisoes/0007-duckdb-parquet-analitico.md). O DuckDB embutido consulta os Parquets para gerar resumos e confere as contagens com o snapshot SQLite. Métricas oficiais e regras financeiras continuam no domínio Decimal existente. A camada não participa da admissão/reserva/fill, não migra o ledger e não altera o protocolo já consumido. Os arquivos são projeções derivadas publicadas atomicamente; uma falha impede a publicação e permite reexportação em leitura. Schema e restrições em [banco analítico](bancos/backtest-analytics.md); resultados novos no [guia complementar](testes/duckdb-parquet-validacao.md), separados das evidências originais.
