"""Check links and JSONs of the affected local documentation; no network."""

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

DOC = Path("/home/cams7/Dev/Cripto/docs")
changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"], cwd=DOC, text=True
).splitlines()
paths = {DOC / name for name in changed if name.endswith(".md")}
paths.update(
    DOC / name
    for name in [
        "api/continuous.md",
        "modulos/paper-continuous.md",
        "operacao/continuous-runbook.md",
        "bancos/continuous-sqlite.md",
        "bancos/notification-sqlite.md",
        "decisoes/0011-paper-continuous-e-entrega-local.md",
        "testes/sprint-06d-validacao.md",
    ]
)
missing = []
count = 0
for path in sorted(paths):
    assert path.is_file(), path
    for target in re.findall(r"\[[^\]\n]+\]\(([^\s)]+)\)", path.read_text()):
        if "://" in target or target.startswith(("mailto:", "#")):
            continue
        target = unquote(target.split("#")[0])
        if target and not (path.parent / target).resolve().exists():
            missing.append([str(path), target])
        count += 1
for name in [
    "sprint-06d-evidencias.json",
    "sprint-06d-schema.json",
    "sprint-06d-pre-protocolo.json",
]:
    json.loads((DOC / "testes" / name).read_text())
assert not missing, missing
print(
    json.dumps(
        {
            "markdown_files": len(paths),
            "local_links": count,
            "missing": missing,
            "json_valid": 3,
        }
    )
)
