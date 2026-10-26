# Sprint 06 — Extração multiprojeto e PAPER contínuo local

Revisão: 26/10/2026. **Estado: PARCIAL — 06A/06B/06C implementadas/validadas; software 06D validado offline; piloto/gate global pendentes.** Documento agregador alinhado ao planejamento vigente. Substitui a organização anterior, de 25/10/2026, que concentrava a Sprint no piloto contínuo; seus critérios operacionais são preservados em 06D.

Registro da revisão documental original: esta entrega atualizava somente a documentação. Não cria projetos, move fontes/dados, executa testes, coleta, envia mensagens, inicia o piloto ou autoriza operações externas. O detalhamento executável de cada etapa deve preceder sua implementação e usar o estado real dos repositórios.

Referências principais: [planejamento](../planejamento.md), seções 4.5–4.10, 5, 6.3–6.5, 8–10 e 13; [Sprint 05](sprint-05.md), em especial o registro da execução e o ajuste analítico posterior; [guia 05](../testes/sprint-05-validacao.md), [validação DuckDB/Parquet](../testes/duckdb-parquet-validacao.md), [arquitetura modular](../arquitetura-modular.md) e [matriz modular](../testes/estrategias-modulares-validacao.md). Decisões: [ADR 0005](../decisoes/0005-estrategia-modular-e-persistencia.md), [ADR 0006](../decisoes/0006-backtest-historico-e-protocolo.md) e [ADR 0007](../decisoes/0007-duckdb-parquet-analitico.md).

## 1. Objetivo e incremento demonstrável

Entregar, na ordem **06A → 06B → 06C → 06D**, uma composição Python instalável por wheels, com bibliotecas de regras puras, dados públicos e análises, preservando o bot como proprietário da carteira, risco, coordenação, execução e backtest. Depois das extrações aprovadas, acompanhar dados públicos reais e simular localmente ordens, reservas, posições e recuperação durante o piloto PAPER.

Cada extração precisa demonstrar consumidor funcional, equivalência dos contratos e ausência de duplicação das regras. A entrega final demonstra a composição congelada operando continuamente, com relatórios diários, outbox, pausa/retomada e cenários de falha. Separar equivalência de software, observação de mercado e cenários injetados; lucro não é condição de aceite técnico nem prova de desempenho futuro.

Este agregador define sequência, fronteiras e aceites. Os arquivos `docs/sprints/sprint-06a.md` a `sprint-06d.md`, seus guias e prompts autossuficientes surgem no detalhamento da etapa elegível, sem criar placeholders das demais. O texto anterior da 06 não permite começar pelo piloto.

## 2. Diretórios, estado e pré-requisitos

Workspace exclusivo: `/home/cams7/Dev/Cripto`. Aplicação existente em `cripto-bot/`; documentação central em `docs/`, com Git independente. Cada novo projeto será irmão desses diretórios, com Git, manifest, versão, lock, testes e build próprios. Não criar repositório agregador, submódulos ou Git aninhado. Todos os arquivos de Cripto permanecem no workspace.

A Sprint 05 registra implementação e validação local/PAPER/backtest/BTCUSDT/15m; o guia complementar registra a camada DuckDB/Parquet aprovada. Esses são resultados documentais históricos, não resultados novos do piloto. As regressões e a integridade da baseline foram posteriormente conferidas em 06A, conforme seu guia. A configuração/modelo que vier a executar o piloto deve ser identificada separadamente.

| Dependência | Base documental disponível | Condição antes do trabalho dependente |
|---|---|---|
| D01 — Backtest 05 | Protocolo congelado, avaliação real, oráculos, relatórios e resultado do gate no guia 05 | Rever critérios/evidências, fontes e mudanças posteriores; reproduzir regressões pertinentes, sem reabrir o teste final |
| D02 — Ajuste analítico | DuckDB/Parquet, precisão, publicação, falhas e wheel no guia complementar | Rever evidências e compatibilidade com a versão usada; registrar limitações e resultados atuais |
| D03 — Identidade e ferramentas | `pyproject.toml`, `uv.lock` e pin Python do bot; referências da 05 e do ajuste analítico | Inspecionar HEAD, alterações locais, versões e hashes reais; preservar trabalho e registrar baseline por projeto; não atualizar dependências por conveniência |
| D04 — Estado e proveniência | Stores de mercado/financeiros/históricos distintos e registro de consumo final | Inventariar ownership, schemas, paths e fingerprints; preservar dados, locks, journal, checkpoints e registro de uso |
| D05 — Sequência | Decisão multiprojeto e layout da seção 9.2 do planejamento | 06B exige 06A aprovada; 06C exige 06B aprovada; 06D exige 06A–06C aprovadas e composição congelada |
| D06 — Piloto e mensagens | Critérios originais da 06 e contratos da seção 4.5 do planejamento | Detalhar relógio contínuo, dados, execução, retenção, canais e ensaios antes de 06D; envio efetivo somente no escopo explicitamente autorizado |

