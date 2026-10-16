import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "example"


def test_parse_config_reads_ranges():
    import monolith_splitter

    sections = monolith_splitter.parse_config(str(EXAMPLE / "inif.csv"))
    assert [section.name for section in sections[:3]] == ["MAIN.py", "UTILITIES", "DATA_LOADING"]
    assert sections[0].start == 3 and sections[0].end == 12


def test_output_filename_for_main_and_module_names():
    import monolith_splitter

    assert monolith_splitter.output_filename_for("main") == "main.py"
    assert monolith_splitter.output_filename_for("UTILITIES") == "UTILITIES.py"


def test_extract_lines_and_uncomment_imports():
    import monolith_splitter

    lines = ["# import os\n", "print('hi')\n", "# from x import y\n"]
    extracted = monolith_splitter.extract_lines(lines, 1, 3)
    assert extracted == lines
    uncommented = monolith_splitter.uncomment_imports(extracted)
    assert uncommented[0] == "import os\n"
    assert uncommented[2] == "from x import y\n"


def test_cli_generates_split_output(tmp_path):
    out_dir = tmp_path / "output"
    result = subprocess.run(
        [sys.executable, "-m", "monolith_splitter.core", "--src", str(EXAMPLE / "main.py"), "--cfg", str(EXAMPLE / "inif.csv"), "--out", str(out_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (out_dir / "main.py").exists()
    assert (out_dir / "UTILITIES.py").exists()
    assert "Wrote" in result.stdout


def test_cli_help_works():
    result = subprocess.run([sys.executable, "-m", "monolith_splitter.core", "--help"], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "Split a monolithic Python file" in result.stdout
