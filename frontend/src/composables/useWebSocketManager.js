/**
 * Composable for managing multiple WebSocket connections
 * Uses useWebSocketBase for each connection
 */
import { ref, computed } from 'vue'
import { useWebSocketBase } from './useWebSocketBase'

/**
 * Create WebSocket manager composable
 * @param {Object} options - Manager options
 * @param {Object} options.connections - Connection configurations
 * @returns {Object} Manager state and methods
 */
export function useWebSocketManager(options = {}) {
  const {
    connections = {}
  } = options

  // Connection instances
  const connectionInstances = ref({})

  // Initialize connections
  Object.entries(connections).forEach(([name, config]) => {
    connectionInstances.value[name] = useWebSocketBase({
      url: config.url,
      onMessage: config.onMessage,
      onError: config.onError,
      reconnectInterval: config.reconnectInterval || 3000,
      maxReconnectAttempts: config.maxReconnectAttempts || 5
    })
  })

  /**
   * Get connection by name
   * @param {string} name - Connection name
   * @returns {Object|null} Connection instance
   */
  const getConnection = (name) => {
    return connectionInstances.value[name] || null
  }

  /**
   * Connect all connections
   */
  const connectAll = () => {
    Object.values(connectionInstances.value).forEach(connection => {
      connection.connect()
    })
  }

  /**
   * Disconnect all connections
   */
  const disconnectAll = () => {
    Object.values(connectionInstances.value).forEach(connection => {
      connection.disconnect()
    })
  }

  /**
   * Reconnect all connections
   */
  const reconnectAll = () => {
    Object.values(connectionInstances.value).forEach(connection => {
      connection.reconnect()
    })
  }

  /**
   * Send message to specific connection
   * @param {string} connectionName - Connection name
   * @param {Object} data - Message data
   */
  const send = (connectionName, data) => {
    const connection = getConnection(connectionName)
    if (connection) {
      connection.send(data)
    }
  }

  // Computed
  const isAnyConnected = computed(() => {
    return Object.values(connectionInstances.value).some(
      conn => conn.isConnected.value
    )
  })

  const allConnected = computed(() => {
    return Object.values(connectionInstances.value).every(
      conn => conn.isConnected.value
    )
  })

  const connectionStatuses = computed(() => {
    const statuses = {}
    Object.entries(connectionInstances.value).forEach(([name, conn]) => {
      statuses[name] = conn.connectionStatus.value
    })
    return statuses
  })

  return {
    // State
    connectionInstances,

    // Computed
    isAnyConnected,
    allConnected,
    connectionStatuses,

    // Methods
    getConnection,
    connectAll,
    disconnectAll,
    reconnectAll,
    send
  }
}

