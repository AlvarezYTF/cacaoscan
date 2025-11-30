<template>
  <div class="audit-table-container">
    <div v-if="loading" class="table-loading">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
      <p>Cargando datos de auditoría...</p>
    </div>

    <div v-else-if="data.length === 0" class="table-empty">
      <div class="empty-icon">
        <i class="fas fa-clipboard-list"></i>
      </div>
      <h3>No hay datos</h3>
      <p>No se encontraron registros que coincidan con los filtros aplicados.</p>
    </div>

    <div v-else class="table-wrapper">
      <div class="table-header">
        <h3>{{ getTableTitle() }}</h3>
        <div class="table-info">
          <span>{{ data.length }} registros</span>
        </div>
      </div>

      <div class="table-responsive">
        <table class="audit-table" aria-label="Tabla de registros de auditoría">
          <caption class="sr-only">Tabla de auditoría mostrando registros de actividad del sistema</caption>
          <thead>
            <tr>
              <th 
                v-for="column in getColumns()" 
                :key="column.key"
                :class="{ 
                  'sortable': column.sortable,
                  'sorted': column.sortable && sortKey === column.key
                }"
                @click="column.sortable ? handleSortClick(column.key) : null"
              >
                <div class="th-content">
                  <span>{{ column.label }}</span>
                  <i v-if="column.sortable && sortKey === column.key" 
                     :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'"
                     class="sort-icon"></i>
                  <i v-else-if="column.sortable" class="fas fa-sort sort-icon inactive"></i>
                </div>
              </th>
              <th class="actions-column">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in data" :key="item.id" class="table-row">
              <!-- Columnas dinámicas según el tipo de auditoría -->
              <td v-if="auditType === 'activity' || auditType === 'both'">
                <div class="user-info">
                  <div class="user-avatar">
                    <i class="fas fa-user"></i>
                  </div>
                  <div class="user-details">
                    <div class="username">{{ item.usuario || 'Usuario Anónimo' }}</div>
                    <div class="ip-address">{{ item.ip_address || 'N/A' }}</div>
                  </div>
                </div>
              </td>

              <td v-if="auditType === 'login' || auditType === 'both'">
                <div class="user-info">
                  <div class="user-avatar">
                    <i class="fas fa-user"></i>
                  </div>
                  <div class="user-details">
                    <div class="username">{{ item.usuario }}</div>
                    <div class="ip-address">{{ item.ip_address }}</div>
                  </div>
                </div>
              </td>

              <td v-if="auditType === 'activity' || auditType === 'both'">
                <div class="action-badge" :class="getActionClass(item.accion)">
                  <i :class="getActionIcon(item.accion)"></i>
                  <span>{{ item.accion_display || item.accion }}</span>
                </div>
              </td>

              <td v-if="auditType === 'login' || auditType === 'both'">
                <div class="status-badge" :class="item.success ? 'status-success' : 'status-error'">
                  <i :class="item.success ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
                  <span>{{ item.success ? 'Exitoso' : 'Fallido' }}</span>
                </div>
              </td>

              <td v-if="auditType === 'activity' || auditType === 'both'">
                <div class="model-info">
                  <div class="model-name">{{ item.modelo }}</div>
                  <div v-if="item.objeto_id" class="object-id">ID: {{ item.objeto_id }}</div>
                </div>
              </td>

              <td v-if="auditType === 'login' || auditType === 'both'">
                <div class="session-info">
                  <div class="login-time">{{ formatDateTime(item.login_time) }}</div>
                  <div v-if="item.logout_time" class="logout-time">
                    Cierre: {{ formatDateTime(item.logout_time) }}
                  </div>
                  <div v-if="item.session_duration" class="session-duration">
                    Duración: {{ formatDuration(item.session_duration) }}
                  </div>
                </div>
              </td>

              <td v-if="auditType === 'activity' || auditType === 'both'">
                <div class="description">
                  {{ truncateText(item.descripcion, 50) }}
                </div>
              </td>

              <td v-if="auditType === 'login' || auditType === 'both'">
                <div v-if="item.failure_reason" class="failure-reason">
                  {{ item.failure_reason }}
                </div>
                <div v-else class="success-message">
                  Login exitoso
                </div>
              </td>

              <td>
                <div class="timestamp">
                  <div class="date">{{ formatDate(item.timestamp || item.login_time) }}</div>
                  <div class="time">{{ formatTime(item.timestamp || item.login_time) }}</div>
                </div>
              </td>

              <td class="actions-cell">
                <div class="action-buttons">
                  <button
                    @click="$emit('view-details', item, auditType)"
                    class="btn btn-sm btn-outline"
                    title="Ver detalles"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { useTable } from '@/composables/useTable'
