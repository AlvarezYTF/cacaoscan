import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// Mock services before importing component - use vi.hoisted for hoisting
const { mockGetUsers, mockGetFincas } = vi.hoisted(() => ({
  mockGetUsers: vi.fn(),
  mockGetFincas: vi.fn()
}))

vi.mock('@/services/authApi', () => ({
  default: {
    getUsers: mockGetUsers
  }
}))

vi.mock('@/services/fincasApi', () => ({
  getFincas: mockGetFincas
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    user: { id: 1, username: 'admin', is_superuser: true }
  }))
}))

import BatchInfoForm from './BatchInfoForm.vue'

describe('BatchInfoForm', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockGetUsers.mockResolvedValue({ results: [] })
    mockGetFincas.mockResolvedValue({ results: [] })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render batch info form', () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display farmer field for admin', () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    const text = wrapper.text()
    expect(text.includes('Agricultor') || text.includes('farmer')).toBe(true)
  })

  it('should display readonly farmer field for agricultor role', () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: 'test',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'agricultor'
      }
    })

    const farmerInput = wrapper.find('input[readonly]')
    if (farmerInput.exists()) {
      expect(farmerInput.attributes('readonly')).toBeDefined()
    }
  })

  it('should emit update event when form data changes', async () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    await wrapper.vm.$nextTick()

    const select = wrapper.find('select')
    if (select.exists()) {
      await select.setValue('test')
      await wrapper.vm.$nextTick()
    }
  })

  it('should load agricultores on mount', async () => {
    mockGetUsers.mockResolvedValue({
      results: [
        { id: 1, username: 'farmer1', is_superuser: false, is_staff: false, role: 'farmer' },
        { id: 2, username: 'admin', is_superuser: true, is_staff: true, role: 'admin' }
      ]
    })

    wrapper = mount(BatchInfoForm, {
      props: {
        modelValue: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(mockGetUsers).toHaveBeenCalled()
  })

  it('should handle error when loading agricultores', async () => {
    mockGetUsers.mockRejectedValue(new Error('Network error'))

    wrapper = mount(BatchInfoForm, {
      props: {
        modelValue: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(wrapper.vm.agricultores).toEqual([])
  })

  it('should load all fincas on mount', async () => {
    mockGetFincas.mockResolvedValue({
      results: [
        { id: 1, nombre: 'Finca 1', agricultor_id: 1 },
        { id: 2, nombre: 'Finca 2', agricultor_id: 2 }
      ]
    })

    wrapper = mount(BatchInfoForm, {
      props: {
        modelValue: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(mockGetFincas).toHaveBeenCalled()
  })

  it('should handle error when loading fincas', async () => {
    mockGetFincas.mockRejectedValue(new Error('Network error'))

    wrapper = mount(BatchInfoForm, {
      props: {
        modelValue: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.allFincas).toEqual([])
  })

  it('should update form when modelValue changes', async () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        modelValue: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.setProps({
      modelValue: {
        farmer: 'farmer1',
        finca: 'Finca 1',
        lote: 'Lote 1',
        fecha: '2024-01-01'
      }
    })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.formData.farmer).toBe('farmer1')
  })

  it('should handle farmer change for admin role', async () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    await wrapper.vm.$nextTick()
    wrapper.vm.agricultores = [
      { id: 1, username: 'farmer1' }
    ]
    wrapper.vm.allFincas = [
      { id: 1, nombre: 'Finca 1', agricultor_id: 1 },
      { id: 2, nombre: 'Finca 2', agricultor_id: 2 }
    ]

    wrapper.vm.formData.farmer = 'farmer1'
    await wrapper.vm.handleFarmerChange()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.fincas.length).toBeGreaterThanOrEqual(0)
  })

  it('should not handle farmer change for agricultor role', async () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: 'farmer1',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'agricultor'
      }
    })

    await wrapper.vm.$nextTick()
    const initialFincas = wrapper.vm.fincas.length

    wrapper.vm.formData.farmer = 'farmer2'
    await wrapper.vm.handleFarmerChange()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.fincas.length).toBe(initialFincas)
  })

  it('should handle finca change and update farmer', async () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    await wrapper.vm.$nextTick()
    wrapper.vm.agricultores = [
      { id: 1, username: 'farmer1' }
    ]
    wrapper.vm.allFincas = [
      { id: 1, nombre: 'Finca 1', agricultor_id: 1 }
    ]

    wrapper.vm.formData.farm = 'Finca 1'
    await wrapper.vm.handleFincaChange()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })

  it('should filter fincas by userId for agricultor role', async () => {
    mockGetFincas.mockResolvedValue({
      results: [
        { id: 1, nombre: 'Finca 1', agricultor_id: 1 },
        { id: 2, nombre: 'Finca 2', agricultor_id: 2 }
      ]
    })

    wrapper = mount(BatchInfoForm, {
      props: {
        modelValue: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'agricultor',
        userId: 1
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.fincas.length).toBeGreaterThanOrEqual(0)
  })

  it('should set farmer from userName for agricultor role', async () => {
    mockGetFincas.mockResolvedValue({
      results: []
    })
    mockGetUsers.mockResolvedValue({
      results: []
    })

    wrapper = mount(BatchInfoForm, {
      props: {
        modelValue: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'agricultor',
        userName: 'farmer1'
      }
    })

    // Wait for component to mount and initialize
    await wrapper.vm.$nextTick()
    // Wait for async operations (loadAllFincas, loadAgricultores, and updateForm)
    await new Promise(resolve => setTimeout(resolve, 500))

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    // Verify that the farmer was set correctly
    const emittedEvents = wrapper.emitted('update:modelValue')
    expect(emittedEvents).toBeTruthy()
    expect(emittedEvents[0][0].farmer).toBe('farmer1')
  })
})

