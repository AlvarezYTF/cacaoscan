import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AccessDenied from '../AccessDenied.vue'
import { useAuthStore } from '@/stores/auth'

// Mock stores
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

// Mock vue-router - must be before component import
const mockRoute = {
  query: {}
}

vi.mock('vue-router', () => ({
  useRoute: vi.fn(() => mockRoute),
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn()
  })),
  RouterLink: { name: 'RouterLink', template: '<a><slot /></a>' },
  RouterView: { name: 'RouterView', template: '<div />' }
}))

describe('AccessDenied', () => {
  let mockAuthStore
  let wrapper

  beforeEach(() => {
    mockAuthStore = {
      isAuthenticated: false,
      user: null,
      userRole: null,
      userFullName: '',
      userInitials: '',
      isVerified: false,
      canUploadImages: false,
      logout: vi.fn()
    }
    useAuthStore.mockReturnValue(mockAuthStore)
    
    // Reset route mock
    mockRoute.query = {}
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  it('should render access denied message', () => {
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': true },
        plugins: [] // Don't use global plugins from setup.js
      }
    })

    expect(wrapper.text().includes('Acceso') || wrapper.text().includes('denegado')).toBe(true)
  })

  it('should show login link when not authenticated', () => {
    mockAuthStore.isAuthenticated = false
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a><slot></slot></a>' } },
        plugins: []
      }
    })

    expect(wrapper.text()).toContain('Iniciar Sesión')
  })

  it('should show user info when authenticated', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.user = {
      id: 1,
      email: 'test@example.com',
      role: 'farmer',
      first_name: 'John',
      last_name: 'Doe'
    }
    mockAuthStore.userFullName = 'John Doe'
    mockAuthStore.userInitials = 'JD'
    mockAuthStore.userRole = 'farmer'
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('test@example.com')
  })

  it('should show verification message when verification required', async () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.isVerified = false
    mockAuthStore.user = { id: 1, email: 'test@example.com' }
    
    mockRoute.query = { error: 'verification_required' }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Verificación')
  })

  it('should display correct error title for access_denied', async () => {
    mockRoute.query = { error: 'access_denied' }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Acceso Restringido')
  })

  it('should display correct error title for insufficient_permissions', async () => {
    mockRoute.query = { error: 'insufficient_permissions' }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Permisos Insuficientes')
  })

  it('should show redirect path based on user role', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.user = { role: 'admin' }
    mockAuthStore.userRole = 'admin'
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 
          'router-link': { 
            template: '<a><slot></slot></a>',
            props: ['to']
          } 
        }
      }
    })

    const dashboardLink = wrapper.findAll('a').find(
      link => link.attributes('to') === '/admin/dashboard' || link.text().includes('Dashboard')
    )
    expect(dashboardLink).toBeTruthy()
    expect(wrapper.text()).toContain('Dashboard')
  })

  it('should call logout when logout button is clicked', async () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.user = { id: 1 }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    const logoutButton = wrapper.find('button')
    if (logoutButton.exists()) {
      await logoutButton.trigger('click')
      expect(mockAuthStore.logout).toHaveBeenCalled()
    }
  })

  it('should display role text correctly', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.user = { role: 'farmer' }
    mockAuthStore.userRole = 'farmer'
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    expect(wrapper.text()).toMatch(/Agricultor|Usuario/i)
  })

  it('should display correct error title for verification_required', async () => {
    mockRoute.query = { error: 'verification_required' }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Verificación Requerida')
  })

  it('should display correct error title when message is provided', async () => {
    mockRoute.query = { message: 'Custom error message' }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Acceso Denegado')
  })

  it('should display default error title', async () => {
    mockRoute.query = {}
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Sin Permisos')
  })

  it('should display correct error message for access_denied', async () => {
    mockRoute.query = { error: 'access_denied' }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('No tienes autorización')
  })

  it('should display correct error message for insufficient_permissions', async () => {
    mockRoute.query = { error: 'insufficient_permissions' }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('permisos necesarios')
  })

  it('should display correct error message for verification_required', async () => {
    mockRoute.query = { error: 'verification_required' }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('verificar tu dirección de email')
  })

  it('should display message from query when provided', async () => {
    mockRoute.query = { message: 'Custom message' }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Custom message')
  })

  it('should display default message for authenticated user', async () => {
    mockAuthStore.isAuthenticated = true
    mockRoute.query = {}
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Contacta al administrador')
  })

  it('should get redirect path for analyst role', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.user = { role: 'analyst' }
    mockAuthStore.userRole = 'analyst'
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 
          'router-link': { 
            template: '<a><slot></slot></a>',
            props: ['to']
          } 
        }
      }
    })

    const redirectPath = wrapper.vm.getRedirectPath()
    expect(redirectPath).toBe('/analisis')
  })

  it('should get redirect path for farmer role', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.user = { role: 'farmer' }
    mockAuthStore.userRole = 'farmer'
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 
          'router-link': { 
            template: '<a><slot></slot></a>',
            props: ['to']
          } 
        }
      }
    })

    const redirectPath = wrapper.vm.getRedirectPath()
    expect(redirectPath).toBe('/agricultor-dashboard')
  })

  it('should get default redirect path when no user', () => {
    mockAuthStore.isAuthenticated = false
    mockAuthStore.user = null
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } }
      }
    })

    const redirectPath = wrapper.vm.getRedirectPath()
    expect(redirectPath).toBe('/')
  })

  it('should get default redirect path for unknown role', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.user = { role: 'unknown' }
    mockAuthStore.userRole = 'unknown'
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } }
      }
    })

    const redirectPath = wrapper.vm.getRedirectPath()
    expect(redirectPath).toBe('/')
  })

  it('should show canUploadImages link when user can upload', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.canUploadImages = true
    mockAuthStore.user = { id: 1 }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 
          'router-link': { 
            template: '<a><slot></slot></a>',
            props: ['to']
          } 
        },
        plugins: []
      }
    })

    expect(wrapper.text()).toContain('Analizar Cacao')
  })

  it('should handle needsVerification with message containing verificar', async () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.isVerified = false
    mockRoute.query = { message: 'Debes verificar tu email' }
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.vm.needsVerification).toBe(true)
  })

  it('should display role text for analyst', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.user = { role: 'analyst' }
    mockAuthStore.userRole = 'analyst'
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    expect(wrapper.text()).toContain('Analista')
  })

  it('should display role text for admin', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.user = { role: 'admin' }
    mockAuthStore.userRole = 'admin'
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    expect(wrapper.text()).toContain('Administrador')
  })

  it('should display default role text for unknown role', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.user = { role: 'unknown' }
    mockAuthStore.userRole = 'unknown'
    
    wrapper = mount(AccessDenied, {
      global: {
        stubs: { 'router-link': { template: '<a>Link</a>' } },
        plugins: []
      }
    })

    expect(wrapper.text()).toContain('Usuario')
  })
})

