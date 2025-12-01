/**
 * Tests unitarios para composables de CacaoScan.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useImageStats } from '../useImageStats.js'
import { useWebSocket } from '../useWebSocket.js'

// Mock de servicios
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    isAuthenticated: true,
    user: { id: 1 }
  })
}))

describe('useImageStats', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('inicializa correctamente', () => {
    const result = useImageStats()
    
    expect(result).toBeDefined()
    expect(result.stats).toBeDefined()
    expect(result.loading).toBeDefined()
    expect(result.error).toBeDefined()
  })

  it('tiene función fetchStats', () => {
    const result = useImageStats()
    
    expect(typeof result.fetchStats).toBe('function')
  })
})

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('inicializa correctamente', () => {
    const result = useWebSocket()
    
    expect(result).toBeDefined()
    expect(result.isConnected).toBeDefined()
    expect(result.isConnecting).toBeDefined()
    expect(result.connectionError).toBeDefined()
  })

  it('tiene función connect', () => {
    const result = useWebSocket()
    
    expect(typeof result.connect).toBe('function')
  })

  it('tiene función disconnect', () => {
    const result = useWebSocket()
    
    expect(typeof result.disconnect).toBe('function')
  })
})
