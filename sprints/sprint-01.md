# Sprint 01 — Base local segura

Data da especificação: 24/10/2026.

**Estado em 24/10/2026: implementação local entregue; AC01–AC16 aprovados; pendência de organização Git resolvida por repositório independente em `cripto-bot/`.** Consulte o [guia e registro de validação](../testes/sprint-01-validacao.md) e as [evidências dos comandos](../testes/sprint-01-evidencias.json). Este documento detalha a seção 12 de [planejamento.md](../planejamento.md).

## 1. Objetivo e incremento demonstrável

Criar a base local do robô Binance Spot: um pacote Python instalável, configuração validada, tipos de domínio mínimos, precisão decimal, logs JSON e uma CLI que executa exclusivamente um ciclo vazio `PAPER`, sem acesso à rede.

Ao final, o operador deverá conseguir instalar o pacote e executar:

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
uv run --locked cripto-bot check-config --config config/paper.example.toml
uv run --locked cripto-bot run-once --config config/paper.example.toml
```

O segundo comando deverá informar `status=NOOP`, `mode=PAPER` e `orders_sent=0`. Esse resultado comprova inicialização e composição seguras; ainda não representa coleta, simulação financeira ou negociação.

## 2. Referências e pré-requisitos

Ler as seções 3, 4, 5, 7, 8, 9, 10 e 12 do planejamento, as instruções locais aplicáveis e todos os arquivos existentes que serão afetados. Consultar README, arquitetura, ADRs, módulos e testes se já existirem. Sua ausência inicial é esperada e não exige criar implementações de etapas futuras.

| Dependência | Situação observada nesta especificação | Condição para implementar |
|---|---|---|
| D01 — Planejamento | `docs/planejamento.md` disponível | Preservar escopo e decisões estabelecidas |
| D02 — Sprint anterior | Inexistente; esta é a primeira Sprint de código | Nenhuma dependência de código anterior |
| D03 — Código e evidências anteriores | Nenhum pacote, manifest ou guia de Sprint encontrado na raiz consultada | Inspecionar novamente antes de editar |
| D04 — Python/uv e dependências | Disponibilidade e compatibilidade não testadas nesta entrega | Verificar Python 3.13, uv, resolução e permissões de instalação |
| D05 — Localização do Git | `git rev-parse --show-toplevel` retornou `/home/cams7/Dev/Cripto/docs` | Distinguir raiz do projeto e raiz Git ao preparar a implementação |

A raiz funcional permanece `/home/cams7/Dev/Cripto`. Atualmente o Git cobre `docs`, enquanto os futuros arquivos de aplicação ficam no diretório pai. Não mover `.git`, inicializar outro repositório ou alterar essa organização automaticamente. Registrar a situação no guia de validação; se ela impedir a entrega versionada exigida pelo fluxo de trabalho, resolver essa decisão antes de declarar a Sprint concluída. Esta especificação não muda o layout do planejamento.

Não consultar credenciais. Os projetos LotoBot são referências somente de leitura, sem dependência em runtime. Não é necessário repetir sua auditoria para criar esta base.

## 3. Escopo e exclusões

Incluído:

- Python 3.13, com patch fixado na implementação; uv com versão usada registrada e lock versionado.
- Um pacote `cripto_bot` com setuptools e código em `modules/trading/src`.
- CLI `cripto-bot check-config` e `cripto-bot run-once`.
- Configuração TOML, defaults seguros e override de modo por ambiente.
- Modelo de modo, conversão decimal explícita e resultado tipado do ciclo vazio.
- Logs JSON, timestamps UTC e identificador de execução.
- Testes unitários, integração da CLI, bloqueio de rede e validação do wheel instalado.
- README, arquitetura inicial, dois ADRs e guia de validação em português.

Excluído: HTTP, SDK Binance, boto3, banco, dados de mercado, carteira, saldo, ledger, estratégia, risco financeiro executável, backtest, executor financeiro, TESTNET/LIVE, agendamento, notificações externas, containers, SAM, Terraform, API web e provisionamento. Não criar diretórios, interfaces ou adapters vazios para essas funcionalidades.

## 4. Contratos funcionais

### 4.1 Configuração

Usar `tomllib` para leitura e Pydantic na fronteira de validação, com rejeição de campos extras e sem dependência adicional de settings nesta etapa. O domínio não depende dessas ferramentas.

Exemplo mínimo de `config/paper.example.toml`:

```toml
mode = "PAPER"
```

Não incluir parâmetros de carteira, taxas, endpoints ou símbolos sem uso real nesta Sprint. A regra de rejeitar símbolos de derivativos é atendida nesta etapa pela rejeição de qualquer campo `symbol`; a validação de símbolos Spot será detalhada quando esse campo for introduzido.

Regras:

1. Sem `--config`, usar os defaults internos. Não procurar arquivos automaticamente em diretórios pessoais nem carregar `.env` implicitamente.
2. Com `--config`, ler exatamente o caminho fornecido. Arquivo ausente, ilegível ou TOML inválido resulta em erro; nunca voltar silenciosamente ao default.
3. O único campo permitido no TOML é `mode`. Se omitido, assumir `PAPER`.
4. O único override de configuração por ambiente é `CRIPTO_BOT_MODE`. Variável ausente mantém o valor do arquivo/default; variável presente e vazia é inválida.
5. Precedência: default → arquivo → ambiente. Validar também o arquivo antes de aplicar overrides: um arquivo inválido não pode ser ocultado por `CRIPTO_BOT_MODE=PAPER`.
6. Aceitar somente a string exata `PAPER`. Rejeitar `LIVE`, `TESTNET`, valores desconhecidos, tipos incorretos, espaços adicionais e caixa diferente, sem normalização silenciosa.
7. Rejeitar variáveis desconhecidas no namespace `CRIPTO_BOT_`. Não interpretar outras variáveis do sistema como configuração da aplicação.
8. Campos de credencial no TOML e variáveis como `CRIPTO_BOT_API_KEY` falham como configuração não suportada. Rejeitar também a presença de `BINANCE_API_KEY` e `BINANCE_API_SECRET`, mesmo vazias, sem usar ou registrar seus conteúdos. Não examinar perfis AWS ou arquivos de secrets.
9. Validar completamente antes de chamar o caso de uso. Nenhum cliente externo deve existir ou ser construído. A leitura do arquivo e a emissão local de diagnóstico são os únicos I/Os necessários à validação.
10. Mensagens de erro podem identificar o campo permitido ou o tipo de falha, mas nunca reproduzir valores, conteúdo TOML, ambiente completo ou exceções de validação com entrada original. Para chaves desconhecidas, preferir diagnóstico genérico para evitar expor conteúdo no próprio nome da chave.

### 4.2 CLI e ciclo vazio

Usar `argparse` da biblioteca padrão; não introduzir framework de CLI.

| Comando | Sucesso | Falha esperada |
|---|---|---|
| `check-config [--config CAMINHO]` | Exit code 0; JSON com `status=VALID` e `mode=PAPER` | Exit code 2 para uso/configuração inválidos |
| `run-once [--config CAMINHO]` | Exit code 0; JSON com `status=NOOP`, `mode=PAPER`, `orders_sent=0` | Exit code 2 antes do caso de uso para configuração inválida |
| `--help` | Exit code 0; ajuda textual | Sem execução de ciclo |

Reservar exit code 1 para falha interna inesperada, com diagnóstico sanitizado. Não converter toda falha em sucesso ou NOOP. Argumentos desconhecidos falham; não implementar `--mode`, `--endpoint` ou opções de credenciais.

Em sucesso, stdout contém um único objeto JSON de resultado, com `run_id` e timestamp UTC além dos campos acima. Logs operacionais vão para stderr como JSON Lines. Ajuda textual do parser é exceção ao formato JSON. Erros esperados da aplicação têm diagnóstico JSON em stderr; erros de sintaxe de argumentos podem seguir o formato textual do `argparse`, sem eco de valores sensíveis.

O caso de uso recebe configuração já validada e dependências mínimas injetáveis, retorna resultado tipado e não cria saldo, ordem, reserva ou arquivo de estado. O resultado deve permanecer NOOP em chamadas repetidas. IDs e timestamps podem mudar entre chamadas.

### 4.3 Decimais

Criar uma função pequena de conversão de string para `Decimal` no domínio; não criar modelo completo de dinheiro ou regras de arredondamento da corretora.

- Aceitar strings decimais finitas, como `"0.1"`, `"0.2"`, `"0"` e `"10000.00"`.
- Rejeitar `float`, inteiros, booleanos, `None`, strings vazias ou malformadas, NaN e infinitos. Validar o tipo antes de converter; não usar `str(valor)` para aceitar entradas de outros tipos.
- O conversor genérico pode aceitar números negativos finitos; positividade de preço/quantidade pertence a modelos futuros. Não introduzir essa restrição sem um domínio que a justifique.
- Demonstrar que a soma de `Decimal("0.1")` e `Decimal("0.2")` é igual a `Decimal("0.3")`, sem passagem por float.
- Não alterar globalmente o contexto decimal na importação. Registrar no ADR os limites dessa base: ainda não há quantização, persistência monetária ou política de cálculo financeiro.

O conversor será testado diretamente. Não adicionar um valor financeiro fictício à configuração apenas para exercitá-lo pela CLI.

### 4.4 Logs e separação de camadas

Cada evento operacional contém `timestamp`, `level`, `event`, `run_id` e `mode` quando já validado. UTC deve ter offset explícito (`Z` ou `+00:00`). Um único ciclo compartilha o mesmo `run_id` entre eventos e resultado.

Para falha antes da validação, não registrar um modo não validado como se estivesse autorizado. Usar evento de rejeição e código de erro sanitizado. Não serializar configuração inteira, argumentos, ambiente, caminhos sensíveis ou traceback com entrada original.

O domínio contém somente modelos e regras puras; a aplicação coordena o ciclo; o adapter carrega configuração; o entrypoint compõe e apresenta resultados. Relógio e geração de ID podem ser funções injetadas, sem framework de injeção. Não criar abstrações sem uso.

## 5. Entregáveis e caminhos

Caminhos `docs/...` são relativos ao workspace `/home/cams7/Dev/Cripto`; os demais caminhos abaixo são relativos ao repositório `/home/cams7/Dev/Cripto/cripto-bot`.

| Caminho | Conteúdo esperado |
|---|---|
| `pyproject.toml` | Metadados, setuptools, descoberta em `modules/trading/src`, console script, dependências e configurações de qualidade |
| `uv.lock`, `.python-version` | Resolução de dependências e patch Python 3.13 fixado |
| `.gitignore` | Ambientes, caches, build e artefatos locais; preservar lock e exemplos públicos |
| `README.md` | Instalação, comandos, modo permitido, restrições e links para documentos |
| `config/paper.example.toml` | Exemplo mínimo sem segredos |
| `modules/trading/src/cripto_bot/__init__.py` | Pacote importável, sem efeitos externos ao importar |
| `modules/trading/src/cripto_bot/domain/models.py` | Modo permitido, conversor decimal e modelos mínimos |
| `modules/trading/src/cripto_bot/application/run_once.py` | Caso de uso vazio e resultado tipado |
| `modules/trading/src/cripto_bot/adapters/config.py` | TOML, ambiente, precedência e rejeições |
| `modules/trading/src/cripto_bot/observability/logging.py` | Eventos JSON e diagnóstico sanitizado |
| `modules/trading/src/cripto_bot/entrypoints/cli.py` | Parser, composição e exit codes |
| `tests/unit/test_config.py`, `test_decimal.py`, `test_run_once.py`, `test_logging.py` | Contratos unitários e falhas relevantes |
| `tests/integration/test_cli.py` | CLI instalada, stdout/stderr, exit codes e bloqueios |
| `tests/conftest.py` e fixtures necessárias | Ambiente sintético isolado e bloqueio de sockets |
| `docs/arquitetura.md` | Componentes implementados, fluxo local e distinção do roadmap |
| `docs/decisoes/0001-monolito-modular.md` | Pacote único, camadas, layout e alternativas |
| `docs/decisoes/0002-modos-e-decimais.md` | PAPER, precedência, falhas seguras e precisão |
| `docs/sprints/sprint-01.md` | Esta especificação, com estado real atualizado |
| `docs/testes/sprint-01-validacao.md` | Guia reproduzível, evidências, limitações e decisão de aceite |
| `docs/planejamento.md` | Estado real e referência à especificação/validação |

Adicionar `__init__.py` nos subpacotes necessários. Não criar a estrutura completa futura da seção 5 do planejamento. Usar Pydantic em produção; pytest/pytest-cov, Ruff e mypy no grupo `dev`. Fixar a versão de uv usada no guia e no procedimento de instalação; registrar versões resolvidas pelo lock. Não acrescentar HTTPX ou SDKs nesta etapa.

## 6. Sequência de implementação

1. Inspecionar instruções, arquivos e estado Git. Registrar a localização do repositório e preservar alterações anteriores.
2. Conferir ferramentas, compatibilidade com Python 3.13 e permissões de escrita. Instalar somente em locais permitidos; configurar ambientes/cache locais se necessário.
3. Criar manifest, pacote, entrypoint e configurações de Ruff, mypy strict e pytest. Gerar o lock antes de executar comandos com `--locked`.
4. Implementar os modelos puros e conversão decimal com os testes de fronteira.
5. Implementar configuração e precedência; provar rejeição antes do caso de uso.
6. Implementar ciclo vazio, resultado, logs e CLI conforme os contratos da seção 4.
7. Executar testes unitários e integração com rede bloqueada, inclusive nos processos filhos usados nos testes da CLI.
8. Gerar wheel, instalar em ambiente separado dentro da raiz e validar a partir de diretório sem acesso ao código-fonte por caminho de importação.
9. Atualizar README, arquitetura, ADRs, guia e estado do planejamento com evidências reais. Não iniciar a Sprint 02.

Estimativa orientativa: 2–5 dias úteis de implementação e validação, conforme a seção 9 do plano. Instalação bloqueada ou ajustes de ambiente devem ser registrados, sem reduzir critérios de aceite.

## 7. Matriz de validação e critérios de aceite

Os cenários abaixo definem o contrato de aceite. Foram executados nesta implementação; os resultados, limitações e correspondência com os testes estão no [guia de validação](../testes/sprint-01-validacao.md#4-matriz-de-evidências).

| ID | Cenário | Resultado exigido |
|---|---|---|
| AC01 | Sem arquivo e sem override; TOML sem modo | Default PAPER explícito no resultado |
| AC02 | Arquivo de exemplo e `check-config` | Exit 0, VALID/PAPER, sem chamar o ciclo |
| AC03 | `run-once`, inclusive chamadas repetidas | Exit 0, NOOP/PAPER/0 ordens, sem estado financeiro |
| AC04 | LIVE, TESTNET, modo desconhecido, tipo incorreto, vazio ou grafia divergente | Exit 2; caso de uso não chamado |
| AC05 | Arquivo inválido e ambiente PAPER; arquivo PAPER e ambiente LIVE | Ambas as combinações rejeitadas; override não oculta erro |
| AC06 | Arquivo ausente, ilegível ou TOML malformado | Exit 2; sem fallback e sem eco do conteúdo |
| AC07 | Campo extra, símbolo, endpoint ou chave de credencial | Rejeição, sem exposição de nome/valor arbitrário |
| AC08 | Variável desconhecida `CRIPTO_BOT_*` ou credencial Binance indicada na seção 4.1 | Rejeição mesmo com valor vazio; não usar conteúdo |
| AC09 | Ambiente não relacionado à aplicação | Não interpretado como configuração; testes independentes da máquina |
| AC10 | Strings decimais válidas e soma 0.1 + 0.2 | Resultado Decimal exato e entradas preservadas sem float |
| AC11 | Float, int, bool, None, NaN, infinito, vazio ou texto inválido | Rejeição explícita no conversor |
| AC12 | Eventos e resultado com relógio/ID fixos nos testes | JSON parseável, UTC explícito e correlação consistente |
| AC13 | Segredo sintético em TOML, ambiente e erro de argumento | Ausente de stdout/stderr, logs e erros |
| AC14 | Tentativa controlada de socket e execução normal | Guard bloqueia a tentativa; CLI funciona sob o mesmo bloqueio |
| AC15 | Ruff, formatação, mypy strict, pytest e build | Todos passam; ramificações de segurança cobertas |
| AC16 | Wheel em ambiente separado e diretório neutro | Importa o pacote instalado e executa ambos os comandos sem PYTHONPATH |

Para AC14, não basta bloquear sockets somente no processo pytest se a CLI roda em subprocesso. O harness deve aplicar a restrição também no filho, com um teste de tentativa deliberada que comprove sua eficácia. Não incluir esse harness no wheel de produção. Instalação/resolução pode precisar de rede; a proibição de rede refere-se à aplicação e aos testes de execução, não ao download previamente autorizado de dependências.

Para AC15, apresentar relatório de cobertura de branches e justificar lacunas não críticas. Não impor 100% global como substituto dos cenários: todas as ramificações de rejeição de modo, credenciais, precedência e decimal inválido precisam ser exercitadas. Não excluir caminhos críticos do relatório para obter aprovação.

### 7.1 Comandos previstos

Executar após criar o manifest, gerar o lock e preparar as ferramentas. São comandos de implementação futura, não evidências desta especificação.

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
python3.13 --version
uv --version
uv sync --locked --group dev
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy modules/trading/src
uv run --locked pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
uv build
uv run --locked cripto-bot check-config --config config/paper.example.toml
uv run --locked cripto-bot run-once --config config/paper.example.toml
```

