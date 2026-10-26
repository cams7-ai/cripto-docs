"""Installed-library publication concurrency and real process death, without a ledger."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT=Path('/home/cams7/Dev/Cripto');PROJECT=ROOT/'cripto-analytics'
python=PROJECT/'.venv-standalone-06c/bin/python';runner=PROJECT/'tests/offline_runner.py'
scratch=Path(tempfile.mkdtemp(prefix='publication-',dir=PROJECT/'reports/sprint06c/standalone'))
source=(PROJECT/'tests/test_contracts.py').read_text();tree=ast.parse(source)
parts=[ast.get_source_segment(source,n) for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in {'Rows','report'}]
base="from pathlib import Path\nimport os,sys,json\nfrom cripto_core.serialization import fingerprint\nfrom cripto_analytics.application.publish import publish_backtest\nSEGMENTS=('development','validation','test')\n"+'\n'.join(parts)+'\n'
def command(code):return [str(python),'-I',str(runner),'--code',base+code]
logs=[]
for stage in ['before','after']:
    data=scratch/stage;data.mkdir()
    code=f'''
original=Path.rename
def rename(self,target):
    if {stage!r}=='before':os._exit(73)
    original(self,target)
    os._exit(73)
Path.rename=rename
publish_backtest(report(),Rows(),Path({str(data)!r}),'death',segments=SEGMENTS)
'''
    p=subprocess.run(command(code),capture_output=True,text=True);assert p.returncode==73,p.stderr
    target=data/'exports/death';assert target.exists()==(stage=='after')
    p=subprocess.run(command(f"publish_backtest(report(),Rows(),Path({str(data)!r}),'retry',segments=SEGMENTS)"),capture_output=True,text=True);assert p.returncode==0,p.stderr
    if target.exists():
        m=json.loads((target/'manifest.json').read_text())
        for file,digest in m['files'].items():assert hashlib.sha256((target/file).read_bytes()).hexdigest()==digest
    logs.append({'stage':stage,'death_exit':73,'target_published':target.exists(),'retry_exit':p.returncode})
data=scratch/'concurrent';data.mkdir()
code=f'''
try:
    publish_backtest(report(),Rows(),Path({str(data)!r}),'same-id',segments=SEGMENTS)
except OSError:
    sys.exit(3)
'''
processes=[subprocess.Popen(command(code),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for _ in range(2)]
results=[]
for p in processes:
    out,err=p.communicate(timeout=30);results.append({'exit':p.returncode,'stderr':err})
assert sorted(r['exit'] for r in results)==[0,3],results
m=json.loads((data/'exports/same-id/manifest.json').read_text())
for file,digest in m['files'].items():assert hashlib.sha256((data/'exports/same-id'/file).read_bytes()).hexdigest()==digest
assert not list((data/'exports').glob('.pending-*'))
(PROJECT/'reports/sprint06c/standalone/publication.json').write_text(json.dumps({'death':logs,'concurrent':results,'manifest_hashes_valid':True},indent=2)+'\n')
print('2 real process deaths and concurrent collision passed')
