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
   * Registrar nuevo usuario con información de persona
   * Usa el nuevo endpoint /personas/registrar/ que crea User + Persona
   */
  async register(userData) {
    try {
      console.log('🔍 [authApi] Datos recibidos para registro:', userData);
      
      // Payload para el nuevo endpoint de personas
      const payload = {
        // Datos del usuario
        email: userData.email,
        password: userData.password,
        
        // Datos de la persona
        tipo_documento: userData.tipo_documento || 'CC', // Por defecto Cédula
        numero_documento: userData.numero_documento || '',
        primer_nombre: userData.first_name || userData.primer_nombre || '',
        segundo_nombre: userData.segundo_nombre || userData.middle_name || '',
        primer_apellido: userData.last_name || userData.primer_apellido || '',
        segundo_apellido: userData.segundo_apellido || userData.last_name_2 || '',
        telefono: userData.phone_number || userData.telefono || '',
        direccion: userData.direccion || userData.address || '',
        genero: userData.genero || 'M', // Por defecto Masculino
        fecha_nacimiento: userData.fecha_nacimiento || userData.birthdate || '',
        municipio: userData.municipio || '',
        departamento: userData.departamento || ''
      };
      
      console.log('📤 [authApi] Payload enviado al backend (personas):', payload);
      
      const response = await api.post('/api/v1/personas/registrar/', payload)
      
      console.log('🔍 [authApi] Respuesta cruda del backend (registro):', response.data)
      
      // La respuesta del endpoint personas/registrar/ ahora incluye verification_required
      // No hacer login automático, el usuario debe verificar su email primero
      if (response.data && response.data.verification_required) {
        return {
          success: true,
          verification_required: true,
          data: {
            email: response.data.email || userData.email,
            verification_required: true
          },
          message: 'Registro exitoso. Por favor verifica tu correo electrónico.'
        }
      }
      
      // Fallback para estructura legacy (no debería llegar aquí ahora)
      return {
        success: true,
        verification_required: true,
        data: {
          email: response.data?.email || response.data?.user?.email || userData.email,
          verification_required: true
        },
        message: 'Registro exitoso. Por favor verifica tu correo electrónico.'
      }
      
    } catch (error) {
      console.error('Error en registro API:', error)
      console.error('📋 [authApi] Respuesta completa del error:', {
        status: error.response?.status,
        data: error.response?.data,
        headers: error.response?.headers
      })
      
      // Extraer mensaje de error más detallado
      if (error.response?.data) {
        // Si hay errores de validación específicos
        if (error.response.data.detail) {
          error.message = error.response.data.detail
        } else if (error.response.data.error) {
          error.message = error.response.data.error
        } else if (typeof error.response.data === 'string') {
          error.message = error.response.data
        } else if (error.response.data.non_field_errors) {
          error.message = error.response.data.non_field_errors[0]
        } else {
          // Intentar extraer el primer error de campo
          const firstError = Object.values(error.response.data)[0]
          if (Array.isArray(firstError)) {
            error.message = firstError[0]
          } else if (typeof firstError === 'string') {
            error.message = firstError
          } else {
            error.message = 'Error en los datos proporcionados'
          }
        }
      }
      
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
   * Refrescar token de acceso usando refresh token
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
   * Alias para refreshToken (mantiene compatibilidad)
   */
  async refreshAccessToken(refreshToken) {
    return this.refreshToken(refreshToken)
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
      const payload = {
        first_name: profileData.firstName || profileData.fullName?.split(' ')[0] || '',
        last_name: profileData.lastName || profileData.fullName?.split(' ').slice(1).join(' ') || ''
      }
      
      // Incluir phone_number si está disponible
      if (profileData.phoneNumber || profileData.phone) {
        payload.phone_number = profileData.phoneNumber || profileData.phone
      }
      
      const response = await api.put('/auth/profile/', payload)
      return response.data
    } catch (error) {
      console.error('Error actualizando perfil:', error)
      throw error
    }
  },

  /**
   * Obtener perfil del usuario actual
   */
  async getProfile() {
    try {
      const response = await api.get('/auth/profile/')
      return response.data
    } catch (error) {
      console.error('Error obteniendo perfil:', error)
      throw error
    }
  },

  /**
   * Cambiar contraseña del usuario actual
   */
  async changePassword(passwordData) {
    try {
      const response = await api.post('/auth/change-password/', {
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
   * Verificar email con token (POST con token en body)
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
   * Verificar email con token desde la URL (GET con token en path)
   */
  async verifyEmailFromToken(token) {
    try {
      const response = await api.get(`/auth/verify-email/${token}/`)
      return response.data
    } catch (error) {
      console.error('Error verificando email desde token:', error)
      throw error
    }
  },

  /**
   * Reenviar email de verificación
   */
  async resendEmailVerification(email = null) {
    try {
      const payload = email ? { email } : {}
      const response = await api.post('/auth/resend-verification/', payload)
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
      // Fallback suave para no bloquear la UI si el backend responde 500
      if (error.response?.status === 500) {
        return { results: [], count: 0, page: 1, page_size: 50, total_pages: 1 }
      }
      throw error
    }
  },

  /**
   * Obtener un usuario específico por ID (admin/analyst)
   */
  async getUser(userId) {
    try {
      const response = await api.get(`/api/v1/auth/users/${userId}/`)
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
      const response = await api.patch(`/api/v1/auth/users/${userId}/update/`, userData)
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
      const response = await api.delete(`/api/v1/auth/users/${userId}/delete/`)
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
      const response = await api.patch(`/api/v1/auth/users/${userId}/update/`, {
        is_active: isActive
      })
      return response.data
    } catch (error) {
      console.error('Error cambiando estado de usuario:', error)
      throw error
    }
  },

  /**
   * Obtener estadísticas de usuarios
   */
  async getUserStats() {
    try {
      const response = await api.get('/auth/users/stats/')
      return response.data
    } catch (error) {
      console.error('Error obteniendo estadísticas de usuarios:', error)
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
  },

  /**
   * Enviar código OTP para verificación de email
   */
  async sendOtp(email) {
    try {
      const response = await api.post('/auth/send-otp/', { email })
      return response.data
    } catch (error) {
      console.error('Error enviando código OTP:', error)
      throw error
    }
  },

  /**
   * Verificar código OTP
   */
  async verifyOtp(email, code) {
    try {
      const response = await api.post('/auth/verify-otp/', { email, code })
      return response.data
    } catch (error) {
      console.error('Error verificando código OTP:', error)
      throw error
    }
  }
}

export default authApi