import { useAuditHelpers } from '@/composables/useAuditHelpers'
import { useDateFormatting } from '@/composables/useDateFormatting'
import { formatDate as formatDateUtil, formatDateTime as formatDateTimeUtil } from '@/utils/formatters'

export default {
  name: 'AuditTable',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    auditType: {
      type: String,
      default: 'activity',
      validator: (value) => ['activity', 'login', 'both'].includes(value)
    }
  },
  emits: ['view-details', 'sort'],
  setup(props, { emit }) {
    // Use table composable for sorting
    const table = useTable({
      initialSortKey: '',
      initialSortOrder: 'asc',
      enableSelection: false
    })

    // Use audit helpers
    const {
      getAuditActionIcon,
      getAuditActionMarkerClass
    } = useAuditHelpers()

    // Use date formatting (formatDateTime from centralized formatters, formatDuration from composable)
    const { formatDuration: formatDurationUtil } = useDateFormatting()

    // Handle sort with emit
    const handleSortClick = (key) => {
      table.handleSort(key)
      emit('sort', {
        key: table.sortKey.value,
        order: table.sortOrder.value
      })
    }

    return {
      ...table,
      handleSortClick,
      getAuditActionIcon,
      getAuditActionMarkerClass,
      formatDateTimeUtil,
      formatDurationUtil
    }
  },
  methods: {
    getTableTitle() {
      switch (this.auditType) {
        case 'activity':
          return 'Logs de Actividad'
        case 'login':
          return 'Historial de Logins'
        case 'both':
          return 'Auditoría Completa'
        default:
          return 'Datos de Auditoría'
      }
    },

    getColumns() {
      if (this.auditType === 'activity') {
        return [
          { key: 'usuario', label: 'Usuario', sortable: true },
          { key: 'accion', label: 'Acción', sortable: true },
          { key: 'modelo', label: 'Modelo', sortable: true },
          { key: 'descripcion', label: 'Descripción', sortable: false },
          { key: 'timestamp', label: 'Fecha/Hora', sortable: true }
        ]
      } else if (this.auditType === 'login') {
        return [
          { key: 'usuario', label: 'Usuario', sortable: true },
          { key: 'success', label: 'Estado', sortable: true },
          { key: 'login_time', label: 'Sesión', sortable: true },
          { key: 'failure_reason', label: 'Detalles', sortable: false },
          { key: 'timestamp', label: 'Fecha/Hora', sortable: true }
        ]
      } else {
        return [
          { key: 'usuario', label: 'Usuario', sortable: true },
          { key: 'type', label: 'Tipo', sortable: true },
          { key: 'details', label: 'Detalles', sortable: false },
          { key: 'timestamp', label: 'Fecha/Hora', sortable: true }
        ]
      }
    },

    getActionClass(action) {
      const classes = {
        'login': 'action-login',
        'logout': 'action-logout',
        'create': 'action-create',
        'update': 'action-update',
        'delete': 'action-delete',
        'view': 'action-view',
        'download': 'action-download',
        'upload': 'action-upload',
        'analysis': 'action-analysis',
        'training': 'action-training',
        'report': 'action-report',
        'error': 'action-error'
      }
      return classes[action] || 'action-default'
    },

    getActionIcon(action) {
      return this.getAuditActionIcon(action)
    },

    formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      return this.formatDateTimeUtil(dateString)
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return formatDateUtil(dateString, { dateStyle: 'short' })
    },

    formatTime(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },

    formatDuration(durationString) {
      if (!durationString) return 'N/A'
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
.audit-table-container {
  width: 100%;
}

.table-loading,
.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.loading-spinner {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #3b82f6;
}

.empty-icon {
  font-size: 3rem;
  color: #d1d5db;
  margin-bottom: 1rem;
}

.empty-icon i {
  opacity: 0.5;
}

.table-empty h3 {
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 1.25rem;
  font-weight: 600;
}

.table-empty p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.table-wrapper {
  background: white;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.table-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
}

.table-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
}

