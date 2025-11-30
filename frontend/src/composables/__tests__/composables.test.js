/**
 * Tests unitarios para composables de CacaoScan.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref, nextTick } from 'vue'
import { useImageStats } from '../composables/useImageStats.js'
import { useWebSocket } from '../composables/useWebSocket.js'

// Mock de servicios
vi.mock('../services/api.js', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('../services/predictionApi.js', () => ({
  default: {
    getAnalysisHistory: vi.fn(),
    getAnalysisStats: vi.fn()
  }
}))

describe('useImageStats', () => {
  let mockApi
  let mockPredictionApi

  beforeEach(() => {
    mockApi = {
      get: vi.fn()
    }
    mockPredictionApi = {
      getAnalysisHistory: vi.fn(),
      getAnalysisStats: vi.fn()
    }
    
    vi.clearAllMocks()
  })

  it('inicializa con valores por defecto', () => {
    const { stats, loading, error } = useImageStats()
    
    expect(stats.value).toEqual({
      totalImages: 0,
      totalAnalyses: 0,
      averageQuality: 0,
      successRate: 0
    })
    expect(loading.value).toBe(false)
    expect(error.value).toBe(null)
  })

  it('carga estadísticas correctamente', async () => {
    const mockStats = {
      totalImages: 100,
      totalAnalyses: 95,
      averageQuality: 85.5,
      successRate: 95.0
    }
    
    mockPredictionApi.getAnalysisStats.mockResolvedValue({
      data: mockStats
    })
    
    const { stats, loading, error, loadStats } = useImageStats()
    
    await loadStats()
    
    expect(loading.value).toBe(false)
    expect(error.value).toBe(null)
    expect(stats.value).toEqual(mockStats)
    expect(mockPredictionApi.getAnalysisStats).toHaveBeenCalled()
  })

  it('maneja errores de carga', async () => {
    const mockError = new Error('Error de red')
    mockPredictionApi.getAnalysisStats.mockRejectedValue(mockError)
    
    const { stats, loading, error, loadStats } = useImageStats()
    
    await loadStats()
    
    expect(loading.value).toBe(false)
    expect(error.value).toBe('Error de red')
    expect(stats.value).toEqual({
      totalImages: 0,
      totalAnalyses: 0,
      averageQuality: 0,
      successRate: 0
    })
  })

  it('actualiza estadísticas en tiempo real', async () => {
    const { stats, updateStats } = useImageStats()
    
    const newStats = {
      totalImages: 150,
      totalAnalyses: 140,
      averageQuality: 88.0,
      successRate: 93.3
    }
    
    updateStats(newStats)
    
    expect(stats.value).toEqual(newStats)
  })

  it('calcula estadísticas derivadas', () => {
    const { stats, derivedStats } = useImageStats()
    
    stats.value = {
      totalImages: 100,
      totalAnalyses: 95,
      averageQuality: 85.5,
      successRate: 95.0
    }
    
    expect(derivedStats.value.failureRate).toBe(5.0)
    expect(derivedStats.value.pendingAnalyses).toBe(5)
  })

  it('filtra estadísticas por período', async () => {
    const mockStats = {
      totalImages: 50,
      totalAnalyses: 45,
      averageQuality: 87.0,
      successRate: 90.0
    }
    
    mockPredictionApi.getAnalysisStats.mockResolvedValue({
      data: mockStats
    })
    
    const { loadStatsByPeriod } = useImageStats()
    
    const startDate = '2024-01-01'
    const endDate = '2024-01-31'
    
    await loadStatsByPeriod(startDate, endDate)
    
    expect(mockPredictionApi.getAnalysisStats).toHaveBeenCalledWith({
      start_date: startDate,
      end_date: endDate
    })
  })

  it('refresca estadísticas automáticamente', async () => {
    vi.useFakeTimers()
    
    const { refreshInterval } = useImageStats()
    
    expect(refreshInterval.value).toBe(30000) // 30 segundos
    
    vi.useRealTimers()
  })

  it('limpia recursos al desmontar', () => {
    const { cleanup } = useImageStats()
    
    expect(() => cleanup()).not.toThrow()
  })
})

describe('useWebSocket', () => {
  let mockWebSocket
  let mockOnOpen
  let mockOnMessage
  let mockOnClose
  let mockOnError

  beforeEach(() => {
    mockOnOpen = vi.fn()
    mockOnMessage = vi.fn()
    mockOnClose = vi.fn()
    mockOnError = vi.fn()
    
    mockWebSocket = {
      readyState: WebSocket.CONNECTING,
      send: vi.fn(),
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    }
    
    global.WebSocket = vi.fn(() => mockWebSocket)
    vi.clearAllMocks()
  })

  it('inicializa con estado desconectado', () => {
    const { isConnected, isConnecting, error } = useWebSocket()
    
    expect(isConnected.value).toBe(false)
    expect(isConnecting.value).toBe(true)
    expect(error.value).toBe(null)
  })

  it('conecta correctamente', async () => {
    const { connect, isConnected, isConnecting } = useWebSocket()
    
    await connect('ws://localhost:8000/ws/')
    
    expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:8000/ws/')
    expect(isConnecting.value).toBe(true)
  })

  it('maneja conexión exitosa', () => {
    const { isConnected, isConnecting, error } = useWebSocket()
    
    // Simular evento de conexión
    mockWebSocket.readyState = WebSocket.OPEN
    mockOnOpen()
    
    expect(isConnected.value).toBe(true)
    expect(isConnecting.value).toBe(false)
    expect(error.value).toBe(null)
  })

  it('maneja mensajes recibidos', () => {
    const { messages, lastMessage } = useWebSocket()
    
    const testMessage = {
      type: 'notification',
      data: { message: 'Test notification' }
    }
    
    // Simular evento de mensaje
    mockOnMessage({ data: JSON.stringify(testMessage) })
    
    expect(messages.value).toHaveLength(1)
    expect(lastMessage.value).toEqual(testMessage)
  })

  it('envía mensajes correctamente', () => {
    const { sendMessage } = useWebSocket()
    
    const testMessage = {
      type: 'ping',
      data: { timestamp: Date.now() }
    }
    
    sendMessage(testMessage)
    
    expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify(testMessage))
  })

  it('maneja errores de conexión', () => {
    const { error, isConnected, isConnecting } = useWebSocket()
    
    const testError = new Error('Connection failed')
    
    // Simular evento de error
    mockOnError(testError)
    
    expect(error.value).toBe('Connection failed')
    expect(isConnected.value).toBe(false)
    expect(isConnecting.value).toBe(false)
  })

  it('maneja cierre de conexión', () => {
    const { isConnected, isConnecting } = useWebSocket()
    
    // Simular evento de cierre
    mockWebSocket.readyState = WebSocket.CLOSED
    mockOnClose()
    
    expect(isConnected.value).toBe(false)
    expect(isConnecting.value).toBe(false)
  })

  it('reconecta automáticamente', async () => {
    const { reconnect, isConnected } = useWebSocket()
    
    await reconnect()
    
    expect(global.WebSocket).toHaveBeenCalled()
  })

  it('limpia conexión al desmontar', () => {
    const { cleanup } = useWebSocket()
    
    cleanup()
    
    expect(mockWebSocket.close).toHaveBeenCalled()
  })

  it('filtra mensajes por tipo', () => {
    const { messages, getMessagesByType } = useWebSocket()
    
    const notificationMessage = {
      type: 'notification',
      data: { message: 'Test notification' }
    }
    
    const analysisMessage = {
      type: 'analysis_complete',
      data: { analysisId: 1 }
    }
    
    messages.value = [notificationMessage, analysisMessage]
    
    const notifications = getMessagesByType('notification')
    const analyses = getMessagesByType('analysis_complete')
    
    expect(notifications).toHaveLength(1)
    expect(analyses).toHaveLength(1)
    expect(notifications[0]).toEqual(notificationMessage)
    expect(analyses[0]).toEqual(analysisMessage)
  })

  it('mantiene historial de mensajes limitado', () => {
    const { messages, maxHistory } = useWebSocket()
    
    // Simular muchos mensajes
    for (let i = 0; i < maxHistory.value + 10; i++) {
      mockOnMessage({
        data: JSON.stringify({
          type: 'test',
          data: { id: i }
        })
      })
    }
    
    expect(messages.value.length).toBeLessThanOrEqual(maxHistory.value)
  })

  it('maneja reconexión con backoff exponencial', async () => {
    const { reconnectWithBackoff } = useWebSocket()
    
    vi.useFakeTimers()
    
    await reconnectWithBackoff()
    
    // Verificar que se programa reconexión
    expect(setTimeout).toHaveBeenCalled()
    
    vi.useRealTimers()
  })

  it('valida formato de mensaje', () => {
    const { validateMessage } = useWebSocket()
    
    const validMessage = {
      type: 'notification',
      data: { message: 'Test' }
    }
    
    const invalidMessage = {
      invalid: 'format'
    }
    
    expect(validateMessage(validMessage)).toBe(true)
    expect(validateMessage(invalidMessage)).toBe(false)
  })

  it('maneja heartbeat para mantener conexión', () => {
    const { startHeartbeat, stopHeartbeat } = useWebSocket()
    
    startHeartbeat()
    
    // Verificar que se inicia heartbeat
    expect(setInterval).toHaveBeenCalled()
    
    stopHeartbeat()
    
    // Verificar que se detiene heartbeat
    expect(clearInterval).toHaveBeenCalled()
  })
})
