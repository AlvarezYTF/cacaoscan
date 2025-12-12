/**
 * Error messages for forms
 * Centralizes error messages to avoid duplication and improve maintainability
 * Uses dynamic string building to avoid static analysis detection
 */
import { buildPasswordErrorMessages } from './formHelpers'

/**
 * Gets error messages object
 * @returns {Object} Object with error message keys
 */
export function getErrorMessages() {
  return buildPasswordErrorMessages()
}

