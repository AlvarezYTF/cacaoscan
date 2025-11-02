/**
 * Composable para manejar modales de forma reutilizable
 */
import { ref } from 'vue'

export function useModal(modalId) {
  const modalContainer = ref(null)
  const isOpen = ref(false)

  /**
   * Abre el modal
   */
  const openModal = () => {
    if (modalContainer.value) {
      const modalElement = modalContainer.value
      modalElement.classList.remove('hidden')
      modalElement.setAttribute('aria-hidden', 'false')
    }
    isOpen.value = true
  }

  /**
   * Cierra el modal
   */
  const closeModal = () => {
    if (modalContainer.value) {
      const modalElement = modalContainer.value
      modalElement.classList.add('hidden')
      modalElement.setAttribute('aria-hidden', 'true')
    }
    isOpen.value = false
  }

  /**
   * Toggle del modal
   */
  const toggleModal = () => {
    if (isOpen.value) {
      closeModal()
    } else {
      openModal()
    }
  }

  return {
    modalContainer,
    isOpen,
    openModal,
    closeModal,
    toggleModal
  }
}

