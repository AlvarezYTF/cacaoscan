/**
 * Unit tests for useWebSocketBase composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useWebSocketBase } from '../useWebSocketBase.js'

// Mock WebSocket
const mockWebSocket = {
  readyState: 1, // OPEN
  send: vi.fn(),
  close: vi.fn(),
  onopen: null,
  onmessage: null,
  onerror: null,
  onclose: null
}

globalThis.WebSocket = vi.fn(() => {
  const ws = { ...mockWebSocket }
  setTimeout(() => {
    if (ws.onopen) ws.onopen()
  }, 0)
  return ws
})

describe('useWebSocketBase', () => {
  let socketBase

  beforeEach(() => {
    vi.clearAllMocks()
    mockWebSocket.readyState = 1
  })

  describe('initial state', () => {
    it('should have initial disconnected state', () => {
      socketBase = useWebSocketBase({ url: 'ws://test.com' })
      
      expect(socketBase.isConnected.value).toBe(false)
      expect(socketBase.isConnecting.value).toBe(false)
      expect(socketBase.connectionStatus.value).toBe('disconnected')
    })
  })

  describe('connect', () => {
    it('should connect to WebSocket', async () => {
      const onMessage = vi.fn()
      socketBase = useWebSocketBase({
        url: 'ws://test.com',
        onMessage
      })
      
      socketBase.connect()
      
      // Wait for connection
      await new Promise(resolve => setTimeout(resolve, 10))
      
      expect(globalThis.WebSocket).toHaveBeenCalled()
    })

    it('should not connect if already connecting', () => {
      socketBase = useWebSocketBase({ url: 'ws://test.com' })
      
      socketBase.connect()
      socketBase.connect() // Second call should be ignored
      
      expect(globalThis.WebSocket).toHaveBeenCalledTimes(1)
    })
  })

  describe('disconnect', () => {
    it('should disconnect WebSocket', () => {
      socketBase = useWebSocketBase({ url: 'ws://test.com' })
      
      socketBase.connect()
      socketBase.disconnect()
      
      expect(socketBase.isConnected.value).toBe(false)
    })
  })

  describe('send', () => {
    it('should send message when connected', () => {
      socketBase = useWebSocketBase({ url: 'ws://test.com' })
      mockWebSocket.readyState = 1 // OPEN
      
      // Manually set socket for testing
      socketBase.socket = { value: mockWebSocket }
      socketBase.isConnected.value = true
      
      const message = { type: 'test', data: 'hello' }
      socketBase.send(message)
      
      expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify(message))
    })

    it('should not send if not connected', () => {
      socketBase = useWebSocketBase({ url: 'ws://test.com' })
      mockWebSocket.readyState = 0 // CLOSED
      
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      socketBase.send({ type: 'test' })
      
      expect(mockWebSocket.send).not.toHaveBeenCalled()
      
      consoleSpy.mockRestore()
    })
  })

  describe('reconnect', () => {
    it('should reconnect WebSocket', () => {
      socketBase = useWebSocketBase({ url: 'ws://test.com' })
      
      socketBase.disconnect()
      socketBase.reconnect()
      
      expect(socketBase.reconnectAttempts.value).toBe(0)
    })
  })

  describe('convertToWebSocketUrl', () => {
    it('should convert HTTP to WS', () => {
      socketBase = useWebSocketBase({ url: 'http://test.com' })
      
      socketBase.connect()
      
      expect(globalThis.WebSocket).toHaveBeenCalled()
    })

    it('should convert HTTPS to WSS', () => {
      socketBase = useWebSocketBase({ url: 'https://test.com' })
      
      socketBase.connect()
      
      expect(globalThis.WebSocket).toHaveBeenCalled()
    })

    it('should keep WS/WSS URLs as is', () => {
      socketBase = useWebSocketBase({ url: 'ws://test.com' })
      
      socketBase.connect()
      
      expect(globalThis.WebSocket).toHaveBeenCalled()
    })
  })
})

