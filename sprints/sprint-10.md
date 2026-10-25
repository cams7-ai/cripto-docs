# Sprint 10 — Spot Testnet complementar e recuperação de reset

Revisão: 25/10/2026. **Estado: PLANEJADA; implementação e validação NÃO EXECUTADAS.** Este contrato atualiza o roadmap, sem autorizar execução antecipada. O detalhamento executável de interfaces/comandos depende da conclusão e revisão das Sprints anteriores.

## Objetivo, escopo e dependências

Complementar a validação técnica de contratos e recuperação, sem avaliar a estratégia pelo retorno do Testnet.

Dependências: Sprint 09 aprovada, inclusive disponibilidade Demo e evidências dos ciclos virtuais.

Modo: PAPER/TESTNET; fundos virtuais e credenciais exclusivas do Spot Testnet.

Workspace exclusivo: `/home/cams7/Dev/Cripto`; aplicação Python em `cripto-bot`, documentação em `docs`. Mercado inicial: Spot, sem margem, alavancagem ou derivativos. Não modificar projetos LotoBot nem ativar produção.

## Entregáveis previstos

Composição/allowlist Testnet independente, contratos do adapter privado, identificação de época do ambiente, diagnóstico de reset e runbook de recuperação, sem copiar saldos/IDs entre ambientes.

## Critérios objetivos de aceite

| ID | Condição verificável |
|---|---|
| AC01 | Reconfirmar acesso permitido, endpoints, permissões e filtros; rejeitar mistura entre Demo, Testnet e LIVE antes de I/O privado. |
| AC02 | Executar ≥10 ciclos deliberados: ≥3 BUY e ≥3 SELL com fill e ≥3 cancelamentos sem fill; reconciliar ordens, fills e saldos via API. |
| AC03 | Repetir 100% da matriz técnica da seção 10.2, identificando simulação/injeção e evidência observada, sem inferir fill por preço de produção. |
| AC04 | Ensaiar reset em harness determinístico: desaparecimento de ordens/histórico e reposição de saldo bloqueiam novas ordens, preservam ledger anterior e exigem reconciliação e nova época identificada. Reset real só se observado, sem depender de sua ocorrência para concluir o ensaio. |
| AC05 | Reset não produz lucro/perda artificial nem reaplica saldo inicial no ledger antigo; repetir evidência afetada em janela consistente, sem apagar auditoria. |
| AC06 | Zero duplicação, UNKNOWN pendente ou divergência inexplicada; kill switch e barreiras de host/credenciais aprovados. |
| AC07 | Repetir contratos da composição escolhida no TESTNET, inclusive flags, atribuição de fills/custos e reset de estado por instância; módulos opcionais não escolhidos continuam desabilitados e não bloqueiam o piloto. |

## Evidência e decisão de transição

Todos os critérios e revisão permitem apenas preparar o dossiê LIVE da Sprint 11. Testnet não substitui Demo, PAPER ou avaliação fora da amostra.

Registrar versões, revisão do código, hash de configuração/modelo/dataset, intervalos UTC, execução dos casos, logs sanitizados, métricas, custos e decisão do revisor no [guia 10](../testes/sprint-10-validacao.md). Qualquer caso obrigatório não executado mantém o aceite pendente. Não inventar comandos ou resultados de implementação futura.

## Limitações, recuperação e custos

Preços e livro Testnet são independentes do mercado real. Ordens/histórico e saldos podem ser reinicializados; retorno e liquidez não são evidência de rentabilidade ou execução real.

Em falha, preservar evidências, interromper novos compromissos e reconciliar; não remover ledger ou alterar critério para obter aprovação. Em ambiente virtual, separar épocas de reset e configurações. Na etapa histórica/local, custo de disco/CPU/rede; nas etapas remotas, recotar infraestrutura/rede e dependências, sem pressupor gratuidade. Preparação LIVE não consome capital real.

Referências normativas: [planejamento, seções 6–10](../planejamento.md#10-gates-entre-ambientes-e-modos) e [roteiro comum de validação](../testes/validacao-pre-live.md). Esta revisão autoriza somente documentação.

## Contrato modular aplicável — revisão de 25/10/2026

Adotar a [arquitetura modular](../arquitetura-modular.md) e os casos aplicáveis do [guia modular](../testes/estrategias-modulares-validacao.md). Todos os módulos começam desabilitados; ensaios habilitam explicitamente somente instâncias implementadas por ambiente/modo/par. A elegibilidade é da versão/configuração/composição testada, sem exigir todo o catálogo. Esta atualização é documental, não implementa o schema nem altera evidências históricas.

## Documentação técnica como critério de conclusão

Se esta Sprint implementar ou alterar módulo, regra, interface/dependência/estado, dado/parâmetro/default/validação, flag/composição ou controle de risco, atualizar `docs/estrategias/<module_id>.md` e `docs/estrategias/README.md` na mesma entrega, conforme o [conteúdo obrigatório](../estrategias/README.md). Revisar exemplos, comandos, versões e evidências; separar efetivamente implementado de planejado/pendente. Registrar a decisão documental no guia desta Sprint; ausência/desatualização bloqueia conclusão. Se nenhum módulo for afetado, registrar essa conclusão e sua justificativa sem criar documento de módulo futuro.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.
