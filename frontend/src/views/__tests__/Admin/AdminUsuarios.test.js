import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick, ref } from 'vue'
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

const mockAuthStore = {
  user: { id: 1, first_name: 'Admin', last_name: 'User', username: 'admin' },
  isAdmin: true,
  userRole: 'admin',
  logout: vi.fn()
}

const mockRouter = {
  push: vi.fn(),
  replace: vi.fn()
}

const mockWebSocket = {
  connect: vi.fn(),
  disconnect: vi.fn(),
  send: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  emit: vi.fn()
}

const mockPagination = {
  currentPage: ref(1),
  itemsPerPage: ref(20),
  totalPages: ref(1),
  goToPage: vi.fn(),
  updateFromApiResponse: vi.fn((responseData) => {
    if (responseData) {
      if (responseData.page !== undefined || responseData.currentPage !== undefined) {
        mockPagination.currentPage.value = responseData.page || responseData.currentPage || 1
      }
      if (responseData.total_pages !== undefined || responseData.totalPages !== undefined) {
        mockPagination.totalPages.value = responseData.total_pages || responseData.totalPages || 1
      }
      if (responseData.count !== undefined) {
        // Update totalPages based on count if not provided directly
        if (responseData.total_pages === undefined && responseData.totalPages === undefined) {
          const itemsPerPage = responseData.page_size || mockPagination.itemsPerPage.value
          mockPagination.totalPages.value = Math.ceil(responseData.count / itemsPerPage)
        }
      }
    }
  }),
  updatePagination: vi.fn()
}

vi.mock('@/stores/admin', () => ({
  useAdminStore: () => mockAdminStore
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter,
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
  useWebSocket: () => mockWebSocket
}))

vi.mock('@/composables/usePagination', () => ({
  usePagination: () => mockPagination
}))

vi.mock('@/services/authApi', () => ({
  default: {
    getUserStats: vi.fn().mockResolvedValue({
      total: 10,
      active: 8,
      online: 5,
      new_today: 2
    }),
    toggleUserStatus: vi.fn().mockResolvedValue({})
  }
}))

vi.mock('@/services/reportsApi', () => ({
  default: {
    downloadReporteUsuarios: vi.fn().mockResolvedValue({})
  }
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue({ isConfirmed: false })
  }
}))