Falha em um pré-requisito mantém a etapa dependente pendente. Não declarar revisões limpas, hashes conferidos ou novo gate aprovado sem verificação efetiva. O relatório histórico não elege automaticamente a SMA para negociação privada.

## 3. Escopo e exclusões

Somente Python, ambiente local e modo PAPER; Spot sem margem, empréstimo, short, alavancagem ou derivativos. O escopo funcional inicial continua BTCUSDT/15m e SMA20/50 opt-in. Extração de biblioteca não cria estratégia nem habilita continuous implicitamente.

06A–06C usam fixtures e fontes já disponíveis, sem exigir nova coleta de 24 meses ou avaliação econômica. 06D usa coleta pública explícita e execução interna, sem construir cliente privado ou enviar qualquer mutação de negociação Binance, inclusive `order/test`. Rede pública e ensaios de mensagens pertencem aos comandos/cenários definidos no detalhamento, com guards e opt-in próprios.

Preservar CLI, defaults, configurações e resultados dos fluxos existentes: `check-config`, `run-once` NOOP, `collect-market`, `paper-*`, `strategy-*` e `backtest-*`. Não converter automaticamente bancos de uma modalidade em outra.

Fora da Sprint: AWS/deploy, credenciais Binance, DEMO/TESTNET/LIVE, API web, microsserviços, novas estratégias, multiativo, ranking/Sortino seletor, walk-forward, otimização e carteiras combinadas reais. As evoluções **BT-A–BT-F** permanecem na trilha opcional das seções 6.5 e 9.3 do planejamento, após 06D e conforme dependências. O modelo parcial do piloto não implementa automaticamente a simulação histórica de liquidez de BT-C. `cripto-backtest` e bibliotecas menores independentes continuam adiados.

## 4. Estrutura-alvo e fronteiras de arquitetura

Estrutura planejada, criada progressivamente na etapa correspondente:

```text
/home/cams7/Dev/Cripto/
├── docs/                          # Git e evidências centrais existentes
├── cripto-bot/                    # Git existente
│   ├── pyproject.toml
│   ├── src/cripto_bot/            # alvo da reorganização 06A
│   └── tests/
├── cripto-core/                   # 06A: Git e pacote independentes
│   ├── pyproject.toml
│   ├── src/cripto_core/
│   └── tests/
├── cripto-market-data/            # 06B: Git e pacote independentes
│   ├── pyproject.toml
│   ├── src/cripto_market_data/
│   └── tests/
└── cripto-analytics/              # 06C: Git e pacote independentes
    ├── pyproject.toml
    ├── src/cripto_analytics/
    └── tests/
```

Até a reorganização validada da 06A, o caminho dos fontes do bot continua `modules/trading/src/cripto_bot`. `src/` ficará diretamente na raiz de cada projeto Python; os subpacotes internos não recebem outra árvore de projeto ou Git. Caminhos `docs/...` são relativos ao workspace; comandos uv/Python executam na raiz do projeto identificado no guia.

| Projeto | Responsabilidade | Dependências e restrições |
|---|---|---|
| `cripto-core` | Contratos/DTOs, precisão/arredondamento, custos/dimensionamento e indicadores/SMA puros efetivamente compartilhados | Sem import de consumidores, HTTP, banco, DuckDB, ambiente, credenciais, relógio implícito ou estado financeiro persistido |
| `cripto-market-data` | Coleta pública, normalização, validação, store/checkpoint de mercado, manifestos e CLI | Depende de core; não importa bot/analytics nem altera ledger; rede explícita no entrypoint autorizado |
| `cripto-analytics` | DuckDB/Parquet, consultas e apresentação de relatórios por snapshots/fluxos reconciliados somente leitura | Depende de core; não importa bot/market-data, não reserva saldo, escreve no ledger ou refaz decisões/fills |
| `cripto-bot` | Composição, configuração/flags, coordenação, risco operacional, carteira, executor, backtest e recuperação | Consome as bibliotecas; implementa adapters das portas de leitura; conserva atomicidade e o registro de consumo final |

Chamadas Python síncronas e composição explícita permanecem suficientes. Não passar `BacktestStore` concreto como contrato entre projetos. Não manter duas implementações de uma mesma regra; fachada temporária compatível apenas delega à fonte única. Dependências opcionais desabilitadas não são importadas; runtime sem perfil analítico não carrega DuckDB por import de domínio. Dependência necessária ausente falha claramente, sem sucesso parcial fictício.

## 5. Etapas e sequência de entrega

### 5.1 06A — Layout do bot e extração de `cripto-core`

Dependência: D01–D04 revisadas e inventário de interfaces/fingerprints disponível.

