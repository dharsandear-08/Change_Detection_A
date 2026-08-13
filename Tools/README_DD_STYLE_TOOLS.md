# DD_Style — Universal Project Tools

Reusable Windows tools for any project.

## Folder
```text
YourProject/
├── Tools/
│   ├── RUN_TOOLS.bat
│   ├── folder_to_txt.bat
│   ├── txt_to_folder.bat
│   ├── folder_to_txt.py
│   ├── txt_to_folder.py
│   ├── zip_project.bat
│   ├── zip_project.py
│   └── config.ini
```

## One-click usage

Double-click:

`Tools\RUN_TOOLS.bat`

It automatically:
1. Detects the project root.
2. Creates/refreshes `ProjectSnapshot.txt`.
3. Creates a project ZIP under `release\`.
4. Keeps the tools reusable for any project.

## Individual tools

- `folder_to_txt.bat` -> project snapshot
- `txt_to_folder.bat` -> restore files from snapshot
- `zip_project.bat` -> create ZIP
- `RUN_TOOLS.bat` -> run snapshot + ZIP automatically

## Snapshot policy

Text/source/config files are included.

Large/generated/binary files are excluded by default:
- .git
- .venv / venv
- __pycache__
- node_modules
- output
- release
- ZIPs
- images
- GeoTIFFs
- Shapefile binary components
- QGIS .qgz
- office/media binaries

This prevents huge snapshots.

## Important

The snapshot is intended for source-code transfer/review, not as a replacement for the real GIS/data archive.

The ZIP tool can include project data if you change `EXCLUDE_DIRS` / `EXCLUDE_EXTENSIONS` in `zip_project.py`.
