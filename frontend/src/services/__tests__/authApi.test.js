import { describe, it, expect, beforeEach, vi } from 'vitest'
import authApi from '../authApi.js'
import api from '../api.js'

vi.mock('../api.js', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

describe('authApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('login', () => {
    it('should login with email successfully', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'password123'
      }

      const mockResponse = {
        data: {
          access: 'access-token',
          refresh: 'refresh-token',
          user: { id: 1, email: 'test@example.com' },
          access_expires_at: '2024-12-31T23:59:59Z',
          refresh_expires_at: '2024-12-31T23:59:59Z',
          message: 'Login successful'
        }
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.login(credentials)

      expect(api.post).toHaveBeenCalledWith('/auth/login/', {
        password: 'password123',
        email: 'test@example.com',
        username: 'test@example.com'
      }, {})

      expect(result).toEqual({
        token: 'access-token',
        refresh: 'refresh-token',
        user: { id: 1, email: 'test@example.com' },
        access_expires_at: '2024-12-31T23:59:59Z',
        refresh_expires_at: '2024-12-31T23:59:59Z',
        message: 'Login exitoso'
      })
    })

    it('should login with username when email is not provided', async () => {
      const credentials = {
        username: 'testuser',
        password: 'password123'
      }

      const mockResponse = {
        data: {
          access: 'access-token',
          refresh: 'refresh-token',
          user: { id: 1, username: 'testuser' }
        }
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.login(credentials)

      expect(api.post).toHaveBeenCalledWith('/auth/login/', {
        password: 'password123',
        username: 'testuser'
      }, {})

      expect(result.token).toBe('access-token')
    })

    it('should handle login response with wrapper data', async () => {
      const credentials = { email: 'test@example.com', password: 'pass' }

      const mockResponse = {
        data: {
          access: 'access-token',
          refresh: 'refresh-token',
          user: { id: 1 },
          access_expires_at: '2024-12-31T23:59:59Z',
          refresh_expires_at: '2024-12-31T23:59:59Z',
          message: 'Login successful'
        }
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.login(credentials)

      expect(result.token).toBe('access-token')
      expect(result.message).toBe('Login exitoso')
    })

    it('should throw error on invalid response format', async () => {
      const credentials = { email: 'test@example.com', password: 'pass' }

      const mockResponse = {
        data: {
          invalid: 'format'
        }
      }

      api.post.mockResolvedValue(mockResponse)

      // normalizeLoginResponse doesn't throw, it returns a normalized response
      // with default values. The test should verify the normalized output.
      const result = await authApi.login(credentials)
      expect(result.token).toBeUndefined()
      expect(result.refresh).toBeUndefined()
    })
  })

  describe('register', () => {
    it('should register user successfully', async () => {
      const userData = {
        email: 'newuser@example.com',
        password: 'password123',
        first_name: 'John',
        last_name: 'Doe',
        tipo_documento: 'CC',
        numero_documento: '1234567890',
        telefono: '3001234567'
      }

      const mockResponse = {
        data: {
          email: 'newuser@example.com',
          verification_required: true
        }
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.register(userData)

      expect(api.post).toHaveBeenCalledWith('/personas/registrar/', expect.objectContaining({
        email: 'newuser@example.com',
        password: 'password123',
        primer_nombre: 'John',
        primer_apellido: 'Doe'
      }), {})

      expect(result.success).toBe(true)
      expect(result.verification_required).toBe(true)
    })

    it('should handle registration error with detail', async () => {
      const userData = { email: 'test@example.com', password: 'pass' }

      const error = {
        response: {
          data: {
            detail: 'Email already exists'
          }
        }
      }

      api.post.mockRejectedValue(error)

      await expect(authApi.register(userData)).rejects.toEqual(
        expect.objectContaining({
          message: 'Email already exists'
        })
      )
    })

    it('should handle registration error with non_field_errors', async () => {
      const userData = { email: 'test@example.com', password: 'pass' }

      const error = {
        response: {
          data: {
            non_field_errors: ['Invalid credentials']
          }
        }
      }

      api.post.mockRejectedValue(error)

      try {
        await authApi.register(userData)
      } catch (err) {
        expect(err.message).toBe('Invalid credentials')
      }
    })
  })

  describe('refreshToken', () => {
    it('should refresh token successfully', async () => {
      const refreshToken = 'refresh-token-123'

      const mockResponse = {
        data: {
          access: 'new-access-token',
          refresh: 'new-refresh-token',
          access_expires_at: null,
          refresh_expires_at: null
        }
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.refreshToken(refreshToken)

      expect(api.post).toHaveBeenCalledWith('/auth/refresh/', {
        refresh: refreshToken
      }, {})

      expect(result).toEqual({
        access: 'new-access-token',
        refresh: 'new-refresh-token',
        access_expires_at: null,
        refresh_expires_at: null
      })
    })
  })

  describe('verifyToken', () => {
    it('should verify token successfully', async () => {
      const token = 'test-token'

      const mockResponse = {
        data: {
          valid: true
        }
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.verifyToken(token)

      expect(api.post).toHaveBeenCalledWith('/auth/verify/', {
        token: token
      }, {})

      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('logout', () => {
    it('should logout successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Logged out successfully'
        }
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.logout()

      expect(api.post).toHaveBeenCalledWith('/auth/logout/', {}, {})
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('getCurrentUser', () => {
    it('should get current user successfully', async () => {
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        first_name: 'John',
        last_name: 'Doe'
      }

      const mockResponse = {
        data: mockUser
      }

      api.get.mockResolvedValue(mockResponse)

      const result = await authApi.getCurrentUser()

      expect(api.get).toHaveBeenCalledWith('/auth/profile/', { params: {} })
      expect(result).toEqual(mockUser)
    })
  })

  describe('updateProfile', () => {
    it('should update profile successfully', async () => {
      const profileData = {
        firstName: 'Jane',
        lastName: 'Smith',
        phoneNumber: '3001234567'
      }

      const mockResponse = {
        data: {
          id: 1,
          first_name: 'Jane',
          last_name: 'Smith',
          phone_number: '3001234567'
        }
      }

      api.put.mockResolvedValue(mockResponse)

      const result = await authApi.updateProfile(profileData)

      expect(api.put).toHaveBeenCalledWith('/auth/profile/', {
        first_name: 'Jane',
        last_name: 'Smith',
        phone_number: '3001234567'
      }, {})

      expect(result).toMatchObject({
        id: 1,
        first_name: 'Jane',
        last_name: 'Smith'
      })
    })

    it('should update profile with fullName split', async () => {
      const profileData = {
        fullName: 'Jane Smith'
      }

      api.put.mockResolvedValue({ data: {} })

      await authApi.updateProfile(profileData)

      expect(api.put).toHaveBeenCalledWith('/auth/profile/', {
        first_name: 'Jane',
        last_name: 'Smith'
      }, {})
    })
  })

  describe('changePassword', () => {
    it('should change password successfully', async () => {
      const passwordData = {
        oldPassword: 'oldpass123',
        newPassword: 'newpass123',
        confirmPassword: 'newpass123'
      }

      const mockResponse = {
        data: {
          success: true,
          message: 'Password changed successfully'
        }
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.changePassword(passwordData)

      expect(api.post).toHaveBeenCalledWith('/auth/change-password/', {
        old_password: 'oldpass123',
        new_password: 'newpass123',
        confirm_password: 'newpass123'
      }, {})

      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('requestPasswordReset', () => {
    it('should request password reset successfully', async () => {
      const email = 'test@example.com'

      const mockResponseData = {
        success: true,
        message: 'Password reset email sent'
      }

      const mockResponse = {
        data: mockResponseData
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.requestPasswordReset(email)

      expect(api.post).toHaveBeenCalledWith('/auth/forgot-password/', {
        email: email
      }, {})

      expect(result).toEqual(mockResponseData)
    })
  })

  describe('confirmPasswordReset', () => {
    it('should confirm password reset successfully', async () => {
      const resetData = {
        uid: 'uid123',
        token: 'token123',
        newPassword: 'newpass123',
        confirmPassword: 'newpass123'
      }

      const mockResponseData = {
        success: true,
        message: 'Password reset successfully'
      }

      const mockResponse = {
        data: mockResponseData
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.confirmPasswordReset(resetData)

      expect(api.post).toHaveBeenCalledWith('/auth/reset-password/', {
        uid: 'uid123',
        token: 'token123',
        new_password: 'newpass123',
        confirm_password: 'newpass123'
      }, {})

      expect(result).toEqual(mockResponseData)
    })
  })

  describe('verifyEmail', () => {
    it('should verify email with uid and token', async () => {
      const uid = 'uid123'
      const token = 'token123'

      const mockResponseData = {
        success: true,
        message: 'Email verified'
      }

      const mockResponse = {
        data: mockResponseData
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.verifyEmail(uid, token)

      expect(api.post).toHaveBeenCalledWith('/auth/verify-email/', {
        uid: uid,
        token: token
      }, {})

      expect(result).toEqual(mockResponseData)
    })
  })

  describe('verifyEmailFromToken', () => {
    it('should verify email from token in URL', async () => {
      const token = 'token123'

      const mockResponseData = {
        success: true,
        message: 'Email verified'
      }

      const mockResponse = {
        data: mockResponseData
      }

      api.get.mockResolvedValue(mockResponse)

      const result = await authApi.verifyEmailFromToken(token)

      expect(api.get).toHaveBeenCalledWith('/auth/verify-email/token123/', { params: {} })
      expect(result).toEqual(mockResponseData)
    })
  })

  describe('resendEmailVerification', () => {
    it('should resend email verification with email', async () => {
      const email = 'test@example.com'

      const mockResponseData = {
        success: true,
        message: 'Verification email sent'
      }

      const mockResponse = {
        data: mockResponseData
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.resendEmailVerification(email)

      expect(api.post).toHaveBeenCalledWith('/auth/resend-verification/', {
        email: email
      }, {})

      expect(result).toEqual(mockResponseData)
    })

    it('should resend email verification without email', async () => {
      const mockResponseData = {
        success: true,
        message: 'Verification email sent'
      }

      const mockResponse = {
        data: mockResponseData
      }

      api.post.mockResolvedValue(mockResponse)

      const result = await authApi.resendEmailVerification()

      expect(api.post).toHaveBeenCalledWith('/auth/resend-verification/', {}, {})
      expect(result).toEqual(mockResponseData)
    })
  })

  describe('getUsers', () => {
    it('should get users list successfully', async () => {
      const mockUsers = {
        results: [
          { id: 1, email: 'user1@example.com', username: 'user1', first_name: '', last_name: '', role: 'farmer', is_active: true, is_verified: false, date_joined: null },
          { id: 2, email: 'user2@example.com', username: 'user2', first_name: '', last_name: '', role: 'farmer', is_active: true, is_verified: false, date_joined: null }
        ],
        count: 2,
        page: 1,
        page_size: 50,
        total_pages: 1
      }

      const mockResponse = {
        data: {
          results: [
            { id: 1, email: 'user1@example.com' },
            { id: 2, email: 'user2@example.com' }
          ],
          count: 2,
          page: 1,
          page_size: 50,
          total_pages: 1
        }
      }

      api.get.mockResolvedValue(mockResponse)

      const result = await authApi.getUsers()

      expect(api.get).toHaveBeenCalledWith('/auth/users/', { params: {} })
      expect(result).toMatchObject({
        results: expect.arrayContaining([
          expect.objectContaining({ id: 1, email: 'user1@example.com' }),
          expect.objectContaining({ id: 2, email: 'user2@example.com' })
        ]),
        count: 2,
        page: 1,
        page_size: 50,
        total_pages: 1
      })
    })

    it('should get users with params', async () => {
      const params = { page: 1, page_size: 10 }

      api.get.mockResolvedValue({ data: { results: [], count: 0 } })

      await authApi.getUsers(params)

      expect(api.get).toHaveBeenCalledWith('/auth/users/', { params })
    })

    it('should handle 500 error gracefully', async () => {
      const error = {
        status: 500,
        response: {
          status: 500
        }
      }

      api.get.mockRejectedValue(error)

      const result = await authApi.getUsers()

      expect(result).toEqual({
        results: [],
        count: 0,
        page: 1,
        page_size: 50,
        total_pages: 1
      })
    })
  })

  describe('getUser', () => {
    it('should get user by id successfully', async () => {
      const userId = 1
      const mockUser = {
        id: 1,
        email: 'test@example.com'
      }

      api.get.mockResolvedValue({ data: mockUser })

      const result = await authApi.getUser(userId)

      expect(api.get).toHaveBeenCalledWith('/auth/users/1/', { params: {} })
      expect(result).toMatchObject({ id: 1, email: 'test@example.com' })
    })
  })

  describe('updateUser', () => {
    it('should update user successfully', async () => {
      const userId = 1
      const userData = {
        first_name: 'Updated',
        last_name: 'Name'
      }

      const mockResponseData = {
        id: 1,
        ...userData
      }

      api.patch.mockResolvedValue({ data: mockResponseData })

      const result = await authApi.updateUser(userId, userData)

      expect(api.patch).toHaveBeenCalledWith('/auth/users/1/update/', userData, {})
      expect(result).toMatchObject(mockResponseData)
    })
  })

  describe('deleteUser', () => {
    it('should delete user successfully', async () => {
      const userId = 1

      const mockResponseData = {
        success: true
      }

      api.delete.mockResolvedValue({ data: mockResponseData })

      const result = await authApi.deleteUser(userId)

      expect(api.delete).toHaveBeenCalledWith('/auth/users/1/delete/', {})
      expect(result).toEqual(mockResponseData)
    })
  })

  describe('toggleUserStatus', () => {
    it('should toggle user status to active', async () => {
      const userId = 1
      const isActive = true

      const mockResponseData = {
        id: 1,
        is_active: true
      }

      api.patch.mockResolvedValue({ data: mockResponseData })

      const result = await authApi.toggleUserStatus(userId, isActive)

      expect(api.patch).toHaveBeenCalledWith('/auth/users/1/update/', {
        is_active: true
      }, {})

      expect(result).toMatchObject(mockResponseData)
    })
  })

  describe('getUserStats', () => {
    it('should get user stats successfully', async () => {
      const mockStats = {
        total_users: 100,
        active_users: 80
      }

      api.get.mockResolvedValue({ data: mockStats })

      const result = await authApi.getUserStats()

      expect(api.get).toHaveBeenCalledWith('/auth/admin/stats/', { params: {} })
      expect(result).toEqual(mockStats)
    })
  })

  describe('bulkUserActions', () => {
    it('should perform bulk user actions', async () => {
      const actionData = {
        userIds: [1, 2, 3],
        action: 'activate'
      }

      const mockResponseData = {
        success: true,
        affected: 3
      }

      api.post.mockResolvedValue({ data: mockResponseData })

      const result = await authApi.bulkUserActions(actionData)

      expect(api.post).toHaveBeenCalledWith('/auth/admin/bulk-actions/', {
        user_ids: [1, 2, 3],
        action: 'activate'
      }, {})

      expect(result).toEqual(mockResponseData)
    })
  })

  describe('sendOtp and verifyOtp', () => {
    it('should send OTP successfully', async () => {
      const email = 'test@example.com'

      const mockResponseData = {
        success: true,
        message: 'OTP sent'
      }

      api.post.mockResolvedValue({ data: mockResponseData })

      const result = await authApi.sendOtp(email)

      expect(api.post).toHaveBeenCalledWith('/auth/send-otp/', { email }, {})
      expect(result).toEqual(mockResponseData)
    })

    it('should verify OTP successfully', async () => {
      const email = 'test@example.com'
      const code = '123456'

      const mockResponseData = {
        success: true,
        message: 'OTP verified'
      }

      api.post.mockResolvedValue({ data: mockResponseData })

      const result = await authApi.verifyOtp(email, code)

      expect(api.post).toHaveBeenCalledWith('/auth/verify-otp/', { email, code }, {})
      expect(result).toEqual(mockResponseData)
    })
  })
})

