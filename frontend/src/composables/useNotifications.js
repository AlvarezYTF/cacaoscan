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
   * Shows a success notification
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds (optional)
   * @returns {void}
   */
  const showSuccess = (message, duration = null) => {
    store.createNotification({
      tipo: 'success',
      mensaje: message,
      duracion: duration
    })
  }

  /**
   * Shows an error notification
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds (optional)
   * @returns {void}
   */
  const showError = (message, duration = null) => {
    store.createNotification({
      tipo: 'error',
      mensaje: message,
      duracion: duration
    })
  }

  /**
   * Shows a warning notification
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds (optional)
   * @returns {void}
   */
  const showWarning = (message, duration = null) => {
    store.createNotification({
      tipo: 'warning',
      mensaje: message,
      duracion: duration
    })
  }

  /**
   * Shows an info notification
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds (optional)
   * @returns {void}
   */
  const showInfo = (message, duration = null) => {
    store.createNotification({
      tipo: 'info',
      mensaje: message,
      duracion: duration
    })
  }

  /**
   * Clears all notifications
   * @returns {void}
   */
  const clearAll = () => {
    store.reset()
  }

  return {
    // Convenience methods
    showSuccess,
    showError,
    showWarning,
    showInfo,
    clearAll,
    
    // Store state (read-only access)
    notifications: computed(() => store.notifications),
    unreadCount: computed(() => store.unreadCount),
    loading: computed(() => store.loading),
    error: computed(() => store.error),
    
    // Store methods (for advanced usage)
    store
  }
}

