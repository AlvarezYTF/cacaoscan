/**
 * Unit tests for useWebSocket composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useWebSocket } from '../useWebSocket.js'
import { useWebSocketBase } from '../useWebSocketBase'
import { useAuthStore } from '@/stores/auth'

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
  })
})

