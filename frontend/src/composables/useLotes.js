/**
 * Composable for lotes management
 * Consolidates CRUD operations, permissions, and related data loading
 */
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotifications } from '@/composables/useNotifications'
import * as lotesApi from '@/services/lotesApi'
import { useDateFormatting } from './useDateFormatting'

/**
 * Main useLotes composable
 * @param {Object} options - Configuration options
 * @returns {Object} Lotes composable methods and state
 */
export function useLotes(options = {}) {
  const authStore = useAuthStore()
  const { showSuccess, showError } = useNotifications()
  const { formatDate } = useDateFormatting()
  
  // State
  const loading = ref(false)
  const error = ref(null)
  const lote = ref(null)
  const lotes = ref([])
  const finca = ref(null)
  const analisis = ref([])
  
  // Computed
  const isAdmin = computed(() => authStore.userRole === 'admin')
  const isFarmer = computed(() => authStore.userRole === 'farmer' || authStore.userRole === 'agricultor')
  
  /**
   * Check if user can edit lote
   * @param {Object} loteData - Lote data
   * @returns {boolean} Can edit
   */
  const canEdit = (loteData) => {
    if (!loteData) return false
    if (isAdmin.value) return true
    if (isFarmer.value && loteData.finca) {
      const fincaData = typeof loteData.finca === 'object' ? loteData.finca : finca.value
      if (fincaData) {
        return fincaData.agricultor === authStore.user?.id || fincaData.agricultor_id === authStore.user?.id
      }
    }
    return false
  }
  
  /**
   * Check if user can delete lote
   * @param {Object} loteData - Lote data
   * @returns {boolean} Can delete
   */
  const canDelete = (loteData) => {
    return canEdit(loteData)
  }
  
  /**
   * Check if user can view lote
   * @param {Object} loteData - Lote data
   * @returns {boolean} Can view
   */
  const canView = (loteData) => {
    // View permission is the same as edit permission
    return canEdit(loteData)
  }
  
  /**
   * Load lotes list
   * @param {Object} params - Filter and pagination parameters
   * @returns {Promise<Array>} List of lotes
   */
  const loadLotes = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await lotesApi.getLotes(params)
      lotes.value = Array.isArray(data) ? data : (data?.results || [])
      
      return lotes.value
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al cargar los lotes'
      error.value = errorMessage
      
      showError(errorMessage)
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Load single lote by ID
   * @param {number} loteId - Lote ID
   * @returns {Promise<Object>} Lote data
   */
  const loadLote = async (loteId) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await lotesApi.getLoteById(loteId)
      lote.value = data
      
      // Load finca if included or referenced
      if (data.finca) {
        if (typeof data.finca === 'object') {
          finca.value = data.finca
        } else {
          // Load finca separately if only ID provided
          await loadFinca(data.finca)
        }
      }
      
      return data
    } catch (err) {
      let errorMessage = 'Error al cargar el lote'
      
      // Check for network/connection errors
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error' || err.message?.includes('CONNECTION_REFUSED')) {
        errorMessage = 'No se pudo conectar al servidor. Asegúrate de que el backend esté corriendo en http://localhost:8000'
      } else if (err.response) {
        if (err.response.status === 500) {
          errorMessage = err.response.data?.error || err.response.data?.detail || 'Error interno del servidor. Por favor, intenta nuevamente más tarde.'
        } else if (err.response.data?.detail) {
          errorMessage = err.response.data.detail
        } else if (err.response.data?.error) {
          errorMessage = err.response.data.error
        } else {
          errorMessage = `Error ${err.response.status}: ${err.response.statusText}`
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      error.value = errorMessage
      showError(errorMessage)
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Load finca for lote
   * @param {number} fincaId - Finca ID
   * @returns {Promise<Object>} Finca data
   */
  const loadFinca = async (fincaId) => {
    try {
      const { getFincaById } = await import('@/services/fincasApi')
      finca.value = await getFincaById(fincaId)
      return finca.value
    } catch (err) {
      throw err
    }
  }
  
  /**
   * Create lote
   * @param {Object} loteData - Lote data
   * @returns {Promise<Object>} Created lote
   */
  const createLote = async (loteData) => {
    try {
      loading.value = true
      error.value = null
      
      // Validate data
      const validation = lotesApi.validateLoteData(loteData)
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '))
      }
      
      // Format data
      const formatted = lotesApi.formatLoteData(loteData)
      
      const result = await lotesApi.createLote(formatted)
      
      showSuccess('El lote ha sido creado exitosamente')
      
      return result
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al crear el lote'
      error.value = errorMessage
      
      showError(errorMessage)
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Update lote
   * @param {number} loteId - Lote ID
   * @param {Object} loteData - Updated lote data
   * @returns {Promise<Object>} Updated lote
   */
  const updateLote = async (loteId, loteData) => {
    try {
      loading.value = true
      error.value = null
      
      // Validate data
      const validation = lotesApi.validateLoteData(loteData)
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '))
      }
      
      // Format data
      const formatted = lotesApi.formatLoteData(loteData)
      
      const result = await lotesApi.updateLote(loteId, formatted)
      
      // Update local state
      if (lote.value?.id === loteId) {
        lote.value = result
      }
      
      showSuccess('El lote ha sido actualizado exitosamente')
      
      return result
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al actualizar el lote'
      error.value = errorMessage
      
      showError(errorMessage)
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Delete lote
   * @param {number} loteId - Lote ID
   * @returns {Promise<boolean>} Success status
   */
  const deleteLote = async (loteId) => {
    try {
      loading.value = true
      error.value = null
      
      await lotesApi.deleteLote(loteId)
      
      // Remove from local state
      lotes.value = lotes.value.filter(l => l.id !== loteId)
      if (lote.value?.id === loteId) {
        lote.value = null
      }
      
      showSuccess('El lote ha sido eliminado exitosamente')
      
      return true
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al eliminar el lote'
      error.value = errorMessage
      
      showError(errorMessage)
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Load lote statistics
   * @param {number} loteId - Lote ID
   * @returns {Promise<Object>} Statistics
   */
  const loadStats = async (loteId) => {
    try {
      return await lotesApi.getLoteStats(loteId)
    } catch (err) {
      throw err
    }
  }
  
  /**
   * Load analisis for lote
   * @param {number} loteId - Lote ID
   * @param {Object} params - Filter parameters
   * @returns {Promise<Array>} List of analisis
   */
  const loadAnalisis = async (loteId, params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      // This would call the analisis API - placeholder for now
      // const data = await analisisApi.getAnalisisByLote(loteId, params)
      // analisis.value = Array.isArray(data) ? data : (data?.results || [])
      
      return analisis.value
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al cargar los análisis'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Clear error state
   */
  const clearError = () => {
    error.value = null
  }
  
  return {
    // State
    loading,
    error,
    lote,
    lotes,
    finca,
    analisis,
    
    // Computed
    isAdmin,
    isFarmer,
    
    // Methods
    canEdit,
    canDelete,
    canView,
    loadLotes,
    loadLote,
    loadFinca,
    createLote,
    updateLote,
    deleteLote,
    loadStats,
    loadAnalisis,
    clearError,
    
    // Utilities
    formatDate,
    
    // API helpers
    getVariedadesCacao: lotesApi.getVariedadesCacao,
    getEstadosLote: lotesApi.getEstadosLote,
    validateLoteData: lotesApi.validateLoteData,
    formatLoteData: lotesApi.formatLoteData
  }
}

