/**
 * Unit tests for useConfigStoreWrapper composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useConfigStoreWrapper } from '../useConfigStoreWrapper.js'

// Mock dependencies
const mockStore = {
  general: {},
  security: {},
  ml: {},
  system: {},
  loading: false,
  lastUpdate: null,
  updateGeneralConfig: vi.fn(),
  updateSecurityConfig: vi.fn(),
  updateMLConfig: vi.fn(),
  resetGeneralConfig: vi.fn(),
  resetSecurityConfig: vi.fn(),
  resetMLConfig: vi.fn(),
  resetAllConfig: vi.fn(),
  saveAllConfig: vi.fn()
}

vi.mock('@/stores/config', () => ({
  useConfigStore: () => mockStore
}))

describe('useConfigStoreWrapper', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    wrapper = useConfigStoreWrapper()
  })

  describe('initial state', () => {
    it('should expose store state', () => {
      expect(wrapper.general.value).toEqual({})
      expect(wrapper.loading.value).toBe(false)
    })
  })

  describe('getConfig', () => {
    it('should get config value by key', () => {
      mockStore.general = { nombre_sistema: 'Test System' }
      
      // Re-create to get new computed
      const newWrapper = useConfigStoreWrapper()
      const value = newWrapper.getConfig('general.nombre_sistema')
      
      expect(value).toBe('Test System')
    })

    it('should return undefined for non-existent key', () => {
      const value = wrapper.getConfig('general.nonexistent')
      
      expect(value).toBeUndefined()
    })
  })

  describe('setConfig', () => {
    it('should set general config', async () => {
      await wrapper.setConfig('general.nombre_sistema', 'New System')
      
      expect(mockStore.updateGeneralConfig).toHaveBeenCalledWith({
        nombre_sistema: 'New System'
      })
    })

    it('should set security config', async () => {
      await wrapper.setConfig('security.session_timeout', 30)
      
      expect(mockStore.updateSecurityConfig).toHaveBeenCalledWith({
        session_timeout: 30
      })
    })

    it('should throw error for unknown section', async () => {
      await expect(wrapper.setConfig('unknown.key', 'value')).rejects.toThrow()
    })
  })

  describe('validateConfig', () => {
    it('should validate nombre_sistema', () => {
      expect(wrapper.validateConfig('general.nombre_sistema', '')).toBeTruthy()
      expect(wrapper.validateConfig('general.nombre_sistema', 'Valid Name')).toBeNull()
    })

    it('should validate email_contacto', () => {
      expect(wrapper.validateConfig('general.email_contacto', 'invalid')).toBeTruthy()
      expect(wrapper.validateConfig('general.email_contacto', 'test@example.com')).toBeNull()
    })

    it('should validate session_timeout', () => {
      expect(wrapper.validateConfig('security.session_timeout', 2)).toBeTruthy()
      expect(wrapper.validateConfig('security.session_timeout', 30)).toBeNull()
    })
  })
})

