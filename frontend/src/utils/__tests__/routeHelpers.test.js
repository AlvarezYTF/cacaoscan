/**
 * Unit tests for route helper functions
 * Pure functions with no external dependencies - deterministic tests
 */

import { describe, it, expect } from 'vitest'
import {
  createRouteMeta,
  createPublicRoute,
  createAuthRoute,
  createGuestRoute
} from '../routeHelpers.js'

const mockComponent = { template: '<div>Test</div>' }

describe('routeHelpers', () => {
  describe('createRouteMeta', () => {
    it('should create route meta with default values', () => {
      const meta = createRouteMeta('Test Page')
      expect(meta.title).toBe('Test Page | CacaoScan')
      expect(meta.requiresAuth).toBe(false)
    })

    it('should create route meta with requiresAuth', () => {
      const meta = createRouteMeta('Test Page', { requiresAuth: true })
      expect(meta.title).toBe('Test Page | CacaoScan')
      expect(meta.requiresAuth).toBe(true)
    })

    it('should create route meta with requiresGuest', () => {
      const meta = createRouteMeta('Test Page', { requiresGuest: true })
      expect(meta.title).toBe('Test Page | CacaoScan')
      expect(meta.requiresGuest).toBe(true)
      expect(meta.requiresAuth).toBe(false)
    })

    it('should create route meta with requiresRole', () => {
      const meta = createRouteMeta('Test Page', { requiresRole: 'admin' })
      expect(meta.title).toBe('Test Page | CacaoScan')
      expect(meta.requiresRole).toBe('admin')
    })

    it('should create route meta with requiresVerification', () => {
      const meta = createRouteMeta('Test Page', { requiresVerification: true })
      expect(meta.title).toBe('Test Page | CacaoScan')
      expect(meta.requiresVerification).toBe(true)
    })

    it('should create route meta with all options', () => {
      const meta = createRouteMeta('Test Page', {
        requiresAuth: true,
        requiresRole: 'admin',
        requiresVerification: true
      })
      expect(meta.title).toBe('Test Page | CacaoScan')
      expect(meta.requiresAuth).toBe(true)
      expect(meta.requiresRole).toBe('admin')
      expect(meta.requiresVerification).toBe(true)
    })

    it('should not include optional properties when not set', () => {
      const meta = createRouteMeta('Test Page')
      expect(meta).not.toHaveProperty('requiresRole')
      expect(meta).not.toHaveProperty('requiresVerification')
      expect(meta).not.toHaveProperty('requiresGuest')
    })
  })

  describe('createPublicRoute', () => {
    it('should create public route configuration', () => {
      const route = createPublicRoute('/test', 'Test', mockComponent, 'Test Page')
      expect(route.path).toBe('/test')
      expect(route.name).toBe('Test')
      expect(route.component).toBe(mockComponent)
      expect(route.meta.title).toBe('Test Page | CacaoScan')
      expect(route.meta.requiresAuth).toBe(false)
    })

    it('should have requiresAuth set to false', () => {
      const route = createPublicRoute('/public', 'Public', mockComponent, 'Public Page')
      expect(route.meta.requiresAuth).toBe(false)
    })

    it('should not include requiresRole or requiresVerification', () => {
      const route = createPublicRoute('/public', 'Public', mockComponent, 'Public Page')
      expect(route.meta).not.toHaveProperty('requiresRole')
      expect(route.meta).not.toHaveProperty('requiresVerification')
    })
  })

  describe('createAuthRoute', () => {
    it('should create authenticated route configuration', () => {
      const route = createAuthRoute('/dashboard', 'Dashboard', mockComponent, 'Dashboard')
      expect(route.path).toBe('/dashboard')
      expect(route.name).toBe('Dashboard')
      expect(route.component).toBe(mockComponent)
      expect(route.meta.title).toBe('Dashboard | CacaoScan')
      expect(route.meta.requiresAuth).toBe(true)
    })

    it('should create route with required role', () => {
      const route = createAuthRoute(
        '/admin',
        'Admin',
        mockComponent,
        'Admin Page',
        { requiresRole: 'admin' }
      )
      expect(route.meta.requiresAuth).toBe(true)
      expect(route.meta.requiresRole).toBe('admin')
    })

    it('should create route with email verification requirement', () => {
      const route = createAuthRoute(
        '/settings',
        'Settings',
        mockComponent,
        'Settings',
        { requiresVerification: true }
      )
      expect(route.meta.requiresAuth).toBe(true)
      expect(route.meta.requiresVerification).toBe(true)
    })

    it('should create route with both role and verification', () => {
      const route = createAuthRoute(
        '/admin/settings',
        'AdminSettings',
        mockComponent,
        'Admin Settings',
        {
          requiresRole: 'admin',
          requiresVerification: true
        }
      )
      expect(route.meta.requiresAuth).toBe(true)
      expect(route.meta.requiresRole).toBe('admin')
      expect(route.meta.requiresVerification).toBe(true)
    })

    it('should not include requiresRole when not specified', () => {
      const route = createAuthRoute('/dashboard', 'Dashboard', mockComponent, 'Dashboard')
      expect(route.meta).not.toHaveProperty('requiresRole')
    })
  })

  describe('createGuestRoute', () => {
    it('should create guest route configuration', () => {
      const route = createGuestRoute('/login', 'Login', mockComponent, 'Login')
      expect(route.path).toBe('/login')
      expect(route.name).toBe('Login')
      expect(route.component).toBe(mockComponent)
      expect(route.meta.title).toBe('Login | CacaoScan')
      expect(route.meta.requiresGuest).toBe(true)
    })

    it('should have requiresGuest set to true', () => {
      const route = createGuestRoute('/register', 'Register', mockComponent, 'Register')
      expect(route.meta.requiresGuest).toBe(true)
    })

    it('should not include requiresRole or requiresVerification', () => {
      const route = createGuestRoute('/login', 'Login', mockComponent, 'Login')
      expect(route.meta).not.toHaveProperty('requiresRole')
      expect(route.meta).not.toHaveProperty('requiresVerification')
    })
  })
})

