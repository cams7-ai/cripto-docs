"""Generate the guide only from recorded proof; keep external milestones pending."""

import json
from pathlib import Path

ROOT = Path("/home/cams7/Dev/Cripto")
DOC = ROOT / "docs"
BOT = ROOT / "cripto-bot"
e = json.loads((DOC / "testes/sprint-06d-evidencias.json").read_text())
v = e["verification"]
m = e["measurements"]
c = e["compatibility"]
rows = []
refs = {
    1: "baseline/acceptance.json; 214 hashes/16 artefatos; 542 testes/22 smokes anteriores",
    2: "test_continuous_composition: flags/NOOP/escopo/opt-ins/preparo sem efeitos; configuração estrita",
    3: "test_continuous_storage: schema/lock/readonly/projeções adulteradas/replay/CAS",
    4: "Clock/Feed sintéticos, quatro rotas mockadas, warmup/slots/gap/futuro/RTT/jump/metadata/freshness; preflight real pendente",
    5: "Oráculo instalado: BUY0.4+0.3/cancel e SELL0.2/cancel; Decimal80/partidas/fees/custo/inventário",
    6: "test_continuous_engine: cap/qty0/dust/latência/TTL/LIMIT/quote repetida/nenhum fill garantido",
    7: "Limites, saldo próprio, orçamento de reserva e parâmetros mais restritivos; sem alavancagem",
    8: "Mortes reais de processo em commit de reserva/fill e publicação de controle; IDs conflitantes/CAS/UNKNOWN",
    9: "pause/kill/disable/resume, custódia/owner/geração e preservação de UNKNOWN, sem liquidação",
    10: "Owner único e capacidades inválidas/ausentes rejeitadas; não há carteira combinada implementada",
    11: "PublicSource existente por MockTransport; sockets bloqueados, guard negativo dos wheels; rede real não executada",
    12: "Fila independente, payload/hash/dedupe/lease/retries/UNKNOWN/fallback/backup/restauração e rate global",
    13: "MockTransport mail/WhatsApp, sessão fechada/semântica/timeout/tamanho/deadline; FakeSender não repete finanças",
    14: "NÃO EXECUTADO: falta instrução explícita e configuração autorizada de serviços/destinatários",
    15: "Quatro wheels -I/cwd neutro,31 comandos, standalone analytics e comparação readonly selada/registro final",
    16: "NÃO EXECUTADO: falta autorização para rede pública, preflight elegível e janela real congelada",
    17: "NÃO EXECUTADO: zero horas reais; teste acelerado registra672 MISSED e nunca aprova piloto",
    18: "HTML/JSON/manifest sintéticos conciliados/revisão visual; sete diários reais e consolidado pendentes",
    19: "RSS/latência/bytes/disco de drills; 0 requests/recibos reais; crescimento/hora/uptime/rede/serviços reais pendentes",
    20: "README/API/runbook/ADR0011/arquiteturas/SMA/catálogos/matriz/bancos/guia/evidências atualizados",
    21: "Pausa/custódia e backup/restore dos dois bancos sintéticos; rollback preserva dados/modelos anteriores; operação pendente",
    22: "PENDENTE: D14/D16/D17 e componentes operacionais não preenchidos; gate global/07 não liberados",
}
for i in range(1, 23):
    key = f"D{i:02}"
    rows.append(f"| {key} | {e['acceptance'][key]['status']} | {refs[i]} |")
