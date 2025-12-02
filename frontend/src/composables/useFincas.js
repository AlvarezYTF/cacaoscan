/**
 * Composable for fincas operations
 * Centralizes fincas management logic
 */
import { ref, computed } from 'vue'
import { getFincas, getFincaById, createFinca, updateFinca, deleteFinca } from '@/services/fincasApi'
import { handleApiError } from '@/services/apiErrorHandler'

/**
 * Create fincas composable
 * @param {Object} options - Options
 * @param {Function} options.onFincaCreate - Callback when finca is created
 * @param {Function} options.onFincaUpdate - Callback when finca is updated
 * @param {Function} options.onFincaDelete - Callback when finca is deleted
 * @returns {Object} Fincas state and methods
 */
export function useFincas(options = {}) {
  const {
    onFincaCreate = null,
    onFincaUpdate = null,
    onFincaDelete = null
  } = options

  // State
  const fincas = ref([])
  const currentFinca = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const filters = ref({})
  const pagination = ref({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    itemsPerPage: 20
  })

  // Computed
  const hasFincas = computed(() => fincas.value.length > 0)
  const hasCurrentFinca = computed(() => currentFinca.value !== null)
  const hasError = computed(() => error.value !== null)

  /**
   * Load fincas list
   * @param {Object} filterParams - Filter parameters
   * @param {number} page - Page number
   * @param {number} pageSize - Page size
   * @returns {Promise<Object>} Response data
   */
  const loadFincas = async (filterParams = {}, page = 1, pageSize = 20) => {
    isLoading.value = true
    error.value = null

    try {
      const params = {
        ...filterParams,
        page,
        page_size: pageSize
      }

      const response = await getFincas(params)

      if (page === 1) {
        fincas.value = response.results || []
      } else {
        fincas.value = [...fincas.value, ...(response.results || [])]
      }

      pagination.value = {
        currentPage: page,
        totalPages: Math.ceil((response.count || 0) / pageSize),
        totalItems: response.count || 0,
        itemsPerPage: pageSize
      }

      filters.value = { ...filterParams }

      return response
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load single finca details
   * @param {number} fincaId - Finca ID
   * @returns {Promise<Object>} Finca data
   */
  const loadFinca = async (fincaId) => {
    isLoading.value = true
    error.value = null

    try {
      const fincaData = await getFincaById(fincaId)
      currentFinca.value = fincaData
      return fincaData
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create finca
   * @param {Object} fincaData - Finca data
   * @returns {Promise<Object>} Created finca
   */
  const create = async (fincaData) => {
    isLoading.value = true
    error.value = null

    try {
      const newFinca = await createFinca(fincaData)

      // Add to local state
      fincas.value.unshift(newFinca)
      pagination.value.totalItems += 1

      if (onFincaCreate && typeof onFincaCreate === 'function') {
        onFincaCreate(newFinca)
      }

      return newFinca
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update finca
   * @param {number} fincaId - Finca ID
   * @param {Object} updateData - Data to update
   * @returns {Promise<Object>} Updated finca
   */
  const update = async (fincaId, updateData) => {
    isLoading.value = true
    error.value = null

    try {
      const updatedFinca = await updateFinca(fincaId, updateData)

      // Update in local state
      const index = fincas.value.findIndex(f => f.id === fincaId)
      if (index !== -1) {
        fincas.value[index] = updatedFinca
      }

      if (currentFinca.value?.id === fincaId) {
        currentFinca.value = updatedFinca
      }

      if (onFincaUpdate && typeof onFincaUpdate === 'function') {
        onFincaUpdate(updatedFinca)
      }

      return updatedFinca
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete finca
   * @param {number} fincaId - Finca ID
   * @returns {Promise<void>}
   */
  const remove = async (fincaId) => {
    isLoading.value = true
    error.value = null

    try {
      await deleteFinca(fincaId)

      // Remove from local state
      fincas.value = fincas.value.filter(f => f.id !== fincaId)

      if (currentFinca.value?.id === fincaId) {
        currentFinca.value = null
      }

      // Update pagination
      pagination.value.totalItems = Math.max(0, pagination.value.totalItems - 1)

      if (onFincaDelete && typeof onFincaDelete === 'function') {
        onFincaDelete(fincaId)
      }
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Set filters
   * @param {Object} newFilters - New filter values
   */
  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  /**
   * Clear filters
   */
  const clearFilters = () => {
    filters.value = {}
  }

  /**
   * Set current finca
   * @param {Object} finca - Finca object
   */
  const setCurrentFinca = (finca) => {
    currentFinca.value = finca
  }

  /**
   * Clear current finca
   */
  const clearCurrentFinca = () => {
    currentFinca.value = null
  }

  /**
   * Reset state
   */
  const reset = () => {
    fincas.value = []
    currentFinca.value = null
    isLoading.value = false
    error.value = null
    filters.value = {}
    pagination.value = {
      currentPage: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 20
    }
  }

  /**
   * Clear error
   */
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    fincas,
    currentFinca,
    isLoading,
    error,
    filters,
    pagination,

    // Computed
    hasFincas,
    hasCurrentFinca,
    hasError,

    // Methods
    loadFincas,
    loadFinca,
    create,
    createFinca: create,
    update,
    updateFinca: update,
    remove,
    deleteFinca: remove,
    setFilters,
    clearFilters,
    setCurrentFinca,
    clearCurrentFinca,
    reset,
    clearError
  }
}
