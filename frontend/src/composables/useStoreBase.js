/**
 * Base composable for Pinia stores
 * Provides common state and methods for all stores
 */
import { ref, computed } from 'vue'

/**
 * Create base store state and methods
 * @param {Object} options - Options
 * @param {Object} options.initialState - Initial state values
 * @returns {Object} Store state and methods
 */
export function useStoreBase(options = {}) {
  const {
    initialState = {}
  } = options

  // Common state
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)

  /**
   * Set loading state
   * @param {boolean} value - Loading state
   */
  const setLoading = (value) => {
    loading.value = value
  }

  /**
   * Set error
   * @param {string|Error|null} errorValue - Error value
   */
  const setError = (errorValue) => {
    if (errorValue === null || errorValue === undefined) {
      error.value = null
      return
    }

    if (errorValue instanceof Error) {
      error.value = errorValue.message
    } else {
      error.value = errorValue
    }
  }

  /**
   * Clear error
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * Reset store state
   * @param {Object} newState - New state values
   */
  const resetState = (newState = {}) => {
    loading.value = false
    error.value = null

    // Reset custom state if provided
    for (const [key, value] of Object.entries(newState)) {
      if (initialState[key] !== undefined) {
        initialState[key] = value
      }
    }
  }

  /**
   * Execute async action with loading and error handling
   * @param {Function} action - Async action function
   * @param {Object} options - Options
   * @returns {Promise<any>} Action result
   */
  const executeAction = async (action, options = {}) => {
    const {
      onError = null,
      onSuccess = null,
      clearErrorOnStart = true
    } = options

    if (clearErrorOnStart) {
      clearError()
    }

    setLoading(true)

    try {
      const result = await action()
      
      if (onSuccess && typeof onSuccess === 'function') {
        onSuccess(result)
      }

      return result
    } catch (err) {
      setError(err)

      if (onError && typeof onError === 'function') {
        onError(err)
      }

      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    // State
    loading,
    error,

    // Computed
    isLoading,
    hasError,

    // Methods
    setLoading,
    setError,
    clearError,
    resetState,
    executeAction
  }
}

