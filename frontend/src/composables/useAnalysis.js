/**
 * Composable for analysis operations
 * Domain composable for analysis-related functionality
 */
import { ref, computed } from 'vue'
import { usePredictionStore } from '@/stores/prediction'
import { predictImage, predictImageYolo, predictImageSmart } from '@/services/predictionApi'

/**
 * Provides analysis operations and state
 * @returns {Object} Analysis composable with methods and state
 */
export function useAnalysis() {
  const store = usePredictionStore()

  // Local state
  const isAnalyzing = ref(false)
  const analysisError = ref(null)
  const currentBatch = ref(null)

  // Computed from store
  const currentPrediction = computed(() => store.currentPrediction)
  const predictions = computed(() => store.predictions)
  const stats = computed(() => store.stats)
  const loading = computed(() => store.isLoading || isAnalyzing.value)
  const error = computed(() => analysisError.value || store.error)

  /**
   * Executes analysis on a single image
   * @param {File|string} image - Image file or URL
   * @param {string} method - Analysis method (traditional, yolo, smart)
   * @returns {Promise<Object>} Analysis result
   */
  const analyzeImage = async (image, method = 'traditional') => {
    isAnalyzing.value = true
    analysisError.value = null

    try {
      let result

      switch (method) {
        case 'traditional':
          result = await predictImage(image)
          break
        case 'yolo':
          result = await predictImageYolo(image)
          break
        case 'smart':
          result = await predictImageSmart(image)
          break
        default:
          throw new Error(`Método de análisis no soportado: ${method}`)
      }

      store.setCurrentPrediction(result.data || result)
      return result.data || result
    } catch (err) {
      analysisError.value = err.response?.data?.detail || err.message || 'Error al ejecutar el análisis'
      store.setError(analysisError.value)
      throw err
    } finally {
      isAnalyzing.value = false
    }
  }

  /**
   * Executes batch analysis on multiple images
   * @param {Array<File|string>} images - Array of image files or URLs
   * @param {string} method - Analysis method
   * @param {Function} onProgress - Progress callback (current, total)
   * @returns {Promise<Array>} Array of analysis results
   */
  const analyzeBatch = async (images, method = 'traditional', onProgress = null) => {
    isAnalyzing.value = true
    analysisError.value = null
    currentBatch.value = {
      total: images.length,
      completed: 0,
      results: []
    }

    try {
      const results = []

      for (let i = 0; i < images.length; i++) {
        try {
          const result = await analyzeImage(images[i], method)
          results.push(result)
          currentBatch.value.completed = i + 1
          currentBatch.value.results.push(result)

          if (onProgress) {
            onProgress(i + 1, images.length)
          }
        } catch (err) {
          results.push({ error: err.message, image: images[i] })
        }
      }

      return results
    } catch (err) {
      analysisError.value = err.message || 'Error en el análisis por lotes'
      throw err
    } finally {
      isAnalyzing.value = false
      currentBatch.value = null
    }
  }

  /**
   * Gets analysis summary statistics
   * @param {Array} results - Analysis results array
   * @returns {Object} Summary statistics
   */
  const getAnalysisSummary = (results = null) => {
    const data = results || store.predictions || (store.currentPrediction ? [store.currentPrediction] : [])

    if (!data || data.length === 0) {
      return {
        total: 0,
        avgWeight: 0,
        avgDimensions: { width: 0, height: 0, thickness: 0 },
        qualityDistribution: {}
      }
    }

    const validResults = data.filter(r => r && !r.error)
    const total = validResults.length

    if (total === 0) {
      return {
        total: 0,
        avgWeight: 0,
        avgDimensions: { width: 0, height: 0, thickness: 0 },
        qualityDistribution: {}
      }
    }

    // Calculate averages
    const weights = validResults.map(r => Number.parseFloat(r.peso_estimado || r.weight || 0)).filter(w => !Number.isNaN(w))
    const avgWeight = weights.length > 0 ? weights.reduce((a, b) => a + b, 0) / weights.length : 0

    const widths = validResults.map(r => Number.parseFloat(r.ancho_mm || r.width || 0)).filter(w => !Number.isNaN(w))
    const heights = validResults.map(r => Number.parseFloat(r.altura_mm || r.height || 0)).filter(h => !Number.isNaN(h))
    const thicknesses = validResults.map(r => Number.parseFloat(r.grosor_mm || r.thickness || 0)).filter(t => !Number.isNaN(t))

    const avgDimensions = {
      width: widths.length > 0 ? widths.reduce((a, b) => a + b, 0) / widths.length : 0,
      height: heights.length > 0 ? heights.reduce((a, b) => a + b, 0) / heights.length : 0,
      thickness: thicknesses.length > 0 ? thicknesses.reduce((a, b) => a + b, 0) / thicknesses.length : 0
    }

    // Quality distribution
    const qualityDistribution = {}
    for (const r of validResults) {
      const quality = r.quality || r.calidad || 'unknown'
      qualityDistribution[quality] = (qualityDistribution[quality] || 0) + 1
    }

    return {
      total,
      avgWeight: Number.parseFloat(avgWeight.toFixed(2)),
      avgDimensions: {
        width: Number.parseFloat(avgDimensions.width.toFixed(2)),
        height: Number.parseFloat(avgDimensions.height.toFixed(2)),
        thickness: Number.parseFloat(avgDimensions.thickness.toFixed(2))
      },
      qualityDistribution
    }
  }

  /**
   * Clears current analysis state
   * @returns {void}
   */
  const clearAnalysis = () => {
    isAnalyzing.value = false
    analysisError.value = null
    currentBatch.value = null
    store.clearCurrentPrediction()
  }

  /**
   * Formats analysis result for display
   * @param {Object} result - Analysis result
   * @returns {Object} Formatted result
   */
  const formatAnalysisResult = (result) => {
    if (!result) return null

    return {
      id: result.id,
      weight: Number.parseFloat(result.peso_estimado || result.weight || 0).toFixed(2),
      dimensions: {
        width: Number.parseFloat(result.ancho_mm || result.width || 0).toFixed(2),
        height: Number.parseFloat(result.altura_mm || result.height || 0).toFixed(2),
        thickness: Number.parseFloat(result.grosor_mm || result.thickness || 0).toFixed(2)
      },
      quality: result.quality || result.calidad || 'unknown',
      confidence: result.confidence_score || result.nivel_confianza || 0,
      method: result.method || 'traditional',
      timestamp: result.timestamp || result.created_at || new Date().toISOString()
    }
  }

  return {
    // State
    isAnalyzing,
    analysisError,
    currentBatch,
    currentPrediction,
    predictions,
    stats,
    loading,
    error,

    // Methods
    analyzeImage,
    analyzeBatch,
    getAnalysisSummary,
    clearAnalysis,
    formatAnalysisResult,

    // Store access
    store
  }
}

