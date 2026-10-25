# Sprint 07 — Guia de validação local SAM antes da publicação AWS

Data: 25/10/2026. **Estado: NÃO EXECUTADO / gate PENDENTE.** Este roteiro é documental; ainda não há aceite de build, handler ou integração AWS desta Sprint.

## Preparação e roteiro futuro

Consultar [Sprint 07](../sprints/sprint-07.md) e [planejamento, seção 8.1](../planejamento.md#81-validação-local-obrigatória-antes-de-publicar-na-aws). Exigir Sprint 06 concluída/revisada. Executar comandos a partir de `/home/cams7/Dev/Cripto/cripto-bot`; salvar evidências sanitizadas em `/home/cams7/Dev/Cripto/docs/testes`. Confirmar versões e pré-requisitos quando a implementação existir; não instalar ou executar serviços nesta revisão.

| Ordem | Comando/ação planejada | Resultado a conferir |
|---|---|---|
| 1 | Registrar `sam --version`, `docker version`, Python e ferramentas do projeto | Compatibilidade e runtime/arquitetura de destino identificados |
| 2 | Regressões locais pytest/cobertura, Ruff e mypy | Contratos e invariantes aprovados, sem serviços remotos |
| 3 | `sam validate --lint --template-file <template>` | Template efetivo válido |
| 4 | `sam build --use-container --template-file <template>` | Build do runtime/arquitetura de destino com lock reproduzível |
| 5 | Preparar fakes e, se necessários, DynamoDB Local/serviços HTTP em rede Docker isolada | Endpoints locais explícitos, credenciais sintéticas, sem acesso à conta AWS |
| 6 | `sam local invoke <LogicalId> --template <template-de-build> --event <evento.json> --env-vars <env-local.json>` | Handler real carregado; saída JSON, logs e estado persistido coerentes |
| 7 | Repetir invocação com cenários negativos e evento duplicado | Erros previstos sem ordens externas nem efeito duplicado |
| 8 | Inspecionar pacote de produção, hashes e diferenças do harness | Imports funcionais e ausência de dependências de teste/segredos no pacote |

Os argumentos entre `<...>` são placeholders documentais, não comandos prontos. Fixar caminhos, logical ID, parâmetros de build e rede Docker na futura especificação executável. Usar o template gerado pelo build, sem invocar acidentalmente outro template do diretório. Downloads de preparação são separados do ensaio isolado. Não montar perfis AWS reais; SAM não impede sozinho acesso de rede do código.

Validar cada retorno funcional além do código de saída do SAM; capturar resposta e logs separados e comparar persistência antes/depois. Quando o harness substituir dependências, registrar exatamente quais, mantendo o handler/casos de uso reais e a inspeção do pacote de produção. Qualquer variante de teste não é o artefato de deploy.

## Matriz de resultados

| Critério | Resultado | Evidência |
|---|---|---|
| AC01 — ferramentas/runtime/arquitetura | NÃO EXECUTADO | Pendente |
| AC02 — validação e build em container | NÃO EXECUTADO | Pendente |
| AC03 — handler empacotado e JSON/efeitos | NÃO EXECUTADO | Pendente |
| AC04 — matriz de falhas e repetição | NÃO EXECUTADO | Pendente |
| AC05 — contratos de persistência | NÃO EXECUTADO | Pendente |
| AC06 — isolamento e proteção de logs | NÃO EXECUTADO | Pendente |
| AC07 — regressões e pacote de produção | NÃO EXECUTADO | Pendente |
| AC08 — registro completo antes de publicar | NÃO EXECUTADO | Pendente |
| AC09 — contrato modular/composição | NÃO EXECUTADO | Pendente |

Matriz mínima AC04: evento válido, inválido, duplicado e atrasado; modo DEMO/TESTNET/LIVE rejeitado; kill switch ativo; dados inválidos; dependência indisponível/timeout; conflito e reinício; falha de mensagem sem repetir negociação. Detalhar entrada/resultado esperado de cada caso antes da execução. Casos que exigem persistência em container devem informar rede, volumes e endpoints utilizados.

## Decisão e limites

100% dos critérios obrigatórios devem ser aprovados antes de publicar, com zero ordens externas, duplicações, divergências inexplicadas e vazamento de segredo sintético. Ausência de SAM/Docker ou teste não executado bloqueia o gate. Código, lock, template, runtime, arquitetura ou configuração relevante alterados exigem nova evidência sobre o build correspondente, inclusive em atualizações após a Sprint 08.

Não executar `sam deploy`, `sam sync`, `terraform apply` ou publicação de artefatos neste roteiro. Aceite local não prova IAM/Scheduler/VPC/quotas/entrega/custo em AWS; não libera LIVE. Preservar logs e dados antes de remover apenas recursos locais de teste identificados.

Fontes AWS consultadas em 25/10/2026: [sam validate --lint](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/validate-cfn-lint.html), [sam build](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli-build.html) e [sam local invoke](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli-local-invoke.html). Nenhum teste funcional, container ou chamada AWS foi executado nesta revisão documental.

## Validação modular adicional — pendente

Executar o critério modular adicionado à especificação desta Sprint e os casos aplicáveis do [guia modular](estrategias-modulares-validacao.md), registrando instâncias/versões, flags por ambiente/modo/par, pesos, política de coordenação/desativação, algoritmo e hash/geração. Distinguir ensaio isolado, combinação real e fakes do coordenador; aceites individuais não habilitam composição sem teste conjunto. Nenhum resultado foi obtido por esta revisão; modos privados e LIVE permanecem bloqueados conforme os gates.

## Verificação da documentação técnica — pendente

Na execução futura, identificar os módulos afetados e revisar seus arquivos em `docs/estrategias/` e o catálogo segundo o [conteúdo obrigatório](../estrategias/README.md) e o caso M16 do [guia modular](estrategias-modulares-validacao.md). Conferir comportamento/parametrização/flags/risco contra código, schemas e testes, cálculos do ciclo fictício, links/versão, comandos reproduzíveis e evidências esperadas versus obtidas. Registrar APROVADA/PENDENTE por documento e revisão; pendência bloqueia conclusão da Sprint. Caso nenhum módulo seja alterado, justificar essa constatação. Estado nesta revisão: NÃO EXECUTADO, sem evidência de implementação futura.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.
