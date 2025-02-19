const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const util = require('util');

const reportDir = 'test_reports';

class LogData {
    constructor() {
        this.logs = [];
    }

    addLog(text, addNewLine = true) {
        // If logs array is not empty and addNewLine is true, add newline before text
        if (this.logs.length > 0 && addNewLine) {
            this.logs.push('\n');
        }
        this.logs.push(text);
        return this;  // Enable method chaining
    }

    addDivisor(content, divChar){
        if (!divChar){
            divChar = '-'
        }
        let divLine  = divChar.repeat(30)
        if (content) {
            divLine += content;
        }
        divLine += divChar.repeat(30)
        this.addLog(divLine);
    }

    addNewLine(noNewLine){
        for (let i = 0; i < noNewLine; i++) {
            this.addLog("\t");
        }
    }

    toString() {
        return this.logs.join('');
    }
}

async function runTests(taskId) {
    const taskDir = path.join(process.cwd(), taskId);
    const testFilePath = path.join(taskDir, 'index.test.js');

    // Initialize summary object
    const testSummary = {};


    // Add base_code.js if it exists
    const exemptionFiles = ["solution.js", "index.test.js"];

    const allFileToTest = getAllJsFiles(taskId, exemptionFiles);

    console.log(`\n=== Running tests for task ${taskId} ===\n`);

    // Run tests for each implementation
    for (const file of allFileToTest) {
        const filePath = path.join(taskDir, file);
        const coverageDir = path.join(taskDir, reportDir, file.split('.')[0]);
        copyAndExportFunctions(filePath, taskId);
        const log = new LogData();
        log.addLog(`\n# Testing implementation: ${file}`);
        log.addLog("\n");
        log.addDivisor();


        const normalizedTestPath = testFilePath.split(path.sep).join('/');

        let command = `npx jest ${normalizedTestPath} --json --colors`;

        if (enableCoverage) {
            // For coverage directory, also normalize the path
            const normalizedCoverageDir = coverageDir.split(path.sep).join('/');
            command += ` --coverage --coverageDirectory="${normalizedCoverageDir}"`;
        }
        
        try {
            const output = execSync(command, {
                encoding: 'utf8',
                stdio: ['pipe', 'pipe', 'pipe'],
            });
            testResults = JSON.parse(output);
        } catch (error) {
            testResults = JSON.parse(error.stdout || '{}');
        }

        const testSuite = testResults.testResults?.[0];
        if (!testSuite) {
            log.addLog('\x1b[31mNo test results available\x1b[0m');
            testSummary[file] = { passed: 0, total: 0, status: 'ERROR' };
            return;
        }

        // Calculate summary
        const numPassedTests = testResults.numPassedTests || 0;
        const totalTests = testResults.numTotalTests || 0;
        const allPassed = numPassedTests === totalTests;

        // Store summary
        testSummary[file] = {
            passed: numPassedTests,
            total: totalTests,
            status: allPassed ? 'PASSED' : 'FAILED'
        };

        // Log implementation header
        log.addLog("```bash");

        // Log pass/fail for each test first
        testSuite.assertionResults.forEach(test => {
            const isPassed = test.status === 'passed';
            const status = isPassed ? '\x1b[32m✓\x1b[0m' : '\x1b[31m✕\x1b[0m';
            log.addLog(`${status} ${test.title}`);
        });


        // Log any failure messages
        testSuite.assertionResults.forEach(test => {
            if (test.status !== 'passed' && test.failureMessages?.length > 0) {
                log.addNewLine(1);
                log.addLog("  ● " + test.title);
                log.addLog('\x1b[31m' + test.failureMessages.join('\n') + '\x1b[0m');
            }
        });

        log.addLog("```");

        log.addDivisor();

        // Log suite summary at the end
        log.addLog('\nTest Suites: ' + (allPassed ? '\x1b[32m1 passed\x1b[0m' : '\x1b[31m1 failed\x1b[0m'))
            .addLog(`Tests:       ${numPassedTests} passed, ${totalTests - numPassedTests} failed, ${totalTests} total`);


        writeToReport(taskId, file, log.toString());
    }

    fs.unlinkSync(path.join(taskId,"./solution.js"));


    // Print final summary
    console.log('\n=== Final Summary ===');
    console.log('='.repeat(40));
    Object.entries(testSummary).forEach(([impl, results]) => {
        const status = results.status === 'PASSED'
            ? '\x1b[32mPASSED\x1b[0m'
            : '\x1b[31mFAILED\x1b[0m';
        console.log(`${impl.padEnd(20)}: ${results.passed}/${results.total} tests [${status}]`);
    });

    // Save summary to file
    const summaryPath = path.join(process.cwd(), `${taskId}-test-summary.txt`);
    let summaryContent = `Test Summary for ${taskId}\n${'='.repeat(40)}\n\n`;
    Object.entries(testSummary).forEach(([impl, results]) => {
        summaryContent += `${impl.padEnd(20)}: ${results.passed}/${results.total} tests [${results.status}]\n`;
    });
    fs.writeFileSync(summaryPath, summaryContent);
}

let taskId = process.argv[2] === '-c' || process.argv[2] === '--coverage' ? undefined : process.argv[2];
let enableCoverage = process.argv.includes('--coverage') || process.argv.includes('-c');

