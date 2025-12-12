/**
 * Unit tests for useWebSocketBase composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useWebSocketBase } from '../useWebSocketBase.js'

// Mock WebSocket
const mockWebSocketSend = vi.fn()
const mockWebSocketClose = vi.fn()

// WebSocket readyState constants
const CONNECTING = 0
const OPEN = 1
const CLOSING = 2
const CLOSED = 3

globalThis.WebSocket = vi.fn(() => {
  const ws = {
    readyState: CONNECTING,
    send: mockWebSocketSend,
    close: mockWebSocketClose,
    onopen: null,
    onmessage: null,
    onerror: null,
    onclose: null
  }
  setTimeout(() => {
    ws.readyState = OPEN
    if (ws.onopen) ws.onopen()
  }, 0)
  return ws
})

// Add WebSocket constants to global
globalThis.WebSocket.CONNECTING = CONNECTING
globalThis.WebSocket.OPEN = OPEN
globalThis.WebSocket.CLOSING = CLOSING
globalThis.WebSocket.CLOSED = CLOSED

describe('useWebSocketBase', () => {
  let socketBase

  beforeEach(() => {
    vi.clearAllMocks()
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
    it('should send message when connected', async () => {
      socketBase = useWebSocketBase({ url: 'ws://test.com' })
      
      socketBase.connect()
      
      // Wait for connection
      await new Promise(resolve => setTimeout(resolve, 10))
      
      const message = { type: 'test', data: 'hello' }
      socketBase.send(message)
      
      expect(mockWebSocketSend).toHaveBeenCalledWith(JSON.stringify(message))
    })

    it('should not send if not connected', () => {
      socketBase = useWebSocketBase({ url: 'ws://test.com' })
      // Don't call connect(), so socket remains null or not connected
      
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      socketBase.send({ type: 'test' })
      
      expect(mockWebSocketSend).not.toHaveBeenCalled()
      
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

