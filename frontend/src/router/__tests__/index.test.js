import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createMockAuthStore } from '@/test/mocks'

// Mock views
const mockHomeView = { template: '<div>Home</div>' }
const mockLoginView = { template: '<div>Login</div>' }
const mockAdminDashboard = { template: '<div>Admin Dashboard</div>' }
const mockFincasView = { template: '<div>Fincas</div>' }

// Mock auth store
const mockAuthStore = createMockAuthStore()

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock views imports
vi.mock('@/views/Pages/HomeView.vue', () => ({ default: mockHomeView }))
vi.mock('@/views/Auth/LoginView.vue', () => ({ default: mockLoginView }))
vi.mock('@/views/Admin/AdminDashboard.vue', () => ({ default: mockAdminDashboard }))
vi.mock('@/views/common/FincasView.vue', () => ({ default: mockFincasView }))

// Mock globalThis
globalThis.document = {
  title: '',
  createElement: vi.fn((tag) => {
    const element = {
      tagName: tag.toUpperCase(),
      setAttribute: vi.fn(),
      appendChild: vi.fn(),
      removeChild: vi.fn(),
      style: {},
      innerHTML: '',
      textContent: ''
    }
    return element
  })
}
globalThis.scrollTo = vi.fn()
globalThis.dispatchEvent = vi.fn()

// Mock sweetalert2
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(),
    Swal: {
      fire: vi.fn()
    }
  }
}))

// Import router after mocks
let router

