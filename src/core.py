"""Command-line utility to split a monolithic Python file into separate section files."""

import argparse
import csv
import os
from dataclasses import dataclass
from typing import List, Tuple

__version__ = "1.0.0"


@dataclass
class Section:
    name: str
    start: int
    end: int


class ConfigError(Exception):
    pass


def parse_config(path: str) -> List[Section]:
    sections: List[Section] = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader, start=1):
            if not row or all(not c.strip() for c in row):
                continue
            if len(row) < 3:
                raise ConfigError(f"Invalid config at line {i}: {row}")

            name = row[0].strip()
            if not name:
                continue

            header_name = name.lower()
            if (
                header_name == "section_name"
                and row[1].strip().lower() in {"start_line", "start"}
                and row[2].strip().lower() in {"end_line", "end"}
            ):
                continue

            try:
                start = int(row[1])
                end = int(row[2])
            except ValueError:
                raise ConfigError(f"Invalid range at config line {i}: {row}")
            sections.append(Section(name, start, end))
    return sections


def validate_sections(sections: List[Section], total_lines: int) -> None:
    for s in sections:
        if s.start > s.end:
            raise ConfigError(f"Invalid range for {s.name}: {s.start} > {s.end}")
        if s.start < 1 or s.end < 1:
            raise ConfigError(f"Line numbers must be >= 1 for {s.name}")
        if s.end > total_lines:
            raise ConfigError(f"Range for {s.name} extends beyond source file: {s.end} > {total_lines}")

    ranges = [(s.start, s.end, s.name) for s in sections]
    ranges.sort()
    for (a1, b1, n1), (a2, b2, n2) in zip(ranges, ranges[1:]):
        if a2 <= b1:
            raise ConfigError(
                "Overlapping sections detected.\n{0}: {1}-{2}\n{3}: {4}-{5}".format(
                    n1, a1, b1, n2, a2, b2
                )
            )


def normalize_filename(section_name: str) -> str:
    if section_name.lower().endswith(".py"):
        return section_name
    return f"{section_name}.py"


def output_filename_for(section_name: str) -> str:
    if section_name.lower() in {"main.py", "main"}:
        return "main.py"
    return normalize_filename(section_name)


def extract_lines(lines: List[str], start: int, end: int) -> List[str]:
    return lines[start - 1 : end]


def uncomment_imports(section_lines: List[str]) -> List[str]:
    out = []
    for line in section_lines:
        stripped = line.lstrip()
        if stripped.startswith("# import") or stripped.startswith("#from") or stripped.startswith("# from "):
            idx = line.find("#")
            if idx != -1:
                line = line[:idx] + line[idx + 1 :]
            out.append(line.lstrip())
            continue
        out.append(line)
    return out


def write_output(out_dir: str, filename: str, content_lines: List[str]) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w") as f:
        f.writelines(content_lines)
    return path


def report_unassigned(sections: List[Section], total_lines: int) -> List[Tuple[int, int]]:
    covered = [False] * (total_lines + 1)
    for s in sections:
        for i in range(s.start, s.end + 1):
            covered[i] = True
    gaps = []
    i = 1
    while i <= total_lines:
        if not covered[i]:
            start = i
            while i <= total_lines and not covered[i]:
                i += 1
            gaps.append((start, i - 1))
        else:
            i += 1
    return gaps


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="monolith-splitter",
        description="Split a monolithic Python file into smaller section-specific files based on a CSV config.",
    )
    parser.add_argument("--src", required=True, help="Source Python file to split.")
    parser.add_argument("--cfg", required=True, help="CSV config describing splitting ranges.")
    parser.add_argument("--out", default="output", help="Directory for generated files.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    with open(args.src, "r") as f:
        src_lines = f.readlines()
    total = len(src_lines)

    sections = parse_config(args.cfg)
    validate_sections(sections, total)

    gaps = report_unassigned(sections, total)
    if gaps:
        print("WARNING: Unassigned line ranges:")
        for a, b in gaps:
            print(f"Lines {a}-{b}")

    grouped: dict[str, List[Section]] = {}
    for s in sections:
        filename = output_filename_for(s.name)
        grouped.setdefault(filename, []).append(s)

    for filename, group in sorted(grouped.items()):
        merged: List[str] = []
        for s in sorted(group, key=lambda item: item.start):
            chunk = extract_lines(src_lines, s.start, s.end)
            chunk = uncomment_imports(chunk)
            merged.extend(chunk)
        out_path = write_output(args.out, filename, merged)
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