1. Registrar baseline e reorganizar `cripto-bot/modules/trading/src/cripto_bot` para `cripto-bot/src/cripto_bot`, preservando pacote `cripto_bot` e console script `cripto-bot`.
2. Atualizar descoberta de pacotes, tipagem/qualidade/cobertura, fixtures/testes que referenciem fontes, resolução de caminhos e fingerprints; atualizar README, arquitetura e ADRs afetados. Dados/configuração/relatórios conservam locais e identidade.
3. Validar regressões, build e wheel do bot em ambiente neutro **antes** da extração; registrar esse marco separadamente.
4. Criar `cripto-core/src/cripto_core`, extrair regras puras usadas e integrar o bot como consumidor. Validar contratos, precisão e causalidade contra oráculos independentes e a baseline.
5. Registrar API pública, matriz de versões, locks, hashes dos wheels/fontes e smoke da composição instalada, sem I/O ou ciclos de imports no core.

Avanço: layout e integração core aprovados; não usar a extração para mudar parâmetros, custos, limites ou semântica da SMA.

### 5.2 06B — Extração de `cripto-market-data`

Dependência: 06A aprovada.

Extrair coleta pública, normalização, validação, persistência/checkpoint de mercado e manifestos para `src/cripto_market_data`. Preservar `collect-market` no bot por delegação; o detalhamento define a CLI própria efetiva e seus contratos, sem inventar comandos neste agregador.

Exigir continuidade, deduplicação, hashes canônicos, retomada, rollback/falha de exportação e rejeição de fonte inválida equivalentes à baseline. Tratar paths, descoberta de raiz e symlinks sem derivar o diretório de dados de `site-packages`. Testar o pacote instalado fora do checkout, com fakes/guards de rede. Coleta pública real somente quando explicitamente prevista e autorizada; nunca implícita em backtest ou relatório.

Avanço: biblioteca/CLI e delegação aprovadas, sem escrita ou migração do ledger financeiro, sem dependência inversa do core.

### 5.3 06C — Extração de `cripto-analytics`

Dependência: 06B aprovada; core e contratos de dados revisados. O [detalhamento 06C](sprint-06c.md) foi implementado/testado; aceite final aprovado conforme seção 19.

Extrair exportação DuckDB/Parquet e apresentação de relatórios para `src/cripto_analytics`, por portas somente leitura. O bot conserva os comandos existentes por delegação. Métricas oficiais permanecem no núcleo Decimal; SQLite permanece autoritativo. Valores financeiros exatos continuam sem passagem silenciosa por float ou redução de precisão.

Conferir equivalência CSV/JSON/HTML/Parquet, resumos/contagens SQL, manifesto e publicação atômica após reconciliação. Exercitar snapshots vazio/parcial/concluído, volume representativo, orçamento de memória/spill, falha de conversão e publicação/reexportação sem novo fill. Preservar restrições de acesso externo/extensões do motor analítico e os diretórios permitidos, conforme o ajuste existente. Separar tempo de consulta, exportação e reconciliação; não prometer aceleração do replay pela extração.

Avanço: composição integrada funciona antes de aposentar a implementação anterior; banco financeiro e identidade selada dos protocolos antigos permanecem preservados.

### 5.4 06D — PAPER contínuo local com a composição validada

[Especificação/execução 06D](sprint-06d.md): software D-M1–D-M3 validado offline; observação real/mensagens e D-M4/D-M5 pendentes. Estado SOFTWARE_VALIDATED/PILOT_PENDING; ver seção21 e guia próprio.

Dependência: 06A–06C aprovadas, versões/hashes/configuração/modelo congelados e pré-requisitos operacionais revisados.

Entregar o piloto original: ciclo contínuo com dados públicos reais, execução interna, carteira/risco/coordenação sob controle do bot, outbox/clientes HTTP locais, relatórios diários e runbook de pausa/retomada. Modelo de execução ampliado e versionado, com fill integral, parcial, atraso, ausência de fill e cancelamento. Detalhar antes de executar o relógio, validade de dados/cotações, frequência, filtros, orçamento do ciclo e política de recuperação de evento atrasado; não executar sinais antigos para compensar indisponibilidade.

Observar pelo menos sete dias consecutivos e ≥99% dos ciclos elegíveis. Fixar previamente denominador, critério de elegibilidade e manutenções; não excluir falhas para melhorar a métrica. Rejeição válida de risco/HOLD não equivale a falha de processamento, nem todos os ciclos precisam produzir fill. Separar a amostra observada dos drills determinísticos.

Sem módulo habilitado, não iniciar negociação simulada ou carteira implicitamente. A configuração de continuous exige opt-in próprio; não herda habilitação de fixture/backtest. O detalhamento deve definir o comportamento de inicialização/NOOP e os comandos reais antes de fornecê-los como instruções executáveis.

## 6. Configuração modular, risco e mensagens

