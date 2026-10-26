# ADR 0008 — Core puro e identidade da composição instalada

Data: 26/10/2026. Estado: implementada na Sprint 06A; resultado do aceite no [guia 06A](../testes/sprint-06a-validacao.md).

## Contexto

O layout antigo continha todo o bot em `modules/trading/src`. SMA e preço/plano/sizing eram puros, porém dependiam de erros/DTOs/helpers misturados à configuração e carteira. O fingerprint enumerava o caminho antigo no checkout; extrair sem ampliar a identidade deixaria mudanças no core invisíveis ao protocolo.

## Decisão

Validar primeiro o layout `cripto-bot/src/cripto_bot` (M1); só depois extrair `cripto-core/src/cripto_core` (M2). Core é biblioteca padrão Python, sem efeitos ou dependência inversa. Números/erros/serialização/validação necessários, Plan, execução sintética/sizing e SMA possuem fonte única; o bot mantém fachadas explícitas e identidade dos tipos. Wallet/ledger, risco/admissão, coordenação, backtest, flags, configuração e adapters permanecem no bot. Plan mantém a identidade serializada `paper-integral-v1`, sem criar outro modelo de banco.

Distribuição core 0.1.0, dependência exata no bot e fonte local explícita do wheel. Locks separados, sem workspace ou Git agregador. O lock do consumidor fixa SHA256 do artefato; ambientes de smoke separados por marco instalam os wheels e usam dados/controles sintéticos em raiz própria. Core sem bot é validado separadamente. Nenhuma publicação/commit implícito.

A identidade `runtime-composition-v1` combina hashes de manifest/lock/pin do consumidor e arquivos Python realmente carregados do bot/core, versão e modo de instalação. Em wheel, conferir inventário/caminhos e hashes SHA256 de RECORD; inconsistência/missing metadata é erro. Bot editable é aceito somente com origem explícita em seu src; core editable é rejeitado no consumidor desta entrega. Não depender de caminhos absolutos de checkouts ou apenas do número de versão. RECORD verifica consistência local, não assinatura/atestado externo. Wheel hash, inventário e origem são confrontados na entrega.

O valor `code_sha256` dos protocolos passa a refletir essa composição; o campo persistido continua hash textual, sem mudar DDL/schema. Protocolo antigo não é reescrito: retomar sob código diferente falha; report continua lendo identidade selada e reconciliando o journal. Fontes/versões anteriores são preservadas para recuperação. Registro final e dados permanecem no bot. Reorganização não cria amostra final intocada.

## Consequências

O wheel local precisa existir no caminho documentado para sync locked; a release ainda não está publicada em índice. Atualização do conteúdo exige nova identidade, atualização deliberada do lock e revalidação. O cache offline local não cobriu todos os binários de terceiros; ambientes da entrega reutilizaram dependências da baseline instalada após verificar versões e RECORD, com evidências e helper de reprodução. Isso não demonstra instalação completa com cache frio. Bot/core foram construídos e instalados por wheels; testes não importam o checkout irmão.

Sem mudança de regras financeiras, schemas, capital, flags ou modos. Extrações de dados/análise e piloto ficam em 06B–06D. Referências: [especificação](../sprints/sprint-06a.md), [planejamento](../planejamento.md), [ADR 0006](0006-backtest-historico-e-protocolo.md) e [ADR 0007](0007-duckdb-parquet-analitico.md).


## Adendo 06B

Core/wheel 06A permaneceram inalterados. A identidade do consumidor acrescenta market-data 0.1.0 efetivamente instalado; a inspeção genérica de pacotes foi compartilhada com a biblioteca de dados, enquanto runtime_identity, controles do bot e política de instalações aceitas continuam no bot. As regras de RECORD/origem/versão e rejeição de core/dados editables permanecem. Não se altera identidade selada anterior para aceitar código novo. [ADR 0009](0009-market-data-e-proveniencia-do-produtor.md).


## Adendo 06C

A composição do consumidor acrescenta analytics 0.1.0 efetivamente instalado, mantendo política/inspector de RECORD existentes. Core/dados e suas distribuições permanecem inalterados. Mudar analytics bloqueia retomada congelada sem impedir reexportação readonly da identidade selada; registro final permanece no bot. [ADR 0010](0010-analytics-por-snapshots-somente-leitura.md).
