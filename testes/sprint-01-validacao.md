# Sprint 01 — Guia e registro de validação

Data: 24/10/2026. Raiz do workspace: `/home/cams7/Dev/Cripto`.

**Diretório atual de execução dos comandos: `/home/cams7/Dev/Cripto/cripto-bot`.**

**Resultado técnico local: APROVADO para AC01–AC16. Pendência de organização Git RESOLVIDA por solicitação do responsável.** A aplicação está em `/home/cams7/Dev/Cripto/cripto-bot`, com Git independente; `docs` preservou seu repositório. Consulte a seção 9 para a revalidação no novo caminho. Os comandos deste guia usam o diretório atual da aplicação. Os caminhos e o hash do wheel apresentados nas instruções correspondem à aplicação após a reorganização. As evidências originais anteriores à mudança foram preservadas no JSON; a seção 9 registra a revalidação no novo caminho. A Sprint 02 não foi iniciada.

## 1. Preparação e versões verificadas

| Item | Versão usada |
|---|---|
| Python | CPython 3.13.15, já instalado e descoberto pelo uv |
| uv | 0.12.19, exigido também no manifest |
| setuptools (build) | 84.2.0, fixado no build-system |
| Pydantic / pydantic-core | 2.14.1 / 2.50.1 |
| pytest / pytest-cov | 9.1.1 / 7.1.0 |
| coverage | 7.17.0 |
| Ruff | 0.17.2 |
| mypy | 1.20.2 |

As demais versões e hashes de distribuição estão em `uv.lock`. A instalação e os checks comprovaram compatibilidade local com Linux/Python 3.13.15; não foram avaliados runtimes AWS.

O comando direto `python3.13 --version` inicialmente falhou por ausência no PATH. `uv python list --only-installed` identificou 3.13.15 existente; `uv run --locked python --version` confirmou o interpretador efetivamente usado. Não foi necessário instalar outro Python ou alterar o PATH global.

É necessário acesso de escrita ao módulo `/home/cams7/Dev/Cripto/cripto-bot`, uv 0.12.19 e acesso ao índice para dependências ainda não disponíveis. Os ambientes `.venv` e `.venv-wheel` ficam dentro desse módulo. Os exemplos usam cache local em `$PWD/.uv-cache`; a revalidação da seção 9 reutilizou o cache compartilhado `/home/cams7/Dev/Cripto/.uv-cache`. Instalação de dependências pode usar rede; execução dos testes/CLI não precisa dela.

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv --version
uv python list --only-installed
uv sync --locked --group dev
uv run --locked python --version
uv run --locked python -c 'import sys; print(sys.executable)'
```

O resultado esperado é `Python 3.13.15`, com o executável em `/home/cams7/Dev/Cripto/cripto-bot/.venv/bin/python`. Para repetir a validação com o lock existente, usar `uv sync --locked --group dev`; `uv lock` foi utilizado no bootstrap original e não precisa ser repetido nessa preparação.

### Aviso do pyenv durante a descoberta de Python

Na execução manual informada em 24/10/2026, `uv --version` retornou `0.12.19` e `uv python list --only-installed` apresentou o aviso:

```text
warning: Failed to inspect Python interpreter from search path at `/home/cams7/.pyenv/shims/python`
pyenv: version `3.13.15' is not installed (set by /home/cams7/Dev/Cripto/cripto-bot/.python-version)
```

A mesma listagem identificou `cpython-3.13.15-linux-x86_64-gnu` em `/home/cams7/.local/share/uv/python/cpython-3.13-linux-x86_64-gnu/bin/python3.13`. O aviso se refere ao interpretador acessado pelo shim do pyenv: ele lê o pin `3.13.15`, mas essa versão não está instalada no pyenv. A instalação gerenciada pelo uv existe separadamente e foi encontrada. Ambos podem consultar `.python-version`; instalar uma versão pelo uv não a instala no pyenv.

Esse aviso, acompanhado da descoberta de 3.13.15 pelo uv, permite continuar a preparação acima. Confirmar a versão e o caminho efetivamente usados com os dois comandos `uv run --locked python` apresentados no bloco. O projeto exige `>=3.13,<3.14`; as versões 3.14.7 e 3.12.14 também listadas não atendem ao manifest. Não é necessário reinstalar Python, alterar o pin ou mudar o PATH global apenas por esse aviso. `UV_CACHE_DIR` controla o cache do uv e não altera a seleção feita pelo pyenv.

