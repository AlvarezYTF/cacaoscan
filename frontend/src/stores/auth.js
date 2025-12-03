/**
 * Store de autenticación para CacaoScan
 * Gestiona el estado de autenticación, tokens JWT y datos del usuario
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authApi from '@/services/authApi'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // Estado reactivo
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)
  const error = ref(null)
  const lastActivity = ref(Date.now())

  // Getters computados
  const isAuthenticated = computed(() => {
    return !!(accessToken.value && user.value)
  })

  const userRole = computed(() => {
    return user.value?.role || null
  })

  const isAdmin = computed(() => {
    return userRole.value === 'admin'
  })

  const isFarmer = computed(() => {
    return userRole.value === 'farmer'
  })

  const isAnalyst = computed(() => {
    return userRole.value === 'analyst'
  })

  const isVerified = computed(() => {
    return user.value?.is_verified || false
  })

  const userFullName = computed(() => {
    if (!user.value) return ''
    const firstName = user.value.first_name || ''
    const lastName = user.value.last_name || ''
    return `${firstName} ${lastName}`.trim()
  })

  const userInitials = computed(() => {
    if (!user.value) return ''
    const firstName = user.value.first_name || ''
    const lastName = user.value.last_name || ''
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
  })

  const canUploadImages = computed(() => {
    return isAuthenticated.value && isVerified.value && (isFarmer.value || isAdmin.value)
  })

  const canViewAllPredictions = computed(() => {
    return isAuthenticated.value && (isAdmin.value || isAnalyst.value)
  })

  const canManageUsers = computed(() => {
    return isAuthenticated.value && isAdmin.value
  })

  // Actions
  const setTokens = (tokenData) => {
    // Guardar access y refresh tokens
    if (typeof tokenData === 'string') {
      // Si se pasa directamente el token como string (solo access)
      accessToken.value = tokenData
      localStorage.setItem('access_token', tokenData)
    } else if (tokenData && tokenData.access) {
      // Si se pasa un objeto con access y refresh token
      accessToken.value = tokenData.access
      localStorage.setItem('access_token', tokenData.access)
      
      // Guardar refresh token si está disponible
      if (tokenData.refresh !== undefined && tokenData.refresh !== null) {
        refreshToken.value = tokenData.refresh
        localStorage.setItem('refresh_token', tokenData.refresh)
      }
      
      // Guardar usuario si está disponible
      if (tokenData.user) {
        user.value = tokenData.user
        localStorage.setItem('user', JSON.stringify(tokenData.user))
      }
    }
  }

  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const clearUser = () => {
    user.value = null
    localStorage.removeItem('user')
  }

  const setError = (errorMessage) => {
    error.value = errorMessage
    setTimeout(() => {
      error.value = null
    }, 5000)
  }

  const updateLastActivity = () => {
    lastActivity.value = Date.now()
  }

  // Inicializar desde localStorage
  const initializeFromStorage = () => {
    try {
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        user.value = JSON.parse(storedUser)
      }
      
      const storedToken = localStorage.getItem('access_token')
      
      if (storedToken) {
        accessToken.value = storedToken
      }
    } catch (error) {
      console.error('Error inicializando desde localStorage:', error)
      clearAll()
    }
  }

  // Inicializar autenticación completa
  const initializeAuth = async () => {
    try {
      // Inicializar desde localStorage
      initializeFromStorage()
      
      // Si hay token pero no hay usuario, intentar obtener el usuario actual
      if (accessToken.value && !user.value) {
        console.log('🔄 Restaurando sesión desde token...')
        await getCurrentUser()
      }
      
      console.log('✅ Autenticación inicializada:', {
        hasToken: !!accessToken.value,
        hasUser: !!user.value,
        isAuthenticated: isAuthenticated.value
      })
      
    } catch (error) {
      console.error('❌ Error inicializando autenticación:', error)
      // Si hay error durante la inicialización, limpiar el estado completo
      // para evitar datos inconsistentes o tokens inválidos en el store
      clearAll()
    }
  }

  // Login
  const login = async (credentials) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.login(credentials)
      
      if (response.token && response.user) {
        // Guardar tokens (access y refresh si están disponibles)
        setTokens({
          access: response.token,
          refresh: response.refresh, // Agregar refresh token
          user: response.user
        })
        
        updateLastActivity()
        
        // Redirigir según rol
        const redirectPath = getRedirectPath()
        await router.push(redirectPath)
        
        return { success: true }
      } else {
        throw new Error('Respuesta de login inválida')
      }
    } catch (err) {
      console.error('Error en login:', err)
      setError(err.response?.data?.message || err.message || 'Error al iniciar sesión')
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Registro
  const register = async (userData) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.register(userData)
      
      // Verificar si se requiere verificación de email
      if (response.verification_required || response.data?.verification_required) {
        // No hacer login automático, retornar datos para que el componente maneje la redirección
        return { 
          success: true, 
          data: {
            email: response.data?.email || response.email || userData.email,
            verification_required: true
          }
        }
      }
      
      // El nuevo backend devuelve token directamente en el registro (caso legacy)
      if (response.success && response.token && response.user) {
        // Guardar tokens (access y refresh si están disponibles)
        setTokens({
          access: response.token,
          refresh: response.refresh,
          user: response.user
        })
        
        updateLastActivity()
        
        // Redirigir automáticamente al dashboard de agricultor
        await router.push({ name: 'AgricultorDashboard' })
        
        return { success: true }
      } else {
        // Fallback para formato anterior
        if (response.access && response.refresh) {
          setTokens(response)
          await getCurrentUser()
          updateLastActivity()
          await router.push({ name: 'AgricultorDashboard' })
          return { success: true }
        }
        
        if (response.success) {
          // Si no hay tokens, asumir que necesita verificación
          return {
            success: true,
            data: {
              email: response.email || userData.email,
              verification_required: true
            }
          }
        }
      }

      return response
    } catch (err) {
      console.error('Error en registro:', err)
      setError(err.response?.data?.message || err.message || 'Error en el registro')
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Logout
  const logout = async (showMessage = true) => {
    isLoading.value = true

    try {
      // Intentar hacer logout en el servidor
      if (accessToken.value) {
        await authApi.logout()
      }
    } catch (err) {
      console.error('Error en logout del servidor:', err)
      // Continuar con logout local aunque falle el servidor
    } finally {
      // Limpiar estado local
      clearAll()
      
      // Redirigir al login usando replace para evitar volver atrás
      await router.replace({ 
        name: 'Login',
        query: showMessage ? { message: 'Sesión cerrada exitosamente' } : {}
      })
      
      isLoading.value = false
    }
  }

  // Obtener usuario actual
  const getCurrentUser = async () => {
    if (!accessToken.value) return null

    try {
      const response = await authApi.getCurrentUser()
      
      // El endpoint /auth/profile/ puede devolver dos formatos:
      // 1. { success, data: {...}, message }
      // 2. {...userData} (directo)
      
      const userData = response.data || response
      
      setUser(userData)
      updateLastActivity()
      return userData
    } catch (err) {
      console.error('Error obteniendo usuario actual:', err)
      
      // Si el token no es válido, hacer logout
      if (err.response?.status === 401) {
        await logout(false)
      }
      
      throw err
    }
  }

  // Refrescar access token usando refresh token
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('No hay refresh token disponible')
    }
    
    try {
      const response = await authApi.refreshAccessToken(refreshToken.value)
      
      if (response.access) {
        accessToken.value = response.access
        localStorage.setItem('access_token', response.access)
        
        // Actualizar refresh token si viene en la respuesta
        if (response.refresh) {
          refreshToken.value = response.refresh
          localStorage.setItem('refresh_token', response.refresh)
        }
        
        updateLastActivity()
        return response.access
      }
      
      throw new Error('Respuesta inválida del servidor')
    } catch (err) {
      console.error('❌ Error refrescando token:', err)
      // Si el refresh token expiró o fue rechazado, limpiar el estado completo
      // y forzar logout para que el usuario se autentique nuevamente
      if (err.response?.status === 401 || err.response?.status === 403) {
        await logout(false)
      }
      throw err
    }
  }

  // Cambiar contraseña
  const changePassword = async (passwordData) => {
    isLoading.value = true
    error.value = null

    try {
      await authApi.changePassword(passwordData)
      return { success: true }
    } catch (err) {
      console.error('Error cambiando contraseña:', err)
      setError(err.response?.data?.detail || 'Error al cambiar contraseña')
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Solicitar restablecimiento de contraseña
  const requestPasswordReset = async (email) => {
    isLoading.value = true
    error.value = null

    try {
      await authApi.requestPasswordReset(email)
      return { success: true }
    } catch (err) {
      console.error('Error solicitando reset de contraseña:', err)
      setError(err.response?.data?.detail || 'Error al solicitar restablecimiento')
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Verificar email
  const verifyEmail = async (uid, token) => {
    isLoading.value = true
    error.value = null

    try {
      await authApi.verifyEmail(uid, token)
      
      // Actualizar usuario si está logueado
      if (isAuthenticated.value) {
        await getCurrentUser()
      }
      
      return { success: true }
    } catch (err) {
      console.error('Error verificando email:', err)
      setError(err.response?.data?.message || err.response?.data?.detail || 'Error al verificar email')
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Verificar email desde token en URL
  const verifyEmailFromToken = async (token) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.verifyEmailFromToken(token)
      
      // Actualizar usuario si está logueado
      if (isAuthenticated.value) {
        await getCurrentUser()
      } else if (response.data?.user) {
        // Si no está logueado pero la verificación fue exitosa, establecer usuario
        setUser(response.data.user)
      }
      
      return { 
        success: true, 
        message: response.message || 'Email verificado exitosamente' 
      }
    } catch (err) {
      console.error('Error verificando email desde token:', err)
      const errorMessage = err.response?.data?.message || err.response?.data?.detail || 'Error al verificar email'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Reenviar verificación de email
  const resendEmailVerification = async (email = null) => {
    isLoading.value = true
    error.value = null

    try {
      // Si se proporciona email, enviarlo en el body
      if (email) {
        const response = await authApi.resendEmailVerification(email)
        return { success: true, message: response.message || 'Email de verificación enviado' }
      } else if (user.value?.email) {
        // Si no hay email pero hay usuario logueado, usar su email
        const response = await authApi.resendEmailVerification(user.value.email)
        return { success: true, message: response.message || 'Email de verificación enviado' }
      } else {
        throw new Error('Email requerido para reenviar verificación')
      }
    } catch (err) {
      console.error('Error reenviando verificación:', err)
      const errorMessage = err.response?.data?.message || err.response?.data?.detail || 'Error al reenviar verificación'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Actualizar perfil
  const updateProfile = async (profileData) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.updateProfile(profileData)
      
      // Actualizar datos del usuario si la respuesta incluye data
      if (response.data?.user) {
        setUser(response.data.user)
        return { success: true, data: response.data.user }
      } else if (response.user) {
        setUser(response.user)
        return { success: true, data: response.user }
      }
      
      // Si no hay datos de usuario, actualizar usuario actual
      if (isAuthenticated.value) {
        await getCurrentUser()
      }
      
      return { success: true }
    } catch (err) {
      console.error('Error actualizando perfil:', err)
      setError(err.response?.data?.message || err.message || 'Error al actualizar perfil')
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Limpia el estado completo de autenticación del store.
   * Elimina tokens, datos de usuario, errores y flags de carga.
   * Útil para resetear el estado después de logout o errores de autenticación.
   */
  const clearAll = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    error.value = null
    isLoading.value = false
    lastActivity.value = Date.now()
    
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // Obtener ruta de redirección según rol
  const getRedirectPath = () => {
    if (!user.value) return '/'

    // Verificar si ya estamos en una ruta apropiada para evitar loops
    const currentPath = router.currentRoute.value.path
    const appropriatePaths = {
      admin: ['/admin/dashboard', '/analisis', '/reportes', '/perfil'],
      analyst: ['/analisis', '/reportes', '/perfil'],
      farmer: ['/agricultor-dashboard', '/prediccion', '/perfil']
    }
    
    const userPaths = appropriatePaths[user.value.role] || ['/']
    const isOnAppropriatePath = userPaths.some(path => currentPath.startsWith(path))
    
    if (isOnAppropriatePath) {
      return currentPath // No redirigir si ya está en una ruta apropiada
    }

    switch (user.value.role) {
      case 'admin':
        return '/admin/dashboard'
      case 'analyst':
        return '/analisis'
      case 'farmer':
        return '/agricultor-dashboard'
      default:
        return '/'
    }
  }

  // Verificar si la sesión ha expirado por inactividad
  const checkSessionTimeout = () => {
    const TIMEOUT_DURATION = 30 * 60 * 1000 // 30 minutos
    const now = Date.now()
    
    if (isAuthenticated.value && (now - lastActivity.value) > TIMEOUT_DURATION) {
      logout(true)
      return true
    }
    
    return false
  }

  // Verificar permisos específicos
  const hasPermission = (permission) => {
    if (!isAuthenticated.value) return false

    const permissions = {
      'upload_images': canUploadImages.value,
      'view_all_predictions': canViewAllPredictions.value,
      'manage_users': canManageUsers.value,
      'manage_dataset': isAdmin.value || isAnalyst.value,
      'train_models': isAdmin.value,
      'view_statistics': isAdmin.value || isAnalyst.value
    }

    return permissions[permission] || false
  }

  // Enviar código OTP
  const sendOtp = async (email) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.sendOtp(email)
      
      if (response.success) {
        return { success: true, message: response.message || 'Código OTP enviado exitosamente' }
      } else {
        setError(response.error || 'Error al enviar código OTP')
        return { success: false, error: error.value }
      }
    } catch (err) {
      console.error('Error enviando código OTP:', err)
      setError(err.response?.data?.message || err.message || 'Error al enviar código OTP')
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Verificar código OTP
  const verifyOtp = async (email, code) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.verifyOtp(email, code)
      
      if (response.success) {
        return { success: true, message: response.message || 'Email verificado exitosamente' }
      } else {
        setError(response.error || 'Código OTP inválido o expirado')
        return { success: false, error: error.value }
      }
    } catch (err) {
      console.error('Error verificando código OTP:', err)
      const errorMessage = err.response?.data?.message || err.message || 'Código OTP inválido o expirado'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Inicializar store
  initializeFromStorage()

  return {
    // Estado
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    lastActivity,
    
    // Getters
    isAuthenticated,
    userRole,
    isAdmin,
    isFarmer,
    isAnalyst,
    isVerified,
    userFullName,
    userInitials,
    canUploadImages,
    canViewAllPredictions,
    canManageUsers,
    
    // Actions
    login,
    register,
    logout,
    getCurrentUser,
    refreshAccessToken,
    changePassword,
    requestPasswordReset,
    verifyEmail,
    verifyEmailFromToken,
    resendEmailVerification,
    updateProfile,
    updateLastActivity,
    checkSessionTimeout,
    hasPermission,
    getRedirectPath,
    clearAll,
    clearTokens,
    setError,
    setTokens,
    setUser,
    clearUser,
    initializeAuth,
    sendOtp,
    verifyOtp
  }
})
