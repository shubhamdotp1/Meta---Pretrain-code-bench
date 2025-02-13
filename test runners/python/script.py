#!/usr/bin/env python3
import argparse
import sys
import subprocess
import os
import shutil
from typing import List, Tuple


def setup_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Run tests on multiple Python scripts using a single test file"
    )
    parser.add_argument(
        "folder", help="Path to the folder containing Python scripts and test.py"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show complete test log instead of summary",
    )
    return parser


def get_python_files(folder: str) -> List[str]:
    """Get all Python files in the folder except test.py and solution.py."""
    files = []
    for file in os.listdir(folder):
        if file.endswith(".py") and file not in ["test.py", "solution.py"]:
            files.append(os.path.join(folder, file))
    return files


def create_report_folder(folder: str) -> str:
    """Create a reports folder if it doesn't exist."""
    report_folder = os.path.join(folder, "test_reports")
    os.makedirs(report_folder, exist_ok=True)
    return report_folder


def run_tests_with_coverage(
    script_path: str, test_path: str, verbose: bool
) -> Tuple[bool, str, str]:
    """
    Run pytest with coverage on the specified files.
    """
    script_dir = os.path.dirname(script_path)

    # Add script directory to PYTHONPATH
    env = os.environ.copy()
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{script_dir}:{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = script_dir

    # Configure pytest arguments based on verbosity
    pytest_args = ["-v", "--color=yes"]
    if not verbose:
        pytest_args.extend(["--tb=no", "-ra"])

    # Run tests with coverage
    try:
        test_output = subprocess.run(
            ["coverage", "run", "-m", "pytest", test_path] + pytest_args,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
    except subprocess.CalledProcessError as e:
        return False, "", f"Error running tests: {str(e)}"

    # Generate coverage report
    try:
        coverage_output = subprocess.run(
            ["coverage", "report", "-m"], capture_output=True, text=True, check=False
        )
    except subprocess.CalledProcessError as e:
        return False, test_output.stdout, f"Error generating coverage report: {str(e)}"

    return True, test_output.stdout, coverage_output.stdout


import re


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def process_script(
    script_path: str, folder: str, report_folder: str, verbose: bool
) -> None:
    """Process a single script file."""
    print(f"\nProcessing: {os.path.basename(script_path)}")

    # Create solution.py with script contents
    solution_path = os.path.join(folder, "solution.py")
    shutil.copy2(script_path, solution_path)

    # Run tests
    test_path = os.path.join(folder, "test.py")
    success, test_output, coverage_output = run_tests_with_coverage(
        solution_path, test_path, verbose
    )

    # Generate report
    script_name = os.path.splitext(os.path.basename(script_path))[0]
    report_path = os.path.join(report_folder, f"{script_name}_report.txt")

    with open(report_path, "w") as f:
        f.write(f"Test Report for {script_name}\n")
        f.write("=" * 50 + "\n\n")
        f.write("TEST RESULTS:\n")
        f.write("-" * 20 + "\n")
        f.write(strip_ansi_codes(test_output))
        f.write("\nCOVERAGE REPORT:\n")
        f.write("-" * 20 + "\n")
        f.write(strip_ansi_codes(coverage_output))

    # Clean up
    try:
        os.remove(solution_path)
        os.remove(".coverage")  # Remove coverage data file
    except:
        pass

    print(f"Report generated: {os.path.basename(report_path)}")


def main():
    """Main entry point for the script."""
    parser = setup_parser()
    args = parser.parse_args()

    # Validate folder
    if not os.path.isdir(args.folder):
        print(f"Error: '{args.folder}' is not a valid directory")
        sys.exit(1)

    test_path = os.path.join(args.folder, "test.py")
    if not os.path.exists(test_path):
        print(f"Error: 'test.py' not found in {args.folder}")
        sys.exit(1)

    # Get all Python files to test
    python_files = get_python_files(args.folder)
    if not python_files:
        print("No Python files found to test")
        sys.exit(1)

    # Create reports folder
    report_folder = create_report_folder(args.folder)

    # Process each script
    for script_path in python_files:
        process_script(script_path, args.folder, report_folder, args.verbose)

    print(f"\nAll reports generated in: {report_folder}")


if __name__ == "__main__":
    main()