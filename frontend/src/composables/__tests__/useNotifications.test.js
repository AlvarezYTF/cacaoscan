/**
 * Unit tests for useNotifications composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
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

vi.mock('@/stores/notifications', () => ({
  useNotificationsStore: () => mockStore
}))

describe('useNotifications', () => {
  let notifications

  beforeEach(() => {
    vi.clearAllMocks()
    mockStore.notifications = []
    mockStore.unreadCount = 0
    notifications = useNotifications()
  })

  describe('showSuccess', () => {
    it('should create success notification', () => {
      notifications.showSuccess('Operation successful')
      
      expect(mockStore.createNotification).toHaveBeenCalledWith({
        tipo: 'success',
        mensaje: 'Operation successful',
        duracion: null
      })
    })

    it('should create success notification with duration', () => {
      notifications.showSuccess('Operation successful', 5000)
      
      expect(mockStore.createNotification).toHaveBeenCalledWith({
        tipo: 'success',
        mensaje: 'Operation successful',
        duracion: 5000
      })
    })
  })

  describe('showError', () => {
    it('should create error notification', () => {
      notifications.showError('Operation failed')
      
      expect(mockStore.createNotification).toHaveBeenCalledWith({
        tipo: 'error',
        mensaje: 'Operation failed',
        duracion: null
      })
    })
  })

  describe('showWarning', () => {
    it('should create warning notification', () => {
      notifications.showWarning('Warning message')
      
      expect(mockStore.createNotification).toHaveBeenCalledWith({
        tipo: 'warning',
        mensaje: 'Warning message',
        duracion: null
      })
    })
  })

  describe('showInfo', () => {
    it('should create info notification', () => {
      notifications.showInfo('Info message')
      
      expect(mockStore.createNotification).toHaveBeenCalledWith({
        tipo: 'info',
        mensaje: 'Info message',
        duracion: null
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

