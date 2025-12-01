#!/usr/bin/env node
/**
 * Script to automatically refactor deeply nested Cypress tests
 * Reduces nesting depth by extracting helper functions
 * Addresses SonarQube rule javascript:S2004
 */
const fs = require('fs');
const path = require('path');

const CYPRESS_DIR = path.join(__dirname, 'frontend/cypress/e2e');

// Common patterns to refactor
const PATTERNS = {
  // Pattern: cy.get('body').then(($body) => { if ($body.find(...).length > 0) { ... } })
  bodyThenFind: {
    regex: /cy\.get\(['"]body['"]\)\.then\(\(\$body\)\s*=>\s*\{[\s\S]*?if\s*\(\$body\.find\([^)]+\)\.length\s*>\s*0\)/g,
    replacement: (match, p1) => {
      // Extract the selector and action
      const selectorMatch = match.match(/find\(([^)]+)\)/);
      if (selectorMatch) {
        const selector = selectorMatch[1];
        // This is complex, we'll handle it in the main function
        return match;
      }
      return match;
    }
  }
};

/**
 * Extract helper functions from a test file
 */
function extractHelperFunctions(content) {
  const helpers = [];
  
  // Find common patterns that can be extracted
  // Pattern 1: Repeated selector verification
  const selectorVerificationPattern = /const\s+(\w+Selectors)\s*=\s*\[[\s\S]*?\][\s\S]*?for\s*\(const\s+\w+\s+of\s+\1\)\s*\{[\s\S]*?if\s*\(\$[^)]+\.find\([^)]+\)\.length\s*>\s*0\)\s*\{[\s\S]*?cy\.get\([^)]+\)\.should\('exist'\)/g;
  
  // Pattern 2: Click if exists pattern
  const clickIfExistsPattern = /cy\.get\(['"]body['"]\)\.then\(\(\$body\)\s*=>\s*\{[\s\S]*?if\s*\(\$body\.find\(([^)]+)\)\.length\s*>\s*0\)\s*\{[\s\S]*?cy\.get\([^)]+\)\.first\(\)\.click\(\{?\s*force:\s*true\s*\}?\)/g;
  
  return helpers;
}

/**
 * Refactor a single test file
 */
function refactorFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;
  const originalContent = content;
  
  // Step 1: Add helper functions if needed
  const needsHelper = content.match(/for\s*\(const\s+\w+\s+of\s+\w+Selectors\)/);
  const hasHelper = content.includes('const verifySelectorsExist');
  
  if (needsHelper && !hasHelper) {
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
  
  // Step 2: Replace selector verification loops with helper function
  // Pattern 1: const selectors = [...] followed by for loop with if check
  if (content.includes('verifySelectorsExist')) {
    // Pattern with if check: const XSelectors = [...] for... if ($var.find(selector)...)
    const selectorLoopWithIfPattern = /(const\s+(\w+Selectors)\s*=\s*\[[\s\S]*?\])[\s\n]+for\s*\(const\s+selector\s+of\s+\2\)\s*\{[\s\S]*?if\s*\(\$(\w+)\.find\(selector\)\.length\s*>\s*0\)\s*\{[\s\S]*?cy\.get\(selector(?:,\s*\{\s*timeout:\s*(\d+)\s*\})?\)\.should\('exist'\)[\s\S]*?\}[\s\S]*?\}/g;
    
    let newContent = content;
    let hasReplacement = false;
    
    newContent = newContent.replace(selectorLoopWithIfPattern, (match, selectorsDecl, selectorsName, contextVar, timeout) => {
      hasReplacement = true;
      const timeoutValue = timeout || '3000';
      // Extract indentation from the const declaration
      const lines = selectorsDecl.split('\n');
      const firstLine = lines[0];
      const indent = firstLine.match(/^(\s*)/)?.[1] || '          ';
      return `${selectorsDecl}\n${indent}verifySelectorsExist(${selectorsName}, $${contextVar}, ${timeoutValue})`;
    });
    
    // Pattern 2: const selectors = [...] followed by for loop without if check (simpler case)
    // This pattern is less common but exists in some files
    const selectorLoopSimplePattern = /(const\s+(\w+Selectors)\s*=\s*\[[\s\S]*?\])[\s\n]+for\s*\(const\s+selector\s+of\s+\2\)\s*\{[\s\S]*?cy\.get\(selector(?:,\s*\{\s*timeout:\s*(\d+)\s*\})?\)\.should\('exist'\)[\s\S]*?\}/g;
    
    newContent = newContent.replace(selectorLoopSimplePattern, (match, selectorsDecl, selectorsName, timeout) => {
      // For simple patterns without if check, we need to check if selector exists first
      // But this is trickier - we'll skip these for now as they need context variable
      return match;
    });
    
    if (hasReplacement) {
      content = newContent;
      modified = true;
    }
  }
  
  // Step 3: Simplify nested body.then() patterns
  // Pattern: cy.get('body').then(($body) => { if ($body.find(...).length > 0) { ... } })
  // This is complex and requires careful handling, so we'll do it manually for critical cases
  
  if (modified) {
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
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...findCypressFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.cy.js')) {
      files.push(fullPath);
    }
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

