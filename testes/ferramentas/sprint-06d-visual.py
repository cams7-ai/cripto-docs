"""Render only local synthetic reports, with network resolution blocked."""

import json
import os
from pathlib import Path
import subprocess

ROOT = Path("/home/cams7/Dev/Cripto")
BOT = ROOT / "cripto-bot"
OUT = BOT / "reports/sprint06d"
DOC = ROOT / "docs/testes/relatorios/sprint-06d"
oracle = json.loads((OUT / "offline/oracle.json").read_text())
main = Path(oracle["manifest"]).parent / "report.html"
daily = Path(oracle["daily_manifest"]).parent / "report.html"
shots = [
    ("preview", DOC / "report.html", 3500),
    ("oracle-preview", main, 6000),
    ("daily-preview", daily, 6000),
    ("oracle-top", main, 1900),
    ("daily-top", daily, 1900),
]
for name, path, height in shots:
    profile = OUT / ("chrome-" + name)
    profile.mkdir(exist_ok=True)
    args = [
        "google-chrome",
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-sync",
        "--no-first-run",
        "--no-default-browser-check",
        "--host-resolver-rules=MAP * ~NOTFOUND",
        "--user-data-dir=" + str(profile),
        "--screenshot=" + str(DOC / (name + ".png")),
        "--window-size=1280," + str(height),
        path.as_uri(),
    ]
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=45,
        env={
            **os.environ,
            "XDG_CONFIG_HOME": str(profile / "xdg-config"),
            "XDG_CACHE_HOME": str(profile / "xdg-cache"),
        },
    )
    (OUT / "offline" / ("render-" + name + ".log")).write_text(
        result.stdout + result.stderr
    )
    assert result.returncode == 0 and (DOC / (name + ".png")).stat().st_size > 1000, (
        name
    )
print(json.dumps({"rendered": len(shots), "market_or_service_requests": 0}))
