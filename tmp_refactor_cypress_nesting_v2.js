#!/usr/bin/env node
/**
 * Script to automatically refactor deeply nested Cypress tests
 * Reduces nesting depth by extracting helper functions
 * Addresses SonarQube rule javascript:S2004
 */
const fs = require('fs');
const path = require('path');

const CYPRESS_DIR = path.join(__dirname, 'frontend/cypress/e2e');

/**
 * Refactor a single test file
 */
function refactorFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;
  const originalContent = content;
  
  // Step 1: Check if file needs helper function
  // Look for pattern: for (const selector of X) where X is an array variable
  const hasForLoopPattern = /for\s*\(const\s+selector\s+of\s+\w+\)/.test(content);
  const hasHelper = content.includes('const verifySelectorsExist');
  
  // Step 2: Add helper function if needed
  if (hasForLoopPattern && !hasHelper) {
    const helperFunction = `
  // Helper functions to reduce nesting depth
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => {
    for (const selector of selectors) {
      if ($context.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
      }
    }
  }

`;
    
    // Insert after beforeEach
    const beforeEachMatch = content.match(/(beforeEach\(\(\)\s*=>\s*\{[\s\S]*?\}\s*\))/);
    if (beforeEachMatch) {
      content = content.replace(beforeEachMatch[0], beforeEachMatch[0] + helperFunction);
      modified = true;
    } else {
      // Insert after first describe
      const firstDescribe = content.match(/(describe\([^)]+\)\s*\{)/);
      if (firstDescribe) {
        content = content.replace(firstDescribe[0], firstDescribe[0] + helperFunction);
        modified = true;
      }
    }
  }
  
  // Step 3: Replace selector loops with helper function (only if helper exists)
  if (content.includes('verifySelectorsExist')) {
    // Pattern: const X = [array] followed by for loop with if check
    // More flexible - works with any variable name, not just "Selectors"
    // Match multiline arrays and the for loop that follows
    const pattern = /(const\s+(\w+)\s*=\s*\[[\s\S]*?\])[\s\n]+for\s*\(const\s+selector\s+of\s+\2\)\s*\{[\s\n\s]*if\s*\(\$(\w+)\.find\(selector\)\.length\s*>\s*0\)\s*\{[\s\n\s]*cy\.get\(selector(?:,\s*\{\s*timeout:\s*(\d+)\s*\})?\)\.should\('exist'\)[\s\n\s]*\}[\s\n\s]*\}/g;
    
    let newContent = content;
    let matchFound = false;
    
    newContent = newContent.replace(pattern, (match, selectorsDecl, selectorsName, contextVar, timeout) => {
      matchFound = true;
      const timeoutValue = timeout || '3000';
      // Get indentation from first line of selectors declaration
      const firstLine = selectorsDecl.split('\n')[0];
      const indent = firstLine.match(/^(\s*)/)?.[1] || '          ';
      return `${selectorsDecl}\n${indent}verifySelectorsExist(${selectorsName}, $${contextVar}, ${timeoutValue})`;
    });
    
    if (matchFound) {
      content = newContent;
      modified = true;
    }
  }
  
  if (modified && content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
    return true;
  }
  
  return false;
}

/**
 * Find all Cypress test files
 */
function findCypressFiles(dir) {
  const files = [];
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        files.push(...findCypressFiles(fullPath));
      } else if (entry.isFile() && entry.name.endsWith('.cy.js')) {
        files.push(fullPath);
      }
    }
  } catch (error) {
    console.error(`Error reading directory ${dir}:`, error.message);
  }
  
  return files;
}

/**
 * Main execution
 */
function main() {
  console.log('Finding Cypress test files...');
  const files = findCypressFiles(CYPRESS_DIR);
  console.log(`Found ${files.length} Cypress test files\n`);
  
  let fixedCount = 0;
  const fixedFiles = [];
  let processedCount = 0;
  
  for (const file of files) {
    processedCount++;
    try {
      const relativePath = path.relative(process.cwd(), file);
      process.stdout.write(`Processing [${processedCount}/${files.length}] ${relativePath}... `);
      
      if (refactorFile(file)) {
        console.log('✓ Refactored');
        fixedFiles.push(relativePath);
        fixedCount++;
      } else {
        console.log('○ No changes needed');
      }
    } catch (error) {
      console.log(`✗ Error: ${error.message}`);
    }
  }
  
  console.log(`\n=== Summary ===`);
  console.log(`Files processed: ${files.length}`);
  console.log(`Files refactored: ${fixedCount}`);
  
  if (fixedFiles.length > 0) {
    console.log(`\nRefactored files:`);
    fixedFiles.forEach(file => console.log(`  - ${file}`));
  }
  
  console.log('\n⚠️  Note: This script performs basic refactoring.');
  console.log('Please review the changes and test your Cypress tests before committing.');
}

if (require.main === module) {
  main();
}

module.exports = { refactorFile, findCypressFiles };

