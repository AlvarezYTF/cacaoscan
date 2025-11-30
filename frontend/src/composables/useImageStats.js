/**
 * Composable para manejar estadísticas de imágenes
 */
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from '@/services/api'

export function useImageStats() {
  const authStore = useAuthStore()
  const stats = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  /**
   * Obtener estadísticas de imágenes del usuario
   */
  async function fetchStats() {
    if (!authStore.isAuthenticated) {
      error.value = 'Usuario no autenticado'
      return
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get('/api/v1/images/stats/')
      
      stats.value = response.data
    } catch (err) {
      // Si es error 500, retornar valores por defecto sin loggear
      if (err.response?.status === 500) {
        stats.value = {
          total_images: 0,
          processed_images: 0,
          processing_rate: 0,
          average_confidence: 0,
          average_dimensions: {},
          region_stats: [],
          top_fincas: []
        }
        error.value = null
      } else {
        console.error('Error fetching image stats:', err)
        error.value = err.response?.data?.error || 'Error al obtener estadísticas'
      }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Obtener lista de imágenes del usuario con paginación
   */
  async function fetchImages(page = 1, filters = {}) {
    if (!authStore.isAuthenticated) {
      error.value = 'Usuario no autenticado'
      return { results: [], count: 0, totalPages: 0 }
    }
    
    loading.value = true
    error.value = null
    
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: filters.page_size ? filters.page_size.toString() : '20'
      })
      
      // Agregar otros filtros si existen
      for (const key of Object.keys(filters)) {
        if (key !== 'page_size' && filters[key] !== undefined && filters[key] !== null) {
          params.append(key, filters[key].toString())
        }
      }
      
      const response = await axios.get(`/api/v1/images/?${params}`)
      
      return response.data
    } catch (err) {
      // Si es error 500, retornar objeto vacío sin loggear
      if (err.response?.status !== 500) {
        console.error('Error fetching images:', err)
        error.value = err.response?.data?.error || 'Error al obtener imágenes'
      }
      return { results: [], count: 0, totalPages: 0 }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Obtener estadísticas de reportes
   */
  async function fetchReportStats(filters = {}) {
    if (!authStore.isAuthenticated) {
      error.value = 'Usuario no autenticado'
      return null
    }
    
    loading.value = true
    error.value = null
    
    try {
      const params = new URLSearchParams(filters)
      
      const response = await axios.get(`/reports/stats/?${params}`)
      
      return response.data
    } catch (err) {
      // Si es error 500, retornar null sin loggear
      if (err.response?.status !== 500) {
        console.error('Error fetching report stats:', err)
        error.value = err.response?.data?.error || 'Error al obtener estadísticas de reportes'
      }
      return null
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Generar reporte PDF
   */
  async function generateReport(reportType, filters = {}) {
    if (!authStore.isAuthenticated) {
      error.value = 'Usuario no autenticado'
      return false
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post(`/reports/${reportType}/`, filters, {
        responseType: 'blob'
      })
      
      // Crear blob y descargar
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const link = document.createElement('a')
      link.href = globalThis.URL.createObjectURL(blob)
      link.download = `reporte_${reportType}_${new Date().toISOString().split('T')[0]}.pdf`
      link.click()
      
      return true
    } catch (err) {
      console.error('Error generating report:', err)
      error.value = err.response?.data?.error || 'Error al generar reporte'
      return false
    } finally {
      loading.value = false
    }
  }
  
  // Computed properties
  const hasStats = computed(() => stats.value !== null)
  const totalImages = computed(() => stats.value?.total_images || 0)
  const processedImages = computed(() => stats.value?.processed_images || 0)
  const processingRate = computed(() => stats.value?.processing_rate || 0)
  const averageConfidence = computed(() => stats.value?.average_confidence || 0)
  const averageDimensions = computed(() => stats.value?.average_dimensions || {})
  const regionStats = computed(() => stats.value?.region_stats || [])
  const topFincas = computed(() => stats.value?.top_fincas || [])
  
  return {
    // State
    stats,
    loading,
    error,
    
    // Methods
    fetchStats,
    fetchImages,
    fetchReportStats,
    generateReport,
    
    // Computed
    hasStats,
    totalImages,
    processedImages,
    processingRate,
    averageConfidence,
    averageDimensions,
    regionStats,
    topFincas
  }
}
