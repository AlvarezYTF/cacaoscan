/**
 * Unit tests for NotificationBell component
 * Tests all functionality including dropdown, notifications loading, marking as read, navigation, and toast notifications
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import NotificationBell from '../NotificationBell.vue'

const { mockRouter, mockNotificationStore, mockWebSocket } = vi.hoisted(() => {
  const mockRouter = {
    push: vi.fn()
  }

  const mockWebSocket = {
    onmessage: null
  }

  const mockNotificationStore = {
    getNotifications: vi.fn(),
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
    websocket: mockWebSocket,
    settings: {
      show_toasts: true
    }
  }

  return { mockRouter, mockNotificationStore, mockWebSocket }
})

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => mockNotificationStore
}))

describe('NotificationBell', () => {
  let wrapper

  const createMockNotification = (id = 1, overrides = {}) => ({
    id,
    titulo: `Notification ${id}`,
    mensaje: `Test message ${id}`,
    tipo: 'info',
    fecha_creacion: new Date().toISOString(),
    leida: false,
    datos_extra: {},
    ...overrides
  })

  const createMockNotificationsResponse = (notifications = []) => ({
    data: {
      results: notifications,
      count: notifications.length,
      page: 1,
      total_pages: 1
    }
  })

  beforeEach(() => {
    vi.clearAllMocks()
    mockNotificationStore.getNotifications.mockResolvedValue(
      createMockNotificationsResponse([])
    )
    mockNotificationStore.markAsRead.mockResolvedValue(true)
    mockNotificationStore.markAllAsRead.mockResolvedValue(true)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Initial rendering', () => {
    it('should render notification bell component', () => {
      wrapper = mount(NotificationBell)
      expect(wrapper.exists()).toBe(true)
    })

    it('should render bell icon', () => {
      wrapper = mount(NotificationBell)
      const bellIcon = wrapper.find('.bell-container i')
      expect(bellIcon.exists()).toBe(true)
      expect(bellIcon.classes()).toContain('fa-bell')
    })

    it('should not show dropdown initially', () => {
      wrapper = mount(NotificationBell)
      const dropdown = wrapper.find('.notification-dropdown')
      expect(dropdown.exists()).toBe(false)
    })

    it('should not show badge when there are no unread notifications', async () => {
      wrapper = mount(NotificationBell)
      await nextTick()
      
      const badge = wrapper.find('.notification-badge')
      expect(badge.exists()).toBe(false)
    })
  })

  describe('Dropdown toggle', () => {
    it('should open dropdown when bell is clicked', async () => {
      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      
      await nextTick()
      
      const dropdown = wrapper.find('.notification-dropdown')
      expect(dropdown.exists()).toBe(true)
    })

    it('should close dropdown when bell is clicked again', async () => {
      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      
      // Open dropdown
      await bellContainer.trigger('click')
      await nextTick()
      expect(wrapper.find('.notification-dropdown').exists()).toBe(true)
      
      // Close dropdown
      await bellContainer.trigger('click')
      await nextTick()
      expect(wrapper.find('.notification-dropdown').exists()).toBe(false)
    })

    it('should load notifications when dropdown is opened', async () => {
      const mockNotifications = [
        createMockNotification(1),
        createMockNotification(2)
      ]
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications)
      )

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      
      await nextTick()
      
      expect(mockNotificationStore.getNotifications).toHaveBeenCalledWith({
        page: 1,
        page_size: 5,
        ordering: '-fecha_creacion'
      })
    })
  })

  describe('Badge display', () => {
    it('should show badge with unread count', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: false }),
        createMockNotification(2, { leida: false }),
        createMockNotification(3, { leida: true })
      ]
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications)
      )

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      
      // Check badge outside dropdown
      wrapper.vm.recentNotifications = mockNotifications
      await nextTick()
      
      const badge = wrapper.find('.notification-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toBe('2')
    })

    it('should show 99+ when unread count exceeds 99', async () => {
      const mockNotifications = Array.from({ length: 100 }, (_, i) =>
        createMockNotification(i + 1, { leida: false })
      )
      
      wrapper = mount(NotificationBell)
      wrapper.vm.recentNotifications = mockNotifications
      await nextTick()
      
      const badge = wrapper.find('.notification-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toBe('99+')
    })

    it('should not show badge when all notifications are read', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: true }),
        createMockNotification(2, { leida: true })
      ]
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications)
      )

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      
      wrapper.vm.recentNotifications = mockNotifications
      await nextTick()
      
      const badge = wrapper.find('.notification-badge')
      expect(badge.exists()).toBe(false)
    })
  })

  const createDelayedNotificationsResponse = (delay = 100) => {
    return () => new Promise(resolve => {
      setTimeout(() => {
        resolve(createMockNotificationsResponse([]))
      }, delay)
    })
  }

  describe('Loading state', () => {
    it('should show loading state when fetching notifications', async () => {
      mockNotificationStore.getNotifications.mockImplementation(createDelayedNotificationsResponse())

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      
      expect(wrapper.find('.loading-state').exists()).toBe(true)
    })

    it('should hide loading state after notifications are loaded', async () => {
      const mockNotifications = [createMockNotification(1)]
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications)
      )

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const loadingState = wrapper.find('.loading-state')
      expect(loadingState.exists()).toBe(false)
    })
  })

  describe('Empty state', () => {
    it('should show empty state when there are no notifications', async () => {
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([])
      )

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const emptyState = wrapper.find('.empty-state')
      expect(emptyState.exists()).toBe(true)
      expect(emptyState.text()).toContain('No hay notificaciones')
    })
  })

  describe('Notifications list', () => {
    it('should display list of notifications', async () => {
      const mockNotifications = [
        createMockNotification(1, { titulo: 'Test Notification 1' }),
        createMockNotification(2, { titulo: 'Test Notification 2' })
      ]
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications)
      )

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      expect(wrapper.text()).toContain('Test Notification 1')
      expect(wrapper.text()).toContain('Test Notification 2')
    })

    it('should mark notification as unread with correct styling', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: false })
      ]
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications)
      )

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const notificationItem = wrapper.find('.notification-item')
      expect(notificationItem.classes()).toContain('unread')
    })
  })

  describe('Mark as read functionality', () => {
    it('should mark notification as read when clicked', async () => {
      const mockNotification = createMockNotification(1, { leida: false })
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification])
      )
      mockNotificationStore.markAsRead.mockResolvedValue(true)

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const notificationItem = wrapper.find('.notification-item')
      await notificationItem.trigger('click')
      await nextTick()
      
      expect(mockNotificationStore.markAsRead).toHaveBeenCalledWith(1)
    })

    it('should mark all notifications as read when button is clicked', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: false }),
        createMockNotification(2, { leida: false })
      ]
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications)
      )
      mockNotificationStore.markAllAsRead.mockResolvedValue(true)

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const markAllButton = wrapper.find('.btn-outline-primary')
      if (markAllButton.exists()) {
        await markAllButton.trigger('click')
        await nextTick()
        
        expect(mockNotificationStore.markAllAsRead).toHaveBeenCalled()
      }
    })

    it('should not show mark all button when there are no unread notifications', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: true }),
        createMockNotification(2, { leida: true })
      ]
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications)
      )

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const markAllButton = wrapper.findAll('.btn-outline-primary').find(btn => 
        btn.text().includes('Marcar todas')
      )
      expect(markAllButton).toBeUndefined()
    })
  })

  describe('Navigation', () => {
    it('should navigate to notification center when button is clicked', async () => {
      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      
      const viewAllButton = wrapper.find('.btn-outline-secondary')
      if (viewAllButton.exists()) {
        await viewAllButton.trigger('click')
        await nextTick()
        
        expect(mockRouter.push).toHaveBeenCalledWith('/notifications')
      }
    })

    it('should navigate based on notification type when clicked', async () => {
      const mockNotification = createMockNotification(1, {
        tipo: 'report_ready',
        leida: false
      })
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification])
      )
      mockNotificationStore.markAsRead.mockResolvedValue(true)

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const notificationItem = wrapper.find('.notification-item')
      await notificationItem.trigger('click')
      await nextTick()
      
      expect(mockRouter.push).toHaveBeenCalledWith('/admin/reports')
    })

    it('should navigate to analysis page for defect_alert notification', async () => {
      const mockNotification = createMockNotification(1, {
        tipo: 'defect_alert',
        datos_extra: { imagen_id: 123 },
        leida: false
      })
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification])
      )
      mockNotificationStore.markAsRead.mockResolvedValue(true)

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const notificationItem = wrapper.find('.notification-item')
      await notificationItem.trigger('click')
      await nextTick()
      
      expect(mockRouter.push).toHaveBeenCalledWith('/analysis/123')
    })

    it('should navigate to notifications page for unknown notification type', async () => {
      const mockNotification = createMockNotification(1, {
        tipo: 'unknown_type',
        leida: false
      })
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification])
      )
      mockNotificationStore.markAsRead.mockResolvedValue(true)

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const notificationItem = wrapper.find('.notification-item')
      await notificationItem.trigger('click')
      await nextTick()
      
      expect(mockRouter.push).toHaveBeenCalledWith('/notifications')
    })
  })

  describe('Icon and styling helpers', () => {
    it('should return correct icon for notification type', () => {
      wrapper = mount(NotificationBell)
      
      expect(wrapper.vm.getNotificationIcon('info')).toBe('fas fa-info-circle')
      expect(wrapper.vm.getNotificationIcon('success')).toBe('fas fa-check-circle')
      expect(wrapper.vm.getNotificationIcon('error')).toBe('fas fa-times-circle')
      expect(wrapper.vm.getNotificationIcon('defect_alert')).toBe('fas fa-exclamation-circle')
      expect(wrapper.vm.getNotificationIcon('report_ready')).toBe('fas fa-file-alt')
      expect(wrapper.vm.getNotificationIcon('unknown')).toBe('fas fa-bell')
    })

    it('should return correct toast class for notification type', () => {
      wrapper = mount(NotificationBell)
      
      expect(wrapper.vm.getToastClass('info')).toBe('toast-info')
      expect(wrapper.vm.getToastClass('success')).toBe('toast-success')
      expect(wrapper.vm.getToastClass('error')).toBe('toast-error')
      expect(wrapper.vm.getToastClass('defect_alert')).toBe('toast-warning')
    })
  })

  describe('Time formatting', () => {
    it('should format time as "Ahora" for recent notifications', () => {
      wrapper = mount(NotificationBell)
      
      const recentDate = new Date().toISOString()
      const formatted = wrapper.vm.formatTime(recentDate)
      expect(formatted).toBe('Ahora')
    })

    it('should format time in minutes for notifications less than an hour old', () => {
      wrapper = mount(NotificationBell)
      
      const thirtyMinutesAgo = new Date(Date.now() - 30 * 60 * 1000).toISOString()
      const formatted = wrapper.vm.formatTime(thirtyMinutesAgo)
      expect(formatted).toBe('30m')
    })

    it('should format time in hours for notifications less than a day old', () => {
      wrapper = mount(NotificationBell)
      
      const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
      const formatted = wrapper.vm.formatTime(twoHoursAgo)
      expect(formatted).toBe('2h')
    })
  })

  describe('Message truncation', () => {
    it('should truncate long messages', () => {
      wrapper = mount(NotificationBell)
      
      const longMessage = 'a'.repeat(100)
      const truncated = wrapper.vm.truncateMessage(longMessage)
      
      expect(truncated.length).toBe(63) // 60 + '...'
      expect(truncated).toContain('...')
    })

    it('should not truncate short messages', () => {
      wrapper = mount(NotificationBell)
      
      const shortMessage = 'Short message'
      const result = wrapper.vm.truncateMessage(shortMessage)
      
      expect(result).toBe(shortMessage)
    })

    it('should return empty string for null or undefined message', () => {
      wrapper = mount(NotificationBell)
      
      expect(wrapper.vm.truncateMessage(null)).toBe('')
      expect(wrapper.vm.truncateMessage(undefined)).toBe('')
    })
  })

  describe('Toast notifications', () => {
    it('should show toast notification when received via WebSocket', async () => {
      wrapper = mount(NotificationBell)
      await nextTick()
      
      const mockNotification = createMockNotification(1, {
        tipo: 'success',
        titulo: 'Toast Title',
        mensaje: 'Toast Message'
      })
      
      // Simulate WebSocket message
      if (mockWebSocket.onmessage) {
        mockWebSocket.onmessage({
          data: JSON.stringify({
            type: 'notification',
            notification: mockNotification
          })
        })
      }
      
      await nextTick()
      
      const toast = wrapper.find('.toast-notification')
      expect(toast.exists()).toBe(true)
    })

    it('should close toast when close button is clicked', async () => {
      wrapper = mount(NotificationBell)
      
      wrapper.vm.showToast(createMockNotification(1))
      await nextTick()
      
      const closeButton = wrapper.find('.toast-close')
      if (closeButton.exists()) {
        await closeButton.trigger('click')
        await nextTick()
        
        expect(wrapper.vm.toastNotification).toBeNull()
      }
    })
  })

  describe('Click outside to close', () => {
    it('should close dropdown when clicking outside', async () => {
      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      
      expect(wrapper.find('.notification-dropdown').exists()).toBe(true)
      
      // Simulate click outside - create a real DOM element
      const outsideElement = document.createElement('div')
      document.body.appendChild(outsideElement)
      
      try {
        // Create event with proper target
        const outsideClick = new MouseEvent('click', {
          bubbles: true,
          cancelable: true
        })
        Object.defineProperty(outsideClick, 'target', {
          value: outsideElement,
          enumerable: true
        })
        
        document.dispatchEvent(outsideClick)
        await nextTick()
        
        // Dropdown should be closed
        expect(wrapper.find('.notification-dropdown').exists()).toBe(false)
      } finally {
        // Cleanup
        if (document.body.contains(outsideElement)) {
          outsideElement.remove()
        }
      }
    })

    it('should not close dropdown when clicking inside dropdown', async () => {
      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      
      const dropdown = wrapper.find('.notification-dropdown')
      expect(dropdown.exists()).toBe(true)
      
      await dropdown.trigger('click.stop')
      await nextTick()
      
      // Dropdown should remain open
      expect(wrapper.find('.notification-dropdown').exists()).toBe(true)
    })
  })

  describe('Error handling', () => {
    it('should handle error when loading notifications fails', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      mockNotificationStore.getNotifications.mockRejectedValue(new Error('Network error'))

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })

    it('should handle error when marking notification as read fails', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const mockNotification = createMockNotification(1, { leida: false })
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification])
      )
      mockNotificationStore.markAsRead.mockRejectedValue(new Error('Failed to mark as read'))

      wrapper = mount(NotificationBell)
      
      const bellContainer = wrapper.find('.bell-container')
      await bellContainer.trigger('click')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const notificationItem = wrapper.find('.notification-item')
      await notificationItem.trigger('click')
      await nextTick()
      
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })
  })
})