text = (
    f"""# Validação da Sprint 06D

Execução iniciada em 26/10/2026; guia pendente criado antes dos ensaios. **Estado atual: {e["status"]}.** D-M1–D-M3 aprovados somente no recorte offline; D-M4/D-M5 pendentes. Sprint06D não aprovada globalmente e07 não liberada.

Fontes: [especificação](../sprints/sprint-06d.md), [planejamento](../planejamento.md), [evidências](sprint-06d-evidencias.json), [relatório](relatorios/sprint-06d/report.html), [schema efetivo](sprint-06d-schema.json), [pré-protocolo NÃO ARMADO](sprint-06d-pre-protocolo.json), [runbook](../operacao/continuous-runbook.md), [API](../api/continuous.md), [ADR0011](../decisoes/0011-paper-continuous-e-entrega-local.md).

## Execução e composição

Conferidos214 hashes e16 artefatos atuais06C antes de alterações; baseline archivada em `cripto-bot/reports/sprint06d/baseline/tracked-baseline.tar`. Cinco HEADs e alterações finais no JSON; três entradas staged preexistentes de docs preservadas, sem add/reset/commit. Core/dados sem alteração de fontes ou novos artefatos. Reconstrução externa anterior preservada: dist/06a-final não é rotulado como release original06A; [registro06C](sprint-06c-reconstrucao-externa.json).

Python3.13.15, uv0.12.19, setuptools84.2.0; core0.1.0/data0.1.0/bot0.1.0, analytics0.1.1 e DuckDB1.5.6. Única mudança de versão no lock do bot: analytics0.1.0→0.1.1 para renderer, construído antes da integração. README final alterou hash do wheel novo durante esta execução; entrada local recalculada offline mantendo o pin1.1 e demais versões, seguida de sync/checagem. Nenhum artefato06A–06C sobrescrito.

Mecanismo paper-continuous-v1, schema1 próprio; journal/partidas/ordens/fills/ciclos/config/controles/eventos financeiros atômicos. Carteira/risco/execução pertencem ao bot; core e dados reutilizados; analytics apenas apresenta snapshot. Outbox derivada em banco separado. Defaults desabilitados e controles de estratégia separados dos parâmetros de avaliação. Sem rede de mercado/serviços de entrega, conta/chaves Binance, private/order/test, mensagens efetivas, AWS, otimização/backtest econômico novo, 07/BT ou commits/publicação.

## Verificações executadas

| Etapa | Obtido |
|---|---|
| Baseline bot | {v["baseline"]["pytest"]["tests"]} testes; {v["baseline"]["pytest"]["time"]}s; qualidade e22 smokes |
| Suíte completa após implementação | {v["bot"].get("tests")} testes aprovados; {v["bot"].get("time")}s; confirmação sem cobertura |
| Revisão final de correções | {v["release_review"].get("tests")} testes aprovados; {v["release_review"].get("time")}s; conjunto se sobrepõe à suíte, não somar contagens |
| Analytics | {v["analytics"].get("tests")} testes; qualidade; wheel standalone sem bot; renderer escapado |
| Qualidade final bot | Ruff/check de formato e mypy78 fontes aprovados |
| Release instalada |22 comandos anteriores+9 continuous, quatro pacotes por wheel, -I/cwd neutro/sem editable/PYTHONPATH, sockets bloqueados |
| Compatibilidade | {c.get("curves_equal")} curvas sintéticas iguais, respostas financeiras iguais,6 arquivos exatos e linhas Parquet tipadas iguais; retomada de identidade antiga bloqueada |
| Histórico |16 artefatos atuais anteriores e registro final intactos; DDL/reducers anteriores inalterados |

A confirmação completa de642 casos foi seguida somente pelo ajuste canônico das portas locais, limite restante/normalização de erro do adapter de mercado e acabamento de apresentação; revisão108, analytics30/standalone e wheels finais verificam essas mudanças localizadas. A etapa anterior635 inclui a cobertura registrada. Primeira execução ampla teve626 passes/1 falha porque fontes mudaram entre congelamento e retomada; mantida no log, seguida da suíte estável aprovada. coverage.json corresponde à etapa635 anterior às correções focadas finais; não declarar percentual global final a partir dela. A etapa635 emitiu4 avisos de depreciação de fork e1 ResourceWarning de conexão SQLite de fixture; a confirmação642 emitiu6 avisos de fork e nenhuma falha. Revisão final passou sem avisos. Fork é injeção de morte nos testes; entrega de produção usa subprocess isolado com deadline.

Os logs/casos não são evidência de mercado real. Diretórios `reports/sprint06d/test-*`, `offline/oracle-*` e `.wheel-smoke/06d/*` são sintéticos. Teste acelerado termina com672 slots inválidos e0 válidos/672, sete marcadores DAILY e SYNTHETIC_NOT_PILOT; isso testa o denominador e não comprova duração real.

## Comandos reproduzíveis e resultados

Executados a partir de `/home/cams7/Dev/Cripto/cripto-bot`, com `UV_CACHE_DIR=$PWD/.uv-cache`, sem download. Exemplos correspondem ao software offline; não iniciam piloto externo:

```bash
uv sync --locked --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline mypy src
uv run --locked --offline pytest -q --basetemp=reports/sprint06d/test-complete-release --junitxml=reports/sprint06d/offline/full-release.xml
uv run --locked --offline pytest -q --cov=cripto_bot --cov-branch --cov-report=json:reports/sprint06d/offline/coverage.json --basetemp=reports/sprint06d/test-full-final --junitxml=reports/sprint06d/offline/full-final.xml
uv run --locked --offline pytest -q tests/integration/test_continuous_composition.py tests/integration/test_continuous_storage.py tests/unit/test_continuous_engine.py tests/unit/test_continuous_notifications.py tests/unit/test_analytics_composition.py --basetemp=reports/sprint06d/test-release --junitxml=reports/sprint06d/offline/release-tests.xml
uv build --offline --out-dir dist/06d-final
WHEEL_SMOKE_STAGE=06d .venv/bin/python tests/wheel_smoke.py
.venv/bin/python ../docs/testes/ferramentas/sprint-06d-wheel-continuous.py
.venv/bin/python ../docs/testes/ferramentas/sprint-06d-drill.py
.venv/bin/python ../docs/testes/ferramentas/sprint-06d-compatibilidade.py
```

Instalação por `.venv-wheel-06d`: uv venv com Python já disponível; export externo fixado excluindo os quatro projetos; helper06A verifica versões/RECORD/hashes ao reutilizar dependências do ambiente06C; uv pip install --offline --no-deps instala os quatro wheels por caminho. Reinstalação final sem cache somente dos artefatos novos desta sessão. Standalone analytics em `.venv-standalone-06d` contém core/DuckDB/analytics, sem bot. Não alegar instalação completa em cache frio.

Comandos/script completos, stdout/stderr, hashes e timestamps em `reports/sprint06d/offline/` e evidências; `lock-final.log` registra `uv lock --offline --upgrade-package cripto-analytics`, recalculando apenas o pin exato1.1. `--refresh-package` com --offline foi recusado pelo uv e não utilizado para resolver dependências. O comparador verifica que nenhuma outra versão mudou. Helpers de documentação não são funcionalidades do bot.

## Critérios D01–D22

| ID | Estado | Prova e limite |
|---|---|---|
"""
    + "\n".join(rows)
    + f"""

AC01–AC18 comuns permanecem condicionados ao recorte aplicável e ao gate integrado do agregador. AC12/AC13 e extrações anteriores preservados. Nenhum critério operacional foi removido como não aplicável para tornar esta entrega aprovada. D14/D16/D17 e partes externas de D04/D11–D13/D18/D19/D21/D22 continuam sem evidência real.

## Oráculos, falhas e decisões

BUY1@100, fee0.1%, reserva100.10: fills0.4/0.3 custam40.04/30.03; cancel libera30.03; livre9929.93USDT,0.7BTC, custo70.07, fees0.07. SELL0.2@110 gera21.978 líquidos, baixa20.02 custo, realizado1.958 e restante0.5/custo50.05. Journals/partidas/projeções reconciliados, reservas finais zero. Snapshot stale mostra equity indisponível e última marca separada; fixture nunca recebe status de piloto aprovado.

Correções cobertas: UNKNOWN conserva reservas sob pause/kill/disable/expiry; somente cancel explícito após replay libera. Identidade compara forma canônica após JSON. Livro anterior dentro da ordem não cria capacidade nova; cap/TTL/dust/qty nula não garantem fill. Controle só é aplicado após ack em journal. Metadados diferentes pausam sem substituir regra congelada, sem conflitos/repetição infinita. Salto de clock persiste pausa antes de --once retornar. Preparo com pacote inválido falha antes de banco.

Revisão automática rejeitou proposta de selecionar o primeiro módulo por risco de contornar flags. Proposta abandonada; seleção por active_for preservada. Alternativa autorizada só conserva limites financeiros mais restritivos no ramo de custódia com module=None, active=False e flags desligadas, comprovados pelo teste. Não houve ativação indireta.

Esclarecimento temporal: preflight valida50 candles correntes fechados antes de congelar T0 futuro; a janela final de51 candles causais é reconfirmada no primeiro score. Não solicitar candle futuro para cumprir warmup antecipadamente. Recusa por custódia com dados válidos pode contar como processada conforme seção10.1; ausência de dado/clock/atraso não vira HOLD válido. Todos os slots, inclusive kill/downtime/disable, permanecem no denominador.

## Recursos e limites observados

Drills instalados pequenos: financeiro RSS{m["financial_rss_mib"]:.2f}MiB; worker FakeSender RSS{m["worker_rss_mib"]:.2f}MiB; maior evento{m["max_financial_event_ms"]:.2f}ms; dez passes da fila{m["worker_ten_passes_ms"]:.2f}ms. Bytes dos bancos e disco livre no JSON, medidos na coleta. Fontes HTTP locais/públicas testadas por mocks; payload/response/timeout/rate/backoff/leases verificados. Zero requests reais de mercado/serviços, recibos e horas observadas. Fontes técnicas oficiais foram consultadas separadamente; essas consultas não são coleta do projeto. Custos AWS0; consumo local não foi convertido em tarifa, custos dos serviços externos não presumidos zero.

Alvo512MiB por processo e reserva5GiB antes de iniciar; aviso2GiB/pausa1GiB. Medição sintética não valida uptime/restarts, crescimento por hora, rede/peso429 ou serviços durante sete dias. Esses campos permanecem indisponíveis, com coleta do supervisor exigida no runbook; não preencher com zero para parecer disponibilidade100%. Proxy de participação10% do book não comprova fila/liquidez/execução real nem desempenho futuro.

## Preparação concreta da fase externa

Exemplo de configuração desabilitado no bot, quatro wheels identificados, [pré-protocolo](sprint-06d-pre-protocolo.json) com T0/Tend nulos, [runbook](../operacao/continuous-runbook.md) e [API](../api/continuous.md) prontos. Faltam instrução explícita para dados públicos, serviços/destinatários de teste, preflight elegível/recursos/supervisão e sete dias reais. Flags --allow-network/--allow-send são guards técnicos. Não iniciar daemon ou produzir manifesto de piloto com horários sintéticos como se fosse operação.

## Revisão documental e visual

DDLs criados em scratch/introspectados:9 tabelas/24 objetos financeiros e3 tabelas/7 objetos de fila, schema1; quick_check ok, FK sem violação. PK/FK/índices/constraints/triggers e tipos/nulos/defaults correspondem ao [schema JSON](sprint-06d-schema.json) e aos documentos dos bancos. Criação inicial, sem migração/reset. Backup/restore ensaiados em diretórios novos; rollback não converte continuous para modelo antigo.

HTML deriva deste JSON de evidências e dos snapshots, com valores conferidos no oráculo. Preview de validação e de snapshot financeiro local revisados com Chrome headless, sem resolver rede: [preview](relatorios/sprint-06d/preview.png), [oráculo](relatorios/sprint-06d/oracle-preview.png). Conteúdo/valores/pendências legíveis, sem sobreposição; hashes finais e estado da revisão no JSON. Exportação não reavalia sinais ou finanças.
"""
)
(DOC / "testes/sprint-06d-validacao.md").write_text(text)
