import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import EditFarmerModal from '../EditFarmerModal.vue'
import { getFincas, createFinca } from '@/services/fincasApi'

vi.mock('@/services/authApi', () => ({
  default: {
    updateUser: vi.fn()
  }
}))

vi.mock('@/services', () => ({
  personasApi: {
    getPersonaByUserId: vi.fn().mockResolvedValue({ primer_nombre: '', primer_apellido: '', tipo_documento_info: { codigo: 'CC' }, numero_documento: '' }),
    updatePersonaByUserId: vi.fn()
  }
}))

vi.mock('@/services/fincasApi', () => ({
  createFinca: vi.fn(),
  getFincas: vi.fn().mockResolvedValue({ results: [] })
}))

vi.mock('@/composables/useCatalogos', () => ({
  useCatalogos: () => ({
    tiposDocumento: { value: [{ codigo: 'CC', nombre: 'Cédula' }] },
    generos: { value: [{ codigo: 'M', nombre: 'Masculino' }] },
    departamentos: { value: [{ id: 1, nombre: 'Antioquia' }] },
    municipios: { value: [{ id: 1, nombre: 'Medellín' }] },
    isLoadingCatalogos: { value: false },
    cargarCatalogos: vi.fn(),
    cargarMunicipios: vi.fn(),
    limpiarMunicipios: vi.fn()
  })
}))

vi.mock('@/composables/useFormValidation', () => ({
  useFormValidation: () => ({
    errors: {},
    isValidEmail: (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
    isValidPhone: (phone) => /^\d{7,15}$/.test(phone),
    isValidDocument: (doc) => /^\d{6,11}$/.test(doc),
    clearErrors: vi.fn()
  })
}))

vi.mock('@/composables/useBirthdateRange', () => ({
  useBirthdateRange: () => ({
    maxBirthdate: '2010-01-01',
    minBirthdate: '1950-01-01'
  })
}))

vi.mock('@/composables/useModal', () => ({
  useModal: () => ({
    modalContainer: { value: null },
    openModal: vi.fn(),
    closeModal: vi.fn()
  })
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue({ isConfirmed: true })
  }
}))

describe('EditFarmerModal', () => {
  let wrapper
  let authApi
  let personasApi

  const mockFarmer = {
    id: 1,
    name: 'Juan Pérez',
    email: 'juan@example.com',
    phone_number: '1234567890',
    region: 'Antioquia',
    municipality: 'Medellín'
  }

  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    authApi = (await import('@/services/authApi')).default
    personasApi = (await import('@/services')).personasApi
  })

  it('should render modal', () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        farmer: mockFarmer
      },
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const modal = wrapper.find('#edit-farmer-modal')
    expect(modal.exists()).toBe(true)
  })

  it('should load farmer data when prop changes', async () => {
    personasApi.getPersonaByUserId.mockResolvedValue({
      primer_nombre: 'Juan',
      primer_apellido: 'Pérez',
      tipo_documento_info: { codigo: 'CC' },
      numero_documento: '1234567890'
    })

    getFincas.mockResolvedValue({
      results: []
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        farmer: mockFarmer
      },
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(personasApi.getPersonaByUserId).toHaveBeenCalledWith(1)
  })

  it('should switch between tabs', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        farmer: mockFarmer
      },
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    expect(wrapper.vm.activeTab).toBe('info')

    // Switch to fincas tab by setting activeTab directly
    wrapper.vm.activeTab = 'fincas'
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.activeTab).toBe('fincas')
  })

  it('should update farmer data', async () => {
    authApi.updateUser.mockResolvedValue({
      user: { id: 1, ...mockFarmer }
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        farmer: mockFarmer
      },
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.formData.first_name = 'Juan Updated'
    wrapper.vm.formData.last_name = 'Pérez Updated'
    wrapper.vm.formData.email = 'updated@example.com'

    await wrapper.vm.handleUpdate()
    await wrapper.vm.$nextTick()

    expect(authApi.updateUser).toHaveBeenCalled()
  })

  it('should create finca', async () => {
    createFinca.mockResolvedValue({
      id: 1,
      nombre: 'Nueva Finca'
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        farmer: mockFarmer
      },
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.newFinca.nombre = 'Nueva Finca'
    wrapper.vm.newFinca.municipio = 'Medellín'
    wrapper.vm.newFinca.departamento = 'Antioquia'
    wrapper.vm.newFinca.hectareas = 10.5

    await wrapper.vm.handleCreateFinca()
    await wrapper.vm.$nextTick()

    expect(createFinca).toHaveBeenCalled()
  })

  it('should validate finca creation', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        farmer: mockFarmer
      },
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.newFinca.nombre = ''
    wrapper.vm.newFinca.municipio = ''
    wrapper.vm.newFinca.departamento = ''
    wrapper.vm.newFinca.hectareas = ''

    await wrapper.vm.handleCreateFinca()
    await wrapper.vm.$nextTick()

    expect(createFinca).not.toHaveBeenCalled()
  })

  it('should close modal', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        farmer: mockFarmer
      },
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.closeModal()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should load fincas for farmer', async () => {
    getFincas.mockResolvedValue({
      results: [
        { id: 1, nombre: 'Finca 1' },
        { id: 2, nombre: 'Finca 2' }
      ]
    })

    wrapper = mount(EditFarmerModal, {
      props: {
        farmer: mockFarmer
      },
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(getFincas).toHaveBeenCalled()
  })
})

