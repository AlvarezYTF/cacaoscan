/**
 * Composable for reports management
 * Consolidates report generation, filtering, downloading, and formatting logic
 */
import { ref, reactive, computed } from 'vue'
import { useDateFormatting } from './useDateFormatting'
import reportsService from '@/services/reportsService'
import { useNotificationStore } from '@/stores/notifications'
import { useReportsStore } from '@/stores/reports'

/**
 * Format report type label
 * @param {string} type - Report type
 * @returns {string} Formatted label
 */
export function formatReportType(type) {
  const labels = {
    'calidad': 'Calidad',
    'finca': 'Finca',
    'lote': 'Lote',
    'usuario': 'Usuario',
    'auditoria': 'Auditoría',
    'personalizado': 'Personalizado',
    'metricas': 'Métricas',
    'entrenamiento': 'Entrenamiento'
  }
  return labels[type] || type
}

/**
 * Format report status label
 * @param {string} status - Report status
 * @returns {string} Formatted label
 */
export function formatReportStatus(status) {
  const labels = {
    'pendiente': 'Pendiente',
    'procesando': 'Procesando',
    'generando': 'Generando',
    'completado': 'Completado',
    'error': 'Error',
    'fallido': 'Fallido'
  }
  return labels[status] || status
}

/**
 * Get status class for CSS
 * @param {string} status - Report status
 * @returns {string} CSS class
 */
export function getReportStatusClass(status) {
  const classes = {
    'pendiente': 'status-pending',
    'procesando': 'status-processing',
    'generando': 'status-processing',
    'completado': 'status-completed',
    'error': 'status-error',
    'fallido': 'status-error'
  }
  return classes[status] || 'status-pending'
}

/**
 * Get status icon class
 * @param {string} status - Report status
 * @returns {string} Icon class
 */
export function getReportStatusIcon(status) {
  const icons = {
    'pendiente': 'fas fa-clock',
    'procesando': 'fas fa-spinner fa-spin',
    'generando': 'fas fa-spinner fa-spin',
    'completado': 'fas fa-check-circle',
    'error': 'fas fa-exclamation-circle',
    'fallido': 'fas fa-exclamation-circle'
  }
  return icons[status] || 'fas fa-clock'
}

/**
 * Format file size
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return 'N/A'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Format duration in seconds
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
export function formatDuration(seconds) {
  if (!seconds) return 'N/A'
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`
  }
  return `${remainingSeconds}s`
}

/**
 * Main useReports composable
 * @param {Object} options - Configuration options
 * @returns {Object} Reports composable methods and state
 */
