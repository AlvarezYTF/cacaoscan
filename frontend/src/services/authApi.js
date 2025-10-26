/**
 * Servicio de API para autenticación en CacaoScan
 * Maneja todas las llamadas HTTP relacionadas con autenticación
 */

import api from './api'

const authApi = {
  /**
   * Iniciar sesión con email/username y contraseña
   */
  async login(credentials) {
    try {
      // Enviar email si está disponible, de lo contrario username
      const loginData = {
        password: credentials.password
      }
      
      // Priorizar email sobre username
      if (credentials.email) {
        loginData.email = credentials.email
        loginData.username = credentials.email
      } else if (credentials.username) {
        loginData.username = credentials.username
      }
      
      const response = await api.post('/auth/login/', loginData)
      
      console.log('🔍 [authApi] Respuesta cruda del backend:', response.data)
      
      // El backend puede devolver dos estructuras:
      // 1. { success, data: { access, refresh, user, ... }, message } (con wrapper)
      // 2. { success, access, refresh, user, ..., message } (plana)
      
      let normalizedData;
      
      if (response.data && response.data.data) {
        // Estructura con wrapper 'data'
        normalizedData = {
          token: response.data.data.access,
          refresh: response.data.data.refresh,
          user: response.data.data.user,
          access_expires_at: response.data.data.access_expires_at,
          refresh_expires_at: response.data.data.refresh_expires_at,
          message: response.data.message
        }
      } else if (response.data && response.data.access && response.data.user) {
        // Estructura plana (la que realmente usa el backend)
        normalizedData = {
          token: response.data.access,
          refresh: response.data.refresh,
          user: response.data.user,
          access_expires_at: response.data.access_expires_at,
          refresh_expires_at: response.data.refresh_expires_at,
          message: response.data.message
        }
      } else {
        console.error('❌ [authApi] Estructura de respuesta inesperada:', response.data)
        throw new Error('Respuesta del servidor con formato inválido')
      }
      
      console.log('✅ [authApi] Datos normalizados para el store:', normalizedData)
      return normalizedData
    } catch (error) {
      console.error('Error en login API:', error)
      throw error
    }
  },

  /**
   * Registrar nuevo usuario
   */
  async register(userData) {
    try {
      console.log('🔍 [authApi] Datos recibidos para registro:', userData);
      
      const payload = {
        username: userData.email, // Usar email como username
        email: userData.email,
        password: userData.password,
        password_confirm: userData.password_confirm, // Usar password_confirm correctamente
        first_name: userData.first_name,
        last_name: userData.last_name
      };
      
      console.log('📤 [authApi] Payload enviado al backend:', payload);
      
      const response = await api.post('/auth/register/', payload)
      
      console.log('🔍 [authApi] Respuesta cruda del backend (registro):', response.data)
      
      // El backend puede devolver dos estructuras:
      // 1. { success, data: { access, refresh, user, ... }, message } (con wrapper)
      // 2. { success, access, refresh, user, ..., message } (plana)
      
      let normalizedData;
      
      if (response.data && response.data.data) {
        // Estructura con wrapper 'data'
        normalizedData = {
          token: response.data.data.access,
          refresh: response.data.data.refresh,
          user: response.data.data.user,
          access_expires_at: response.data.data.access_expires_at,
          refresh_expires_at: response.data.data.refresh_expires_at,
          verification_token: response.data.data.verification_token,
          verification_required: response.data.data.verification_required,
          message: response.data.message
        }
      } else if (response.data && response.data.access && response.data.user) {
        // Estructura plana (la que realmente usa el backend)
        normalizedData = {
          token: response.data.access,
          refresh: response.data.refresh,
          user: response.data.user,
          access_expires_at: response.data.access_expires_at,
          refresh_expires_at: response.data.refresh_expires_at,
          verification_token: response.data.verification_token,
          verification_required: response.data.verification_required,
          message: response.data.message
        }
      } else {
        console.error('❌ [authApi] Estructura de respuesta inesperada:', response.data)
        throw new Error('Respuesta del servidor con formato inválido')
      }
      
      console.log('✅ [authApi] Datos normalizados para el store (registro):', normalizedData)
      return normalizedData
    } catch (error) {
      console.error('Error en registro API:', error)
      throw error
    }
  },

  /**
   * Cerrar sesión (blacklist refresh token)
   */
  async logout() {
    try {
      const response = await api.post('/auth/logout/')
      return response.data
    } catch (error) {
      console.error('Error en logout API:', error)
      throw error
    }
  },

  /**
   * Refrescar token de acceso
   */
  async refreshToken(refreshToken) {
    try {
      const response = await api.post('/auth/refresh/', {
        refresh: refreshToken
      })
      return response.data
    } catch (error) {
      console.error('Error refrescando token:', error)
      throw error
    }
  },

  /**
   * Verificar token (comprobar si es válido)
   */
  async verifyToken(token) {
    try {
      const response = await api.post('/auth/verify/', {
        token: token
      })
      return response.data
    } catch (error) {
      console.error('Error verificando token:', error)
      throw error
    }
  },

  /**
   * Obtener información del usuario actual
   */
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/profile/')
      return response.data
    } catch (error) {
      console.error('Error obteniendo usuario actual:', error)
      throw error
    }
  },

  /**
   * Actualizar información del usuario actual
   */
  async updateProfile(profileData) {
    try {
      const response = await api.patch('/auth/users/me/update/', {
        first_name: profileData.firstName,
        last_name: profileData.lastName,
        phone_number: profileData.phoneNumber,
        // Datos del perfil
        region: profileData.region,
        municipality: profileData.municipality,
        farm_name: profileData.farmName,
        years_experience: profileData.yearsExperience,
        farm_size_hectares: profileData.farmSizeHectares,
        preferred_language: profileData.preferredLanguage,
        email_notifications: profileData.emailNotifications
      })
      return response.data
    } catch (error) {
      console.error('Error actualizando perfil:', error)
      throw error
    }
  },

  /**
   * Cambiar contraseña del usuario actual
   */
  async changePassword(passwordData) {
    try {
      const response = await api.post('/auth/users/change-password/', {
        old_password: passwordData.oldPassword,
        new_password: passwordData.newPassword,
        confirm_password: passwordData.confirmPassword
      })
      return response.data
    } catch (error) {
      console.error('Error cambiando contraseña:', error)
      throw error
    }
  },

  /**
   * Solicitar restablecimiento de contraseña
   */
  async requestPasswordReset(email) {
    try {
      const response = await api.post('/auth/forgot-password/', {
        email: email
      })
      return response.data
    } catch (error) {
      console.error('Error solicitando reset de contraseña:', error)
      throw error
    }
  },

  /**
   * Confirmar restablecimiento de contraseña
   */
  async confirmPasswordReset(resetData) {
    try {
      const response = await api.post('/auth/reset-password/', {
        uid: resetData.uid,
        token: resetData.token,
        new_password: resetData.newPassword,
        confirm_password: resetData.confirmPassword
      })
      return response.data
    } catch (error) {
      console.error('Error confirmando reset de contraseña:', error)
      throw error
    }
  },

  /**
   * Verificar email con token
   */
  async verifyEmail(uid, token) {
    try {
      const response = await api.post('/auth/verify-email/', {
        uid: uid,
        token: token
      })
      return response.data
    } catch (error) {
      console.error('Error verificando email:', error)
      throw error
    }
  },

  /**
   * Reenviar email de verificación
   */
  async resendEmailVerification() {
    try {
      const response = await api.post('/auth/resend-verification/')
      return response.data
    } catch (error) {
      console.error('Error reenviando verificación:', error)
      throw error
    }
  },

  /**
   * Obtener estadísticas de usuarios (solo admin)
   */
  async getUserStats() {
    try {
      const response = await api.get('/auth/admin/stats/')
      return response.data
    } catch (error) {
      console.error('Error obteniendo estadísticas:', error)
      throw error
    }
  },

  /**
   * Realizar acciones masivas en usuarios (solo admin)
   */
  async bulkUserActions(actionData) {
    try {
      const response = await api.post('/auth/admin/bulk-actions/', {
        user_ids: actionData.userIds,
        action: actionData.action
      })
      return response.data
    } catch (error) {
      console.error('Error en acciones masivas:', error)
      throw error
    }
  },

  /**
   * Obtener lista de usuarios (admin/analyst)
   */
  async getUsers(params = {}) {
    try {
      const response = await api.get('/auth/users/', { params })
      return response.data
    } catch (error) {
      console.error('Error obteniendo usuarios:', error)
      throw error
    }
  },

  /**
   * Obtener un usuario específico por ID (admin/analyst)
   */
  async getUser(userId) {
    try {
      const response = await api.get(`/auth/users/${userId}/`)
      return response.data
    } catch (error) {
      console.error('Error obteniendo usuario:', error)
      throw error
    }
  },

  /**
   * Actualizar usuario específico (admin)
   */
  async updateUser(userId, userData) {
    try {
      const response = await api.patch(`/auth/users/${userId}/update/`, userData)
      return response.data
    } catch (error) {
      console.error('Error actualizando usuario:', error)
      throw error
    }
  },

  /**
   * Eliminar usuario (admin)
   */
  async deleteUser(userId) {
    try {
      const response = await api.delete(`/auth/users/${userId}/delete/`)
      return response.data
    } catch (error) {
      console.error('Error eliminando usuario:', error)
      throw error
    }
  },

  /**
   * Cambiar estado de usuario (activo/inactivo)
   */
  async toggleUserStatus(userId, isActive) {
    try {
      const response = await api.patch(`/auth/users/${userId}/update/`, {
        is_active: isActive
      })
      return response.data
    } catch (error) {
      console.error('Error cambiando estado de usuario:', error)
      throw error
    }
  },

  /**
   * Solicitar recuperación de contraseña
   */
  async forgotPassword(email) {
    try {
      const response = await api.post('/auth/forgot-password/', {
        email: email
      })
      return response.data
    } catch (error) {
      console.error('Error en forgot password API:', error)
      throw error
    }
  },

  /**
   * Restablecer contraseña con token
   */
  async resetPassword(token, newPassword, confirmPassword) {
    try {
      const response = await api.post('/auth/reset-password/', {
        token: token,
        new_password: newPassword,
        confirm_password: confirmPassword
      })
      return response.data
    } catch (error) {
      console.error('Error en reset password API:', error)
      throw error
    }
  }
}

export default authApi
