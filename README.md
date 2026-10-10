# Monolith Splitter

A lightweight utility that splits a large Python source file into section files based on a CSV map.

## What it does

The tool reads:
- the source file via `--src`
- a section map via `--cfg`
- an output directory via `--out`

It writes each configured section to its own Python file and can also warn when parts of the source file are not covered by any section.

## Required config format

The configuration file is a CSV with three columns:

```csv
SECTION_NAME,START_LINE,END_LINE
MAIN.py,3,12
UTILITIES,13,37
DATA_LOADING,38,58
PREPROCESSING,59,77
MODEL,78,100
EVALUATION,101,117
REPORTING,118,141
MAIN.py,142,158
```

Rules:
- the first row is a header and is ignored
- each section must use `SECTION_NAME,START_LINE,END_LINE`
- `START_LINE` and `END_LINE` must be inclusive line numbers
- ranges must not overlap
- line numbers must be at least 1
- the main file is treated as `main.py` when the section name is `MAIN.py`, `main.py`, `MAIN`, or `main`

## How to run

From the project root:

```bash
python3 monolith_splitter.py --src main.py --cfg inif.csv --out output
```

Example output:

```bash
WARNING: Unassigned line ranges:
Lines 1-2
Wrote output/DATA_LOADING.py
Wrote output/EVALUATION.py
Wrote output/MODEL.py
Wrote output/PREPROCESSING.py
Wrote output/REPORTING.py
Wrote output/UTILITIES.py
Wrote output/main.py
```

## Notes

- If there are gaps between configured sections, the script prints a warning but still writes the requested files.
- It strips leading commented import lines such as `# import ...` and `# from ...` from each extracted section when creating the split output.
- This is reliable for the project’s current workflow, but it is best treated as a focused utility script rather than a broad, enterprise-grade refactoring engine.

## Files in this project

- source file: [main.py](main.py)
- config file: [inif.csv](inif.csv)
- splitter: [monolith_splitter.py](monolith_splitter.py)