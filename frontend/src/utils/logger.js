/**
 * Centralized logging utility
 * Replaces console methods to comply with js.no-console rule
 */

const LOG_LEVELS = {
  ERROR: 'error',
  WARN: 'warn',
  INFO: 'info',
  DEBUG: 'debug'
}

/**
 * Logger class for centralized logging
 */
class Logger {
  constructor() {
    this.enabled = process.env.NODE_ENV !== 'test'
  }

  /**
   * Log error message
   * @param {string} message - Error message
   * @param {Object} context - Additional context
   */
  error(message, context = null) {
    if (!this.enabled) {
      return
    }
    if (context) {
      // eslint-disable-next-line no-console
      } else {
      // eslint-disable-next-line no-console
      }
  }

  /**
   * Log warning message
   * @param {string} message - Warning message
   * @param {Object} context - Additional context
   */
  warn(message, context = null) {
    if (!this.enabled) {
      return
    }
    if (context) {
      // eslint-disable-next-line no-console
      } else {
      // eslint-disable-next-line no-console
      }
  }

  /**
   * Log info message
   * @param {string} message - Info message
   * @param {Object} context - Additional context
   */
  info(message, context = null) {
    if (!this.enabled) {
      return
    }
    if (context) {
      // eslint-disable-next-line no-console
      } else {
      // eslint-disable-next-line no-console
      }
  }

  /**
   * Log debug message
   * @param {string} message - Debug message
   * @param {Object} context - Additional context
   */
  debug(message, context = null) {
    if (!this.enabled || process.env.NODE_ENV === 'production') {
      return
    }
    if (context) {
      // eslint-disable-next-line no-console
      } else {
      // eslint-disable-next-line no-console
      }
  }
}

export const logger = new Logger()
export { LOG_LEVELS }

