/**
 * Composable for image handling operations
 * Provides image upload, validation, preview, and gallery functionality
 */
import { ref, computed } from 'vue'
import { isValidImageFile, validateImageSize, validateImageType } from '@/utils/imageValidationUtils'

/**
 * Provides image handling state and methods
 * @returns {Object} Image handling composable
 */
export function useImageHandling() {
  // State
  const selectedImages = ref([])
  const imagePreviews = ref([])
  const uploadProgress = ref(0)
  const isUploading = ref(false)
  const uploadError = ref(null)
  const currentImageIndex = ref(0)

  // Computed
  const hasImages = computed(() => selectedImages.value.length > 0)
  const currentImage = computed(() => {
    if (selectedImages.value.length === 0) return null
    return selectedImages.value[currentImageIndex.value] || null
  })
  const currentPreview = computed(() => {
    if (imagePreviews.value.length === 0) return null
    return imagePreviews.value[currentImageIndex.value] || null
  })
  const canNavigatePrevious = computed(() => currentImageIndex.value > 0)
  const canNavigateNext = computed(() => currentImageIndex.value < selectedImages.value.length - 1)

  /**
   * Validates an image file
   * @param {File} file - Image file to validate
   * @returns {Object} Validation result with isValid and error message
   */
  const validateImage = (file) => {
    if (!file) {
      return { isValid: false, error: 'No se seleccionó ningún archivo' }
    }

    // Type validation
    const typeValidation = validateImageType(file)
    if (!typeValidation.isValid) {
      return typeValidation
    }

    // Size validation
    const sizeValidation = validateImageSize(file)
    if (!sizeValidation.isValid) {
      return sizeValidation
    }

    // General validation
    const generalValidation = isValidImageFile(file)
    if (!generalValidation.isValid) {
      return generalValidation
    }

    return { isValid: true, error: null }
  }

  /**
   * Adds images to the selection
   * @param {File|Array<File>} files - Image file(s) to add
   * @returns {Object} Result with added files and errors
   */
  const addImages = (files) => {
    const fileArray = Array.isArray(files) ? files : [files]
    const added = []
    const errors = []

    for (const file of fileArray) {
      const validation = validateImage(file)
      if (validation.isValid) {
        selectedImages.value.push(file)
        added.push(file)
        createPreview(file)
      } else {
        errors.push({ file: file.name, error: validation.error })
      }
    }

    return { added, errors }
  }

  /**
   * Creates a preview URL for an image file
   * @param {File} file - Image file
   * @returns {string} Preview URL
   */
  const createPreview = (file) => {
    if (!file) return null

    const reader = new FileReader()
    return new Promise((resolve, reject) => {
      reader.onload = (e) => {
        const previewUrl = e.target.result
        imagePreviews.value.push(previewUrl)
        resolve(previewUrl)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  /**
   * Removes an image from selection
   * @param {number} index - Index of image to remove
   * @returns {void}
   */
  const removeImage = (index) => {
    if (index < 0 || index >= selectedImages.value.length) return

    // Revoke preview URL to free memory
    if (imagePreviews.value[index]) {
      URL.revokeObjectURL(imagePreviews.value[index])
    }

    selectedImages.value.splice(index, 1)
    imagePreviews.value.splice(index, 1)

    // Adjust current index if needed
    if (currentImageIndex.value >= selectedImages.value.length) {
      currentImageIndex.value = Math.max(0, selectedImages.value.length - 1)
    }
  }

  /**
   * Clears all selected images
   * @returns {void}
   */
  const clearImages = () => {
    // Revoke all preview URLs
    for (const url of imagePreviews.value) {
      if (url.startsWith('blob:')) {
        URL.revokeObjectURL(url)
      }
    }

    selectedImages.value = []
    imagePreviews.value = []
    currentImageIndex.value = 0
    uploadProgress.value = 0
    uploadError.value = null
  }

  /**
   * Navigates to previous image
   * @returns {void}
   */
  const previousImage = () => {
    if (canNavigatePrevious.value) {
      currentImageIndex.value--
    }
  }

  /**
   * Navigates to next image
   * @returns {void}
   */
  const nextImage = () => {
    if (canNavigateNext.value) {
      currentImageIndex.value++
    }
  }

  /**
   * Sets current image index
   * @param {number} index - Index to set
   * @returns {void}
   */
  const setCurrentImageIndex = (index) => {
    if (index >= 0 && index < selectedImages.value.length) {
      currentImageIndex.value = index
    }
  }

  /**
   * Uploads images with progress tracking
   * @param {Function} uploadFn - Upload function that accepts (file, onProgress) and returns Promise
   * @returns {Promise<Array>} Array of upload results
   */
  const uploadImages = async (uploadFn) => {
    if (!uploadFn || typeof uploadFn !== 'function') {
      throw new Error('Upload function is required')
    }

    if (selectedImages.value.length === 0) {
      throw new Error('No images to upload')
    }

    isUploading.value = true
    uploadError.value = null
    uploadProgress.value = 0

    try {
      const results = []

      for (let i = 0; i < selectedImages.value.length; i++) {
        const file = selectedImages.value[i]
        const progressCallback = (progress) => {
          const totalProgress = ((i + progress / 100) / selectedImages.value.length) * 100
          uploadProgress.value = Math.round(totalProgress)
        }

        try {
          const result = await uploadFn(file, progressCallback)
          results.push({ success: true, file, result })
        } catch (error) {
          results.push({ success: false, file, error: error.message })
        }
      }

      uploadProgress.value = 100
      return results
    } catch (error) {
      uploadError.value = error.message || 'Error al subir las imágenes'
      throw error
    } finally {
      isUploading.value = false
    }
  }

  /**
   * Gets image dimensions
   * @param {File|string} image - Image file or URL
   * @returns {Promise<Object>} Image dimensions { width, height }
   */
  const getImageDimensions = (image) => {
    return new Promise((resolve, reject) => {
      const img = new Image()
      
      img.onload = () => {
        resolve({ width: img.width, height: img.height })
      }
      
      img.onerror = reject

      if (typeof image === 'string') {
        img.src = image
      } else if (image instanceof File) {
        const reader = new FileReader()
        reader.onload = (e) => {
          img.src = e.target.result
        }
        reader.onerror = reject
        reader.readAsDataURL(image)
      } else {
        reject(new Error('Invalid image source'))
      }
    })
  }

  return {
    // State
    selectedImages,
    imagePreviews,
    uploadProgress,
    isUploading,
    uploadError,
    currentImageIndex,
    hasImages,
    currentImage,
    currentPreview,
    canNavigatePrevious,
    canNavigateNext,

    // Methods
    validateImage,
    addImages,
    createPreview,
    removeImage,
    clearImages,
    previousImage,
    nextImage,
    navigatePrevious: previousImage,
    navigateNext: nextImage,
    setCurrentImageIndex,
    uploadImages,
    getImageDimensions
  }
}

