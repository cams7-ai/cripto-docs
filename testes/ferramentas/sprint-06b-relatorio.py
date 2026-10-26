"""Render a self-contained report from recorded 06B evidence; no market execution."""
import html
import json
from pathlib import Path

DOCS=Path(__file__).resolve().parents[2]
def render():
    e=json.loads((DOCS/'testes/sprint-06b-evidencias.json').read_text())
    def esc(x): return html.escape(str(x))
    rows=''.join('<tr>'+''.join(f'<td>{esc(v)}</td>' for v in [name,d['pytest']['tests'],d['pytest']['failures'],f"{float(d['pytest']['time']):.3f} s",f"{d['coverage']['percent_covered']:.2f}%"] )+'</tr>' for name,d in e['verification'].items())
    artifacts=''.join(f'<tr><td>{esc(k)}</td><td class="hash">{esc(v)}</td></tr>' for k,v in e['artifact_sha256'].items() if '/06b-final/' in k and k.endswith(('.whl','.tar.gz')))
    accepted=sum(i['status']=='APPROVED' for i in e['acceptance'].values())
    output=DOCS/'testes/relatorios/sprint-06b/report.html';output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text('''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>Sprint 06B — Relatório técnico</title><style>
:root{font:16px/1.55 system-ui,sans-serif;color:#172c3d;background:#eef3f6}body{max-width:1040px;margin:30px auto;padding:0 24px}
header,section{background:white;border:1px solid #dce5eb;border-radius:12px;padding:26px 32px;margin:0 0 18px}header{border-top:7px solid #126665}
h1{font-size:34px;line-height:1.2;margin:12px 0}h2{font-size:21px;margin:0 0 12px}.eyebrow{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#126665;font-weight:700}
p{margin:10px 0}.muted{color:#536779}.cards{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:22px}.card{background:#edf7f4;border-radius:8px;padding:16px}.card strong{display:block;font-size:28px;color:#126665}
table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;vertical-align:top;padding:10px 8px;border-bottom:1px solid #dce5eb}th{background:#f3f6f8}.hash{font:11px/1.6 monospace;overflow-wrap:anywhere}.notice{border-left:4px solid #c89538;padding-left:16px}.small{font-size:13px}code{font-size:.9em;overflow-wrap:anywhere}a{color:#126665}
@media(max-width:700px){body{padding:0 12px}header,section{padding:20px}.cards{grid-template-columns:1fr}h1{font-size:28px}td,th{padding:7px 4px}}
@media print{body{margin:0;padding:0;background:white}header,section{break-inside:avoid;border-radius:0}table{font-size:11px}}
</style></head><body><header><div class="eyebrow">Engenharia · 26 de outubro de 2026 · local / PAPER</div>
<h1>Sprint 06B<br>Dados de mercado em biblioteca independente</h1><p class="muted">Extração de coleta, parsers, store e exportação. Evidências offline com dados sintéticos e sockets bloqueados.</p>
<div class="cards"><div class="card"><strong>533 → 537</strong>testes do bot, antes e depois</div><div class="card"><strong>120</strong>testes da biblioteca de dados</div></div></header>
<section><h2>Composição e limites</h2><p><code>cripto-bot → cripto-market-data → cripto-core</code>. Instalação pelos três wheels; standalone sem bot ou DuckDB. Core e seis artefatos 06A preservados. Git do novo projeto sem commit ou remoto.</p>
<p>Bot conserva carteira, risco, coordenação, flags, backtest e análise. Sem estratégia nova, migração física de dados ou ativação implícita. Python 3.13.15, uv 0.12.19, setuptools 84.2.0; distribuições próprias 0.1.0 identificadas também por hash.</p></section>
<section><h2>Marcos e qualidade</h2><p>B-M1 baseline aprovada antes da extração; B-M2 standalone aprovado antes da integração; B-M3 verificado com composição instalada. Ruff, formatação, mypy e builds aprovados.</p>
<table><thead><tr><th>Execução</th><th>Testes</th><th>Falhas</th><th>Tempo XML</th><th>Cobertura combinada</th></tr></thead><tbody>'''+rows+'''</tbody></table>
<p class="small muted">Cobertura por pacote: a extração altera o denominador do bot. Core: 54 testes históricos da 06A; sem reexecução nesta etapa, com fontes/controles/artefatos conferidos.</p></section>
<section><h2>Coleta, retomada e publicação</h2><div class="cards"><div class="card"><strong>2 → 0</strong>inseridos: fixture inicial → repetição</div><div class="card"><strong>22 + 5</strong>comandos: integração + standalone</div></div>
<p>Três replays alternados entre CLIs: zero inserções, mesmo dataset e hash. Ambas bloqueadas pelo mesmo writer lock com saída 3/WRITER_BUSY. Store anterior preserva schema, candles e checkpoint. DDL e classe do store têm AST idêntico.</p>
<p class="small">Candles SHA-256:<br><code class="hash">fec39ffcbf53d685fcd5606a51585e364c6dbecd06b991d0dabc4722e04aa74d</code></p>
<p>Manifesto mantém quatro arquivos e valida seus hashes; proveniência identifica o produtor. Novo manifesto com 1.010 candles aceito pelo preparo histórico: 50 warmup + 960 score. Rollback/morte, publicação incompleta, orçamento/retry/429/418 e paths/credenciais inválidos cobertos por ensaios offline.</p></section>
<section><h2>Regressão financeira e identidade</h2><p>Oito respostas PAPER/SMA mantêm hashes financeiros. Saldo manual <strong>10009.58001000</strong>; SMA <strong>9905.46181258</strong>, 71 ciclos e replay sem fills novos. <strong>48 curvas sintéticas equivalentes</strong>, incluindo métricas, chart, motivos e períodos; excluídos somente run_key/checkpoint_bytes ligados à nova identidade.</p>
<p>Alteração isolada em market-data muda fingerprint e bloqueia retomada congelada. Relatório sintético anterior reexporta a identidade selada sem alterar SQLite. Execução antiga sob código novo retorna FROZEN_PROTOCOL_CHANGED. Registro final real permanece intacto.</p>
<p class="notice">Esses testes retrospectivos sintéticos demonstram compatibilidade técnica. Não representam nova evidência econômica fora da amostra nem garantia de desempenho futuro.</p></section>
<section><h2>Artefatos 06B</h2><table><thead><tr><th>Arquivo relativo ao workspace</th><th>SHA-256</th></tr></thead><tbody>'''+artifacts+'''</tbody></table><p class="small muted">Wheels/sdist locais em diretórios próprios; artefatos 06A não sobrescritos. Versões anteriores dos 27 pacotes do bot preservadas; somente market-data adicionado.</p></section>
<section><h2>Custos, limitações e recuperação</h2><p>Suítes principais: cerca de 9min25s baseline, 9min22s bot final e 3,9s biblioteca. Reports medidos antes do fechamento: bot 3.056 KiB, dados 344 KiB; artefatos 180/68 KiB. Stores/exports isolados de smoke não incluídos. Pico de memória não instrumentado; não é benchmark de throughput.</p>
<p class="notice">Cache frio completo não demonstrado. Dependências externas reutilizadas da baseline após conferir versões do lock e hashes/RECORD; wheels próprios instalados offline. Custo externo zero.</p>
<p>Rollback restaura composição/manifest/lock compatíveis com revisão do trabalho posterior, preservando dados, checkpoints, ledger e registro final. Nenhum reset de banco para contornar incompatibilidade.</p></section>
<section><h2>Decisão e continuidade</h2><p>Critérios aprovados registrados no JSON: <strong>'''+str(accepted)+'''/18</strong>. A revisão visual possui registro próprio nas evidências. 06C é a próxima etapa elegível para detalhamento/revisão. 06D, gate global da 06 e Sprint 07 continuam pendentes.</p><p>Sem rede de mercado, credenciais, ordens, AWS, mensagens, commits/publicação ou nova avaliação da janela final real.</p><p class="small"><a href="../../sprint-06b-validacao.md">Guia e comandos</a> · <a href="../../sprint-06b-evidencias.json">Evidências estruturadas</a></p></section></body></html>''')
    print(output)
if __name__=='__main__': render()
