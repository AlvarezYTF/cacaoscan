/**
 * Composable for prediction flow orchestration
 * Handles method selection, image upload, prediction execution, and results
 */
import { ref, computed } from 'vue'
import { usePredictionStore } from '@/stores/prediction'
import { predictImage, predictImageYolo, predictImageSmart } from '@/services/predictionApi'

/**
 * Provides prediction flow state and methods
 * @returns {Object} Prediction flow state and methods
 */
export function usePredictionFlow() {
  const store = usePredictionStore()

  // Local state
  const selectedMethod = ref('traditional')
  const imageFile = ref(null)
  const imagePreview = ref(null)
  const isExecuting = ref(false)
  const executionError = ref(null)

  // Computed from store
  const predictionResult = computed(() => store.currentPrediction)
  const loading = computed(() => store.isLoading || isExecuting.value)
  const error = computed(() => executionError.value || store.error || store.uploadError)
  const hasImage = computed(() => imageFile.value !== null || store.currentImage !== null)
  const hasResult = computed(() => predictionResult.value !== null)

  /**
   * Selects a prediction method
   * @param {string} method - Method name (traditional, yolo, smart)
   * @returns {void}
   */
  const selectMethod = (method) => {
    if (!['traditional', 'yolo', 'smart'].includes(method)) {
      throw new Error(`Invalid prediction method: ${method}`)
    }
    selectedMethod.value = method
    executionError.value = null
  }

  /**
   * Sets the image file for prediction
   * @param {File} file - Image file
   * @returns {Promise<void>}
   */
  const setImage = async (file) => {
    if (!file) {
      imageFile.value = null
      imagePreview.value = null
      store.setCurrentImage(null)
      return
    }

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if (!validTypes.includes(file.type)) {
      throw new Error('Tipo de archivo no válido. Solo se permiten imágenes (JPG, PNG, WEBP)')
    }

    // Validate file size (max 20MB)
    const maxSize = 20 * 1024 * 1024
    if (file.size > maxSize) {
      throw new Error('El archivo es demasiado grande. El tamaño máximo es 20MB')
    }

    imageFile.value = file

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
      store.setCurrentImage(e.target.result)
    }
    reader.readAsDataURL(file)

    executionError.value = null
  }

  /**
   * Validates that all requirements are met for prediction
   * @returns {Object} Validation result with isValid and error message
   */
  const validateBeforeExecution = () => {
    if (!selectedMethod.value) {
      return { isValid: false, error: 'Debes seleccionar un método de análisis' }
    }

    if (!imageFile.value && !store.currentImage) {
      return { isValid: false, error: 'No hay imagen disponible para analizar' }
    }

    return { isValid: true, error: null }
  }

  /**
   * Executes the prediction based on selected method
   * @returns {Promise<void>}
   */
  const executePrediction = async () => {
    const validation = validateBeforeExecution()
    if (!validation.isValid) {
      executionError.value = validation.error
      throw new Error(validation.error)
    }

    isExecuting.value = true
    executionError.value = null

    try {
      const imageToUse = imageFile.value || store.currentImage
      
      if (!imageToUse) {
        throw new Error('No hay imagen disponible para analizar')
      }

      let result

      switch (selectedMethod.value) {
        case 'traditional':
          result = await predictImage(imageToUse)
          break
        case 'yolo':
          result = await predictImageYolo(imageToUse)
          break
        case 'smart':
          result = await predictImageSmart(imageToUse)
          break
        default:
          throw new Error(`Método de predicción no soportado: ${selectedMethod.value}`)
      }

      // Store the result
      store.setCurrentPrediction(result.data || result)
    } catch (err) {
      executionError.value = err.response?.data?.detail || err.message || 'Error al ejecutar la predicción'
      store.setError(executionError.value)
      throw err
    } finally {
      isExecuting.value = false
    }
  }

  /**
   * Resets the prediction flow to initial state
   * @returns {void}
   */
  const reset = () => {
    selectedMethod.value = 'traditional'
    imageFile.value = null
    imagePreview.value = null
    isExecuting.value = false
    executionError.value = null
    store.clearCurrentPrediction()
    store.setCurrentImage(null)
  }

  /**
   * Clears only the error state
   * @returns {void}
   */
  const clearError = () => {
    executionError.value = null
    store.clearError()
  }

  /**
   * Gets method display information
   * @param {string} method - Method name
   * @returns {Object} Method info with title and description
   */
  const getMethodInfo = (method) => {
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
      }
    }
    return methods[method] || methods.traditional
  }

  /**
   * Checks if a method is available
   * @param {string} method - Method name
   * @returns {boolean} True if method is available
   */
  const isMethodAvailable = (method) => {
    // All methods are available by default
    // Can be extended to check feature flags or user permissions
    return ['traditional', 'yolo', 'smart'].includes(method)
  }

  return {
    // State
    selectedMethod,
    imageFile,
    imagePreview,
    isExecuting,
    executionError,
    predictionResult,
    loading,
    error,
    hasImage,
    hasResult,

    // Methods
    selectMethod,
    setImage,
    executePrediction,
    reset,
    clearError,
    validateBeforeExecution,
    getMethodInfo,
    isMethodAvailable,

    // Store access (for advanced usage)
    store
  }
}

