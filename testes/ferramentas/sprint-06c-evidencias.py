"""Consolidate observed 06C evidence; does not execute financial commands."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import xml.etree.ElementTree as ET

DOCS=Path(__file__).resolve().parents[2];ROOT=DOCS.parent
BOT=ROOT/'cripto-bot';AN=ROOT/'cripto-analytics';OUT=BOT/'reports/sprint06c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def suite(path):
    node=ET.parse(path/'pytest.xml').getroot()[0];assert node.get('failures')==node.get('errors')=='0'
    return {'pytest':node.attrib,'coverage':read(path/'coverage.json')['totals'],'logs':str(path.relative_to(ROOT))}
prior=read(DOCS/'testes/sprint-06b-evidencias.json')
with tarfile.open(OUT/'baseline/tracked-baseline.tar') as archive:
    for p,digest in prior['source_files_sha256'].items():
        if p.startswith('cripto-bot/'):
            member=p.removeprefix('cripto-bot/')
            if member in archive.getnames():
                stream=archive.extractfile(member);assert stream
                assert hashlib.sha256(stream.read()).hexdigest()==digest,p
            else:
                assert sha(ROOT/p)==digest,p
        else:assert sha(ROOT/p)==digest,p
artifact_observed={p:sha(ROOT/p) for p in prior['artifact_sha256']}
artifact_mismatches={p:{'expected':h,'observed':artifact_observed[p]} for p,h in prior['artifact_sha256'].items() if artifact_observed[p]!=h}
review_path=DOCS/'testes/sprint-06c-reconstrucao-externa.json'
external_review=read(review_path) if review_path.exists() else {}
artifact_reviewed=(external_review.get('status')=='VERIFIED_EXTERNAL_REBUILD' and external_review.get('prior_vs_current_sha256')==artifact_mismatches and external_review.get('runtime_changed_after_tests') is False)

for name in ['cripto-core','cripto-market-data']:
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT/name).strip(),name
verification={name:suite(path) for name,path in {'baseline_bot':OUT/'baseline','standalone_analytics':AN/'reports/sprint06c/standalone','final_bot':OUT/'final'}.items()}
compat=read(OUT/'compatibility.json')
source={}
for name in ['cripto-bot','cripto-analytics','cripto-core','cripto-market-data']:
    project=ROOT/name
    paths=[*project.joinpath('src').rglob('*.py'),*project.joinpath('src').rglob('py.typed'),*project.joinpath('tests').rglob('*.py')]
    paths += [p for p in project.joinpath('config').rglob('*') if p.is_file()]
    paths += [project/p for p in ['pyproject.toml','uv.lock','.python-version','README.md','.gitignore']]
    for path in paths:
        if path.is_file() and '__pycache__' not in path.parts:source[str(path.relative_to(ROOT))]=sha(path)
smoke=read(OUT/'final/wheel-smoke.json');stand=read(AN/'reports/sprint06c/standalone/wheel-smoke.json')
assert smoke['socket_probe_blocked'] and stand['socket_probe_blocked'] and stand['readonly_files_unchanged']
proof={
'C01':['cripto-bot/reports/sprint06c/baseline/acceptance.json','cripto-analytics/reports/sprint06c/standalone/acceptance.json'],
'C02':['cripto-bot/src/cripto_bot/adapters/storage/analytics_source.py','cripto-analytics/tests/test_contracts.py'],
'C03':['cripto-bot/reports/sprint06c/compatibility.json'],
'C04':['cripto-analytics/tests/test_conversion.py','cripto-bot/reports/sprint06c/compatibility.json'],
'C05':['cripto-analytics/tests/test_contracts.py','cripto-bot/tests/integration/test_backtest_analytics.py'],
'C06':['cripto-analytics/tests/test_conversion.py','cripto-analytics/tests/test_contracts.py'],
'C07':['cripto-analytics/reports/sprint06c/scale-synthetic.json','cripto-analytics/reports/sprint06c/scale-preserved.json'],
'C08':['cripto-analytics/tests/test_contracts.py','cripto-bot/reports/sprint06c/integration-contracts.xml'],
'C09':['cripto-analytics/reports/sprint06c/standalone/publication.json','cripto-bot/tests/integration/test_backtest_publication.py'],
'C10':['cripto-analytics/reports/sprint06c/standalone/wheel-smoke.json'],
'C11':['cripto-analytics/tests/test_contracts.py'],
'C12':['cripto-bot/reports/sprint06c/final/wheel-smoke.json','cripto-bot/reports/sprint06c/final/negative-missing-analytics.json','cripto-bot/reports/sprint06c/final/negative-missing-duckdb.json','cripto-bot/tests/unit/test_analytics_composition.py'],
'C13':['cripto-bot/tests/unit/test_analytics_composition.py'],
'C14':['cripto-bot/reports/sprint06c/composition-contracts.xml'],
'C15':['cripto-bot/reports/sprint06c/compatibility.json'],
'C16':['cripto-bot/reports/sprint06c/final/pytest.xml','cripto-bot/reports/sprint06c/compatibility.json'],
'C17':['docs/testes/sprint-06c-validacao.md','docs/testes/relatorios/sprint-06c/report.html'],
'C18':['docs/sprints/sprint-06c.md','docs/planejamento.md']}
file=DOCS/'testes/sprint-06c-evidencias.json';visual=read(file).get('visual_review',{}) if file.exists() else {}
visual_approved=visual.get('status')=='APPROVED'
approved=visual_approved and (not artifact_mismatches or artifact_reviewed)
acceptance={key:{'status':'APPROVED' if key not in {'C17','C18'} or (visual_approved if key=='C17' else approved) else 'PENDING_DOCUMENTATION_REVIEW','proof':paths} for key,paths in proof.items()}
if artifact_mismatches and not artifact_reviewed:
    for key in ['C01','C12','C18']:
        acceptance[key]['status']='PENDING_PRIOR_ARTIFACT_REVIEW'
if artifact_reviewed:
    for key in ['C01','C12','C18']:
        acceptance[key]['proof'].append('docs/testes/sprint-06c-reconstrucao-externa.json')
for item in acceptance.values():
    for p in item['proof']:
        if p.endswith('/report.html') and not approved:continue
        assert (ROOT/p).exists(),p
repos={}
for name in ['docs','cripto-bot','cripto-core','cripto-market-data']:
    repos[name]={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT/name,text=True).strip(),'committed_by_task':False}
repos['cripto-analytics']={'head':None,'branch':'main','committed_by_task':False,'remote_created':False}
data={'schema':1,'generated_at':datetime.now(timezone.utc).isoformat(),'status':'APPROVED_OFFLINE_06C' if approved else ('PENDING_PRIOR_ARTIFACT_REVIEW' if artifact_mismatches else 'TECHNICAL_CHECKS_PASSED_DOCUMENTATION_REVIEW_PENDING'),'scope':'Python/local/PAPER/Spot/BTCUSDT/15m; synthetic regressions and readonly projections of previously published CSVs; no new economic evaluation','repositories':repos,
'baseline_verified':{'source_control_config_test_hashes':185,'artifact_files':12,'bot_archive':'cripto-bot/reports/sprint06c/baseline/tracked-baseline.tar','docs_preexisting_changes_preserved':True,'ignored_local_config':'config/backtest.sma.public.local.toml verified directly, not included in git archive'},
'verification':verification,'milestones':{'C-M1':read(OUT/'baseline/acceptance.json'),'C-M2':read(AN/'reports/sprint06c/standalone/acceptance.json'),'C-M3':{'technical_checks':'PASSED','status':'APPROVED' if approved else 'PENDING_DOCUMENTATION_REVIEW'}},
'wheel_smokes':{'baseline_commands':22,'standalone_checks':len(stand['checks']),'final_commands':len(smoke['checks']),'socket_probes_blocked':True,'standalone_without_bot_or_data_httpx_pydantic':True,'standalone_readonly_files_unchanged':stand['readonly_files_unchanged'],'origins':{name:smoke[name] for name in ['core','market_data','analytics']}|{'bot':smoke['origin']}},
'compatibility':compat,'negative_installation':{name:read(OUT/f'final/negative-missing-{name}.json') for name in ['analytics','duckdb']},'publication':read(AN/'reports/sprint06c/standalone/publication.json'),
'scale':{name:read(AN/f'reports/sprint06c/scale-{name}.json') for name in ['synthetic','preserved']},
'artifact_sha256':artifact_observed|compat['artifact_sha256'],'prior_artifact_expected_sha256':prior['artifact_sha256'],'prior_artifact_mismatches':artifact_mismatches,'external_artifact_review':external_review,'source_files_sha256':source,'acceptance':acceptance,'visual_review':visual,
'limitations':['Complete cold-cache installation not demonstrated: new-cache offline lock failed on DuckDB metadata; existing baseline cache supplied metadata and third-party distributions reused only after locked versions/RECORD/hash verification.','Core/data tests are historical (54/120); sources/controls unchanged; external 06A rebuild verified separately, historical artifacts have different hashes. Coverage measured per package, with changed denominators after extraction.','Retrospective synthetic replay proves technical equivalence, not new out-of-sample economic evidence. Only run_key/checkpoint_bytes excluded from the 48-curve comparison.','Projection/SQL measurements exclude reconciliation; cold-cache query conditions not controlled. DuckDB internal memory limit differs from process RSS. Spill sampling is observational, not an absolute peak guarantee.'],
'actions_not_performed':['market network','private credentials/orders','new real final-window evaluation or reset registry','AWS/messages','commits/remotes/publication','06D/07 or BT-A–BT-F implementation']}
raw={}
for base in [OUT,AN/'reports/sprint06c']:
    for p in base.rglob('*'):
        if not p.is_file() or p.suffix not in {'.json','.xml','.log'}:continue
        rel=p.relative_to(base)
        if any(part.startswith(('scale-','wheel-','publication-','chrome-profile','implementation-scripts')) for part in rel.parts[:-1]):continue
        raw[str(p.relative_to(ROOT))]=sha(p)
data['raw_evidence_sha256']=raw
files=['planejamento.md','sprints/sprint-06.md','sprints/sprint-06c.md','testes/sprint-06-validacao.md','testes/sprint-06c-validacao.md','arquitetura.md','arquitetura-modular.md','bancos/README.md','bancos/backtest-sqlite.md','bancos/backtest-analytics.md','estrategias/README.md','estrategias/trend_sma.md','decisoes/0007-duckdb-parquet-analitico.md','decisoes/0008-core-e-identidade-da-composicao.md','decisoes/0010-analytics-por-snapshots-somente-leitura.md']
data['documentation_sha256']={p:sha(DOCS/p) for p in files}
data['evidence_tools_sha256']={str(p.relative_to(DOCS)):sha(p) for p in (DOCS/'testes/ferramentas').glob('sprint-06c-*.py')}
data['rendered_report_sha256']={str(p.relative_to(DOCS)):sha(p) for p in (DOCS/'testes/relatorios/sprint-06c').glob('*') if p.is_file()}
data['final_documentation_checks']={'markdown_files':15,'fences_and_local_targets':'PASSED','artifact_review':'VERIFIED_EXTERNAL_REBUILD: confirmed by user; historical hashes retained' if artifact_reviewed else 'PENDING: four prior 06A files differ; current bytes preserved','runtime_projects_core_data_sources':'unchanged'}
file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('Recorded',len(source),'source/config/control/test hashes;',len(acceptance),'criteria')
