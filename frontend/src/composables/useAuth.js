/**
 * Composable for authentication management
 * Consolidates login, registration, verification, password reset, and user management
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import authApi from '@/services/authApi'

/**
 * Main useAuth composable
 * @param {Object} options - Configuration options
 * @returns {Object} Auth composable methods and state
 */
export function useAuth(options = {}) {
  const router = useRouter()
  const authStore = useAuthStore()
  const notificationStore = useNotificationsStore()
  
  // Local state
  const loading = ref(false)
  const error = ref(null)
  
  // Re-export computed from store
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const user = computed(() => authStore.user)
  const userRole = computed(() => authStore.userRole)
  const isAdmin = computed(() => authStore.isAdmin)
  const isFarmer = computed(() => authStore.isFarmer)
  const isAnalyst = computed(() => authStore.isAnalyst)
  const isVerified = computed(() => authStore.isVerified)
  const userFullName = computed(() => authStore.userFullName)
  const userInitials = computed(() => authStore.userInitials)
  
  /**
   * Login with credentials
   * @param {Object} credentials - Login credentials
   * @param {string} credentials.email - User email
   * @param {string} credentials.username - Username (alternative to email)
   * @param {string} credentials.password - User password
   * @param {boolean} credentials.remember - Remember session
   * @returns {Promise<Object>} Login result
   */
  const login = async (credentials) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authStore.login(credentials)
      
      // If store returns error object, throw exception for composable compatibility
      if (result && result.success === false) {
        const errorMessage = result.error || 'Error al iniciar sesión'
        error.value = errorMessage
        
        const authError = new Error(errorMessage)
        authError.originalError = result.originalError
        throw authError
      }
      
      // Show success notification
      if (result && result.success !== false) {
        notificationStore.addNotification({
          type: 'success',
          title: 'Éxito',
          message: `Bienvenido, ${authStore.userFullName || 'usuario'}`
        })
      }
      
      return result
    } catch (err) {
      // Extract error message from normalized error or response
      const errorMessage = err.message || 
                          err.response?.data?.error ||
                          err.response?.data?.message || 
                          err.response?.data?.detail ||
                          'Error al iniciar sesión'
      error.value = errorMessage
      
      // Re-throw with message for form handling
      const authError = new Error(errorMessage)
      authError.originalError = err
      throw authError
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Register new user
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} Registration result
   */
  const register = async (userData) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authStore.register(userData)
      
      // Show success notification
      if (result && result.success !== false) {
        notificationStore.addNotification({
          type: 'success',
          title: 'Éxito',
          message: 'Registro exitoso'
        })
      }
      
      return result
    } catch (err) {
      const errorMessage = err.message || 'Error al registrar usuario'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Logout current user
   * @param {boolean} redirectToLogin - Redirect to login page after logout
   * @returns {Promise<void>}
   */
  const logout = async (redirectToLogin = true) => {
    try {
      loading.value = true
      error.value = null
      
      await authStore.logout(redirectToLogin)
      notificationStore.addNotification({
        type: 'success',
        title: 'Sesión cerrada',
        message: 'Has cerrado sesión correctamente'
      })
    } catch (err) {
      // Still clear local state even if API call fails
      authStore.clearAll()
      if (redirectToLogin) {
        router.push('/login')
      }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Verify email with token
   * @param {string} uid - User ID from verification link
   * @param {string} token - Verification token
   * @returns {Promise<Object>} Verification result
   */
  const verifyEmail = async (uid, token) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authStore.verifyEmail(uid, token)
      notificationStore.addNotification({
        type: 'success',
        title: 'Email verificado',
        message: 'Tu email ha sido verificado correctamente'
      })
      return result
    } catch (err) {
      const errorMessage = err.message || 'Error al verificar el email'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Verify email from token in URL
   * @param {string} token - Verification token from URL
   * @returns {Promise<Object>} Verification result
   */
  const verifyEmailFromToken = async (token) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authStore.verifyEmailFromToken(token)
      return result
    } catch (err) {
      const errorMessage = err.message || 'Error al verificar el email'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Resend email verification
   * @param {string} email - User email (optional, uses current user if not provided)
   * @returns {Promise<Object>} Resend result
   */
  const resendEmailVerification = async (email = null) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authStore.resendEmailVerification(email)
      notificationStore.addNotification({
        type: 'success',
        title: 'Email reenviado',
        message: 'Se ha reenviado el email de verificación'
      })
      
      return result
    } catch (err) {
      const errorMessage = err.message || 'Error al reenviar el email'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Request password reset
   * @param {string} email - User email
   * @returns {Promise<Object>} Reset request result
   */
  const requestPasswordReset = async (email) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authStore.requestPasswordReset(email)
      
      return result
    } catch (err) {
      const errorMessage = err.message || 'Error al solicitar restablecimiento'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Confirm password reset
   * @param {Object} resetData - Password reset data
   * @param {string} resetData.uid - User ID from reset link
   * @param {string} resetData.token - Reset token
   * @param {string} resetData.newPassword - New password
   * @param {string} resetData.confirmPassword - Password confirmation
   * @returns {Promise<Object>} Reset result
   */
  const confirmPasswordReset = async (resetData) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authApi.confirmPasswordReset(resetData)
      
      // Redirect to login after successful reset
      setTimeout(() => {
        router.push('/login')
      }, 2000)
      
      return result
    } catch (err) {
      const errorMessage = err.message || 'Error al restablecer la contraseña'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Change password for authenticated user
   * @param {Object} passwordData - Password change data
   * @param {string} passwordData.oldPassword - Current password
   * @param {string} passwordData.newPassword - New password
   * @param {string} passwordData.confirmPassword - Password confirmation
   * @returns {Promise<Object>} Change result
   */
  const changePassword = async (passwordData) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authStore.changePassword(passwordData)
      
      return result
    } catch (err) {
      const errorMessage = err.message || 'Error al cambiar la contraseña'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Update user profile
   * @param {Object} profileData - Profile data to update
   * @returns {Promise<Object>} Update result
   */
  const updateProfile = async (profileData) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authStore.updateProfile(profileData)
      
      return result
    } catch (err) {
      const errorMessage = err.message || 'Error al actualizar el perfil'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Get current user profile
   * @returns {Promise<Object>} User profile
   */
  const getCurrentUser = async () => {
    try {
      loading.value = true
      error.value = null
      
      return await authStore.getCurrentUser()
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar el perfil'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Check if user has specific permission
   * @param {string} permission - Permission name
   * @returns {boolean} Has permission
   */
  const hasPermission = (permission) => {
    return authStore.hasPermission(permission)
  }
  
  /**
   * Send OTP code for email verification
   * @param {string} email - User email
   * @returns {Promise<Object>} OTP send result
   */
  const sendOtp = async (email) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authStore.sendOtp(email)
      
      return result
    } catch (err) {
      const errorMessage = err.message || 'Error al enviar el código'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Verify OTP code
   * @param {string} email - User email
   * @param {string} code - OTP code
   * @returns {Promise<Object>} OTP verification result
   */
  const verifyOtp = async (email, code) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await authStore.verifyOtp(email, code)
      return result
    } catch (err) {
      const errorMessage = err.message || 'Código inválido o expirado'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Refresh access token
   * @returns {Promise<boolean>} Refresh success
   */
  const refreshAccessToken = async () => {
    try {
      return await authStore.refreshAccessToken()
    } catch (err) {
      return false
    }
  }
  
  /**
   * Clear error state
   */
  const clearError = () => {
    error.value = null
    authStore.setError(null)
  }
  
  return {
    // State
    loading,
    error,
    
    // Computed (from store)
    isAuthenticated,
    user,
    userRole,
    isAdmin,
    isFarmer,
    isAnalyst,
    isVerified,
    userFullName,
    userInitials,
    
    // Methods
    login,
    register,
    logout,
    verifyEmail,
    verifyEmailFromToken,
    resendEmailVerification,
    requestPasswordReset,
    confirmPasswordReset,
    changePassword,
    updateProfile,
    getCurrentUser,
    hasPermission,
    sendOtp,
    verifyOtp,
    refreshAccessToken,
    clearError
  }
}

