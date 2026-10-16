# Monolith Splitter

Split a large Python file into smaller, organized modules using a CSV-based section map.

This utility is designed for monolithic scripts that were intentionally sectioned with marker comments such as `# ============================================================` and then later need to be rebuilt into separate files.

## Why use it

- Extract sections from one big file into multiple Python files
- Keep generated module names predictable
- Restore import lines that were commented out for splitting
- Work from the command line in a simple terminal workflow

## Features

- CLI-based usage via `monolith-splitter`
- CSV config with `SECTION_NAME,START_LINE,END_LINE`
- Automatic output directory creation
- Warning output for unassigned ranges
- Wheel packaging for easy installation

## Installation

### From the built wheel

```bash
python3 -m pip install dist/monolith_splitter-0.1.0-py3-none-any.whl
```

## Quick start

```bash
monolith-splitter --src main.py --cfg inif.csv --out output
```

This will read the source file, parse the section ranges from the CSV, generate separate files, and save them in the output directory.

## Example config

```csv
SECTION_NAME,START_LINE,END_LINE
MAIN.py,3,12
UTILITIES,13,37
DATA_LOADING,38,58
MODEL,78,100
```

The tool will create files such as:

- `main.py`
- `UTILITIES.py`
- `DATA_LOADING.py`
- `MODEL.py`

## Command help

```bash
monolith-splitter --help
```

## Version

```bash
monolith-splitter --version
```

## Example output

```text
Wrote output/main.py
Wrote output/UTILITIES.py
Wrote output/DATA_LOADING.py
```

## Notes

The project includes a sample source file and config in the workspace, so you can test it immediately with the included files.

