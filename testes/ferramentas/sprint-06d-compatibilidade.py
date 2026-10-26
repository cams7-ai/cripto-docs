"""Preserve sealed history and compare installed synthetic 06C/06D results, offline."""

import hashlib
import json
import subprocess
import tomllib
import zipfile
from pathlib import Path

ROOT = Path("/home/cams7/Dev/Cripto")
BOT = ROOT / "cripto-bot"
OUT = BOT / "reports/sprint06d"


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def old(path):
    return subprocess.check_output(["git", "show", "HEAD:" + path], cwd=BOT)


a = load(OUT / "baseline/wheel-smoke.json")
b = load(OUT / "offline/wheel-smoke-final.json")


def manifest(data):
    return Path(
        next(
            c["result"]["manifest"]
            for c in data["checks"]
            if c["command"] == "backtest-report"
        )
    )


def curves(data):
    return sorted(
        [
            {k: v for k, v in row.items() if k not in {"run_key", "checkpoint_bytes"}}
            for row in load(manifest(data).parent / "report.json")["curves"]
        ],
        key=lambda row: (row["segment"], row["variant"], row["profile"]),
    )


assert curves(a) == curves(b)
financial = []
for before, after in zip(a["checks"], b["checks"], strict=True):
    assert (
        before["command"] == after["command"]
        and before["exit_code"] == after["exit_code"]
    )
    if "financial_sha256" in before["result"]:
        assert (
            before["result"]["financial_sha256"] == after["result"]["financial_sha256"]
        )
        financial.append(before["command"])
prior = {
    p["name"]: p["version"] for p in tomllib.loads(old("uv.lock").decode())["package"]
}
current = {
    p["name"]: p["version"]
    for p in tomllib.loads((BOT / "uv.lock").read_text())["package"]
}
assert set(prior) == set(current)
assert {k: (prior[k], current[k]) for k in prior if prior[k] != current[k]} == {
    "cripto-analytics": ("0.1.0", "0.1.1")
}
protected = {}
for relative in [
    "adapters/storage/paper_sqlite.py",
    "adapters/storage/strategy_sqlite.py",
    "adapters/storage/backtest_sqlite.py",
    "domain/portfolio/models.py",
    "domain/portfolio/engine.py",
    "domain/backtest/engine.py",
]:
    p = BOT / "src/cripto_bot" / relative
    if not p.exists():
        continue
    assert p.read_bytes() == old(str(p.relative_to(BOT)))
    protected[str(p.relative_to(ROOT))] = sha(p)
prior_evidence = load(ROOT / "docs/testes/sprint-06c-evidencias.json")
for p, digest in prior_evidence["artifact_sha256"].items():
    assert sha(ROOT / p) == digest, p
m = manifest(a)
scratch = m.parents[3]
db = m.parents[2] / "backtest.sqlite3"
before = sha(db)
python = BOT / ".venv-wheel-06d/bin/python"
runner = BOT / "tests/offline_runner.py"


