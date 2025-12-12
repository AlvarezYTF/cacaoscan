/**
 * Composable for smart alerts system
 */
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { getFincas } from '@/services/fincasApi'

export function useAlerts() {
  const authStore = useAuthStore()
  const alerts = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  /**
   * Generate alerts based on business rules and ML analysis
   */
  async function generateAlerts() {
    if (!authStore.isAuthenticated) {
      return []
    }
    
    loading.value = true
    error.value = null
    
    try {
      const generatedAlerts = []
      
      // 1. Fetch fincas and their stats
      const fincasResponse = await getFincas({ activa: true })
      const fincas = fincasResponse.results || []
      
      // 2. Fetch images stats
      const imagesStatsResponse = await api.get('/images/stats/')
      const imagesStats = imagesStatsResponse.data || {}
      
      // 3. Check for unprocessed images
      const unprocessedCount = imagesStats.unprocessed_images || 0
      if (unprocessedCount > 0) {
        generatedAlerts.push({
          id: 'unprocessed-images',
          type: 'warning',
          priority: unprocessedCount >= 5 ? 'high' : 'medium',
          title: `${unprocessedCount} análisis pendientes de procesamiento`,
          message: `Tienes ${unprocessedCount} imagen${unprocessedCount > 1 ? 'es' : ''} esperando procesamiento`,
          action: {
            label: 'Ver análisis',
            route: '/analisis'
          }
        })
      }
      
      // 4. Check each finca for quality issues
      for (const finca of fincas) {
        try {
          const fincaStatsResponse = await api.get(`/fincas/${finca.id}/stats/`)
          const fincaStats = fincaStatsResponse.data || {}
          const calidadPromedio = fincaStats.calidad_promedio || 0
          const defectRate = (1 - (calidadPromedio / 100)) * 100
          
          // Alert if defect rate is high
          if (defectRate > 20) {
            generatedAlerts.push({
              id: `finca-${finca.id}-defects`,
              type: 'warning',
              priority: defectRate > 30 ? 'high' : 'medium',
              title: `La finca ${finca.nombre} presenta ${Math.round(defectRate)}% de granos defectuosos`,
              message: `La calidad promedio es ${Math.round(calidadPromedio)}%. Se recomienda revisar el proceso de poscosecha.`,
              action: {
                label: 'Revisar finca',
                route: `/fincas/${finca.id}`
              }
            })
          }
        } catch (err) {
          // Skip finca if stats fail
          console.warn(`[useAlerts] Could not fetch stats for finca ${finca.id}:`, err)
        }
      }
      
      // 5. Check for quality drops in recent analyses
      try {
        const recentImagesResponse = await api.get('/images/', {
          params: {
            page: 1,
            page_size: 10,
            ordering: '-created_at'
          }
        })
        
        const recentImages = recentImagesResponse.data?.results || []
        if (recentImages.length >= 2) {
          const latest = recentImages[0]
          const previous = recentImages[1]
          
          if (latest.prediction && previous.prediction) {
            const latestQuality = latest.prediction.average_confidence * 100
            const previousQuality = previous.prediction.average_confidence * 100
            const qualityDrop = previousQuality - latestQuality
            
            if (qualityDrop > 10) {
              const loteId = latest.lote_id ? `CAC-${latest.lote_id}` : 'desconocido'
              generatedAlerts.push({
                id: `quality-drop-${latest.id}`,
                type: 'warning',
                priority: qualityDrop > 20 ? 'high' : 'medium',
                title: `La calidad del lote ${loteId} bajó ${Math.round(qualityDrop)}% esta semana`,
                message: `Calidad actual: ${Math.round(latestQuality)}% vs ${Math.round(previousQuality)}% anterior`,
                action: {
                  label: 'Re-analizar lote',
                  route: `/analisis`
                }
              })
            }
          }
        }
      } catch (err) {
        console.warn('[useAlerts] Could not check quality trends:', err)
      }
      
      alerts.value = generatedAlerts.sort((a, b) => {
        const priorityOrder = { high: 0, medium: 1, low: 2 }
        return priorityOrder[a.priority] - priorityOrder[b.priority]
      })
      
      return alerts.value
    } catch (err) {
      console.error('[useAlerts] Error generating alerts:', err)
      if (err.response?.status !== 500) {
        error.value = err.response?.data?.error || 'Error al generar alertas'
      }
      alerts.value = []
      return []
    } finally {
      loading.value = false
    }
  }
  
  // Computed properties
  const highPriorityAlerts = computed(() => {
    return alerts.value.filter(alert => alert.priority === 'high')
  })
  
  const mediumPriorityAlerts = computed(() => {
    return alerts.value.filter(alert => alert.priority === 'medium')
  })
  
  const lowPriorityAlerts = computed(() => {
    return alerts.value.filter(alert => alert.priority === 'low')
  })
  
  const hasAlerts = computed(() => {
    return alerts.value.length > 0
  })
  
  return {
    // State
    alerts,
    loading,
    error,
    
    // Methods
    generateAlerts,
    
    // Computed
    highPriorityAlerts,
    mediumPriorityAlerts,
    lowPriorityAlerts,
    hasAlerts
  }
}

