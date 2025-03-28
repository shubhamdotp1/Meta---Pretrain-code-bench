import os
import json
import subprocess
import textwrap
import ast

def create_cpp_file(task, solution_key):
    code = []
    
    # Add includes (assumed necessary)
    code.append("#include <iostream>")
    code.append("#include <cassert>")
    code.append("using namespace std;\n")

    # Add prompt as comment
    code.append(task["prompt"].strip())

    # Add function implementation
    dedented_solution = textwrap.dedent(task[solution_key])
    code.append(dedented_solution)

    # Add main function and tests
    code.append("\nint main() {")
    test_cases = ast.literal_eval(task["test"]) if isinstance(task["test"], str) else task["test"]
    for test in test_cases:
        code.append("    " + test.strip())
    code.append("    cout << \"All tests passed.\\n\";\n    return 0;\n}")

    return "\n".join(code)

def run_cpp_file(source_path):
    binary_path = source_path.replace(".cpp", "")
    try:
        compile_result = subprocess.run(
            ["g++", source_path, "-o", binary_path],
            capture_output=True,
            text=True
        )
        if compile_result.returncode != 0:
            return "COMPILE ERROR", compile_result.stderr

        run_result = subprocess.run(
            [binary_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        status = "PASS" if run_result.returncode == 0 else "FAIL"
        return status, run_result.stdout + run_result.stderr

    except subprocess.TimeoutExpired:
        return "TIMEOUT", "Execution timed out."

def create_python_file(task, solution_key):
    code = []

    # Add prompt (as-is)
    code.append(task["prompt"].strip())
    # Add dedented solution under function definition
    dedented_solution = textwrap.dedent(task[solution_key])
    indented_solution = textwrap.indent(dedented_solution, '    ')  # indent inside the function
    code.append(indented_solution)
    # Add test cases
    code.append("\n# Tests")

    test_field = task.get("test")
    
    #test_cases = json.loads(task["test"])
    
    test_cases = ast.literal_eval(task["test"]) if isinstance(task["test"], str) else task["test"]

    for test in test_cases:
        code.append(test)

    return "\n".join(code)

def run_python_file(filepath):
    try:
        result = subprocess.run(
            ["python", filepath],
            capture_output=True,
            text=True,
            timeout=5
        )
        status = "PASS" if result.returncode == 0 else "FAIL"
        return status, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "Execution timed out."
def create_java_file(task, solution_key, classname):
    code = []


    # Add prompt as comment
    code.append(task["prompt"].strip())

    # Add method body (from canonical/incorrect solution)
    dedented_solution = textwrap.dedent(task[solution_key].strip())
    solution_lines = textwrap.indent(dedented_solution, "    ").splitlines()
    code.extend(solution_lines)

    # Add main method with test cases
    code.append("\n    public static void main(String[] args) {")
    
    test_field = task.get("test")
    test_cases = ast.literal_eval(test_field) if isinstance(test_field, str) else test_field
    for test in test_cases:
        code.append("        " + test.strip())
    
    code.append('        System.out.println("All tests passed.");')
    code.append("    }")

    # Close class
    code.append("}")

    return "\n".join(code)

def run_java_file(filepath):
    folder, filename = os.path.split(filepath)
    classname = filename.replace(".java", "")

    try:
        # Compile
        compile_result = subprocess.run(
            ["javac", filename],
            cwd=folder,
            capture_output=True,
            text=True
        )
        if compile_result.returncode != 0:
            return "COMPILE ERROR", compile_result.stderr

        # Run with assertions enabled
        run_result = subprocess.run(
            ["java", "-ea", classname],
            cwd=folder,
            capture_output=True,
            text=True,
            timeout=5
        )
        status = "PASS" if run_result.returncode == 0 else "FAIL"
        return status, run_result.stdout + run_result.stderr

    except subprocess.TimeoutExpired:
        return "TIMEOUT", "Execution timed out."

def create_js_file(task, solution_key):
    code = []
    code.append("const assert = require('assert');" + "\n")
    
    code.append(task["prompt"].strip())

    # Add function code
    
    
    solution = textwrap.dedent(task[solution_key].strip())
    code.append(solution + "\n")

    # Add test cases using console.assert
    test_field = task.get("test")
    test_cases = ast.literal_eval(test_field) if isinstance(test_field, str) else test_field

    code.append("// Tests")
    for test in test_cases:
        code.append(test)

    code.append('console.log("All tests passed.");')

    return "\n".join(code)

def run_js_file(filepath):
    try:
        result = subprocess.run(
            ["node", filepath],
            capture_output=True,
            text=True,
            timeout=5
        )
        status = "PASS" if result.returncode == 0 else "FAIL"
        return status, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "Execution timed out."


def handle_python_task(task, task_dir):
    ir_path = os.path.join(task_dir, "ir.py")
    with open(ir_path, "w") as f:
        f.write(create_python_file(task, "canonical_solution"))

    incs_path = os.path.join(task_dir, "incs.py")
    with open(incs_path, "w") as f:
        f.write(create_python_file(task, "incorrect_solution"))

    ir_status, ir_output = run_python_file(ir_path)
    incs_status, incs_output = run_python_file(incs_path)

    return (ir_path, ir_status, ir_output), (incs_path, incs_status, incs_output)


def handle_cpp_task(task, task_dir):
    ir_path = os.path.join(task_dir, "ir.cpp")
    with open(ir_path, "w") as f:
        f.write(create_cpp_file(task, "canonical_solution"))

    incs_path = os.path.join(task_dir, "incs.cpp")
    with open(incs_path, "w") as f:
        f.write(create_cpp_file(task, "incorrect_solution"))

    ir_status, ir_output = run_cpp_file(ir_path)
    incs_status, incs_output = run_cpp_file(incs_path)

    return (ir_path, ir_status, ir_output), (incs_path, incs_status, incs_output)


def handle_java_task(task, task_dir):
    entry_class = task['entry_point'].split(':')[0]
    ir_path = os.path.join(task_dir, f"{entry_class}.java")
    with open(ir_path, "w") as f:
        f.write(create_java_file(task, "canonical_solution", "IR"))

    ir_status, ir_output = run_java_file(ir_path)

    incs_path = os.path.join(task_dir, f"{entry_class}.java")
    with open(incs_path, "w") as f:
        f.write(create_java_file(task, "incorrect_solution", "INCS"))

    incs_status, incs_output = run_java_file(incs_path)

    return (ir_path, ir_status, ir_output), (incs_path, incs_status, incs_output)


def handle_js_task(task, task_dir):
    ir_path = os.path.join(task_dir, "ir.js")
    with open(ir_path, "w") as f:
        f.write(create_js_file(task, "canonical_solution"))

    incs_path = os.path.join(task_dir, "incs.js")
    with open(incs_path, "w") as f:
        f.write(create_js_file(task, "incorrect_solution"))

    ir_status, ir_output = run_js_file(ir_path)
    incs_status, incs_output = run_js_file(incs_path)

    return (ir_path, ir_status, ir_output), (incs_path, incs_status, incs_output)


def test_task(task):
    task_id = task["task_id"]
    language = task["language"]
    task_dir = os.path.join("all_tasks", task_id)
    os.makedirs(task_dir, exist_ok=True)

    print(f"\n=== Creating Task {task_id} ({language}) ===")

    if language == "Python":
        ir_result, incs_result = handle_python_task(task, task_dir)
    elif language == "C++":
        ir_result, incs_result = handle_cpp_task(task, task_dir)
    elif language == "Java":
        ir_result, incs_result = handle_java_task(task, task_dir)
    elif language == "JavaScript":
        ir_result, incs_result = handle_js_task(task, task_dir)
    else:
        print(f"⚠️ Skipping unsupported language: {language}")
        return None

    # Log and store test results
    ir_path, ir_status, ir_output = ir_result
    incs_path, incs_status, incs_output = incs_result

    print(f"\n=== Testing Task {task_id} ===")
    print(f"✅ {os.path.basename(ir_path)}: {ir_status}")
    task['ir_test_status'] = ir_status.strip()
    if ir_output.strip():
        print(ir_output.strip())
        task['ir_test_output'] = ir_output.strip()

    print(f"❌ {os.path.basename(incs_path)}: {incs_status}")
    task['incs_test_status'] = incs_status.strip()
    if incs_output.strip():
        print(incs_output.strip())
        task['incs_test_output'] = incs_output.strip()

    return task


def process_json(json_list):
  json_list=json.loads(json_list)
  AllTasks = []
  os.makedirs("all_tasks", exist_ok=True)
  for task in json_list:
      result = test_task(task)
      if result:
          AllTasks.append(result)
  return AllTasks