Todos os módulos começam desabilitados; opt-in por instância, ambiente, modo, tipo de avaliação e par. Somente implementações registradas e compatíveis são elegíveis. Configuração inválida falha integralmente antes de efeitos; não há import dinâmico arbitrário ou fallback para estratégia não habilitada. Risco, reconciliação e kill switch não são opcionais.

A política inicial continua `exclusive_owner`. Testar isolamento, conflitos, orçamento concorrente e composição com fakes de contrato sem apresentá-los como validação de estratégias reais ausentes. Composição real não suportada deve ser rejeitada. Capital/reservas, atribuição de inventário e limites globais/por instância permanecem centralizados. Desativação bloqueia entradas, mantém custódia/monitoramento e DRAINING com posições remanescentes, sem venda, transferência ou reset automáticos. Reload/reativação preservam geração, deduplicação, custos e pico de drawdown; UNKNOWN bloqueia novos compromissos afetados até reconciliação.

Em 06D, introduzir porta de notificação, outbox e clientes HTTP locais conforme seção 4.5 do planejamento: e-mail via `mail-sender`; WhatsApp via `whatsapp-notify`, quando habilitado, com consulta da sessão e fallback para e-mail configurado. Não incorporar navegador/QR nem gerenciar silenciosamente sessão compartilhada. Transporte Lambda pertence à 07; IAM/rede/entrega AWS à 08.

Persistir evento/tentativas/canal confirmado; validar resposta/payload e limitar espera, repetição e frequência. Timeout pode deixar entrega desconhecida, sem garantia de exactly-once; registrar a incerteza. Falha de mensagens nunca reexecuta negociação. Se ambos os canais falham, manter outbox e diagnóstico para alarme independente. Testes de contrato usam fakes/MockTransport sem enviar mensagens; ensaios de entrega efetiva são separados, opt-in e com destinatários de teste autorizados. Não alterar projetos de referência.

## 7. Persistência, protocolo e compatibilidade

O bot conserva journal, ledger, reservas, fills, risco persistente, writer lock/CAS e atomicidade entre decisão/intenção/checkpoint e efeitos financeiros. A biblioteca de dados possui estado de mercado; analytics recebe snapshot/fluxo somente leitura. Não criar um segundo ledger para facilitar a extração.

Preservar stores e datasets anteriores, seus schemas/modelos e paths. Incompatibilidade deve falhar explicitamente; mudança necessária exige plano de migração/compatibilidade e recuperação no detalhamento, sem conversão automática ou exclusão de bancos. O estado contínuo exige modelo/versão explícitos e diretório próprio quando incompatível; não retomar carteiras históricas como carteiras do piloto.

O registro `cripto-bot/data/backtest-usage/test-usage.sqlite3` permanece no bot, com o histórico existente. Não inicializar registro vazio em outro projeto. Protocolos novos identificam versões/hashes das bibliotecas e lock do consumidor; em uso editável, identificar fontes efetivos, inclusive ao retomar. Reorganização altera fingerprint sem criar outra amostra independente.

Regressões usam fixtures e oráculos financeiros/causais: saldos, quantidades, custos, decisões, métricas e efeitos idempotentes. Não forçar igualdade de fingerprint de código alterado nem ocultar a mudança para satisfazer um hash global. Reexportação de protocolo antigo preserva identidade selada e somente lê o estado reconciliado; não refaz estratégia/fills nem reabre teste final consumido. Resultados retrospectivos conhecidos não passam a evidência independente por mudança de layout/pacote/ID.

## 8. Entregáveis e verificação por etapa

| Entregável | Verificação exigida |
|---|---|
| Fontes reorganizados e bibliotecas usadas pelo consumidor | API pequena, fonte única de regras, imports permitidos, CLI/defaults compatíveis e contratos de dados/precisão preservados |
| Manifest, versão, lock, testes e wheel de cada projeto | Ferramentas fixadas/compatíveis, dependências necessárias, builds identificados e instalação integrada em ambiente neutro |
| Configurações/fixtures de exemplo | Defaults desabilitados, opt-in isolado por escopo, parâmetros válidos e guards negativos reproduzíveis |
| Modelo/CLI contínuos, outbox e clientes locais em 06D | Contratos e comandos reais documentados, execução interna, falhas/retomada e rede autorizada separados |
| Relatórios por etapa e diários em 06D | Valores confrontados com snapshot/ledger, HTML ou formato legível revisado visualmente, manifestos e limites explícitos |
| Guias/evidências centrais e documentos técnicos | Revisões/hashes da composição, cenários e resultados reais, pendências/recuperação e decisão por etapa |

Rodar Ruff/formatação/mypy conforme os projetos, testes unitários/contratuais e regressões de consumidores afetados. Validar import/CLI com wheels das dependências instalados, sem `PYTHONPATH`, instalação editable ou checkout irmão implicitamente importável. Fixar cwd/paths absolutos dos ensaios; manter arquivos no workspace. Não impor o número histórico de testes como contagem fixa nem registrá-lo como execução nova.

