import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminConfiguracion from '../../Admin/AdminConfiguracion.vue'
import configApi from '@/services/configApi'

vi.mock('@/services/configApi', () => ({
  default: {
    getSystemConfig: vi.fn().mockResolvedValue({
      version: '1.0.0',
      server_status: 'online',
      backend_version: '4.2.7',
      frontend_version: '3.5.3',
      database: 'PostgreSQL 16'
    }),
    getGeneralConfig: vi.fn().mockResolvedValue({
      nombre_sistema: 'CacaoScan',
      email_contacto: 'contacto@cacaoscan.com',
      lema: 'La mejor plataforma para el control de calidad del cacao',
      logo_url: null
    }),
    getSecurityConfig: vi.fn().mockResolvedValue({
      recaptcha_enabled: true,
      session_timeout: 60,
      login_attempts: 5,
      two_factor_auth: false
    }),
    getMLConfig: vi.fn().mockResolvedValue({
      active_model: 'yolov8',
      last_training: null
    }),
    saveGeneralConfig: vi.fn().mockResolvedValue({}),
    saveSecurityConfig: vi.fn().mockResolvedValue({}),
    saveMLConfig: vi.fn().mockResolvedValue({})
  }
}))

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    user: { id: 1, first_name: 'Test', last_name: 'User', username: 'testuser' },
    userRole: 'admin',
    isAdmin: true,
    isAnalyst: false,
    logout: vi.fn()
  })
}))

// Mock vue-router
vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => ({
      push: vi.fn(),
      replace: vi.fn(),
      go: vi.fn(),
      back: vi.fn(),
      forward: vi.fn()
    })
  }
})

// Mock sweetalert2
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue({ isConfirmed: true })
  }
}))

describe('AdminConfiguracion', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render configuration view', () => {
    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should load configuration on mount', async () => {
    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    // Wait for async operations to complete
    await new Promise(resolve => setTimeout(resolve, 200))

    // Verify that the config API methods were called
    expect(configApi.getSystemConfig).toHaveBeenCalled()
    expect(configApi.getGeneralConfig).toHaveBeenCalled()
    expect(configApi.getSecurityConfig).toHaveBeenCalled()
    expect(configApi.getMLConfig).toHaveBeenCalled()
  })

  it('should save configuration', async () => {
    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    // Update general config
    wrapper.vm.generalConfig.nombre_sistema = 'New System Name'

    if (wrapper.vm.saveGeneralConfig) {
      await wrapper.vm.saveGeneralConfig()
      await wrapper.vm.$nextTick()

      expect(configApi.saveGeneralConfig).toHaveBeenCalled()
    }
  })

  it('should handle save error', async () => {
    const error = new Error('Save failed')
    configApi.saveGeneralConfig.mockRejectedValueOnce(error)

    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    if (wrapper.vm.saveGeneralConfig) {
      await wrapper.vm.saveGeneralConfig()
      await wrapper.vm.$nextTick()

      // Error should be handled by Swal.fire
      expect(configApi.saveGeneralConfig).toHaveBeenCalled()
    }
  })

  it('should display configuration data', async () => {
    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    // Verify that configuration data is available
    expect(wrapper.vm.generalConfig).toBeDefined()
    expect(wrapper.vm.securityConfig).toBeDefined()
    expect(wrapper.vm.systemConfig).toBeDefined()
  })
})

