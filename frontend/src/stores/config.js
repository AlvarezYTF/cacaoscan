import { defineStore } from 'pinia'
import configApi from '@/services/configApi'

export const useConfigStore = defineStore('config', {
  state: () => ({
    // Configuración General
    general: {
      nombre_sistema: 'CacaoScan',
      email_contacto: 'contacto@cacaoscan.com',
      lema: 'La mejor plataforma para el control de calidad del cacao',
      logo_url: null
    },
    
    // Configuración de Seguridad
    security: {
      recaptcha_enabled: true,
      session_timeout: 60,
      login_attempts: 5,
      two_factor_auth: false
    },
    
    // Configuración ML
    ml: {
      active_model: 'yolov8',
      last_training: null
    },
    
    // Configuración del Sistema
    system: {
      version: '1.0.0',
      server_status: 'online',
      backend_version: '4.2.7',
      frontend_version: '3.5.3',
      database: 'PostgreSQL 16'
    },
    
    // Estados
    loading: false,
    lastUpdate: null
  }),

  getters: {
    // Getter para el nombre del sistema
    brandName: (state) => state.general.nombre_sistema || 'CacaoScan',
    
    // Getter para el lema
    sistemaLema: (state) => state.general.lema,
    
    // Getter para el logo
    sistemaLogo: (state) => state.general.logo_url,
    
    // Getter para configuración completa
    getGeneralConfig: (state) => state.general,
    getSecurityConfig: (state) => state.security,
    getMLConfig: (state) => state.ml,
    getSystemConfig: (state) => state.system
  },

  actions: {
    _handleAuthStoreImportError(err) {
      if (err.code === 'MODULE_NOT_FOUND' || err.message?.includes('Cannot find module')) {
        return null
      }
      throw err
    },

    async _loadAuthStore() {
      const importPromise = import('@/stores/auth')
      return importPromise
        .then(({ useAuthStore }) => useAuthStore())
        .catch((err) => this._handleAuthStoreImportError(err))
    },

    _canAccessConfig(authStore) {
      const isAdmin = authStore?.isAdmin || false
      const isAnalyst = authStore?.isAnalyst || false
      return isAdmin || isAnalyst
    },

    _buildConfigPromises(canAccessConfig, isAuthenticated) {
      const promises = []
      
      // Solo cargar system config si el usuario está autenticado
      // Don't catch errors here - let them propagate to Promise.allSettled
      if (isAuthenticated) {
        promises.push(configApi.getSystemConfig())
      }
      
      if (canAccessConfig && isAuthenticated) {
        promises.push(
          configApi.getGeneralConfig(),
          configApi.getSecurityConfig(),
          configApi.getMLConfig()
        )
      }
      return promises
    },

    _processConfigResults(results, canAccessConfig) {
      // Filtrar resultados nulos (errores silenciados)
      const validResults = results.filter(r => r !== null)
      
      if (canAccessConfig && validResults.length === 4) {
        // results order: [system, general, security, ml]
        return {
          system: validResults[0] || null,
          general: validResults[1] || null,
          security: validResults[2] || null,
          ml: validResults[3] || null
        }
      } else if (validResults.length > 0) {
        // Solo tenemos system config
        return {
          system: validResults[0] || null,
          general: null,
          security: null,
          ml: null
        }
      }
      
      return {
        general: null,
        security: null,
        ml: null,
        system: null
      }
    },

    _updateConfigState(general, security, ml, system) {
      if (general && typeof general === 'object' && Object.keys(general).length > 0) {
        this.general = {
          nombre_sistema: general.nombre_sistema || 'CacaoScan',
          email_contacto: general.email_contacto || 'contacto@cacaoscan.com',
          lema: general.lema || 'La mejor plataforma para el control de calidad del cacao',
          logo_url: general.logo_url
        }
      }
      
      if (security && typeof security === 'object' && Object.keys(security).length > 0) {
        this.security = {
          recaptcha_enabled: security.recaptcha_enabled ?? true,
          session_timeout: security.session_timeout || 60,
          login_attempts: security.login_attempts || 5,
          two_factor_auth: security.two_factor_auth ?? false
        }
      }
      
      if (ml && typeof ml === 'object' && Object.keys(ml).length > 0) {
        this.ml = {
          active_model: ml.active_model || 'yolov8',
          last_training: ml.last_training || null
        }
      }
      
      if (system && typeof system === 'object' && Object.keys(system).length > 0) {
        this.system = {
          version: system.version || '1.0.0',
          server_status: system.server_status || 'online',
          backend_version: system.backend_version || '4.2.7',
          frontend_version: system.frontend_version || '3.5.3',
          database: system.database || 'PostgreSQL 16'
        }
      }
    },

    // Cargar todas las configuraciones (respetando permisos por rol)
    async loadAll() {
      this.loading = true
      try {
        const authStore = await this._loadAuthStore()
        if (!authStore) {
          // Si no hay authStore, no intentar cargar configuraciones
          return { success: false, loaded: false, error: 'Auth store not available' }
        }

        const isAuthenticated = authStore?.isAuthenticated || false
        
        // Verificar que haya un token válido antes de intentar cargar configuraciones
        const accessToken = authStore?.accessToken || localStorage.getItem('access_token')
        const refreshToken = authStore?.refreshToken || localStorage.getItem('refresh_token')
        
        // Si no hay token ni refresh token, no intentar cargar configuraciones que requieren autenticación
        if (!accessToken && !refreshToken) {
          return { success: false, loaded: false, error: 'No authentication tokens available' }
        }

        const canAccessConfig = isAuthenticated && this._canAccessConfig(authStore)

        const promises = this._buildConfigPromises(canAccessConfig, isAuthenticated)
        
        // Si no hay promesas que ejecutar, retornar sin cargar
        if (promises.length === 0) {
          return { success: true, loaded: false }
        }
        
        // Usar Promise.allSettled para que los errores individuales no detengan todo
        const results = await Promise.allSettled(promises)
        let hasError403Or500 = false
        const settledResults = results.map(result => {
          if (result.status === 'fulfilled') {
            return result.value
          }
          // Check for 403 or 500 errors
          if (result.reason?.response?.status === 403 || result.reason?.response?.status === 500) {
            hasError403Or500 = true
          }
          // Check for network errors
          if (result.reason?.code === 'ERR_NETWORK' || result.reason?.message === 'Network Error') {
            console.warn('Backend no disponible. Asegúrate de que el servidor esté corriendo en http://localhost:8000')
            // Don't show error for network issues during config load - it's expected if backend is down
            return null
          }
          // Log unexpected errors (not 401/403)
          if (result.reason?.response?.status !== 401 && result.reason?.response?.status !== 403) {
            console.error('Unexpected error loading config:', result.reason)
          }
          // Ignorar errores 401/403 silenciosamente - el usuario simplemente no tiene acceso
          return null
        })
        
        const configs = this._processConfigResults(settledResults, canAccessConfig)
        
        // Check if any valid configs were loaded
        const hasValidConfigs = settledResults.some(result => result !== null)
        
        // If there were 403 or 500 errors, return success: false
        const success = hasError403Or500 ? false : hasValidConfigs
        
        this._updateConfigState(configs.general, configs.security, configs.ml, configs.system)
        
        this.lastUpdate = new Date()
        return { success, loaded: hasValidConfigs }
      } catch (error) {
        // Log unexpected errors
        console.error(error)
        // Silenciar errores de configuración - usar valores por defecto
        return { success: false, loaded: false, error: error.message }
      } finally {
        this.loading = false
      }
    },

    // Guardar configuración general
    async saveGeneral(data) {
      try {
        const saved = await configApi.saveGeneralConfig(data)
        
        // Actualizar el store con los datos guardados
        if (saved) {
          this.general.nombre_sistema = saved.nombre_sistema || data.nombre_sistema
          this.general.email_contacto = saved.email_contacto || data.email_contacto
          this.general.lema = saved.lema || data.lema
          this.general.logo_url = saved.logo_url || this.general.logo_url
          
          this.lastUpdate = new Date()
          // Emitir evento de actualización global
          globalThis.dispatchEvent(new CustomEvent('config-updated', { 
            detail: { section: 'general', data: this.general }
          }))
        }
        
        return saved
      } catch (error) {
        throw error
      }
    },

    // Guardar configuración de seguridad
    async saveSecurity(data) {
      try {
        const saved = await configApi.saveSecurityConfig(data)
        
        // Actualizar el store
        if (saved) {
          this.security = { ...this.security, ...saved }
          this.lastUpdate = new Date()
          
          globalThis.dispatchEvent(new CustomEvent('config-updated', { 
            detail: { section: 'security', data: this.security }
          }))
        }
        
        return saved
      } catch (error) {
        throw error
      }
    },

    // Guardar configuración ML
    async saveML(data) {
      try {
        const saved = await configApi.saveMLConfig(data)
        
        // Actualizar el store
        if (saved) {
          this.ml = { ...this.ml, ...saved }
          this.lastUpdate = new Date()
          
          globalThis.dispatchEvent(new CustomEvent('config-updated', { 
            detail: { section: 'ml', data: this.ml }
          }))
        }
        
        return saved
      } catch (error) {
        throw error
      }
    },

    // Actualizar configuración general localmente (sin guardar en backend)
    updateGeneral(data) {
      this.general = { ...this.general, ...data }
    },

    // Actualizar configuración de seguridad localmente
    updateSecurity(data) {
      this.security = { ...this.security, ...data }
    },

    // Actualizar configuración ML localmente
    updateML(data) {
      this.ml = { ...this.ml, ...data }
    },

    // Resetear configuración
    reset() {
      this.general = {
        nombre_sistema: 'CacaoScan',
        email_contacto: 'contacto@cacaoscan.com',
        lema: 'La mejor plataforma para el control de calidad del cacao',
        logo_url: null
      }
      this.security = {
        recaptcha_enabled: true,
        session_timeout: 60,
        login_attempts: 5,
        two_factor_auth: false
      }
      this.ml = {
        active_model: 'yolov8',
        last_training: null
      }
    }
  }
})