Se a sincronização ou a confirmação do interpretador falhar, registrar essa falha e investigar antes de prosseguir com os checks. O log manual apresentado contém somente a versão do uv e a descoberta de interpretadores: não comprova nova instalação de dependências nem nova aprovação dos testes. Os resultados das seções seguintes permanecem como evidências das execuções anteriores registradas.

`.python-version` contém `3.13.15`. O lock foi gerado a partir do manifest e validado novamente com `--locked`; não manter um requirements manual paralelo. O manifest exige a versão de uv; instalar essa versão pelo método oficial disponível antes de repetir o bootstrap.

## 2. Comandos e resultados

Os comandos abaixo permitem repetir a validação no diretório atual. A suíte, os checks e o build passaram após a mudança, conforme a seção 9. As saídas da execução original e o resumo da reorganização estão em [sprint-01-evidencias.json](sprint-01-evidencias.json).

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked --group dev
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy modules/trading/src
uv run --locked pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
uv build
uv run --locked cripto-bot check-config --config config/paper.example.toml
uv run --locked cripto-bot run-once --config config/paper.example.toml
```

Resultado após a reorganização: Ruff sem achados, 21 arquivos Python com formatação verificada, mypy sem problemas em 11 fontes e **79 testes aprovados**. Cobertura da aplicação: **113 statements e 18 branches, 100%, sem lacunas ou exclusões de caminhos críticos**. A medição cobre a aplicação, não o harness nem todas as dependências transitivas.

O build produziu `dist/cripto_bot-0.1.0.tar.gz` e `dist/cripto_bot-0.1.0-py3-none-any.whl`. O uv emitiu aviso genérico sobre cache dentro da origem; a inspeção do arquivo sdist confirmou ausência de `.uv-cache`/`.venv`. O wheel foi inspecionado e não inclui `tests` ou o harness de bloqueio.

Configuração pública usada:

```toml
mode = "PAPER"
```

Saídas funcionais obtidas, omitindo apenas ID e timestamp variáveis:

```json
{"mode":"PAPER","status":"VALID"}
{"mode":"PAPER","status":"NOOP","orders_sent":0}
```

Cada objeto real inclui `run_id` e `timestamp` UTC. stdout contém somente o resultado; stderr contém o evento JSON com a mesma correlação.

## 3. Wheel em ambiente separado

Procedimento para reproduzir a instalação e conferir as dependências pelo lock. A instalação e o smoke test após a reorganização foram executados conforme a seção 9:

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv venv --python 3.13.15 .venv-wheel
uv pip install --python .venv-wheel/bin/python dist/cripto_bot-0.1.0-py3-none-any.whl
mkdir -p .wheel-smoke
uv export --locked --no-dev --no-emit-project --format requirements-txt --output-file .wheel-smoke/requirements.txt
uv pip install --python .venv-wheel/bin/python --requirement .wheel-smoke/requirements.txt dist/cripto_bot-0.1.0-py3-none-any.whl
uv run --locked python tests/wheel_smoke.py
```

O arquivo exportado é temporário e derivado do lock. O procedimento cria `.wheel-smoke` antes do export para funcionar também em ambiente limpo.

- Wheel: `cripto_bot-0.1.0-py3-none-any.whl`.
- SHA-256 após a reorganização: `6648586f24285bbea538f335b6d5be7fc9b45b116fc4b908bec4d34d2962f03c`.
- Origem da importação: `/home/cams7/Dev/Cripto/cripto-bot/.venv-wheel/lib/python3.13/site-packages/cripto_bot/__init__.py`.
- Diretório de execução: `.wheel-smoke`; Python isolado com `-I` e `PYTHONPATH` removido do ambiente dos comandos.
- `check-config` e `run-once`: exit 0 com os resultados previstos, sob o harness que bloqueia sockets.
- `CRIPTO_BOT_MODE=LIVE`: exit 2, stdout vazio e evento `configuration_rejected`.
- Probe de socket no mesmo interpretador/harness: falhou com `NETWORK_BLOCKED`, como exigido.

Reconstruções podem mudar o hash do wheel; comparar o artefato exato usado no teste, não presumir identidade binária de builds futuros. O smoke test imprime o hash corrente.

## 4. Matriz de evidências

