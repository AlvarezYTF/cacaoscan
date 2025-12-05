import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ref, computed } from 'vue'
import AdminAgricultores from '../../Admin/AdminAgricultores.vue'

// Mock usePagination composable - define mockPagination first
const mockPagination = {
  currentPage: ref(1),
  itemsPerPage: ref(10),
  totalItems: ref(0),
  totalPages: computed(() => Math.ceil(mockPagination.totalItems.value / mockPagination.itemsPerPage.value)),
  updatePagination: vi.fn((params) => {
    if (params.count !== undefined) {
      mockPagination.totalItems.value = params.count
    }
    if (params.page !== undefined) {
      mockPagination.currentPage.value = params.page
    }
    if (params.page_size !== undefined) {
      mockPagination.itemsPerPage.value = params.page_size
    }
  }),
  goToPage: vi.fn(),
  nextPage: vi.fn(),
  previousPage: vi.fn(),
  setItemsPerPage: vi.fn(),
  setTotalItems: vi.fn()
}

vi.mock('@/composables/usePagination', () => ({
  usePagination: () => mockPagination
}))

// Mock auth store
const mockAuthStore = {
  user: { id: 1, first_name: 'Test', last_name: 'User', username: 'testuser' },
  userRole: 'admin',
  logout: vi.fn()
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock services - must be defined inside vi.mock factory to avoid hoisting issues
vi.mock('@/services/authApi', () => {
  const mockAuthApi = {
    getUsers: vi.fn().mockResolvedValue({ results: [] }),
    deleteUser: vi.fn().mockResolvedValue({}),
    toggleUserStatus: vi.fn().mockResolvedValue({})
  }
  return {
    default: mockAuthApi
  }
})

vi.mock('@/services/fincasApi', () => ({
  getFincas: vi.fn().mockResolvedValue({ results: [] })
}))

vi.mock('@/services/reportsApi', () => ({
  default: {
    downloadReporteAgricultores: vi.fn().mockResolvedValue({})
  }
}))

// Mock sweetalert2 - define mock inside factory to avoid hoisting issues
vi.mock('sweetalert2', () => {
  const mockSwal = {
    fire: vi.fn().mockResolvedValue({ isConfirmed: false })
  }
  return {
    default: mockSwal
  }
})

// Mock vue-router - define mockRouter inside factory to avoid hoisting issues
vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  const mockRouterInstance = {
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    beforeEach: vi.fn(),
    beforeResolve: vi.fn(),
    afterEach: vi.fn(),
    currentRoute: { value: { path: '/', params: {}, query: {}, meta: {} } },
    isReady: vi.fn().mockResolvedValue(true)
  }
  return {
    ...actual,
    createRouter: vi.fn((options) => mockRouterInstance),
    createWebHistory: vi.fn(() => ({})),
    createMemoryHistory: vi.fn(() => ({})),
    useRouter: () => mockRouterInstance,
    useRoute: () => ({
      path: '/',
      params: {},
      query: {},
      meta: {}
    }),
    RouterLink: {
      name: 'RouterLink',
      template: '<a><slot></slot></a>',
      props: ['to']
    },
    RouterView: {
      name: 'RouterView',
      template: '<div></div>'
    }
  }
})

