/**
 * Composable for prediction operations
 * Centralizes prediction logic and state management
 */
import { ref, computed } from 'vue'
import { predictImage, predictImageYolo, predictImageSmart } from '@/services/predictionApi'
import { handleApiError } from '@/services/apiErrorHandler'

/**
 * Create prediction composable
 * @param {Object} options - Options
 * @param {string} options.method - Prediction method (traditional, yolo, smart, cacaoscan)
 * @param {Function} options.onSuccess - Success callback
 * @param {Function} options.onError - Error callback
 * @returns {Object} Prediction state and methods
 */
export function usePrediction(options = {}) {
  const {
    method = 'traditional',
    onSuccess = null,
    onError = null
  } = options

  // State
  const isLoading = ref(false)
  const error = ref(null)
  const result = ref(null)
  const processingTime = ref(0)

  // Computed
  const hasResult = computed(() => result.value !== null)
  const hasError = computed(() => error.value !== null)

  /**
   * Map API response to prediction data format
   * @param {Object} apiData - API response data
   * @param {string} predictionMethod - Method used
   * @returns {Object} Mapped prediction data
   */
  const mapApiResponseToPredictionData = (apiData, predictionMethod = method) => {
    return {
      id: apiData.id || Date.now(),
      width: apiData.ancho_mm || apiData.width,
      height: apiData.alto_mm || apiData.altura_mm || apiData.height,
      thickness: apiData.grosor_mm || apiData.grosor || apiData.thickness,
      predicted_weight: apiData.peso_g || apiData.peso_estimado || apiData.predicted_weight,
      prediction_method: apiData.method || apiData.prediction_method || predictionMethod || 'unknown',
      confidence_level: (() => {
        if (apiData.nivel_confianza) {
          if (apiData.nivel_confianza > 0.8) {
            return 'high'
          } else if (apiData.nivel_confianza > 0.6) {
            return 'medium'
          }
          return 'low'
        }
        return apiData.confidence_level || 'unknown'
      })(),
      confidence_score: apiData.nivel_confianza || apiData.confidence_score || 0,
      processing_time: apiData.processing_time || 0,
      image_url: apiData.image_url,
      created_at: apiData.created_at,
      detection_info: apiData.detection_info,
      smart_crop: apiData.smart_crop,
      derived_metrics: apiData.derived_metrics,
      weight_comparison: apiData.weight_comparison
    }
  }

  /**
   * Execute prediction
   * @param {FormData} formData - Form data with image
   * @param {Object} predictionOptions - Additional options for prediction
   * @returns {Promise<Object>} Prediction result
   */
  const executePrediction = async (formData, predictionOptions = {}) => {
    isLoading.value = true
    error.value = null
    result.value = null
    processingTime.value = 0

    const startTime = Date.now()

    try {
      let apiResult

      switch (method) {
        case 'yolo':
          apiResult = await predictImageYolo(formData)
          break
        case 'smart':
          apiResult = await predictImageSmart(formData, {
            returnCroppedImage: true,
            returnTransparentImage: true,
            ...predictionOptions
          })
          break
        case 'cacaoscan': {
          // Import dynamically to avoid circular dependencies
          const { predictImage: predictImageNew } = await import('@/services/api')
          const newFormData = formData // Use same FormData
          apiResult = { success: true, data: await predictImageNew(newFormData) }
          break
        }
        case 'traditional':
        default:
          apiResult = await predictImage(formData)
          break
      }

      if (apiResult.success) {
        const mappedData = mapApiResponseToPredictionData(apiResult.data, method)
        result.value = mappedData
        processingTime.value = Date.now() - startTime

        if (onSuccess && typeof onSuccess === 'function') {
          onSuccess(mappedData)
        }

        return mappedData
      } else {
        throw new Error(apiResult.error || 'Error en la predicción')
      }
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message

      if (onError && typeof onError === 'function') {
        onError(errorInfo)
      }

      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Reset prediction state
   */
  const reset = () => {
    isLoading.value = false
    error.value = null
    result.value = null
    processingTime.value = 0
  }

  /**
   * Clear error
   */
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    isLoading,
    error,
    result,
    processingTime,

    // Computed
    hasResult,
    hasError,

    // Methods
    executePrediction,
    reset,
    clearError,
    mapApiResponseToPredictionData
  }
}

