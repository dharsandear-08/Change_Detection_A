#!/usr/bin/env python3
"""DD_Style universal ProjectSnapshot.txt restore tool.

Restores files into the project root.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "ProjectSnapshot.txt"
MARKER_START = re.compile(r"^###FILE### (.+)$")
MARKER_END = "###ENDFILE###"

def safe_relative_path(value: str) -> Path:
    value = value.replace("\\", "/")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe snapshot path: {value}")
    return path

def main():
    if not SNAPSHOT.exists():
        raise FileNotFoundError(f"{SNAPSHOT} not found")

    current = None
    buffer = []
    created = 0

    for raw in SNAPSHOT.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True):
        line = raw.rstrip("\r\n")
        match = MARKER_START.match(line)

        if match:
            current = safe_relative_path(match.group(1).strip())
            buffer = []
            continue

        if line == MARKER_END:
            if current is not None:
                target = ROOT / current
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("".join(buffer), encoding="utf-8", newline="\n")
                print(f"[CREATED] {current.as_posix()}")
                created += 1
            current = None
            buffer = []
            continue

        if current is not None:
            buffer.append(raw)

    print(f"\n[OK] Project restored. Files created/updated: {created}")

if __name__ == "__main__":
    main()
