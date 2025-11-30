<template>
  <div class="audit-card" :class="getCardClass()">
    <div class="card-header">
      <div class="card-icon">
        <i :class="getCardIcon()"></i>
      </div>
      <div class="card-title">
        <h4>{{ getCardTitle() }}</h4>
        <div class="card-meta">
          <span class="item-type">{{ getItemType() }}</span>
          <span class="item-status" :class="getStatusClass()">
            {{ getItemStatus() }}
          </span>
        </div>
      </div>
    </div>

    <div class="card-body">
      <div class="item-info">
        <div class="info-item">
          <i class="fas fa-user"></i>
          <span>{{ data.usuario || 'Usuario Anónimo' }}</span>
        </div>
        <div class="info-item">
          <i class="fas fa-globe"></i>
          <span>{{ data.ip_address || 'N/A' }}</span>
        </div>
        <div v-if="auditType === 'activity' || auditType === 'both'" class="info-item">
          <i class="fas fa-cube"></i>
          <span>{{ data.modelo }}</span>
        </div>
        <div v-if="auditType === 'login' || auditType === 'both'" class="info-item">
          <i class="fas fa-clock"></i>
          <span>{{ formatDuration(data.session_duration) }}</span>
        </div>
      </div>

      <div v-if="auditType === 'activity' || auditType === 'both'" class="item-description">
        <p>{{ truncateText(data.descripcion, 100) }}</p>
      </div>

      <div v-if="auditType === 'login' || auditType === 'both'" class="session-info">
        <div class="session-item">
          <span class="session-label">Inicio:</span>
          <span class="session-value">{{ formatDateTime(data.login_time) }}</span>
        </div>
        <div v-if="data.logout_time" class="session-item">
          <span class="session-label">Cierre:</span>
          <span class="session-value">{{ formatDateTime(data.logout_time) }}</span>
        </div>
        <div v-if="data.failure_reason" class="session-item">
          <span class="session-label">Error:</span>
          <span class="session-value error">{{ data.failure_reason }}</span>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <div class="timestamp">
        <i class="fas fa-calendar"></i>
        <span>{{ formatDateTime(data.timestamp || data.login_time) }}</span>
      </div>
      <div class="card-actions">
        <button
          @click="$emit('view-details', data, auditType)"
          class="btn btn-sm btn-outline"
        >
          <i class="fas fa-eye"></i>
          Ver Detalles
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useDateFormatting } from '@/composables/useDateFormatting'
import { useAuditHelpers } from '@/composables/useAuditHelpers'

export default {
  name: 'AuditCard',
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
  emits: ['view-details'],
  setup() {
    const { formatDateTime: formatDateTimeUtil, formatDuration: formatDurationUtil } = useDateFormatting()
    const {
      getAuditItemTitle,
      getAuditItemType,
      getAuditItemStatus,
      getAuditActionMarkerClass,
      getAuditActionIcon,
      getAuditStatusClass
    } = useAuditHelpers()

    return {
      formatDateTimeUtil,
      formatDurationUtil,
      getAuditItemTitle,
      getAuditItemType,
      getAuditItemStatus,
      getAuditActionMarkerClass,
      getAuditActionIcon,
      getAuditStatusClass
    }
  },
  methods: {
    getCardTitle() {
      return this.getAuditItemTitle(this.data, this.auditType)
    },

    getItemType() {
      return this.getAuditItemType(this.auditType)
    },

    getItemStatus() {
      return this.getAuditItemStatus(this.data, this.auditType)
    },

    getCardClass() {
      if (this.auditType === 'activity' || this.auditType === 'both') {
        const markerClass = this.getAuditActionMarkerClass(this.data.accion)
        return markerClass.replace('marker-', 'card-')
      } else if (this.auditType === 'login') {
        return this.data.success ? 'card-success' : 'card-error'
      }
      return 'card-default'
    },

    getCardIcon() {
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

    truncateText(text, maxLength) {
      if (!text) return 'N/A'
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }
  }
}
</script>

<style scoped>
.audit-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  overflow: hidden;
  transition: all 0.2s;
  cursor: pointer;
}

.audit-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.card-login {
  border-left: 4px solid #3b82f6;
}

.card-logout {
  border-left: 4px solid #f59e0b;
}

.card-create {
  border-left: 4px solid #10b981;
}

.card-update {
  border-left: 4px solid #3b82f6;
}

.card-delete {
  border-left: 4px solid #ef4444;
}

.card-view {
  border-left: 4px solid #8b5cf6;
}

.card-download {
  border-left: 4px solid #059669;
}

.card-upload {
  border-left: 4px solid #0284c7;
}

.card-analysis {
  border-left: 4px solid #f59e0b;
}

.card-training {
  border-left: 4px solid #8b5cf6;
}

.card-report {
  border-left: 4px solid #059669;
}

.card-error {
  border-left: 4px solid #ef4444;
}

.card-success {
  border-left: 4px solid #10b981;
}

.card-default {
  border-left: 4px solid #6b7280;
}

.card-header {
  padding: 1rem 1.25rem 0.75rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.card-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: #374151;
}

.card-login .card-icon {
  background: #dbeafe;
  color: #1e40af;
}

.card-logout .card-icon {
  background: #fef3c7;
  color: #92400e;
}

.card-create .card-icon {
  background: #d1fae5;
  color: #065f46;
}

.card-update .card-icon {
  background: #dbeafe;
  color: #1e40af;
}

.card-delete .card-icon {
  background: #fee2e2;
  color: #991b1b;
}

.card-view .card-icon {
  background: #f3e8ff;
  color: #7c3aed;
}

.card-download .card-icon {
  background: #ecfdf5;
  color: #047857;
}

.card-upload .card-icon {
  background: #f0f9ff;
  color: #0369a1;
}

.card-analysis .card-icon {
  background: #fef3c7;
  color: #92400e;
}

.card-training .card-icon {
  background: #f3e8ff;
  color: #7c3aed;
}

.card-report .card-icon {
  background: #ecfdf5;
  color: #047857;
}

.card-error .card-icon {
  background: #fee2e2;
  color: #991b1b;
}

.card-success .card-icon {
  background: #d1fae5;
  color: #065f46;
}

.card-title {
  flex: 1;
}

.card-title h4 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
}

.card-meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.item-type {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.item-status {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-success {
  background: #d1fae5;
  color: #065f46;
}

.status-error {
  background: #fee2e2;
  color: #991b1b;
}

.status-default {
  background: #f3f4f6;
  color: #374151;
}

.card-body {
  padding: 0 1.25rem 1rem;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.info-item i {
  width: 1rem;
  color: #9ca3af;
}

.item-description {
  margin-bottom: 1rem;
}

.item-description p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-label {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
}

.session-value {
  color: #374151;
  font-size: 0.875rem;
}

.session-value.error {
  color: #dc2626;
}

.card-footer {
  padding: 0.75rem 1.25rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f3f4f6;
}

.timestamp {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.timestamp i {
  color: #9ca3af;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
  gap: 0.25rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
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

/* Responsive */
@media (max-width: 640px) {
  .card-header {
    padding: 0.75rem 1rem 0.5rem;
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
  
  .card-body {
    padding: 0 1rem 0.75rem;
  }
  
  .card-footer {
    padding: 0.5rem 1rem 0.75rem;
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .card-actions {
    justify-content: center;
  }
  
  .btn {
    flex: 1;
    justify-content: center;
  }
  
  .card-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