| Critério | Evidência executada | Resultado |
|---|---|---|
| AC01 | `test_config.py`: defaults sem arquivo, TOML vazio e PAPER | Aprovado |
| AC02 | CLI unitária, subprocesso instalado e wheel; sentinela impede chamar ciclo no check | Aprovado |
| AC03 | Ciclo repetido, CLI e wheel com NOOP/PAPER/0 | Aprovado |
| AC04 | Modos, grafias e tipos proibidos; sentinela no caso de uso | Aprovado |
| AC05 | Arquivo inválido com override PAPER e arquivo PAPER com override inválido | Aprovado |
| AC06 | Arquivo ausente, TOML inválido, encoding inválido e PermissionError injetado | Aprovado |
| AC07 | Campo extra, símbolo, endpoint e credenciais/chave sintética | Aprovado |
| AC08 | Quatro nomes proibidos/desconhecidos, valores sintéticos e vazios | Aprovado |
| AC09 | Ambiente externo ignorado e ambiente explícito nos testes | Aprovado |
| AC10 | Strings finitas, negativos e igualdade decimal exata | Aprovado |
| AC11 | Float/int/bool/None/texto/NaN/sNaN/infinito rejeitados | Aprovado |
| AC12 | Relógio/ID fixos, correlação e normalização UTC; naive rejeitado | Aprovado |
| AC13 | Segredo sintético em arquivo, nome de campo, ambiente, argumento e exceção | Aprovado |
| AC14 | Guard em pytest e audit hook nos processos filhos; probes deliberados | Aprovado |
| AC15 | Lint, formatação, mypy, 79 testes e build | Aprovado |
| AC16 | Wheel não editable, diretório neutro, origem em site-packages e rejeição LIVE | Aprovado |

