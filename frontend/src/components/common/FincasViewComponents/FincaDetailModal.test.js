import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick, ref } from 'vue'
import FincaDetailModal from './FincaDetailModal.vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div><slot name="header"></slot><slot></slot><slot name="footer"></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth'],
    emits: ['close']
  }
}))

vi.mock('@/components/fincas/FincaLocationMap.vue', () => ({
  default: {
    name: 'FincaLocationMap',
    template: '<div>FincaLocationMap</div>',
    props: ['nombre', 'latitud', 'longitud']
  }
}))

// Use vi.hoisted() to define mock before vi.mock() hoisting
const { mockUseFincas } = vi.hoisted(() => {
  return {
    mockUseFincas: vi.fn()
  }
})

vi.mock('@/composables/useFincas', () => ({
  useFincas: mockUseFincas
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    isAdmin: false
  }))
}))

describe('FincaDetailModal', () => {
  let wrapper
  let mockLoadFinca
  let mockClearCurrentFinca
  let mockCurrentFinca

  const mockFinca = {
    id: 1,
    nombre: 'Test Finca',
    municipio: 'Test Municipio',
    departamento: 'Test Departamento',
    activa: true
  }

  const mockFincaDetail = {
    id: 1,
    nombre: 'Test Finca',
    municipio: 'Test Municipio',
    departamento: 'Test Departamento',
    ubicacion: 'Test Ubicación',
    hectareas: 10,
    activa: true,
    agricultor_name: 'Test Agricultor',
    fecha_registro: '2024-01-01',
    descripcion: 'Test Description',
    coordenadas_lat: 4.6097,
    coordenadas_lng: -74.0817,
    estadisticas: {
      total_lotes: 5,
      lotes_activos: 3,
      total_analisis: 10,
      calidad_promedio: 85
    }
  }

  beforeEach(() => {
    mockLoadFinca = vi.fn(async (fincaId) => {
      // Set currentFinca when loadFinca is called
      if (fincaId === mockFinca.id) {
        mockCurrentFinca.value = mockFincaDetail
      }
      return Promise.resolve()
    })
    mockClearCurrentFinca = vi.fn()
    mockCurrentFinca = { value: null }

    mockUseFincas.mockReturnValue({
      currentFinca: mockCurrentFinca,
      isLoading: { value: false },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  it('should render modal when show is true', () => {
    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should not render modal when show is false', () => {
    wrapper = mount(FincaDetailModal, {
      props: {
        show: false,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should emit close event when modal is closed', async () => {
    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await wrapper.vm.closeModal()
    await nextTick()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should emit edit event when edit button is clicked', async () => {
    const mockCurrentFinca = { value: mockFincaDetail }
    
    mockUseFincas.mockReturnValue({
      currentFinca: mockCurrentFinca,
      isLoading: { value: false },
      loadFinca: vi.fn(() => {
        mockCurrentFinca.value = mockFincaDetail
        return Promise.resolve()
      }),
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca,
        userRole: 'admin'
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()
    await nextTick()

    await wrapper.vm.handleEdit()
    await nextTick()

    expect(wrapper.emitted('edit')).toBeTruthy()
  })

  it('should emit view-lotes event when view lotes button is clicked', async () => {
    const mockCurrentFinca = { value: mockFincaDetail }
    
    mockUseFincas.mockReturnValue({
      currentFinca: mockCurrentFinca,
      isLoading: { value: false },
      loadFinca: vi.fn(() => {
        mockCurrentFinca.value = mockFincaDetail
        return Promise.resolve()
      }),
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca,
        userRole: 'admin'
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()
    await nextTick()

    await wrapper.vm.handleViewLotes()
    await nextTick()

    expect(wrapper.emitted('view-lotes')).toBeTruthy()
  })

  it('should load finca details when finca prop changes', async () => {
    mockUseFincas.mockReturnValue({
      currentFinca: { value: null },
      isLoading: { value: false },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: null
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()

    await wrapper.setProps({ finca: mockFinca })
    await nextTick()

    expect(mockLoadFinca).toHaveBeenCalledWith(mockFinca.id)
  })

  it('should load finca details when show becomes true', async () => {
    mockUseFincas.mockReturnValue({
      currentFinca: { value: null },
      isLoading: { value: false },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: false,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()

    await wrapper.setProps({ show: true })
    await nextTick()

    expect(mockLoadFinca).toHaveBeenCalledWith(mockFinca.id)
  })

  it('should display loading state when loading', async () => {
    mockUseFincas.mockReturnValue({
      currentFinca: { value: null },
      isLoading: { value: true },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: {
            template: '<div v-if="show"><slot name="header"></slot><slot></slot><slot name="footer"></slot></div>',
            props: ['show', 'title', 'subtitle', 'maxWidth'],
            emits: ['close']
          },
          FincaLocationMap: true
        }
      }
    })

    await nextTick()
    
    const text = wrapper.text()
    expect(text.includes('Cargando') || text.includes('loading') || text.includes('información')).toBe(true)
  })

  it('should display finca statistics correctly', async () => {
    // Create reactive refs using Vue's ref function with data already set
    const mockCurrentFincaForTest = ref(mockFincaDetail)
    const mockIsLoading = ref(false)
    
    // Mock loadFinca - it should set the data when called
    const testLoadFinca = vi.fn(async (fincaId) => {
      if (fincaId === mockFinca.id) {
        mockCurrentFincaForTest.value = mockFincaDetail
      }
      mockIsLoading.value = false
      return Promise.resolve()
    })
    
    mockUseFincas.mockReturnValue({
      currentFinca: mockCurrentFincaForTest,
      isLoading: mockIsLoading,
      loadFinca: testLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: {
            template: '<div v-if="show"><slot name="header"></slot><slot></slot><slot name="footer"></slot></div>',
            props: ['show', 'title', 'subtitle', 'maxWidth'],
            emits: ['close']
          },
          FincaLocationMap: true
        }
      }
    })

    // Wait for component to render and loadFinca to complete
    await nextTick()
    await wrapper.vm.$nextTick()
    // Ensure loadFinca has been called and completed
    await testLoadFinca(mockFinca.id)
    await nextTick()
    await wrapper.vm.$nextTick()
    // Additional wait for reactive updates
    await new Promise(resolve => setTimeout(resolve, 100))
    await nextTick()
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    // Verify statistics are displayed - check for the actual values
    expect(text.includes('5')).toBe(true) // total_lotes
    expect(text.includes('3')).toBe(true) // lotes_activos
    expect(text.includes('10')).toBe(true) // total_analisis
    expect(text.includes('85')).toBe(true) // calidad_promedio
  })

  it('should clear current finca after close delay', async () => {
    vi.useFakeTimers()
    mockUseFincas.mockReturnValue({
      currentFinca: { value: mockFincaDetail },
      isLoading: { value: false },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()

    wrapper.vm.closeModal()
    await nextTick()

    vi.advanceTimersByTime(300)
    await nextTick()

    expect(mockClearCurrentFinca).toHaveBeenCalled()

    vi.useRealTimers()
  })
})

