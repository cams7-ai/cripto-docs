"""Installed financial/queue drills with fake observations and fake sender; no network."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path("/home/cams7/Dev/Cripto")
BOT = ROOT / "cripto-bot"
OUT = BOT / "reports/sprint06d/offline"
PYTHON = BOT / ".venv-wheel-06d/bin/python"
RUNNER = BOT / "tests/offline_runner.py"
scratch = Path(tempfile.mkdtemp(prefix="oracle-", dir=OUT))
for name in ["pyproject.toml", "uv.lock", ".python-version"]:
    shutil.copyfile(BOT / name, scratch / name)
base = 1790812800000
step = 900000
rules = json.loads((BOT / "config/fixtures/paper-roundtrip.json").read_text())["rules"]
capture = scratch / "capture.json"
capture.write_text('{"synthetic":true}')
body = (
    (BOT / "config/continuous.example.toml")
    .read_text()
    .replace(
        'source = "binance_public"', f'source = "fixture"\nfixture_file = "{capture}"'
    )
    .replace('slippage_bps = "5"', 'slippage_bps = "0"')
)
body = body.replace("enabled = false", "enabled = true", 1).replace(
    '[modules.trend_btc]\nmodule_id = "trend_sma"\nenabled = false',
    '[modules.trend_btc]\nmodule_id = "trend_sma"\nenabled = true',
)
body = body.replace(
    "[continuous.notifications]\nenabled = false",
    '[continuous.notifications]\nenabled = true\nmail_sender_url = "http://127.0.0.1:8002"\nmail_to = "test@example.invalid"',
)
for old, new in [
    ("data/continuous-demo", "financial"),
    ("data/continuous-market", "market"),
    ("data/continuous-delivery", "delivery"),
]:
    body = body.replace(old, str(scratch / new))
config = scratch / "drill.toml"
config.write_text(body)
env = {
    k: v
    for k, v in os.environ.items()
    if k != "PYTHONPATH"
    and not k.startswith(("BINANCE_", "CRIPTO_BOT_", "MAIL_", "WHATSAPP_"))
}
common = f"""
import json,time,resource
from pathlib import Path
from cripto_bot.adapters.config import load_config
from cripto_bot.adapters.storage.continuous_sqlite import ContinuousStore
from cripto_bot.adapters.storage.continuous_report import snapshot,export_report
from cripto_bot.adapters.storage.notification_sqlite import NotificationStore
from cripto_bot.entrypoints.continuous import context
from cripto_bot.domain.market import iso
cfg=load_config(Path({str(config)!r}),{{}},root=Path({str(scratch)!r})).continuous
BASE={base};STEP=900000
"""
financial = (
    common
    + f"""
from cripto_bot.adapters.continuous_market import normalize
rules=json.loads({json.dumps(rules)!r})
def quote(at,price='100',qty='10',key='quote'):
    return {{'symbol':'BTCUSDT','kind':'BID_ASK','bid':price,'ask':price,'bid_qty':qty,'ask_qty':qty,
            'quote_id':key,'observed_at':iso(at),'market_timestamp':None}}
rows=[]
for i in range(50):
    opened=BASE-(51-i)*STEP
    rows.append([opened,'100','100','100','100','100',opened+STEP-1,'10000',1,'0','0','0'])
