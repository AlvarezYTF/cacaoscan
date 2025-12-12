/**
 * Configuration for BasePreferencesWrapper components
 * Reduces duplication between BaseScanPreferences and BaseVisualSettings
 */

/**
 * Icon paths for different preference types
 */
export const PREFERENCE_ICONS = {
  SCAN: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  VISUAL: 'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01'
}

/**
 * Default configurations for different preference types
 */
export const PREFERENCE_CONFIGS = {
  SCAN: {
    title: 'Preferencias de Escaneo',
    saveButtonText: 'Guardar Preferencias',
    contentSlotName: 'preferences'
  },
  VISUAL: {
    title: 'Ajustes Visuales',
    saveButtonText: 'Guardar Ajustes',
    contentSlotName: 'settings'
  }
}

/**
 * Creates props definition with default values for a preference type
 * @param {string} type - Type of preference (SCAN or VISUAL)
 * @returns {Object} Props definition object
 */
export function createPreferenceWrapperProps(type) {
  const config = PREFERENCE_CONFIGS[type]
  if (!config) {
    throw new Error(`Invalid preference type: ${type}. Must be SCAN or VISUAL.`)
  }

  return {
    modelValue: {
      type: Object,
      required: true,
      default: () => ({})
    },
    title: {
      type: String,
      default: config.title
    },
    showHeader: {
      type: Boolean,
      default: true
    },
    showActions: {
      type: Boolean,
      default: true
    },
    showSaveButton: {
      type: Boolean,
      default: true
    },
    showResetButton: {
      type: Boolean,
      default: false
    },
    saveButtonText: {
      type: String,
      default: config.saveButtonText
    },
    resetButtonText: {
      type: String,
      default: 'Restablecer'
    },
    containerClass: {
      type: String,
      default: 'bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg'
    }
  }
}

/**
 * Gets icon path for a preference type
 * @param {string} type - Type of preference (SCAN or VISUAL)
 * @returns {string} Icon path
 */
export function getPreferenceIconPath(type) {
  const iconPath = PREFERENCE_ICONS[type]
  if (!iconPath) {
    throw new Error(`Invalid preference type: ${type}. Must be SCAN or VISUAL.`)
  }
  return iconPath
}

/**
 * Gets content slot name for a preference type
 * @param {string} type - Type of preference (SCAN or VISUAL)
 * @returns {string} Content slot name
 */
export function getPreferenceContentSlotName(type) {
  const config = PREFERENCE_CONFIGS[type]
  if (!config) {
    throw new Error(`Invalid preference type: ${type}. Must be SCAN or VISUAL.`)
  }
  return config.contentSlotName
}

