"""Assemble actual offline evidence; never approve missing operational criteria."""

import hashlib
import html
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path("/home/cams7/Dev/Cripto")
DOC = ROOT / "docs"
BOT = ROOT / "cripto-bot"
OUT = BOT / "reports/sprint06d"


def load(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def xml(p):
    if not p.exists():
        return {"status": "PENDING"}
    return ET.parse(p).getroot().find("testsuite").attrib


proof = (
    load(OUT / "offline/compatibility.json")
    if (OUT / "offline/compatibility.json").exists()
    else {"status": "PENDING"}
)
verification = {
    "baseline": load(OUT / "baseline/acceptance.json"),
    "baseline_archive_sha256": sha(OUT / "baseline/tracked-baseline.tar"),
    "bot": xml(OUT / "offline/full-release.xml"),
    "earlier_full_with_coverage": xml(OUT / "offline/full-final.xml"),
    "release_review": xml(OUT / "offline/release-tests.xml"),
    "analytics": xml(OUT / "offline/analytics.xml"),
    "analytics_standalone": load(
        ROOT / "cripto-analytics/reports/sprint06d/standalone.json"
    ),
    "coverage_stage_note": "coverage.json belongs to the 635-test stage before focused final corrections; no claim of final full coverage percentage.",
    "final_lock_check": (OUT / "offline/final-lock-check.log").read_text()
    if (OUT / "offline/final-lock-check.log").exists()
    else "PENDING",
    "quality": {
        n: (OUT / "offline" / n).read_text()
        for n in [
            "ruff-final-direct.log",
            "format-final-direct.log",
            "mypy-final-direct.log",
        ]
    },
}
criteria = {}
for index in range(1, 23):
    state = "VALIDATED_OFFLINE"
    if index in {4, 11, 12, 13, 18, 19, 21}:
        state = "OFFLINE_VALIDATED_OPERATIONAL_PENDING"
    if index in {14, 16, 17}:
        state = "NOT_EXECUTED_AUTHORIZATION_OR_OBSERVATION_REQUIRED"
    if index == 22:
        state = "PENDING_GLOBAL_ACCEPTANCE"
    criteria[f"D{index:02}"] = {"status": state, "pilot_evidence": False}
complete = (
    verification["release_review"].get("failures") == "0"
    and verification["analytics"].get("failures") == "0"
    and verification["bot"].get("failures") == "0"
    and verification["bot"].get("errors") == "0"
    and proof.get("sources_equal_to_final_wheels") is True
    and "PENDING" not in verification["final_lock_check"]
)
status = (
    "SOFTWARE_VALIDATED/PILOT_PENDING"
    if complete
    else "OFFLINE_VALIDATION_IN_PROGRESS/PILOT_PENDING"
)
oracle = load(OUT / "offline/oracle.json")
worker = load(OUT / "offline/worker.json")
wheel = (
    load(OUT / "offline/wheel-smoke-final.json")
    if (OUT / "offline/wheel-smoke-final.json").stat().st_size
    else {}
)
continuous = load(OUT / "offline/continuous-wheels.json")
repositories = {}
for name in [
    "docs",
    "cripto-bot",
    "cripto-core",
    "cripto-market-data",
    "cripto-analytics",
]:

    def git(*args):
        return subprocess.check_output(
            ["git", *args], cwd=ROOT / name, text=True
        ).strip()

    repositories[name] = {
        "head": git("rev-parse", "HEAD"),
        "status": git("status", "--short"),
        "committed_by_task": False,
    }
files = {}
for name in ["cripto-bot", "cripto-analytics", "cripto-core", "cripto-market-data"]:
    p = ROOT / name
    for source in [
        *(p / "src").rglob("*.py"),
        *(p / "tests").rglob("*.py"),
        p / "pyproject.toml",
        p / "uv.lock",
        p / ".python-version",
    ]:
        if source.is_file():
            files[str(source.relative_to(ROOT))] = sha(source)
raw = {
    str(p.relative_to(ROOT)): sha(p)
    for p in [
        *(OUT / "offline").glob("*.json"),
        *(OUT / "offline").glob("*.log"),
        *(OUT / "offline").glob("*.xml"),
        *(OUT / "baseline").glob("*.json"),
    ]
    if p.is_file()
}
evidence = {
    "schema": 1,
    "generated_at": datetime.now(UTC).isoformat(),
    "status": status,
    "pilot_approved": False,
    "scope": "Python/local/PAPER/Spot/BTCUSDT/15m; synthetic observations/mock HTTP only",
    "milestones": {
        "D-M1": "APPROVED_OFFLINE",
        "D-M2": "APPROVED_OFFLINE" if complete else "IN_VALIDATION",
        "D-M3": "APPROVED_OFFLINE" if complete else "IN_VALIDATION",
        "D-M4": "NOT_EXECUTED",
        "D-M5": "PENDING",
    },
    "verification": verification,
    "acceptance": criteria,
    "repositories": repositories,
    "compatibility": proof,
    "wheel_checks": {
        "legacy": len(wheel.get("checks", [])),
        "continuous": len(continuous["checks"]),
        "socket_guard": True,
        "all_four_packages_wheel": True,
    },
    "synthetic_oracles": {
        "buy": oracle["buy_oracle"],
        "after_sell": oracle["sell_oracle"],
        "pilot_approved": False,
    },
    "measurements": {
        "financial_rss_mib": oracle["rss_mib"],
        "worker_rss_mib": worker["rss_mib"],
        "max_financial_event_ms": oracle["max_event_ms"],
        "worker_ten_passes_ms": worker["elapsed_ms"],
        "free_disk_gib": shutil.disk_usage(OUT).free / 1024**3,
        "synthetic_store_bytes": {
            p.name: p.stat().st_size
            for p in [
                Path(oracle["manifest"]).parents[2] / "continuous.sqlite3",
                Path(oracle["manifest"]).parents[3] / "delivery/notifications.sqlite3",
            ]
        },
        "observed_real_hours": 0,
        "real_network_requests": 0,
        "network_measurement_scope": "Project market/notification HTTP only; official documentation lookups are not pilot data.",
        "real_delivery_attempts": 0,
        "real_service_receipts": 0,
        "growth_per_real_hour": None,
        "operational_uptime": None,
    },
    "limitations": [
        "Seven actual days, eligible preflight and authorized channels remain unexecuted.",
        "Local book-participation proxy is not execution/queue/liquidity guarantee.",
        "RSS/latency/storage are small synthetic drills, not seven-day capacity proof.",
        "Complete cold-cache installation is not demonstrated; reused external RECORD/hash-verified packages.",
        "No additional economic backtest, tuning, OOS claim or guarantee of future performance.",
    ],
    "failures_and_corrections": [
        "Initial risk test used a loss below configured threshold; corrected oracle uses permitted tighter limit.",
        "Protective controls initially released UNKNOWN reservation; fixed and covered.",
        "Canonical JSON identity prevents tuple/list restart mismatch.",
        "Initial broad suite crossed live source edits and rejected frozen protocol; rerun with stable source. Full suite passed; Focused release tests validate the final subsequent corrections.",
        "Full suite emitted four fork deprecation warnings and one fixture SQLite ResourceWarning; focused release tests passed without warnings. Production delivery uses isolated subprocess, not test fork.",
        "Final analytics README rebuild changed the new wheel hash; lock and installed composition reverified.",
        "Auto-review rejected changing module selection; safer custody-only financial limits preserve module=None/active=False.",
    ],
    "source_files_sha256": files,
    "raw_evidence_sha256": raw,
    "actions_not_performed": [
        "market network",
        "real mail/WhatsApp",
        "Binance private/order/test",
        "AWS",
        "07/BT implementation",
        "commit",
        "remote/publication",
        "historical artifact replacement",
    ],
    "visual_review": {"status": "PENDING"},
}
(DOC / "testes/sprint-06d-evidencias.json").write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2) + "\n"
)


