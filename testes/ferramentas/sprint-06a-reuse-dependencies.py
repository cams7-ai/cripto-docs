"""Reuse verified baseline runtime distributions when offline wheel cache is incomplete.

Run with the existing bot Python. Both environments and requirements must
be inside Cripto. This does not replace installation of the application/core
wheels or claim a cold-cache install.
"""

import argparse
import base64
import csv
import hashlib
import io
import json
import re
import shutil
from importlib import metadata
from pathlib import Path

from packaging.requirements import Requirement

WORKSPACE = Path("/home/cams7/Dev/Cripto").resolve()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_environment", type=Path)
    parser.add_argument("target_environment", type=Path)
    parser.add_argument("requirements", type=Path)
    args = parser.parse_args()
    paths = [
        args.source_environment.resolve(),
        args.target_environment.resolve(),
        args.requirements.resolve(),
    ]
    if not all(p.is_relative_to(WORKSPACE) for p in paths) or paths[0] == paths[1]:
        parser.error(
            "Use distinct environments and requirements inside the Cripto workspace"
        )
    src = paths[0] / "lib/python3.13/site-packages"
    dst = paths[1] / "lib/python3.13/site-packages"
    if not src.is_dir() or not dst.is_dir():
        parser.error("Both Python 3.13 environments must already exist")
    required = []
    for line in paths[2].read_text().splitlines():
        match = re.match(r"^([a-zA-Z0-9_-]+)==([^\s]+)", line)
        if match:
            requirement = Requirement(line.rstrip().removesuffix("\\").strip())
            if requirement.marker is None or requirement.marker.evaluate():
                required.append((match[1], match[2]))
    if not required or any(
        n.replace("_", "-") in {"cripto-bot", "cripto-core"} for n, _ in required
    ):
        parser.error(
            "Export only pinned external runtime dependencies, excluding bot/core"
        )
    distributions = {
        d.metadata["Name"].lower().replace("_", "-"): d
        for d in metadata.distributions(path=[str(src)])
    }
    checked = []
    copies = []
    for name, version in required:
        distribution = distributions[name.lower().replace("_", "-")]
        if distribution.version != version:
            raise ValueError(f"Version mismatch for {name}")
        count = 0
        for file in distribution.files or []:
            path = Path(distribution.locate_file(file))
            target = dst / str(file)
            if not path.resolve().is_relative_to(
                src
            ) or not target.resolve().is_relative_to(dst):
                if path.resolve().parent == paths[0] / "bin":
                    target = paths[1] / "bin" / path.name
                else:
                    continue
            if not path.is_file() or path.suffix == ".pyc":
                continue
            if file.hash is not None:
                if file.hash.mode != "sha256":
                    raise ValueError("Unsupported RECORD hash")
                digest = base64.urlsafe_b64encode(
                    hashlib.sha256(path.read_bytes()).digest()
                )
                if digest.rstrip(b"=").decode() != file.hash.value:
                    raise ValueError(f"RECORD mismatch for {name}/{file}")
            copies.append((path, target))
            count += 1
        checked.append(
            {
                "name": name,
                "version": version,
                "copied_files": count,
                "record_mismatches": [],
            }
        )
    # Verify the complete input before copying, without modifying the baseline.
    for source, target in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if target.parent == paths[1] / "bin":
            body = target.read_bytes()
            if body.startswith(b"#!"):
                line, rest = body.split(b"\n", 1)
                if b"python" in line:
                    target.write_bytes(
                        b"#!" + str(paths[1] / "bin/python").encode() + b"\n" + rest
                    )
            target.chmod(source.stat().st_mode)
    # Rebase only generated console script entries in the copied installation RECORD.
    for name, _ in required:
        distribution = distributions[name.lower().replace("_", "-")]
        record = distribution.read_text("RECORD")
        if record is None:
            raise ValueError("Missing source RECORD")
        rows = list(csv.reader(io.StringIO(record)))
        for row in rows:
            target = (dst / row[0]).resolve()
            if target.parent == paths[1] / "bin" and target.is_file():
                body = target.read_bytes()
                encoded = base64.urlsafe_b64encode(hashlib.sha256(body).digest())
                row[1] = "sha256=" + encoded.rstrip(b"=").decode()
                row[2] = str(len(body))
        for file in distribution.files or []:
            if str(file).endswith(".dist-info/RECORD"):
                with (dst / str(file)).open("w", newline="") as handle:
                    csv.writer(handle, lineterminator="\n").writerows(rows)
    print(json.dumps(checked, indent=2))


if __name__ == "__main__":
    main()
