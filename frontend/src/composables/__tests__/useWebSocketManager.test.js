/**
 * Unit tests for useWebSocketManager composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useWebSocketManager } from '../useWebSocketManager.js'
import { useWebSocketBase } from '../useWebSocketBase'

// Mock useWebSocketBase
const mockConnection = {
  isConnected: { value: false },
  isConnecting: { value: false },
  connectionStatus: { value: 'disconnected' },
  connect: vi.fn(),
  disconnect: vi.fn(),
  reconnect: vi.fn(),
  send: vi.fn()
}

vi.mock('../useWebSocketBase', () => ({
  useWebSocketBase: vi.fn(() => mockConnection)
}))

describe('useWebSocketManager', () => {
  let manager

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should initialize with connections', () => {
      manager = useWebSocketManager({
        connections: {
          notifications: { url: 'ws://test.com/notifications' },
          system: { url: 'ws://test.com/system' }
        }
      })
      
      expect(useWebSocketBase).toHaveBeenCalledTimes(2)
      expect(manager.connectionInstances.value).toHaveProperty('notifications')
      expect(manager.connectionInstances.value).toHaveProperty('system')
    })
  })

  describe('getConnection', () => {
    it('should get connection by name', () => {
      manager = useWebSocketManager({
        connections: {
          test: { url: 'ws://test.com' }
        }
      })
      
      const connection = manager.getConnection('test')
      
      expect(connection).toBeDefined()
    })

    it('should return null for non-existent connection', () => {
      manager = useWebSocketManager({
        connections: {}
      })
      
      const connection = manager.getConnection('nonexistent')
      
      expect(connection).toBeNull()
    })
  })

  describe('connectAll', () => {
    it('should connect all connections', () => {
      manager = useWebSocketManager({
        connections: {
          conn1: { url: 'ws://test.com/1' },
          conn2: { url: 'ws://test.com/2' }
        }
      })
      
      manager.connectAll()
      
      expect(mockConnection.connect).toHaveBeenCalledTimes(2)
    })
  })

  describe('disconnectAll', () => {
    it('should disconnect all connections', () => {
      manager = useWebSocketManager({
        connections: {
          conn1: { url: 'ws://test.com/1' }
        }
      })
      
      manager.disconnectAll()
      
      expect(mockConnection.disconnect).toHaveBeenCalled()
    })
  })

  describe('send', () => {
    it('should send message to specific connection', () => {
      manager = useWebSocketManager({
        connections: {
          test: { url: 'ws://test.com' }
        }
      })
      
      manager.send('test', { type: 'message' })
      
      expect(mockConnection.send).toHaveBeenCalledWith({ type: 'message' })
    })

    it('should not send if connection does not exist', () => {
      manager = useWebSocketManager({
        connections: {}
      })
      
      manager.send('nonexistent', { type: 'message' })
      
      expect(mockConnection.send).not.toHaveBeenCalled()
    })
  })

  describe('computed properties', () => {
    it('should compute isAnyConnected', () => {
      mockConnection.isConnected.value = true
      
      manager = useWebSocketManager({
        connections: {
          test: { url: 'ws://test.com' }
        }
      })
      
      expect(manager.isAnyConnected.value).toBe(true)
    })

    it('should compute allConnected', () => {
      mockConnection.isConnected.value = true
      
      manager = useWebSocketManager({
        connections: {
          conn1: { url: 'ws://test.com/1' },
          conn2: { url: 'ws://test.com/2' }
        }
      })
      
      expect(manager.allConnected.value).toBe(true)
    })
  })
})