O executor deve acrescentar ao guia os comandos exatos usados para criar o lock, fixar versões, instalar o wheel e executar a matriz negativa. Se houver incompatibilidade com a versão fixada, documentar o ajuste e sua justificativa.

### 7.2 Verificação do wheel

1. Criar ambiente dedicado, por exemplo `.venv-wheel`, dentro da raiz e ignorado pelo Git.
2. Instalar exatamente o wheel recém-gerado e suas dependências, registrando nome, SHA-256 e comando utilizado. Não instalar o projeto em modo editable nesse ambiente.
3. Executar o console script desse ambiente a partir de diretório neutro dentro da raiz, com caminho absoluto para o exemplo TOML e sem `PYTHONPATH` apontando para o checkout.
4. Verificar a origem de `cripto_bot.__file__` em `site-packages`, ambos os comandos positivos e ao menos a rejeição de LIVE.
5. Registrar exit codes, JSON e bloqueio de rede. O smoke test comprova distribuição e entrypoint, além dos testes sobre o código-fonte.

## 8. Evidências, falhas e recuperação

O guia `docs/testes/sprint-01-validacao.md` deverá conter versões de Python/uv e dependências relevantes, diretório de execução, preparação, comandos, exit codes, resultados esperados/obtidos, resumo de testes e cobertura, hash do wheel, sua origem de importação, saída NOOP, matriz AC01–AC16 e limitações.

