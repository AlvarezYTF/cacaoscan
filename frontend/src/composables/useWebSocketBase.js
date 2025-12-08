/**
 * Base composable for a single WebSocket connection
 * Provides connection management, message handling, and reconnection logic
 */
import { ref, computed, onUnmounted } from 'vue'

/**
 * Create base WebSocket composable
 * @param {Object} options - WebSocket options
 * @param {string} options.url - WebSocket URL
 * @param {Function} options.onMessage - Message handler
 * @param {Function} options.onError - Error handler
 * @param {number} options.reconnectInterval - Reconnect interval in ms
 * @param {number} options.maxReconnectAttempts - Maximum reconnect attempts
 * @returns {Object} WebSocket state and methods
 */
export function useWebSocketBase(options = {}) {
  const {
    url = '',
    onMessage = null,
    onError = null,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5
  } = options

  // State
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const connectionError = ref(null)
  const lastMessage = ref(null)
  const messageHistory = ref([])
  const reconnectAttempts = ref(0)
  const socket = ref(null)
  let reconnectTimer = null
  let heartbeatInterval = null

  // Computed
  const connectionStatus = computed(() => {
    if (isConnecting.value) return 'connecting'
    if (isConnected.value) return 'connected'
    if (connectionError.value) return 'error'
    return 'disconnected'
  })

  /**
   * Convert HTTP/HTTPS URL to WS/WSS
   * @param {string} httpUrl - HTTP URL
   * @returns {string} WebSocket URL
   */
  const convertToWebSocketUrl = (httpUrl) => {
    if (!httpUrl) return ''
    
    if (httpUrl.startsWith('ws://') || httpUrl.startsWith('wss://')) {
      return httpUrl
    }

    if (httpUrl.startsWith('http://')) {
      return httpUrl.replace('http://', 'ws://')
    }

    if (httpUrl.startsWith('https://')) {
      return httpUrl.replace('https://', 'wss://')
    }

    return httpUrl
  }

  /**
   * Handle WebSocket message
   * @param {MessageEvent} event - Message event
   */
  const handleMessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      lastMessage.value = data
      messageHistory.value.push(data)

      // Keep only last 100 messages
      if (messageHistory.value.length > 100) {
        messageHistory.value.shift()
      }

      if (onMessage && typeof onMessage === 'function') {
        onMessage(data)
      }
    } catch (err) {
      }
  }

  /**
   * Handle WebSocket error
   * @param {Event} event - Error event
   */
  const handleError = (event) => {
    connectionError.value = 'WebSocket connection error'
    isConnected.value = false
    isConnecting.value = false

    if (onError && typeof onError === 'function') {
      onError(event)
    }
  }

  /**
   * Handle WebSocket close
   */
  const handleClose = () => {
    isConnected.value = false
    isConnecting.value = false

    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }

    // Attempt reconnect if not manually closed
    if (reconnectAttempts.value < maxReconnectAttempts) {
      reconnectAttempts.value++
      reconnectTimer = setTimeout(() => {
        connect()
      }, reconnectInterval)
    }
  }

  /**
   * Start heartbeat
   */
  const startHeartbeat = () => {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
    }

    heartbeatInterval = setInterval(() => {
      if (socket.value && socket.value.readyState === WebSocket.OPEN) {
        socket.value.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000) // 30 seconds
  }

  /**
   * Connect to WebSocket
   */
  const connect = () => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      return
    }

    if (isConnecting.value) {
      return
    }

    isConnecting.value = true
    connectionError.value = null

    try {
      const wsUrl = convertToWebSocketUrl(url)
      socket.value = new WebSocket(wsUrl)

      socket.value.onopen = () => {
        isConnected.value = true
        isConnecting.value = false
        reconnectAttempts.value = 0
        startHeartbeat()
      }

      socket.value.onmessage = handleMessage
      socket.value.onerror = handleError
      socket.value.onclose = handleClose
    } catch (err) {
      connectionError.value = err.message
      isConnecting.value = false
      handleClose()
    }
  }

  /**
   * Disconnect WebSocket
   */
  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }

    if (socket.value) {
      socket.value.close()
      socket.value = null
    }

    isConnected.value = false
    isConnecting.value = false
    reconnectAttempts.value = 0
  }

  /**
   * Reconnect WebSocket
   */
  const reconnect = () => {
    disconnect()
    reconnectAttempts.value = 0
    connect()
  }

  /**
   * Send message through WebSocket
   * @param {Object} data - Message data
   */
  const send = (data) => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify(data))
    } else {
      }
  }

  // Cleanup on unmount
  onUnmounted(() => {
    disconnect()
  })

  return {
    // State
    isConnected,
    isConnecting,
    connectionError,
    lastMessage,
    messageHistory,
    reconnectAttempts,

    // Computed
    connectionStatus,

    // Methods
    connect,
    disconnect,
    reconnect,
    send
  }
}

