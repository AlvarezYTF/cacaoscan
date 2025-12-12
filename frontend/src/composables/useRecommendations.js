/**
 * Composable for smart recommendations based on ML and business rules
 */
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { getFincas } from '@/services/fincasApi'

export function useRecommendations() {
  const authStore = useAuthStore()
  const recommendations = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  /**
   * Generate smart recommendations
   */
  async function generateRecommendations() {
    if (!authStore.isAuthenticated) {
      return []
    }
    
    loading.value = true
    error.value = null
    
    try {
      const generatedRecommendations = []
      
      // 1. Fetch fincas and their stats
      const fincasResponse = await getFincas({ activa: true })
      const fincas = fincasResponse.results || []
      
      // 2. Analyze each finca
      for (const finca of fincas) {
        try {
          const fincaStatsResponse = await api.get(`/fincas/${finca.id}/stats/`)
          const fincaStats = fincaStatsResponse.data || {}
          const calidadPromedio = fincaStats.calidad_promedio || 0
          
          // Recommendation for stable quality
          if (calidadPromedio >= 80 && calidadPromedio < 90) {
            generatedRecommendations.push({
              id: `finca-${finca.id}-stable`,
              type: 'success',
              title: `La finca ${finca.nombre} mantiene calidad estable`,
              message: `Calidad promedio: ${Math.round(calidadPromedio)}%. Continúe el proceso actual.`,
              priority: 'low'
            })
          }
          
          // Recommendation for quality improvement
          if (calidadPromedio < 70) {
            generatedRecommendations.push({
              id: `finca-${finca.id}-improve`,
              type: 'warning',
              title: `Se recomienda mejorar el proceso de poscosecha en ${finca.nombre}`,
              message: `Calidad actual: ${Math.round(calidadPromedio)}%. Revise el secado y fermentación.`,
              priority: 'high'
            })
          }
        } catch (err) {
          console.warn(`[useRecommendations] Could not analyze finca ${finca.id}:`, err)
        }
      }
      
      // 3. Check for dimension variability
      try {
        const imagesStatsResponse = await api.get('/images/stats/')
        const avgDimensions = imagesStatsResponse.data?.average_dimensions || {}
        
        if (avgDimensions.alto_mm && avgDimensions.ancho_mm) {
          const dimensionVariability = Math.abs(
            (avgDimensions.alto_mm - avgDimensions.ancho_mm) / avgDimensions.alto_mm
          ) * 100
          
          if (dimensionVariability > 15) {
            generatedRecommendations.push({
              id: 'dimension-variability',
              type: 'info',
              title: 'Alta variabilidad en dimensiones detectada',
              message: 'Se recomienda revisar la selección manual de granos para mantener uniformidad.',
              priority: 'medium'
            })
          }
        }
      } catch (err) {
        console.warn('[useRecommendations] Could not check dimension variability:', err)
      }
      
      // 4. Check for lotes with low quality
      try {
        const recentImagesResponse = await api.get('/images/', {
          params: {
            page: 1,
            page_size: 20,
            ordering: '-created_at'
          }
        })
        
        const recentImages = recentImagesResponse.data?.results || []
        const lotesQuality = {}
        
        for (const image of recentImages) {
          if (image.lote_id && image.prediction) {
            const loteId = image.lote_id
            if (!lotesQuality[loteId]) {
              lotesQuality[loteId] = {
                total: 0,
                sumQuality: 0,
                loteName: `CAC-${loteId}`
              }
            }
            lotesQuality[loteId].total++
            lotesQuality[loteId].sumQuality += image.prediction.average_confidence * 100
          }
        }
        
        for (const [loteId, data] of Object.entries(lotesQuality)) {
          const avgQuality = data.sumQuality / data.total
          if (avgQuality < 70) {
            generatedRecommendations.push({
              id: `lote-${loteId}-low-quality`,
              type: 'warning',
              title: `Se recomienda mejorar el secado del lote ${data.loteName}`,
              message: `Calidad promedio: ${Math.round(avgQuality)}%. Revise el proceso de secado.`,
              priority: 'high'
            })
          }
        }
      } catch (err) {
        console.warn('[useRecommendations] Could not check lotes quality:', err)
      }
      
      recommendations.value = generatedRecommendations.sort((a, b) => {
        const priorityOrder = { high: 0, medium: 1, low: 2 }
        return priorityOrder[a.priority] - priorityOrder[b.priority]
      })
      
      return recommendations.value
    } catch (err) {
      console.error('[useRecommendations] Error generating recommendations:', err)
      if (err.response?.status !== 500) {
        error.value = err.response?.data?.error || 'Error al generar recomendaciones'
      }
      recommendations.value = []
      return []
    } finally {
      loading.value = false
    }
  }
  
  // Computed properties
  const highPriorityRecommendations = computed(() => {
    return recommendations.value.filter(rec => rec.priority === 'high')
  })
  
  const hasRecommendations = computed(() => {
    return recommendations.value.length > 0
  })
  
  return {
    // State
    recommendations,
    loading,
    error,
    
    // Methods
    generateRecommendations,
    
    // Computed
    highPriorityRecommendations,
    hasRecommendations
  }
}

