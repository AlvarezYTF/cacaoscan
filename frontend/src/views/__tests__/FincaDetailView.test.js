import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ref } from 'vue'
import FincaDetailView from '../FincaDetailView.vue'

globalThis.fetch = vi.fn()

// Create refs for useFincas mock
const mockFincaRef = ref(null)
const mockLoadingRef = ref(true)
const mockErrorRef = ref(null)

// Mock vue-router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn()
}

const mockRoute = {
  path: '/fincas/1',
  name: 'finca-detail',
  params: { id: '1' },
  query: {},
  meta: {}
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter,
    useRoute: () => mockRoute
  }
})

// Mock useFincas composable
vi.mock('@/composables/useFincas', () => ({
  useFincas: () => ({
    loading: mockLoadingRef,
    error: mockErrorRef,
    finca: mockFincaRef,
    currentFinca: mockFincaRef, // Also provide as alias
    loadFinca: vi.fn().mockResolvedValue({}),
    canEdit: vi.fn(() => false)
  })
}))

// Mock useDateFormatting composable
vi.mock('@/composables/useDateFormatting', () => ({
  useDateFormatting: () => ({
    formatDate: vi.fn((date) => date ? new Date(date).toLocaleDateString() : 'N/A')
  })
}))

// Mock sweetalert2
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue({ isConfirmed: true })
  }
}))

// Mock components
vi.mock('@/components/common/BaseDetailView.vue', () => ({
  default: {
    name: 'BaseDetailView',
    template: `
      <div>
        <div v-if="loading" class="text-center py-5">
          <div class="spinner"></div>
          <p>{{ loadingText || 'Cargando información...' }}</p>
        </div>
        <div v-else-if="error" class="alert alert-danger">
          <p>{{ error }}</p>
        </div>
        <div v-else>
          <slot name="main"></slot>
          <slot name="actions"></slot>
          <slot name="sidebar"></slot>
        </div>
      </div>
    `,
    props: ['loading', 'error', 'title', 'subtitle', 'icon', 'breadcrumbs', 'showEditButton', 'canEdit', 'statusBadge', 'statistics', 'loadingText'],
    emits: ['edit', 'retry']
  }
}))

vi.mock('@/components/fincas/FincaLocationMap.vue', () => ({
  default: {
    name: 'FincaLocationMap',
    template: '<div class="finca-location-map"></div>',
    props: ['nombre', 'latitud', 'longitud']
  }
}))

describe('FincaDetailView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    // Reset refs
    mockFincaRef.value = null
    mockLoadingRef.value = true
    mockErrorRef.value = null
  })

  it('should render loading state initially', () => {
    const wrapper = mount(FincaDetailView, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.text().includes('Cargando') || wrapper.find('.spinner').exists()).toBe(true)
  })
})

