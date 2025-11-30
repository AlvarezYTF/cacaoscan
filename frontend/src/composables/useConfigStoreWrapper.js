/**
 * Composable wrapper for config store with domain-specific helpers
 */
import { computed } from 'vue'
import { useConfigStore } from '@/stores/config'

/**
 * Validates domain labels
 * @param {string[]} labels - Domain labels to validate
 * @returns {boolean} True if all labels are valid
 */
const validateDomainLabels = (labels) => {
  for (const label of labels) {
    if (label.length === 0 || label.length > 63) {
      return false
    }
    if (!/^[A-Za-z0-9-]+$/.test(label)) {
      return false
    }
    if (label.startsWith('-') || label.endsWith('-')) {
      return false
    }
  }
  return true
}

/**
 * Validates local part of email
 * @param {string} local - Local part to validate
 * @returns {boolean} True if local part is valid
 */
const validateLocalPart = (local) => {
  if (local.length === 0 || local.length > 64) {
    return false
  }
  if (/\s/.test(local)) {
    return false
  }
  if (!/^[A-Za-z0-9!#$%&'*+\-/=?^_`{|}~.]+$/.test(local)) {
    return false
  }
  if (local.includes('..')) {
    return false
  }
  return true
}

/**
 * Validates domain part of email
 * @param {string} domain - Domain part to validate
 * @returns {boolean} True if domain part is valid
 */
const validateDomainPart = (domain) => {
  if (domain.length === 0 || domain.length > 255) {
    return false
  }
  if (/\s/.test(domain)) {
    return false
  }
  if (!domain.includes('.')) {
    return false
  }
  if (domain.includes('..')) {
    return false
  }
  const labels = domain.split('.')
  return validateDomainLabels(labels)
}

/**
 * Secure email validation function that prevents ReDoS attacks
 * Uses bounded checks instead of complex regex to avoid catastrophic backtracking
 * 
 * SECURITY: This validation avoids ReDoS by:
 * - Using length bounds before regex checks
 * - Splitting validation into multiple simple checks
 * - Using simple regex patterns without nested quantifiers
 * - Bounding all regex operations to prevent exponential backtracking
 * 
 * @param {string} email - Email to validate
 * @returns {boolean} True if email is valid
 */
const isValidEmailSecure = (email) => {
  if (!email || typeof email !== 'string') {
    return false
  }
  if (email.length > 320) {
    return false
  }

  const parts = email.split('@')
  if (parts.length !== 2) {
    return false
  }

  const [local, domain] = parts
  return validateLocalPart(local) && validateDomainPart(domain)
}

/**
 * Provides config store wrapper with helpers
 * @returns {Object} Config store wrapper with helpers
 */
export function useConfigStoreWrapper() {
  const store = useConfigStore()

  /**
   * Gets a config value by key
   * @param {string} key - Config key (e.g., 'general.nombre_sistema', 'security.session_timeout')
   * @returns {*} Config value
   */
  const getConfig = (key) => {
    const keys = key.split('.')
    let value = store

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k]
      } else {
        return undefined
      }
    }

    return value
  }

  /**
   * Sets a config value by key
   * @param {string} key - Config key
   * @param {*} value - Config value
   * @returns {Promise<void>}
   */
  const setConfig = async (key, value) => {
    const keys = key.split('.')
    const lastKey = keys.pop()
    const section = keys.join('.')

    if (section === 'general') {
      await store.updateGeneralConfig({ [lastKey]: value })
    } else if (section === 'security') {
      await store.updateSecurityConfig({ [lastKey]: value })
    } else if (section === 'ml') {
      await store.updateMLConfig({ [lastKey]: value })
    } else {
      throw new Error(`Unknown config section: ${section}`)
    }
  }

  /**
   * Resets config to defaults
   * @param {string} key - Optional config key to reset (if not provided, resets all)
   * @returns {Promise<void>}
   */
  const resetConfig = async (key = null) => {
    if (key) {
      const keys = key.split('.')
      const section = keys[0]

      if (section === 'general') {
        await store.resetGeneralConfig()
      } else if (section === 'security') {
        await store.resetSecurityConfig()
      } else if (section === 'ml') {
        await store.resetMLConfig()
      }
    } else {
      await store.resetAllConfig()
    }
  }

  /**
   * Saves all config changes
   * @returns {Promise<void>}
   */
  const saveConfig = async () => {
    await store.saveAllConfig()
  }

  /**
   * Validates a config value
   * @param {string} key - Config key
   * @param {*} value - Config value to validate
   * @returns {string|null} Error message or null if valid
   */
  const validateConfig = (key, value) => {
    // Validation rules
    const validations = {
      'general.nombre_sistema': (val) => {
        if (!val || typeof val !== 'string' || val.trim().length === 0) {
          return 'El nombre del sistema es requerido'
        }
        if (val.length > 100) {
          return 'El nombre del sistema no puede exceder 100 caracteres'
        }
        return null
      },
      'general.email_contacto': (val) => {
        if (!val || typeof val !== 'string') {
          return 'El email de contacto es requerido'
        }
        // Use secure email validation to prevent ReDoS attacks
        // This validation uses bounded checks instead of vulnerable regex patterns
        // SonarQube S5852: ReDoS protection - regex operations are bounded by length checks
        if (!isValidEmailSecure(val)) {
          return 'El email de contacto no es válido'
        }
        return null
      },
      'security.session_timeout': (val) => {
        const num = Number.parseInt(val, 10)
        if (Number.isNaN(num) || num < 5 || num > 480) {
          return 'El tiempo de sesión debe estar entre 5 y 480 minutos'
        }
        return null
      },
      'security.login_attempts': (val) => {
        const num = Number.parseInt(val, 10)
        if (Number.isNaN(num) || num < 3 || num > 10) {
          return 'Los intentos de login deben estar entre 3 y 10'
        }
        return null
      }
    }

    const validator = validations[key]
    if (validator) {
      return validator(value)
    }

    return null
  }

  return {
    // Store state (computed for reactivity)
    general: computed(() => store.general),
    security: computed(() => store.security),
    ml: computed(() => store.ml),
    system: computed(() => store.system),
    loading: computed(() => store.loading),
    lastUpdate: computed(() => store.lastUpdate),

    // Helper methods
    getConfig,
    setConfig,
    resetConfig,
    saveConfig,
    validateConfig,

    // Store methods (for advanced usage)
    store
  }
}

