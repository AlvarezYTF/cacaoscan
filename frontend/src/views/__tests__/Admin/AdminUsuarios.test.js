import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminUsuarios from '../../Admin/AdminUsuarios.vue'

// Mock stores
const mockAdminStore = {
  users: [],
  loading: false,
  error: null,
  getAllUsers: vi.fn(),
  getUserById: vi.fn(),
  updateUser: vi.fn(),
  deleteUser: vi.fn()
}

vi.mock('@/stores/admin', () => ({
  useAdminStore: () => mockAdminStore
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    user: { id: 1, first_name: 'Admin', last_name: 'User', username: 'admin' },
    isAdmin: true,
    userRole: 'admin'
  })
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => ({
      push: vi.fn(),
      replace: vi.fn()
    }),
    useRoute: () => ({
      path: '/admin/usuarios',
      query: {},
      params: {}
    })
  }
})

vi.mock('@/stores/config', () => ({
  useConfigStore: () => ({
    brandName: 'CacaoScan'
  })
}))

vi.mock('@/composables/useWebSocket', () => ({
  useWebSocket: () => ({
    connect: vi.fn(),
    disconnect: vi.fn(),
    send: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn()
  })
}))

vi.mock('@/composables/usePagination', () => ({
  usePagination: () => ({
    currentPage: { value: 1 },
    itemsPerPage: { value: 20 },
    totalPages: { value: 1 },
    goToPage: vi.fn(),
    updateFromApiResponse: vi.fn(),
    updatePagination: vi.fn()
  })
}))

vi.mock('@/services/authApi', () => ({
  default: {
    getUserStats: vi.fn().mockResolvedValue({
      total: 0,
      active: 0,
      online: 0,
      new_today: 0
    })
  }
}))

describe('AdminUsuarios', () => {
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

  it('should render usuarios view', () => {
    wrapper = mount(AdminUsuarios, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should load users on mount', async () => {
    mockAdminStore.getAllUsers.mockResolvedValue({
      data: {
        results: [
          { id: 1, email: 'user1@example.com' },
          { id: 2, email: 'user2@example.com' }
        ],
        count: 2,
        current_page: 1,
        total_pages: 1
      }
    })

    wrapper = mount(AdminUsuarios, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(mockAdminStore.getAllUsers).toHaveBeenCalled()
  })
})

