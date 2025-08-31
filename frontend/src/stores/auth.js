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
    return `${user.value.first_name} ${user.value.last_name}`.trim()
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
  const setTokens = (tokens) => {
    accessToken.value = tokens.access
    refreshToken.value = tokens.refresh
    
    localStorage.setItem('access_token', tokens.access)
    localStorage.setItem('refresh_token', tokens.refresh)
  }

  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
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
      
      const storedTokens = {
        access: localStorage.getItem('access_token'),
        refresh: localStorage.getItem('refresh_token')
      }
      
      if (storedTokens.access && storedTokens.refresh) {
        accessToken.value = storedTokens.access
        refreshToken.value = storedTokens.refresh
      }
    } catch (error) {
      console.error('Error inicializando desde localStorage:', error)
      clearAll()
    }
  }

  // Login
  const login = async (credentials) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.login(credentials)
      
      if (response.access && response.refresh) {
        setTokens(response)
        
        // Obtener datos del usuario
        await getCurrentUser()
        
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
      setError(err.response?.data?.detail || err.message || 'Error al iniciar sesión')
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
      
      // Si el registro incluye tokens (auto-login)
      if (response.access && response.refresh) {
        setTokens(response)
        await getCurrentUser()
        updateLastActivity()
        
        const redirectPath = getRedirectPath()
        await router.push(redirectPath)
      } else {
        // Redirigir a login con mensaje de éxito
        await router.push({ 
          name: 'Login', 
          query: { message: 'Registro exitoso. Por favor inicia sesión.' }
        })
      }
      
      return { success: true }
    } catch (err) {
      console.error('Error en registro:', err)
      setError(err.response?.data?.detail || err.message || 'Error en el registro')
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
      if (refreshToken.value) {
        await authApi.logout(refreshToken.value)
      }
    } catch (err) {
      console.error('Error en logout del servidor:', err)
      // Continuar con logout local aunque falle el servidor
    } finally {
      // Limpiar estado local
      clearAll()
      
      // Redirigir al login
      await router.push({ 
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
      const userData = await authApi.getCurrentUser()
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

  // Refrescar token
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await authApi.refreshToken(refreshToken.value)
      
      setTokens({
        access: response.access,
        refresh: refreshToken.value // Mantener el refresh token actual
      })
      
      return response.access
    } catch (err) {
      console.error('Error refrescando token:', err)
      await logout(false)
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
      setError(err.response?.data?.detail || 'Error al verificar email')
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Reenviar verificación de email
  const resendEmailVerification = async () => {
    isLoading.value = true
    error.value = null

    try {
      await authApi.resendEmailVerification()
      return { success: true }
    } catch (err) {
      console.error('Error reenviando verificación:', err)
      setError(err.response?.data?.detail || 'Error al reenviar verificación')
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Actualizar perfil
  const updateProfile = async (profileData) => {
    isLoading.value = true
    error.value = null

    try {
      const updatedUser = await authApi.updateProfile(profileData)
      setUser(updatedUser)
      return { success: true }
    } catch (err) {
      console.error('Error actualizando perfil:', err)
      setError(err.response?.data?.detail || 'Error al actualizar perfil')
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Limpiar todo el estado
  const clearAll = () => {
    clearTokens()
    clearUser()
    error.value = null
    lastActivity.value = Date.now()
  }

  // Obtener ruta de redirección según rol
  const getRedirectPath = () => {
    if (!user.value) return '/'

    // Verificar si ya estamos en una ruta apropiada para evitar loops
    const currentPath = router.currentRoute.value.path
    const appropriatePaths = {
      admin: ['/admin/', '/analisis', '/reportes', '/perfil'],
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
    resendEmailVerification,
    updateProfile,
    updateLastActivity,
    checkSessionTimeout,
    hasPermission,
    clearAll,
    setError
  }
})
