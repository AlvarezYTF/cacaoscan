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
  const hasPassword = ref(null) // Indica si el usuario tiene contraseña usable

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
    } else if (tokenData?.access) {
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
    if (!userData) {
      user.value = null
      localStorage.removeItem('user')
      hasPassword.value = null
      return
    }
    
    // 🔥 FIX 1: Limpiar localStorage ANTES de guardar para evitar datos viejos
    localStorage.removeItem('user')
    
    // 🔥 FIX CRÍTICO: Preservar valores existentes si no vienen en userData
    // Esto evita que se sobrescriban datos correctos cuando se actualiza parcialmente
    const existingUser = user.value || {}
    
    // Ensure role is set (default to 'farmer' if missing)
    if (!userData.role) {
      userData.role = existingUser.role || 'farmer'
    }
    
    // 🔥 FIX 2: Preservar login_provider si no viene en userData o es undefined
    // NO establecer 'local' por defecto si ya existe un valor correcto (como "google")
    if (!('login_provider' in userData) || userData.login_provider === undefined) {
      // Si no viene o es undefined, usar el valor existente (puede ser "google" del login)
      if (existingUser.login_provider !== undefined) {
        userData.login_provider = existingUser.login_provider
      } else {
        // Solo establecer 'local' si NO hay valor existente Y NO viene del backend
        userData.login_provider = 'local'
      }
    }
    
    // 🔥 FIX 3: Preservar password_allowed si no viene en userData o es undefined
    if (!('password_allowed' in userData) || userData.password_allowed === undefined) {
      // Si no viene o es undefined, usar el valor existente
      if (existingUser.password_allowed !== undefined) {
        userData.password_allowed = existingUser.password_allowed
      } else if (userData.login_provider !== undefined) {
        // Solo calcular si no hay valor existente Y hay login_provider
        userData.password_allowed = userData.login_provider !== 'google'
      } else {
        // Si no hay nada, establecer true por defecto (comportamiento seguro)
        userData.password_allowed = true
      }
    }
    
    // 🔥 FIX 4: Preservar has_password si no viene en userData o es undefined
    if (!('has_password' in userData) || userData.has_password === undefined) {
      // Si no viene o es undefined, usar el valor existente
      if (existingUser.has_password !== undefined) {
        userData.has_password = existingUser.has_password
      } else {
        // Solo establecer true por defecto si NO hay valor existente
        userData.has_password = true
      }
    }
    
    // Guardar has_password en el ref separado (solo para compatibilidad, NO usar para mostrar/ocultar secciones)
    if ('has_password' in userData) {
      hasPassword.value = userData.has_password
    }
    
    // 🔥 FIX 5: Construir objeto de usuario con TODOS los campos necesarios
    // Usar los valores de userData (que ya preservan los existentes si no vienen)
    const userObject = {
      ...userData,
      login_provider: userData.login_provider, // Ya preservado arriba
      password_allowed: userData.password_allowed, // Ya preservado arriba
      has_password: userData.has_password !== undefined ? userData.has_password : true
    }
    
    console.log('🔐 setUser - Saving user to store:', {
      login_provider: userObject.login_provider,
      password_allowed: userObject.password_allowed,
      has_password: userObject.has_password,
      preserved_from_existing: {
        login_provider: (!('login_provider' in userData) || userData.login_provider === undefined) && existingUser.login_provider !== undefined,
        password_allowed: (!('password_allowed' in userData) || userData.password_allowed === undefined) && existingUser.password_allowed !== undefined,
        has_password: (!('has_password' in userData) || userData.has_password === undefined) && existingUser.has_password !== undefined
      }
    })
    
    // Guardar en el store
    user.value = userObject
    
    // 🔥 FIX 6: Guardar en localStorage DESPUÉS de limpiar
    localStorage.setItem('user', JSON.stringify(userObject))
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
        const parsedUser = JSON.parse(storedUser)
        
        // 🔥 FIX: Asegurar que login_provider y password_allowed estén presentes
        // Si no están, establecer defaults (se actualizarán desde el backend)
        if (parsedUser) {
          if (!('login_provider' in parsedUser)) {
            parsedUser.login_provider = 'local' // Default temporal
          }
          if (!('password_allowed' in parsedUser)) {
            // Calcular password_allowed si no viene
            parsedUser.password_allowed = parsedUser.login_provider !== 'google'
          }
          
          // Restaurar has_password desde el usuario almacenado
          if ('has_password' in parsedUser) {
            hasPassword.value = parsedUser.has_password
          }
          
          // Actualizar user.value con los valores
          user.value = parsedUser
          
          // NOTA: Los valores correctos se obtendrán cuando se llame a getCurrentUser()
          // que actualizará desde el backend y limpiará localStorage antes de guardar
        }
      }
      
      const storedToken = localStorage.getItem('access_token')
      
      if (storedToken) {
        accessToken.value = storedToken
      }
    } catch (error) {
      clearAll()
    }
  }

  // Inicializar autenticación completa
  const initializeAuth = async () => {
    try {
      // Inicializar desde localStorage
      initializeFromStorage()
      
      // 🔥 FIX: Solo llamar a getCurrentUser() si hay token pero NO hay usuario
      // Si ya hay usuario con datos correctos (como login_provider: "google"),
      // NO llamar a getCurrentUser() para evitar sobrescribir esos datos
      if (accessToken.value && !user.value) {
        try {
          await getCurrentUser()
        } catch (error) {
          // Si getCurrentUser() falla, NO limpiar todo - puede ser un error temporal
          // Solo loguear el error pero mantener el token (el usuario puede estar logueado)
          console.warn('⚠️ Error loading user on init, but keeping token:', error.message || error)
          // NO llamar a clearAll() - el usuario puede estar logueado correctamente
        }
      }
      
      } catch (error) {
      // Si hay error durante la inicialización, limpiar el estado completo
      // para evitar datos inconsistentes o tokens inválidos en el store
      console.error('Error during auth initialization:', error)
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
        // Incluir has_password si viene en la respuesta
        if (response.has_password !== undefined) {
          response.user.has_password = response.has_password
        }
        // Incluir login_provider y password_allowed si vienen en la respuesta
        if (response.login_provider !== undefined) {
          response.user.login_provider = response.login_provider
        }
        if (response.password_allowed !== undefined) {
          response.user.password_allowed = response.password_allowed
        } else if (response.user.login_provider) {
          // Calcular password_allowed si no viene pero sí login_provider
          response.user.password_allowed = response.user.login_provider !== 'google'
        }
        
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
      // Extract error message from normalized error or response
      const errorMessage = err.message || 
                          err.response?.data?.error ||
                          err.response?.data?.message || 
                          err.response?.data?.detail ||
                          'Error al iniciar sesión'
      setError(errorMessage)
      // Return error object instead of throwing
      return {
        success: false,
        error: errorMessage,
        originalError: err
      }
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
      
      // Si el backend devuelve tokens (registro sin verificación de email)
      if (response.access && response.refresh) {
        // Guardar tokens y hacer login automático
        const userData = response.user || {}
        
        // Asegurar que el usuario tenga el rol (normalizar a 'farmer' si no viene)
        if (!userData.role) {
          userData.role = 'farmer'
        }
        
        setTokens({
          access: response.access,
          refresh: response.refresh,
          user: userData
        })
        
        // Obtener usuario completo desde el backend para asegurar que tenga todos los datos
        try {
          await getCurrentUser()
        } catch (err) {
          // Si falla getCurrentUser, usar el usuario del registro
          }
        
        updateLastActivity()
        
        // Redirigir automáticamente al dashboard de agricultor
        await router.push({ name: 'AgricultorDashboard' })
        
        return { success: true }
      }
      
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
      
      // Fallback para formato anterior con token
      if (response.success && response.token && response.user) {
        setTokens({
          access: response.token,
          refresh: response.refresh,
          user: response.user
        })
        
        updateLastActivity()
        await router.push({ name: 'AgricultorDashboard' })
        
        return { success: true }
      }
      
      // Si no hay tokens, asumir que necesita verificación
      if (response.success) {
        return {
          success: true,
          data: {
            email: response.email || userData.email,
            verification_required: true
          }
        }
      }

      return response
    } catch (err) {
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
      
      // 🔥 FIX CRÍTICO: Preservar valores existentes del usuario si no vienen del backend
      // Esto evita que se sobrescriban datos correctos (como login_provider: "google")
      const existingUser = user.value || {}
      
      // 🔥 FIX 1: Si el backend NO devuelve login_provider, password_allowed o has_password,
      // NO actualizar esos campos - mantener los valores existentes del usuario
      // Esto es crítico porque el backend puede no devolver estos campos en /auth/me/
      
      // Ensure role is present (UserSerializer should return it, but ensure it)
      if (!userData.role) {
        // Usar role existente o default a 'farmer'
        userData.role = existingUser.role || 'farmer'
      }
      
      // 🔥 FIX 2: Solo actualizar login_provider si viene explícitamente del backend
      // Si NO viene, mantener el valor existente (que puede ser "google" del login)
      if (!('login_provider' in userData)) {
        // Si no viene del backend, NO establecer nada - mantener el valor existente
        // El setUser() se encargará de preservarlo
        userData.login_provider = existingUser.login_provider
      }
      
      // 🔥 FIX 3: Solo actualizar password_allowed si viene explícitamente del backend
      if (!('password_allowed' in userData)) {
        // Si no viene del backend, usar el valor existente
        if (existingUser.password_allowed !== undefined) {
          userData.password_allowed = existingUser.password_allowed
        } else if (userData.login_provider) {
          // Solo calcular si no hay valor existente Y hay login_provider
          userData.password_allowed = userData.login_provider !== 'google'
        } else {
          // Si no hay nada, mantener undefined - setUser() lo manejará
          userData.password_allowed = existingUser.password_allowed
        }
      }
      
      // 🔥 FIX 4: Solo actualizar has_password si viene explícitamente del backend
      if (!('has_password' in userData)) {
        // Si no viene del backend, mantener el valor existente
        userData.has_password = existingUser.has_password
      }
      
      console.log('🔐 getCurrentUser - User data from backend:', {
        login_provider: userData.login_provider,
        password_allowed: userData.password_allowed,
        has_password: userData.has_password,
        backend_provided: {
          login_provider: 'login_provider' in (response.data || response),
          password_allowed: 'password_allowed' in (response.data || response),
          has_password: 'has_password' in (response.data || response)
        },
        preserved_from_existing: {
          login_provider: !('login_provider' in (response.data || response)) && !!existingUser.login_provider,
          password_allowed: !('password_allowed' in (response.data || response)) && existingUser.password_allowed !== undefined,
          has_password: !('has_password' in (response.data || response)) && existingUser.has_password !== undefined
        }
      })
      
      setUser(userData)
      updateLastActivity()
      return userData
    } catch (err) {
      // 🔥 FIX CRÍTICO: NO sobrescribir el usuario con valores por defecto cuando hay error
      // Solo hacer logout si el token es inválido, pero preservar los datos del usuario
      if (err.response?.status === 401) {
        await logout(false)
      } else {
        // Para otros errores (500, etc.), solo loguear el error pero NO cambiar el usuario
        console.warn('⚠️ Error loading user profile, keeping existing user data:', err.message || err)
        // NO hacer nada más - el usuario mantiene sus datos correctos del login
        // NO llamar a setUser() con valores por defecto
      }
      
      // Re-lanzar el error para que el llamador pueda manejarlo si es necesario
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
    hasPassword.value = null
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
    hasPassword,
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
