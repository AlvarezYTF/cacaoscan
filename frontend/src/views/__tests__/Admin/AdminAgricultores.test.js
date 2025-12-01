import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ref, computed } from 'vue'
import AdminAgricultores from '../../Admin/AdminAgricultores.vue'

// Mock usePagination composable
vi.mock('@/composables/usePagination', () => ({
  usePagination: () => {
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const totalItems = ref(0)
    const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value))

    return {
      currentPage,
      itemsPerPage,
      totalItems,
      totalPages,
      updatePagination: vi.fn((params) => {
        if (params.count !== undefined) {
          totalItems.value = params.count
        }
        if (params.page !== undefined) {
          currentPage.value = params.page
        }
        if (params.page_size !== undefined) {
          itemsPerPage.value = params.page_size
        }
      }),
      goToPage: vi.fn(),
      nextPage: vi.fn(),
      previousPage: vi.fn(),
      setItemsPerPage: vi.fn(),
      setTotalItems: vi.fn()
    }
  }
}))

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    user: { id: 1, first_name: 'Test', last_name: 'User', username: 'testuser' },
    userRole: 'admin',
    logout: vi.fn()
  })
}))

// Mock services
vi.mock('@/services/authApi', () => ({
  default: {
    getUsers: vi.fn().mockResolvedValue({ results: [] })
  }
}))

vi.mock('@/services/fincasApi', () => ({
  getFincas: vi.fn().mockResolvedValue({ results: [] })
}))

vi.mock('@/services/reportsApi', () => ({
  default: {
    downloadReporteAgricultores: vi.fn().mockResolvedValue({})
  }
}))

describe('AdminAgricultores', () => {
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

  it('should render agricultores view', () => {
    wrapper = mount(AdminAgricultores, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})

