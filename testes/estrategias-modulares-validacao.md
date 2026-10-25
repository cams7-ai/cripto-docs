# Guia de validação de módulos isolados e combinações

Revisão: 25/10/2026. **Estado: NÃO EXECUTADO / elegibilidade PENDENTE para todos os módulos e combinações.** Documento de planejamento, sem implementação, ativação ou negociação autorizada.

Escopo: [Sprint 04](../sprints/sprint-04.md), Sprints 05–11 e [incrementos opcionais 12–21](../sprints/estrategias-opcionais.md). Contratos: [arquitetura modular](../arquitetura-modular.md). Python em `/home/cams7/Dev/Cripto/cripto-bot`, evidências em `/home/cams7/Dev/Cripto/docs/testes`.

## Matriz comum obrigatória

| Caso | Cenário e resultado esperado | Estado |
|---|---|---|
| M01 | Instalação/arquivo sem flags: todos desabilitados; nenhum sinal de entrada/intenção; namespaces históricos preservados | NÃO EXECUTADO |
| M02 | Matriz de ambiente × modo × par × avaliação: opt-in exato apenas; ausência e falso mantêm bloqueio, PAPER não habilita DEMO/LIVE | NÃO EXECUTADO |
| M03 | ID/versão/parâmetro inválido, ativação não implementada, dependência ausente/cíclica e consumidor ausente rejeitados antes de efeito; sem ativação parcial | NÃO EXECUTADO |
| M04 | Import trap/sentinelas provam isolamento: módulo desabilitado/ausente não importa bibliotecas nem chama I/O; cada implementado roda sem demais opcionais | NÃO EXECUTADO |
| M05 | Sinais opostos e sinais iguais no mesmo ciclo; ordem de chegada invertida produz decisão idêntica, sem ordens duplicadas nem venda de inventário alheio | NÃO EXECUTADO |
| M06 | Concorrência e saldo compartilhado: dois módulos disputam capital; reserva atômica/CAS mantém soma de compromissos ≤ saldo; falha entre reserva/envio/commit sem duplicação | NÃO EXECUTADO |
| M07 | Pesos >1/negativos, saldo insuficiente, limites globais/por módulo/par, correlação/concentração declaradas e ordens pendentes: central reduz/rejeita; flag não remove risco | NÃO EXECUTADO |
| M08 | Filhos TWAP/VWAP: limite agregado do pai, parcial, reinício e deadline; risco revalidado, sem reserva contada duas vezes nem dois algoritmos no mesmo pai | NÃO EXECUTADO |
| M09 | Desativar com ordem aberta/parcial/UNKNOWN e posição: bloqueia entradas/filhos, monitora/cancela só se configurado, reconcilia; sem liquidação/reset/abandono | NÃO EXECUTADO |
| M10 | Reload inválido, troca concorrente de geração, migração/reativação: configuração atômica, pendências da versão anterior rastreáveis, sem replay ou apagar drawdown | NÃO EXECUTADO |
| M11 | Falha de módulo/fonte, feature vencida e timeout: consumidores dependentes pausam; falha financeira compartilhada bloqueia afetados; sem fallback implícito | NÃO EXECUTADO |
| M12 | IDs de instância/versão/hash em cada sinal/pai/filho/fill; atribuição determinística de custos/resíduo; soma dos subledgers e caixa = consolidado por ativo | NÃO EXECUTADO |
| M13 | Backtest causal com custos, janelas comparáveis e capital justo; parcial/atraso/sem fill no PAPER; dados point-in-time, nenhum vazamento futuro em ranking/notícias/ML | NÃO EXECUTADO |
| M14 | Composição sem manifesto, resource ownership conflitante e self-trade rejeitados; composição aprovada respeita budgets, contratos e filtros/STP suportados | NÃO EXECUTADO |
| M15 | Flags verdadeiras não autorizam LIVE: aprovação/gate/limite ausente ou expirado bloqueia executor; mudança de módulo/composição invalida liberação anterior; smoke SAM antes de publicação AWS | NÃO EXECUTADO |
| M16 | Documento individual criado somente junto da implementação e atualizado na Sprint, sem documentação detalhada antecipada de módulos ausentes; catálogo atualizado; confrontar regras/parâmetros/flags/risco com código/schema/testes, exemplos e cálculos, links/versões, comandos e evidências observadas; ausência ou desatualização bloqueia aceite | NÃO EXECUTADO |

Na Sprint 04, executar cenários do coordenador/combinação com módulos fake e marcar o alcance: isso não aprova a futura combinação de implementações reais. Casos específicos de TWAP/VWAP e multiativo são obrigatórios quando essa capacidade for introduzida, permanecendo pendentes para ela enquanto ausente; não bloqueiam a SMA isolada se forem explicitamente fora do seu escopo e a tentativa de ativação for rejeitada.

## Casos específicos por incremento opcional

