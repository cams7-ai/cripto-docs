"""Measure projection and queries from synthetic rows or an already published export."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import resource
import statistics
import sys
import tempfile
import threading
import time

from cripto_analytics.adapters import duckdb_export
from cripto_analytics.application.publish import file_hash, publish_backtest
from cripto_analytics.presentation.backtest import document
from cripto_core.serialization import fingerprint

ROOT=Path('/home/cams7/Dev/Cripto');PROJECT=ROOT/'cripto-analytics'
parent=PROJECT/'reports/sprint06c';parent.mkdir(exist_ok=True)
scratch=Path(tempfile.mkdtemp(prefix='scale-',dir=parent))
segments=('development','validation','test')
mode=sys.argv[1]
if mode=='synthetic':
    source=(PROJECT/'tests/test_contracts.py').read_text();tree=ast.parse(source)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='report')
    scope={'SEGMENTS':segments,'fingerprint':fingerprint};exec(ast.get_source_segment(source,node),scope)
    report=scope['report']();total=150_000
    class Rows:
        def counts(self,table):return {'run':total} if table=='decisions' else {}
        def iter_rows(self,table):
            if table!='decisions':return
            for index in range(total):
                digest=hashlib.sha256(str(index).encode()).hexdigest()
                yield {'run_key':'run','decision_id':digest,'as_of':'2026-10-25T00:00:00+00:00','target':'HOLD','reason':'NO_CROSS','status':'HOLD','prefix_sha256':digest,'data_json':json.dumps({'id':index,'payload':digest*20})}
    rows=Rows();report['curves'][0]['metrics']['decisions']=total
    report['result_sha256']=fingerprint({k:v for k,v in report.items() if k!='result_sha256'})
    preserved=None
else:
    preserved=ROOT/'cripto-bot/data/backtest-btc-audit-v1/exports/97f4c02a-872f-4640-baf9-2645ad73cade'
    manifest=json.loads((preserved/'manifest.json').read_text())
    checked={name:file_hash(preserved/name) for name in ['report.json','equity.csv','trades.csv','decisions.csv']}
    assert all(manifest['files'][name]==digest for name,digest in checked.items())
    report=json.loads((preserved/'report.json').read_text())
    counts={}
    import duckdb
    with duckdb.connect(str(preserved/'analytics.duckdb'),read_only=True) as db:
        records=db.execute('SELECT run_key,equity_rows,fills,decisions FROM curve_summary').fetchall()
    for name,index in [('equity',1),('trades',2),('decisions',3)]:counts[name]={str(r[0]):int(r[index]) for r in records if r[index]}
    class Rows:
        def counts(self,table):return counts[table]
        def iter_rows(self,table):
            with (preserved/f'{table}.csv').open(newline='') as stream:
                yield from csv.DictReader(stream)
    rows=Rows()
phase={};state={'stop':False,'peak_spill_bytes':0}
def watch():
    while not state['stop']:
        size=sum(p.stat().st_size for p in scratch.rglob('*') if p.is_file() and '.duckdb-tmp' in p.parts)
        state['peak_spill_bytes']=max(size,state['peak_spill_bytes']);time.sleep(.02)
thread=threading.Thread(target=watch,daemon=True);thread.start()
def renderer(body):
    start=time.perf_counter();result=document(body,segments=segments);phase['render_seconds']=time.perf_counter()-start;phase['csv_started']=time.perf_counter();return result
def parquet(db,directory,name):
    start=time.perf_counter();result=duckdb_export._parquet(db,directory,name);phase[name+'_parquet_seconds']=time.perf_counter()-start;return result
def exporter(port,body,directory):
    phase['csv_seconds']=time.perf_counter()-phase.pop('csv_started');start=time.perf_counter();result=duckdb_export.export_analytics(port,body,directory,parquet_writer=parquet);phase['analytics_seconds']=time.perf_counter()-start;return result
start=time.perf_counter()
try:manifest=publish_backtest(report,rows,scratch,'measured',segments=segments,renderer=renderer,analytics_exporter=exporter)
finally:state['stop']=True;thread.join()
phase['publish_seconds']=time.perf_counter()-start
folder=manifest.parent
queries={}
with __import__('duckdb').connect(':memory:',config={'threads':'1','memory_limit':'256MB','autoinstall_known_extensions':'false','autoload_known_extensions':'false','temp_directory':''}) as db:
    db.execute('SET allowed_directories = ?',[[str(folder.resolve())]])
    db.execute('SET enable_external_access=false');db.execute('SET lock_configuration=true')
    for name,columns in duckdb_export.COLUMNS.items():
        readings={};answers=[]
        for ext in ['csv','parquet']:
            times=[]
            for iteration in range(3):
                start=time.perf_counter()
                if ext=='csv':
                    definitions=','.join(f"'{column}':'VARCHAR'" for column in columns)
                    result=db.execute(f"SELECT run_key,count(*) FROM read_csv(?,header=true,columns={{{definitions}}},nullstr='') GROUP BY run_key ORDER BY run_key",[str(folder/f'{name}.csv')]).fetchall()
                else:result=db.execute('SELECT run_key,count(*) FROM read_parquet(?) GROUP BY run_key ORDER BY run_key',[str(folder/f'{name}.parquet')]).fetchall()
                times.append(time.perf_counter()-start)
            answers.append(result);readings[ext]={'median_seconds':statistics.median(times),'repeats':3,'bytes':(folder/f'{name}.{ext}').stat().st_size}
        assert answers[0]==answers[1]
        queries[name]=readings
if preserved:assert checked=={name:file_hash(preserved/name) for name in checked}
result={'mode':mode,'manifest':str(manifest),'reconciliation':'NOT_RUN: consumes existing reconciled snapshot/port; timing excludes reconciliation','phases':phase,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'peak_spill_bytes_observed':state['peak_spill_bytes'],'sampling_seconds':.02,'rows':{name:sum(rows.counts(name).values()) for name in duckdb_export.COLUMNS},'queries':queries,'query_order':'CSV then Parquet, 3 repeats each; cold cache not controlled','published_bytes':sum(p.stat().st_size for p in folder.iterdir()),'source_export_unchanged':bool(preserved),'no_ledger_opened':True}
(parent/f'scale-{mode}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
