/**
 * Composable for notifications
 * Wrapper around notifications store with convenient methods
 */
import { computed } from 'vue'
import { useNotificationsStore } from '@/stores/notifications'

/**
 * Provides convenient notification methods
 * @returns {Object} Notification methods and store state
 */
export function useNotifications() {
  const store = useNotificationsStore()

  /**
   * Shows a success notification (local toast, not persisted)
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds (optional)
   * @returns {void}
   */
  const showSuccess = (message, duration = 5000) => {
    if (typeof globalThis !== 'undefined' && globalThis.showNotification) {
      globalThis.showNotification({
        type: 'success',
        title: 'Éxito',
        message: message,
        duration: duration
      })
    } else {
      }
  }

  /**
   * Shows an error notification (local toast, not persisted)
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds (optional)
   * @returns {void}
   */
  const showError = (message, duration = 8000) => {
    if (typeof globalThis !== 'undefined' && globalThis.showNotification) {
      globalThis.showNotification({
        type: 'error',
        title: 'Error',
        message: message,
        duration: duration
      })
    } else {
      }
  }

  /**
   * Shows a warning notification (local toast, not persisted)
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds (optional)
   * @returns {void}
   */
  const showWarning = (message, duration = 6000) => {
    if (typeof globalThis !== 'undefined' && globalThis.showNotification) {
      globalThis.showNotification({
        type: 'warning',
        title: 'Advertencia',
        message: message,
        duration: duration
      })
    } else {
      }
  }

  /**
   * Shows an info notification (local toast, not persisted)
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds (optional)
   * @returns {void}
   */
  const showInfo = (message, duration = 5000) => {
    if (typeof globalThis !== 'undefined' && globalThis.showNotification) {
      globalThis.showNotification({
        type: 'info',
        title: 'Información',
        message: message,
        duration: duration
      })
    } else {
      }
  }

  /**
   * Clears all notifications
   * @returns {void}
   */
  const clearAll = () => {
    store.reset()
  }

  /**
   * Creates a persistent notification in the backend
   * Use this only when you need to save a notification to the database
   * For temporary messages, use showSuccess/showError/showWarning/showInfo instead
   * @param {Object} notificationData - Notification data (user, tipo, titulo, mensaje, datos_extra)
   * @returns {Promise} Promise that resolves with the created notification
   */
  const createPersistentNotification = async (notificationData) => {
    return await store.createNotification(notificationData)
  }

  return {
    // Convenience methods for local toast notifications (not persisted)
    showSuccess,
    showError,
    showWarning,
    showInfo,
    clearAll,
    
    // Method for creating persistent notifications in backend
    createPersistentNotification,
    
    // Store state (read-only access)
    notifications: computed(() => store.notifications),
    unreadCount: computed(() => store.unreadCount),
    loading: computed(() => store.loading),
    error: computed(() => store.error),
    
    // Store methods (for advanced usage)
    store
  }
}

