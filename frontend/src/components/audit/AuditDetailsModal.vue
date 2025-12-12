<template>
  <BaseModal
    :show="true"
    :title="getHeaderTitle()"
    subtitle="Detalles completos del evento de auditoría"
    max-width="4xl"
    @close="closeModal"
  >
    <template #header>
      <div class="flex items-center">
        <div class="bg-blue-100 p-2 rounded-lg mr-3">
          <i :class="getHeaderIcon()" class="text-blue-600"></i>
        </div>
        <div>
          <h3 class="text-xl font-bold text-gray-900">{{ getHeaderTitle() }}</h3>
          <p class="text-sm text-gray-600 mt-1">Detalles completos del evento de auditoría</p>
        </div>
      </div>
    </template>

    <div class="modal-body-content">
      <div class="details-content">
          <!-- Información básica -->
          <div class="details-section">
            <h4>
              <i class="fas fa-info-circle"></i>
              Información Básica
            </h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Usuario:</span>
                <span class="info-value">{{ data.usuario || 'Usuario Anónimo' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Dirección IP:</span>
                <span class="info-value">{{ data.ip_address || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Fecha y Hora:</span>
                <span class="info-value">{{ formatDateTime(data.timestamp || data.login_time) }}</span>
              </div>
              <div v-if="auditType === 'activity' || auditType === 'both'" class="info-item">
                <span class="info-label">Acción:</span>
                <span class="info-value">{{ data.accion_display || data.accion }}</span>
              </div>
              <div v-if="auditType === 'login' || auditType === 'both'" class="info-item">
                <span class="info-label">Estado:</span>
                <span class="info-value" :class="getStatusClass()">
                  {{ data.success ? 'Exitoso' : 'Fallido' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Detalles específicos según el tipo -->
          <div v-if="auditType === 'activity' || auditType === 'both'" class="details-section">
            <h4>
              <i class="fas fa-cube"></i>
              Detalles de Actividad
            </h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Modelo:</span>
                <span class="info-value">{{ data.modelo }}</span>
              </div>
              <div v-if="data.objeto_id" class="info-item">
                <span class="info-label">ID del Objeto:</span>
                <span class="info-value">{{ data.objeto_id }}</span>
              </div>
              <div class="info-item full-width">
                <span class="info-label">Descripción:</span>
                <span class="info-value">{{ data.descripcion }}</span>
              </div>
            </div>
          </div>

          <div v-if="auditType === 'login' || auditType === 'both'" class="details-section">
            <h4>
              <i class="fas fa-sign-in-alt"></i>
              Detalles de Sesión
            </h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Hora de Inicio:</span>
                <span class="info-value">{{ formatDateTime(data.login_time) }}</span>
              </div>
              <div v-if="data.logout_time" class="info-item">
                <span class="info-label">Hora de Cierre:</span>
                <span class="info-value">{{ formatDateTime(data.logout_time) }}</span>
              </div>
              <div v-if="data.session_duration" class="info-item">
                <span class="info-label">Duración:</span>
                <span class="info-value">{{ formatDuration(data.session_duration) }}</span>
              </div>
              <div v-if="data.failure_reason" class="info-item full-width">
                <span class="info-label">Razón del Fallo:</span>
                <span class="info-value error">{{ data.failure_reason }}</span>
              </div>
            </div>
          </div>

          <!-- Información técnica -->
          <div v-if="data.user_agent" class="details-section">
            <h4>
              <i class="fas fa-desktop"></i>
              Información Técnica
            </h4>
            <div class="info-grid">
              <div class="info-item full-width">
                <span class="info-label">User Agent:</span>
                <span class="info-value">{{ data.user_agent }}</span>
              </div>
            </div>
          </div>

          <!-- Cambios de datos -->
          <div v-if="data.datos_antes || data.datos_despues" class="details-section">
            <h4>
              <i class="fas fa-exchange-alt"></i>
              Cambios de Datos
            </h4>
            <div class="changes-container">
              <div v-if="data.datos_antes" class="change-section">
                <h5>Estado Anterior</h5>
                <pre class="change-data">{{ formatJson(data.datos_antes) }}</pre>
              </div>
              <div v-if="data.datos_despues" class="change-section">
                <h5>Estado Posterior</h5>
                <pre class="change-data">{{ formatJson(data.datos_despues) }}</pre>
              </div>
            </div>
          </div>

          <!-- Análisis de seguridad -->
          <div v-if="isSecurityRelevant()" class="details-section security-section">
            <h4>
              <i class="fas fa-shield-alt"></i>
              Análisis de Seguridad
            </h4>
            <div class="security-analysis">
              <div v-if="isFailedLogin()" class="security-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <span>Intento de login fallido detectado</span>
              </div>
              <div v-if="isSuspiciousIP()" class="security-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <span>IP con múltiples intentos fallidos</span>
              </div>
              <div v-if="isDeleteAction()" class="security-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <span>Acción de eliminación registrada</span>
              </div>
              <div v-if="isErrorAction()" class="security-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <span>Error del sistema registrado</span>
              </div>
            </div>
          </div>
        </div>
      </div>

    <template #footer>
      <div class="flex justify-between items-center w-full">
        <button
          @click="exportEvent"
          class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
        >
          <i class="fas fa-download"></i>
          Exportar Evento
        </button>
        <button 
          @click="closeModal" 
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          Cerrar
        </button>
      </div>
    </template>
  </BaseModal>
</template>

<script>
import { useAuditHelpers } from '@/composables/useAuditHelpers'
import { useDateFormatting } from '@/composables/useDateFormatting'
import BaseModal from '@/components/common/BaseModal.vue'

export default {
  name: 'AuditDetailsModal',
  components: {
    BaseModal
  },
  props: {
    data: {
      type: Object,
      required: true
    },
    auditType: {
      type: String,
      default: 'activity',
      validator: (value) => ['activity', 'login', 'both'].includes(value)
    }
  },
  emits: ['close'],
  setup() {
    const {
      getAuditItemTitle,
      getAuditActionIcon,
      getAuditStatusClass,
      formatJson: formatJsonUtil
    } = useAuditHelpers()

    const { formatDateTime: formatDateTimeUtil, formatDuration: formatDurationUtil } = useDateFormatting()

    return {
      getAuditItemTitle,
      getAuditActionIcon,
      getAuditStatusClass,
      formatDateTimeUtil,
      formatDurationUtil,
      formatJsonUtil
    }
  },
  methods: {
    getHeaderTitle() {
      return this.getAuditItemTitle(this.data, this.auditType)
    },

    getHeaderIcon() {
      if (this.auditType === 'activity' || this.auditType === 'both') {
        return this.getAuditActionIcon(this.data.accion)
      } else if (this.auditType === 'login') {
        return this.data.success ? 'fas fa-check-circle' : 'fas fa-times-circle'
      }
      return 'fas fa-circle'
    },

    getStatusClass() {
      return this.getAuditStatusClass(this.data, this.auditType)
    },

    formatDateTime(dateString) {
      return this.formatDateTimeUtil(dateString)
    },

    formatDuration(durationString) {
      return this.formatDurationUtil(durationString)
    },

    formatJson(data) {
      return this.formatJsonUtil(data)
    },

    isSecurityRelevant() {
      return this.isFailedLogin() || this.isSuspiciousIP() || this.isDeleteAction() || this.isErrorAction()
    },

    isFailedLogin() {
      return this.auditType === 'login' && !this.data.success
    },

    isSuspiciousIP() {
      // Esta lógica podría mejorarse consultando estadísticas de IPs
      return this.data.ip_address && this.data.ip_address.includes('192.168')
    },

    isDeleteAction() {
      return this.auditType === 'activity' && this.data.accion === 'delete'
    },

    isErrorAction() {
      return this.auditType === 'activity' && this.data.accion === 'error'
    },

    exportEvent() {
      // Crear un objeto con los datos del evento para exportar
      const eventData = {
        ...this.data,
        export_timestamp: new Date().toISOString(),
        export_type: this.auditType
      }

      const blob = new Blob([JSON.stringify(eventData, null, 2)], { type: 'application/json' })
      const url = globalThis.URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = `audit_event_${this.data.id}_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      
      link.remove()
      globalThis.URL.revokeObjectURL(url)
    },

    closeModal() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.audit-details-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: linear-gradient(135deg, #1f4e79 0%, #31235d 100%);
  color: #f8fafc;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  width: 3rem;
  height: 3rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.header-text h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-text p {
  margin: 0.25rem 0 0 0;
  opacity: 0.9;
  font-size: 0.875rem;
}

.close-btn {
  background: #0f172a;
  border: none;
  color: #f8fafc;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.details-section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.details-section h4 {
  margin: 0 0 1rem 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.details-section h4 i {
  color: #3b82f6;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
}

.info-value {
  color: #374151;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-success {
  color: #059669;
}

.status-error {
  color: #dc2626;
}

.status-default {
  color: #374151;
}

.changes-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.change-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.change-section h5 {
  margin: 0;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 600;
}

.change-data {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  color: #374151;
  margin: 0;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}

.security-section {
  background: #fef2f2;
  border-color: #fecaca;
}

.security-analysis {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.security-warning {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 0.375rem;
  color: #92400e;
  font-size: 0.875rem;
}

.security-warning i {
  color: #f59e0b;
  font-size: 1rem;
}

.modal-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
}

.footer-left,
.footer-right {
  display: flex;
  gap: 0.75rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
  gap: 0.5rem;
}

.btn-outline {
  background-color: transparent;
  color: #374151;
  border-color: #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.btn-primary {
  background-color: #1f4e79;
  color: #ffffff;
  border-color: #1f4e79;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1a3d5b;
  border-color: #1a3d5b;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container {
    margin: 0.5rem;
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .modal-footer {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .footer-left,
  .footer-right {
    width: 100%;
    justify-content: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .changes-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .audit-details-modal {
    padding: 0.25rem;
  }
  
  .modal-container {
    margin: 0;
    border-radius: 0;
    max-height: 100vh;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .header-icon {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1rem;
  }
  
  .header-text h3 {
    font-size: 1.25rem;
  }
  
  .btn {
    padding: 0.625rem 1rem;
    font-size: 0.8125rem;
  }
}
</style>
