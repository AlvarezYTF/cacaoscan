<template>
  <div class="audit-stats-modal" @click="closeModal">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <div class="header-content">
          <div class="header-icon">
            <i class="fas fa-chart-bar"></i>
          </div>
          <div class="header-text">
            <h3>Estadísticas Detalladas de Auditoría</h3>
            <p>Análisis completo de la actividad del sistema</p>
          </div>
        </div>
        <button class="close-btn" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <div class="stats-content">
          <!-- Resumen general -->
          <div class="stats-section">
            <h4>
              <i class="fas fa-tachometer-alt"></i>
              Resumen General
            </h4>
            <div class="summary-grid">
              <div class="summary-card">
                <div class="summary-icon">
                  <i class="fas fa-activity"></i>
                </div>
                <div class="summary-content">
                  <div class="summary-value">{{ stats.activity_log?.total_activities || 0 }}</div>
                  <div class="summary-label">Actividades Totales</div>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-icon">
                  <i class="fas fa-calendar-day"></i>
                </div>
                <div class="summary-content">
                  <div class="summary-value">{{ stats.activity_log?.activities_today || 0 }}</div>
                  <div class="summary-label">Actividades Hoy</div>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-icon">
                  <i class="fas fa-sign-in-alt"></i>
                </div>
                <div class="summary-content">
                  <div class="summary-value">{{ stats.login_history?.total_logins || 0 }}</div>
                  <div class="summary-label">Logins Totales</div>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-icon">
                  <i class="fas fa-percentage"></i>
                </div>
                <div class="summary-content">
                  <div class="summary-value">{{ Math.round(stats.login_history?.success_rate || 0) }}%</div>
                  <div class="summary-label">Tasa de Éxito</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actividades por acción -->
          <div v-if="stats.activity_log?.activities_by_action" class="stats-section">
            <h4>
              <i class="fas fa-tasks"></i>
              Actividades por Acción
            </h4>
            <div class="chart-container">
              <div class="chart-grid">
                <div 
                  v-for="(count, action) in stats.activity_log.activities_by_action" 
                  :key="action"
                  class="chart-item"
                >
                  <div class="chart-bar">
                    <div 
                      class="chart-fill"
                      :style="{ height: getBarHeight(count, stats.activity_log.total_activities) }"
                    ></div>
                  </div>
                  <div class="chart-label">{{ getActionLabel(action) }}</div>
                  <div class="chart-value">{{ count }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actividades por modelo -->
          <div v-if="stats.activity_log?.activities_by_model" class="stats-section">
            <h4>
              <i class="fas fa-cube"></i>
              Actividades por Modelo
            </h4>
            <div class="model-stats">
              <div 
                v-for="(count, model) in stats.activity_log.activities_by_model" 
                :key="model"
                class="model-item"
              >
                <div class="model-name">{{ model }}</div>
                <div class="model-bar">
                  <div 
                    class="model-fill"
                    :style="{ width: getBarWidth(count, stats.activity_log.total_activities) }"
                  ></div>
                </div>
                <div class="model-count">{{ count }}</div>
              </div>
            </div>
          </div>

          <!-- Top usuarios activos -->
          <div v-if="stats.activity_log?.top_active_users?.length" class="stats-section">
            <h4>
              <i class="fas fa-users"></i>
              Usuarios Más Activos
            </h4>
            <div class="users-list">
              <div 
                v-for="(user, index) in stats.activity_log.top_active_users" 
                :key="user.usuario__username"
                class="user-item"
              >
                <div class="user-rank">{{ index + 1 }}</div>
                <div class="user-info">
                  <div class="user-name">{{ user.usuario__username || 'Usuario Anónimo' }}</div>
                  <div class="user-activity">{{ user.count }} actividades</div>
                </div>
                <div class="user-bar">
                  <div 
                    class="user-fill"
                    :style="{ width: getBarWidth(user.count, stats.activity_log.top_active_users[0].count) }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Estadísticas de login por día -->
          <div v-if="stats.login_history?.login_stats_by_day?.length" class="stats-section">
            <h4>
              <i class="fas fa-calendar-week"></i>
              Logins por Día (Últimos 7 días)
            </h4>
            <div class="daily-stats">
              <div 
                v-for="day in stats.login_history.login_stats_by_day" 
                :key="day.date"
                class="day-item"
              >
                <div class="day-date">{{ formatDate(day.date) }}</div>
                <div class="day-bar">
                  <div 
                    class="day-fill"
                    :style="{ height: getBarHeight(day.count, getMaxDailyLogins()) }"
                  ></div>
                </div>
                <div class="day-count">{{ day.count }}</div>
              </div>
            </div>
          </div>

          <!-- Top IPs -->
          <div v-if="stats.login_history?.top_ips?.length" class="stats-section">
            <h4>
              <i class="fas fa-globe"></i>
              Direcciones IP Más Frecuentes
            </h4>
            <div class="ips-list">
              <div 
                v-for="(ip, index) in stats.login_history.top_ips" 
                :key="ip.ip_address"
                class="ip-item"
              >
                <div class="ip-rank">{{ index + 1 }}</div>
                <div class="ip-address">{{ ip.ip_address }}</div>
                <div class="ip-bar">
                  <div 
                    class="ip-fill"
                    :style="{ width: getBarWidth(ip.count, stats.login_history.top_ips[0].count) }"
                  ></div>
                </div>
                <div class="ip-count">{{ ip.count }}</div>
              </div>
            </div>
          </div>

          <!-- Duración promedio de sesión -->
          <div v-if="stats.login_history?.avg_session_duration_minutes" class="stats-section">
            <h4>
              <i class="fas fa-clock"></i>
              Duración Promedio de Sesión
            </h4>
            <div class="duration-info">
              <div class="duration-value">
                {{ Math.round(stats.login_history.avg_session_duration_minutes) }} minutos
              </div>
              <div class="duration-label">
                Tiempo promedio que los usuarios permanecen conectados
              </div>
            </div>
          </div>

          <!-- Información de generación -->
          <div class="stats-section">
            <h4>
              <i class="fas fa-info-circle"></i>
              Información del Reporte
            </h4>
            <div class="report-info">
              <div class="info-item">
                <span class="info-label">Generado el:</span>
                <span class="info-value">{{ formatDateTime(stats.generated_at) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Período:</span>
                <span class="info-value">Desde el inicio del sistema</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <div class="footer-left">
          <button
            @click="exportStats"
            class="btn btn-outline"
          >
            <i class="fas fa-download"></i>
            Exportar Estadísticas
          </button>
        </div>

        <div class="footer-right">
          <button @click="closeModal" class="btn btn-primary">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuditStatsModal',
  props: {
    stats: {
      type: Object,
      required: true
    }
  },
  emits: ['close'],
  methods: {
    getActionLabel(action) {
      const labels = {
        'login': 'Login',
        'logout': 'Logout',
        'create': 'Crear',
        'update': 'Actualizar',
        'delete': 'Eliminar',
        'view': 'Ver',
        'download': 'Descargar',
        'upload': 'Subir',
        'analysis': 'Análisis',
        'training': 'Entrenar',
        'report': 'Reporte',
        'error': 'Error'
      }
      return labels[action] || action
    },

    getBarHeight(value, max) {
      if (!max || max === 0) return '0%'
      return `${(value / max) * 100}%`
    },

    getBarWidth(value, max) {
      if (!max || max === 0) return '0%'
      return `${(value / max) * 100}%`
    },

    getMaxDailyLogins() {
      if (!this.stats.login_history?.login_stats_by_day?.length) return 1
      return Math.max(...this.stats.login_history.login_stats_by_day.map(day => day.count))
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('es-ES', {
        weekday: 'short',
        month: 'short',
        day: 'numeric'
      })
    },

    formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    exportStats() {
      const statsData = {
        ...this.stats,
        export_timestamp: new Date().toISOString(),
        export_type: 'audit_statistics'
      }

      const blob = new Blob([JSON.stringify(statsData, null, 2)], { type: 'application/json' })
      const url = globalThis.URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = `audit_statistics_${new Date().toISOString().split('T')[0]}.json`
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
.audit-stats-modal {
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
  max-width: 1000px;
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
  background-color: #0f172a;
  border: none;
  color: #ffffff;
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
  background-color: #1a2640;
  color: #ffffff;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.stats-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.stats-section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.stats-section h4 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stats-section h4 i {
  color: #3b82f6;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.summary-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: #1f4e79;
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.summary-content {
  flex: 1;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.summary-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.chart-container {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.chart-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.chart-bar {
  width: 20px;
  height: 100px;
  background: #e5e7eb;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.chart-fill {
  position: absolute;
  bottom: 0;
  width: 100%;
  background: #3b82f6;
  border-radius: 10px;
  transition: height 0.3s ease;
}

.chart-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-align: center;
  font-weight: 500;
}

.chart-value {
  font-size: 0.875rem;
  color: #374151;
  font-weight: 600;
}

.model-stats {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.model-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.model-name {
  min-width: 120px;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.model-bar {
  flex: 1;
  height: 20px;
  background: #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.model-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: #10b981;
  border-radius: 10px;
  transition: width 0.3s ease;
}

.model-count {
  min-width: 40px;
  text-align: right;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.user-rank {
  width: 2rem;
  height: 2rem;
  background: #1f4e79;
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.user-activity {
  color: #6b7280;
  font-size: 0.75rem;
}

.user-bar {
  width: 100px;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.user-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: #3b82f6;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.daily-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1rem;
}

.day-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.day-date {
  font-size: 0.75rem;
  color: #6b7280;
  text-align: center;
  font-weight: 500;
}

.day-bar {
  width: 20px;
  height: 80px;
  background: #e5e7eb;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.day-fill {
  position: absolute;
  bottom: 0;
  width: 100%;
  background: #10b981;
  border-radius: 10px;
  transition: height 0.3s ease;
}

.day-count {
  font-size: 0.875rem;
  color: #374151;
  font-weight: 600;
}

.ips-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ip-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.ip-rank {
  width: 2rem;
  height: 2rem;
  background: #8a4b00;
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.ip-address {
  min-width: 120px;
  font-family: 'Courier New', monospace;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.ip-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.ip-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: #f59e0b;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.ip-count {
  min-width: 40px;
  text-align: right;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.duration-info {
  text-align: center;
  padding: 2rem;
  background: #f0f9ff;
  border-radius: 0.5rem;
  border: 1px solid #bae6fd;
}

.duration-value {
  font-size: 2rem;
  font-weight: 700;
  color: #0369a1;
  margin-bottom: 0.5rem;
}

.duration-label {
  color: #0284c7;
  font-size: 0.875rem;
}

.report-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
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
  
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .daily-stats {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 480px) {
  .audit-stats-modal {
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
  
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .daily-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .btn {
    padding: 0.625rem 1rem;
    font-size: 0.8125rem;
  }
}
</style>
