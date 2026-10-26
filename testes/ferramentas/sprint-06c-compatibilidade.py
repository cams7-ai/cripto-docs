"""Compare preserved synthetic baseline and installed 06C composition, offline."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import tomllib
import zipfile

ROOT=Path('/home/cams7/Dev/Cripto');BOT=ROOT/'cripto-bot';OUT=BOT/'reports/sprint06c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def previous(path):return subprocess.check_output(['git','show',f'HEAD:{path}'],cwd=BOT)
a=load(OUT/'baseline/wheel-smoke.json');b=load(OUT/'final/wheel-smoke.json')
def report(d):return Path(next(x['result']['manifest'] for x in d['checks'] if x['command']=='backtest-report'))
def curves(d):
    rows=load(report(d).parent/'report.json')['curves']
    return sorted([{k:v for k,v in c.items() if k not in {'run_key','checkpoint_bytes'}} for c in rows],key=lambda c:(c['segment'],c['variant'],c['profile']))
assert curves(a)==curves(b)
financial=[]
for x,y in zip(a['checks'],b['checks'],strict=True):
    assert x['command']==y['command'] and x['exit_code']==y['exit_code']
    if 'financial_sha256' in x['result']:
        assert x['result']['financial_sha256']==y['result']['financial_sha256']
        financial.append(x['command'])
old={p['name']:p['version'] for p in tomllib.loads(previous('uv.lock').decode())['package']}
new={p['name']:p['version'] for p in tomllib.loads((BOT/'uv.lock').read_text())['package']}
assert all(new[k]==v for k,v in old.items()) and set(new)-set(old)=={'cripto-analytics'}
protected={}
for f in ['paper_sqlite.py','strategy_sqlite.py','backtest_sqlite.py']:
    p=BOT/'src/cripto_bot/adapters/storage'/f
    assert p.read_bytes()==previous(str(p.relative_to(BOT)))
    protected[str(p.relative_to(ROOT))]=sha(p)
unchanged_functions=[]
for name,functions in [('paper_report.py',{'summary','diagnostic'}),('strategy_report.py',{'summary','diagnostic'}),('backtest_report.py',{'snapshot','_series'})]:
    path='src/cripto_bot/adapters/storage/'+name
    def bodies(src):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name in functions}
    assert bodies(previous(path))==bodies((BOT/path).read_text())
    unchanged_functions.extend(name+':'+n for n in functions)
artifacts={}
for project in ['cripto-bot','cripto-analytics']:
    for p in (ROOT/project/'dist/06c-final').iterdir():
        if not p.name.endswith(('.whl','.tar.gz')):continue
        artifacts[str(p.relative_to(ROOT))]=sha(p)
        if p.suffix=='.whl':
            with zipfile.ZipFile(p) as z:
                for f in (ROOT/project/'src').rglob('*.py'):assert z.read(str(f.relative_to(ROOT/project/'src')))==f.read_bytes()
                meta=z.read(next(n for n in z.namelist() if n.endswith('/METADATA'))).decode()
                assert 'file://' not in meta and '@ /home/' not in meta
registry=BOT/'data/backtest-usage/test-usage.sqlite3';registry_sha='af7ee92659cb1be9c4e322daeba997755430a040faec4b1342c1cabf082810bd';assert sha(registry)==registry_sha
m=report(a);scratch=m.parents[3];db=m.parents[2]/'backtest.sqlite3';before=sha(db)
python=BOT/'.venv-wheel-06c/bin/python';runner=BOT/'tests/offline_runner.py'
def run(args):
    p=subprocess.run([str(python),'-I',str(runner),*args],cwd=BOT,text=True,capture_output=True)
    return {'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
old_report=run([str(python.parent/'cripto-bot'),'backtest-report','--config',str(scratch/'backtest.toml')]);assert old_report['exit']==0,old_report
result=json.loads(old_report['stdout']);new_manifest=Path(result['manifest'])
assert result['result_sha256']==load(m)['result_sha256'] and sha(db)==before
same_files=[]
for name in ['report.json','report.html','equity.csv','trades.csv','decisions.csv','analytics.json']:
    assert (m.parent/name).read_bytes()==(new_manifest.parent/name).read_bytes(),name
    same_files.append(name)
# Compare complete typed columnar rows, in export order, under the same sealed identity.
code=f'''
import json,duckdb
from pathlib import Path
from cripto_analytics.adapters.reader import validate_export,query_export
from cripto_bot.adapters.provenance import runtime_identity
old=Path({str(m.parent)!r});new=Path({str(new_manifest.parent)!r})
with duckdb.connect(':memory:') as db:
    db.execute("SET autoinstall_known_extensions=false");db.execute("SET autoload_known_extensions=false")
    for name in ('equity','trades','decisions'):
        for offset in [0]:
            a=db.execute('SELECT * FROM read_parquet(?) ORDER BY export_row',[str(old/(name+'.parquet'))]).fetchall()
            b=db.execute('SELECT * FROM read_parquet(?) ORDER BY export_row',[str(new/(name+'.parquet'))]).fetchall()
            assert a==b,name
valid=validate_export(Path({str(BOT)!r}),new/'manifest.json')
answers={{view:query_export(valid,view,1000) for view in ('curve-summary','decisions-counts','trades-counts')}}
print(json.dumps({{'typed_parquet_rows_equal':True,'queries':answers,'identity':runtime_identity(Path({str(BOT)!r}))}}))
'''
checked=run(['--code',code]);assert checked['exit']==0,checked
proof=json.loads(checked['stdout'])
resume=run([str(python.parent/'cripto-bot'),'backtest-run','--config',str(scratch/'backtest.toml'),'--segment','development'])
assert resume['exit']==3 and 'FROZEN_PROTOCOL_CHANGED' in resume['stdout']+resume['stderr']
assert sha(db)==before and sha(registry)==registry_sha
result={'curves_equal':48,'excluded_curve_fields':['run_key','checkpoint_bytes'],'financial_commands_equal':financial,'lock_prior_versions_preserved':len(old),'only_added_dependency':'cripto-analytics==0.1.0','duckdb_transitive_version':new['duckdb'],'protected_storage_sha256':protected,'financial_snapshot_functions_ast_unchanged':unchanged_functions,'source_matches_wheels':True,'artifact_sha256':artifacts,'old_report':old_report,'old_resume':resume,'old_sqlite_sha256':before,'old_sqlite_unchanged':True,'registry_sha256':sha(registry),'old_export_exact_files':same_files,'installed_proof':proof}
(OUT/'compatibility.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('48 curves, 8 financial responses, 6 exact files, typed Parquet and sealed readonly report passed')