| Falha | Diagnóstico e recuperação esperados |
|---|---|
| Python/uv indisponível ou escrita negada | Registrar ferramenta/permissão faltante; não declarar aceite nem instalar fora dos limites permitidos |
| Resolução ou lock incompatível | Revisar versões com documentação oficial; regenerar deliberadamente e repetir checks afetados |
| Configuração inválida | Encerrar com código 2, corrigir arquivo/override e repetir; não migrar para outro modo |
| Wheel não importa fora do checkout | Corrigir descoberta de pacotes/entrypoint; reconstruir e reinstalar o artefato correto |
| Segredo sintético aparece em erro | Sanitizar a fronteira e adicionar regressão antes de repetir a matriz |
| Teste acessa rede | Corrigir a dependência/efeito e demonstrar o guard no processo afetado |
| Layout Git não cobre arquivos previstos | Registrar o alcance real do versionamento; não mover metadados automaticamente |

Não há banco ou estado remoto a recuperar. Ambientes, caches e `dist` são regeneráveis. Na limpeza, remover somente artefatos identificados como produzidos nesta execução, preservando código, documentos, fixtures e trabalho anterior. Não usar limpeza ampla do Git nem apagar ambientes preexistentes sem inspecionar sua origem.

Custo AWS: **zero**, pois nenhum recurso ou API AWS será utilizado. Há apenas uso local de disco, CPU e eventuais downloads de dependências. Não consultar conta AWS, provisionar ou acessar credenciais para comprovar esse custo.

