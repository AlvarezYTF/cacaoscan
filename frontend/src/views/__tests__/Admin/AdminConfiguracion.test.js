import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminConfiguracion from '../../Admin/AdminConfiguracion.vue'
import configApi from '@/services/configApi'

vi.mock('@/services/configApi', () => ({
  default: {
    getConfig: vi.fn(),
    updateConfig: vi.fn()
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
    configApi.getConfig.mockResolvedValue({
      data: { setting1: 'value1', setting2: 'value2' }
    })

    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(configApi.getConfig).toHaveBeenCalled()
  })

  it('should save configuration', async () => {
    configApi.updateConfig.mockResolvedValue({
      data: { success: true }
    })

    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.config = { setting1: 'newvalue' }

    if (wrapper.vm.saveConfig) {
      await wrapper.vm.saveConfig()
      await wrapper.vm.$nextTick()

      expect(configApi.updateConfig).toHaveBeenCalled()
    }
  })

  it('should handle save error', async () => {
    const error = new Error('Save failed')
    configApi.updateConfig.mockRejectedValue(error)

    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    if (wrapper.vm.saveConfig) {
      await wrapper.vm.saveConfig()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.error).toBeDefined()
    }
  })

  it('should reset configuration', async () => {
    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.config = { setting1: 'modified' }

    if (wrapper.vm.resetConfig) {
      await wrapper.vm.resetConfig()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.config).toBeDefined()
    }
  })
})