// If not in args, try .env file first, then env file
if (!taskId) {
    try {
        // Try .env file first
        const dotEnvPath = path.join(process.cwd(), '.env');
        const envContent = fs.readFileSync(dotEnvPath, 'utf8');
        const envVars = Object.fromEntries(
            envContent.split('\n')
                .filter(line => line.trim() && !line.startsWith('#'))
                .map(line => line.split('=').map(part => part.trim()))
        );
        taskId = envVars.WORKING_TASK;
    } catch (error) {
        // If .env fails, try env file
        try {
            const envPath = path.join(process.cwd(), 'env');
            const envContent = fs.readFileSync(envPath, 'utf8');
            const envVars = Object.fromEntries(
                envContent.split('\n')
                    .filter(line => line.trim() && !line.startsWith('#'))
                    .map(line => line.split('=').map(part => part.trim()))
            );
            taskId = envVars.WORKING_TASK;
        } catch (error) {
            // Ignore error if env file doesn't exist or can't be parsed
        }
    }
}

// If still not found, check environment variables
if (!taskId) {
    taskId = process.env.WORKING_TASK;
}

// Exit if task ID is not found in any source
if (!taskId) {
    console.error('Task ID not found in arguments, .env file, env file, or environment variables');
    process.exit(1);
}

runTests(taskId).catch(error => {
    console.error('Error running tests:', error);
    process.exit(1);
});

function getAllJsFiles(directoryPath, exemptionFiles = []) {
    try {
        // Read all files in directory
        convertJsxToJs(directoryPath);

        // Read all files in directory
        const files = fs.readdirSync(directoryPath);

        // Filter for .js files and exclude exempted files
        return files.filter(file => {
            return path.extname(file) === '.js' &&
                !exemptionFiles.includes(file);
        });

    } catch (error) {
        console.error('Error reading directory:', error);
        return [];
    }
}

function copyAndExportFunctions(inputFilePath, taskId, outputFilePath = 'solution.js') {
    try {
        outputFilePath = path.join(taskId, outputFilePath);
        // Read the input file

        let content = fs.readFileSync(inputFilePath, 'utf8');

        // This regex matches function declarations while tracking brace depth
        const functions = [];
        let braceDepth = 0;

        // Split content into lines for better processing
        const lines = content.split('\n');

        for (let line of lines) {
            // Count braces to track nesting level
            const openBraces = (line.match(/\{/g) || []).length;
            const closeBraces = (line.match(/\}/g) || []).length;

            // Check for function declaration at depth 0
            if (braceDepth === 0) {
                const funcMatch = line.match(/^(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(/);
                if (funcMatch && !funcMatch[1].startsWith('_')) {
                    functions.push(funcMatch[1]);
                }
            }

            braceDepth += openBraces - closeBraces;
        }

        // If there's already an exports statement, remove it
        content = content.replace(/module\.exports\s*=\s*{[^}]*};?\s*$/, '');

        // Add the export statement at the end
        if (functions.length > 0) {
            const exportStatement = `\nmodule.exports = { ${functions.join(', ')} };\n`;
            content = content.trim() + exportStatement;
        }

        const fd = fs.openSync(outputFilePath, 'w');
        fs.writeFileSync(fd, content);
        // Force write to disk
        fs.fsyncSync(fd);
        // Close the file descriptor
        fs.closeSync(fd);

        return functions; // Return list of exported functions

    } catch (error) {
        console.error('Error processing file:', error);
        return [];
    }
}

function writeToReport(taskId, filename, content) {
    // More comprehensive ANSI escape code stripping
    const stripAnsi = (str) => {
        // Remove color codes
        str = str.replace(/\x1b\[[0-9;]*m/g, '');
        // Remove other control sequences
        str = str.replace(/\x1b\[([0-9]{1,2}(;[0-9]{1,2})*)?[m|K]/g, '');
        // Remove unicode escape sequences
        str = str.replace(/[\u001b\u009b][[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><]/g, '');
        return str;
    };

    // Format the test results for better readability
    const formatTestResults = (content) => {
        const lines = content.split('\n');
        let formatted = [];

        // Add a timestamp
        formatted.push(`Test Run: ${new Date().toISOString()}\n`);

        // Process each line
        lines.forEach(line => {
            // Clean the line
            let cleanLine = stripAnsi(line.trim());

            // // Skip empty lines
            // if (!cleanLine) return;

            // Format test results
            if (cleanLine.startsWith('✓')) {
                cleanLine = '✓ ' + cleanLine.substring(1).trim();
            }

            formatted.push(cleanLine);
        });

        return formatted.join('\n');
    };

    // Create test_reports directory if it doesn't exist

    const reportDirPath = path.join(taskId, reportDir);
    if (!fs.existsSync(reportDirPath)) {
        fs.mkdirSync(reportDirPath, { recursive: true });
    }

    // Clean and format the content
    const formattedContent = formatTestResults(content);

    // Write to file (overwrite instead of append to avoid duplicates)
    const reportPath = path.join(reportDirPath, `${filename}_report.md`);
    fs.writeFileSync(reportPath, formattedContent + '\n\n');
}

function convertJsxToJs(directoryPath) {
    // Will store list of converted files
    const convertedFiles = [];

    try {
        const files = fs.readdirSync(directoryPath);

        // Find and process all jsx and txt files
        for (const file of files) {
            if (file.endsWith('.jsx') || file.endsWith('.txt')) {
                // Get base name without any extension
                const baseName = path.basename(file, path.extname(file));
                const originalPath = path.join(directoryPath, file);
                const jsPath = path.join(directoryPath, `${baseName}.js`);

                // Remove existing .js file if it exists
                if (fs.existsSync(jsPath)) {
                    console.log(`Removing existing file: ${baseName}.js`);
                    fs.unlinkSync(jsPath);
                }

                // Rename file to .js
                console.log(`Converting ${file} to ${baseName}.js`);
                fs.renameSync(originalPath, jsPath);
                convertedFiles.push(baseName);
            }
        }

        return convertedFiles;

    } catch (error) {
        console.error('Error converting files to JS:', error);
        return convertedFiles;
    }
}