timings=[]
with ContinuousStore(cfg.data_dir,create=True) as store:
    store.initialize(context(cfg),BASE-2000)
    def event(key,kind,payload):
        start=time.perf_counter();result=store.append(key,kind,payload)
        timings.append((time.perf_counter()-start)*1000);return result
    event('arm','ARM',{{'at':BASE-1000,'t0':BASE,'rules':rules,'quote':quote(BASE-1000),
        'candles':normalize(rows,BASE-1000,BASE-STEP,50),'metadata_at':BASE-1000}})
    event('buy','ADMIT',{{'at':BASE+2000,'order_id':'buy','side':'BUY','quantity':'1','quote':quote(BASE+2000)}})
    event('first','POLL',{{'at':BASE+7000,'quote':quote(BASE+7000,qty='4',key='first')}})
    event('second','POLL',{{'at':BASE+12000,'quote':quote(BASE+12000,qty='3',key='second')}})
    state=event('cancel','CONTROL',{{'at':BASE+13000,'request_id':'cancel-buy','action':'cancel','order_id':'buy'}})
    buy=state.wallet.data()
    assert buy['usdt_free']=='9929.93000000' and buy['btc_free']=='0.70000000',buy
    event('sell','ADMIT',{{'at':BASE+14000,'order_id':'sell','side':'SELL','quantity':'0.7',
        'quote':quote(BASE+14000,price='110',key='sell-admit')}})
    event('third','POLL',{{'at':BASE+19000,'quote':quote(BASE+19000,price='110',qty='2',key='third')}})
    event('sell-cancel','CONTROL',{{'at':BASE+20000,'request_id':'cancel-sell','action':'cancel','order_id':'sell'}})
    report=snapshot(store,BASE+20000,notification_dir=cfg.notification_data_dir)
    assert report['wallet']['realized']=='1.95800000' and report['position']=='0.50000000',report['wallet']
    manifest=export_report(cfg,report,'oracle')
    daily=snapshot(store,BASE+86400000,day='2026-10-01',notification_dir=cfg.notification_data_dir)
    assert daily['day']=='2026-10-01' and daily['eligible_slots']==96 and daily['day_complete']
    assert daily['equity'] is None and daily['pilot_approved'] is False
    daily_manifest=export_report(cfg,daily,'oracle-daily')
    daily_html=(daily_manifest.parent/'report.html').read_text()
    assert '2026-10-01' in daily_html and 'Clock e qualidade' in daily_html

    ddl={{name:sql for name,sql in store.db.execute("SELECT name,sql FROM sqlite_schema WHERE sql IS NOT NULL")}}
    introspection={{name:{{'columns':store.db.execute('PRAGMA table_info('+name+')').fetchall(),
        'foreign_keys':store.db.execute('PRAGMA foreign_key_list('+name+')').fetchall(),
        'indexes':store.db.execute('PRAGMA index_list('+name+')').fetchall()}} for name in
        ('journal','postings','projection','orders','fills','cycles','configurations','controls','notification_events')}}
    proof={{'synthetic':True,'network_requests':0,'orders_sent':0,'buy_oracle':buy,'sell_oracle':report['wallet'],
        'manifest':str(manifest),'daily_manifest':str(daily_manifest),'max_event_ms':max(timings),'event_ms':timings,
        'rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        'ddl':ddl,'introspection':introspection,'pilot_approved':False}}
Path({str(OUT / "oracle.json")!r}).write_text(json.dumps(proof,indent=2)+'\\n')
"""
)
worker = (
    common
    + f"""
from cripto_bot.application.notifications import drain
class FakeSender:
    def send(self,*args,**kwargs):return 'CONFIRMED'
start=time.perf_counter()
with NotificationStore(cfg.notification_data_dir) as queue:
    outcomes=[]
    for i in range(10):outcomes.append(drain(cfg,queue,BASE+20000+i*1000,FakeSender()))
    ddl={{name:sql for name,sql in queue.db.execute("SELECT name,sql FROM sqlite_schema WHERE sql IS NOT NULL")}}
    proof={{'synthetic':True,'delivery_fake':True,'http_requests':0,'service_receipts':0,
        'outcomes':outcomes,'elapsed_ms':(time.perf_counter()-start)*1000,
        'rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'ddl':ddl}}
Path({str(OUT / "worker.json")!r}).write_text(json.dumps(proof,indent=2)+'\\n')
"""
)
for phase, code in [("financial", financial), ("worker", worker)]:
    result = subprocess.run(
        [str(PYTHON), "-I", str(RUNNER), "--code", code],
        cwd=scratch,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (phase, result.stdout, result.stderr)
print(
    json.dumps(
        {
            "synthetic": True,
            "financial": str(OUT / "oracle.json"),
            "worker": str(OUT / "worker.json"),
        }
    )
)
