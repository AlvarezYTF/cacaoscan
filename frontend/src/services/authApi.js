/**
 * Servicio de API para autenticación en CacaoScan
 * Maneja todas las llamadas HTTP relacionadas con autenticación
 * Usa apiClient para reducir duplicación de código
 * Normaliza DTOs para consistencia en el frontend
 */

import { apiPost, apiGet, apiPut, apiPatch, apiDelete } from './apiClient'
import {
  normalizeLoginResponse,
  normalizeRegisterResponse,
  normalizeUser,
  normalizeAuthError
} from './auth/authDTOs'

/**
 * Build login payload from credentials
 * @param {Object} credentials - Login credentials
 * @returns {Object} Login payload
 */
function buildLoginPayload(credentials) {
  const loginData = {
    password: credentials.password
  }
  
  // Priorizar email sobre username
  // Normalizar a lowercase para coincidir con el backend
  if (credentials.email) {
    const normalizedEmail = credentials.email.toLowerCase().trim()
    loginData.email = normalizedEmail
    // El backend puede usar email o username, enviar ambos para compatibilidad
    loginData.username = normalizedEmail
  } else if (credentials.username) {
    const normalizedUsername = credentials.username.toLowerCase().trim()
    loginData.username = normalizedUsername
  }
  
  return loginData
}

/**
 * Build register payload from user data
 * @param {Object} userData - User registration data
 * @returns {Object} Register payload
 */
function buildRegisterPayload(userData) {
  return {
    // Datos del usuario
    email: userData.email,
    password: userData.password,
    
    // Datos de la persona
    tipo_documento: userData.tipo_documento || 'CC',
    numero_documento: userData.numero_documento || '',
    primer_nombre: userData.first_name || userData.primer_nombre || '',
    segundo_nombre: userData.segundo_nombre || userData.middle_name || '',
    primer_apellido: userData.last_name || userData.primer_apellido || '',
    segundo_apellido: userData.segundo_apellido || userData.last_name_2 || '',
    telefono: userData.phone_number || userData.telefono || '',
    direccion: userData.direccion || userData.address || '',
    genero: userData.genero || 'M',
    fecha_nacimiento: userData.fecha_nacimiento || userData.birthdate || '',
    municipio: userData.municipio || '',
    departamento: userData.departamento || ''
  }
}

