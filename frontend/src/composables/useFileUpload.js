/**
 * Composable for file upload functionality
 * Handles drag-drop, preview, validation, and file management
 */
import { ref, computed } from 'vue'
import { validateImageFile, getImageValidationError } from '@/utils/imageValidationUtils'

/**
 * Create file upload composable
 * @param {Object} options - Upload options
 * @param {string[]} options.allowedTypes - Allowed MIME types
 * @param {number} options.maxSize - Maximum file size in bytes
 * @param {number} options.minSize - Minimum file size in bytes
 * @param {boolean} options.enablePreview - Enable image preview (default: true)
 * @returns {Object} Upload state and methods
 */
export function useFileUpload(options = {}) {
  const {
    allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp'],
    maxSize = 20 * 1024 * 1024, // 20MB
    minSize = 1024, // 1KB
    enablePreview = true
  } = options

  // State
  const isDragging = ref(false)
  const selectedFile = ref(null)
  const imagePreview = ref(null)
  const error = ref('')
  const fileInput = ref(null)

  // Computed
  const hasFile = computed(() => !!selectedFile.value)
  const canSubmit = computed(() => hasFile.value && !error.value)

  /**
   * Format file size for display
   * @param {number} bytes - File size in bytes
   * @returns {string} Formatted file size
   */
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'

    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  /**
   * Create image preview from file
   * @param {File} file - File to preview
   * @returns {Promise<string>} Preview data URL
   */
  const createPreview = (file) => {
    return new Promise((resolve, reject) => {
      if (!enablePreview || !file.type.startsWith('image/')) {
        resolve(null)
        return
      }

      const reader = new FileReader()
      reader.onload = (e) => {
        resolve(e.target.result)
      }
      reader.onerror = (err) => {
        reject(err)
      }
      reader.readAsDataURL(file)
    })
  }

  /**
   * Process and validate file
   * @param {File} file - File to process
   * @returns {Promise<boolean>} True if file is valid
   */
  const processFile = async (file) => {
    error.value = ''

    if (!file) {
      error.value = 'Archivo requerido'
      return false
    }

    // Validate file
    const validationError = getImageValidationError(file, {
      allowedTypes,
      maxSize,
      minSize
    })

    if (validationError) {
      error.value = validationError
      return false
    }

    // Set file
    selectedFile.value = file

    // Create preview if enabled
    if (enablePreview) {
      try {
        imagePreview.value = await createPreview(file)
      } catch (err) {
        console.warn('Error creating preview:', err)
        imagePreview.value = null
      }
    }

    return true
  }

  /**
   * Handle drag over event
   * @param {Event} event - Drag event
   */
  const handleDragOver = (event) => {
    event.preventDefault()
    isDragging.value = true
  }

  /**
   * Handle drag leave event
   * @param {Event} event - Drag event
   */
  const handleDragLeave = (event) => {
    event.preventDefault()
    // Only change state if we really left the area
    if (!event.currentTarget.contains(event.relatedTarget)) {
      isDragging.value = false
    }
  }

  /**
   * Handle drop event
   * @param {Event} event - Drop event
   */
  const handleDrop = async (event) => {
    event.preventDefault()
    isDragging.value = false

    const files = Array.from(event.dataTransfer.files)
    if (files.length > 0) {
      await processFile(files[0])
    }
  }

  /**
   * Open file selector
   */
  const openFileSelector = () => {
    if (fileInput.value) {
      fileInput.value.click()
    }
  }

  /**
   * Handle file select from input
   * @param {Event} event - Change event
   */
  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files)
    if (files.length > 0) {
      await processFile(files[0])
    }
    // Clear input to allow selecting same file again
    event.target.value = ''
  }

  /**
   * Remove selected file
   */
  const removeSelectedFile = () => {
    selectedFile.value = null
    imagePreview.value = null
    error.value = ''
  }

  /**
   * Reset upload state
   */
  const reset = () => {
    removeSelectedFile()
    isDragging.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }

  /**
   * Get file data for FormData
   * @param {Object} metadata - Additional metadata to include
   * @returns {FormData} FormData with file and metadata
   */
  const getFormData = (metadata = {}) => {
    const formData = new FormData()
    
    if (selectedFile.value) {
      formData.append('image', selectedFile.value)
    }

    // Add metadata
    Object.entries(metadata).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        formData.append(key, value)
      }
    })

    return formData
  }

  return {
    // State
    isDragging,
    selectedFile,
    imagePreview,
    error,
    fileInput,

    // Computed
    hasFile,
    canSubmit,

    // Methods
    formatFileSize,
    processFile,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    openFileSelector,
    handleFileSelect,
    removeSelectedFile,
    reset,
    getFormData
  }
}