## 9. Conclusão da Sprint e próximo gate

Marcar a implementação como concluída somente após AC01–AC16 atendidos, pacote e wheel operacionais, documentação coerente e guia com evidência verificável. Quando houver comando não executado ou critério obrigatório sem prova, registrar **PENDENTE**, com causa e ação necessária.

A revisão da entrega deve distinguir implementação concluída de validação aprovada. Atualizar o planejamento com o resultado real e o link para o guia. A Sprint 02 só se torna elegível depois da aprovação das evidências da Sprint 01; sua implementação não integra esta tarefa.

## 10. Prompt autossuficiente de execução

```text
Implemente somente a Sprint 01 — Base local segura do robô Binance Spot.

Workspace obrigatório: /home/cams7/Dev/Cripto.
Diretório de comandos e repositório da aplicação: /home/cams7/Dev/Cripto/cripto-bot.
Caminhos docs/... são relativos ao workspace; demais entregáveis são relativos
a cripto-bot. Cada novo módulo independente deve nascer diretamente na raiz
do workspace, com repositório próprio, conforme a seção 5 do planejamento.
Todos os arquivos produzidos devem permanecer nela, respeitando as
permissões do ambiente. Leia as instruções locais, docs/planejamento.md
(seções 3, 4, 5, 7, 8, 9, 10 e 12) e docs/sprints/sprint-01.md na íntegra.
Leia README.md, docs/arquitetura.md, docs/decisoes/, configuração, código e
testes se existirem. Inspecione alterações atuais e preserve trabalho anterior.

Dependências:
1. Planejamento disponível; não existe Sprint anterior de código.
2. Ferramentas Python 3.13/uv compatíveis e escrita permitida na raiz.
3. Contratos e critérios AC01–AC16 desta especificação preservados.
Verifique novamente esses itens. A documentação está no Git de Cripto/docs e a aplicação no Git independente
de Cripto/cripto-bot. Preserve ambos os históricos e não mova seus metadados. Se um requisito
indispensável falhar, registre o impedimento em
docs/testes/sprint-01-validacao.md e interrompa só o trabalho dependente.

Modo permitido: exclusivamente PAPER offline, Spot. Não implemente HTTP,
SDK Binance, boto3, persistência, carteira, estratégia, risco financeiro,
backtest, executores TESTNET/LIVE, notificações, agendamento ou infraestrutura.
Não consulte credenciais de produção nem altere os projetos LotoBot.

Entregue README.md, pyproject.toml, uv.lock, .python-version, .gitignore,
config/paper.example.toml e pacote cripto_bot em modules/trading/src.
Use Python 3.13 com patch fixado, uv com versão registrada, setuptools,
Pydantic na fronteira, argparse/tomllib da biblioteca padrão e ferramentas
pytest/pytest-cov, Ruff e mypy strict em dev. Verifique documentação oficial
e compatibilidade antes de fixar as versões e gerar o lock.

Implemente domain/models.py, application/run_once.py, adapters/config.py,
observability/logging.py, entrypoints/cli.py e arquivos de pacote necessários.
Não crie módulos vazios de funcionalidades futuras.

Siga os contratos da seção 4: somente mode no TOML, PAPER como default,
CRIPTO_BOT_MODE como único override, validação do arquivo antes do merge,
rejeição de variáveis desconhecidas CRIPTO_BOT_* e de BINANCE_API_KEY/
BINANCE_API_SECRET presentes. Não carregue .env implicitamente. Rejeite
configurações não suportadas antes do caso de uso, sem ecoar valores.

Exponha cripto-bot check-config e run-once, ambos com --config opcional.
check-config retorna JSON VALID/PAPER; run-once retorna NOOP/PAPER e
orders_sent=0. Exit codes: 0 sucesso, 2 uso/configuração inválida, 1 falha
interna. Um resultado JSON em stdout, logs JSON Lines em stderr, UTC e
run_id correlacionado. Não invente saldo ou atividade financeira.

Implemente conversor Decimal a partir exclusivamente de strings finitas,
rejeitando float/int/bool/None/NaN/infinito e texto inválido. Teste a igualdade
Decimal('0.1') + Decimal('0.2') == Decimal('0.3'), sem float intermediário.
Não crie campo financeiro na configuração apenas para testar o conversor.

Crie testes unitários e integração cobrindo AC01–AC16. Bloqueie sockets nos
testes e nos subprocessos da CLI, com teste deliberado do próprio bloqueio.
Use somente segredos sintéticos e prove que não aparecem nas saídas.
Execute, desde a raiz, uv sync --locked --group dev; uv run --locked ruff
check .; uv run --locked ruff format --check .; uv run --locked mypy
modules/trading/src; uv run --locked pytest -q --cov=cripto_bot --cov-branch
--cov-report=term-missing; uv build; e os dois comandos CLI com o exemplo.
Gere o lock antes de usar --locked. Registre adaptações justificadas.

Instale o wheel gerado em ambiente separado dentro da raiz; execute de
diretório neutro sem PYTHONPATH do checkout, verifique importação de
site-packages, os comandos positivos e a rejeição de LIVE. Registre nome e
SHA-256 do wheel. Não confunda teste editable com teste da distribuição.

Documente em português docs/arquitetura.md,
docs/decisoes/0001-monolito-modular.md,
docs/decisoes/0002-modos-e-decimais.md e
docs/testes/sprint-01-validacao.md. O guia deve conter preparação, versões,
comandos, resultados esperados/obtidos, exit codes, matriz AC01–AC16,
cobertura, prova do wheel, diagnóstico, recuperação, limpeza e AWS zero.
Atualize docs/sprints/sprint-01.md e docs/planejamento.md com o estado real.

Não apresente verificação não executada como aprovada. Conclua somente com
todos os critérios obrigatórios atendidos e evidências reproduzíveis; caso
contrário registre PENDENTE, causa e correção. Informe alterações, resultados
e limitações sem iniciar a Sprint 02, enviar mensagens/ordens ou provisionar.
```

