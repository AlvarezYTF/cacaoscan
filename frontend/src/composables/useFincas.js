/**
 * Composable for fincas management
 * Consolidates CRUD operations, permissions, and related data loading
 */
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import * as fincasApi from '@/services/fincasApi'
import { useDateFormatting } from './useDateFormatting'

/**
 * Main useFincas composable
 * @param {Object} options - Configuration options
 * @returns {Object} Fincas composable methods and state
 */
export function useFincas(options = {}) {
  const authStore = useAuthStore()
  const notificationStore = useNotificationStore()
  const { formatDate } = useDateFormatting()
  
  // State
  const loading = ref(false)
  const error = ref(null)
  const finca = ref(null)
  const fincas = ref([])
  const lotes = ref([])
  const analisis = ref([])
  
  // Computed
  const isAdmin = computed(() => authStore.userRole === 'admin')
  const isFarmer = computed(() => authStore.userRole === 'farmer' || authStore.userRole === 'agricultor')
  
  /**
   * Check if user can edit finca
   * @param {Object} fincaData - Finca data
   * @returns {boolean} Can edit
   */
  const canEdit = (fincaData) => {
    if (!fincaData) return false
    if (isAdmin.value) return true
    if (isFarmer.value) {
      return fincaData.agricultor === authStore.user?.id || fincaData.agricultor_id === authStore.user?.id
    }
    return false
  }
  
  /**
   * Check if user can delete finca
   * @param {Object} fincaData - Finca data
   * @returns {boolean} Can delete
   */
  const canDelete = (fincaData) => {
    return canEdit(fincaData)
  }
  
  /**
   * Check if user can view finca
   * @param {Object} fincaData - Finca data
   * @returns {boolean} Can view
   */
  const canView = (fincaData) => {
    if (!fincaData) return false
    if (isAdmin.value) return true
    if (isFarmer.value) {
      return fincaData.agricultor === authStore.user?.id || fincaData.agricultor_id === authStore.user?.id
    }
    return false
  }
  
  /**
   * Load fincas list
   * @param {Object} params - Filter and pagination parameters
   * @returns {Promise<Array>} List of fincas
   */
  const loadFincas = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await fincasApi.getFincas(params)
      fincas.value = Array.isArray(data) ? data : (data?.results || [])
      
      return fincas.value
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al cargar las fincas'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error',
        message: errorMessage
      })
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Load single finca by ID
   * @param {number} fincaId - Finca ID
   * @returns {Promise<Object>} Finca data
   */
  const loadFinca = async (fincaId) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await fincasApi.getFincaById(fincaId)
      finca.value = data
      
      return data
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al cargar la finca'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error',
        message: errorMessage
      })
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Create finca
   * @param {Object} fincaData - Finca data
   * @returns {Promise<Object>} Created finca
   */
  const createFinca = async (fincaData) => {
    try {
      loading.value = true
      error.value = null
      
      // Validate data
      const validation = fincasApi.validateFincaData(fincaData)
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '))
      }
      
      // Format data
      const formatted = fincasApi.formatFincaData(fincaData)
      
      const result = await fincasApi.createFinca(formatted)
      
      notificationStore.addNotification({
        type: 'success',
        title: 'Finca creada',
        message: 'La finca ha sido creada exitosamente'
      })
      
      return result
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al crear la finca'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error',
        message: errorMessage
      })
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Update finca
   * @param {number} fincaId - Finca ID
   * @param {Object} fincaData - Updated finca data
   * @returns {Promise<Object>} Updated finca
   */
  const updateFinca = async (fincaId, fincaData) => {
    try {
      loading.value = true
      error.value = null
      
      // Validate data
      const validation = fincasApi.validateFincaData(fincaData)
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '))
      }
      
      // Format data
      const formatted = fincasApi.formatFincaData(fincaData)
      
      const result = await fincasApi.updateFinca(fincaId, formatted)
      
      // Update local state
      if (finca.value && finca.value.id === fincaId) {
        finca.value = result
      }
      
      notificationStore.addNotification({
        type: 'success',
        title: 'Finca actualizada',
        message: 'La finca ha sido actualizada exitosamente'
      })
      
      return result
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al actualizar la finca'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error',
        message: errorMessage
      })
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Delete (deactivate) finca
   * @param {number} fincaId - Finca ID
   * @returns {Promise<boolean>} Success status
   */
  const deleteFinca = async (fincaId) => {
    try {
      loading.value = true
      error.value = null
      
      await fincasApi.deleteFinca(fincaId)
      
      // Remove from local state
      fincas.value = fincas.value.filter(f => f.id !== fincaId)
      if (finca.value && finca.value.id === fincaId) {
        finca.value = null
      }
      
      notificationStore.addNotification({
        type: 'success',
        title: 'Finca desactivada',
        message: 'La finca ha sido desactivada exitosamente'
      })
      
      return true
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al desactivar la finca'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error',
        message: errorMessage
      })
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Activate finca
   * @param {number} fincaId - Finca ID
   * @returns {Promise<Object>} Activated finca
   */
  const activateFinca = async (fincaId) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await fincasApi.activateFinca(fincaId)
      
      notificationStore.addNotification({
        type: 'success',
        title: 'Finca reactivada',
        message: 'La finca ha sido reactivada exitosamente'
      })
      
      return result
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al reactivar la finca'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Load lotes for a finca
   * @param {number} fincaId - Finca ID
   * @param {Object} params - Filter parameters
   * @returns {Promise<Array>} List of lotes
   */
  const loadLotes = async (fincaId, params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await fincasApi.getLotesByFinca(fincaId, params)
      lotes.value = Array.isArray(data.lotes || data) ? (data.lotes || data) : (data?.results || [])
      
      return lotes.value
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al cargar los lotes'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Load finca statistics
   * @param {number} fincaId - Finca ID
   * @returns {Promise<Object>} Statistics
   */
  const loadStats = async (fincaId) => {
    try {
      return await fincasApi.getFincaStats(fincaId)
    } catch (err) {
      console.error('Error loading finca stats:', err)
      throw err
    }
  }
  
  /**
   * Format finca location
   * @param {Object} fincaData - Finca data
   * @returns {string} Formatted location
   */
  const formatLocation = (fincaData) => {
    if (!fincaData) return ''
    if (fincaData.ubicacion_completa) return fincaData.ubicacion_completa
    if (fincaData.municipio && fincaData.departamento) {
      return `${fincaData.municipio}, ${fincaData.departamento}`
    }
    return fincaData.ubicacion || ''
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
    finca,
    fincas,
    lotes,
    analisis,
    
    // Computed
    isAdmin,
    isFarmer,
    
    // Methods
    canEdit,
    canDelete,
    canView,
    loadFincas,
    loadFinca,
    createFinca,
    updateFinca,
    deleteFinca,
    activateFinca,
    loadLotes,
    loadStats,
    formatLocation,
    clearError,
    
    // Utilities
    formatDate,
    
    // API helpers
    getDepartamentosColombia: fincasApi.getDepartamentosColombia,
    getMunicipiosByDepartamento: fincasApi.getMunicipiosByDepartamento,
    validateFincaData: fincasApi.validateFincaData,
    formatFincaData: fincasApi.formatFincaData
  }
}