Não há novos comandos executáveis de aplicação definidos por esta revisão. Cada especificação de etapa deve fornecer comandos verificados para instalação locked, qualidade, build, smoke, demonstração, reconciliação e recuperação, com artefatos esperados e códigos de saída. A ausência desse detalhamento impede usar o agregador como prompt genérico para implementar as quatro etapas de uma vez.

## 9. Critérios objetivos de aceite

AC01–AC08 conservam os temas do contrato anterior e aplicam-se ao piloto 06D. AC09–AC18 acrescentam aceites das extrações e da integração. **AC09–AC13 cumpridos nas extrações 06A–06C; AC06 e AC14–AC17 verificados no alcance das composições entregues**, conforme seu guia. Os critérios operacionais do piloto e AC18 permanecem pendentes; os casos comuns serão repetidos no alcance de cada nova composição. Não atribuir os testes sintéticos da 06A aos aceites operacionais de 06D.

| ID | Etapa | Condição verificável |
|---|---|---|
| AC01 | 06D | Pelo menos sete dias consecutivos e ≥99% dos ciclos elegíveis; registrar numerador/denominador, intervalos UTC e manutenções predefinidas |
| AC02 | 06D | Fill integral, múltiplos parciais, atraso, ordem limitada sem fill e cancelamento do restante; tocar preço não garante execução |
| AC03 | 06D | Quantidade cumulativa ≤ solicitada, taxas por fill, saldos/reservas corretos e liberação somente do restante cancelado; zero divergência inexplicada |
| AC04 | 06D | Timeout, reinício, repetição de evento e falhas entre transações sem duplicar fill/ledger; kill switch bloqueia novas entradas sem liquidar automaticamente |
| AC05 | 06D | Dados atrasados/lacunas, saldo insuficiente, filtros e limites bloqueiam efeitos indevidos; sem preço válido não fabricar fill |
| AC06 | Todas | Guards rejeitam credenciais e mutações Binance, inclusive `order/test`; execução não constrói cliente privado; backtest/report sem rede e coleta somente explícita |
| AC07 | 06D | Falha dos canais, fallback, resultado desconhecido e recuperação da outbox sem repetir negociação; entrega efetiva separada dos testes de contrato |
| AC08 | 06D | Isolamento/conflitos e orçamento concorrente, risco global/instância, reload/desativação com pendências e posições; composição ausente rejeitada e flags sem permissão privada |
| AC09 | 06A | Layout `src/cripto_bot` validado antes da extração: empacotamento, imports, CLI, resolução de paths e regressões preservados |
| AC10 | 06A | Core puro sem efeitos/ciclos de imports; custos/dimensionamento/SMA equivalentes aos oráculos, sem cópias divergentes e com bot consumidor funcional |
| AC11 | 06B | Coleta delegada, parsers/qualidade, checkpoint/retomada e hashes compatíveis; dados inválidos, concorrência e falhas tratados sem tocar ledger |
| AC12 | 06C | Métricas/valores exatos e formatos compatíveis, contagens SQL coerentes, snapshot vazio/parcial/concluído e volume representativo verificados |
| AC13 | 06C | Falha de memória/conversão/publicação preserva ledger; reexportação sem novos sinais/fills; publicação atômica e restrições analíticas mantidas |
| AC14 | 06A–06C | Todos os wheels integrados instalados em ambiente neutro; comandos/imports independentes de checkouts/editables/PYTHONPATH; versões/hashes/locks registrados |
| AC15 | Todas | Paths/symlinks/ownership e schemas preservados ou incompatibilidade explicitamente rejeitada; zero migração silenciosa ou perda de estado/evidência |
| AC16 | 06A–06C | Dependências extraídas entram na identidade experimental; registro de consumo final preservado; fixtures/oráculos usados sem reabrir avaliação final |
| AC17 | Todas | Documentação técnica/bancos/READMEs/API e exemplos atualizados conforme impacto, catálogo e revisão visual dos relatórios; pendência documental bloqueia conclusão |
| AC18 | Integração/06D | Guias das quatro etapas aprovados, composição congelada, limitações/rollback/runbook e revisão de evidências completos antes de declarar 07 elegível |

## 10. Evidências, documentação e decisão de transição

O [guia 06](../testes/sprint-06-validacao.md) existente permanece como roteiro anterior, sem evidência nova de execução; deverá ser alinhado ao papel de consolidação das quatro etapas antes dos ensaios. Os guias `docs/testes/sprint-06a-validacao.md` a `sprint-06d-validacao.md` serão criados no detalhamento de cada etapa; este agregador não cria arquivos vazios nem links que pressuponham sua existência.

Cada guia identifica revisões/alterações locais, ferramentas, versões/hashes dos projetos/wheels/locks, configuração/modelo/dataset e schemas, comandos efetivos, intervalos UTC, resultados esperados/obtidos, métricas/custos, logs sanitizados, manifestos e limitações. Separar testes executados, apenas planejados, não aplicáveis justificados e pendentes. Caso obrigatório sem execução mantém o aceite pendente; não reduzir critérios para ocultar falha.

