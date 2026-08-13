#!/usr/bin/env python3
"""DD_Style universal project ZIP builder.

Creates a clean release ZIP while excluding development/generated files by
default. The archive contains the project root folder.
"""

from pathlib import Path
from datetime import datetime
import configparser
import zipfile

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "Tools" / "config.ini"

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".idea", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build", "release"
}

EXCLUDE_EXTENSIONS = {
    ".pyc", ".pyo", ".exe", ".dll", ".so", ".bin",
    ".tmp", ".log"
}

def load_config():
    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        cfg.read(CONFIG_PATH, encoding="utf-8")
    return cfg

def main():
    cfg = load_config()
    output_dir = ROOT / cfg.get("output", "release_dir", fallback="release")
    project_name = cfg.get("project", "name", fallback=ROOT.name)
    zip_name = cfg.get("output", "zip_name", fallback="{project_name}.zip").format(
        project_name=project_name
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_zip = output_dir / zip_name

    if output_zip.exists():
        output_zip.unlink()

    include_output = cfg.getboolean("options", "include_output", fallback=False)
    include_git = cfg.getboolean("options", "include_git", fallback=False)
    include_venv = cfg.getboolean("options", "include_venv", fallback=False)

    count = 0

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue

            rel = path.relative_to(ROOT)
            parts = set(rel.parts)

            if path == output_zip:
                continue
            if "release" in parts:
                continue
            if not include_git and ".git" in parts:
                continue
            if not include_venv and (".venv" in parts or "venv" in parts):
                continue
            if not include_output and "output" in parts:
                continue
            if any(part in EXCLUDE_DIRS for part in parts):
                continue
            if path.suffix.lower() in EXCLUDE_EXTENSIONS:
                continue

            # Include project folder in archive.
            arcname = Path(ROOT.name) / rel
            zf.write(path, arcname.as_posix())
            count += 1

    print("=" * 70)
    print("DD_STYLE PROJECT ZIP CREATED")
    print("=" * 70)
    print(f"Created : {output_zip}")
    print(f"Files   : {count}")
    print(f"Time    : {datetime.now().isoformat(sep=' ', timespec='seconds')}")
    print("=" * 70)

if __name__ == "__main__":
    main()
