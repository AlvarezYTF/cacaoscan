import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useNotificationsStore } from '../notifications'
import api from '@/services/api'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/utils/fileExportUtils', () => ({
  downloadFileFromResponse: vi.fn()
}))

describe('Notifications Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useNotificationsStore()
    vi.clearAllMocks()
  })

  describe('State and Getters', () => {
    it('should have initial state', () => {
      expect(store.notifications).toEqual([])
      expect(store.unreadCount).toBe(0)
      expect(store.stats.total_notifications).toBe(0)
      expect(store.pagination.currentPage).toBe(1)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('should get notification by id', () => {
      store.notifications = [
        { id: 1, titulo: 'Test 1' },
        { id: 2, titulo: 'Test 2' }
      ]

      const notification = store.getNotificationById(1)
      expect(notification).toEqual({ id: 1, titulo: 'Test 1' })
    })

    it('should get unread notifications', () => {
      store.notifications = [
        { id: 1, leida: false },
        { id: 2, leida: true },
        { id: 3, leida: false }
      ]

      const unread = store.getUnreadNotifications
      expect(unread).toHaveLength(2)
      expect(unread.every(n => !n.leida)).toBe(true)
    })

    it('should get notifications by type', () => {
      store.notifications = [
        { id: 1, tipo: 'info' },
        { id: 2, tipo: 'error' },
        { id: 3, tipo: 'info' }
      ]

      const infoNotifications = store.getNotificationsByType('info')
      expect(infoNotifications).toHaveLength(2)
    })

    it('should get recent notifications', () => {
      const now = new Date()
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)

      store.notifications = [
        { id: 1, fecha_creacion: now.toISOString() },
        { id: 2, fecha_creacion: yesterday.toISOString() },
        { id: 3, fecha_creacion: now.toISOString() },
        { id: 4, fecha_creacion: now.toISOString() },
        { id: 5, fecha_creacion: now.toISOString() },
        { id: 6, fecha_creacion: now.toISOString() }
      ]

      const recent = store.getRecentNotifications(5)
      expect(recent).toHaveLength(5)
    })

    it('should get notifications by date', () => {
      // Use a date string that will match when converted to DateString
      // The getter uses toDateString() which compares dates in local timezone
      // We need to ensure all dates are in the same timezone for comparison
      const targetDate = new Date('2024-01-15T00:00:00')
      store.notifications = [
        { id: 1, fecha_creacion: '2024-01-15T00:00:00' },
        { id: 2, fecha_creacion: '2024-01-16T00:00:00' },
        { id: 3, fecha_creacion: '2024-01-15T12:00:00' }
      ]

      const byDate = store.getNotificationsByDate(targetDate)
      // The getter compares dates using toDateString(), so all notifications from 2024-01-15 should match
      expect(byDate.length).toBe(2)
      // Verify that the returned notifications are from the correct date
      for (const notification of byDate) {
        const notificationDate = new Date(notification.fecha_creacion).toDateString()
        expect(notificationDate).toBe(targetDate.toDateString())
      }
    })
  })

  describe('Actions', () => {
    it('should fetch notifications successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, titulo: 'Test', leida: false },
            { id: 2, titulo: 'Test 2', leida: true }
          ],
          page: 1,
          total_pages: 1,
          count: 2,
          page_size: 20
        }
      }

      api.get.mockResolvedValue(mockResponse)

      await store.fetchNotifications()

      expect(store.notifications).toHaveLength(2)
      expect(store.unreadCount).toBe(1)
      expect(store.pagination.currentPage).toBe(1)
      expect(store.loading).toBe(false)
    })

    it('should handle fetch notifications error', async () => {
      const error = {
        response: {
          data: {
            detail: 'Error message'
          }
        }
      }

      api.get.mockRejectedValue(error)

      await expect(store.fetchNotifications()).rejects.toEqual(error)
      expect(store.error).toBe('Error message')
      expect(store.loading).toBe(false)
    })

    it('should mark notification as read', async () => {
      store.notifications = [
        { id: 1, leida: false }
      ]
      store.unreadCount = 1

      api.post.mockResolvedValue({})

      const result = await store.markAsRead(1)

      expect(result).toBe(true)
      expect(store.notifications[0].leida).toBe(true)
      expect(store.unreadCount).toBe(0)
    })

    it('should mark all notifications as read', async () => {
      store.notifications = [
        { id: 1, leida: false },
        { id: 2, leida: false }
      ]
      store.unreadCount = 2

      api.post.mockResolvedValue({})

      const result = await store.markAllAsRead()

      expect(result).toBe(true)
      expect(store.notifications.every(n => n.leida)).toBe(true)
      expect(store.unreadCount).toBe(0)
    })

    it('should get unread count', async () => {
      const mockResponse = {
        data: {
          unread_count: 5
        }
      }

      api.get.mockResolvedValue(mockResponse)

      const count = await store.getUnreadCount()

      expect(count).toBe(5)
      expect(store.unreadCount).toBe(5)
    })

    it('should get notification stats', async () => {
      const mockStats = {
        total_notifications: 10,
        unread_count: 3,
        notifications_by_type: { info: 5, error: 2 },
        recent_notifications: []
      }

      const mockResponse = {
        data: mockStats
      }

      api.get.mockResolvedValue(mockResponse)

      const stats = await store.getNotificationStats()

      expect(stats).toEqual(mockStats)
      expect(store.stats).toEqual(mockStats)
    })

    it('should create notification', async () => {
      const newNotification = {
        id: 1,
        titulo: 'New',
        leida: false
      }

      const mockResponse = {
        data: newNotification
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await store.createNotification({ titulo: 'New' })

      expect(result).toEqual(newNotification)
      expect(store.notifications[0]).toEqual(newNotification)
      expect(store.unreadCount).toBe(1)
    })

    it('should add realtime notification', () => {
      const notification = {
        id: 1,
        titulo: 'Realtime',
        leida: false
      }

      store.addRealtimeNotification(notification)

      expect(store.notifications).toContainEqual(notification)
      expect(store.unreadCount).toBe(1)
    })

    it('should update existing realtime notification', () => {
      store.notifications = [
        { id: 1, titulo: 'Old', leida: false }
      ]
      store.unreadCount = 1

      const updated = {
        id: 1,
        titulo: 'Updated',
        leida: false
      }

      store.addRealtimeNotification(updated)

      expect(store.notifications[0].titulo).toBe('Updated')
      expect(store.notifications).toHaveLength(1)
    })

    it('should limit notifications to 100', () => {
      const notifications = Array.from({ length: 101 }, (_, i) => ({
        id: i + 1,
        leida: false
      }))

      for (const n of notifications) {
        store.addRealtimeNotification(n)
      }

      expect(store.notifications).toHaveLength(100)
    })

    it('should update realtime notification', () => {
      store.notifications = [
        { id: 1, leida: false }
      ]
      store.unreadCount = 1

      const updated = {
        id: 1,
        leida: true
      }

      store.updateRealtimeNotification(updated)

      expect(store.notifications[0].leida).toBe(true)
      expect(store.unreadCount).toBe(0)
    })

    it('should update realtime stats', () => {
      const stats = {
        total_notifications: 10,
        unread_count: 3,
        notifications_by_type: {},
        recent_notifications: []
      }

      store.updateRealtimeStats(stats)

      expect(store.stats).toEqual(stats)
      expect(store.unreadCount).toBe(3)
    })

    it('should search notifications', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, titulo: 'Search result' }
          ]
        }
      }

      api.get.mockResolvedValue(mockResponse)

      await store.searchNotifications('test')

      expect(api.get).toHaveBeenCalledWith('/notifications/', {
        params: { search: 'test' }
      })
      expect(store.notifications).toHaveLength(1)
    })

    it('should filter by type', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, tipo: 'info' }
          ]
        }
      }

      api.get.mockResolvedValue(mockResponse)

      await store.filterByType('info')

      expect(api.get).toHaveBeenCalledWith('/notifications/', {
        params: { tipo: 'info' }
      })
    })

    it('should filter by read status', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, leida: false }
          ]
        }
      }

      api.get.mockResolvedValue(mockResponse)

      await store.filterByReadStatus(false)

      expect(api.get).toHaveBeenCalledWith('/notifications/', {
        params: { leida: false }
      })
    })

    it('should go to page', async () => {
      const mockResponse = {
        data: {
          results: [],
          page: 2,
          total_pages: 2,
          count: 20,
          page_size: 20
        }
      }

      api.get.mockResolvedValue(mockResponse)

      await store.goToPage(2)

      expect(store.pagination.currentPage).toBe(2)
    })

    it('should change page size', async () => {
      const mockResponse = {
        data: {
          results: [],
          page: 1,
          total_pages: 1,
          count: 10,
          page_size: 50
        }
      }

      api.get.mockResolvedValue(mockResponse)

      await store.changePageSize(50)

      expect(store.pagination.itemsPerPage).toBe(50)
    })

    it('should export notifications', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/json' })
      const mockResponse = {
        data: mockBlob
      }

      api.get.mockResolvedValue(mockResponse)

      const result = await store.exportNotifications('json')

      expect(result).toBe(true)
      expect(api.get).toHaveBeenCalledWith('/notifications/export/', {
        params: { format: 'json' },
        responseType: 'blob'
      })
    })

    it('should clear error', () => {
      store.error = 'Some error'
      store.clearError()
      expect(store.error).toBe(null)
    })

    it('should reset store', () => {
      store.notifications = [{ id: 1 }]
      store.unreadCount = 5
      store.loading = true
      store.error = 'Error'

      store.reset()

      expect(store.notifications).toEqual([])
      expect(store.unreadCount).toBe(0)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('should handle fetchNotificationDetails', async () => {
      const mockResponse = {
        data: { id: 1, titulo: 'Details' }
      }

      api.get.mockResolvedValue(mockResponse)

      const result = await store.fetchNotificationDetails(1)

      expect(api.get).toHaveBeenCalledWith('/notifications/1/')
      expect(result).toEqual(mockResponse)
    })

    it('should handle fetchNotificationDetails error', async () => {
      const error = new Error('Not found')
      api.get.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.fetchNotificationDetails(1)).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should not update unreadCount if notification already read', async () => {
      store.notifications = [
        { id: 1, leida: true }
      ]
      store.unreadCount = 0

      api.post.mockResolvedValue({})

      await store.markAsRead(1)

      expect(store.unreadCount).toBe(0)
    })

    it('should handle markAsRead when notification not found', async () => {
      store.notifications = []
      store.unreadCount = 0

      api.post.mockResolvedValue({})

      await store.markAsRead(999)

      expect(store.unreadCount).toBe(0)
    })

    it('should handle markAsRead error', async () => {
      const error = new Error('Mark read failed')
      api.post.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.markAsRead(1)).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle markAllAsRead error', async () => {
      const error = new Error('Mark all read failed')
      api.post.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.markAllAsRead()).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle getUnreadCount error', async () => {
      const error = new Error('Get count failed')
      api.get.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.getUnreadCount()).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle getNotificationStats error', async () => {
      const error = new Error('Get stats failed')
      api.get.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.getNotificationStats()).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle createNotification error', async () => {
      const error = new Error('Create failed')
      api.post.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.createNotification({})).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle updateRealtimeNotification when notification not found', () => {
      store.notifications = []
      store.unreadCount = 0

      const notification = {
        id: 999,
        leida: true
      }

      store.updateRealtimeNotification(notification)

      expect(store.notifications).toHaveLength(0)
      expect(store.unreadCount).toBe(0)
    })

    it('should handle updateRealtimeNotification when unread becomes read', () => {
      store.notifications = [
        { id: 1, leida: false }
      ]
      store.unreadCount = 1

      const updated = {
        id: 1,
        leida: true
      }

      store.updateRealtimeNotification(updated)

      expect(store.notifications[0].leida).toBe(true)
      expect(store.unreadCount).toBe(0)
    })

    it('should handle updateRealtimeNotification when read becomes unread', () => {
      store.notifications = [
        { id: 1, leida: true }
      ]
      store.unreadCount = 0

      const updated = {
        id: 1,
        leida: false
      }

      store.updateRealtimeNotification(updated)

      expect(store.notifications[0].leida).toBe(false)
      expect(store.unreadCount).toBe(1)
    })

    it('should handle searchNotifications error', async () => {
      const error = new Error('Search failed')
      api.get.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.searchNotifications('test')).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle filterByType error', async () => {
      const error = new Error('Filter failed')
      api.get.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.filterByType('info')).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle filterByReadStatus error', async () => {
      const error = new Error('Filter failed')
      api.get.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.filterByReadStatus(false)).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle goToPage error', async () => {
      const error = new Error('Page failed')
      api.get.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.goToPage(2)).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle changePageSize error', async () => {
      const error = new Error('Change size failed')
      api.get.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.changePageSize(50)).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle exportNotifications error', async () => {
      const error = new Error('Export failed')
      api.get.mockRejectedValue(error)
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(store.exportNotifications('json')).rejects.toThrow()

      expect(consoleError).toHaveBeenCalled()
      consoleError.mockRestore()
    })

    it('should handle fetchNotifications with array response', async () => {
      const mockResponse = {
        data: [
          { id: 1, titulo: 'Test', leida: false }
        ]
      }

      api.get.mockResolvedValue(mockResponse)

      await store.fetchNotifications()

      expect(store.notifications).toHaveLength(1)
    })

    it('should handle fetchNotifications without pagination data', async () => {
      const mockResponse = {
        data: {
          results: [{ id: 1, titulo: 'Test', leida: false }]
        }
      }

      api.get.mockResolvedValue(mockResponse)

      await store.fetchNotifications()

      expect(store.pagination.currentPage).toBe(1)
      expect(store.pagination.totalPages).toBe(1)
    })
  })
})

