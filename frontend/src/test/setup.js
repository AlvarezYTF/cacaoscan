import { config } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import { vi } from 'vitest'

// Mock para Tailwind CSS v4 - clsfn function
if (globalThis.clsfn === undefined) {
  globalThis.clsfn = (classes) => {
    if (typeof classes === 'string') {
      return classes
    }
    if (Array.isArray(classes)) {
      return classes.filter(Boolean).join(' ')
    }
    if (typeof classes === 'object' && classes !== null) {
      return Object.entries(classes)
        .filter(([, value]) => Boolean(value))
        .map(([key]) => key)
        .join(' ')
    }
    return ''
  }
}

// Configuración global para tests
const pinia = createPinia()
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/login', component: { template: '<div>Login</div>' } },
    { path: '/dashboard', component: { template: '<div>Dashboard</div>' } },
    { path: '/reset-password/confirm', component: { template: '<div>PasswordResetConfirm</div>' } },
    { path: '/reset-password', component: { template: '<div>Reset</div>' } },
    { path: '/user/prediction', component: { template: '<div>UserPrediction</div>' } }
  ]
})

config.global.plugins = [pinia, router]

// Mock global de window.matchMedia
Object.defineProperty(globalThis, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock global de IntersectionObserver
globalThis.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock global de ResizeObserver
globalThis.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock global de fetch
globalThis.fetch = vi.fn()

// Mock global de localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
globalThis.localStorage = localStorageMock

// Mock global de sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
globalThis.sessionStorage = sessionStorageMock

// Mock global de URL.createObjectURL y URL.revokeObjectURL
if (typeof URL.createObjectURL === 'undefined') {
  globalThis.URL.createObjectURL = vi.fn((file) => {
    return `blob:${file.name || 'mock-url'}-${Date.now()}`
  })
}

if (typeof URL.revokeObjectURL === 'undefined') {
  globalThis.URL.revokeObjectURL = vi.fn()
}
