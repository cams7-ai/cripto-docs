"""Prove shared lock/replay across installed CLIs on the preserved synthetic store."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path('/home/cams7/Dev/Cripto'); BOT=ROOT/'cripto-bot'; DATA=ROOT/'cripto-market-data'
OUT=BOT/'reports/sprint06b'
sys.path.insert(0,str(BOT/'.venv-wheel-06b/lib/python3.13/site-packages'))
from cripto_market_data.adapters.storage.sqlite import SQLiteMarketStore
baseline=json.loads((OUT/'baseline/wheel-smoke.json').read_text())
item=next(x['result'] for x in baseline['checks'] if x['command']=='collect-market')
scratch=Path(item['manifest']).parents[3]; config=scratch/'fixture.toml'
env={k:v for k,v in os.environ.items() if not k.startswith('CRIPTO_BOT_') and k not in {'PYTHONPATH','BINANCE_API_KEY','BINANCE_API_SECRET'}}
checks=[]
def invoke(producer,expected):
    python=(BOT/'.venv-wheel-06b/bin/python') if producer=='cripto-bot' else DATA/'.venv-standalone-06b/bin/python'
    command=[str(python),'-I',str(BOT/'tests/offline_runner.py'),str(python.parent/producer),'collect-market','--config',str(config),'--start','2026-10-01T00:00:00Z','--end','2026-10-01T00:30:00Z']
    if producer!='cripto-bot': command.extend(['--root',str(BOT)])
    p=subprocess.run(command,cwd=BOT,env=env,capture_output=True,text=True)
    assert p.returncode==expected,p.stdout+p.stderr
    record={'producer':producer,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    if expected==0:
        r=json.loads(p.stdout); m=json.loads(Path(r['manifest']).read_text())
        assert r['inserted']==0 and r['dataset']==item['dataset']
        assert m['data_sha256']=='fec39ffcbf53d685fcd5606a51585e364c6dbecd06b991d0dabc4722e04aa74d'
        assert len(m['files'])==4
        for f,digest in m['files'].items(): assert hashlib.sha256((Path(r['manifest']).parent/f).read_bytes()).hexdigest()==digest
    else: assert 'WRITER_BUSY' in p.stdout+p.stderr
    checks.append(record)
for producer in ['cripto-bot','cripto-market-data','cripto-bot']: invoke(producer,0)
with SQLiteMarketStore(scratch/'data'):
    for producer in ['cripto-bot','cripto-market-data']: invoke(producer,3)
(OUT/'cross-cli.json').write_text(json.dumps({'checks':checks,'replay_inserted':0,'same_dataset_hash':True,'same_lock':True},indent=2)+'\n')
print('3 alternating replays; 2 cross-CLI writer exclusions passed')
