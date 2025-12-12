/**
 * Test utilities shared between unit tests and E2E tests
 */

/**
 * Generates a secure password for testing
 * 
 * SECURITY: S2245 - Using pseudorandom number generators (PRNGs) is security-sensitive.
 * This function uses Math.random() which is safe in this context because:
 * 1. It's only used for generating test passwords in test environments
 * 2. The generated passwords are not used for cryptographic purposes
 * 3. They are not used for security-sensitive operations (tokens, keys, etc.)
 * 4. The randomness is sufficient for test data uniqueness
 * 
 * For production cryptographic needs, use crypto.getRandomValues() instead.
 * 
 * @returns {string} Generated password
 */
export function generatePassword() {
  // NOSONAR S2245 - Math.random() is safe for test password generation
  return `Pass!${Date.now()}-${Math.random().toString(36).slice(2)}` // NOSONAR S2245
}

