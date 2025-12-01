import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useConfigStore } from '../config.js'

// Mock configApi
vi.mock('@/services/configApi', () => ({
  default: {
    getSystemConfig: vi.fn(),
    getGeneralConfig: vi.fn(),
    getSecurityConfig: vi.fn(),
    getMLConfig: vi.fn(),
    saveGeneralConfig: vi.fn(),
    saveSecurityConfig: vi.fn(),
    saveMLConfig: vi.fn()
  }
}))

// Import configApi after mock
import configApi from '@/services/configApi'

// Mock auth store
const mockAuthStore = {
  isAdmin: false,
  isAnalyst: false
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock globalThis.dispatchEvent
globalThis.dispatchEvent = vi.fn()

describe('ConfigStore', () => {
  let configStore

  beforeEach(() => {
    setActivePinia(createPinia())
    configStore = useConfigStore()
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      expect(configStore.general.nombre_sistema).toBe('CacaoScan')
      expect(configStore.general.email_contacto).toBe('contacto@cacaoscan.com')
      expect(configStore.security.recaptcha_enabled).toBe(true)
      expect(configStore.security.session_timeout).toBe(60)
      expect(configStore.ml.active_model).toBe('yolov8')
      expect(configStore.system.version).toBe('1.0.0')
      expect(configStore.loading).toBe(false)
      expect(configStore.lastUpdate).toBe(null)
    })
  })

  describe('Getters', () => {
    it('should return brandName from general config', () => {
      expect(configStore.brandName).toBe('CacaoScan')
    })

    it('should return sistemaLema from general config', () => {
      expect(configStore.sistemaLema).toBe('La mejor plataforma para el control de calidad del cacao')
    })

    it('should return sistemaLogo from general config', () => {
      expect(configStore.sistemaLogo).toBe(null)
    })

    it('should return getGeneralConfig', () => {
      expect(configStore.getGeneralConfig).toEqual({
        nombre_sistema: 'CacaoScan',
        email_contacto: 'contacto@cacaoscan.com',
        lema: 'La mejor plataforma para el control de calidad del cacao',
        logo_url: null
      })
    })

    it('should return getSecurityConfig', () => {
      expect(configStore.getSecurityConfig).toEqual({
        recaptcha_enabled: true,
        session_timeout: 60,
        login_attempts: 5,
        two_factor_auth: false
      })
    })

    it('should return getMLConfig', () => {
      expect(configStore.getMLConfig).toEqual({
        active_model: 'yolov8',
        last_training: null
      })
    })

    it('should return getSystemConfig', () => {
      expect(configStore.getSystemConfig).toEqual({
        version: '1.0.0',
        server_status: 'online',
        backend_version: '4.2.7',
        frontend_version: '3.5.3',
        database: 'PostgreSQL 16'
      })
    })
  })

  describe('loadAll', () => {
    it('should load all configs for admin user', async () => {
      mockAuthStore.isAdmin = true
      // _buildConfigPromises creates: [system, general, security, ml]
      // _processConfigResults maps: { system: results[0], general: results[1], security: results[2], ml: results[3] }
      configApi.getSystemConfig.mockResolvedValue({
        version: '2.0.0',
        server_status: 'online'
      })
      configApi.getGeneralConfig.mockResolvedValue({
        nombre_sistema: 'New Name',
        email_contacto: 'new@example.com'
      })
      configApi.getSecurityConfig.mockResolvedValue({
        session_timeout: 120
      })
      configApi.getMLConfig.mockResolvedValue({
        active_model: 'yolov9'
      })

      const result = await configStore.loadAll()

      expect(result.success).toBe(true)
      expect(result.loaded).toBe(true)
      expect(configStore.general.nombre_sistema).toBe('New Name')
      expect(configStore.security.session_timeout).toBe(120)
      expect(configStore.ml.active_model).toBe('yolov9')
      expect(configStore.lastUpdate).toBeInstanceOf(Date)
    })

    it('should load only system config for non-admin user', async () => {
      mockAuthStore.isAdmin = false
      mockAuthStore.isAnalyst = false

      configApi.getSystemConfig.mockResolvedValue({
        version: '1.0.0',
        server_status: 'online'
      })

      const result = await configStore.loadAll()

      expect(result.success).toBe(true)
      expect(configApi.getGeneralConfig).not.toHaveBeenCalled()
      expect(configApi.getSecurityConfig).not.toHaveBeenCalled()
      expect(configApi.getMLConfig).not.toHaveBeenCalled()
    })

    it('should handle errors gracefully', async () => {
      mockAuthStore.isAdmin = false
      const error = new Error('Network error')
      error.response = { status: 500 }

      configApi.getSystemConfig.mockRejectedValue(error)

      const result = await configStore.loadAll()

      expect(result.success).toBe(false)
      expect(result.loaded).toBe(false)
      expect(configStore.loading).toBe(false)
    })

    it('should set loading state correctly', async () => {
      mockAuthStore.isAdmin = false
      const delayedPromise = new Promise((resolve) => setTimeout(resolve, 100))
      configApi.getSystemConfig.mockImplementation(() => delayedPromise)

      const loadPromise = configStore.loadAll()

      expect(configStore.loading).toBe(true)

      await loadPromise

      expect(configStore.loading).toBe(false)
    })
  })

  describe('saveGeneral', () => {
    it('should save general config successfully', async () => {
      const data = {
        nombre_sistema: 'New System',
        email_contacto: 'new@example.com',
        lema: 'New lema'
      }

      configApi.saveGeneralConfig.mockResolvedValue(data)

      await configStore.saveGeneral(data)

      expect(configApi.saveGeneralConfig).toHaveBeenCalledWith(data)
      expect(configStore.general.nombre_sistema).toBe('New System')
      expect(configStore.general.email_contacto).toBe('new@example.com')
      expect(configStore.lastUpdate).toBeInstanceOf(Date)
      expect(globalThis.dispatchEvent).toHaveBeenCalled()
    })

    it('should handle save errors', async () => {
      const data = { nombre_sistema: 'New' }
      const error = new Error('Save failed')

      configApi.saveGeneralConfig.mockRejectedValue(error)

      await expect(configStore.saveGeneral(data)).rejects.toThrow('Save failed')
    })
  })

  describe('saveSecurity', () => {
    it('should save security config successfully', async () => {
      const data = {
        session_timeout: 120,
        login_attempts: 10
      }

      configApi.saveSecurityConfig.mockResolvedValue(data)

      await configStore.saveSecurity(data)

      expect(configApi.saveSecurityConfig).toHaveBeenCalledWith(data)
      expect(configStore.security.session_timeout).toBe(120)
      expect(configStore.security.login_attempts).toBe(10)
      expect(configStore.lastUpdate).toBeInstanceOf(Date)
      expect(globalThis.dispatchEvent).toHaveBeenCalled()
    })

    it('should handle save errors', async () => {
      const data = { session_timeout: 120 }
      const error = new Error('Save failed')

      configApi.saveSecurityConfig.mockRejectedValue(error)

      await expect(configStore.saveSecurity(data)).rejects.toThrow('Save failed')
    })
  })

  describe('saveML', () => {
    it('should save ML config successfully', async () => {
      const data = {
        active_model: 'yolov9',
        last_training: '2024-01-01'
      }

      configApi.saveMLConfig.mockResolvedValue(data)

      await configStore.saveML(data)

      expect(configApi.saveMLConfig).toHaveBeenCalledWith(data)
      expect(configStore.ml.active_model).toBe('yolov9')
      expect(configStore.ml.last_training).toBe('2024-01-01')
      expect(configStore.lastUpdate).toBeInstanceOf(Date)
      expect(globalThis.dispatchEvent).toHaveBeenCalled()
    })

    it('should handle save errors', async () => {
      const data = { active_model: 'yolov9' }
      const error = new Error('Save failed')

      configApi.saveMLConfig.mockRejectedValue(error)

      await expect(configStore.saveML(data)).rejects.toThrow('Save failed')
    })
  })

  describe('updateGeneral', () => {
    it('should update general config locally', () => {
      const data = {
        nombre_sistema: 'Updated Name'
      }

      configStore.updateGeneral(data)

      expect(configStore.general.nombre_sistema).toBe('Updated Name')
      expect(configStore.general.email_contacto).toBe('contacto@cacaoscan.com')
    })
  })

  describe('updateSecurity', () => {
    it('should update security config locally', () => {
      const data = {
        session_timeout: 90
      }

      configStore.updateSecurity(data)

      expect(configStore.security.session_timeout).toBe(90)
      expect(configStore.security.login_attempts).toBe(5)
    })
  })

  describe('updateML', () => {
    it('should update ML config locally', () => {
      const data = {
        active_model: 'yolov10'
      }

      configStore.updateML(data)

      expect(configStore.ml.active_model).toBe('yolov10')
    })
  })

  describe('reset', () => {
    it('should reset all configs to defaults', () => {
      configStore.general.nombre_sistema = 'Custom'
      configStore.security.session_timeout = 90
      configStore.ml.active_model = 'custom'

      configStore.reset()

      expect(configStore.general.nombre_sistema).toBe('CacaoScan')
      expect(configStore.security.session_timeout).toBe(60)
      expect(configStore.ml.active_model).toBe('yolov8')
    })
  })

  describe('loadAll with analyst user', () => {
    it('should load all configs for analyst user', async () => {
      mockAuthStore.isAdmin = false
      mockAuthStore.isAnalyst = true

      configApi.getSystemConfig.mockResolvedValue({
        version: '1.0.0'
      })
      configApi.getGeneralConfig.mockResolvedValue({
        nombre_sistema: 'Analyst Name'
      })
      configApi.getSecurityConfig.mockResolvedValue({})
      configApi.getMLConfig.mockResolvedValue({})

      await configStore.loadAll()

      expect(configApi.getGeneralConfig).toHaveBeenCalled()
      expect(configApi.getSecurityConfig).toHaveBeenCalled()
      expect(configApi.getMLConfig).toHaveBeenCalled()
    })
  })
})