## 11. Fontes e verificação desta especificação

Referência de escopo: [planejamento, seção 12](../planejamento.md#12-sprint-01-detalhada--base-local-segura).

Documentação oficial consultada em 24/10/2026 para confirmar os fundamentos dos contratos:

- [uv — lock e sincronização](https://docs.astral.sh/uv/concepts/projects/sync/): uso de lock e sincronização controlada de dependências.
- [setuptools — descoberta de pacotes](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html): configuração da origem de pacotes para o layout proposto.
- [Python 3.13 — Decimal](https://docs.python.org/3.13/library/decimal.html): construção a partir de strings, precisão e rejeição explícita de valores não finitos na aplicação.
- [Pydantic — modelos](https://docs.pydantic.dev/latest/concepts/models/): validação na fronteira e configuração de tratamento de campos extras.

Essas consultas não constituem teste de compatibilidade das versões que serão instaladas. O executor deverá reconfirmar as versões exatas e registrar suas fontes. Nenhuma API Binance ou serviço AWS novo é definido nesta Sprint.

Na entrega original da especificação foram inspecionados o planejamento, os arquivos visíveis da raiz e a localização Git. Foram criados apenas esta especificação e o registro correspondente no planejamento, sem implementação ou testes naquela etapa.

## 12. Registro da execução em 24/10/2026

O prompt da seção 10 foi executado mediante solicitação do responsável. Foram criados pacote, CLI, configuração, lock, testes, README, arquitetura, ADRs e guia. Python 3.13.15 e uv 0.12.19 foram usados. Ruff, formatação, mypy strict e 79 testes passaram, com 100% de cobertura de linhas e ramificações da aplicação. Wheel instalado em ambiente separado foi validado sob bloqueio de sockets, incluindo rejeição de LIVE.

Os critérios técnicos AC01–AC16 estão aprovados. A conclusão global permanece PENDENTE porque o Git em `docs` não cobre os arquivos de aplicação e o lock no diretório pai. Foi solicitada decisão sobre essa organização; nenhum metadado Git foi movido ou repositório criado. Não houve implantação, acesso a credenciais, integração financeira ou início da Sprint 02.

## 13. Reorganização autorizada em 24/10/2026

O responsável determinou que cada módulo independente tenha diretório e Git próprios diretamente em `/home/cams7/Dev/Cripto`. A aplicação foi movida para `cripto-bot/`, preservando fontes, testes, configuração e lock. A pasta `docs` manteve seu Git. As observações de pendência nas seções anteriores descrevem o estado inicial e foram resolvidas por essa decisão; não houve commit, remoto ou início da Sprint 02. Os comandos ativos acima usam a nova raiz da aplicação.

## Adendo documental de 25/10/2026 — validações antes de LIVE

O aceite registrado neste documento permanece restrito ao escopo histórico executado. Ele não comprova backtest fora da amostra, PAPER contínuo, Demo Spot, Spot Testnet ou `POST /api/v3/order/test`. A sequência e os gates atualizados estão no [planejamento, seção 10](../planejamento.md#10-gates-entre-ambientes-e-modos) e no [roteiro de validação](../testes/validacao-pre-live.md). Demo passa à Sprint 09, Testnet complementar à 10 e preparação LIVE à 11, sem ativação. A implementação desta Sprint continua exclusivamente PAPER; DEMO/TESTNET/LIVE não são liberados por esta revisão.

Nenhum teste foi repetido e nenhuma evidência JSON foi alterada por este adendo. A solicitação atual autoriza somente revisão documental. LIVE permanece bloqueado por padrão e exige validações concluídas, limites de risco reais e aprovação explícita vigente do responsável.
