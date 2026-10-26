"""Render the technical 06A report from its recorded JSON evidence, without running the bot."""

import html
import json
from pathlib import Path

DOCS = Path(__file__).resolve().parents[2]


def render():
    evidence = json.loads((DOCS / 'testes/sprint-06a-evidencias.json').read_text())
    rows = []
    for name, item in evidence['verification'].items():
        if name == 'contracts':
            continue
        tests = item['pytest']
        coverage = item['coverage']
        rows.append('<tr>' + ''.join(f'<td>{html.escape(str(v))}</td>' for v in [
            name, tests['tests'], tests['failures'],
            f"{float(tests['time']):.2f} s", f"{coverage['percent_covered']:.2f}%",
        ]) + '</tr>')
    artifacts = ''.join(
        f"<tr><td>{html.escape(name)}</td><td class='hash'>{value}</td></tr>"
        for name, value in evidence['artifact_sha256'].items()
    )
    output = DOCS / 'testes/relatorios/sprint-06a/report.html'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>Sprint 06A — Relatório técnico</title><style>
:root{color:#152637;background:#eef2f5;font:16px/1.55 system-ui,sans-serif}
body{max-width:1040px;margin:36px auto;padding:0 24px}header,section{background:white;
padding:28px 32px;border-radius:12px;margin-bottom:20px;border:1px solid #dce4ea}
header{border-top:7px solid #126665}.eyebrow{font-weight:700;color:#126665;letter-spacing:.07em;
font-size:12px;text-transform:uppercase}h1{font-size:34px;line-height:1.2;margin:14px 0}
h2{font-size:21px;margin-top:0}h3{font-size:17px}p{margin:12px 0}.muted{color:#536779}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:20px}.card{padding:16px;background:#edf7f4;
border-radius:8px}.card strong{display:block;font-size:27px;color:#126665}table{width:100%;
border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:12px 10px;
border-bottom:1px solid #dce4ea;vertical-align:top}th{background:#f3f6f8}.hash{
font-family:monospace;font-size:11px;overflow-wrap:anywhere}code{font-size:.9em;
background:#eef2f5;padding:2px 4px;border-radius:3px}.notice{border-left:4px solid #c89538;
padding-left:16px}.small{font-size:13px}.ok{color:#126665;font-weight:700}
@media(max-width:700px){body{padding:0 12px;margin:16px auto}header,section{padding:20px}
.cards{grid-template-columns:1fr}h1{font-size:28px}td,th{padding:8px 5px}}
@media print{body{margin:0;padding:0;max-width:none;background:white}section,header{
break-inside:avoid;border-radius:0}table{font-size:11px}.hash{font-size:9px}}
@page{size:A4;margin:14mm}</style></head><body>
<header><div class="eyebrow">Engenharia · 26 de outubro de 2026 · local / PAPER</div>
<h1>Sprint 06A<br>Core puro e composição verificável</h1>
<p class="muted">Validação técnica de layout, extração e instalação. Dados de demonstração
sintéticos; nenhuma avaliação econômica nova ou operação externa.</p>
<div class="cards"><div class="card"><strong>528 → 533</strong>testes do bot:
baseline/layout → composição final</div><div class="card"><strong>54</strong>
testes próprios do core, sem o bot instalado</div></div></header>
<section><h2>Entrega e sequência</h2><p><span class="ok">M1 — layout aprovado antes de extrair.</span>
Fontes do bot em <code>src/cripto_bot</code>, build e wheel isolados, com regressões preservadas.</p>
<p><span class="ok">M2 — integração verificada.</span> Contratos, Decimal, execução/sizing
sintéticos e SMA têm fonte única em <code>cripto_core</code>. Carteira, admissão de risco,
coordenação, flags, ledger e backtest permanecem no bot.</p>
<p>Os dois wheels foram instalados em ambiente novo. Origem de bot/core em
<code>site-packages</code>, sem importar checkout irmão ou depender de PYTHONPATH.</p></section>
<section><h2>Verificação executada</h2><table><thead><tr><th>Marco</th><th>Testes</th>
<th>Falhas</th><th>Tempo</th><th>Cobertura combinada</th></tr></thead><tbody>'''
+ ''.join(rows) + '''</tbody></table><p class="small muted">São execuções separadas da mesma
regressão, não amostras independentes de desempenho. A cobertura do core e do bot tem escopos
distintos após a extração; os percentuais não são diretamente comparáveis. Lint, formatação,
tipagem estrita, builds e contratos também foram verificados.</p></section>
<section><h2>Equivalência financeira e recuperação</h2><table><thead><tr><th>Controle sintético</th>
<th>Esperado e obtido nos três marcos</th></tr></thead><tbody>
<tr><td>Roteiro manual</td><td>10009.58001000 USDT · dois fills · replay zero novos fills</td></tr>
<tr><td>SMA fixture</td><td>9905.46181258 USDT · 71 ciclos · dois fills · replay zero novos fills</td></tr>
<tr><td>Backtest fixture</td><td>48 curvas equivalentes: métricas, séries, motivos e resultados</td></tr>
<tr><td>Banco sintético anterior</td><td>Reexportação preserva hash SQLite e resultado selado;
retomada rejeitada com FROZEN_PROTOCOL_CHANGED</td></tr></tbody></table>
<p>As comparações das curvas excluem run_key e tamanho do checkpoint; os demais campos são
idênticos. Hash de código/protocolo muda legitimamente com a composição e não é tratado
como divergência financeira. O registro real de consumo final permaneceu com o mesmo SHA256.</p></section>
<section><h2>Identidade e isolamento</h2><p>O lock preservou as 26 versões anteriores e acrescentou
somente core 0.1.0. Core não tem dependências de produção. A identidade combina controles do
consumidor, arquivos efetivamente carregados, versão e instalação. Conteúdo fora de RECORD,
versão incompatível, core editable e alteração da composição são rejeitados.</p>
<p>O wheel core foi importado sozinho, sem bot. Bot forçado sem core falha explicitamente.
Os quatro módulos de persistência SQLite mantêm AST idêntica à baseline; não houve migração
ou mudança de esquema. Guards de sockets foram exercitados nos smokes.</p></section>
<section><h2>Artefatos identificados</h2><table><thead><tr><th>Artefato</th><th>SHA256</th></tr>
</thead><tbody>''' + artifacts + '''</tbody></table></section>
<section><h2>Limitações e continuidade</h2><p class="notice">O cache não continha todos os binários
de terceiros. Dependências externas da baseline instalada foram reutilizadas após conferir
versões e RECORD, sem downloads. Isso não demonstra instalação completa com cache frio.
Os wheels locais do bot/core foram construídos e instalados separadamente.</p>
<p>A fonte local do core precisa estar disponível no caminho declarado no lock; não houve
publicação em índice, commit ou remoto. Testes não garantem lucro nem execução real.</p>
<p>06B fica elegível apenas para detalhamento/revisão após o aceite documental. 06C, piloto 06D,
AWS, mensagens, novas estratégias e modos privados continuam fora desta entrega.</p>
<p class="small muted">Fontes: sprint-06a-evidencias.json, JUnit/cobertura dos marcos,
financial-equivalence.json e registros de instalação/compatibilidade. Relatório produzido
sem reexecutar estratégias ou avaliação econômica.</p></section></body></html>''')
    return output


if __name__ == '__main__':
    print(render())
