# Test Suite for C++ Code Runner and Task Creator

## Folder Structure

The project is organized as follows:

```
Test_Suite/
│
├── tasks/
│   ├── 621206/
│   │   ├── src/                     # Source files for the task
│   │   │   ├── base_code.cpp
│   │   │   ├── correct_response.cpp
│   │   │   ├── incorrect_response.cpp
│   │   │   ├── model1.cpp
│   │   │   ├── model2.cpp
│   │   │   ├── ...
│   │   ├── tests/                   # Unit tests for the task
│   │   │   └── test_model.cpp
│   │   ├── CMakeLists.txt           # CMake configuration for the task
│   │   ├── template_wrapper.h.in    # Template for wrapper headers
│   │   ├── logs.txt                 # Logs generated by the code runner
│   │   └── build/                   # Build directory (generated)
│   ├── 621262/                      # Example of another task
│   └── ...                          # Additional tasks
│
├── create_task.sh                   # Script to create new tasks
├── code_runner.sh                   # Script to build and run tasks
└── README.md                        # Documentation
```

---

## Creating a Task

To create a new task, use the `create_task.sh` script:

1. Run the script with a task ID:
   ```bash
   chmod +x ./create_task.sh
   ./create_task.sh <task_id>
   ```
   Example:
   ```bash
   chmod +x ./create_task.sh
   ./create_task.sh 621300
   ```

2. This will generate the following directory structure for the new task:
   ```
   tasks/<task_id>/
   ├── src/                     # Contains all source files
   │   ├── base.cpp
   │   ├── ideal.cpp
   │   ├── incorrect.cpp
   │   ├── A.cpp
   │   ├── B.cpp
   │   ├── ...
   ├── tests/                   # Contains the unit test file
   │   └── test_model.cpp
   ├── CMakeLists.txt           # Task-specific CMake configuration
   ├── template_wrapper.h.in    # Template for the wrapper header
   └── build/                   # Build directory (created during the build process)
   ```

3. **Important Note**:  

The `template_wrapper.h.in` and other generated files are handled automatically. You don't need to modify or worry about them.  

There are two scripts:  
1. For macOS and Linux  
2. For Windows  

Please use `code_runner.sh` according to your OS.

---

## Running the Scripts

To build and test tasks, use the `code_runner.sh` script:

### Running a Specific Task
```bash
chmod +x ./code_runner.sh
./code_runner.sh <task_id>
```
Example:
```bash
chmod +x ./code_runner.sh
./code_runner.sh 621206
```

- This will:
  - Clean the `build/` directory.
  - Generate build files using `cmake`.
  - Build the project using `make`.
  - Run the tests and save the output to `logs.txt` inside the task folder.

### Running All Tasks
```bash
./code_runner.sh ALL
```
This will iterate through all tasks in the `tasks/` directory and process them.

---

## Task Hierarchy

Each task has a structured folder layout:
```
tasks/<task_id>/
├── src/                     # Source files (e.g., models, base code, etc.)
├── tests/                   # Unit tests (include necessary headers and GTest)
├── CMakeLists.txt           # Build configuration
├── template_wrapper.h.in    # Wrapper template for dynamic linking
├── logs.txt                 # Logs for test runs
├── build/                   # Build output (generated automatically)
```

### Notes on `test_model.cpp`
- Ensure the following is included in your test file:
  ```cpp
  #include WRAPPER_FILE  // Include the wrapper file dynamically
  #include <gtest/gtest.h>  // Include GoogleTest
  ```

- If your tests require additional headers, include them explicitly in the test file.

---

## Example Workflow

1. Create a task:
   ```bash
   ./create_task.sh 621300
   ```
2. Add your logic to `src/` files and write tests in `tests/test_model.cpp`.

3. Run the task:
   ```bash
   ./code_runner.sh 621300
   ```

4. View logs:
   Open `tasks/621300/logs.txt` to check the test results.

---

## Dependencies

- **GoogleTest**: The project automatically fetches GoogleTest using CMake. Ensure you have internet access during the build process.
- **CMake**: Version 3.14 or higher.
- **Make**: For building the projects.

## Requirements
- CMake>=3.14
- Make
- GoogleTest (fetched automatically during the build process)
- C++17-compatible compiler (e.g., GCC, Clang, MSVC)
- Bash