/**
 * Composable for dataset operations
 * Centralizes dataset management logic
 */
import { ref, computed } from 'vue'
import { getDatasetImages, getDatasetImage, updateDatasetImage, deleteDatasetImage } from '@/services/datasetApi'
import { handleApiError } from '@/services/apiErrorHandler'

/**
 * Create dataset composable
 * @param {Object} options - Options
 * @param {Function} options.onImageUpdate - Callback when image is updated
 * @param {Function} options.onImageDelete - Callback when image is deleted
 * @returns {Object} Dataset state and methods
 */
export function useDataset(options = {}) {
  const {
    onImageUpdate = null,
    onImageDelete = null
  } = options

  // State
  const images = ref([])
  const currentImage = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const filters = ref({})
  const pagination = ref({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    itemsPerPage: 20
  })

  // Computed
  const hasImages = computed(() => images.value.length > 0)
  const hasCurrentImage = computed(() => currentImage.value !== null)
  const hasError = computed(() => error.value !== null)

  /**
   * Load dataset images
   * @param {Object} filterParams - Filter parameters
   * @param {number} page - Page number
   * @param {number} pageSize - Page size
   * @returns {Promise<Object>} Response data
   */
  const loadImages = async (filterParams = {}, page = 1, pageSize = 20) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await getDatasetImages(filterParams, page, pageSize)

      if (page === 1) {
        images.value = response.results || []
      } else {
        images.value = [...images.value, ...(response.results || [])]
      }

      pagination.value = {
        currentPage: page,
        totalPages: Math.ceil((response.count || 0) / pageSize),
        totalItems: response.count || 0,
        itemsPerPage: pageSize
      }

      filters.value = { ...filterParams }

      return response
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load single image details
   * @param {number} imageId - Image ID
   * @returns {Promise<Object>} Image data
   */
  const loadImage = async (imageId) => {
    isLoading.value = true
    error.value = null

    try {
      const imageData = await getDatasetImage(imageId)
      currentImage.value = imageData
      return imageData
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update image
   * @param {number} imageId - Image ID
   * @param {Object} updateData - Data to update
   * @returns {Promise<Object>} Updated image
   */
  const updateImage = async (imageId, updateData) => {
    isLoading.value = true
    error.value = null

    try {
      const updatedImage = await updateDatasetImage(imageId, updateData)

      // Update in local state
      const index = images.value.findIndex(img => img.id === imageId)
      if (index !== -1) {
        images.value[index] = updatedImage
      }

      if (currentImage.value?.id === imageId) {
        currentImage.value = updatedImage
      }

      if (onImageUpdate && typeof onImageUpdate === 'function') {
        onImageUpdate(updatedImage)
      }

      return updatedImage
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete image
   * @param {number} imageId - Image ID
   * @returns {Promise<void>}
   */
  const deleteImage = async (imageId) => {
    isLoading.value = true
    error.value = null

    try {
      await deleteDatasetImage(imageId)

      // Remove from local state
      images.value = images.value.filter(img => img.id !== imageId)

      if (currentImage.value?.id === imageId) {
        currentImage.value = null
      }

      // Update pagination
      pagination.value.totalItems = Math.max(0, pagination.value.totalItems - 1)

      if (onImageDelete && typeof onImageDelete === 'function') {
        onImageDelete(imageId)
      }
    } catch (err) {
      const errorInfo = handleApiError(err, { logError: true })
      error.value = errorInfo.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Set filters
   * @param {Object} newFilters - New filter values
   */
  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  /**
   * Clear filters
   */
  const clearFilters = () => {
    filters.value = {}
  }

  /**
   * Set current image
   * @param {Object} image - Image object
   */
  const setCurrentImage = (image) => {
    currentImage.value = image
  }

  /**
   * Clear current image
   */
  const clearCurrentImage = () => {
    currentImage.value = null
  }

  /**
   * Reset state
   */
  const reset = () => {
    images.value = []
    currentImage.value = null
    isLoading.value = false
    error.value = null
    filters.value = {}
    pagination.value = {
      currentPage: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 20
    }
  }

  /**
   * Clear error
   */
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    images,
    currentImage,
    isLoading,
    error,
    filters,
    pagination,

    // Computed
    hasImages,
    hasCurrentImage,
    hasError,

    // Methods
    loadImages,
    loadImage,
    updateImage,
    deleteImage,
    setFilters,
    clearFilters,
    setCurrentImage,
    clearCurrentImage,
    reset,
    clearError
  }
}