Na implementação, criar/atualizar READMEs/API das bibliotecas e arquitetura/ADRs centrais conforme a distribuição entregue. Atualizar `docs/estrategias/<module_id>.md` e o [catálogo](../estrategias/README.md) quando regras/interfaces/dependências/estado/dados/parâmetros/flags/risco do módulo forem afetados. Não criar documento fictício de estratégia para uma biblioteca de infraestrutura ou módulo futuro. Ausência de impacto precisa de justificativa no guia.

Se mudar estrutura, relações, constraints/índices/triggers, formato persistido, versão ou migração, atualizar o documento real em `docs/bancos/` e o [catálogo](../bancos/README.md), com modelo/diagrama, dicionário/DDL, operação, compatibilidade/rejeição, recuperação e evidências. Confrontar com schema em fixture e testes; sem alteração, registrar a justificativa. Documentação ausente/desatualizada bloqueia aceite.

Aprovação de 06A libera somente o trabalho dependente da 06B, e assim sucessivamente. Somente 06A–06D aprovadas e revisão da composição permitem declarar a **Sprint 07 elegível para detalhamento/revisão**, sem iniciá-la automaticamente. A 07 deve incorporar bibliotecas e locks reais e validar SAM local; piloto AWS depende também da 08. Gates privados 09–11 e aprovação real permanecem independentes. A aprovação técnica da 06 não demonstra rentabilidade ou execução real.

## 11. Limitações, custos e recuperação

A extração modifica organização/empacotamento e proveniência do código; pode revelar dependências ocultas de paths/imports, aumentando o trabalho de compatibilidade. O piloto usa mercado real, mas carteira e fills internos não medem fila, impacto próprio ou liquidez/fill da corretora. Relatórios devem distinguir observação contínua e falhas injetadas. Seleção/otimização histórica não faz parte desta entrega.

Custos: CPU, disco, rede pública e retenção local; nenhum recurso AWS nesta Sprint. Estimar volume dos journals/exportações, memória/conversão analítica, orçamento de chamadas e timeouts/canais no detalhamento. Medir por etapa sem supor gratuidade de serviços externos; os sete dias de observação não podem ser comprimidos em prazo de desenvolvimento.

Em falha, bloquear novos compromissos, preservar estado/evidências e reconciliar. Rollback restaura versões/locks compatíveis de toda a composição, sem sobrescrever fontes alheios ou remover dados. Incompatibilidade persistida exige plano específico; não apagar ledger, dataset, outbox, pico de risco ou registro final para destravar execução. Ensaios sintéticos usam diretórios/identidades próprios, sem reset de carteira operacional. Runbook de 06D deve cobrir pausa, custódia, restart, reconciliação, pendências, falha de dados/canais e encerramento do piloto.

## 12. Prompt para detalhar a próxima etapa elegível

Este prompt é de **documentação**, não de implementação. Após o detalhamento/revisão, a etapa terá seu próprio prompt executável, com caminhos/comandos/contratos concretos, como na estrutura da Sprint 05.

```text
Em /home/cams7/Dev/Cripto, detalhe somente a próxima etapa elegível de
06A -> 06B -> 06C -> 06D. Leia docs/planejamento.md (4.5–4.10, 5, 6, 8–10,
13), docs/sprints/sprint-05.md e sprint-06.md, guias/evidências da 05 e do
ajuste DuckDB/Parquet, arquitetura, ADRs e contratos de estratégia/bancos.
Inspecione código, testes, manifests, locks, pins, revisões e alterações locais
dos projetos efetivamente existentes, preservando trabalho, dados e segredos.
Não presuma extrações realizadas ou evidências novas aprovadas.

Confira os pré-requisitos e identifique a etapa ainda não concluída. Se uma
dependência falhar, registre a pendência e a correção necessária, sem detalhar
trabalho dependente como pronto. Para 06A, inclua layout src na raiz do bot,
sua validação antes da extração e depois core com consumidor funcional.
Para 06B/C, respeite ownership e direções de dependência. Para 06D, exija as
três extrações aprovadas e a composição congelada antes do piloto.

Produza apenas docs/sprints/sprint-06a.md, 06b.md, 06c.md ou 06d.md da etapa
elegível e atualizações documentais necessárias no agregador/planejamento.
Defina o guia de validação correspondente no detalhamento, diferenciando
roteiro e execução. Não crie placeholders de etapas futuras nem projetos,
não mova código/dados, não rode otimizações, piloto, rede ou mensagens,
não provisione e não altere projetos de referência. Use Python/local/PAPER,
Spot/BTCUSDT/15m; modos privados e trilha opcional BT-A–BT-F ficam fora.

Especifique objetivo demonstrável, escopo/exclusões, baseline verificada,
interfaces/arquivos, tarefas ordenadas, esquema e flags, matriz de versões,
fingerprints, compatibilidade/rollback, critérios positivos/negativos e de
falha parcial, testes, evidências, custos/retencao e recuperação. Confirme
fontes oficiais vigentes para APIs/dependências efetivamente alteradas.
Preserve CLI/defaults, regras puras, Decimal e ledger/reconciliação do bot;
não duplicar regras nem depender de imports do checkout irmão.
Não reabrir a janela final da 05 nem recriar seu registro em outro projeto.

Inclua prompt de implementação autossuficiente limitado à etapa, com raízes
absolutas, documentos/dependências numerados, comandos verificados de
instalação locked/qualidade/build/wheel/regressões/demonstração, guards e
resultados esperados, evidências e critérios de conclusão. Não invente
comandos de funcionalidades futuras como já implementados. Em 06D,
separe contratos sem rede de coleta pública e entregas de mensagens opt-in;
defina previamente os sete dias, os ciclos elegíveis e os drills.
Exija documentação incremental dos módulos/bibliotecas e bancos afetados,
revisão visual dos relatórios e atualização dos guias com resultados reais.
O detalhamento não autoriza executar a etapa ou promover modo.
```

