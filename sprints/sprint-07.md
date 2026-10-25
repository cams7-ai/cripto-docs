# Sprint 07 — Adapters AWS e validação local obrigatória com SAM CLI

Revisão: 25/10/2026. **Estado: PLANEJADA; implementação e validação NÃO EXECUTADAS.** Este contrato documenta o gate; detalhamento de interfaces, logical IDs e comandos executáveis depende da conclusão das etapas anteriores. Não autoriza implementação antecipada nem publicação.

## Objetivo e dependências

Preparar o handler Python e adapters AWS e validá-los localmente antes da publicação na AWS. Depende da [Sprint 06](sprint-06.md) concluída e de suas evidências revisadas. Modo exclusivamente PAPER, mercado Spot; sem credenciais privadas Binance, ordens externas ou infraestrutura provisionada.

Workspace `/home/cams7/Dev/Cripto`; aplicação em `cripto-bot`, documentos em `docs`. Caminhos previstos na aplicação: `adapters/storage`, `adapters/notifications`, `entrypoints`, `infra/sam` e `tests/sam_local`. Dependências de teste ficam fora do pacote de produção. E-mail AWS segue o contrato de `mail-sender-aws`, com transporte substituído por stub no ensaio local; integrações locais seguem a seção 4.5 do planejamento.

## Entregáveis e critérios de aceite

| ID | Condição verificável |
|---|---|
| AC01 | Registrar versões de SAM CLI, Docker, Python, ferramentas, imagem, runtime e arquitetura; dependências de produção derivadas do lock |
| AC02 | `sam validate --lint` aprovado no template efetivo; `sam build --use-container` aprovado para o destino; identificar template e artefato por hash/revisão |
| AC03 | `sam local invoke` executa o handler real empacotado, usando template de build, evento sintético e configuração PAPER; validar JSON funcional, logs e efeitos persistidos além do exit code |
| AC04 | Cobrir evento válido/inválido/duplicado/atrasado, modo proibido, kill switch, dados inválidos, timeout/falha de dependência, conflito de escrita, reinício e falha de notificação; zero ordens externas, duplicações ou divergências inexplicadas |
| AC05 | Contratos SQLite/DynamoDB aprovados; usar DynamoDB Local quando necessário para comprovar adapter, transações e conflitos, com endpoints e rede Docker locais explícitos |
| AC06 | SDK/HTTP usam fakes, MockTransport, Stubber/Moto ou serviços locais conforme necessário; sem perfis/segredos reais e sem acesso a serviços remotos; testar rejeição de destinos proibidos e redaction com segredos sintéticos |
| AC07 | Regressões pytest/cobertura, Ruff e mypy aprovadas; validar integridade/importação do pacote de produção e documentar diferenças do harness, sem embutir dependências de teste no deploy |
| AC08 | Registrar comandos reais, resultados por cenário, hashes e limitações no guia 07; todo caso obrigatório aprovado antes de publicar. Ferramenta ausente/caso não executado mantém publicação bloqueada |
| AC09 | SAM local cobre default sem estratégias, opt-in da composição escolhida, flags/modos inválidos, conflito de reserva e desativação; novo módulo/composição publicado exige smoke SAM do build correspondente. |

A especificação executável refinará os eventos e resultados esperados sem dispensar esses critérios. Ferramentas auxiliares são escolhidas conforme a dependência; não é obrigatório instalar emuladores sem uso. `sam local start-api` só se aplica a eventos HTTP existentes, sem adicionar API web ao escopo.

## Transição, limitações e recuperação

O aceite completo permite planejar a Sprint 08 e prosseguir apenas no fluxo de publicação autorizado. IAM, rede AWS, agendamento, alarmes, entrega e custos reais continuam pendentes do piloto AWS. SAM não emula integralmente esses serviços.

A exigência vale também para atualizações posteriores: repetir checks afetados e smoke SAM sobre o novo build quando mudar código, lock, template, runtime, arquitetura ou configuração relevante. Terraform permanece autoridade de deploy; não executar apply, deploy, sync ou upload neste gate local. LIVE permanece bloqueado por padrão e depende das validações e aprovação explícita previstas nas Sprints 09–11.

Falha exige corrigir, reconstruir e repetir testes afetados, preservando evidências e dados. Limpeza remove apenas containers/volumes/diretórios de teste identificados após preservar logs; nenhum recurso remoto é criado. Custo previsto de CPU, disco e preparação de imagens/dependências locais, sem pressupor infraestrutura AWS gratuita.

Referências: [planejamento, seção 8.1](../planejamento.md#81-validação-local-obrigatória-antes-de-publicar-na-aws), [guia 07](../testes/sprint-07-validacao.md) e [roteiro comum](../testes/validacao-pre-live.md).

## Contrato modular aplicável — revisão de 25/10/2026

Adotar a [arquitetura modular](../arquitetura-modular.md) e os casos aplicáveis do [guia modular](../testes/estrategias-modulares-validacao.md). Todos os módulos começam desabilitados; ensaios habilitam explicitamente somente instâncias implementadas por ambiente/modo/par. A elegibilidade é da versão/configuração/composição testada, sem exigir todo o catálogo. Esta atualização é documental, não implementa o schema nem altera evidências históricas.

## Documentação técnica como critério de conclusão

Se esta Sprint implementar ou alterar módulo, regra, interface/dependência/estado, dado/parâmetro/default/validação, flag/composição ou controle de risco, atualizar `docs/estrategias/<module_id>.md` e `docs/estrategias/README.md` na mesma entrega, conforme o [conteúdo obrigatório](../estrategias/README.md). Revisar exemplos, comandos, versões e evidências; separar efetivamente implementado de planejado/pendente. Registrar a decisão documental no guia desta Sprint; ausência/desatualização bloqueia conclusão. Se nenhum módulo for afetado, registrar essa conclusão e sua justificativa sem criar documento de módulo futuro.

## Estrutura dos bancos e aceite documental

Se esta Sprint criar/alterar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração de banco, atualizar na mesma entrega o documento correspondente em `docs/bancos/` e o [catálogo](../bancos/README.md): diagrama/modelo real, dicionário/DDL, operação, compatibilidade/migração ou rejeição, recuperação e referências/evidências. Confrontar com schema em fixture e testes aplicáveis; registrar a revisão no guia da Sprint. Documento ausente/desatualizado bloqueia conclusão, conforme seção 4.8 do planejamento. Sem mudança de banco, registrar ausência de impacto e justificativa. Esta revisão não executou teste ou migração.
