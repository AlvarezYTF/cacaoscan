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
        ]
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
    expect(mockAdminStore.getAllUsers).toHaveBeenCalled()
  })
})

