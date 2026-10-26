"""Offline evidence: compare preserved baseline against installed 06B wheels."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import tomllib
import zipfile

ROOT = Path('/home/cams7/Dev/Cripto')
BOT = ROOT / 'cripto-bot'
DATA = ROOT / 'cripto-market-data'
OUT = BOT / 'reports/sprint06b'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def old(path):
    return subprocess.check_output(['git','show',f'HEAD:{path}'],cwd=BOT)
a=json.loads((OUT/'baseline/wheel-smoke.json').read_text())
b=json.loads((OUT/'final/wheel-smoke.json').read_text())
def report(d):
    return Path(next(x['result']['manifest'] for x in d['checks'] if x['command']=='backtest-report'))
def curves(d):
    items=json.loads((report(d).parent/'report.json').read_text())['curves']
    return sorted([{k:v for k,v in c.items() if k not in {'run_key','checkpoint_bytes'}} for c in items],key=lambda c:(c['segment'],c['variant'],c['profile']))
assert curves(a)==curves(b)
financial=[]
for x,y in zip(a['checks'],b['checks'],strict=True):
    assert x['command']==y['command'] and x['exit_code']==y['exit_code']
    if 'financial_sha256' in x['result']:
        assert x['result']['financial_sha256']==y['result']['financial_sha256']
        financial.append(x['command'])
prior={p['name']:p['version'] for p in tomllib.loads(old('uv.lock').decode())['package']}
current={p['name']:p['version'] for p in tomllib.loads((BOT/'uv.lock').read_text())['package']}
assert all(current[k]==v for k,v in prior.items())
assert set(current)-set(prior)=={'cripto-market-data'}
old_ast=ast.parse(old('src/cripto_bot/adapters/storage/market_sqlite.py'))
new_ast=ast.parse((DATA/'src/cripto_market_data/adapters/storage/sqlite.py').read_text())
def bodies(tree):
    return [ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,ast.ClassDef) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DDL' for t in n.targets)]
assert bodies(old_ast)==bodies(new_ast)
artifacts={}
for project in [BOT,DATA]:
    for p in sorted((project/'dist/06b-final').iterdir()):
        artifacts[str(p.relative_to(ROOT))]=sha(p)
        if p.suffix=='.whl':
            with zipfile.ZipFile(p) as z:
                if project == DATA:
                    assert any(n.endswith('/py.typed') for n in z.namelist())
                meta=z.read(next(n for n in z.namelist() if n.endswith('/METADATA'))).decode()
                assert 'file://' not in meta and '@ /home/' not in meta
                for f in (project/'src').rglob('*'):
                    if f.is_file() and f.suffix in {'.py','.typed'}:
                        assert z.read(str(f.relative_to(project/'src')))==f.read_bytes()
registry=BOT/'data/backtest-usage/test-usage.sqlite3'
assert sha(registry)=='af7ee92659cb1be9c4e322daeba997755430a040faec4b1342c1cabf082810bd'
python=BOT/'.venv-wheel-06b/bin/python'
runner=BOT/'tests/offline_runner.py'
cli=python.parent/'cripto-bot'
m=report(a); scratch=m.parents[3]; db=m.parents[2]/'backtest.sqlite3'; before=sha(db)
def run(command):
    p=subprocess.run([str(python),'-I',str(runner),str(cli),command,'--config',str(scratch/'backtest.toml'),*(['--segment','development'] if command=='backtest-run' else [])],cwd=BOT,capture_output=True,text=True)
    return {'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
r=run('backtest-report'); assert r['exit_code']==0,r
parsed=json.loads(r['stdout']); assert parsed['result_sha256']==next(c['result']['result_sha256'] for c in a['checks'] if c['command']=='backtest-report')
assert sha(db)==before
rejected=run('backtest-run'); assert rejected['exit_code']==3,rejected
assert 'FROZEN_PROTOCOL_CHANGED' in rejected['stdout']+rejected['stderr']
assert sha(db)==before and sha(registry)=='af7ee92659cb1be9c4e322daeba997755430a040faec4b1342c1cabf082810bd'
result={'financial_commands_equal':financial,'curves_equal':48,'excluded_curve_fields':['run_key','checkpoint_bytes'],'prior_lock_packages_preserved':len(prior),'only_added_dependency':'cripto-market-data==0.1.0','ddl_class_ast_identical':True,'source_matches_wheels':True,'artifacts':artifacts,'registry_sha256':sha(registry),'old_report':r,'old_resume_rejected':rejected,'old_sqlite_unchanged':True}
(OUT/'compatibility.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in {'old_report','old_resume_rejected','artifacts'}}))