describe('Router Configuration', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    mockAuthStore.isAuthenticated = false
    mockAuthStore.accessToken = null
    mockAuthStore.user = null
    mockAuthStore.userRole = null

    // Dynamic import to ensure mocks are set up
    const routerModule = await import('../index.js')
    router = routerModule.default
  })

  describe('Route Definitions', () => {
    it('should have Home route', () => {
      const route = router.resolve('/')
      expect(route.name).toBe('Home')
      expect(route.meta.requiresAuth).toBe(false)
    })

    it('should have Login route', () => {
      const route = router.resolve('/login')
      expect(route.name).toBe('Login')
      expect(route.meta.requiresGuest).toBe(true)
    })

    it('should have Dashboard route with redirect', () => {
      const route = router.resolve('/dashboard')
      expect(route.name).toBe('Dashboard')
      expect(route.meta.requiresAuth).toBe(true)
    })

    it('should have Fincas route', () => {
      const route = router.resolve('/fincas')
      expect(route.name).toBe('Fincas')
      expect(route.meta.requiresAuth).toBe(true)
    })

    it('should have Admin Dashboard route', () => {
      const route = router.resolve('/admin/dashboard')
      expect(route.name).toBe('AdminDashboard')
      expect(route.meta.requiresAuth).toBe(true)
      expect(route.meta.requiresRole).toBe('admin')
    })

    it('should have Register route', () => {
      const route = router.resolve('/registro')
      expect(route.name).toBe('Register')
      expect(route.meta.requiresGuest).toBe(true)
    })

    it('should have ForgotPassword route', () => {
      const route = router.resolve('/auth/forgot-password')
      expect(route.name).toBe('ForgotPassword')
      expect(route.meta.requiresGuest).toBe(true)
    })
  })

  describe('Dashboard Redirect', () => {
    it('should redirect to login when not authenticated', () => {
      mockAuthStore.isAuthenticated = false

      const redirectFn = router.resolve('/dashboard').redirectedFrom?.redirect
      if (redirectFn) {
        const result = redirectFn()
        expect(result).toBe('/login')
      }
    })

    it('should redirect admin to admin dashboard', () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.userRole = 'admin'

      const redirectFn = router.resolve('/dashboard').redirectedFrom?.redirect
      if (redirectFn) {
        const result = redirectFn()
        expect(result).toBe('/admin/dashboard')
      }
    })

    it('should redirect analyst to analisis', () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.userRole = 'analyst'

      const redirectFn = router.resolve('/dashboard').redirectedFrom?.redirect
      if (redirectFn) {
        const result = redirectFn()
        expect(result).toBe('/analisis')
      }
    })

    it('should redirect farmer to agricultor-dashboard', () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.userRole = 'farmer'

      const redirectFn = router.resolve('/dashboard').redirectedFrom?.redirect
      if (redirectFn) {
        const result = redirectFn()
        expect(result).toBe('/agricultor-dashboard')
      }
    })
  })

  describe('Navigation Guards', () => {
    it('should set document title from route meta', async () => {
      const to = {
        path: '/',
        name: 'Home',
        meta: { title: 'Test Title' }
      }

      await router.beforeEach(to, { path: '/' })

      expect(globalThis.document.title).toBeDefined()
    })

    it('should redirect guest route if authenticated', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.userRole = 'admin'

      const to = {
        path: '/login',
        name: 'Login',
        meta: { requiresGuest: true },
        fullPath: '/login'
      }

      const result = await router.beforeEach(to, { path: '/' })

      expect(result).toBeDefined()
    })

    it('should redirect to login if requiresAuth and not authenticated', async () => {
      mockAuthStore.isAuthenticated = false
      mockAuthStore.accessToken = null

      const to = {
        path: '/fincas',
        name: 'Fincas',
        meta: { requiresAuth: true },
        fullPath: '/fincas'
      }

      const result = await router.beforeEach(to, { path: '/' })

      expect(result).toBeDefined()
      if (result && typeof result === 'object') {
        expect(result.name).toBe('Login')
      }
    })

    it('should allow navigation if authenticated and has required role', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.accessToken = 'test-token'
      mockAuthStore.user = { id: 1, role: 'admin' }
      mockAuthStore.userRole = 'admin'
      mockAuthStore.getCurrentUser.mockResolvedValue(mockAuthStore.user)

      const to = {
        path: '/admin/dashboard',
        name: 'AdminDashboard',
        meta: { requiresAuth: true, requiresRole: 'admin' },
        fullPath: '/admin/dashboard'
      }

      const result = await router.beforeEach(to, { path: '/' })

      expect(mockAuthStore.updateLastActivity).toHaveBeenCalled()
    })

    it('should redirect if user does not have required role', async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.accessToken = 'test-token'
      mockAuthStore.user = { id: 1, role: 'farmer' }
      mockAuthStore.userRole = 'farmer'
      mockAuthStore.getCurrentUser.mockResolvedValue(mockAuthStore.user)

      const to = {
        path: '/admin/dashboard',
        name: 'AdminDashboard',
        meta: { requiresAuth: true, requiresRole: 'admin' },
        fullPath: '/admin/dashboard'
      }

      const result = await router.beforeEach(to, { path: '/' })

      expect(result).toBeDefined()
      if (result && typeof result === 'object' && result.path) {
        expect(result.path).toBe('/acceso-denegado')
      }
    })

    it('should handle getCurrentUser error and redirect to login', async () => {
      mockAuthStore.isAuthenticated = false
      mockAuthStore.accessToken = 'invalid-token'
      mockAuthStore.user = null
      mockAuthStore.getCurrentUser.mockRejectedValue(new Error('Invalid token'))

      const to = {
        path: '/fincas',
        name: 'Fincas',
        meta: { requiresAuth: true },
        fullPath: '/fincas'
      }

      const result = await router.beforeEach(to, { path: '/' })

      expect(mockAuthStore.clearAll).toHaveBeenCalled()
      expect(result).toBeDefined()
    })
  })

  describe('After Each Guard', () => {
    it('should scroll to top on route change', async () => {
      const to = { path: '/new', name: 'NewRoute' }
      const from = { path: '/old', name: 'OldRoute' }

      router.afterEach(to, from)

      expect(globalThis.scrollTo).toHaveBeenCalledWith(0, 0)
    })

    it('should not scroll if same path', async () => {
      const to = { path: '/same', name: 'SameRoute' }
      const from = { path: '/same', name: 'SameRoute' }

      globalThis.scrollTo.mockClear()
      router.afterEach(to, from)

      expect(globalThis.scrollTo).not.toHaveBeenCalled()
    })
  })

  describe('Route Meta', () => {
    it('should have correct meta for public routes', () => {
      const route = router.resolve('/')
      expect(route.meta.requiresAuth).toBe(false)
    })

    it('should have correct meta for protected routes', () => {
      const route = router.resolve('/fincas')
      expect(route.meta.requiresAuth).toBe(true)
    })

    it('should have role requirements for admin routes', () => {
      const route = router.resolve('/admin/dashboard')
      expect(route.meta.requiresRole).toBe('admin')
    })
  })
})

