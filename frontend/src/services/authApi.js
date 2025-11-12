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
      
      // El backend puede devolver dos estructuras:
      // 1. { success, data: { access, refresh, user, ... }, message } (con wrapper)
      // 2. { success, access, refresh, user, ..., message } (plana)
      
      let normalizedData;
      
      if (response.data?.data) {
        // Estructura con wrapper 'data'
        normalizedData = {
          token: response.data.data.access,
          refresh: response.data.data.refresh,
          user: response.data.data.user,
          access_expires_at: response.data.data.access_expires_at,
          refresh_expires_at: response.data.data.refresh_expires_at,
          message: response.data.message
        }
      } else if (response.data?.access && response.data?.user) {
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
        throw new Error('Respuesta del servidor con formato inválido')
      }
      
      return normalizedData
  },

  /**
   * Registrar nuevo usuario con información de persona
   * Usa el nuevo endpoint /personas/registrar/ que crea User + Persona
   */
  async register(userData) {
    try {
      const payload = this._buildRegisterPayload(userData)
      const response = await api.post('/personas/registrar/', payload)
      return this._handleRegisterResponse(response, userData)
    } catch (error) {
      this._processRegisterError(error)
      throw error
    }
  },

  /**
   * Construir payload para registro de usuario
   * @private
   */
  _buildRegisterPayload(userData) {
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
  },

  /**
   * Procesar respuesta del registro
   * @private
   */
  _handleRegisterResponse(response, userData) {
    const successResponse = {
      success: true,
      verification_required: true,
      message: 'Registro exitoso. Por favor verifica tu correo electrónico.'
    }

    if (response.data?.verification_required) {
      return {
        ...successResponse,
        data: {
          email: response.data.email || userData.email,
          verification_required: true
        }
      }
    }

    // Fallback para estructura legacy
    return {
      ...successResponse,
      data: {
        email: response.data?.email || response.data?.user?.email || userData.email,
        verification_required: true
      }
    }
  },

  /**
   * Procesar errores del registro
   * @private
   */
  _processRegisterError(error) {
    if (!error.response?.data) return

    const errorData = error.response.data

    if (errorData.detail) {
      error.message = errorData.detail
    } else if (errorData.error) {
      error.message = errorData.error
    } else if (typeof errorData === 'string') {
      error.message = errorData
    } else if (errorData.non_field_errors) {
      error.message = errorData.non_field_errors[0]
    } else {
      const firstError = Object.values(errorData)[0]
      if (Array.isArray(firstError)) {
        error.message = firstError[0]
      } else if (typeof firstError === 'string') {
        error.message = firstError
      } else {
        error.message = 'Error en los datos proporcionados'
      }
    }
  },

  /**
   * Cerrar sesión (blacklist refresh token)
   */
  async logout() {
    const response = await api.post('/auth/logout/')
    return response.data
  },

  /**
   * Refrescar token de acceso usando refresh token
   */
  async refreshToken(refreshToken) {
    const response = await api.post('/auth/refresh/', {
      refresh: refreshToken
    })
    return response.data
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
    const response = await api.post('/auth/verify/', {
      token: token
    })
    return response.data
  },

  /**
   * Obtener información del usuario actual
   */
  async getCurrentUser() {
    const response = await api.get('/auth/profile/')
    return response.data
  },

  /**
   * Actualizar información del usuario actual
   */
  async updateProfile(profileData) {
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
  },

  /**
   * Obtener perfil del usuario actual
   */
  async getProfile() {
    const response = await api.get('/auth/profile/')
    return response.data
  },

  /**
   * Cambiar contraseña del usuario actual
   */
  async changePassword(passwordData) {
    const response = await api.post('/auth/change-password/', {
      old_password: passwordData.oldPassword,
      new_password: passwordData.newPassword,
      confirm_password: passwordData.confirmPassword
    })
    return response.data
  },

  /**
   * Solicitar restablecimiento de contraseña
   */
  async requestPasswordReset(email) {
    const response = await api.post('/auth/forgot-password/', {
      email: email
    })
    return response.data
  },

  /**
   * Confirmar restablecimiento de contraseña
   */
  async confirmPasswordReset(resetData) {
    const response = await api.post('/auth/reset-password/', {
      uid: resetData.uid,
      token: resetData.token,
      new_password: resetData.newPassword,
      confirm_password: resetData.confirmPassword
    })
    return response.data
  },

  /**
   * Verificar email con token (POST con token en body)
   */
  async verifyEmail(uid, token) {
    const response = await api.post('/auth/verify-email/', {
      uid: uid,
      token: token
    })
    return response.data
  },

  /**
   * Verificar email con token desde la URL (GET con token en path)
   */
  async verifyEmailFromToken(token) {
    const response = await api.get(`/auth/verify-email/${token}/`)
    return response.data
  },

  /**
   * Reenviar email de verificación
   */
  async resendEmailVerification(email = null) {
    const payload = email ? { email } : {}
    const response = await api.post('/auth/resend-verification/', payload)
    return response.data
  },

  /**
   * Obtener estadísticas de usuarios (solo admin)
   */
  async getUserStats() {
    const response = await api.get('/auth/admin/stats/')
    return response.data
  },

  /**
   * Realizar acciones masivas en usuarios (solo admin)
   */
  async bulkUserActions(actionData) {
    const response = await api.post('/auth/admin/bulk-actions/', {
      user_ids: actionData.userIds,
      action: actionData.action
    })
    return response.data
  },

  /**
   * Obtener lista de usuarios (admin/analyst)
   */
  async getUsers(params = {}) {
    try {
      const response = await api.get('/auth/users/', { params })
      return response.data
    } catch (error) {
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
    const response = await api.get(`/auth/users/${userId}/`)
    return response.data
  },

  /**
   * Actualizar usuario específico (admin)
   */
  async updateUser(userId, userData) {
    const response = await api.patch(`/auth/users/${userId}/update/`, userData)
    return response.data
  },

  /**
   * Eliminar usuario (admin)
   */
  async deleteUser(userId) {
    const response = await api.delete(`/auth/users/${userId}/delete/`)
    return response.data
  },

  /**
   * Cambiar estado de usuario (activo/inactivo)
   */
  async toggleUserStatus(userId, isActive) {
    const response = await api.patch(`/auth/users/${userId}/update/`, {
      is_active: isActive
    })
    return response.data
  },

  /**
   * Solicitar recuperación de contraseña
   */
  async forgotPassword(email) {
    const response = await api.post('/auth/forgot-password/', {
      email: email
    })
    return response.data
  },

  /**
   * Restablecer contraseña con token
   */
  async resetPassword(token, newPassword, confirmPassword) {
    const response = await api.post('/auth/reset-password/', {
      token: token,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
    return response.data
  },

  /**
   * Enviar código OTP para verificación de email
   */
  async sendOtp(email) {
    const response = await api.post('/auth/send-otp/', { email })
    return response.data
  },

  /**
   * Verificar código OTP
   */
  async verifyOtp(email, code) {
    const response = await api.post('/auth/verify-otp/', { email, code })
    return response.data
  }
}

export default authApi
