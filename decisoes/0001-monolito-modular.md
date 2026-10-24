# ADR 0001 — Pacote único com camadas mínimas

Data: 24/10/2026. Estado: adotada na implementação local da Sprint 01.

## Contexto

A primeira Sprint precisa comprovar empacotamento, configuração e execução local segura. Ainda não há justificativa para serviços independentes ou infraestrutura. O [planejamento](../planejamento.md) prevê crescimento incremental com regras independentes das integrações.

## Decisão

Usar um pacote `cripto_bot`, origem em `modules/trading/src`, com setuptools como backend e console script declarado no `pyproject.toml`. `uv.lock` fixa a resolução das dependências; uv 0.12.19 é exigido pelo manifest e Python 3.13.15 é fixado em `.python-version`.

Separar domínio puro, aplicação, adapter de configuração, apresentação CLI e serialização de logs. Usar funções pequenas e dataclasses, sem framework de plugins ou de injeção. Apenas os componentes necessários ao ciclo vazio foram criados.

Pydantic valida a fronteira; argparse e tomllib evitam dependências adicionais. pytest/pytest-cov, Ruff e mypy strict complementam a verificação do wheel instalado. O modo de importação `importlib` do pytest permite módulos de teste com o mesmo nome em diretórios diferentes.

## Alternativas e consequências

Microsserviços, framework web e processamento assíncrono acrescentariam operação sem atender a um requisito desta etapa. Um único script misturaria fronteiras e dificultaria testar a configuração antes de executar.

O layout exige configurar explicitamente a descoberta de pacotes; por isso a validação instala o wheel fora do ambiente editable. Não criar interfaces de integrações futuras até existir uso real.

A raiz Git encontrada em `docs` não cobre a aplicação no diretório pai. Essa decisão não autoriza reorganização do Git; o alcance de versionamento precisa ser definido separadamente. O lock foi produzido, mas ainda está fora do repositório existente.

## Atualização autorizada em 24/10/2026 — repositórios independentes

O responsável definiu um repositório Git por módulo independente, cada qual em diretório diretamente na raiz `/home/cams7/Dev/Cripto`. A aplicação agora reside em `cripto-bot/`, com Git inicializado na branch main; a documentação permanece em `docs/`, preservando seu histórico. Manifest, lock, fontes e testes foram movidos para o novo repositório. Isso resolve a pendência descrita acima, sem mudar a decisão de um pacote único para a aplicação. Não houve commit ou remoto.
