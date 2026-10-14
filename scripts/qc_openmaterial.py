"""Run the ASAM OpenMATERIAL 3D quality checker on every .xoma file in the given directories.

Needs the `qc_openmaterial` command from https://github.com/asam-ev/qc-openmaterial-3d.
Writes one .xqar report per file to --report-dir and exits with status 1 if any
checker reports an issue or fails to run.
"""

import argparse
import pathlib
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


def check_file(xoma, report):
    """Check one .xoma file and return a list of problem descriptions."""
    proc = subprocess.run(
        ["qc_openmaterial", "-d", "-i", str(xoma), "-r", str(report)],
        capture_output=True,
        text=True,
    )
    if proc.returncode or not report.exists():
        return [f"checker failed to run: {proc.stderr.strip()[-500:]}"]

    problems = []
    for checker in ET.parse(report).iter("Checker"):
        checker_id = checker.get("checkerId")
        if checker.get("status") == "error":
            problems.append(f"{checker_id}: {checker.get('summary')}")
        for issue in checker.iter("Issue"):
            problems.append(f"{checker_id}: {issue.get('description')}")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "dirs",
        nargs="+",
        type=pathlib.Path,
        help="Directories to search for .xoma files",
    )
    parser.add_argument(
        "--report-dir", type=pathlib.Path, default=pathlib.Path("qc-reports")
    )
    args = parser.parse_args()

    if not shutil.which("qc_openmaterial"):
        sys.exit(
            "qc_openmaterial not found; install https://github.com/asam-ev/qc-openmaterial-3d"
        )

    checked = failed = 0
    for root in args.dirs:
        for xoma in sorted(root.rglob("*.xoma")):
            rel = xoma.relative_to(root)
            report = args.report_dir / root.name / rel.with_suffix(".xqar")
            report.parent.mkdir(parents=True, exist_ok=True)
            problems = check_file(xoma, report)
            checked += 1
            if problems:
                failed += 1
                for problem in problems:
                    print(f"::error file={root.name}/{rel}::{problem}")

    print(f"Checked {checked} .xoma files, {failed} with issues.")
    if checked == 0:
        sys.exit("No .xoma files found.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