.table-info {
  color: #6b7280;
  font-size: 0.875rem;
}

.table-responsive {
  overflow-x: auto;
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
}

.audit-table th {
  background: #f8fafc;
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  border-bottom: 1px solid #e5e7eb;
}

.audit-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.audit-table th.sortable:hover {
  background: #f1f5f9;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-icon {
  color: #9ca3af;
  font-size: 0.75rem;
}

.actions-column {
  width: 100px;
  text-align: center;
}

.audit-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  font-size: 0.875rem;
}

.table-row:hover {
  background: #f8fafc;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  background: #e5e7eb;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #374151;
  font-size: 0.875rem;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.username {
  font-weight: 500;
  color: #374151;
}

.ip-address {
  color: #6b7280;
  font-size: 0.75rem;
}

.action-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.action-login {
  background: #dbeafe;
  color: #1e40af;
}

.action-logout {
  background: #fef3c7;
  color: #92400e;
}

.action-create {
  background: #d1fae5;
  color: #065f46;
}

.action-update {
  background: #dbeafe;
  color: #1e40af;
}

.action-delete {
  background: #fee2e2;
  color: #991b1b;
}

.action-view {
  background: #f3e8ff;
  color: #7c3aed;
}

.action-download {
  background: #ecfdf5;
  color: #047857;
}

.action-upload {
  background: #f0f9ff;
  color: #0369a1;
}

.action-analysis {
  background: #fef3c7;
  color: #92400e;
}

.action-training {
  background: #f3e8ff;
  color: #7c3aed;
}

.action-report {
  background: #ecfdf5;
  color: #047857;
}

.action-error {
  background: #fee2e2;
  color: #991b1b;
}

.action-default {
  background: #f3f4f6;
  color: #374151;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
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

.model-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.model-name {
  font-weight: 500;
  color: #374151;
}

.object-id {
  color: #6b7280;
  font-size: 0.75rem;
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.login-time {
  font-weight: 500;
  color: #374151;
}

.logout-time,
.session-duration {
  color: #6b7280;
  font-size: 0.75rem;
}

.description {
  color: #6b7280;
  line-height: 1.4;
}

.failure-reason {
  color: #dc2626;
  font-size: 0.75rem;
}

.success-message {
  color: #059669;
  font-size: 0.75rem;
}

.timestamp {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.date {
  font-weight: 500;
  color: #374151;
}

.time {
  color: #6b7280;
  font-size: 0.75rem;
}

.actions-cell {
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
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
@media (max-width: 768px) {
  .table-responsive {
    font-size: 0.75rem;
  }
  
  .audit-table th,
  .audit-table td {
    padding: 0.5rem 0.75rem;
  }
  
  .user-info {
    gap: 0.5rem;
  }
  
  .user-avatar {
    width: 1.5rem;
    height: 1.5rem;
    font-size: 0.75rem;
  }
  
  .action-badge,
  .status-badge {
    padding: 0.125rem 0.5rem;
    font-size: 0.625rem;
  }
}

@media (max-width: 640px) {
  .table-header {
    padding: 0.75rem 1rem;
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .audit-table th,
  .audit-table td {
    padding: 0.375rem 0.5rem;
  }
  
  .th-content {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .sort-icon {
    display: none;
  }
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
