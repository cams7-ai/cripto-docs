"""Inspect only closed synthetic drill stores and derive technical documentation."""

import json
import sqlite3
from pathlib import Path

root = Path("/home/cams7/Dev/Cripto")
out = root / "cripto-bot/reports/sprint06d/offline"
oracle = json.loads((out / "oracle.json").read_text())
directory = Path(oracle["manifest"]).parents[2]
result = {}
for key, path in [
    ("continuous", directory / "continuous.sqlite3"),
    ("notification", directory.parent / "delivery/notifications.sqlite3"),
]:
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("BEGIN")
    schema = {
        n: s
        for n, s in db.execute(
            "SELECT name,sql FROM sqlite_schema WHERE sql IS NOT NULL"
        )
    }
    tables = {}
    for (name,) in db.execute("SELECT name FROM sqlite_schema WHERE type='table'"):
        indexes = db.execute("PRAGMA index_list(" + name + ")").fetchall()
        tables[name] = {
            "columns": db.execute("PRAGMA table_info(" + name + ")").fetchall(),
            "foreign_keys": db.execute(
                "PRAGMA foreign_key_list(" + name + ")"
            ).fetchall(),
            "indexes": {
                row[1]: {
                    "list": row,
                    "columns": db.execute(
                        "PRAGMA index_info(" + row[1] + ")"
                    ).fetchall(),
                }
                for row in indexes
            },
        }
    result[key] = {
        "schema_version": db.execute("PRAGMA user_version").fetchone()[0],
        "quick_check": db.execute("PRAGMA quick_check").fetchone()[0],
        "foreign_key_check": db.execute("PRAGMA foreign_key_check").fetchall(),
        "ddl": schema,
        "tables": tables,
    }
    db.close()
    name = "continuous-sqlite" if key == "continuous" else "notification-sqlite"
    p = root / "docs/bancos" / (name + ".md")
    body = p.read_text().split("\n## DDL efetivo e inspeção offline")[0]
    body += (
        "\n## DDL efetivo e inspeção offline\n\nExtraído do banco sintético dos oráculos instalados em 26/10/2026, schema1. Não é dump operacional. [Introspecção completa](../testes/sprint-06d-schema.json) contém tipos/nulabilidade/defaults/PK/FK/índices, incluindo autoíndices UNIQUE. Fonte: `cripto-bot/src/cripto_bot/adapters/storage/"
        + ("continuous_sqlite.py" if key == "continuous" else "notification_sqlite.py")
        + "`; hashes no guia/evidências.\n\n```sql\n"
        + ";\n".join(schema.values())
        + ";\n```\n"
    )
    p.write_text(body)
(root / "docs/testes/sprint-06d-schema.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n"
)
print(
    {
        k: {
            "tables": len(v["tables"]),
            "ddl": len(v["ddl"]),
            "quick_check": v["quick_check"],
        }
        for k, v in result.items()
    }
)
