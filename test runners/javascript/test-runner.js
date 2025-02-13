const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const util = require('util');

async function runTests(taskId) {
    const taskDir = path.join(process.cwd(), taskId);
    const testFilePath = path.join(taskDir, 'index.test.js');
    const originalTestContent = fs.readFileSync(testFilePath, 'utf8');
    
     // Match both import patterns: destructured ({ func }) and direct (ClassName)
    const destructuredMatch = originalTestContent.match(/const\s*{([^}]+)}\s*=\s*require\(['"]\.\/[^'"]+['"]\)/);
    const directMatch = originalTestContent.match(/const\s+([^=\s]+)\s*=\s*require\(['"]\.\/[^'"]+['"]\)/);
    
    // Determine the import pattern based on the original test file
    let importPattern;
    if (destructuredMatch) {
        const functionName = destructuredMatch[1].trim();
        importPattern = `const { ${functionName} } = require`;
    } else if (directMatch) {
        const className = directMatch[1].trim();
        importPattern = `const ${className} = require`;
    } else {
        console.error('Could not find require statement in test file');
        process.exit(1);
    }
    
    // Initialize summary object
    const testSummary = {};
    
    // Get all files to test against
    const filesToTest = [];
    
    // Add base_code.js if it exists
    const baseCodePath = path.join(taskDir, 'base_code.js');
    if (fs.existsSync(baseCodePath)) {
        filesToTest.push({
            name: 'base_code',
            path: './base_code.js'
        });
    }
    
    // Add solution.js
    filesToTest.push({
        name: 'solution',
        path: './solution.js'
    });
    
    // Add files from alternate_responses folder
    const altResponsesDir = path.join(taskDir, 'alternate_responses');
    if (fs.existsSync(altResponsesDir)) {
        const altFiles = fs.readdirSync(altResponsesDir)
            .filter(file => file.endsWith('.js'))
            .map(file => ({
                name: file.replace('.js', ''),
                path: './alternate_responses/' + file
            }));
        filesToTest.push(...altFiles);
    }

    console.log(`\n=== Running tests for task ${taskId} ===\n`);
    
    // Run tests for each implementation
    for (const file of filesToTest) {
        console.log(`\nTesting implementation: ${file.name}`);
        console.log('='.repeat(40));
        
        // Modify the import statement in the test file
        const newTestContent = originalTestContent.replace(
            /const\s*(?:{[^}]+}|[^=\s]+)\s*=\s*require\(['"]\.\/[^'"]+['"]\)/,
            `${importPattern}('${file.path}')`
        );
        
        // Write the modified test file
        fs.writeFileSync(testFilePath, newTestContent);
        
        try {
            // Run Jest with --json flag to get detailed test results
            const jsonOutput = execSync(`npx jest ${taskId} --json --colors`, {
                encoding: 'utf8',
                stdio: ['pipe', 'pipe', 'pipe']
            });
            
            const testResults = JSON.parse(jsonOutput);
            const testSuite = testResults.testResults[0];
            
            // Print test results in Jest-like format
            testSuite.assertionResults.forEach(test => {
                const status = test.status === 'passed' 
                    ? '\x1b[32m✓\x1b[0m' 
                    : '\x1b[31m✕\x1b[0m';
                console.log(`${status} ${test.title}`);
                
                if (test.failureMessages && test.failureMessages.length > 0) {
                    console.log('\x1b[31m' + test.failureMessages.join('\n') + '\x1b[0m');
                }
            });
            
            // Store summary information
            const numPassedTests = testResults.numPassedTests;
            const totalTests = testResults.numTotalTests;
            testSummary[file.name] = {
                passed: numPassedTests,
                total: totalTests,
                status: numPassedTests === totalTests ? 'PASSED' : 'FAILED'
            };
            
            // Print suite summary
            console.log('\nTest Suites: ' + (testSuite.status === 'passed' ? '\x1b[32m1 passed\x1b[0m' : '\x1b[31m1 failed\x1b[0m'));
            console.log(`Tests:       ${numPassedTests} passed, ${totalTests - numPassedTests} failed, ${totalTests} total`);
            
        } catch (error) {
            try {
                // Try to parse error output for test results
                const errorOutput = error.stdout ? error.stdout.toString() : '{}';
                const testResults = JSON.parse(errorOutput);
                
                // Store summary even for failed runs
                testSummary[file.name] = {
                    passed: testResults.numPassedTests || 0,
                    total: testResults.numTotalTests || 0,
                    status: 'FAILED'
                };
                
                // Print the error output
                if (error.stderr) {
                    console.error('\x1b[31m' + error.stderr.toString() + '\x1b[0m');
                }
            } catch {
                testSummary[file.name] = {
                    passed: 0,
                    total: 0,
                    status: 'ERROR'
                };
                console.error('\x1b[31mFailed to run tests\x1b[0m');
            }
        }
    }
    
    // Restore the original test file
    fs.writeFileSync(testFilePath, originalTestContent);
    
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

// Get task ID from command line arguments
const taskId = process.argv[2];
if (!taskId) {
    console.error('Please provide a task ID');
    process.exit(1);
}

runTests(taskId).catch(error => {
    console.error('Error running tests:', error);
    process.exit(1);
});