Para repetir apenas cenários negativos e diagnóstico:

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR="$PWD/.uv-cache"
uv run --locked pytest -q tests/unit/test_config.py tests/unit/test_decimal.py tests/unit/test_cli.py tests/integration/test_cli.py
```

Esse comando agrupa os testes já executados na suíte completa; a evidência final registra a execução completa. Arquivo ilegível é simulado com `PermissionError` determinístico, evitando dependência de permissões do usuário que roda o teste.

## 5. Diagnóstico, correções e limitações

Durante a execução inicial, uma configuração `exclude` do Ruff substituiu as exclusões padrão e permitiu alterações em `.venv`. Foi corrigida para `extend-exclude`; ambiente e cache criados nesta execução foram removidos e recriados antes dos checks finais. Nenhum ambiente preexistente foi removido. A reinstalação corretiva usou `UV_LINK_MODE=copy`.

O pytest inicialmente detectou colisão entre os dois arquivos `test_cli.py`; foi configurado `--import-mode=importlib`. O mypy exigiu `Never` no retorno da sobrescrita de `ArgumentParser.error`; a anotação foi corrigida. As falhas iniciais não foram contabilizadas como aprovações; os resultados registrados são da execução final corrigida.

Falha de configuração: corrigir arquivo/override, sem trocar de modo ou ignorar a validação. Falha de importação do wheel: revisar descoberta de pacotes e reinstalar o artefato reconstruído. Falha de tipagem, redaction ou bloqueio de rede exige corrigir e repetir os checks afetados.

O bloqueio por audit hook verifica a execução Python desta base; não é um firewall de sistema operacional. Não foram executados testes AWS, Binance, performance, carteira ou negociação, porque esses componentes não existem nesta Sprint. Nenhum segredo real foi consultado e nenhuma mensagem ou ordem externa foi enviada.

## 6. Organização dos repositórios — pendência resolvida

A aplicação e seus arquivos de configuração, fontes, testes e lock estão no repositório independente `/home/cams7/Dev/Cripto/cripto-bot`. A documentação central permanece no repositório `/home/cams7/Dev/Cripto/docs`.

Antes da reorganização, a aplicação ficava diretamente no workspace e fora do alcance do Git de `docs`. Essa pendência foi resolvida por solicitação do responsável, com a criação do Git próprio do módulo. Não houve commit ou configuração de remoto nesta execução. A Sprint 02 não foi iniciada.

## 7. Limpeza e custos

Custo AWS desta execução: zero; nenhum recurso foi criado ou API AWS utilizada. Foram consumidos somente recursos locais e downloads de dependências.

Não há estado financeiro a restaurar. Dentro de `/home/cams7/Dev/Cripto/cripto-bot`, após inspecionar origem e necessidade, podem ser removidos os artefatos gerados `.venv`, `.venv-wheel`, `.uv-cache`, `.wheel-smoke`, `dist`, `build`, caches de ferramentas, `.coverage` e `modules/trading/src/cripto_bot.egg-info`. A remoção não foi feita ao final para permitir inspeção. Preservar manifest, lock, fontes, testes, exemplo e documentos. Não usar `git clean` amplo ou apagar ambientes preexistentes.

## 8. Fontes consultadas

Documentação oficial consultada em 24/10/2026, além do planejamento e da especificação:

- [uv — Python](https://docs.astral.sh/uv/guides/install-python/) e [lock/sync](https://docs.astral.sh/uv/concepts/projects/sync/).
- [setuptools — descoberta de pacotes](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html).
- [Pydantic — configuração](https://docs.pydantic.dev/latest/api/config/).
- [pytest — modos de importação](https://docs.pytest.org/en/stable/explanation/pythonpath.html).
- [Ruff — configuração e exclusões](https://docs.astral.sh/ruff/configuration/).
- [mypy — opções de verificação](https://mypy.readthedocs.io/en/stable/command_line.html).

As páginas acompanham suas versões correntes; as versões efetivamente testadas são as da tabela e do lock, não necessariamente as mais recentes publicadas.

## 9. Repositório independente e revalidação em 24/10/2026

O responsável definiu que cada módulo terá diretório diretamente em `/home/cams7/Dev/Cripto` e Git independente. Foram movidos para `cripto-bot/`: README, manifest, lock, `.python-version`, `.gitignore`, configuração, fontes e testes. Executado `git init --initial-branch=main` nesse diretório. O Git da documentação permaneceu intacto. Nenhum commit ou remoto foi criado.

A pendência da seção 6 está resolvida quanto à organização: os arquivos agora estão dentro do novo repositório e aparecem como não rastreados, disponíveis para o primeiro commit. Ambientes e artefatos antigos na raiz foram preservados; novos ambientes foram criados no módulo, pois virtualenvs contêm referências absolutas e não devem ser simplesmente movidos.

Comandos executados a partir de `/home/cams7/Dev/Cripto/cripto-bot` (todos com exit code 0):

```bash
cd /home/cams7/Dev/Cripto/cripto-bot
export UV_CACHE_DIR=/home/cams7/Dev/Cripto/.uv-cache
uv sync --locked --group dev
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy modules/trading/src
uv run --locked pytest -q --cov=cripto_bot --cov-branch --cov-report=term-missing
uv build --quiet
uv venv --python 3.13.15 .venv-wheel
uv pip install --python .venv-wheel/bin/python dist/cripto_bot-0.1.0-py3-none-any.whl
uv run --locked python tests/wheel_smoke.py
git rev-parse --show-toplevel
git status --short
```

Resultado: 79 testes aprovados, 100% de cobertura de linhas e ramificações, Ruff/formatação e mypy aprovados. Wheel validado sob bloqueio de sockets, com VALID/PAPER, NOOP/PAPER/0 ordens e rejeição LIVE com código 2.

Novo SHA-256 do wheel: `6648586f24285bbea538f335b6d5be7fc9b45b116fc4b908bec4d34d2962f03c`. Origem de importação: `/home/cams7/Dev/Cripto/cripto-bot/.venv-wheel/lib/python3.13/site-packages/cripto_bot/__init__.py`. O hash anterior (`a63c44062eed804c45723c3a2b0708f5d8140abcc3a32944008060e1e7e9e6e7`) foi preservado nas evidências originais do JSON; não corresponde ao wheel reconstruído no novo diretório.

Os links no README foram ajustados para `../docs`. A documentação central segue no repositório próprio e os fontes/lock estão disponíveis para versionamento no Git de `cripto-bot`. Não houve mudança no comportamento da aplicação ou integração externa.

## Adendo documental de 25/10/2026 — validações antes de LIVE

O aceite registrado neste documento permanece restrito ao escopo histórico executado. Ele não comprova backtest fora da amostra, PAPER contínuo, Demo Spot, Spot Testnet ou `POST /api/v3/order/test`. A sequência e os gates atualizados estão no [planejamento, seção 10](../planejamento.md#10-gates-entre-ambientes-e-modos) e no [roteiro de validação](../testes/validacao-pre-live.md). Demo passa à Sprint 09, Testnet complementar à 10 e preparação LIVE à 11, sem ativação. A implementação desta Sprint continua exclusivamente PAPER; DEMO/TESTNET/LIVE não são liberados por esta revisão.

Nenhum teste foi repetido e nenhuma evidência JSON foi alterada por este adendo. A solicitação atual autoriza somente revisão documental. LIVE permanece bloqueado por padrão e exige validações concluídas, limites de risco reais e aprovação explícita vigente do responsável.
