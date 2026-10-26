"""Exercise installed continuous commands with explicit current synthetic capture, no sockets."""

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path("/home/cams7/Dev/Cripto")
BOT = ROOT / "cripto-bot"
PYTHON = BOT / ".venv-wheel-06d/bin/python"
RUNNER = BOT / "tests/offline_runner.py"
parent = BOT / ".wheel-smoke/06d"
parent.mkdir(parents=True, exist_ok=True)
scratch = Path(tempfile.mkdtemp(prefix="continuous-", dir=parent))
for name in ["pyproject.toml", "uv.lock", ".python-version"]:
    shutil.copyfile(BOT / name, scratch / name)
now = time.time_ns() // 1000000
step = 900000
close = now // step * step
rules = json.loads((BOT / "config/fixtures/paper-roundtrip.json").read_text())["rules"]
# Use the existing fixture's record format, with explicit synthetic time/constant prices.
rows = []
for index in range(51):
    opened = close - (51 - index) * step
    rows.append(
        [
            opened,
            "100",
            "100",
            "100",
            "100",
            "100",
            opened + step - 1,
            "10000",
            1,
            "0",
            "0",
            "0",
        ]
    )
capture = scratch / "capture.json"
capture.write_text(
    json.dumps(
        {
            "schema": 1,
            "exchange_info": {"symbols": [rules]},
            "frames": [
                {
                    "at": now,
                    "server_time": now,
                    "klines": rows,
                    "book_ticker": {
                        "symbol": "BTCUSDT",
                        "bidPrice": "100",
                        "askPrice": "100",
                        "bidQty": "10",
                        "askQty": "10",
                    },
                }
            ],
        }
    )
)
body = (
    (BOT / "config/continuous.example.toml")
    .read_text()
    .replace(
        'source = "binance_public"', f'source = "fixture"\nfixture_file = "{capture}"'
    )
)
for old, new in [
    ("data/continuous-demo", "financial"),
    ("data/continuous-market", "market"),
    ("data/continuous-delivery", "delivery"),
]:
    body = body.replace(old, str(scratch / new))
config = scratch / "continuous.toml"
config.write_text(body)
env = {
    k: v
    for k, v in os.environ.items()
    if k != "PYTHONPATH"
    and not k.startswith(("BINANCE_", "CRIPTO_BOT_", "MAIL_", "WHATSAPP_"))
}
checks = []


def invoke(command, *options, expected=0):
    args = [
        str(PYTHON),
        "-I",
        str(RUNNER),
        str(PYTHON.parent / "cripto-bot"),
        command,
        "--config",
        str(config),
        *options,
    ]
    started = time.monotonic()
    result = subprocess.run(
        args, cwd=scratch, env=env, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == expected, (command, result.stdout, result.stderr)
    data = json.loads(result.stdout) if result.stdout else {}
    assert data.get("orders_sent", 0) == 0
    checks.append(
        {
            "command": command,
            "options": options,
            "exit_code": result.returncode,
            "elapsed_ms": round((time.monotonic() - started) * 1000, 3),
            "result": data,
        }
    )
    return data


assert invoke("continuous-run", "--once")["status"] == "CONTINUOUS_NOOP"
assert not (scratch / "financial").exists()
active = body.replace("enabled = false", "enabled = true", 1)
active = active.replace(
    '[modules.trend_btc]\nmodule_id = "trend_sma"\nenabled = false',
    '[modules.trend_btc]\nmodule_id = "trend_sma"\nenabled = true',
)
config.write_text(active)
assert invoke("continuous-prepare")["status"] == "PREPARED"
assert invoke("continuous-run", "--once")["status"] == "ARMED"
assert invoke("continuous-reconcile")["status"] == "CONTINUOUS_RECONCILED"
report = invoke("continuous-report")
assert report["observation_status"] == "SYNTHETIC_NOT_PILOT"
assert invoke("notify-drain", "--once")["status"] == "NOTIFICATIONS_DISABLED"
assert not (scratch / "delivery").exists()
assert (
    invoke(
        "continuous-control",
        "--action",
        "pause",
        "--reason",
        "synthetic wheel drill",
        "--request-id",
        "wheel-pause",
    )["application"]
    == "PENDING"
)
assert invoke("continuous-run", "--once")["status"] == "PAUSED"
invoke("continuous-run", "--once", "--allow-network", expected=2)
manifest = json.loads(Path(report["manifest"]).read_text())
for name, digest in manifest["files"].items():
    assert (
        hashlib.sha256(
            (Path(report["manifest"]).parent / name).read_bytes()
        ).hexdigest()
        == digest
    )
snapshot = json.loads((Path(report["manifest"]).parent / "report.json").read_text())
assert snapshot["pilot_approved"] is False and snapshot["eligible_slots"] == 672
packages = snapshot["runtime_identity"]["packages"]
assert len(packages) == 4 and all(
    v["installation"] == "wheel" for v in packages.values()
)
proof = {
    "status": "APPROVED_OFFLINE_CONTINUOUS_WHEELS",
    "synthetic": True,
    "pilot_approved": False,
    "sockets_blocked": True,
    "scratch": str(scratch),
    "checks": checks,
    "packages": packages,
    "report": report["html_report"],
}
(BOT / "reports/sprint06d/offline/continuous-wheels.json").write_text(
    json.dumps(proof, indent=2) + "\n"
)
print(
    json.dumps(
        {"checks": len(checks), "report": proof["report"], "status": proof["status"]}
    )
)
