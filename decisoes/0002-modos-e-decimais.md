# ADR 0002 — PAPER exclusivo e decimais explícitos

Data: 24/10/2026. Estado: adotada na implementação local da Sprint 01.

## Contexto

A base deve falhar diante de configuração não suportada e evitar conversões monetárias por float. Não existe executor financeiro nesta Sprint.

## Decisão sobre configuração

Somente o literal exato `PAPER` é aceito. Sem arquivo, usar defaults internos. Um caminho explícito ausente ou inválido falha sem fallback. Ler TOML com tomllib e validar com Pydantic, `extra="forbid"` e validação estrita.

A precedência é default → arquivo → ambiente, validando o arquivo antes do override. O único override aceito é `CRIPTO_BOT_MODE`. Variáveis desconhecidas no namespace `CRIPTO_BOT_` e a presença das duas credenciais Binance especificadas são proibidas, inclusive vazias. Outras variáveis não são interpretadas como configuração.

Erros têm códigos e eventos fixos; não incluir valores, nomes arbitrários de campos, conteúdo TOML ou mensagens originais do parser/Pydantic. O parser seguro também impede que argumentos desconhecidos com segredos sintéticos apareçam no diagnóstico. Não carregar `.env` ou ler arquivos de credenciais.

Configuração válida é convertida em dataclass do domínio antes do caso de uso. Não há importação ou construção de clientes privados. A ausência desses componentes complementa o bloqueio de modo.

## Decisão sobre precisão

O conversor recebe exclusivamente strings e constrói `Decimal` diretamente. Rejeita outros tipos, strings inválidas e valores não finitos; aceita negativos finitos porque ainda não representa preço ou quantidade. A soma 0.1 + 0.2 é testada sem float intermediário.

Não alterar o contexto global decimal ao importar. Não há quantização, persistência monetária, validação de filtros da corretora ou política financeira de arredondamento nesta etapa. Esses requisitos pertencem aos modelos futuros que usarão o conversor.

## Consequências

TESTNET/LIVE exigem implementação e avaliação próprias; trocar uma variável não os ativa. A base retorna apenas NOOP. Diagnósticos sanitizados fornecem menos detalhes da entrada, compensados por testes de fronteira e documentação dos contratos.

O tipo `Literal` orienta a tipagem; a validação efetiva de entradas externas ocorre no adapter. Esta decisão não atribui a dataclasses uma garantia de validação dinâmica de dados arbitrários.
