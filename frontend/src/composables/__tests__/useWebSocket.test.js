/**
 * Unit tests for useWebSocket composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useWebSocket } from '../useWebSocket.js'
import { useWebSocketBase } from '../useWebSocketBase'

// Mock dependencies
const mockAuthStore = {
  user: {
    id: 1,
    is_superuser: false,
    is_staff: false
  }
}

const mockWebSocketBase = {
  isConnected: { value: false },
  isConnecting: { value: false },
  connectionError: { value: null },
  reconnectAttempts: { value: 0 },
  connect: vi.fn(),
  disconnect: vi.fn(),
  send: vi.fn()
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('../useWebSocketBase', () => ({
  useWebSocketBase: vi.fn(() => mockWebSocketBase)
}))

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock import.meta.env
    vi.stubGlobal('import', {
      meta: {
        env: {
          MODE: 'production',
          VITE_WS_ENABLED: 'true',
          VITE_WS_URL: undefined,
          VITE_API_BASE_URL: undefined
        }
      }
    })
  })

  describe('development mode', () => {
    it('should return mock interface in development mode', () => {
      // Override import.meta.env.MODE for this test
      const env = import.meta.env
      const originalMode = env.MODE
      env.MODE = 'development'
      
      const socket = useWebSocket()
      
      // Verify the mock interface structure
      expect(socket.isConnected).toBeDefined()
      expect(socket.isConnected.value).toBe(false)
      expect(socket.connectionStatus).toBeDefined()
      expect(socket.connectionStatus.value).toBe('disabled')
      
      // Restore original MODE
      env.MODE = originalMode
    })
  })

  describe('connect', () => {
    it('should connect when user is authenticated', () => {
      mockAuthStore.user = { id: 1 }
      
      const socket = useWebSocket()
      socket.connect()
      
      expect(useWebSocketBase).toHaveBeenCalled()
    })

    it('should not connect when user is not authenticated', () => {
      mockAuthStore.user = null
      
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      const socket = useWebSocket()
      socket.connect()
      
      expect(useWebSocketBase).not.toHaveBeenCalled()
      
      consoleSpy.mockRestore()
    })

    it('should create audit socket for admin users', () => {
      mockAuthStore.user = {
        id: 1,
        is_superuser: true,
        is_staff: false
      }
      
      const socket = useWebSocket()
      socket.connect()
      
      // Should create multiple sockets including audit
      expect(useWebSocketBase).toHaveBeenCalled()
    })
  })

  describe('disconnect', () => {
    it('should disconnect all sockets', () => {
      mockAuthStore.user = { id: 1 }
      
      const socket = useWebSocket()
      socket.connect()
      socket.disconnect()
      
      expect(mockWebSocketBase.disconnect).toHaveBeenCalled()
    })
  })

  describe('ping', () => {
    it('should send ping to all sockets', () => {
      const socket = useWebSocket()
      
      // Mock socket instances
      socket.notificationSocket = mockWebSocketBase
      socket.systemStatusSocket = mockWebSocketBase
      
      socket.ping()
      
      expect(mockWebSocketBase.send).toHaveBeenCalled()
    })
  })

  describe('notification methods', () => {
    it('should mark notification as read', () => {
      const socket = useWebSocket()
      socket.notificationSocket = mockWebSocketBase
      
      socket.markNotificationRead(123)
      
      expect(mockWebSocketBase.send).toHaveBeenCalledWith({
        type: 'mark_read',
        notification_id: 123
      })
    })

    it('should mark all notifications as read', () => {
      const socket = useWebSocket()
      socket.notificationSocket = mockWebSocketBase
      
      socket.markAllNotificationsRead()
      
      expect(mockWebSocketBase.send).toHaveBeenCalledWith({
        type: 'mark_all_read'
      })
    })
  })

  describe('event emitter', () => {
    it('should register event listener', () => {
      const socket = useWebSocket()
      const callback = vi.fn()
      
      socket.on('test-event', callback)
      socket.emit('test-event', { data: 'test' })
      
      expect(callback).toHaveBeenCalledWith({ data: 'test' })
    })

    it('should remove event listener', () => {
      const socket = useWebSocket()
      const callback = vi.fn()
      
      socket.on('test-event', callback)
      socket.off('test-event', callback)
      socket.emit('test-event', { data: 'test' })
      
      expect(callback).not.toHaveBeenCalled()
    })

    it('should handle multiple listeners for same event', () => {
      const socket = useWebSocket()
      const callback1 = vi.fn()
      const callback2 = vi.fn()
      
      socket.on('test-event', callback1)
      socket.on('test-event', callback2)
      socket.emit('test-event', { data: 'test' })
      
      expect(callback1).toHaveBeenCalledWith({ data: 'test' })
      expect(callback2).toHaveBeenCalledWith({ data: 'test' })
    })

    it('should handle listener errors gracefully', () => {
      const socket = useWebSocket()
      const errorCallback = vi.fn(() => {
        throw new Error('Listener error')
      })
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      socket.on('test-event', errorCallback)
      socket.emit('test-event', { data: 'test' })
      
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })

    it('should not emit when no listeners', () => {
      const socket = useWebSocket()
      socket.emit('test-event', { data: 'test' })
      // Should not throw
      expect(true).toBe(true)
    })
  })

  describe('connect', () => {
    it('should create all socket connections', () => {
      mockAuthStore.user = { id: 1, is_superuser: false, is_staff: false }
      
      const socket = useWebSocket()
      socket.connect()
      
      // Should create notification, system status, and user stats sockets
      expect(useWebSocketBase).toHaveBeenCalledTimes(3)
    })

    it('should create audit socket for staff users', () => {
      mockAuthStore.user = {
        id: 1,
        is_superuser: false,
        is_staff: true
      }
      
      const socket = useWebSocket()
      socket.connect()
      
      // Should create audit socket for staff
      expect(useWebSocketBase).toHaveBeenCalled()
    })

    it('should handle connection error', () => {
      mockAuthStore.user = { id: 1 }
      const error = new Error('Connection failed')
      useWebSocketBase.mockImplementationOnce(() => {
        throw error
      })
      
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const socket = useWebSocket()
      socket.connect()
      
      expect(consoleErrorSpy).toHaveBeenCalled()
      expect(socket.connectionError.value).toBe('Connection failed')
      consoleErrorSpy.mockRestore()
    })

    it('should disconnect existing connections before connecting', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      
      // Set up existing sockets with separate mock instances
      const mockNotificationSocket = { ...mockWebSocketBase, disconnect: vi.fn() }
      const mockSystemStatusSocket = { ...mockWebSocketBase, disconnect: vi.fn() }
      
      socket.notificationSocket = mockNotificationSocket
      socket.systemStatusSocket = mockSystemStatusSocket
      
      socket.connect()
      
      expect(mockNotificationSocket.disconnect).toHaveBeenCalled()
      expect(mockSystemStatusSocket.disconnect).toHaveBeenCalled()
    })
  })

  describe('disconnect', () => {
    it('should disconnect all socket types', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      
      socket.notificationSocket = mockWebSocketBase
      socket.systemStatusSocket = mockWebSocketBase
      socket.auditSocket = mockWebSocketBase
      socket.userStatsSocket = mockWebSocketBase
      
      socket.disconnect()
      
      expect(mockWebSocketBase.disconnect).toHaveBeenCalled()
      expect(socket.connectionError.value).toBe(null)
    })
  })

  describe('reconnect', () => {
    it('should disconnect and reconnect', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      
      vi.useFakeTimers()
      socket.disconnect = vi.fn()
      socket.connect = vi.fn()
      
      socket.reconnect()
      
      expect(socket.disconnect).toHaveBeenCalled()
      
      vi.advanceTimersByTime(5000)
      
      expect(socket.connect).toHaveBeenCalled()
      vi.useRealTimers()
    })
  })

  describe('ping', () => {
    it('should send ping to all available sockets', () => {
      const socket = useWebSocket()
      
      socket.notificationSocket = mockWebSocketBase
      socket.systemStatusSocket = mockWebSocketBase
      socket.auditSocket = mockWebSocketBase
      socket.userStatsSocket = mockWebSocketBase
      
      socket.ping()
      
      expect(mockWebSocketBase.send).toHaveBeenCalledTimes(4)
      expect(mockWebSocketBase.send).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'ping'
        })
      )
    })

    it('should not send ping when sockets are null', () => {
      const socket = useWebSocket()
      
      socket.notificationSocket = null
      socket.systemStatusSocket = null
      
      socket.ping()
      
      // Should not throw
      expect(true).toBe(true)
    })
  })

  describe('notification methods', () => {
    it('should not mark notification read when socket is null', () => {
      const socket = useWebSocket()
      socket.notificationSocket = null
      
      socket.markNotificationRead(123)
      
      expect(mockWebSocketBase.send).not.toHaveBeenCalled()
    })

    it('should get notification stats', () => {
      const socket = useWebSocket()
      socket.notificationSocket = mockWebSocketBase
      
      socket.getNotificationStats()
      
      expect(mockWebSocketBase.send).toHaveBeenCalledWith({
        type: 'get_stats'
      })
    })

    it('should not get notification stats when socket is null', () => {
      const socket = useWebSocket()
      socket.notificationSocket = null
      
      socket.getNotificationStats()
      
      expect(mockWebSocketBase.send).not.toHaveBeenCalled()
    })
  })

  describe('audit methods', () => {
    it('should get audit stats', () => {
      const socket = useWebSocket()
      socket.auditSocket = mockWebSocketBase
      
      socket.getAuditStats()
      
      expect(mockWebSocketBase.send).toHaveBeenCalledWith({
        type: 'get_audit_stats'
      })
    })

    it('should not get audit stats when socket is null', () => {
      const socket = useWebSocket()
      socket.auditSocket = null
      
      socket.getAuditStats()
      
      expect(mockWebSocketBase.send).not.toHaveBeenCalled()
    })

    it('should get recent activity', () => {
      const socket = useWebSocket()
      socket.auditSocket = mockWebSocketBase
      
      socket.getRecentActivity()
      
      expect(mockWebSocketBase.send).toHaveBeenCalledWith({
        type: 'get_recent_activity'
      })
    })

    it('should not get recent activity when socket is null', () => {
      const socket = useWebSocket()
      socket.auditSocket = null
      
      socket.getRecentActivity()
      
      expect(mockWebSocketBase.send).not.toHaveBeenCalled()
    })
  })

  describe('system methods', () => {
    it('should get system status', () => {
      const socket = useWebSocket()
      socket.systemStatusSocket = mockWebSocketBase
      
      socket.getSystemStatus()
      
      expect(mockWebSocketBase.send).toHaveBeenCalledWith({
        type: 'get_status'
      })
    })

    it('should not get system status when socket is null', () => {
      const socket = useWebSocket()
      socket.systemStatusSocket = null
      
      socket.getSystemStatus()
      
      expect(mockWebSocketBase.send).not.toHaveBeenCalled()
    })
  })

  describe('user stats methods', () => {
    it('should get user stats', () => {
      const socket = useWebSocket()
      socket.userStatsSocket = mockWebSocketBase
      
      socket.getUserStats()
      
      expect(mockWebSocketBase.send).toHaveBeenCalledWith({
        type: 'get_stats'
      })
    })

    it('should not get user stats when socket is null', () => {
      const socket = useWebSocket()
      socket.userStatsSocket = null
      
      socket.getUserStats()
      
      expect(mockWebSocketBase.send).not.toHaveBeenCalled()
    })
  })

  describe('computed properties', () => {
    it('should compute hasAnyConnection correctly', () => {
      const socket = useWebSocket()
      
      socket.notificationSocket = { isConnected: { value: false } }
      socket.systemStatusSocket = { isConnected: { value: false } }
      socket.auditSocket = { isConnected: { value: false } }
      socket.userStatsSocket = { isConnected: { value: false } }
      
      expect(socket.hasAnyConnection.value).toBe(false)
      
      socket.notificationSocket = { isConnected: { value: true } }
      expect(socket.hasAnyConnection.value).toBe(true)
    })

    it('should compute connectionStatus correctly', () => {
      const socket = useWebSocket()
      
      // Initialize all sockets before testing
      socket.notificationSocket = { isConnecting: { value: true }, isConnected: { value: false } }
      socket.systemStatusSocket = { isConnecting: { value: false }, isConnected: { value: false } }
      socket.auditSocket = { isConnecting: { value: false }, isConnected: { value: false } }
      socket.userStatsSocket = { isConnecting: { value: false }, isConnected: { value: false } }
      expect(socket.connectionStatus.value).toBe('connecting')
      
      socket.notificationSocket = { isConnecting: { value: false }, isConnected: { value: true } }
      socket.systemStatusSocket = { isConnecting: { value: false }, isConnected: { value: false } }
      socket.auditSocket = { isConnecting: { value: false }, isConnected: { value: false } }
      socket.userStatsSocket = { isConnecting: { value: false }, isConnected: { value: false } }
      expect(socket.connectionStatus.value).toBe('connected')
      
      socket.connectionError.value = 'Error'
      socket.notificationSocket = { isConnecting: { value: false }, isConnected: { value: false } }
      socket.systemStatusSocket = { isConnecting: { value: false }, isConnected: { value: false } }
      socket.auditSocket = { isConnecting: { value: false }, isConnected: { value: false } }
      socket.userStatsSocket = { isConnecting: { value: false }, isConnected: { value: false } }
      expect(socket.connectionStatus.value).toBe('error')
      
      socket.connectionError.value = null
      expect(socket.connectionStatus.value).toBe('disconnected')
    })

    it('should compute reconnectAttempts correctly', () => {
      const socket = useWebSocket()
      
      socket.notificationSocket = { reconnectAttempts: { value: 2 } }
      socket.systemStatusSocket = { reconnectAttempts: { value: 3 } }
      socket.auditSocket = { reconnectAttempts: { value: 1 } }
      socket.userStatsSocket = { reconnectAttempts: { value: 4 } }
      
      expect(socket.reconnectAttempts.value).toBe(4)
    })

    it('should compute reconnectAttempts as 0 when no sockets', () => {
      const socket = useWebSocket()
      
      socket.notificationSocket = null
      socket.systemStatusSocket = null
      socket.auditSocket = null
      socket.userStatsSocket = null
      
      expect(socket.reconnectAttempts.value).toBe(0)
    })

    it('should compute isConnecting correctly', () => {
      const socket = useWebSocket()
      
      socket.notificationSocket = { isConnecting: { value: true } }
      expect(socket.isConnecting.value).toBe(true)
      
      socket.notificationSocket = { isConnecting: { value: false } }
      socket.systemStatusSocket = { isConnecting: { value: false } }
      socket.auditSocket = { isConnecting: { value: false } }
      socket.userStatsSocket = { isConnecting: { value: false } }
      expect(socket.isConnecting.value).toBe(false)
    })
  })

  describe('message handlers', () => {
    it('should handle notification messages', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      const callback = vi.fn()
      
      socket.on('notification-received', callback)
      socket.connect() // Connect to create the socket and handler
      
      // Verify that useWebSocketBase was called
      expect(useWebSocketBase).toHaveBeenCalled()
      
      // Get handler from the notification socket call
      const notificationCallIndex = useWebSocketBase.mock.calls.findIndex(call => {
        return call[0]?.url?.includes('/notifications/')
      })
      expect(notificationCallIndex).toBeGreaterThanOrEqual(0)
      expect(useWebSocketBase.mock.calls[notificationCallIndex]).toBeDefined()
      expect(useWebSocketBase.mock.calls[notificationCallIndex][0]).toBeDefined()
      expect(useWebSocketBase.mock.calls[notificationCallIndex][0].onMessage).toBeDefined()
      
      const handler = useWebSocketBase.mock.calls[notificationCallIndex][0].onMessage
      handler({ type: 'notification', data: { id: 1 } })
      
      expect(callback).toHaveBeenCalledWith({ id: 1 })
    })

    it('should handle system status messages', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      const callback = vi.fn()
      
      socket.on('system-status-updated', callback)
      socket.connect() // Connect to create the socket and handler
      
      // Verify that useWebSocketBase was called
      expect(useWebSocketBase).toHaveBeenCalled()
      
      // Get handler from system status socket call
      const systemStatusCallIndex = useWebSocketBase.mock.calls.findIndex(call => {
        return call[0]?.url?.includes('/system-status/')
      })
      expect(systemStatusCallIndex).toBeGreaterThanOrEqual(0)
      expect(useWebSocketBase.mock.calls[systemStatusCallIndex]).toBeDefined()
      expect(useWebSocketBase.mock.calls[systemStatusCallIndex][0]).toBeDefined()
      expect(useWebSocketBase.mock.calls[systemStatusCallIndex][0].onMessage).toBeDefined()
      
      const handler = useWebSocketBase.mock.calls[systemStatusCallIndex][0].onMessage
      handler({ type: 'system_status', data: { status: 'ok' } })
      
      expect(callback).toHaveBeenCalledWith({ status: 'ok' })
    })

    it('should handle audit messages', () => {
      mockAuthStore.user = { id: 1, is_superuser: true }
      const socket = useWebSocket()
      socket.connect()
      const callback = vi.fn()
      
      socket.on('audit-activity', callback)
      
      // Get handler from audit socket call
      const auditCallIndex = useWebSocketBase.mock.calls.findIndex(call => {
        return call[0]?.url?.includes('/audit/')
      })
      expect(auditCallIndex).toBeGreaterThanOrEqual(0)
      const handler = useWebSocketBase.mock.calls[auditCallIndex][0].onMessage
      handler({ type: 'audit_activity', data: { action: 'create' } })
      
      expect(callback).toHaveBeenCalledWith({ action: 'create' })
    })

    it('should handle user stats messages', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      socket.connect()
      const callback = vi.fn()
      
      socket.on('user-stats-updated', callback)
      
      // Get handler from user stats socket call
      const userStatsCallIndex = useWebSocketBase.mock.calls.findIndex(call => {
        return call[0]?.url?.includes('/user-stats/')
      })
      expect(userStatsCallIndex).toBeGreaterThanOrEqual(0)
      const handler = useWebSocketBase.mock.calls[userStatsCallIndex][0].onMessage
      handler({ type: 'user_stats', data: { count: 10 } })
      
      expect(callback).toHaveBeenCalledWith({ count: 10 })
    })

    it('should handle pong messages', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      const callback = vi.fn()
      
      socket.on('test-event', callback)
      socket.connect()
      
      // Get handler from the first call (notification socket)
      const notificationCallIndex = useWebSocketBase.mock.calls.findIndex(call => {
        return call[0]?.url?.includes('/notifications/')
      })
      expect(notificationCallIndex).toBeGreaterThanOrEqual(0)
      const handler = useWebSocketBase.mock.calls[notificationCallIndex][0].onMessage
      handler({ type: 'pong' })
      
      expect(callback).not.toHaveBeenCalled()
    })

    it('should handle unhandled message types', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      
      socket.connect() // Connect to create the socket and handler
      const notificationCallIndex = useWebSocketBase.mock.calls.findIndex(call => {
        return call[0]?.url?.includes('/notifications/')
      })
      expect(notificationCallIndex).toBeGreaterThanOrEqual(0)
      const handler = useWebSocketBase.mock.calls[notificationCallIndex][0].onMessage
      handler({ type: 'unknown_type', data: {} })
      
      expect(consoleLogSpy).toHaveBeenCalled()
      consoleLogSpy.mockRestore()
    })

    it('should add messages to history', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      socket.connect()
      
      // Get handler from notification socket
      const notificationCallIndex = useWebSocketBase.mock.calls.findIndex(call => {
        return call[0]?.url?.includes('/notifications/')
      })
      expect(notificationCallIndex).toBeGreaterThanOrEqual(0)
      const handler = useWebSocketBase.mock.calls[notificationCallIndex][0].onMessage
      handler({ type: 'notification', data: { id: 1 } })
      
      expect(socket.lastMessage.value).toEqual({ type: 'notification', data: { id: 1 } })
      expect(socket.messageHistory.value.length).toBeGreaterThan(0)
    })

    it('should limit message history', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      socket.connect()
      
      // Get handler from notification socket
      const notificationCallIndex = useWebSocketBase.mock.calls.findIndex(call => {
        return call[0]?.url?.includes('/notifications/')
      })
      expect(notificationCallIndex).toBeGreaterThanOrEqual(0)
      const handler = useWebSocketBase.mock.calls[notificationCallIndex][0].onMessage
      
      // Add more than 100 messages
      for (let i = 0; i < 150; i++) {
        handler({ type: 'notification', data: { id: i } })
      }
      
      expect(socket.messageHistory.value.length).toBeLessThanOrEqual(100)
    })
  })

  describe('getWebSocketUrl', () => {
    it('should use VITE_WS_URL when available', () => {
      const originalEnv = import.meta.env
      import.meta.env.VITE_WS_URL = 'ws://custom-url.com'
      
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      socket.connect()
      
      expect(useWebSocketBase).toHaveBeenCalled()
      import.meta.env = originalEnv
    })

    it('should use globalThis.__API_BASE_URL__ when available', () => {
      globalThis.__API_BASE_URL__ = 'https://api.example.com/api/v1'
      
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      socket.connect()
      
      expect(useWebSocketBase).toHaveBeenCalled()
      delete globalThis.__API_BASE_URL__
    })

    it('should use VITE_API_BASE_URL when available', () => {
      const originalEnv = import.meta.env
      import.meta.env.VITE_API_BASE_URL = 'https://api.example.com/api/v1'
      
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      socket.connect()
      
      expect(useWebSocketBase).toHaveBeenCalled()
      import.meta.env = originalEnv
    })
  })

  describe('error handling', () => {
    it('should handle notification socket error', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      const callback = vi.fn()
      
      socket.on('connection-error', callback)
      
      socket.connect()
      const errorHandler = useWebSocketBase.mock.calls[0][0].onError
      errorHandler(new Error('Connection failed'))
      
      expect(socket.connectionError.value).toBe('Error de conexión de notificaciones')
      expect(callback).toHaveBeenCalled()
    })

    it('should handle system status socket error', () => {
      mockAuthStore.user = { id: 1 }
      const socket = useWebSocket()
      const callback = vi.fn()
      
      socket.on('connection-error', callback)
      
      socket.connect()
      const errorHandler = useWebSocketBase.mock.calls[1][0].onError
      errorHandler(new Error('Connection failed'))
      
      expect(callback).toHaveBeenCalled()
    })
  })
})

