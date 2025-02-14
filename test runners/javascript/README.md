# Task Testing Guide
This guide will help you set up and run tests for the JavaScript tasks using Jest.

# Test Runner V1
This is the original test runner

## Prerequisites
- Node.js (Latest LTS version recommended)
  ```bash
  # Verify Node.js installation
  node --version
  ```

## Setup Instructions
### 1. Project Initialization
Navigate to the tasks folder and initialize a new Node.js project:
```bash
npm init -y
```

### 2. Installing Dependencies
Install Jest as a development dependency:
```bash
npm install --save-dev jest
```

### 3. Configure Package.json
Add Jest to your test scripts in `package.json`:
```json
{
  "scripts": {
    "test": "jest",
    "test-all": "node test-runner.js"
  }
}
```

### 4. Additional Dependencies
If a task has specific requirements:
1. Check for `requiredPackages.txt` in the task folder
2. Install any listed dependencies using the commands provided in the file
   ```bash
   # Example: If requiredPackages.txt contains "npm install jsonwebtoken bcrypt zod crypto"
   npm install jsonwebtoken bcrypt zod crypto
   ```

## Project Structure
Your project should follow this structure:
```
tasks/
├── node_modules/
├── package.json
├── package-lock.json
├── README.md
├── test-runner.js
├── task1/
│   ├── index.test.js
│   ├── solution.js
│   ├── base_code.js
│   └── alternate_responses/
│       ├── model1.js
│       ├── model2.js
│       └── ...
├── task2/
│   ├── index.test.js
│   ├── solution.js
│   ├── base_code.js
│   └── alternate_responses/
│       ├── model1.js
│       ├── model2.js
│       └── ...
└── ...
```

## Running Tests
### Regular Test Commands
To run tests for all tasks:
```bash
npm test
```

To run tests for a specific task:
```bash
npm test <task>
# Example: npm test 303989
```

### Test Runner
The test runner allows you to run tests against multiple implementations of a solution:

```bash
npm run test-all <task>
# Example: npm run test-all 303989
```

This command will:
1. Run tests against:
   - base_code.js (if present)
   - solution.js
   - All implementations in the alternate_responses folder
2. Show detailed test results for each implementation
3. Generate a summary showing pass/fail status for each implementation
4. Save a test summary file (<task>-test-summary.txt)

Example output structure:
```
=== Running tests for task 303989 ===

Testing implementation: base_code
========================================
✓ should handle a single string response
✓ should handle an empty object
...

Testing implementation: solution
========================================
✓ should handle a single string response
✓ should handle an empty object
...

=== Final Summary ===
========================================
base_code           : 40/40 tests [PASSED]
solution            : 38/40 tests [FAILED]
model1              : 40/40 tests [PASSED]
model2              : 35/40 tests [FAILED]
```

## Test Coverage (Optional)
To enable test coverage reporting, add this to your `package.json`:
```json
{
  "scripts": {
    "test": "jest",
    "test:coverage": "jest --coverage"
  }
}
```

## Additional Options
- **Watch Mode**: Run tests in watch mode
  ```bash
  npm test -- --watch
  ```
- **Verbose Output**: Get detailed test information
  ```bash
  npm test -- --verbose
  ```

## Troubleshooting
If you encounter any issues:
1. Verify your folder structure matches the project structure above
2. Ensure all dependencies are properly installed
3. Check that file paths in test files are correct
4. Verify Node.js and npm are up to date
5. For the test runner, ensure:
   - The test file has a proper require statement
   - All implementation files export the same function name
   - Files in alternate_responses have .js extension

# Test Runner V2
This is the improved test runner version.
Improvement compared to the original version includes:
- Simpler folder structure. Just like the python runner, you only need to put  the model files, like `model_A.js`, `model_B.js`... in a folder (preferably the task ID folder), and execute the rest runner file. There is no need for `base_code.js`, `solution.js`, `alternate_response` folder.
- Export test results to a `.md` file, which allow you to copy the result with a single click when you have an IDE.

## Prerequisites & Setup Instructions
Similar to `Test Runner V1`

## Project Structure
Your project should follow this structure:
```
tasks/
├── node_modules/
├── package.json
├── package-lock.json
├── README.md
├── test-runner-v2.js
├── task1/
│   ├── index.test.js
│   ├── model_A.js
│   ├── model_B.js
│   ├── model_C.js

```

## Running The Test Runner

The test runner allows you to run tests against multiple implementations of a solution and automatically generate markdown files consisting of test results.

For example, with the above folder structure, the command to generate the test should be

```bash
node test-runner-v2.js task1
```

The parameter `task1` is optional. If not presence, it will search for the file `.env` for the environmen variable `WORKING_TASK`, if not found, it search in the file `env`, if not found then it will try to call the process environment variable. Only after that, if a value is still not found, and error will occur.

The command will:
1. Run tests against all `.js` file in the provided folder
2. Output the result in the `report_results` folder
3. Generate a summary showing pass/fail status for each implementation
4. Save a test summary file (like `task1-test-summary.txt`)

## Additional Options
- **Coverage**: To output coverage information in the `report_results` folder, you can add `-c` or `--coverage`
  ```bash
  node test-runner-v2.js -c
  ```
## Bug Fix And Other Issues
If there is any issue with the `test-runner-v2.js`, feel free to contact me through the account `cuong.h@turing.com`, and I will response