export function useReports(options = {}) {
  const notificationStore = useNotificationStore()
  const reportsStore = useReportsStore()
  const { formatDate } = useDateFormatting()
  
  // State
  const loading = ref(false)
  const error = ref(null)
  const generating = ref(false)
  const reports = ref([])
  const filters = reactive({
    tipo_reporte: '',
    formato: '',
    estado: '',
    usuario_id: '',
    fecha_desde: '',
    fecha_hasta: '',
    finca_id: '',
    lote_id: ''
  })
  
  // Form state
  const formData = reactive({
    tipo_reporte: '',
    formato: '',
    titulo: '',
    descripcion: '',
    parametros: {
      finca_id: '',
      include_dimensions: true,
      include_weight: true,
      include_confidence: true
    },
    filtros: {
      fecha_desde: '',
      fecha_hasta: ''
    }
  })
  
  // Computed
  const hasFilters = computed(() => {
    return Object.values(filters).some(value => value !== '')
  })
  
  const reportTypes = computed(() => {
    return reportsService.getReportTypes()
  })
  
  const reportFormats = computed(() => {
    return reportsService.getReportFormats()
  })
  
  const reportStates = computed(() => {
    return reportsService.getReportStates()
  })
  
  /**
   * Build report data from form
   * @returns {Object} Report data ready for API
   */
  const buildReportData = () => {
    const data = {
      tipo_reporte: formData.tipo_reporte,
      formato: formData.formato,
      titulo: formData.titulo,
      descripcion: formData.descripcion || '',
      parametros: {},
      filtros: {}
    }
    
    // Add parameters if they exist
    if (formData.parametros && Object.keys(formData.parametros).length > 0) {
      data.parametros = { ...formData.parametros }
    }
    
    // Add filters if they exist
    if (formData.filtros && (formData.filtros.fecha_desde || formData.filtros.fecha_hasta)) {
      data.filtros = { ...formData.filtros }
    }
    
    return data
  }
  
  /**
   * Validate report form
   * @returns {Object} Validation result { valid: boolean, errors: Object }
   */
  const validateReportForm = () => {
    const errors = {}
    
    if (!formData.tipo_reporte) {
      errors.tipo_reporte = 'El tipo de reporte es requerido'
    }
    
    if (!formData.formato) {
      errors.formato = 'El formato es requerido'
    }
    
    if (!formData.titulo || formData.titulo.trim() === '') {
      errors.titulo = 'El título es requerido'
    }
    
    // Validate finca_id if tipo_reporte is 'finca'
    if (formData.tipo_reporte === 'finca' && !formData.parametros.finca_id) {
      errors.finca_id = 'La finca es requerida para reportes de finca'
    }
    
    return {
      valid: Object.keys(errors).length === 0,
      errors
    }
  }
  
  /**
   * Generate report
   * @returns {Promise<Object>} Generated report
   */
  const generateReport = async () => {
    const validation = validateReportForm()
    if (!validation.valid) {
      throw new Error(Object.values(validation.errors).join(', '))
    }
    
    try {
      generating.value = true
      error.value = null
      
      const reportData = buildReportData()
      const result = await reportsService.createReport(reportData)
      
      notificationStore.addNotification({
        type: 'success',
        title: 'Reporte generado',
        message: `El reporte "${reportData.titulo}" se está generando en segundo plano.`
      })
      
      return result
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al generar el reporte'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error al generar reporte',
        message: errorMessage
      })
      
      throw err
    } finally {
      generating.value = false
    }
  }
  
  /**
   * Apply filters
   * @param {Object} newFilters - New filter values
   */
  const applyFilters = (newFilters = {}) => {
    Object.assign(filters, newFilters)
  }
  
  /**
   * Clear all filters
   */
  const clearFilters = () => {
    for (const key of Object.keys(filters)) {
      filters[key] = ''
    }
  }
  
  /**
   * Download report
   * @param {number} reportId - Report ID
   * @param {string} filename - Optional filename
   * @returns {Promise<boolean>} Success status
   */
  const downloadReport = async (reportId, filename = null) => {
    try {
      loading.value = true
      error.value = null
      
      // Use store's downloadReport method which handles the download properly
      await reportsStore.downloadReport(reportId)
      
      notificationStore.addNotification({
        type: 'success',
        title: 'Descarga iniciada',
        message: 'El archivo se está descargando'
      })
      
      return true
    } catch (err) {
      const errorMessage = err.message || 'Error al descargar el reporte'
      error.value = errorMessage
      
      notificationStore.addNotification({
        type: 'error',
        title: 'Error al descargar',
        message: errorMessage
      })
      
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Preview report
   * @param {number} reportId - Report ID
   * @returns {Promise<Object>} Preview data
   */
  const previewReport = async (reportId) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await reportsService.getReportDetails(reportId)
      return result
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error al obtener preview'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Check report status
   * @param {number} reportId - Report ID
   * @returns {Promise<Object>} Status information
   */
  const checkReportStatus = async (reportId) => {
    try {
      return await reportsService.checkReportStatus(reportId)
    } catch (err) {
      throw err
    }
  }
  
  /**
   * Poll for report completion
   * @param {number} reportId - Report ID
   * @param {number} interval - Polling interval in ms
   * @param {number} maxAttempts - Maximum polling attempts
   * @returns {Promise<Object>} Completed report
   */
  const pollForCompletion = async (reportId, interval = 3000, maxAttempts = 60) => {
    let attempts = 0
    let timeoutId = null
    let isResolved = false
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        // Prevent execution if promise already resolved/rejected
        if (isResolved) {
          return
        }
        
        try {
          attempts++
          const status = await checkReportStatus(reportId)
          const estado = (status.estado || '').toLowerCase()
          
          if (estado === 'completado' || estado === 'completed') {
            isResolved = true
            if (timeoutId) {
              clearTimeout(timeoutId)
            }
            const report = await reportsService.getReportDetails(reportId)
            resolve(report)
            return
          }
          
          if (estado === 'error' || estado === 'fallido' || estado === 'failed') {
            isResolved = true
            if (timeoutId) {
              clearTimeout(timeoutId)
            }
            reject(new Error(status.mensaje_error || 'Error al generar el reporte'))
            return
          }
          
          if (attempts >= maxAttempts) {
            isResolved = true
            if (timeoutId) {
              clearTimeout(timeoutId)
            }
            reject(new Error('Tiempo de espera agotado'))
            return
          }
          
          // Only schedule next poll if promise hasn't been resolved
          if (!isResolved) {
            timeoutId = setTimeout(poll, interval)
          }
        } catch (err) {
          isResolved = true
          if (timeoutId) {
            clearTimeout(timeoutId)
          }
          reject(err)
        }
      }
      
      poll()
    })
  }
  
  /**
   * Watch report status (reactive polling)
   * @param {number} reportId - Report ID
   * @param {Function} onStatusChange - Callback for status changes
   * @returns {Function} Stop watching function
   */
  const watchStatus = (reportId, onStatusChange) => {
    let isWatching = true
    let intervalId = null
    
    const watch = async () => {
      if (!isWatching) return
      
      try {
        const status = await checkReportStatus(reportId)
        onStatusChange(status)
        
        if (status.estado === 'completado' || status.estado === 'error' || status.estado === 'fallido') {
          stopWatching()
          return
        }
        
        intervalId = setTimeout(watch, 3000)
      } catch (err) {
        stopWatching()
      }
    }
    
    const stopWatching = () => {
      isWatching = false
      if (intervalId) {
        clearTimeout(intervalId)
      }
    }
    
    watch()
    return stopWatching
  }
  
  /**
   * Reset form
   */
  const resetForm = () => {
    formData.tipo_reporte = ''
    formData.formato = ''
    formData.titulo = ''
    formData.descripcion = ''
    formData.parametros = {
      finca_id: '',
      include_dimensions: true,
      include_weight: true,
      include_confidence: true
    }
    formData.filtros = {
      fecha_desde: '',
      fecha_hasta: ''
    }
    error.value = null
  }
  
  return {
    // State
    loading,
    error,
    generating,
    reports,
    filters,
    formData,
    
    // Computed
    hasFilters,
    reportTypes,
    reportFormats,
    reportStates,
    
    // Methods
    buildReportData,
    validateReportForm,
    generateReport,
    applyFilters,
    clearFilters,
    downloadReport,
    previewReport,
    checkReportStatus,
    pollForCompletion,
    watchStatus,
    resetForm,
    
    // Formatting utilities (exported from module)
    formatReportType,
    formatReportStatus,
    getReportStatusClass,
    getReportStatusIcon,
    formatFileSize,
    formatDuration,
    formatDate
  }
}

