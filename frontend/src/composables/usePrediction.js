/**
 * Composable for prediction operations
 * Centralizes prediction logic, state management, and flow orchestration
 * Consolidates usePrediction and usePredictionFlow functionality
 */
import { ref, computed } from 'vue'
import { usePredictionStore } from '@/stores/prediction'
import { predictImage, predictImageYolo, predictImageSmart } from '@/services/predictionApi'
import { handleApiError } from '@/services/apiErrorHandler'
import { useFileUpload } from './useFileUpload'

/**
 * Create prediction composable
 * @param {Object} options - Options
 * @param {string} options.method - Prediction method (traditional, yolo, smart, cacaoscan)
 * @param {Function} options.onSuccess - Success callback
 * @param {Function} options.onError - Error callback
 * @param {boolean} options.useStore - Whether to use prediction store (default: true)
 * @returns {Object} Prediction state and methods
 */
export function usePrediction(options = {}) {
  const {
    method: initialMethod = 'traditional',
    onSuccess = null,
    onError = null,
    useStore = true
  } = options

  const store = useStore ? usePredictionStore() : null

  // State
  const selectedMethod = ref(initialMethod)
  const isLoading = ref(false)
  const error = ref(null)
  const result = ref(null)
  const processingTime = ref(0)

  // Use file upload composable for image handling (optional, can be provided externally)
  const fileUpload = options.fileUpload || useFileUpload({
    allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff'],
    maxSize: 20 * 1024 * 1024, // 20MB
    enablePreview: true
  })

  // Expose file upload state as computed properties
  const imageFile = computed(() => fileUpload.selectedFile.value)
  const imagePreview = computed(() => fileUpload.imagePreview.value)

  // Computed
  const hasResult = computed(() => {
    if (useStore && store) {
      return store.hasPrediction || result.value !== null
    }
    return result.value !== null
  })
  const hasError = computed(() => {
    if (useStore && store) {
      return error.value !== null || store.error !== null
    }
    return error.value !== null
  })
  const hasImage = computed(() => {
    if (useStore && store) {
      return fileUpload.hasFile.value || store.currentImage !== null
    }
    return fileUpload.hasFile.value
  })
  const loading = computed(() => {
    if (useStore && store) {
      return isLoading.value || store.isLoading
    }
    return isLoading.value
  })
  const predictionResult = computed(() => {
    if (useStore && store) {
      return store.currentPrediction || result.value
    }
    return result.value
  })

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
   * Select prediction method
   * @param {string} method - Method name (traditional, yolo, smart, cacaoscan)
   * @returns {void}
   */
  const selectMethod = (method) => {
    const validMethods = ['traditional', 'yolo', 'smart', 'cacaoscan']
    if (!validMethods.includes(method)) {
      throw new Error(`Invalid prediction method: ${method}. Valid methods: ${validMethods.join(', ')}`)
    }
    selectedMethod.value = method
    error.value = null
    if (store) {
      store.clearError()
    }
  }

  /**
   * Set image file for prediction
   * @param {File} file - Image file
   * @returns {Promise<void>}
   */
  const setImage = async (file) => {
    if (!file) {
      fileUpload.removeSelectedFile()
      if (store) {
        store.setCurrentImage(null)
      }
      return
    }

    // Use file upload composable validation
    try {
      await fileUpload.selectFile(file)
      
      if (store && fileUpload.imagePreview.value) {
        store.setCurrentImage(fileUpload.imagePreview.value)
      }
      
      error.value = null
      fileUpload.error.value = ''
    } catch (err) {
      error.value = err.message
      fileUpload.error.value = err.message
      throw err
    }
  }

  /**
   * Validate before execution
   * @returns {Object} Validation result with isValid and error message
   */
  const validateBeforeExecution = () => {
    if (!selectedMethod.value) {
      return { isValid: false, error: 'Debes seleccionar un método de análisis' }
    }

    if (!fileUpload.hasFile.value && !store?.currentImage) {
      return { isValid: false, error: 'Debes subir una imagen para analizar' }
    }

    return { isValid: true, error: null }
  }

  /**
   * Prepares FormData from various input types
   * @param {FormData|File|null} formDataOrFile - Form data, File, or null
   * @returns {FormData} Prepared FormData
   */
  const createImageFormData = (file) => {
    const formData = new FormData()
    formData.append('image', file)
    return formData
  }

  const getImageFromStore = () => {
    return fileUpload.selectedFile.value || store?.currentImage
  }

  const prepareFormData = (formDataOrFile) => {
    if (formDataOrFile instanceof FormData) {
      return formDataOrFile
    }
    
    if (formDataOrFile instanceof File) {
      return createImageFormData(formDataOrFile)
    }
    
    const imageToUse = getImageFromStore()
    if (!imageToUse) {
      throw new Error('No hay imagen disponible para analizar')
    }
    
    if (imageToUse instanceof File) {
      return createImageFormData(imageToUse)
    }
    
    throw new Error('Formato de imagen no soportado para predicción directa')
  }

  /**
   * Executes prediction API call based on selected method
   * @param {FormData} formData - FormData with image
   * @param {Object} predictionOptions - Additional options
   * @returns {Promise<Object>} API result
   */
  const executePredictionApi = async (formData, predictionOptions) => {
    switch (selectedMethod.value) {
      case 'yolo':
        return await predictImageYolo(formData)
      
      case 'smart':
        return await predictImageSmart(formData, {
          returnCroppedImage: true,
          returnTransparentImage: true,
          ...predictionOptions
        })
      
      case 'cacaoscan': {
        const { predictImage: predictImageNew } = await import('@/services/api')
        return { success: true, data: await predictImageNew(formData) }
      }
      
      case 'traditional':
      default:
        return await predictImage(formData)
    }
  }

  /**
   * Handles successful prediction result
   * @param {Object} apiResult - API result
   * @param {number} startTime - Start timestamp
   * @returns {Object} Mapped prediction data
   */
  const handlePredictionSuccess = (apiResult, startTime) => {
    const mappedData = mapApiResponseToPredictionData(apiResult.data, selectedMethod.value)
    result.value = mappedData
    processingTime.value = Date.now() - startTime

    if (store) {
      store.setCurrentPrediction(mappedData)
    }

    if (onSuccess && typeof onSuccess === 'function') {
      onSuccess(mappedData)
    }

    return mappedData
  }

  /**
   * Handles prediction error
   * @param {Error} err - Error object
   * @returns {void}
   */
  const handlePredictionError = (err) => {
    const errorInfo = handleApiError(err, { logError: true })
    error.value = errorInfo.message

    if (store) {
      store.setError(errorInfo.message)
    }

    if (onError && typeof onError === 'function') {
      onError(errorInfo)
    }
  }

  /**
   * Execute prediction
   * @param {FormData|File|null} formDataOrFile - Form data with image, File object, or null to use current image
   * @param {Object} predictionOptions - Additional options for prediction
   * @returns {Promise<Object>} Prediction result
   */
  const executePrediction = async (formDataOrFile = null, predictionOptions = {}) => {
    const validation = validateBeforeExecution()
    if (!validation.isValid) {
      error.value = validation.error
      if (store) {
        store.setError(validation.error)
      }
      throw new Error(validation.error)
    }

    isLoading.value = true
    error.value = null
    result.value = null
    processingTime.value = 0

    if (store) {
      store.isLoading = true
      store.error = null
    }

    const startTime = Date.now()

    try {
      const formData = prepareFormData(formDataOrFile)
      const apiResult = await executePredictionApi(formData, predictionOptions)

      if (apiResult.success) {
        return handlePredictionSuccess(apiResult, startTime)
        }

        throw new Error(apiResult.error || 'Error en la predicción')
    } catch (err) {
      handlePredictionError(err)
      throw err
    } finally {
      isLoading.value = false
      if (store) {
        store.isLoading = false
      }
    }
  }

  /**
   * Get method display information
   * @param {string} method - Method name (optional, uses selectedMethod if not provided)
   * @returns {Object} Method info with title, description, color, and icon
   */
  const getMethodInfo = (method = null) => {
    const methodToCheck = method || selectedMethod.value
    const methods = {
      traditional: {
        title: 'Análisis Tradicional',
        description: 'CNN + Regresión para predicción de peso basada en características visuales tradicionales.',
        color: 'blue',
        icon: 'chart'
      },
      yolo: {
        title: 'YOLOv8',
        description: 'Detección automática del grano con YOLOv8 y estimación de dimensiones físicas.',
        color: 'purple',
        icon: 'eye'
      },
      smart: {
        title: 'YOLOv8 + Recorte Inteligente',
        description: 'Detección con YOLOv8 y recorte inteligente para máxima precisión en dimensiones.',
        color: 'green',
        icon: 'sparkles'
      },
      cacaoscan: {
        title: 'CacaoScan',
        description: 'Método avanzado de análisis con procesamiento optimizado.',
        color: 'green',
        icon: 'sparkles'
      }
    }
    return methods[methodToCheck] || methods.traditional
  }

  /**
   * Check if a method is available
   * @param {string} method - Method name (optional, uses selectedMethod if not provided)
   * @returns {boolean} True if method is available
   */
  const isMethodAvailable = (method = null) => {
    const methodToCheck = method || selectedMethod.value
    const availableMethods = ['traditional', 'yolo', 'smart', 'cacaoscan']
    return availableMethods.includes(methodToCheck)
  }

  /**
   * Reset prediction state
   */
  const reset = () => {
    selectedMethod.value = initialMethod
    isLoading.value = false
    error.value = null
    result.value = null
    processingTime.value = 0
    fileUpload.removeSelectedFile()
    
    if (store) {
      store.clearCurrentPrediction()
      store.setCurrentImage(null)
      store.clearError()
    }
  }

  /**
   * Clear error
   */
  const clearError = () => {
    error.value = null
    if (store) {
      store.clearError()
    }
  }

  return {
    // State
    selectedMethod,
    isLoading: loading,
    error,
    result: predictionResult,
    resultRef: result, // Expose ref directly for testing
    processingTime,
    imageFile,
    imagePreview,

    // Computed
    hasResult,
    hasError,
    hasImage,
    loading,

    // Methods
    selectMethod,
    setImage,
    executePrediction,
    validateBeforeExecution,
    reset,
    clearError,
    getMethodInfo,
    isMethodAvailable,
    mapApiResponseToPredictionData,

    // File upload helpers (re-exported from useFileUpload)
    fileUpload: {
      isDragging: fileUpload.isDragging,
      selectedFile: fileUpload.selectedFile,
      imagePreview: fileUpload.imagePreview,
      error: fileUpload.error,
      hasFile: fileUpload.hasFile,
      formatFileSize: fileUpload.formatFileSize,
      openFileSelector: fileUpload.openFileSelector,
      removeSelectedFile: fileUpload.removeSelectedFile,
      handleDragOver: fileUpload.handleDragOver,
      handleDragLeave: fileUpload.handleDragLeave,
      handleDrop: fileUpload.handleDrop
    },

    // Store access (for advanced usage)
    store
  }
}

