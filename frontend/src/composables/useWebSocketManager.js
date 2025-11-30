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
  for (const [name, config] of Object.entries(connections)) {
    connectionInstances.value[name] = useWebSocketBase({
      url: config.url,
      onMessage: config.onMessage,
      onError: config.onError,
      reconnectInterval: config.reconnectInterval || 3000,
      maxReconnectAttempts: config.maxReconnectAttempts || 5
    })
  }

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
    for (const connection of Object.values(connectionInstances.value)) {
      connection.connect()
    }
  }

  /**
   * Disconnect all connections
   */
  const disconnectAll = () => {
    for (const connection of Object.values(connectionInstances.value)) {
      connection.disconnect()
    }
  }

  /**
   * Reconnect all connections
   */
  const reconnectAll = () => {
    for (const connection of Object.values(connectionInstances.value)) {
      connection.reconnect()
    }
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
    for (const [name, conn] of Object.entries(connectionInstances.value)) {
      statuses[name] = conn.connectionStatus.value
    }
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

