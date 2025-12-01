import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import EditFarmerModal from '../EditFarmerModal.vue'
import {
  createMockAuthApi,
  createMockPersonasApi,
  createMockFincasApi,
  createMockUseCatalogos,
  createMockUseFormValidation,
  createMockUseBirthdateRange,
  createMockUseModal
} from '@/test/mocks'

const mockAuthApi = createMockAuthApi()
const mockPersonasApi = createMockPersonasApi()
const mockFincasApi = createMockFincasApi()
const mockUseCatalogos = createMockUseCatalogos()
const mockUseFormValidation = createMockUseFormValidation()
const mockUseBirthdateRange = createMockUseBirthdateRange()
const mockUseModal = createMockUseModal()

vi.mock('@/services/authApi', () => ({
  default: mockAuthApi
}))

vi.mock('@/services', () => ({
  personasApi: mockPersonasApi
}))

vi.mock('@/services/fincasApi', () => ({
  getFincas: mockFincasApi.getFincas,
  createFinca: mockFincasApi.createFinca
}))

vi.mock('@/composables/useCatalogos', () => ({
  useCatalogos: () => mockUseCatalogos
}))

vi.mock('@/composables/useFormValidation', () => ({
  useFormValidation: () => mockUseFormValidation
}))

vi.mock('@/composables/useBirthdateRange', () => ({
  useBirthdateRange: () => mockUseBirthdateRange
}))

vi.mock('@/composables/useModal', () => ({
  useModal: () => mockUseModal
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue({ isConfirmed: true })
  }
}))

describe('EditFarmerModal', () => {
  let wrapper

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
    mockPersonasApi.getPersonaByUserId.mockResolvedValue({
      primer_nombre: 'Juan',
      primer_apellido: 'Pérez',
      tipo_documento_info: { codigo: 'CC' },
      numero_documento: '1234567890'
    })

    mockFincasApi.getFincas.mockResolvedValue({
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

    expect(mockPersonasApi.getPersonaByUserId).toHaveBeenCalledWith(1)
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
    mockAuthApi.updateUser.mockResolvedValue({
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

    expect(mockAuthApi.updateUser).toHaveBeenCalled()
  })

  it('should create finca', async () => {
    mockFincasApi.createFinca.mockResolvedValue({
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

    expect(mockFincasApi.createFinca).toHaveBeenCalled()
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

    expect(mockFincasApi.createFinca).not.toHaveBeenCalled()
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
    mockFincasApi.getFincas.mockResolvedValue({
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

    expect(mockFincasApi.getFincas).toHaveBeenCalled()
  })
})

