/**
 * Unit tests for authDTOs
 * Tests data normalization functions for authentication
 */

import { describe, it, expect } from 'vitest'
import {
  normalizeLoginResponse,
  normalizeRegisterResponse,
  normalizeUser,
  normalizeAuthError
} from '../authDTOs.js'

describe('authDTOs', () => {
  describe('normalizeLoginResponse', () => {
    it('should normalize login response with data property', () => {
      const rawResponse = {
        data: {
          access: 'access-token',
          refresh: 'refresh-token',
          user: { id: 1, email: 'test@example.com' }
        }
      }
      
      const normalized = normalizeLoginResponse(rawResponse)
      
      expect(normalized.token).toBe('access-token')
      expect(normalized.refresh).toBe('refresh-token')
      expect(normalized.user).toEqual({ id: 1, email: 'test@example.com' })
    })

    it('should normalize login response without data property', () => {
      const rawResponse = {
        access: 'access-token',
        refresh: 'refresh-token',
        user: { id: 1 }
      }
      
      const normalized = normalizeLoginResponse(rawResponse)
      
      expect(normalized.token).toBe('access-token')
    })

    it('should handle token property', () => {
      const rawResponse = {
        data: {
          token: 'token-value',
          refresh: 'refresh-token'
        }
      }
      
      const normalized = normalizeLoginResponse(rawResponse)
      
      expect(normalized.token).toBe('token-value')
    })
  })

  describe('normalizeRegisterResponse', () => {
    it('should normalize registration response', () => {
      const rawResponse = {
        data: {
          email: 'new@example.com',
          verification_required: true
        }
      }
      
      const normalized = normalizeRegisterResponse(rawResponse)
      
      expect(normalized.success).toBe(true)
      expect(normalized.verification_required).toBe(true)
      expect(normalized.email).toBe('new@example.com')
    })

    it('should use userData email if not in response', () => {
      const rawResponse = { data: {} }
      const userData = { email: 'user@example.com' }
      
      const normalized = normalizeRegisterResponse(rawResponse, userData)
      
      expect(normalized.email).toBe('user@example.com')
    })
  })

  describe('normalizeUser', () => {
    it('should normalize user object', () => {
      const rawUser = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'John',
        last_name: 'Doe',
        role: 'farmer',
        is_active: true,
        is_verified: true
      }
      
      const normalized = normalizeUser(rawUser)
      
      expect(normalized.id).toBe(1)
      expect(normalized.email).toBe('test@example.com')
      expect(normalized.username).toBe('testuser')
      expect(normalized.role).toBe('farmer')
    })

    it('should handle alternative field names', () => {
      const rawUser = {
        id: 1,
        email: 'test@example.com',
        primer_nombre: 'John',
        primer_apellido: 'Doe',
        user_role: 'admin'
      }
      
      const normalized = normalizeUser(rawUser)
      
      expect(normalized.first_name).toBe('John')
      expect(normalized.last_name).toBe('Doe')
      expect(normalized.role).toBe('admin')
    })

    it('should return null for null input', () => {
      expect(normalizeUser(null)).toBe(null)
    })

    it('should generate username from email if missing', () => {
      const rawUser = {
        id: 1,
        email: 'testuser@example.com'
      }
      
      const normalized = normalizeUser(rawUser)
      
      expect(normalized.username).toBe('testuser')
    })
  })

  describe('normalizeAuthError', () => {
    it('should normalize error with response data', () => {
      const error = {
        response: {
          status: 401,
          data: {
            detail: 'Invalid credentials'
          }
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.message).toBe('Invalid credentials')
      expect(normalized.type).toBe('authentication')
      expect(normalized.status).toBe(401)
    })

    it('should handle error without response', () => {
      const error = {
        message: 'Network error'
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.message).toBe('Network error')
      expect(normalized.type).toBe('unknown')
    })

    it('should extract field errors', () => {
      const error = {
        response: {
          status: 422,
          data: {
            email: ['Invalid email format'],
            password: ['Password too short']
          }
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.fieldErrors).toBeDefined()
      expect(normalized.fieldErrors.email).toBe('Invalid email format')
    })
  })
})

