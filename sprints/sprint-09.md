# Sprint 09 — Binance Demo Spot e validação de solicitações

Revisão: 25/10/2026. **Estado: PLANEJADA; implementação e validação NÃO EXECUTADAS.** Este contrato atualiza o roadmap, sem autorizar execução antecipada. O detalhamento executável de interfaces/comandos depende da conclusão e revisão das Sprints anteriores.

## Objetivo, escopo e dependências

Validar parâmetros/assinatura e o ciclo privado completo por API em Demo Spot, com reconciliação de ordens e carteira.

Dependências: Sprints 07 e 08 aprovadas; ≥30 dias de PAPER AWS, ≥99% de ciclos elegíveis, zero duplicações/divergências e restauração/kill switch comprovados.

Modo: PAPER/DEMO após implementação autorizada; somente fundos virtuais e credenciais Demo próprias.

Workspace exclusivo: `/home/cams7/Dev/Cripto`; aplicação Python em `cripto-bot`, documentação em `docs`. Mercado inicial: Spot, sem margem, alavancagem ou derivativos. Não modificar projetos LotoBot nem ativar produção.

## Entregáveis previstos

Adapter privado Python com allowlist Demo, assinador/relógio testáveis, persistência de identidade antes do envio, consultas de ordens/fills/saldos, reconciliação, fixtures, configuração isolada e relatório auditável. Não criar componentes antes da Sprint elegível.

## Critérios objetivos de aceite

| ID | Condição verificável |
|---|---|
| AC01 | Confirmar e registrar disponibilidade Demo Spot para a conta/região e a origem AWS, acesso ao portal e criação de chave própria; sem acesso, PENDENTE e LIVE bloqueado. |
| AC02 | Verificar modo-host-conta-segredo; rejeitar chave/host de produção, redirects e fallback. Guard negativo comprova que DEMO não acessa recursos LIVE. |
| AC03 | Executar POST /api/v3/order/test com solicitação válida e testar assinatura, timestamp/recvWindow e parâmetros inválidos. Confirmar ausência de nova ordem, fill e alteração de saldo atribuível ao endpoint. |
| AC04 | Observar ≥14 dias consecutivos e ≥20 ciclos deliberados: ≥5 BUY e ≥5 SELL com fills e ≥5 cancelamentos sem fill; consultar ordens, trades e saldos na API e reconciliar cada ciclo. |
| AC05 | Aprovar 100% da matriz da seção 10.2: parcial/cancelamento restante, rejeição, timeout ambíguo, reinício, deduplicação, kill switch e indisponibilidade. Identificar injeção versus evidência da API. |
| AC06 | Zero efeito duplicado, UNKNOWN pendente ou divergência inexplicada; preservar intenção e reconciliar resultado desconhecido antes de qualquer repetição. |
| AC07 | Revalidar status, permissões e filtros do símbolo no ambiente; custo/comissão observados não são automaticamente os da conta real. |
| AC08 | Evidências Demo identificam módulo/instância/versão/hash/composição/algoritmo; testar elegibilidade e desativação/reconciliação; opt-in PAPER não habilita DEMO nem LIVE. |

## Evidência e decisão de transição

Todos os critérios e revisão permitem Spot Testnet complementar na Sprint 10. order/test não substitui ordens virtuais. Falta de Demo não autoriza pular para LIVE ou trocar de ambiente.

Registrar versões, revisão do código, hash de configuração/modelo/dataset, intervalos UTC, execução dos casos, logs sanitizados, métricas, custos e decisão do revisor no [guia 09](../testes/sprint-09-validacao.md). Qualquer caso obrigatório não executado mantém o aceite pendente. Não inventar comandos ou resultados de implementação futura.

## Limitações, recuperação e custos

Mercado Demo não é idêntico ao real e não prova execução/rentabilidade em produção. Disponibilidade da conta/região está PENDENTE nesta revisão. Não foram lidas credenciais nem consultada a conta.

Em falha, preservar evidências, interromper novos compromissos e reconciliar; não remover ledger ou alterar critério para obter aprovação. Em ambiente virtual, separar épocas de reset e configurações. Na etapa histórica/local, custo de disco/CPU/rede; nas etapas remotas, recotar infraestrutura/rede e dependências, sem pressupor gratuidade. Preparação LIVE não consome capital real.

Referências normativas: [planejamento, seções 6–10](../planejamento.md#10-gates-entre-ambientes-e-modos) e [roteiro comum de validação](../testes/validacao-pre-live.md). Esta revisão autoriza somente documentação.

## Contrato modular aplicável — revisão de 25/10/2026

Adotar a [arquitetura modular](../arquitetura-modular.md) e os casos aplicáveis do [guia modular](../testes/estrategias-modulares-validacao.md). Todos os módulos começam desabilitados; ensaios habilitam explicitamente somente instâncias implementadas por ambiente/modo/par. A elegibilidade é da versão/configuração/composição testada, sem exigir todo o catálogo. Esta atualização é documental, não implementa o schema nem altera evidências históricas.

## Documentação técnica como critério de conclusão

Se esta Sprint implementar ou alterar módulo, regra, interface/dependência/estado, dado/parâmetro/default/validação, flag/composição ou controle de risco, atualizar `docs/estrategias/<module_id>.md` e `docs/estrategias/README.md` na mesma entrega, conforme o [conteúdo obrigatório](../estrategias/README.md). Revisar exemplos, comandos, versões e evidências; separar efetivamente implementado de planejado/pendente. Registrar a decisão documental no guia desta Sprint; ausência/desatualização bloqueia conclusão. Se nenhum módulo for afetado, registrar essa conclusão e sua justificativa sem criar documento de módulo futuro.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.