describe('AdminUsuarios', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockPagination.currentPage.value = 1
    mockPagination.totalPages.value = 1
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('rendering', () => {
    it('should render usuarios view', () => {
      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should redirect non-admin users', async () => {
      mockAuthStore.isAdmin = false
      mockAuthStore.userRole = 'farmer'

      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true
          }
        }
      })

      await nextTick()
      expect(mockRouter.push).toHaveBeenCalledWith('/acceso-denegado')
    })
  })

  describe('data loading', () => {
    it('should load users on mount', async () => {
      // Ensure isAdmin is true so the component doesn't redirect
      mockAuthStore.isAdmin = true
      
      mockAdminStore.getAllUsers.mockResolvedValue({
        data: {
          results: [
            { id: 1, email: 'user1@example.com', first_name: 'User', last_name: 'One' },
            { id: 2, email: 'user2@example.com', first_name: 'User', last_name: 'Two' }
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
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()
      await nextTick()

      expect(mockAdminStore.getAllUsers).toHaveBeenCalled()
    })

    it('should load user stats on mount', async () => {
      // Import the mocked authApi module
      const authApiModule = await import('@/services/authApi')
      
      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()
      // Give additional time for onMounted to complete
      await new Promise(resolve => setTimeout(resolve, 100))

      // Check that getUserStats was called on the mocked authApi
      expect(authApiModule.default.getUserStats).toHaveBeenCalled()
    })

    it('should handle error loading users', async () => {
      mockAuthStore.isAdmin = true
      mockAuthStore.userRole = 'admin'
      const error = { code: 'ERR_NETWORK', message: 'Network Error' }
      mockAdminStore.getAllUsers.mockRejectedValue(error)

      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()

      expect(mockAdminStore.getAllUsers).toHaveBeenCalled()
    })

    it('should handle error loading user stats', async () => {
      const authApi = await import('@/services/authApi')
      authApi.default.getUserStats.mockRejectedValueOnce(new Error('Stats error'))

      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()
    })
  })

  describe('user management', () => {
    beforeEach(async () => {
      mockAdminStore.getAllUsers.mockResolvedValue({
        data: {
          results: [
            { id: 1, email: 'user1@example.com', first_name: 'User', last_name: 'One', is_active: true, is_superuser: false }
          ],
          count: 1,
          current_page: 1,
          total_pages: 1
        }
      })

      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()
    })

    it('should open create modal', async () => {
      await wrapper.vm.openCreateModal()
      expect(wrapper.vm.showUserModal).toBe(true)
      expect(wrapper.vm.modalMode).toBe('create')
      expect(wrapper.vm.editingUser).toBe(null)
    })

    it('should open edit modal', async () => {
      const user = { id: 1, email: 'user@example.com' }
      await wrapper.vm.editUser(user)
      expect(wrapper.vm.showUserModal).toBe(true)
      expect(wrapper.vm.modalMode).toBe('edit')
      expect(wrapper.vm.editingUser).toStrictEqual(user)
    })

    it('should open view modal', async () => {
      const user = { id: 1, email: 'user@example.com' }
      await wrapper.vm.viewUser(user)
      expect(wrapper.vm.showDetailsModal).toBe(true)
      expect(wrapper.vm.viewingUser).toStrictEqual(user)
    })

    it('should open activity modal', async () => {
      const user = { id: 1, email: 'user@example.com' }
      await wrapper.vm.viewUserActivity(user)
      expect(wrapper.vm.showActivityModal).toBe(true)
      expect(wrapper.vm.activityUser).toStrictEqual(user)
    })

    it('should close user modal', async () => {
      wrapper.vm.showUserModal = true
      wrapper.vm.editingUser = { id: 1 }
      await wrapper.vm.closeUserModal()
      expect(wrapper.vm.showUserModal).toBe(false)
      expect(wrapper.vm.editingUser).toBe(null)
    })

    it('should close details modal', async () => {
      wrapper.vm.showDetailsModal = true
      wrapper.vm.viewingUser = { id: 1 }
      await wrapper.vm.closeDetailsModal()
      expect(wrapper.vm.showDetailsModal).toBe(false)
      expect(wrapper.vm.viewingUser).toBe(null)
    })

    it('should close activity modal', async () => {
      wrapper.vm.showActivityModal = true
      wrapper.vm.activityUser = { id: 1 }
      await wrapper.vm.closeActivityModal()
      expect(wrapper.vm.showActivityModal).toBe(false)
      expect(wrapper.vm.activityUser).toBe(null)
    })

    it('should edit user from details', async () => {
      const user = { id: 1, email: 'user@example.com' }
      wrapper.vm.viewingUser = user
      wrapper.vm.showDetailsModal = true
      
      await wrapper.vm.editUserFromDetails(user)
      
      expect(wrapper.vm.showDetailsModal).toBe(false)
      expect(wrapper.vm.showUserModal).toBe(true)
      expect(wrapper.vm.editingUser).toStrictEqual(user)
    })

    it('should handle user saved', async () => {
      wrapper.vm.showUserModal = true
      mockAdminStore.getAllUsers.mockResolvedValueOnce({
        data: {
          results: [],
          count: 0,
          current_page: 1,
          total_pages: 1
        }
      })

      await wrapper.vm.handleUserSaved()
      
      expect(wrapper.vm.showUserModal).toBe(false)
      expect(mockAdminStore.getAllUsers).toHaveBeenCalled()
    })
  })

  describe('user deletion', () => {
    beforeEach(async () => {
      mockAdminStore.getAllUsers.mockResolvedValue({
        data: {
          results: [
            { id: 1, email: 'user1@example.com', first_name: 'User', last_name: 'One', is_superuser: false }
          ],
          count: 1,
          current_page: 1,
          total_pages: 1
        }
      })

      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()
    })

    it('should prevent deleting superuser', async () => {
      const Swal = await import('sweetalert2')
      const user = { id: 1, is_superuser: true, first_name: 'Super', last_name: 'User' }
      
      await wrapper.vm.confirmDeleteUser(user)
      
      expect(Swal.default.fire).toHaveBeenCalled()
      expect(mockAdminStore.deleteUser).not.toHaveBeenCalled()
    })

    it('should delete user when confirmed', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire.mockResolvedValueOnce({ isConfirmed: true })
      mockAdminStore.deleteUser.mockResolvedValueOnce({})

      const user = { id: 1, is_superuser: false, first_name: 'User', last_name: 'One' }
      wrapper.vm.users = [user]
      wrapper.vm.selectedUsers = [1]
      wrapper.vm.totalUsersCount = 1

      await wrapper.vm.confirmDeleteUser(user)
      
      expect(mockAdminStore.deleteUser).toHaveBeenCalledWith(1)
    })

    it('should handle delete error', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire.mockResolvedValueOnce({ isConfirmed: true })
      const error = new Error('Delete failed')
      mockAdminStore.deleteUser.mockRejectedValueOnce(error)

      const user = { id: 1, is_superuser: false, first_name: 'User', last_name: 'One' }
      
      await wrapper.vm.confirmDeleteUser(user)
      
      expect(Swal.default.fire).toHaveBeenCalledTimes(2)
    })
  })

  describe('bulk operations', () => {
    beforeEach(async () => {
      mockAdminStore.getAllUsers.mockResolvedValue({
        data: {
          results: [
            { id: 1, email: 'user1@example.com', is_active: false },
            { id: 2, email: 'user2@example.com', is_active: true }
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
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()
    })

    it('should bulk activate users', async () => {
      const Swal = await import('sweetalert2')
      wrapper.vm.selectedUsers = [1, 2]
      wrapper.vm.users = [
        { id: 1, is_active: false },
        { id: 2, is_active: false }
      ]
      mockAdminStore.updateUser.mockResolvedValue({})

      await wrapper.vm.bulkActivate()
      
      expect(mockAdminStore.updateUser).toHaveBeenCalledTimes(2)
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should bulk deactivate users', async () => {
      const Swal = await import('sweetalert2')
      wrapper.vm.selectedUsers = [1, 2]
      wrapper.vm.users = [
        { id: 1, is_active: true },
        { id: 2, is_active: true }
      ]
      mockAdminStore.updateUser.mockResolvedValue({})

      await wrapper.vm.bulkDeactivate()
      
      expect(mockAdminStore.updateUser).toHaveBeenCalledTimes(2)
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should bulk delete users', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire.mockResolvedValueOnce({ isConfirmed: true })
      wrapper.vm.selectedUsers = [1, 2]
      wrapper.vm.users = [
        { id: 1, is_active: false },
        { id: 2, is_active: false }
      ]
      wrapper.vm.totalUsersCount = 2
      mockAdminStore.deleteUser.mockResolvedValue({})

      await wrapper.vm.bulkDelete()
      
      expect(mockAdminStore.deleteUser).toHaveBeenCalledTimes(2)
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should handle bulk operation errors', async () => {
      const Swal = await import('sweetalert2')
      wrapper.vm.selectedUsers = [1]
      mockAdminStore.updateUser.mockRejectedValueOnce(new Error('Update failed'))

      await wrapper.vm.bulkActivate()
      
      expect(Swal.default.fire).toHaveBeenCalled()
    })
  })

  describe('user selection', () => {
    beforeEach(async () => {
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
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()
    })

    it('should toggle select all', async () => {
      // Ensure users are available for selection
      const mockUsers = [
        { id: 1, email: 'user1@example.com' },
        { id: 2, email: 'user2@example.com' }
      ]
      
      // Set users directly to ensure they're available
      wrapper.vm.users = mockUsers
      await nextTick()
      
      wrapper.vm.toggleSelectAll(true)
      expect(wrapper.vm.selectedUsers.length).toBe(2)
      expect(wrapper.vm.selectedUsers).toContain(1)
      expect(wrapper.vm.selectedUsers).toContain(2)

      wrapper.vm.toggleSelectAll(false)
      expect(wrapper.vm.selectedUsers.length).toBe(0)
    })

    it('should handle user select', () => {
      wrapper.vm.handleUserSelect(1)
      expect(wrapper.vm.selectedUsers).toContain(1)

      wrapper.vm.handleUserSelect(1)
      expect(wrapper.vm.selectedUsers).not.toContain(1)
    })
  })

  describe('filters and search', () => {
    beforeEach(async () => {
      mockAdminStore.getAllUsers.mockResolvedValue({
        data: {
          results: [],
          count: 0,
          current_page: 1,
          total_pages: 1
        }
      })

      // Reset pagination mock to default values
      mockPagination.currentPage.value = 1
      mockPagination.totalPages.value = 1

      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()
    })

    it('should apply filters', async () => {
      wrapper.vm.roleFilter = 'admin'
      wrapper.vm.applyFilters()
      
      await nextTick()
      expect(mockPagination.goToPage).toHaveBeenCalledWith(1)
    })

    it('should clear filters', async () => {
      wrapper.vm.searchQuery = 'test'
      wrapper.vm.roleFilter = 'admin'
      wrapper.vm.statusFilter = 'active'
      wrapper.vm.sortBy = 'name'
      
      wrapper.vm.clearFilters()
      
      expect(wrapper.vm.searchQuery).toBe('')
      expect(wrapper.vm.roleFilter).toBe('')
      expect(wrapper.vm.statusFilter).toBe('')
      expect(wrapper.vm.sortBy).toBe('-date_joined')
    })

    it('should change page', async () => {
      // Ensure getAllUsers is mocked to return a resolved promise with 5 total pages
      mockAdminStore.getAllUsers.mockResolvedValue({
        data: {
          results: [],
          count: 100, // Set count to ensure totalPages can be calculated
          current_page: 1,
          total_pages: 5
        }
      })
      
      // Reset totalPages to initial value
      mockPagination.totalPages.value = 1
      
      // Clear any previous calls
      mockPagination.goToPage.mockClear()
      mockPagination.updateFromApiResponse.mockClear()
      
      // Load users first to update pagination from API response
      await wrapper.vm.loadUsers()
      await nextTick()
      await flushPromises()
      await nextTick() // Extra tick to ensure computed updates
      
      // Verify totalPages computed is updated after loadUsers
      // The computed should reflect the updated mockPagination.totalPages.value
      expect(mockPagination.updateFromApiResponse).toHaveBeenCalledWith(
        expect.objectContaining({
          total_pages: 5
        })
      )
      expect(mockPagination.totalPages.value).toBe(5)
      // Force reactivity update
      await nextTick()
      expect(wrapper.vm.totalPages).toBe(5)
      
      // The component's changePage method checks: if (page >= 1 && page <= totalPages.value)
      // Since totalPages.value is 5, page 3 should pass the validation
      // and call pagination.goToPage(3)
      wrapper.vm.changePage(3)
      await nextTick()
      await flushPromises() // Wait for loadUsers() to complete
      
      // Verify goToPage was called with the correct page number
      expect(mockPagination.goToPage).toHaveBeenCalledWith(3)
    })

    it('should not change to invalid page', async () => {
      mockPagination.totalPages.value = 5
      await nextTick()
      
      wrapper.vm.changePage(0)
      expect(mockPagination.goToPage).not.toHaveBeenCalled()
      
      wrapper.vm.changePage(10)
      expect(mockPagination.goToPage).not.toHaveBeenCalled()
    })
  })

  describe('toggle status', () => {
    beforeEach(async () => {
      mockAdminStore.getAllUsers.mockResolvedValue({
        data: {
          results: [
            { id: 1, email: 'user1@example.com', is_active: true, isUpdating: false }
          ],
          count: 1,
          current_page: 1,
          total_pages: 1
        }
      })

      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()
    })

    it('should toggle user status', async () => {
      const Swal = await import('sweetalert2')
      const authApi = await import('@/services/authApi')
      
      // Wait for users to be loaded
      await nextTick()
      await flushPromises()
      
      // Ensure users array has at least one user
      expect(wrapper.vm.users.length).toBeGreaterThan(0)
      const user = wrapper.vm.users[0]
      expect(user).toBeDefined()

      await wrapper.vm.handleToggleStatus(user)
      
      expect(authApi.default.toggleUserStatus).toHaveBeenCalled()
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should handle toggle status error', async () => {
      const Swal = await import('sweetalert2')
      const authApi = await import('@/services/authApi')
      const error = { response: { data: { error: 'Toggle failed' } } }
      authApi.default.toggleUserStatus.mockRejectedValueOnce(error)
      
      // Wait for users to be loaded
      await nextTick()
      await flushPromises()
      
      // Ensure users array has at least one user
      expect(wrapper.vm.users.length).toBeGreaterThan(0)
      const user = wrapper.vm.users[0]
      expect(user).toBeDefined()
      
      // Ensure user has required properties
      if (!user.hasOwnProperty('isUpdating')) {
        user.isUpdating = false
      }

      await wrapper.vm.handleToggleStatus(user)
      
      expect(Swal.default.fire).toHaveBeenCalled()
      // Verify isUpdating is reset after error
      if (user) {
        expect(user.isUpdating).toBe(false)
      }
    })
  })

  describe('export', () => {
    beforeEach(async () => {
      mockAdminStore.getAllUsers.mockResolvedValue({
        data: {
          results: [],
          count: 0,
          current_page: 1,
          total_pages: 1
        }
      })

      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
      await flushPromises()
    })

    it('should export users', async () => {
      const Swal = await import('sweetalert2')
      const reportsApi = await import('@/services/reportsApi')

      await wrapper.vm.exportUsers()
      
      expect(reportsApi.default.downloadReporteUsuarios).toHaveBeenCalled()
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should handle export error', async () => {
      const Swal = await import('sweetalert2')
      const reportsApi = await import('@/services/reportsApi')
      reportsApi.default.downloadReporteUsuarios.mockRejectedValueOnce(new Error('Export failed'))

      await wrapper.vm.exportUsers()
      
      expect(Swal.default.fire).toHaveBeenCalled()
    })
  })

  describe('sidebar', () => {
    beforeEach(async () => {
      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      await nextTick()
    })

    it('should toggle sidebar collapse', () => {
      const initialValue = wrapper.vm.isSidebarCollapsed
      wrapper.vm.toggleSidebarCollapse()
      expect(wrapper.vm.isSidebarCollapsed).toBe(!initialValue)
    })

    it('should handle menu click', () => {
      wrapper.vm.handleMenuClick({ route: '/admin/dashboard' })
      expect(mockRouter.push).toHaveBeenCalledWith('/admin/dashboard')
    })

    it('should handle logout', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire.mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.handleLogout()
      
      expect(mockAuthStore.logout).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })
  })

  describe('websocket', () => {
    beforeEach(async () => {
      // Clear previous calls
      mockWebSocket.on.mockClear()
      
      mockAdminStore.getAllUsers.mockResolvedValue({
        data: {
          results: [],
          count: 0,
          current_page: 1,
          total_pages: 1
        }
      })

      wrapper = mount(AdminUsuarios, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            UsersSearchBar: true,
            UsersStatsCards: true,
            UsersTable: true,
            UserFormModal: true,
            UserDetailsModal: true,
            UserActivityModal: true
          }
        }
      })

      // Wait for component to mount and onMounted to execute
      await nextTick()
      await flushPromises()
      // Give additional time for setupWebSocketConnection to be called
      await new Promise(resolve => setTimeout(resolve, 50))
    })

    it('should setup websocket connection', () => {
      expect(mockWebSocket.on).toHaveBeenCalledWith('user-stats-updated', expect.any(Function))
    })

    it('should handle stats update', () => {
      const updateData = {
        total: 20,
        active: 15,
        online: 10,
        new_today: 5
      }
      
      wrapper.vm.handleStatsUpdate(updateData)
      
      expect(wrapper.vm.userStats.total).toBe(20)
      expect(wrapper.vm.userStats.active).toBe(15)
      expect(wrapper.vm.userStats.online).toBe(10)
      expect(wrapper.vm.userStats.new_today).toBe(5)
    })
  })
})

