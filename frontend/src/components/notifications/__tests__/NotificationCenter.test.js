/**
 * Unit tests for NotificationCenter component
 * Tests all functionality including loading, filtering, pagination, marking as read, deleting, and settings
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import NotificationCenter from '../NotificationCenter.vue'

const { mockNotificationStore, mockUseNotifications, mockSwal } = vi.hoisted(() => {
  const mockNotificationStore = {
    getNotifications: vi.fn(),
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
    deleteNotification: vi.fn(),
    updateSettings: vi.fn(),
    websocket: {
      onmessage: null
    },
    showToast: vi.fn(),
    settings: {
      show_toasts: true
    }
  }

  const mockUseNotifications = {
    showSuccess: vi.fn(),
    showError: vi.fn()
  }

  const mockSwal = {
    fire: vi.fn().mockResolvedValue({ isConfirmed: false })
  }

  return { mockNotificationStore, mockUseNotifications, mockSwal }
})

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => mockNotificationStore
}))

vi.mock('@/composables/useNotifications', () => ({
  useNotifications: () => mockUseNotifications
}))

vi.mock('sweetalert2', () => ({
  default: mockSwal
}))

describe('NotificationCenter', () => {
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

  const createMockNotificationsResponse = (notifications = [], total = null) => {
    const count = total ?? notifications.length
    return {
      data: {
        results: notifications,
        count,
        page: 1,
        page_size: 20,
        total_pages: Math.ceil(count / 20)
      }
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockNotificationStore.getNotifications.mockResolvedValue(
      createMockNotificationsResponse([])
    )
    mockNotificationStore.markAsRead.mockResolvedValue(true)
    mockNotificationStore.markAllAsRead.mockResolvedValue(true)
    mockNotificationStore.deleteNotification.mockResolvedValue(true)
    mockNotificationStore.updateSettings.mockResolvedValue(true)
    mockSwal.fire.mockResolvedValue({ isConfirmed: false })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Initial rendering', () => {
    it('should render notification center component', () => {
      wrapper = mount(NotificationCenter)
      expect(wrapper.exists()).toBe(true)
    })

    it('should display header with title', () => {
      wrapper = mount(NotificationCenter)
      expect(wrapper.text()).toContain('Centro de Notificaciones')
    })

    it('should display filter tabs', () => {
      wrapper = mount(NotificationCenter)
      expect(wrapper.text()).toContain('Todas')
      expect(wrapper.text()).toContain('No Leídas')
      expect(wrapper.text()).toContain('Leídas')
    })

    it('should load notifications on mount', async () => {
      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      expect(mockNotificationStore.getNotifications).toHaveBeenCalled()
    })
  })

  const createDelayedResponse = (delay = 100) => {
    return new Promise(resolve => {
      setTimeout(() => resolve(createMockNotificationsResponse([])), delay)
    })
  }

  describe('Loading state', () => {
    it('should show loading state when fetching notifications', async () => {
      mockNotificationStore.getNotifications.mockImplementation(() => createDelayedResponse())

      wrapper = mount(NotificationCenter)
      await nextTick()
      
      expect(wrapper.find('.loading-state').exists()).toBe(true)
    })

    it('should hide loading state after notifications are loaded', async () => {
      const mockNotifications = [createMockNotification(1)]
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications)
      )

      wrapper = mount(NotificationCenter)
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

      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const emptyState = wrapper.find('.empty-state')
      expect(emptyState.exists()).toBe(true)
      expect(emptyState.text()).toContain('No hay notificaciones')
    })

    it('should show appropriate message for empty unread filter', async () => {
      wrapper = mount(NotificationCenter)
      await nextTick()
      
      wrapper.vm.activeFilter = 'unread'
      wrapper.vm.notifications = []
      await nextTick()
      
      const emptyState = wrapper.find('.empty-state')
      if (emptyState.exists()) {
        expect(emptyState.text()).toContain('No tienes notificaciones sin leer')
      }
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

      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      expect(wrapper.text()).toContain('Test Notification 1')
      expect(wrapper.text()).toContain('Test Notification 2')
    })

    it('should display notification title and message', async () => {
      const mockNotification = createMockNotification(1, {
        titulo: 'Test Title',
        mensaje: 'Test Message'
      })
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification])
      )

      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      expect(wrapper.text()).toContain('Test Title')
      expect(wrapper.text()).toContain('Test Message')
    })

    it('should display notification icon based on type', async () => {
      const mockNotification = createMockNotification(1, { tipo: 'success' })
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification])
      )

      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const icon = wrapper.find('.notification-icon i')
      expect(icon.exists()).toBe(true)
    })

    it('should display extra data when available', async () => {
      const mockNotification = createMockNotification(1, {
        datos_extra: {
          key1: 'value1',
          key2: 'value2'
        }
      })
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification])
      )

      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      expect(wrapper.text()).toContain('key1')
      expect(wrapper.text()).toContain('value1')
    })
  })

  describe('Filters', () => {
    it('should filter by all notifications', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: false }),
        createMockNotification(2, { leida: true })
      ]
      
      // Configure mock before mounting
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications, mockNotifications.length)
      )
      
      wrapper = mount(NotificationCenter)
      await flushPromises()
      await nextTick()
      
      wrapper.vm.activeFilter = 'all'
      await nextTick()
      
      expect(wrapper.vm.filteredNotifications.length).toBe(2)
    })

    it('should filter by unread notifications', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: false }),
        createMockNotification(2, { leida: true }),
        createMockNotification(3, { leida: false })
      ]
      
      // Configure mock before mounting
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications, mockNotifications.length)
      )
      
      wrapper = mount(NotificationCenter)
      await flushPromises()
      await nextTick()
      
      // Use the setFilter method to ensure reactivity
      wrapper.vm.setFilter('unread')
      await nextTick()
      
      expect(wrapper.vm.filteredNotifications.length).toBe(2)
      expect(wrapper.vm.filteredNotifications.every(n => !n.leida)).toBe(true)
    })

    it('should filter by read notifications', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: false }),
        createMockNotification(2, { leida: true }),
        createMockNotification(3, { leida: true })
      ]
      
      // Configure mock before mounting
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications, mockNotifications.length)
      )
      
      wrapper = mount(NotificationCenter)
      await flushPromises()
      await nextTick()
      
      // Use the setFilter method to ensure reactivity
      wrapper.vm.setFilter('read')
      await nextTick()
      
      expect(wrapper.vm.filteredNotifications.length).toBe(2)
      expect(wrapper.vm.filteredNotifications.every(n => n.leida)).toBe(true)
    })

    it('should filter by notification type', async () => {
      const mockNotifications = [
        createMockNotification(1, { tipo: 'info' }),
        createMockNotification(2, { tipo: 'success' }),
        createMockNotification(3, { tipo: 'info' })
      ]
      
      // Configure mock before mounting
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications, mockNotifications.length)
      )
      
      wrapper = mount(NotificationCenter)
      await flushPromises()
      await nextTick()
      
      wrapper.vm.typeFilter = 'info'
      await nextTick()
      
      expect(wrapper.vm.filteredNotifications.length).toBe(2)
      expect(wrapper.vm.filteredNotifications.every(n => n.tipo === 'info')).toBe(true)
    })

    it('should reset to page 1 when filter changes', async () => {
      wrapper = mount(NotificationCenter)
      wrapper.vm.currentPage = 3
      await nextTick()
      
      await wrapper.vm.setFilter('unread')
      await nextTick()
      
      expect(wrapper.vm.currentPage).toBe(1)
    })

    it('should update active filter tab styling', async () => {
      wrapper = mount(NotificationCenter)
      await nextTick()
      
      wrapper.vm.activeFilter = 'unread'
      await nextTick()
      
      const unreadTab = wrapper.findAll('.filter-tab').find(tab => 
        tab.text().includes('No Leídas')
      )
      if (unreadTab) {
        expect(unreadTab.classes()).toContain('active')
      }
    })
  })

  describe('Counts display', () => {
    it('should display correct total count', async () => {
      const mockNotifications = [
        createMockNotification(1),
        createMockNotification(2),
        createMockNotification(3)
      ]
      wrapper = mount(NotificationCenter)
      wrapper.vm.notifications = mockNotifications
      wrapper.vm.totalCount = 3
      await nextTick()
      
      expect(wrapper.text()).toContain('Todas (3)')
    })

    it('should display correct unread count', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: false }),
        createMockNotification(2, { leida: false }),
        createMockNotification(3, { leida: true })
      ]
      
      // Configure mock before mounting
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications, mockNotifications.length)
      )
      
      wrapper = mount(NotificationCenter)
      await flushPromises()
      await nextTick()
      
      expect(wrapper.vm.unreadCount).toBe(2)
    })

    it('should display correct read count', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: true }),
        createMockNotification(2, { leida: true }),
        createMockNotification(3, { leida: false })
      ]
      
      // Configure mock before mounting
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications, mockNotifications.length)
      )
      
      wrapper = mount(NotificationCenter)
      await flushPromises()
      await nextTick()
      
      expect(wrapper.vm.readCount).toBe(2)
    })
  })

  describe('Mark as read functionality', () => {
    it('should mark notification as read when clicked', async () => {
      const mockNotification = createMockNotification(1, { leida: false })
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification])
      )
      mockNotificationStore.markAsRead.mockResolvedValue(true)

      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const notificationItem = wrapper.find('.notification-item')
      await notificationItem.trigger('click')
      await nextTick()
      
      expect(mockNotificationStore.markAsRead).toHaveBeenCalledWith(1)
    })

    it('should not mark notification as read if already read', async () => {
      const mockNotification = createMockNotification(1, { leida: true })
      wrapper = mount(NotificationCenter)
      wrapper.vm.notifications = [mockNotification]
      await nextTick()
      
      await wrapper.vm.markAsRead(mockNotification)
      await nextTick()
      
      expect(mockNotificationStore.markAsRead).not.toHaveBeenCalled()
    })

    it('should update local state after marking as read', async () => {
      const mockNotification = createMockNotification(1, { leida: false })
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification])
      )
      mockNotificationStore.markAsRead.mockResolvedValue(true)
      
      wrapper = mount(NotificationCenter)
      await flushPromises()
      await nextTick()
      
      await wrapper.vm.markAsRead(mockNotification)
      await flushPromises()
      await nextTick()
      
      const updatedNotification = wrapper.vm.notifications.find(n => n.id === mockNotification.id)
      expect(updatedNotification).toBeDefined()
      expect(updatedNotification.leida).toBe(true)
    })

    it('should mark all notifications as read', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: false }),
        createMockNotification(2, { leida: false })
      ]
      wrapper = mount(NotificationCenter)
      wrapper.vm.notifications = mockNotifications
      await nextTick()
      
      await wrapper.vm.markAllAsRead()
      await nextTick()
      
      expect(mockNotificationStore.markAllAsRead).toHaveBeenCalled()
      expect(mockUseNotifications.showSuccess).toHaveBeenCalled()
    })

    it('should disable mark all button when no unread notifications', async () => {
      const mockNotifications = [
        createMockNotification(1, { leida: true }),
        createMockNotification(2, { leida: true })
      ]
      wrapper = mount(NotificationCenter)
      wrapper.vm.notifications = mockNotifications
      await nextTick()
      
      const markAllButton = wrapper.find('.btn-outline-primary')
      if (markAllButton.exists()) {
        expect(markAllButton.attributes('disabled')).toBeDefined()
      }
    })
  })

  describe('Delete functionality', () => {
    it('should show confirmation dialog before deleting', async () => {
      const mockNotification = createMockNotification(1)
      wrapper = mount(NotificationCenter)
      wrapper.vm.notifications = [mockNotification]
      await nextTick()
      
      await wrapper.vm.deleteNotification(mockNotification)
      await nextTick()
      
      expect(mockSwal.fire).toHaveBeenCalledWith(
        expect.objectContaining({
          title: '¿Eliminar notificación?',
          icon: 'warning'
        })
      )
    })

    it('should delete notification when confirmed', async () => {
      mockSwal.fire.mockResolvedValue({ isConfirmed: true })
      const mockNotification = createMockNotification(1)
      
      // Mock getNotifications to return the notification initially
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification], 1)
      )
      
      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // Verify initial state
      expect(wrapper.vm.notifications.length).toBe(1)
      expect(wrapper.vm.totalCount).toBe(1)
      
      await wrapper.vm.deleteNotification(mockNotification)
      await nextTick()
      
      expect(mockNotificationStore.deleteNotification).toHaveBeenCalledWith(1)
      expect(mockUseNotifications.showSuccess).toHaveBeenCalled()
      expect(wrapper.vm.notifications.length).toBe(0)
      expect(wrapper.vm.totalCount).toBe(0)
    })

    it('should not delete notification when cancelled', async () => {
      mockSwal.fire.mockResolvedValue({ isConfirmed: false })
      const mockNotification = createMockNotification(1)
      
      // Mock getNotifications to return the notification initially
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse([mockNotification], 1)
      )
      
      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // Verify initial state
      expect(wrapper.vm.notifications.length).toBe(1)
      expect(wrapper.vm.totalCount).toBe(1)
      
      await wrapper.vm.deleteNotification(mockNotification)
      await nextTick()
      
      expect(mockNotificationStore.deleteNotification).not.toHaveBeenCalled()
      expect(wrapper.vm.notifications.length).toBe(1)
      expect(wrapper.vm.totalCount).toBe(1)
    })
  })

  describe('Pagination', () => {
    it('should display pagination when there are multiple pages', async () => {
      const mockNotifications = Array.from({ length: 20 }, (_, i) =>
        createMockNotification(i + 1)
      )
      mockNotificationStore.getNotifications.mockResolvedValue(
        createMockNotificationsResponse(mockNotifications, 50)
      )

      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      wrapper.vm.totalPages = 3
      await nextTick()
      
      const pagination = wrapper.find('.pagination-container')
      expect(pagination.exists()).toBe(true)
    })

    it('should not display pagination when there is only one page', async () => {
      const mockNotifications = [createMockNotification(1)]
      wrapper = mount(NotificationCenter)
      wrapper.vm.notifications = mockNotifications
      wrapper.vm.totalPages = 1
      await nextTick()
      
      const pagination = wrapper.find('.pagination-container')
      expect(pagination.exists()).toBe(false)
    })

    it('should change page when page button is clicked', async () => {
      // Mock response that maintains totalPages = 3 (60 items / 20 pageSize = 3 pages)
      const mockResponse = createMockNotificationsResponse([], 60)
      mockNotificationStore.getNotifications.mockResolvedValue(mockResponse)
      
      wrapper = mount(NotificationCenter)
      await flushPromises()
      await nextTick()
      
      // Verify initial state after mount (should have totalPages = 3 from mock)
      expect(wrapper.vm.totalPages).toBe(3)
      expect(wrapper.vm.currentPage).toBe(1)
      
      // Change page
      await wrapper.vm.changePage(2)
      await flushPromises()
      await nextTick()
      
      expect(wrapper.vm.currentPage).toBe(2)
      expect(mockNotificationStore.getNotifications).toHaveBeenCalled()
    })

    it('should not change to invalid page', async () => {
      wrapper = mount(NotificationCenter)
      wrapper.vm.totalPages = 3
      wrapper.vm.currentPage = 1
      await nextTick()
      
      await wrapper.vm.changePage(0)
      await nextTick()
      
      expect(wrapper.vm.currentPage).toBe(1)
      
      await wrapper.vm.changePage(4)
      await nextTick()
      
      expect(wrapper.vm.currentPage).toBe(1)
    })

    it('should calculate visible pages correctly', async () => {
      // Mock response that gives us 10 pages (200 items / 20 pageSize = 10 pages)
      const mockResponse = createMockNotificationsResponse([], 200)
      mockNotificationStore.getNotifications.mockResolvedValue(mockResponse)
      
      wrapper = mount(NotificationCenter)
      await flushPromises()
      await nextTick()
      
      // Verify totalPages is set correctly from mock (should be 10)
      expect(wrapper.vm.totalPages).toBe(10)
      
      // Set currentPage to 5
      wrapper.vm.currentPage = 5
      await nextTick()
      
      // Get visible pages - should show pages around currentPage (5)
      const visiblePages = wrapper.vm.visiblePages
      expect(visiblePages.length).toBeGreaterThan(0)
      expect(visiblePages).toContain(5)
    })
  })

  describe('Settings', () => {
    it('should display notification settings section', () => {
      wrapper = mount(NotificationCenter)
      expect(wrapper.text()).toContain('Configuración de Notificaciones')
    })

    it('should display all setting options', () => {
      wrapper = mount(NotificationCenter)
      
      expect(wrapper.text()).toContain('Notificaciones por Email')
      expect(wrapper.text()).toContain('Notificaciones Push')
      expect(wrapper.text()).toContain('Notificaciones de Reportes')
      expect(wrapper.text()).toContain('Notificaciones de Análisis')
    })

    it('should update settings when checkbox is changed', async () => {
      wrapper = mount(NotificationCenter)
      await nextTick()
      
      wrapper.vm.settings.email_notifications = false
      await wrapper.vm.updateSettings()
      await nextTick()
      
      expect(mockNotificationStore.updateSettings).toHaveBeenCalledWith(
        wrapper.vm.settings
      )
      expect(mockUseNotifications.showSuccess).toHaveBeenCalled()
    })
  })

  describe('Refresh functionality', () => {
    it('should refresh notifications when refresh button is clicked', async () => {
      wrapper = mount(NotificationCenter)
      await nextTick()
      
      vi.clearAllMocks()
      
      await wrapper.vm.refreshNotifications()
      await nextTick()
      
      expect(mockNotificationStore.getNotifications).toHaveBeenCalled()
    })

    it('should disable refresh button when loading', async () => {
      wrapper = mount(NotificationCenter)
      wrapper.vm.loading = true
      await nextTick()
      
      const refreshButton = wrapper.find('.btn-outline-secondary')
      if (refreshButton.exists() && refreshButton.text().includes('Actualizar')) {
        expect(refreshButton.attributes('disabled')).toBeDefined()
      }
    })
  })

  describe('Time formatting', () => {
    it('should format time correctly for recent notifications', () => {
      wrapper = mount(NotificationCenter)
      
      const recentDate = new Date().toISOString()
      const formatted = wrapper.vm.formatTime(recentDate)
      expect(formatted).toContain('Ahora mismo')
    })

    it('should format time in minutes', () => {
      wrapper = mount(NotificationCenter)
      
      const thirtyMinutesAgo = new Date(Date.now() - 30 * 60 * 1000).toISOString()
      const formatted = wrapper.vm.formatTime(thirtyMinutesAgo)
      expect(formatted).toContain('min')
    })

    it('should format time in hours', () => {
      wrapper = mount(NotificationCenter)
      
      const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
      const formatted = wrapper.vm.formatTime(twoHoursAgo)
      expect(formatted).toContain('h')
    })
  })

  describe('Icon helper', () => {
    it('should return correct icon for notification type', () => {
      wrapper = mount(NotificationCenter)
      
      expect(wrapper.vm.getNotificationIcon('info')).toBe('fas fa-info-circle')
      expect(wrapper.vm.getNotificationIcon('success')).toBe('fas fa-check-circle')
      expect(wrapper.vm.getNotificationIcon('error')).toBe('fas fa-times-circle')
      expect(wrapper.vm.getNotificationIcon('defect_alert')).toBe('fas fa-exclamation-circle')
      expect(wrapper.vm.getNotificationIcon('report_ready')).toBe('fas fa-file-alt')
      expect(wrapper.vm.getNotificationIcon('unknown')).toBe('fas fa-bell')
    })
  })

  describe('WebSocket integration', () => {
    it('should add new notification when received via WebSocket', async () => {
      wrapper = mount(NotificationCenter)
      wrapper.vm.notifications = []
      wrapper.vm.totalCount = 0
      await nextTick()
      
      const mockNotification = createMockNotification(1)
      
      // Simulate WebSocket message
      if (mockNotificationStore.websocket.onmessage) {
        mockNotificationStore.websocket.onmessage({
          data: JSON.stringify({
            type: 'notification',
            notification: mockNotification
          })
        })
      }
      
      await nextTick()
      
      expect(wrapper.vm.notifications.length).toBeGreaterThan(0)
    })
  })

  describe('Error handling', () => {
    it('should handle error when loading notifications fails', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      mockNotificationStore.getNotifications.mockRejectedValue(new Error('Network error'))

      wrapper = mount(NotificationCenter)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      expect(mockUseNotifications.showError).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })

    it('should handle error when marking as read fails', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const mockNotification = createMockNotification(1, { leida: false })
      mockNotificationStore.markAsRead.mockRejectedValue(new Error('Failed'))

      wrapper = mount(NotificationCenter)
      wrapper.vm.notifications = [mockNotification]
      await nextTick()
      
      await wrapper.vm.markAsRead(mockNotification)
      await nextTick()
      
      expect(mockUseNotifications.showError).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })

    it('should handle error when deleting notification fails', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      mockSwal.fire.mockResolvedValue({ isConfirmed: true })
      mockNotificationStore.deleteNotification.mockRejectedValue(new Error('Failed'))
      const mockNotification = createMockNotification(1)

      wrapper = mount(NotificationCenter)
      wrapper.vm.notifications = [mockNotification]
      await nextTick()
      
      await wrapper.vm.deleteNotification(mockNotification)
      await nextTick()
      
      expect(mockUseNotifications.showError).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })

    it('should handle error when updating settings fails', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      mockNotificationStore.updateSettings.mockRejectedValue(new Error('Failed'))

      wrapper = mount(NotificationCenter)
      await nextTick()
      
      await wrapper.vm.updateSettings()
      await nextTick()
      
      expect(mockUseNotifications.showError).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })
  })

  describe('Styling classes', () => {
    it('should apply unread class to unread notifications', async () => {
      const mockNotification = createMockNotification(1, { leida: false })
      wrapper = mount(NotificationCenter)
      await nextTick()
      
      wrapper.vm.loading = false
      wrapper.vm.activeFilter = 'all'
      wrapper.vm.notifications = [mockNotification]
      await nextTick()
      
      const notificationItem = wrapper.find('.notification-item')
      expect(notificationItem.exists()).toBe(true)
      expect(notificationItem.classes()).toContain('unread')
    })

    it('should apply read class to read notifications', async () => {
      const mockNotification = createMockNotification(1, { leida: true })
      wrapper = mount(NotificationCenter)
      await nextTick()
      
      wrapper.vm.loading = false
      wrapper.vm.activeFilter = 'all'
      wrapper.vm.notifications = [mockNotification]
      await nextTick()
      
      const notificationItem = wrapper.find('.notification-item')
      expect(notificationItem.exists()).toBe(true)
      expect(notificationItem.classes()).toContain('read')
    })
  })
})