const authApi = {
  /**
   * Iniciar sesión con email/username y contraseña
   * @param {Object} credentials - Login credentials
   * @returns {Promise<Object>} Normalized login response
   */
  async login(credentials) {
    try {
      const loginData = buildLoginPayload(credentials)
      const response = await apiPost('/auth/login/', loginData)
      return normalizeLoginResponse(response)
    } catch (error) {
      const normalizedError = normalizeAuthError(error)
      // Create a new Error with the message so it can be properly caught
      const authError = new Error(normalizedError.message)
      authError.type = normalizedError.type
      authError.status = normalizedError.status
      authError.fieldErrors = normalizedError.fieldErrors
      authError.response = error.response // Preserve original response
      throw authError
    }
  },

  /**
   * Registrar nuevo usuario con información de persona
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} Normalized registration response
   */
  async register(userData) {
    try {
      const payload = buildRegisterPayload(userData)
      const response = await apiPost('/personas/registrar/', payload)
      return normalizeRegisterResponse(response, userData)
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Cerrar sesión (blacklist refresh token)
   * @returns {Promise<Object>} Logout response
   */
  async logout() {
    try {
      return await apiPost('/auth/logout/')
    } catch (error) {
      // Don't throw on logout errors - always allow logout
      return { success: true }
    }
  },

  /**
   * Refrescar token de acceso usando refresh token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} New token response
   */
  async refreshToken(refreshToken) {
    try {
      const response = await apiPost('/auth/refresh/', {
        refresh: refreshToken
      })
      
      return {
        access: response.access || response.token,
        refresh: response.refresh,
        access_expires_at: response.access_expires_at || null,
        refresh_expires_at: response.refresh_expires_at || null
      }
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Alias para refreshToken (mantiene compatibilidad)
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} New token response
   */
  async refreshAccessToken(refreshToken) {
    return this.refreshToken(refreshToken)
  },

  /**
   * Verificar token (comprobar si es válido)
   * @param {string} token - Token to verify
   * @returns {Promise<Object>} Verification response
   */
  async verifyToken(token) {
    try {
      return await apiPost('/auth/verify/', { token })
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Obtener información del usuario actual
   * @returns {Promise<Object>} User profile
   */
  async getCurrentUser() {
    try {
      const response = await apiGet('/auth/profile/')
      return normalizeUser(response.user || response)
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Obtener perfil del usuario actual
   * @returns {Promise<Object>} User profile
   */
  async getProfile() {
    return this.getCurrentUser()
  },

  /**
   * Actualizar información del usuario actual
   * @param {Object} profileData - Profile data to update
   * @returns {Promise<Object>} Updated profile
   */
  async updateProfile(profileData) {
    try {
      const payload = {
        first_name: profileData.firstName || profileData.fullName?.split(' ')[0] || '',
        last_name: profileData.lastName || profileData.fullName?.split(' ').slice(1).join(' ') || ''
      }
      
      if (profileData.phoneNumber || profileData.phone) {
        payload.phone_number = profileData.phoneNumber || profileData.phone
      }
      
      const response = await apiPut('/auth/profile/', payload)
      return normalizeUser(response.user || response)
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Cambiar contraseña del usuario actual
   * @param {Object} passwordData - Password change data
   * @returns {Promise<Object>} Change response
   */
  async changePassword(passwordData) {
    try {
      return await apiPost('/auth/change-password/', {
        old_password: passwordData.oldPassword,
        new_password: passwordData.newPassword,
        confirm_password: passwordData.confirmPassword
      })
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Solicitar restablecimiento de contraseña
   * @param {string} email - User email
   * @returns {Promise<Object>} Reset request response
   */
  async requestPasswordReset(email) {
    try {
      return await apiPost('/auth/forgot-password/', { email })
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Confirmar restablecimiento de contraseña
   * @param {Object} resetData - Password reset data
   * @returns {Promise<Object>} Reset response
   */
  async confirmPasswordReset(resetData) {
    try {
      return await apiPost('/auth/reset-password/', {
        uid: resetData.uid,
        token: resetData.token,
        new_password: resetData.newPassword,
        confirm_password: resetData.confirmPassword
      })
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Verificar email con token (POST con token en body)
   * @param {string} uid - User ID
   * @param {string} token - Verification token
   * @returns {Promise<Object>} Verification response
   */
  async verifyEmail(uid, token) {
    try {
      return await apiPost('/auth/verify-email/', { uid, token })
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Verificar email con token desde la URL (GET con token en path)
   * @param {string} token - Verification token
   * @returns {Promise<Object>} Verification response
   */
  async verifyEmailFromToken(token) {
    try {
      return await apiGet(`/auth/verify-email/${token}/`)
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Reenviar email de verificación
   * @param {string|null} email - User email (optional)
   * @returns {Promise<Object>} Resend response
   */
  async resendEmailVerification(email = null) {
    try {
      const payload = email ? { email } : {}
      return await apiPost('/auth/resend-verification/', payload)
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Obtener estadísticas de usuarios (solo admin)
   * @returns {Promise<Object>} User statistics
   */
  async getUserStats() {
    try {
      return await apiGet('/auth/admin/stats/')
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Realizar acciones masivas en usuarios (solo admin)
   * @param {Object} actionData - Action data
   * @returns {Promise<Object>} Bulk action response
   */
  async bulkUserActions(actionData) {
    try {
      return await apiPost('/auth/admin/bulk-actions/', {
        user_ids: actionData.userIds,
        action: actionData.action
      })
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Obtener lista de usuarios (admin/analyst)
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Users list response
   */
  async getUsers(params = {}) {
    try {
      const response = await apiGet('/auth/users/', params)
      return {
        results: (response.results || []).map(user => normalizeUser(user)),
        count: response.count || 0,
        page: response.page || params.page || 1,
        page_size: response.page_size || params.page_size || 50,
        total_pages: response.total_pages || Math.ceil((response.count || 0) / (response.page_size || params.page_size || 50))
      }
    } catch (error) {
      // Fallback suave para no bloquear la UI si el backend responde 500
      if (error.status === 500) {
        return { results: [], count: 0, page: 1, page_size: 50, total_pages: 1 }
      }
      throw normalizeAuthError(error)
    }
  },

  /**
   * Obtener un usuario específico por ID (admin/analyst)
   * @param {number} userId - User ID
   * @returns {Promise<Object>} User object
   */
  async getUser(userId) {
    try {
      const response = await apiGet(`/auth/users/${userId}/`)
      return normalizeUser(response.user || response)
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Actualizar usuario específico (admin)
   * @param {number} userId - User ID
   * @param {Object} userData - User data to update
   * @returns {Promise<Object>} Updated user
   */
  async updateUser(userId, userData) {
    try {
      const response = await apiPatch(`/auth/users/${userId}/update/`, userData)
      return normalizeUser(response.user || response)
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Eliminar usuario (admin)
   * @param {number} userId - User ID
   * @returns {Promise<Object>} Delete response
   */
  async deleteUser(userId) {
    try {
      return await apiDelete(`/auth/users/${userId}/delete/`)
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Cambiar estado de usuario (activo/inactivo)
   * @param {number} userId - User ID
   * @param {boolean} isActive - Active status
   * @returns {Promise<Object>} Updated user
   */
  async toggleUserStatus(userId, isActive) {
    try {
      const response = await apiPatch(`/auth/users/${userId}/update/`, {
        is_active: isActive
      })
      return normalizeUser(response.user || response)
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Solicitar recuperación de contraseña (alias)
   * @param {string} email - User email
   * @returns {Promise<Object>} Reset request response
   */
  async forgotPassword(email) {
    return this.requestPasswordReset(email)
  },

  /**
   * Restablecer contraseña con token (alias)
   * @param {string} token - Reset token
   * @param {string} newPassword - New password
   * @param {string} confirmPassword - Password confirmation
   * @returns {Promise<Object>} Reset response
   */
  async resetPassword(token, newPassword, confirmPassword) {
    return this.confirmPasswordReset({
      token,
      newPassword,
      confirmPassword
    })
  },

  /**
   * Enviar código OTP para verificación de email
   * @param {string} email - User email
   * @returns {Promise<Object>} OTP send response
   */
  async sendOtp(email) {
    try {
      return await apiPost('/auth/send-otp/', { email })
    } catch (error) {
      throw normalizeAuthError(error)
    }
  },

  /**
   * Verificar código OTP
   * @param {string} email - User email
   * @param {string} code - OTP code
   * @returns {Promise<Object>} OTP verification response
   */
  async verifyOtp(email, code) {
    try {
      return await apiPost('/auth/verify-otp/', { email, code })
    } catch (error) {
      throw normalizeAuthError(error)
    }
  }
}

export default authApi
