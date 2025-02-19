#!/usr/bin/env python3
import argparse
import platform
import sys
import subprocess
import os
import shutil
from typing import List, Tuple
from datetime import datetime


def setup_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Run tests on multiple Python scripts using a single test file"
    )
    parser.add_argument(
        "folder", nargs="?", help="Path to the folder containing Python scripts and test.py"
    )
    parser.add_argument(
        "--verbose",
        default=True,
        action="store_true",
        help="Show complete test log instead of summary",
    )
    return parser


def convert_pyx_to_py(folder: str) -> List[str]:
    """Convert .pyx files to .py files by renaming and return list of converted files."""
    converted_files = []

    # Find all .pyx files
    for file in os.listdir(folder):
        if file.endswith('.pyx') or file.endswith('.txt'):
            base_name = os.path.splitext(file)[0]
            pyx_path = os.path.join(folder, file)
            py_path = os.path.join(folder, f"{base_name}.py")

            # Remove existing .py file if it exists
            if os.path.exists(py_path):
                print(f"Removing existing file: {base_name}.py")
                os.remove(py_path)

            # Rename .pyx to .py
            print(f"Converting {file} to {base_name}.py")
            os.rename(pyx_path, py_path)
            converted_files.append(base_name)

    return converted_files


def get_working_task() -> str:
    """Get the WORKING_TASK folder from environment or .env/env file."""
    # Check environment variable first
    if "WORKING_TASK" in os.environ:
        return os.environ["WORKING_TASK"]

    # Check .env file
    env_files = [".env", "env"]  # List of files to check
    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    key, _, value = line.strip().partition("=")
                    if key == "WORKING_TASK":
                        return value

    # If nothing is found, return None
    return None


def get_python_files(folder: str) -> Tuple[List[str], List[str]]:
    """
    Get all Python files in the folder except test.py and solution.py.
    Returns a tuple of (python_files, converted_files)
    """
    converted_files = convert_pyx_to_py(folder)

    python_files = [
        os.path.join(folder, file) for file in os.listdir(folder)
        if file.endswith(".py") and file not in ["test.py", "solution.py"]
    ]

    return python_files, converted_files


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
    python_path = script_dir
    if "PYTHONPATH" in env:
        # Use OS-appropriate path separator
        python_path = f"{script_dir}{os.pathsep}{env['PYTHONPATH']}"
    env["PYTHONPATH"] = python_path

    # Configure pytest arguments based on verbosity
    pytest_args = ["-v", "--color=no"]
    if not verbose:
        pytest_args.extend(["--tb=no", "-ra"])

    # Determine coverage command based on OS
    if platform.system().lower() == 'darwin':  # macOS
        try:
            # Try to find coverage in PATH
            subprocess.run(['which', 'coverage'], check=True, capture_output=True)
            coverage_command = ['coverage']
        except subprocess.CalledProcessError:
            # Fall back to python -m coverage
            coverage_command = [sys.executable, "-m", "coverage"]
    else:
        # For Windows and Linux, use python -m coverage
        coverage_command = [sys.executable, "-m", "coverage"]

    # Run tests with coverage
    try:
        test_output = subprocess.run(
            [*coverage_command, "run", "-m", "pytest", test_path] + pytest_args,
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
            [*coverage_command, "report", "-m"],
            capture_output=True,
            text=True,
            check=False
        )
    except subprocess.CalledProcessError as e:
        return False, test_output.stdout, f"Error generating coverage report: {str(e)}"

    return True, test_output.stdout, coverage_output.stdout


def process_script(script_path: str, folder: str, report_folder: str, verbose: bool) -> None:
    """Process a single script file."""
    print(f"\nProcessing: {os.path.basename(script_path)}")
    solution_path = os.path.join(folder, "solution.py")
    shutil.copy2(script_path, solution_path)
    test_path = os.path.join(folder, "test.py")
    success, test_output, coverage_output = run_tests_with_coverage(solution_path, test_path, verbose)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = os.path.join(report_folder, f"{os.path.basename(script_path)}_report.md")

    with open(report_path, "w", encoding='utf-8') as f:
        f.write(f"# Test Report for {os.path.basename(script_path)}\n\n")
        f.write(f"Generated on: {timestamp}\n\n")
        f.write("## Test Results\n\n<details open>\n<summary>Click to expand/collapse</summary>\n\n```bash\n")
        f.write(test_output + "\n```\n\n</details>\n\n")
        f.write("## Coverage Report\n\n<details open>\n<summary>Click to expand/collapse</summary>\n\n```\n")
        f.write(coverage_output + "\n```\n\n</details>\n")

    os.remove(solution_path)
    try:
        os.remove(".coverage")
    except FileNotFoundError:
        pass
    print(f"Report generated: {os.path.basename(report_path)}")


def main():
    """Main entry point for the script."""
    parser = setup_parser()
    args = parser.parse_args()
    folder = args.folder or get_working_task()

    if not folder or not os.path.isdir(folder):
        print("Error: No valid input folder provided and WORKING_TASK not set.")
        sys.exit(1)

    test_path = os.path.join(folder, "test.py")
    if not os.path.exists(test_path):
        print(f"Error: 'test.py' not found in {folder}")
        sys.exit(1)

    python_files, converted_files = get_python_files(folder)
    if not python_files:
        print("No Python files found to test")
        sys.exit(1)

    report_folder = create_report_folder(folder)

    try:
        for script_path in python_files:
            process_script(script_path, folder, report_folder, args.verbose)
    except Exception as e:
        print("An error occurred: ", e)

    print(f"\nAll reports generated in: {report_folder}")


if __name__ == "__main__":
    main()