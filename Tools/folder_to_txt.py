#!/usr/bin/env python3
"""DD_Style universal project snapshot generator.

Creates ProjectSnapshot.txt in the project root.
Only text/source/config files are included by default.
"""

from pathlib import Path
from datetime import datetime
import configparser

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "Tools" / "config.ini"
OUTPUT = ROOT / "ProjectSnapshot.txt"

DEFAULT_IGNORE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    "dist", "build", "output", "release", ".idea", ".vscode",
    ".pytest_cache", ".mypy_cache", ".ruff_cache"
}

DEFAULT_IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp",
    ".pdf", ".zip", ".rar", ".7z", ".exe", ".dll", ".so", ".bin",
    ".pyc", ".class", ".db", ".sqlite", ".sqlite3",
    ".xlsx", ".xls", ".pptx", ".docx", ".doc", ".mp4", ".mp3",
    ".wav", ".avi", ".mov", ".tif", ".tiff", ".jp2",
    ".shp", ".dbf", ".shx", ".prj", ".cpg", ".qgz", ".qgs"
}

def load_config():
    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        cfg.read(CONFIG_PATH, encoding="utf-8")
    return cfg

def should_skip(path: Path, cfg):
    if path.name == OUTPUT.name:
        return True
    if any(part in DEFAULT_IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in DEFAULT_IGNORE_EXTENSIONS:
        return True
    return False

def build_tree(folder: Path, cfg, prefix=""):
    entries = [p for p in folder.iterdir() if not should_skip(p, cfg)]
    entries.sort(key=lambda p: (p.is_file(), p.name.lower()))
    lines = []
    for i, entry in enumerate(entries):
        last = i == len(entries) - 1
        lines.append(prefix + ("└── " if last else "├── ") + entry.name)
        if entry.is_dir():
            lines.extend(build_tree(entry, cfg, prefix + ("    " if last else "│   ")))
    return lines

def main():
    cfg = load_config()
    files_written = 0

    with OUTPUT.open("w", encoding="utf-8", newline="\n") as out:
        out.write("=" * 80 + "\n")
        out.write("DD_STYLE PROJECT SNAPSHOT\n")
        out.write("=" * 80 + "\n")
        out.write(f"Generated : {datetime.now().isoformat(sep=' ', timespec='seconds')}\n")
        out.write(f"Root      : {ROOT}\n\n")

        out.write("=" * 80 + "\nPROJECT TREE\n" + "=" * 80 + "\n\n")
        out.write(ROOT.name + "\n")
        for line in build_tree(ROOT, cfg):
            out.write(line + "\n")

        out.write("\n" + "=" * 80 + "\nFILES\n" + "=" * 80 + "\n\n")

        for file in sorted(ROOT.rglob("*")):
            if not file.is_file() or should_skip(file, cfg):
                continue

            rel = file.relative_to(ROOT).as_posix()
            out.write(f"###FILE### {rel}\n")
            try:
                text = file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    text = file.read_text(encoding="utf-8-sig")
                except Exception:
                    text = "<<BINARY_OR_UNREADABLE_FILE_SKIPPED>>\n"
            except Exception as exc:
                text = f"<<READ ERROR: {exc}>>\n"

            out.write(text)
            if not text.endswith("\n"):
                out.write("\n")
            out.write("###ENDFILE###\n\n")
            files_written += 1

        out.write("=" * 80 + "\n")
        out.write(f"TOTAL FILES EXPORTED : {files_written}\n")
        out.write("=" * 80 + "\n")

    print(f"[OK] Snapshot: {OUTPUT}")
    print(f"[OK] Files exported: {files_written}")

if __name__ == "__main__":
    main()
