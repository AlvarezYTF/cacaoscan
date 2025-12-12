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

    it('should handle access_expires_at and refresh_expires_at', () => {
      const rawResponse = {
        data: {
          access: 'token',
          refresh: 'refresh',
          access_expires_at: 1234567890,
          refresh_expires_at: 1234567891
        }
      }
      
      const normalized = normalizeLoginResponse(rawResponse)
      
      expect(normalized.access_expires_at).toBe(1234567890)
      expect(normalized.refresh_expires_at).toBe(1234567891)
    })

    it('should use default message when not provided', () => {
      const rawResponse = {
        data: {
          access: 'token',
          refresh: 'refresh'
        }
      }
      
      const normalized = normalizeLoginResponse(rawResponse)
      
      expect(normalized.message).toBe('Login exitoso')
    })

    it('should handle user_data property', () => {
      const rawResponse = {
        data: {
          access: 'token',
          user_data: { id: 1, email: 'test@example.com' }
        }
      }
      
      const normalized = normalizeLoginResponse(rawResponse)
      
      expect(normalized.user).toEqual({ id: 1, email: 'test@example.com' })
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

    it('should handle verification_required false', () => {
      const rawResponse = {
        data: {
          verification_required: false
        }
      }
      
      const normalized = normalizeRegisterResponse(rawResponse)
      
      expect(normalized.verification_required).toBe(false)
    })

    it('should default verification_required to true', () => {
      const rawResponse = { data: {} }
      
      const normalized = normalizeRegisterResponse(rawResponse)
      
      expect(normalized.verification_required).toBe(true)
    })

    it('should use custom message when provided', () => {
      const rawResponse = {
        data: {
          message: 'Custom message'
        }
      }
      
      const normalized = normalizeRegisterResponse(rawResponse)
      
      expect(normalized.message).toBe('Custom message')
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

    it('should handle email without @ for username', () => {
      const rawUser = {
        id: 1,
        email: 'noat'
      }
      
      const normalized = normalizeUser(rawUser)
      
      expect(normalized.username).toBe('')
    })

    it('should handle is_active false', () => {
      const rawUser = {
        id: 1,
        email: 'test@example.com',
        is_active: false
      }
      
      const normalized = normalizeUser(rawUser)
      
      expect(normalized.is_active).toBe(false)
    })

    it('should default is_active to true when not provided', () => {
      const rawUser = {
        id: 1,
        email: 'test@example.com'
      }
      
      const normalized = normalizeUser(rawUser)
      
      expect(normalized.is_active).toBe(true)
    })

    it('should handle is_email_verified', () => {
      const rawUser = {
        id: 1,
        email: 'test@example.com',
        is_email_verified: true
      }
      
      const normalized = normalizeUser(rawUser)
      
      expect(normalized.is_verified).toBe(true)
    })

    it('should handle created_at for date_joined', () => {
      const rawUser = {
        id: 1,
        email: 'test@example.com',
        created_at: '2024-01-01'
      }
      
      const normalized = normalizeUser(rawUser)
      
      expect(normalized.date_joined).toBe('2024-01-01')
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

    it('should handle error with error field', () => {
      const error = {
        response: {
          status: 400,
          data: {
            error: 'Error message'
          }
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.message).toBe('Error message')
    })

    it('should handle error with non_field_errors array', () => {
      const error = {
        response: {
          status: 400,
          data: {
            non_field_errors: ['Error 1', 'Error 2']
          }
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.message).toBe('Error 1')
    })

    it('should handle error with non_field_errors string', () => {
      const error = {
        response: {
          status: 400,
          data: {
            non_field_errors: 'Error message'
          }
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.message).toBe('Error message')
    })

    it('should use status message when no error message found', () => {
      const error = {
        response: {
          status: 403,
          data: {}
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.message).toBe('No tienes permisos')
      expect(normalized.type).toBe('validation')
    })

    it('should handle unknown status code', () => {
      const error = {
        response: {
          status: 999,
          data: {}
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.message).toBe('Error de autenticación')
    })

    it('should handle field errors as strings', () => {
      const error = {
        response: {
          status: 422,
          data: {
            email: 'Invalid email'
          }
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.fieldErrors.email).toBe('Invalid email')
    })

    it('should exclude detail, error, and non_field_errors from fieldErrors', () => {
      const error = {
        response: {
          status: 422,
          data: {
            detail: 'Detail',
            error: 'Error',
            non_field_errors: ['Non field'],
            email: ['Email error']
          }
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.fieldErrors.detail).toBeUndefined()
      expect(normalized.fieldErrors.error).toBeUndefined()
      expect(normalized.fieldErrors.non_field_errors).toBeUndefined()
      expect(normalized.fieldErrors.email).toBe('Email error')
    })

    it('should return null fieldErrors when no field errors', () => {
      const error = {
        response: {
          status: 400,
          data: {
            detail: 'Error message'
          }
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.fieldErrors).toBeNull()
    })

    it('should handle error without status', () => {
      const error = {
        response: {
          data: {
            detail: 'Error message'
          }
        }
      }
      
      const normalized = normalizeAuthError(error)
      
      expect(normalized.message).toBe('Error message')
      expect(normalized.status).toBeUndefined()
    })
  })
})

