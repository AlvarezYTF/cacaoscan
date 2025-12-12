/**
 * Unit tests for useAdminSidebarProps composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAdminSidebarProps } from '../useAdminSidebarProps.js'

// Mock dependencies
const mockAuthStore = {
  user: {
    first_name: 'John',
    last_name: 'Doe',
    username: 'johndoe',
    is_superuser: false
  }
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

describe('useAdminSidebarProps', () => {
  let props

  beforeEach(() => {
    props = useAdminSidebarProps()
  })

  describe('brandName', () => {
    it('should return CacaoScan', () => {
      expect(props.brandName.value).toBe('CacaoScan')
    })
  })

  describe('userName', () => {
    it('should return full name when available', () => {
      expect(props.userName.value).toBe('John Doe')
    })

    it('should return username when name not available', () => {
      mockAuthStore.user = { username: 'johndoe' }
      
      // Re-create to get new computed
      const newProps = useAdminSidebarProps()
      
      expect(newProps.userName.value).toBe('johndoe')
    })

    it('should return default when no user data', () => {
      mockAuthStore.user = null
      
      const newProps = useAdminSidebarProps()
      
      expect(newProps.userName.value).toBe('Usuario')
    })
  })

  describe('userRole', () => {
    it('should return Administrador for superuser', () => {
      mockAuthStore.user = { is_superuser: true }
      
      const newProps = useAdminSidebarProps()
      
      expect(newProps.userRole.value).toBe('Administrador')
    })

    it('should return Analista for non-superuser', () => {
      mockAuthStore.user = { is_superuser: false }
      
      const newProps = useAdminSidebarProps()
      
      expect(newProps.userRole.value).toBe('Analista')
    })
  })
})

