/**
 * Unit tests for useNotifications composable
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { useNotifications } from '../useNotifications.js'

// Mock notifications store
const mockStore = {
  createNotification: vi.fn(),
  reset: vi.fn(),
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null
}

// Mock globalThis.showNotification
const mockShowNotification = vi.fn()

vi.mock('@/stores/notifications', () => ({
  useNotificationsStore: () => mockStore
}))

describe('useNotifications', () => {
  let notifications

  beforeEach(() => {
    vi.clearAllMocks()
    mockStore.notifications = []
    mockStore.unreadCount = 0
    // Setup globalThis.showNotification mock
    globalThis.showNotification = mockShowNotification
    notifications = useNotifications()
  })

  afterEach(() => {
    delete globalThis.showNotification
  })

  describe('showSuccess', () => {
    it('should create success notification', () => {
      notifications.showSuccess('Operation successful')
      
      expect(mockShowNotification).toHaveBeenCalledWith({
        type: 'success',
        title: 'Éxito',
        message: 'Operation successful',
        duration: 5000
      })
    })

    it('should create success notification with duration', () => {
      notifications.showSuccess('Operation successful', 5000)
      
      expect(mockShowNotification).toHaveBeenCalledWith({
        type: 'success',
        title: 'Éxito',
        message: 'Operation successful',
        duration: 5000
      })
    })
  })

  describe('showError', () => {
    it('should create error notification', () => {
      notifications.showError('Operation failed')
      
      expect(mockShowNotification).toHaveBeenCalledWith({
        type: 'error',
        title: 'Error',
        message: 'Operation failed',
        duration: 8000
      })
    })
  })

  describe('showWarning', () => {
    it('should create warning notification', () => {
      notifications.showWarning('Warning message')
      
      expect(mockShowNotification).toHaveBeenCalledWith({
        type: 'warning',
        title: 'Advertencia',
        message: 'Warning message',
        duration: 6000
      })
    })
  })

  describe('showInfo', () => {
    it('should create info notification', () => {
      notifications.showInfo('Info message')
      
      expect(mockShowNotification).toHaveBeenCalledWith({
        type: 'info',
        title: 'Información',
        message: 'Info message',
        duration: 5000
      })
    })
  })

  describe('clearAll', () => {
    it('should reset store', () => {
      notifications.clearAll()
      
      expect(mockStore.reset).toHaveBeenCalled()
    })
  })

  describe('computed properties', () => {
    it('should expose notifications', () => {
      mockStore.notifications = [{ id: 1, mensaje: 'Test' }]
      
      expect(notifications.notifications.value).toEqual([{ id: 1, mensaje: 'Test' }])
    })

    it('should expose unreadCount', () => {
      mockStore.unreadCount = 5
      
      expect(notifications.unreadCount.value).toBe(5)
    })

    it('should expose loading', () => {
      mockStore.loading = true
      
      expect(notifications.loading.value).toBe(true)
    })

    it('should expose error', () => {
      mockStore.error = 'Error message'
      
      expect(notifications.error.value).toBe('Error message')
    })
  })
})