Cada linha abaixo requer todos os casos específicos da seção correspondente nas [Sprints opcionais](../sprints/estrategias-opcionais.md), mais os casos comuns aplicáveis. Qualquer exclusão deve citar capacidade ausente e provar que sua ativação é rejeitada, sem marcar o módulo ausente como aprovado.

| Sprint | Módulo | Estado | Evidência futura |
|---|---|---|---|
| 04 | trend_sma | NÃO EXECUTADO | Guia 04, incluindo warm-up e cruzamentos |
| 12 | mean_reversion | NÃO EXECUTADO | Desvio/reversão, variância zero e regime adverso |
| 13 | breakout | NÃO EXECUTADO | Faixa anterior, confirmação e falso rompimento |
| 14A | dca | NÃO EXECUTADO | Calendário, orçamento e disparo perdido |
| 14B | rebalance | NÃO EXECUTADO | Pesos/bandas, mínimos e caixa confirmado |
| 14C | relative_momentum | NÃO EXECUTADO | Ranking, universo histórico e dados ausentes |
| 15A | twap | NÃO EXECUTADO | Tempo, filhos/restante e deadline |
| 15B | vwap | NÃO EXECUTADO | Volume causal, participação e benchmark |
| 16 | grid | NÃO EXECUTADO | Níveis, reservas, reancoragem e parcial |
| 17 | arbitrage | NÃO EXECUTADO | Custos/tempo de pernas e exposição residual |
| 18 | market_making | NÃO EXECUTADO | Inventário, latência, desconexão e ordens opostas |
| 19 | pairs | NÃO EXECUTADO | Estabilidade, risco de perna e rejeição de short |
| 20 | news_sentiment | NÃO EXECUTADO | Origem/publicação/recebimento, duplicação e texto não confiável |
| 21 | ml_signal | NÃO EXECUTADO | Treino temporal, versão, vazamento, drift e reprodutibilidade |

## Testes conjuntos e avaliação comparável

Testar cada módulo isolado e cada combinação declarada permitida, com pesos/algoritmo/ambiente/modo/pares reais da configuração. Usar pares de módulos para conflitos e também a configuração completa para saldo/risco agregado; pairwise sozinho não aprova interações de três ou mais. Combinação sem cobertura permanece inelegível. Exemplos de aceites futuros: duas instâncias em subcarteiras segregadas; tendência e reversão com weighted_targets declarado; ranking alimentando alocação sem dupla ordem; SMA + TWAP ou SMA + VWAP; fonte de sentimento/ML com consumidor nomeado. DCA/rebalanceamento sobre mesmo caixa sem precedência e grid/market making no mesmo inventário sem exclusividade são rejeitados por padrão.

Reproduzir dataset/split, capital total, custos, modelo de execução, benchmark e timestamps. Medir por módulo e consolidado retorno líquido/PnL realizado e não realizado, drawdown, exposição, turnover, fills, rejeições, taxas/spread/slippage e latência; acrescentar métricas específicas do catálogo. Não somar backtests que usam cada um 100% do mesmo capital para simular uma carteira combinada. Subledgers, atribuições/resíduos e custos devem reconciliar exatamente com a carteira; covariância/correlação e concentração devem ser reportadas quando combinar exposições. DCA com fluxos adicionais futuros deve usar benchmarks com os mesmos fluxos.

## Evidências e ativação

Para cada execução registrar ID, módulo/instância, versão/schema/estado/modelo, configuração/hash/geração e política de desativação/coordenação, ambiente/modo/par, versão do código/dataset, horários UTC, dependências, comandos reais, resultados e limitações. Registrar origem fixture/injeção/API. Não registrar segredos. Os comandos serão fixados no detalhamento elegível, sem presumir uma CLI inexistente.

Aceite técnico exige 100% dos casos obrigatórios aplicáveis aprovados, zero bypass de risco, duplicação, saldo negativo ou divergência inexplicada, custos/atribuições reproduzíveis e review. Habilitação exige opt-in explícito e evidência de elegibilidade daquela versão/configuração/composição. Promoção privada depende também dos gates Demo/Testnet e aprovação LIVE nova; resultados positivos em simulação não garantem rentabilidade. Módulos não escolhidos continuam desabilitados e não bloqueiam dependentes que não os utilizem.

Nenhum teste foi executado nesta revisão documental. Evidências históricas JSON não foram alteradas. Não foram criados recursos AWS, modelos, módulos ou ordens.

## Revisão documental obrigatória por módulo

Aplicar o [conteúdo obrigatório e as adaptações por papel](../estrategias/README.md). Registrar por módulo/Sprint/revisão: documento e catálogo, código/schema/artefato confrontados, comandos e evidências referenciados, cálculos de taxas/resultados conferidos, exemplos de flags isoladas/conjuntas aceitos ou explicitamente planejados, itens pendentes/não suportados e decisão documental APROVADA/PENDENTE. Validar o M16 tanto na primeira implementação quanto em mudanças de regras, interfaces, parâmetros, flags ou controles de risco. O aceite documental não transforma exemplo fictício em evidência financeira nem libera operação real.
