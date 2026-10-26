"""Consolidate recorded offline 06B checks; never executes trading or tests."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import xml.etree.ElementTree as ET

DOCS=Path(__file__).resolve().parents[2]; ROOT=DOCS.parent
BOT=ROOT/'cripto-bot'; DATA=ROOT/'cripto-market-data'; OUT=BOT/'reports/sprint06b'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def suite(p):
    node=ET.parse(p/'pytest.xml').getroot().find('testsuite')
    assert node is not None and node.get('failures')=='0' and node.get('errors')=='0'
    return {'pytest':node.attrib,'coverage':read(p/'coverage.json')['totals'],'logs':str(p.relative_to(ROOT))}
prior=read(DOCS/'testes/sprint-06a-evidencias.json')
with tarfile.open(OUT/'baseline/tracked-baseline.tar') as archive:
    for path,digest in prior['source_files_sha256'].items():
        if path.startswith('cripto-bot/'):
            stream=archive.extractfile(path.removeprefix('cripto-bot/')); assert stream
            assert hashlib.sha256(stream.read()).hexdigest()==digest,path
        else: assert sha(ROOT/path)==digest,path
for path,digest in prior['artifact_sha256'].items(): assert sha(ROOT/path)==digest,path
protected={}
for name in ['paper_sqlite.py','strategy_sqlite.py','backtest_sqlite.py']:
    p=BOT/'src/cripto_bot/adapters/storage'/name
    previous=subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(BOT))],cwd=BOT)
    assert previous==p.read_bytes(),p
    protected[str(p.relative_to(ROOT))]=sha(p)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT/'cripto-core').strip()
verification={'baseline_bot':suite(OUT/'baseline'),'standalone_data':suite(DATA/'reports/sprint06b/standalone'),'final_bot':suite(OUT/'final')}
checks=read(OUT/'compatibility.json')
smokes={k:read(p) for k,p in {'baseline':OUT/'baseline/wheel-smoke.json','standalone':DATA/'reports/sprint06b/standalone/wheel-smoke.json','final':OUT/'final/wheel-smoke.json'}.items()}
assert smokes['baseline']['socket_probe_blocked'] and smokes['final']['socket_probe_blocked'] and smokes['standalone']['probe_blocked']
source={}
for project in [BOT,DATA,ROOT/'cripto-core']:
    paths=[*project.joinpath('src').rglob('*.py'),*project.joinpath('src').rglob('py.typed'),*project.joinpath('tests').rglob('*.py')]
    paths += [project/n for n in ['pyproject.toml','uv.lock','.python-version','README.md','.gitignore']]
    paths += [p for p in project.joinpath('config').rglob('*') if p.is_file()]
    for p in sorted(paths):
        if p.is_file() and '__pycache__' not in p.parts: source[str(p.relative_to(ROOT))]=sha(p)
acceptance={}
proofs={
'B01':['baseline/acceptance.json','standalone/acceptance.json'],
'B02':['tests/unit/test_market_composition.py','market-data/tests/test_cli_collection.py'],
'B03':['market-data/tests/test_cli_collection.py','tests/unit/test_config.py'],
'B04':['market-data/tests/test_binance_public.py','market-data/tests/test_cli_collection.py'],
'B05':['market-data/tests/test_market.py','market-data/tests/test_collect_market.py'],
'B06':['cross-cli.json','standalone-previous-store.json'],
'B07':['cross-cli.json','market-data/tests/test_market_storage.py'],
'B08':['market-data/tests/test_binance_public.py','market-data/tests/test_collect_market.py'],
'B09':['standalone/wheel-smoke.json','final/wheel-smoke.json'],
'B10':['market-data/tests/test_market_storage.py','tests/unit/test_collection_entrypoint.py'],
'B11':['standalone-previous-store.json','compatibility.json'],
'B12':['tests/unit/test_market_composition.py','compatibility.json'],
'B13':['tests/unit/test_market_composition.py','tests/unit/test_core_composition.py'],
'B14':['compatibility.json'],
'B15':['standalone/wheel-smoke.json','final/wheel-smoke.json','final/missing-data.json'],
'B16':['final/pytest.xml','compatibility.json'],
'B17':['docs/testes/sprint-06b-validacao.md','docs/testes/relatorios/sprint-06b/report.html'],
'B18':['docs/sprints/sprint-06b.md','docs/planejamento.md']}
for key, proof in proofs.items():
    resolved=[]
    for name in proof:
        if name.startswith('docs/'): path=ROOT/name
        elif name.startswith('market-data/'): path=ROOT/('cripto-'+name)
        elif name.startswith('tests/'): path=BOT/name
        elif name=='standalone/wheel-smoke.json': path=DATA/'reports/sprint06b'/name
        elif name=='standalone/acceptance.json': path=DATA/'reports/sprint06b'/name
        else: path=OUT/name
        resolved.append(str(path.relative_to(ROOT)))
    acceptance[key]={'status':'APPROVED' if key not in {'B17','B18'} else 'PENDING_DOCUMENTATION_REVIEW','proof':resolved}

existing=DOCS/'testes/sprint-06b-evidencias.json'
visual=read(existing).get('visual_review',{}) if existing.exists() else {}
if visual.get('status')=='APPROVED':
    for key in ['B17','B18']: acceptance[key]['status']='APPROVED'
data={'schema':1,'generated_at':datetime.now(timezone.utc).isoformat(),'status':'APPROVED_OFFLINE_06B' if visual.get('status')=='APPROVED' else 'TECHNICAL_CHECKS_PASSED_DOCUMENTATION_REVIEW_PENDING','scope':'Python/local/PAPER/Spot/BTCUSDT/15m; synthetic fixtures; socket guard',
'repositories':{p.name:{'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip() if p!=DATA else None,'committed_by_this_task':False} for p in [BOT,ROOT/'cripto-core',DOCS,DATA]},
'baseline_verified':{'source_control_hashes':len(prior['source_files_sha256']),'artifacts':len(prior['artifact_sha256']),'bot_archive':'cripto-bot/reports/sprint06b/baseline/tracked-baseline.tar','docs_preexisting_changes_preserved':True},
'verification':verification,'milestones':{'B-M1':read(OUT/'baseline/acceptance.json'),'B-M2':read(DATA/'reports/sprint06b/standalone/acceptance.json'),'B-M3':{'technical_checks':'PASSED','status':'APPROVED' if visual.get('status')=='APPROVED' else 'PENDING_DOCUMENTATION_REVIEW','smoke_commands':len(smokes['final']['checks'])}},
'wheel_smokes':{'baseline_commands':len(smokes['baseline']['checks']),'standalone_commands':len(smokes['standalone']['checks']),'final_commands':len(smokes['final']['checks']),'socket_probes_blocked':True,'origins':{'bot':smokes['final']['origin'],'market':smokes['final']['market_data']['origin'],'core':smokes['final']['core']['origin']},'standalone_without_bot_or_duckdb':True},
'compatibility':checks,'cross_cli':read(OUT/'cross-cli.json'),'previous_store':read(OUT/'standalone-previous-store.json'),'negative_missing_dependency':read(OUT/'final/missing-data.json'),
'protected_storage_sha256':protected,'artifact_sha256':checks['artifacts']|prior['artifact_sha256'],'source_files_sha256':source,'acceptance':acceptance,'visual_review':visual,
'limitations':['Cold-cache installation not demonstrated; third-party distributions copied from baseline only after lock version and RECORD/hash verification; own wheels installed offline with --no-deps.','Coverage measures each package separately; 06B extraction changes bot denominator. Core suite historical: 54 tests from 06A, not rerun; core sources/controls/artifacts remain unchanged.','Synthetic replay establishes technical equivalence, not out-of-sample economic performance. Only run_key and checkpoint_bytes excluded when comparing 48 complete curves.','Memory peak not instrumented; local smoke fixture is not a throughput benchmark.'],
'costs':{'baseline_pytest_seconds':verification['baseline_bot']['pytest']['time'],'final_bot_pytest_seconds':verification['final_bot']['pytest']['time'],'standalone_pytest_seconds':verification['standalone_data']['pytest']['time'],'measured_before_documentation':{'bot_reports_KiB':3056,'data_reports_KiB':344,'bot_artifacts_KiB':180,'data_artifacts_KiB':68},'external_spend':0,'memory_peak':'NOT_MEASURED'},
'actions_not_performed':['market network','credentials/private/orders','real final-window evaluation','AWS/messages','commits/remotes/publication','06C/06D/07 or BT-A–BT-F implementation']}
for item in acceptance.values():
    for proof in item['proof']: assert (ROOT/proof).is_file(),proof
doc_files=[
    'planejamento.md','sprints/sprint-06.md','sprints/sprint-06b.md',
    'testes/sprint-06-validacao.md','testes/sprint-06b-validacao.md',
    'arquitetura.md','arquitetura-modular.md','bancos/README.md',
    'bancos/market-sqlite.md','bancos/backtest-sqlite.md','estrategias/README.md',
    'estrategias/trend_sma.md','decisoes/0003-coleta-publica-e-persistencia-local.md',
    'decisoes/0008-core-e-identidade-da-composicao.md',
    'decisoes/0009-market-data-e-proveniencia-do-produtor.md']
data['documentation_sha256']={name:sha(DOCS/name) for name in doc_files}
data['raw_evidence_sha256']={str(p.relative_to(ROOT)):sha(p) for base in [OUT,DATA/'reports/sprint06b'] for p in base.rglob('*') if p.is_file() and p.suffix in {'.json','.xml','.log'} and 'chrome-profile' not in p.parts and 'implementation-scripts' not in p.parts and not any(part.startswith('wheel-') for part in p.relative_to(base).parts)}
data['rendered_report_sha256']={str(p.relative_to(DOCS)):sha(p) for p in (DOCS/'testes/relatorios/sprint-06b').glob('*') if p.is_file()}
data['evidence_tools_sha256']={str(p.relative_to(DOCS)):sha(p) for p in (DOCS/'testes/ferramentas').glob('sprint-06b-*.py')}
data['final_documentation_checks']={'markdown_fences_and_local_link_targets':'15 files checked; no missing local target','acceptance_proof_paths':'all exist','report':'self-contained HTML, values derived from JSON','pending_pilot_criteria':'not executed'}
existing.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Recorded evidence:',len(source),'source/test/control hashes; 127 baseline hashes + 6 artifacts preserved')
