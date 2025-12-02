/**
 * Composable for modal management
 * Provides reusable modal state and methods
 */
import { ref, computed, watch, onUnmounted } from 'vue'

/**
 * Provides modal state and methods
 * @param {Object} options - Modal options
 * @param {boolean} options.closeOnBackdrop - Close modal when clicking backdrop
 * @param {boolean} options.closeOnEscape - Close modal on Escape key
 * @param {Function} options.onOpen - Callback when modal opens
 * @param {Function} options.onClose - Callback when modal closes
 * @returns {Object} Modal composable
 */
export function useModal(options = {}) {
  const {
    closeOnBackdrop = true,
    closeOnEscape = true,
    onOpen = null,
    onClose = null
  } = options

  const isOpen = ref(false)
  const isClosing = ref(false)

  // Computed
  const isVisible = computed(() => isOpen.value && !isClosing.value)

  /**
   * Opens the modal
   * @returns {void}
   */
  const open = () => {
    if (isOpen.value) return
    isOpen.value = true
    isClosing.value = false
    
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden'
    
    if (onOpen) {
      onOpen()
    }
  }

  /**
   * Closes the modal
   * @returns {void}
   */
  const close = () => {
    if (!isOpen.value) return
    
    isClosing.value = true
    
    // Allow body scroll when modal closes
    document.body.style.overflow = ''
    
    // Wait for animation to complete
    setTimeout(() => {
      isOpen.value = false
      isClosing.value = false
      
      if (onClose) {
        onClose()
      }
    }, 300) // Match transition duration
  }

  /**
   * Toggles the modal
   * @returns {void}
   */
  const toggle = () => {
    if (isOpen.value) {
      close()
    } else {
      open()
    }
  }

  /**
   * Handles backdrop click
   * @returns {void}
   */
  const handleBackdropClick = () => {
    if (closeOnBackdrop) {
      close()
    }
  }

  /**
   * Handles Escape key press
   * @param {KeyboardEvent} event - Keyboard event
   * @returns {void}
   */
  const handleEscape = (event) => {
    if (closeOnEscape && event.key === 'Escape' && isOpen.value) {
      close()
    }
  }

  // Watch for Escape key
  watch(isOpen, (open) => {
    if (open && closeOnEscape) {
      document.addEventListener('keydown', handleEscape)
    } else {
      document.removeEventListener('keydown', handleEscape)
    }
  })

  // Cleanup on unmount
  onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
    document.body.style.overflow = ''
  })

  return {
    isOpen,
    isClosing,
    isVisible,
    open,
    close,
    toggle,
    handleBackdropClick,
    handleEscape
  }
}

