#!/usr/bin/env node
/**
 * Simple script to refactor Cypress tests - direct pattern replacement
 */
const fs = require('fs');
const path = require('path');

const CYPRESS_DIR = path.join(__dirname, 'frontend/cypress/e2e');

function refactorFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  const originalContent = content;
  let modified = false;
  
  // Add helper if needed
  const needsHelper = /for\s*\(const\s+selector\s+of\s+\w+\)/.test(content);
  const hasHelper = content.includes('verifySelectorsExist');
  
  if (needsHelper && !hasHelper) {
    const helper = `
  // Helper functions to reduce nesting depth
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => {
    for (const selector of selectors) {
      if ($context.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
      }
    }
  }

`;
    const beforeEachMatch = content.match(/(beforeEach\(\(\)\s*=>\s*\{[\s\S]*?\}\s*\))/);
    if (beforeEachMatch) {
      content = content.replace(beforeEachMatch[0], beforeEachMatch[0] + helper);
      modified = true;
    }
  }
  
  // Simple replacement: find exact pattern and replace
  if (content.includes('verifySelectorsExist')) {
    // Pattern: const X = [...]\nfor (const selector of X) { if ($Y.find(selector)... cy.get(selector, {timeout: Z}).should('exist') } }
    const simplePattern = /(const\s+(\w+)\s*=\s*\[[^\]]*(?:\n[^\]]*)*\])\s*\n\s*for\s*\(const\s+selector\s+of\s+\2\)\s*\{\s*\n\s*if\s*\(\$(\w+)\.find\(selector\)\.length\s*>\s*0\)\s*\{\s*\n\s*cy\.get\(selector,\s*\{\s*timeout:\s*(\d+)\s*\}\)\.should\('exist'\)\s*\n\s*\}\s*\n\s*\}/g;
    
    content = content.replace(simplePattern, (match, decl, name, ctx, timeout) => {
      const indent = decl.match(/^(\s*)/)?.[1] || '          ';
      return `${decl}\n${indent}verifySelectorsExist(${name}, $${ctx}, ${timeout})`;
    });
    
    if (content !== originalContent) modified = true;
  }
  
  if (modified) {
    fs.writeFileSync(filePath, content, 'utf8');
    return true;
  }
  return false;
}

function findFiles(dir) {
  const files = [];
  try {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        files.push(...findFiles(fullPath));
      } else if (entry.name.endsWith('.cy.js')) {
        files.push(fullPath);
      }
    }
  } catch (e) {}
  return files;
}

// Main
const files = findFiles(CYPRESS_DIR);
let count = 0;
for (const file of files) {
  if (refactorFile(file)) {
    console.log(`✓ ${path.relative(process.cwd(), file)}`);
    count++;
  }
}
console.log(`\nRefactored ${count} files`);