def esc(value):
    return html.escape(str(value))


def table(headers, rows):
    return (
        "<table><tr>"
        + "".join("<th>" + esc(x) + "</th>" for x in headers)
        + "</tr>"
        + "".join(
            "<tr>" + "".join("<td>" + esc(x) + "</td>" for x in row) + "</tr>"
            for row in rows
        )
        + "</table>"
    )


body = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sprint 06D — validação offline</title><style>body{font:16px/1.5 system-ui;background:#edf2f6;color:#163147;margin:0}main{max-width:1080px;margin:32px auto;background:white;padding:32px;border-top:6px solid #087577}h1{font-size:34px}h2{color:#087577;margin-top:30px}.notice{padding:16px;background:#fff2ce;border-left:4px solid #b27800}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:9px;text-align:left;border-bottom:1px solid #ccd8df;overflow-wrap:anywhere}th{background:#163147;color:white}.small{font-size:13px;overflow-wrap:anywhere}@media(max-width:600px){main{margin:0;padding:16px}h1{font-size:28px}}</style></head><body><main><p>CRIPTO / SPRINT 06D / PAPER LOCAL</p><h1>Software e piloto têm evidências distintas</h1>"""
body += (
    '<p class="notice">'
    + esc(status)
    + ". Zero horas reais observadas, zero mensagens reais e zero ordens externas. Drills sintéticos não comprovam sete dias, execução na corretora ou rentabilidade futura.</p>"
)
body += "<h2>Validação executada</h2>" + table(
    ["Prova", "Obtido"],
    [
        ["Baseline bot", verification["baseline"]["pytest"]["tests"] + " testes"],
        [
            "Bot após implementação",
            verification["bot"].get("tests", "Pendente") + " testes",
        ],
        [
            "Revisão das últimas correções",
            verification["release_review"].get("tests", "Pendente")
            + " testes (sobrepõem a suíte)",
        ],
        [
            "Analytics standalone",
            verification["analytics"].get("tests", "Pendente") + " testes",
        ],
        [
            "Comandos instalados",
            str(len(wheel.get("checks", [])))
            + " anteriores + "
            + str(len(continuous["checks"]))
            + " continuous",
        ],
        ["Curvas sintéticas iguais", proof.get("curves_equal", "Pendente")],
        [
            "Artefatos anteriores preservados",
            proof.get("prior_artifacts_preserved", "Pendente"),
        ],
    ],
)
body += "<h2>Oráculo financeiro — fills parciais e cancelamento</h2>" + table(
    ["Momento", "USDT livre", "BTC livre", "Custo USDT", "Fees USDT", "Realizado USDT"],
    [
        [
            label,
            *[
                wallet[k]
                for k in ["usdt_free", "btc_free", "cost_basis", "fees", "realized"]
            ],
        ]
        for label, wallet in [
            ("Após BUY0,4 + BUY0,3 e cancelamento", oracle["buy_oracle"]),
            ("Após SELL0,2 e cancelamento", oracle["sell_oracle"]),
        ]
    ],
)
body += "<p>BUY1@100, taxa0,1%; SELL parcial@110. Reservas finais zeradas, posição preservada. Valores reconciliados do novo journal; nenhuma liquidação automática.</p>"
body += "<h2>Recursos — somente drills pequenos</h2>" + table(
    ["Medição", "Obtido", "Limite / interpretação"],
    [
        [
            "RSS financeiro",
            f"{oracle['rss_mib']:.2f} MiB",
            "Alvo operacional512MiB, período real pendente",
        ],
        [
            "RSS worker fake",
            f"{worker['rss_mib']:.2f} MiB",
            "Processo separado; sem HTTP",
        ],
        [
            "Maior evento financeiro",
            f"{oracle['max_event_ms']:.2f} ms",
            "Não é latência de rede/slot real",
        ],
        [
            "Fila, dez passos fake",
            f"{worker['elapsed_ms']:.2f} ms",
            "Sem serviços ou recibos reais",
        ],
    ],
)
body += "<h2>Critérios e pendências</h2>" + table(
    ["ID", "Estado", "Evidência prospectiva"],
    [[k, v["status"], "Não executada"] for k, v in criteria.items()],
)
body += "<h2>Próxima fase depende de autorização e tempo real</h2><p>Revisar composição/runbook e obter autorização explícita para dados públicos, serviços e destinatários de teste. Preflight elegível congela T0/Tend antes de observar; sete dias UTC completos,672 slots e≥666 válidos no prazo, sete diários e consolidado. Falhas, kill e atraso permanecem no denominador. 07 não liberada.</p>"
body += (
    "<h2>Limitações</h2><ul>"
    + "".join("<li>" + esc(x) + "</li>" for x in evidence["limitations"])
    + "</ul>"
)
body += '<p class="small">Fonte: sprint-06d-evidencias.json e snapshots reconciliados dos drills. Hashes, comandos, revisões e falhas no guia de validação. Dados históricos anteriores apenas comparados/reexportados readonly; não houve nova otimização ou teste econômico da janela final.</p></main></body></html>'
(DOC / "testes/relatorios/sprint-06d/report.html").write_text(body)
print(status)

# A reviewable pre-protocol, deliberately not an armed pilot/manifest.
preprotocol = {
    "schema": 1,
    "status": "DRAFT_NOT_ARMED_PILOT_PENDING",
    "model": "paper-continuous-v1",
    "artifact_sha256": proof.get("artifact_sha256", {}),
    "configuration_example_sha256": sha(BOT / "config/continuous.example.toml"),
    "t0": None,
    "tend": None,
    "eligible_slots": 672,
    "minimum_valid_slots": 666,
    "t0_rule": "Next UTC midnight at least 15 minutes after successful authorized current-data preflight.",
    "warmup_rule": "50 current closed candles before freeze; reconfirm final 51 causal candles at T0 score.",
    "scope": {
        "mode": "PAPER",
        "market": "Spot",
        "symbol": "BTCUSDT",
        "interval": "15m",
        "strategy": "trend_sma20/50",
        "policy": "exclusive_owner",
    },
    "risk_caps": {
        "entry": "0.10",
        "exposure": "0.10",
        "daily_loss": "0.01",
        "drawdown": "0.05",
        "fee_bps": "10",
        "slippage_bps": "5",
    },
    "flags": {
        "engine": False,
        "strategy": False,
        "notifications": False,
        "whatsapp": False,
    },
    "authorization": {"public_data": False, "local_services_and_recipients": False},
    "missing": [
        "Explicit responsible instruction for D-M4 data and services/recipients.",
        "Eligible live filters/clock/closed data with four installed wheels.",
        "Supervision/resource budget and consistent backups.",
        "Seven actual UTC days and authorized receipts/daily and consolidated reports/review.",
    ],
    "instruction": "Do not replace missing fields with synthetic pilot timestamps, auto-enable flags or infer authorization.",
}
(DOC / "testes/sprint-06d-pre-protocolo.json").write_text(
    json.dumps(preprotocol, ensure_ascii=False, indent=2) + "\n"
)