// Mock @/router to prevent router/index.js from executing
vi.mock('@/router', () => {
  const mockRouterForApi = {
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    beforeEach: vi.fn(),
    beforeResolve: vi.fn(),
    afterEach: vi.fn(),
    currentRoute: { value: { path: '/', params: {}, query: {}, meta: {} } },
    isReady: vi.fn().mockResolvedValue(true)
  }
  return {
    default: mockRouterForApi
  }
})

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

  describe('rendering', () => {
    it('should render agricultores view', () => {
      wrapper = mount(AdminAgricultores, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            FarmersStatsCards: true,
            FarmersSearchBar: true,
            FarmersTable: true,
            CreateFarmerModal: true,
            FarmerDetailModal: true,
            EditFarmerModal: true
          }
        }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('data loading', () => {
    it('should load farmers on mount', async () => {
      const authApi = await import('@/services/authApi')
      const fincasApi = await import('@/services/fincasApi')
      
      authApi.default.getUsers.mockResolvedValue({
        results: [
          { id: 1, role: 'farmer', first_name: 'Farmer', last_name: 'One', email: 'farmer1@test.com' }
        ]
      })
      fincasApi.getFincas.mockResolvedValue({
        results: [
          { id: 1, nombre: 'Finca 1', agricultor_id: 1, hectareas: 10, activa: true }
        ]
      })

      wrapper = mount(AdminAgricultores, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            FarmersStatsCards: true,
            FarmersSearchBar: true,
            FarmersTable: true,
            CreateFarmerModal: true,
            FarmerDetailModal: true,
            EditFarmerModal: true
          }
        }
      })

      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(authApi.default.getUsers).toHaveBeenCalled()
      expect(fincasApi.getFincas).toHaveBeenCalled()
    })

    it('should handle error loading farmers', async () => {
      const authApi = await import('@/services/authApi')
      await import('sweetalert2')
      
      authApi.default.getUsers.mockRejectedValue(new Error('Load error'))

      wrapper = mount(AdminAgricultores, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            FarmersStatsCards: true,
            FarmersSearchBar: true,
            FarmersTable: true,
            CreateFarmerModal: true,
            FarmerDetailModal: true,
            EditFarmerModal: true
          }
        }
      })

      await new Promise(resolve => setTimeout(resolve, 100))
    })
  })

  describe('farmer management', () => {
    let openModalSpy
    let viewModalSpy
    let editModalSpy
    
    beforeEach(async () => {
      const authApi = await import('@/services/authApi')
      const fincasApi = await import('@/services/fincasApi')
      
      authApi.default.getUsers.mockResolvedValue({ results: [] })
      fincasApi.getFincas.mockResolvedValue({ results: [] })
      
      openModalSpy = vi.fn()
      viewModalSpy = vi.fn()
      editModalSpy = vi.fn()

      wrapper = mount(AdminAgricultores, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            FarmersStatsCards: true,
            FarmersSearchBar: true,
            FarmersTable: true,
            CreateFarmerModal: {
              template: '<div></div>',
              methods: {
                openModal: openModalSpy
              }
            },
            FarmerDetailModal: {
              template: '<div></div>',
              methods: {
                openModal: viewModalSpy
              }
            },
            EditFarmerModal: {
              template: '<div></div>',
              methods: {
                openModal: editModalSpy
              }
            }
          }
        }
      })

      await new Promise(resolve => setTimeout(resolve, 100))
      
      // Set up the refs after mount - Vue 3 template refs need to be configured
      await wrapper.vm.$nextTick()
      
      // Import ref from vue to create refs if they don't exist
      const { ref } = await import('vue')
      
      // Configure createFarmerModalRef
      if (!wrapper.vm.createFarmerModalRef) {
        wrapper.vm.createFarmerModalRef = ref(null)
      }
      wrapper.vm.createFarmerModalRef.value = { openModal: openModalSpy }
      
      // Configure farmerDetailModalRef
      if (!wrapper.vm.farmerDetailModalRef) {
        wrapper.vm.farmerDetailModalRef = ref(null)
      }
      wrapper.vm.farmerDetailModalRef.value = { openModal: viewModalSpy }
      
      // Configure editFarmerModalRef
      if (!wrapper.vm.editFarmerModalRef) {
        wrapper.vm.editFarmerModalRef = ref(null)
      }
      wrapper.vm.editFarmerModalRef.value = { openModal: editModalSpy }
      
      await wrapper.vm.$nextTick()
    })

    it('should open create farmer modal', async () => {
      // The component accesses createFarmerModalRef.value.openModal()
      // In Vue 3 with script setup, template refs are in $refs
      // We need to ensure the ref is set correctly
      const mockModal = { openModal: openModalSpy }
      
      // Set the ref value - try both $refs and direct access
      if (wrapper.vm.$refs?.createFarmerModalRef) {
        // If ref exists in $refs, update it
        Object.assign(wrapper.vm.$refs.createFarmerModalRef, mockModal)
      }
      
      // Also try setting it as a Vue ref on the component instance
      const { ref } = await import('vue')
      const modalRef = ref(mockModal)
      // Use defineProperty to set the ref on the component
      Object.defineProperty(wrapper.vm, 'createFarmerModalRef', {
        value: modalRef,
        writable: true,
        configurable: true,
        enumerable: true
      })

      await wrapper.vm.$nextTick()
      await wrapper.vm.handleNewFarmer()
      await wrapper.vm.$nextTick()
      
      expect(openModalSpy).toHaveBeenCalled()
    })

    it('should handle farmer created', async () => {
      const authApi = await import('@/services/authApi')
      const fincasApi = await import('@/services/fincasApi')
      await import('sweetalert2')
      
      authApi.default.getUsers.mockResolvedValue({ results: [] })
      fincasApi.getFincas.mockResolvedValue({ results: [] })

      await wrapper.vm.handleFarmerCreated()
      
      expect(authApi.default.getUsers).toHaveBeenCalled()
    })

    it('should view farmer', async () => {
      const farmer = { id: 1, name: 'Farmer One' }
      
      // Clear any previous calls
      viewModalSpy.mockClear()
      
      // Verify the ref is set correctly (configured in beforeEach)
      expect(wrapper.vm.farmerDetailModalRef).toBeDefined()
      expect(wrapper.vm.farmerDetailModalRef.value).toBeDefined()
      expect(wrapper.vm.farmerDetailModalRef.value.openModal).toBe(viewModalSpy)

      await wrapper.vm.handleViewFarmer(farmer)
      await wrapper.vm.$nextTick() // Wait for nextTick inside handleViewFarmer
      await wrapper.vm.$nextTick() // Additional tick for async operations
      
      expect(wrapper.vm.selectedFarmer).toStrictEqual(farmer)
      expect(viewModalSpy).toHaveBeenCalled()
    })

    it('should edit farmer', async () => {
      const farmer = { id: 1, name: 'Farmer One' }
      
      // Clear any previous calls
      editModalSpy.mockClear()
      
      // Ensure the ref is set correctly (configured in beforeEach, but verify and ensure it's available)
      expect(wrapper.vm.editFarmerModalRef).toBeDefined()
      if (!wrapper.vm.editFarmerModalRef.value) {
        wrapper.vm.editFarmerModalRef.value = { openModal: editModalSpy }
      }
      expect(wrapper.vm.editFarmerModalRef.value).toBeDefined()
      expect(wrapper.vm.editFarmerModalRef.value.openModal).toBe(editModalSpy)
      await wrapper.vm.$nextTick()

      await wrapper.vm.handleEditFarmer(farmer)
      await wrapper.vm.$nextTick() // Wait for nextTick inside handleEditFarmer
      await wrapper.vm.$nextTick() // Additional tick for async operations
      
      expect(wrapper.vm.selectedFarmerForEdit).toStrictEqual(farmer)
      expect(editModalSpy).toHaveBeenCalled()
    })

    it('should handle farmer updated', async () => {
      const authApi = await import('@/services/authApi')
      const fincasApi = await import('@/services/fincasApi')
      
      authApi.default.getUsers.mockResolvedValue({ results: [] })
      fincasApi.getFincas.mockResolvedValue({ results: [] })

      await wrapper.vm.handleFarmerUpdated()
      
      expect(authApi.default.getUsers).toHaveBeenCalled()
    })
  })

  describe('farmer deletion', () => {
    beforeEach(async () => {
      const authApi = await import('@/services/authApi')
      const fincasApi = await import('@/services/fincasApi')
      
      authApi.default.getUsers.mockResolvedValue({
        results: [
          { id: 1, role: 'farmer', first_name: 'Farmer', last_name: 'One' }
        ]
      })
      fincasApi.getFincas.mockResolvedValue({ results: [] })

      wrapper = mount(AdminAgricultores, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            FarmersStatsCards: true,
            FarmersSearchBar: true,
            FarmersTable: true,
            CreateFarmerModal: true,
            FarmerDetailModal: true,
            EditFarmerModal: true
          }
        }
      })

      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should delete farmer when confirmed', async () => {
      await import('sweetalert2')
      const authApi = await import('@/services/authApi')
      
      Swal.default.fire.mockResolvedValue({ isConfirmed: true })
      authApi.default.deleteUser.mockResolvedValue({})

      const farmer = { id: 1, name: 'Farmer One' }
      wrapper.vm.farmers = [farmer]

      await wrapper.vm.handleDeleteFarmer(farmer)
      
      expect(authApi.default.deleteUser).toHaveBeenCalledWith(1)
    })

    it('should handle delete error', async () => {
      await import('sweetalert2')
      const authApi = await import('@/services/authApi')
      
      Swal.default.fire.mockResolvedValue({ isConfirmed: true })
      const error = { response: { data: { error: 'Delete failed' } } }
      authApi.default.deleteUser.mockRejectedValue(error)

      const farmer = { id: 1, name: 'Farmer One' }
      
      await wrapper.vm.handleDeleteFarmer(farmer)
      
      expect(Swal.default.fire).toHaveBeenCalled()
    })
  })

  describe('toggle status', () => {
    beforeEach(async () => {
      const authApi = await import('@/services/authApi')
      const fincasApi = await import('@/services/fincasApi')
      
      authApi.default.getUsers.mockResolvedValue({
        results: [
          { id: 1, role: 'farmer', first_name: 'Farmer', last_name: 'One', is_active: true }
        ]
      })
      fincasApi.getFincas.mockResolvedValue({ results: [] })

      wrapper = mount(AdminAgricultores, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            FarmersStatsCards: true,
            FarmersSearchBar: true,
            FarmersTable: true,
            CreateFarmerModal: true,
            FarmerDetailModal: true,
            EditFarmerModal: true
          }
        }
      })

      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should toggle farmer status', async () => {
      await import('sweetalert2')
      const authApi = await import('@/services/authApi')
      
      authApi.default.toggleUserStatus.mockResolvedValue({})

      const farmer = wrapper.vm.farmers[0]
      const initialStatus = farmer.is_active

      await wrapper.vm.handleToggleStatus(farmer)
      
      expect(authApi.default.toggleUserStatus).toHaveBeenCalled()
      expect(farmer.is_active).toBe(!initialStatus)
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should handle toggle error', async () => {
      await import('sweetalert2')
      const authApi = await import('@/services/authApi')
      
      const error = { response: { data: { error: 'Toggle failed' } } }
      authApi.default.toggleUserStatus.mockRejectedValue(error)

      const farmer = wrapper.vm.farmers[0]
      
      await wrapper.vm.handleToggleStatus(farmer)
      
      expect(Swal.default.fire).toHaveBeenCalled()
    })
  })

  describe('report download', () => {
    beforeEach(async () => {
      const authApi = await import('@/services/authApi')
      const fincasApi = await import('@/services/fincasApi')
      
      authApi.default.getUsers.mockResolvedValue({ results: [] })
      fincasApi.getFincas.mockResolvedValue({ results: [] })

      wrapper = mount(AdminAgricultores, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            FarmersStatsCards: true,
            FarmersSearchBar: true,
            FarmersTable: true,
            CreateFarmerModal: true,
            FarmerDetailModal: true,
            EditFarmerModal: true
          }
        }
      })

      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should download report', async () => {
      await import('sweetalert2')
      const reportsApi = await import('@/services/reportsApi')
      
      // Ensure the mock is set up
      Swal.default.fire.mockClear()
      
      await wrapper.vm.descargarReporteAgricultores()
      
      expect(reportsApi.default.downloadReporteAgricultores).toHaveBeenCalled()
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should handle download error', async () => {
      await import('sweetalert2')
      const reportsApi = await import('@/services/reportsApi')
      
      // Ensure the mock is set up
      Swal.default.fire.mockClear()
      reportsApi.default.downloadReporteAgricultores.mockRejectedValue(new Error('Download failed'))

      await wrapper.vm.descargarReporteAgricultores()
      
      expect(Swal.default.fire).toHaveBeenCalled()
    })
  })

  describe('pagination', () => {
    beforeEach(async () => {
      const authApi = await import('@/services/authApi')
      const fincasApi = await import('@/services/fincasApi')
      
      authApi.default.getUsers.mockResolvedValue({ results: [] })
      fincasApi.getFincas.mockResolvedValue({ results: [] })

      wrapper = mount(AdminAgricultores, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            FarmersStatsCards: true,
            FarmersSearchBar: true,
            FarmersTable: true,
            CreateFarmerModal: true,
            FarmerDetailModal: true,
            EditFarmerModal: true
          }
        }
      })

      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should handle page change', () => {
      wrapper.vm.handlePageChange(2)
      expect(mockPagination.goToPage).toHaveBeenCalledWith(2)
    })
  })

  describe('sidebar', () => {
    beforeEach(async () => {
      wrapper = mount(AdminAgricultores, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            FarmersStatsCards: true,
            FarmersSearchBar: true,
            FarmersTable: true,
            CreateFarmerModal: true,
            FarmerDetailModal: true,
            EditFarmerModal: true
          }
        }
      })

      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should toggle sidebar collapse', () => {
      const initialValue = wrapper.vm.isSidebarCollapsed
      wrapper.vm.toggleSidebarCollapse()
      expect(wrapper.vm.isSidebarCollapsed).toBe(!initialValue)
    })

    it('should handle menu click', async () => {
      const { useRouter } = await import('vue-router')
      const mockRouter = useRouter()
      wrapper.vm.handleMenuClick({ route: '/admin/dashboard' })
      expect(mockRouter.push).toHaveBeenCalledWith('/admin/dashboard')
    })

    it('should handle logout', async () => {
      const { useRouter } = await import('vue-router')
      const mockRouter = useRouter()
      await wrapper.vm.handleLogout()
      expect(mockAuthStore.logout).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })
  })

  describe('filtering', () => {
    beforeEach(async () => {
      const authApi = await import('@/services/authApi')
      const fincasApi = await import('@/services/fincasApi')
      
      authApi.default.getUsers.mockResolvedValue({
        results: [
          { id: 1, role: 'farmer', first_name: 'Farmer', last_name: 'One', email: 'farmer1@test.com', region: 'Region1' }
        ]
      })
      fincasApi.getFincas.mockResolvedValue({ results: [] })

      wrapper = mount(AdminAgricultores, {
        global: {
          stubs: {
            'router-link': true,
            'router-view': true,
            AdminSidebar: true,
            FarmersStatsCards: true,
            FarmersSearchBar: true,
            FarmersTable: true,
            CreateFarmerModal: true,
            FarmerDetailModal: true,
            EditFarmerModal: true
          }
        }
      })

      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should filter farmers by search query', () => {
      wrapper.vm.searchQuery = 'Farmer'
      expect(wrapper.vm.filteredFarmers.length).toBeGreaterThan(0)

      wrapper.vm.searchQuery = 'Nonexistent'
      expect(wrapper.vm.filteredFarmers.length).toBe(0)
    })

    it('should filter farmers by region', () => {
      wrapper.vm.filters.region = 'Region1'
      expect(wrapper.vm.filteredFarmers.length).toBeGreaterThan(0)

      wrapper.vm.filters.region = 'Region2'
      expect(wrapper.vm.filteredFarmers.length).toBe(0)
    })

    it('should filter farmers by status', () => {
      wrapper.vm.filters.status = 'Activo'
      const activeCount = wrapper.vm.filteredFarmers.length

      wrapper.vm.filters.status = 'Inactivo'
      const inactiveCount = wrapper.vm.filteredFarmers.length

      expect(activeCount).not.toBe(inactiveCount)
    })
  })
})