## 13. Registro da atualização documental original

Em 26/10/2026, este documento foi reorganizado como agregador 06A–06D, usando o planejamento vigente e a Sprint 05 como referências de dependências, contratos, proveniência, estrutura de aceite e documentação. Os critérios operacionais AC01–AC08 foram preservados e vinculados a 06D, com AC06 abrangendo os guards de todas as etapas; os demais critérios tornam explícita a validação das extrações e da composição instalada.

Nenhuma etapa foi implementada ou validada nesta revisão. Os resultados da Sprint 05 e do ajuste analítico continuam históricos e separados. Registro posterior em 26/10/2026: a [Sprint 06A](sprint-06a.md) foi especificada após inspeção estática e conferência de 120/120 hashes da evidência analítica. Implementação/testes continuam pendentes; a próxima ação é revisar essa especificação. Não iniciar diretamente o piloto nem antecipar BT-A–BT-F.


## 14. Consolidação da etapa 06A

06A implementada e validada em 26/10/2026: M1 aprovado antes de extrair o core; M2 com 533 testes do bot, 54 do core, qualidade/build/wheels, 22 fluxos por smoke e 48 curvas sintéticas equivalentes. Identidade inclui o core efetivamente carregado; dados/DDL/registro final preservados. Cache frio completo não comprovado; reutilização de dependências verificadas da baseline documentada. Ver [especificação 06A](sprint-06a.md#14-registro-da-implementação-em-26102026), [guia](../testes/sprint-06a-validacao.md) e [evidências](../testes/sprint-06a-evidencias.json).

A próxima etapa elegível é o detalhamento/revisão de 06B. 06B/06C/06D não foram iniciadas; a Sprint 06 como um todo continua parcial, sem liberação automática da 07 ou do piloto. O registro da seção 13 descreve a entrega documental anterior, não o estado final da 06A.


## 15. Detalhamento da próxima etapa — 06B

Em 26/10/2026, a [Sprint 06B](sprint-06b.md) foi especificada após conferir os 127 hashes e seis artefatos da 06A e os repositórios limpos. Biblioteca/CLI, fronteiras de proveniência, compatibilidade de store/manifestos, B01–B18 e prompt de implementação futura estão definidos. Estado: especificada, aguardando revisão; implementação/testes ainda não executados. Não foram criados market-data/analytics nem iniciados 06C/06D; o gate global da 06 e a 07 continuam pendentes.


## 16. Consolidação da etapa 06B

06B implementada e validada offline em 26/10/2026: B-M1 baseline 533 testes; B-M2 standalone 120 testes/CLI sem bot; B-M3 integração 537 testes/22 comandos por três wheels. B01–B18, qualidade, builds, compatibilidade/locks/store/manifestos, proveniência/relatório anterior e equivalência financeira estão no [guia 06B](../testes/sprint-06b-validacao.md), nas [evidências](../testes/sprint-06b-evidencias.json) e no [relatório](../testes/relatorios/sprint-06b/report.html). Cache frio completo não demonstrado; reutilização verificada da baseline, sem rede de mercado. Core/artefatos anteriores e registro final preservados.

AC11 cumprido; AC06/AC14/AC15/AC16 foram verificados no recorte da composição 06B, devendo ser repetidos conforme as etapas seguintes. AC12/AC13 e critérios operacionais 06D continuam pendentes. Os registros das seções 13–15 são históricos. Próxima etapa elegível: detalhar/revisar 06C, sem criá-la/implementá-la nesta execução. Sprint 06 continua parcial; 07 não é liberada.


## 17. Detalhamento da próxima etapa — 06C

Em 26/10/2026, a [Sprint 06C](sprint-06c.md) foi especificada após conferir 185/185 hashes e 12/12 arquivos registrados nas evidências da 06B, sem divergência; os quatro repositórios estavam limpos no início. Define portas somente leitura, ownership dos snapshots/métricas no bot, biblioteca de apresentação/DuckDB/Parquet, CLI de validação/consultas de exports, C-M1–C-M3/C01–C18, instalação por quatro wheels e prompt autossuficiente de implementação futura.

Estado: especificada, aguardando revisão; implementação/testes não executados nesta entrega. Nenhum projeto analytics, guia vazio, instalação/build, relatório econômico, migração ou piloto foi criado/executado. Próxima ação: revisar a especificação antes de solicitar implementação. 06D/gate global/07 continuam pendentes; 06A/06B e suas evidências permanecem preservadas.


## 18. Registro inicial 06C — aceite então pendente

06C implementada em 26/10/2026: analytics standalone 28 testes; bot integrado 542, qualidade/build e quatro wheels/22 comandos aprovados. Projeções/formatos/precisão/portas readonly, compatibilidade selada e medições documentados no [guia](../testes/sprint-06c-validacao.md), nas [evidências](../testes/sprint-06c-evidencias.json) e no [relatório](../testes/relatorios/sprint-06c/report.html).

C01/C12/C18 pendentes: quatro artefatos 06A foram encontrados substituídos após baseline inicialmente íntegra; origem/recuperação ainda não esclarecidas. Não houve aceitação silenciosa nem alteração das evidências anteriores. AC12/AC13 têm provas técnicas; aceite integrado/comum permanece condicionado à resolução. Próxima ação: resolver hashes de artefatos e revisar 06C. 06D/gate global/07 não liberados. Registros anteriores conservam contexto histórico.


## 19. Aceite 06C concluído após esclarecimento externo

Reconstrução externa confirmada pelo responsável; conteúdo/inventário de wheels/sdists verificado contra fontes 06B e composição/locks testados inalterados. C01/C12/C18 resolvidos; C01–C18/C-M1–C-M3 aprovados offline conforme [guia](../testes/sprint-06c-validacao.md), [prova complementar](../testes/sprint-06c-reconstrucao-externa.json) e [relatório](../testes/relatorios/sprint-06c/report.html). Hashes históricos/atuais separados; não afirmar que os quatro artefatos reconstruídos são os originais 06A. Limitação de rollback exato documentada, sem restaurar/apagar trabalho externo.

AC12/AC13 cumpridos; critérios comuns de composição verificados no recorte 06C, a repetir conforme a evolução. 06D fica somente elegível para detalhamento/revisão. Critérios operacionais/piloto/gate global/07 continuam pendentes; Sprint 06 ainda parcial. Seção 18 preserva o estado anterior ao esclarecimento.


## 20. Detalhamento da próxima etapa — 06D

Criada a [especificação 06D](sprint-06d.md) após conferir 214/214 hashes e 16/16 artefatos atuais da 06C, com cinco repositórios limpos no início. Define implementação incremental offline, modelo/store parcial separado, scheduler/clock/causalidade, controles/custódia, outbox/workers/clientes locais, protocolo de sete dias UTC/672 slots/≥666 válidos e relatórios/drills separados. D01–D22 e prompt autossuficiente distinguem preparo de software e operação externa autorizada.

Estado: especificada, aguardando revisão/implementação. Não houve suíte/build, abertura de banco, coleta, mensagem ou piloto nesta revisão. Autorizações para dados públicos e destinatários de teste não são presumidas; falta de período/recurso mantém o respectivo marco pendente. Próxima ação: revisar a especificação. Nenhum critério operacional 06D ou gate 07 foi liberado por este detalhamento.


## 21. Execução offline 06D — SOFTWARE_VALIDATED/PILOT_PENDING

Modelo contínuo parcial isolado, scheduler/clock/controles/custódia, outbox/entrega local e snapshots implementados. Baseline542; suíte635, revisão final108 casos sobrepostos, analytics30;31 comandos instalados,48 curvas sintéticas e6 arquivos exatos/Parquet comparados. Core/dados e16 artefatos anteriores preservados; analytics0.1.1 apenas renderer. [Guia](../testes/sprint-06d-validacao.md), [evidências](../testes/sprint-06d-evidencias.json), [relatório](../testes/relatorios/sprint-06d/report.html), [módulo](../modulos/paper-continuous.md).

D-M1–D-M3 aprovados no recorte offline; D-M4/D-M5 e gate global pendentes. Não houve preflight público, entrega real ou sete dias observados; T0/Tend reais não definidos. Preservar672 slots/≥666 válidos, autorização/configuração específica e revisão antes de qualquer aceite. Drills/recibos falsos não preenchem critérios operacionais;07 continua não elegível para implementação. Seções anteriores conservam seus estados históricos.
