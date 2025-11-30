// Tests unitarios para servicios de CacaoScan Frontend.
import { describe, it, expect, beforeEach, vi } from 'vitest'
import api from '../api.js'

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exporta api service', () => {
    expect(api).toBeDefined()
    expect(typeof api.get).toBe('function')
    expect(typeof api.post).toBe('function')
  })
})