def run(args):
    result = subprocess.run(
        [str(python), "-I", str(runner), *args],
        cwd=BOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {"exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


report = run(
    [
        str(python.parent / "cripto-bot"),
        "backtest-report",
        "--config",
        str(scratch / "backtest.toml"),
    ]
)
assert report["exit"] == 0, report
new = Path(json.loads(report["stdout"])["manifest"])
exact = []
for name in [
    "report.json",
    "report.html",
    "equity.csv",
    "trades.csv",
    "decisions.csv",
    "analytics.json",
]:
    assert (m.parent / name).read_bytes() == (new.parent / name).read_bytes(), name
    exact.append(name)
code = f"""
import duckdb,json
from pathlib import Path
from cripto_analytics.adapters.reader import validate_export,query_export
old=Path({str(m.parent)!r});new=Path({str(new.parent)!r})
with duckdb.connect(':memory:') as db:
    db.execute('SET autoinstall_known_extensions=false');db.execute('SET autoload_known_extensions=false')
    for name in ['equity','trades','decisions']:
        a=db.execute('SELECT * FROM read_parquet(?) ORDER BY export_row',[str(old/(name+'.parquet'))]).fetchall()
        b=db.execute('SELECT * FROM read_parquet(?) ORDER BY export_row',[str(new/(name+'.parquet'))]).fetchall()
        assert a==b,name
checked=validate_export(Path({str(BOT)!r}),new/'manifest.json')
print(json.dumps({{'typed_parquet_rows_equal':True,'queries':{{v:query_export(checked,v,1000) for v in ['curve-summary','decisions-counts','trades-counts']}}}}))
"""
checked = run(["--code", code])
assert checked["exit"] == 0, checked
resume = run(
    [
        str(python.parent / "cripto-bot"),
        "backtest-run",
        "--config",
        str(scratch / "backtest.toml"),
        "--segment",
        "development",
    ]
)
assert (
    resume["exit"] == 3
    and "FROZEN_PROTOCOL_CHANGED" in resume["stdout"] + resume["stderr"]
), resume
registry = BOT / "data/backtest-usage/test-usage.sqlite3"
assert (
    sha(registry) == "af7ee92659cb1be9c4e322daeba997755430a040faec4b1342c1cabf082810bd"
)
assert sha(db) == before
artifacts = {}
for project in ["cripto-bot", "cripto-analytics"]:
    for p in (ROOT / project / "dist/06d-final").iterdir():
        if p.name.endswith((".whl", ".tar.gz")):
            artifacts[str(p.relative_to(ROOT))] = sha(p)
        if p.suffix == ".whl":
            with zipfile.ZipFile(p) as z:
                for source in (ROOT / project / "src").rglob("*.py"):
                    assert (
                        z.read(str(source.relative_to(ROOT / project / "src")))
                        == source.read_bytes()
                    ), source
                meta = z.read(
                    next(n for n in z.namelist() if n.endswith("/METADATA"))
                ).decode()
                assert "file://" not in meta and "@ /home/" not in meta
old_python = BOT / ".venv-wheel-06c/bin/python"


def old_run(args):
    result = subprocess.run(
        [
            str(old_python),
            "-I",
            str(runner),
            str(old_python.parent / "cripto-bot"),
            *args,
        ],
        cwd=BOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {"exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


paper_files = {p: sha(p) for p in (scratch / "paper-wallet").glob("*.sqlite3")}
rollback = old_run(["paper-reconcile", "--config", str(scratch / "paper.toml")])
assert rollback["exit"] == 0, rollback
assert json.loads(rollback["stdout"])["wallet"]["usdt_free"] == "10009.58001000"
assert all(sha(p) == h for p, h in paper_files.items())
continuous = load(OUT / "offline/continuous-wheels.json")
reject_new = old_run(
    ["paper-run", "--config", str(Path(continuous["scratch"]) / "continuous.toml")]
)
assert reject_new["exit"] == 2, reject_new
proof = {
    "curves_equal": len(curves(a)),
    "financial_commands_equal": financial,
    "prior_artifacts_preserved": len(prior_evidence["artifact_sha256"]),
    "dependency_version_changes": {"cripto-analytics": ["0.1.0", "0.1.1"]},
    "protected_sources_sha256": protected,
    "old_report": report,
    "old_resume_blocked": resume,
    "old_sqlite_sha256": before,
    "old_sqlite_unchanged": True,
    "registry_sha256": sha(registry),
    "old_export_exact_files": exact,
    "installed_projection_proof": json.loads(checked["stdout"]),
    "artifact_sha256": artifacts,
    "sources_equal_to_final_wheels": True,
    "rollback_old_release_paper_reconcile": rollback,
    "rollback_new_configuration_rejected": reject_new,
}
(OUT / "offline/compatibility.json").write_text(json.dumps(proof, indent=2) + "\n")
print(
    json.dumps(
        {
            "curves": proof["curves_equal"],
            "exact_files": len(exact),
            "artifacts_preserved": proof["prior_artifacts_preserved"],
        }
    )
)
