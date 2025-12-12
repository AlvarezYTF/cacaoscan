/**
 * Composable for quality data and statistics
 */
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { getFincas } from '@/services/fincasApi'

export function useQualityData() {
  const authStore = useAuthStore()
  const qualityStats = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const fincasData = ref([])
  
  /**
   * Fetch quality statistics
   */
  async function fetchQualityStats() {
    if (!authStore.isAuthenticated) {
      error.value = 'Usuario no autenticado'
      return
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/images/stats/')
      
      if (response.data) {
        const avgConfidence = response.data.average_confidence || 0
        const qualityPercent = Math.round(avgConfidence * 100)
        
        qualityStats.value = {
          averageQuality: qualityPercent,
          totalImages: response.data.total_images || 0,
          processedImages: response.data.processed_images || 0,
          averageConfidence: avgConfidence,
          previousPeriod: null // TODO: Implement when backend provides this
        }
      }
    } catch (err) {
      console.error('[useQualityData] Error fetching quality stats:', err)
      if (err.response?.status !== 500) {
        error.value = err.response?.data?.error || 'Error al obtener estadísticas de calidad'
      }
      qualityStats.value = {
        averageQuality: 0,
        totalImages: 0,
        processedImages: 0,
        averageConfidence: 0,
        previousPeriod: null
      }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Fetch fincas with quality data
   */
  async function fetchFincasWithQuality() {
    if (!authStore.isAuthenticated) {
      return []
    }
    
    try {
      const response = await getFincas({ activa: true })
      const fincas = response.results || []
      
      // Fetch stats for each finca
      const fincasWithStats = await Promise.all(
        fincas.map(async (finca) => {
          try {
            const statsResponse = await api.get(`/fincas/${finca.id}/stats/`)
            return {
              ...finca,
              quality: statsResponse.data?.calidad_promedio || 0,
              totalAnalyses: statsResponse.data?.total_analisis || 0,
              lastAnalysisDate: statsResponse.data?.ultima_fecha_analisis || null
            }
          } catch (err) {
            return {
              ...finca,
              quality: 0,
              totalAnalyses: 0,
              lastAnalysisDate: null
            }
          }
        })
      )
      
      fincasData.value = fincasWithStats
      return fincasWithStats
    } catch (err) {
      console.error('[useQualityData] Error fetching fincas:', err)
      fincasData.value = []
      return []
    }
  }
  
  /**
   * Get quality classification
   */
  const getQualityClassification = (quality) => {
    if (quality >= 85) {
      return {
        label: 'Excelente',
        color: 'green',
        icon: '🟢'
      }
    } else if (quality >= 70) {
      return {
        label: 'Aceptable',
        color: 'yellow',
        icon: '🟡'
      }
    } else {
      return {
        label: 'Riesgo',
        color: 'red',
        icon: '🔴'
      }
    }
  }
  
  /**
   * Calculate trend (up/down/stable)
   */
  const calculateTrend = (current, previous) => {
    if (!previous || previous === 0) {
      return current > 0 ? 'up' : 'stable'
    }
    const change = ((current - previous) / previous) * 100
    if (Math.abs(change) < 1) {
      return 'stable'
    }
    return change > 0 ? 'up' : 'down'
  }
  
  // Computed properties
  const qualityClassification = computed(() => {
    if (!qualityStats.value) return null
    return getQualityClassification(qualityStats.value.averageQuality)
  })
  
  const qualityTrend = computed(() => {
    if (!qualityStats.value) return 'stable'
    return calculateTrend(
      qualityStats.value.averageQuality,
      qualityStats.value.previousPeriod
    )
  })
  
  return {
    // State
    qualityStats,
    fincasData,
    loading,
    error,
    
    // Methods
    fetchQualityStats,
    fetchFincasWithQuality,
    getQualityClassification,
    calculateTrend,
    
    // Computed
    qualityClassification,
    qualityTrend
  }
}

