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
    // Cargar todas las configuraciones
    async loadAll() {
      this.loading = true
      try {
        const [general, security, ml, system] = await Promise.all([
          configApi.getGeneralConfig().catch(() => ({})),
          configApi.getSecurityConfig().catch(() => ({})),
          configApi.getMLConfig().catch(() => ({})),
          configApi.getSystemConfig().catch(() => ({}))
        ])
        
        // Actualizar estado si hay datos
        if (general && Object.keys(general).length > 0) {
          this.general = {
            nombre_sistema: general.nombre_sistema || 'CacaoScan',
            email_contacto: general.email_contacto || 'contacto@cacaoscan.com',
            lema: general.lema || 'La mejor plataforma para el control de calidad del cacao',
            logo_url: general.logo_url
          }
        }
        
        if (security && Object.keys(security).length > 0) {
          this.security = {
            recaptcha_enabled: security.recaptcha_enabled ?? true,
            session_timeout: security.session_timeout || 60,
            login_attempts: security.login_attempts || 5,
            two_factor_auth: security.two_factor_auth ?? false
          }
        }
        
        if (ml && Object.keys(ml).length > 0) {
          this.ml = {
            active_model: ml.active_model || 'yolov8',
            last_training: ml.last_training || null
          }
        }
        
        if (system && Object.keys(system).length > 0) {
          this.system = {
            version: system.version || '1.0.0',
            server_status: system.server_status || 'online',
            backend_version: system.backend_version || '4.2.7',
            frontend_version: system.frontend_version || '3.5.3',
            database: system.database || 'PostgreSQL 16'
          }
        }
        
        this.lastUpdate = new Date()
        console.log('✅ Configuración del sistema cargada:', this.brandName)
        
        return true
      } catch (error) {
        console.error('Error cargando configuración:', error)
        return false
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
          console.log('✅ Configuración general actualizada:', this.brandName)
          
          // Emitir evento de actualización global
          window.dispatchEvent(new CustomEvent('config-updated', { 
            detail: { section: 'general', data: this.general }
          }))
        }
        
        return saved
      } catch (error) {
        console.error('Error guardando configuración general:', error)
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
          
          window.dispatchEvent(new CustomEvent('config-updated', { 
            detail: { section: 'security', data: this.security }
          }))
        }
        
        return saved
      } catch (error) {
        console.error('Error guardando configuración de seguridad:', error)
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
          
          window.dispatchEvent(new CustomEvent('config-updated', { 
            detail: { section: 'ml', data: this.ml }
          }))
        }
        
        return saved
      } catch (error) {
        console.error('Error guardando configuración ML:', error)
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

