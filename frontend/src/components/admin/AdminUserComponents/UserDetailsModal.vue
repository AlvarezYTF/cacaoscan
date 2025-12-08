<template>
  <BaseModal
    :show="true"
    title="Detalles del Usuario"
    subtitle="Información completa del usuario"
    max-width="4xl"
    @close="closeModal"
  >
    <template #header>
      <div class="flex items-center">
        <div class="bg-blue-100 p-2 rounded-lg mr-3">
          <i class="fas fa-user text-blue-600"></i>
        </div>
        <div>
          <h3 class="text-xl font-bold text-gray-900">Detalles del Usuario</h3>
          <p class="text-sm text-gray-600 mt-1">Información completa del usuario</p>
        </div>
      </div>
    </template>

    <div class="modal-body-content">
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Cargando detalles del usuario...</p>
        </div>

        <div v-else-if="userDetails" class="user-details">
          <!-- Información Básica -->
          <div class="section">
            <h4>
              <i class="fas fa-info-circle"></i>
              Información Básica
            </h4>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">Nombre de Usuario</div>
                <span>{{ userDetails.username }}</span>
              </div>
              <div class="info-item">
                <div class="info-label">Email</div>
                <span>{{ userDetails.email }}</span>
              </div>
              <div class="info-item">
                <div class="info-label">Nombre Completo</div>
                <span>{{ userDetails.first_name }} {{ userDetails.last_name }}</span>
              </div>
              <div class="info-item">
                <div class="info-label">Rol</div>
                <span class="badge" :class="getRoleBadgeClass(userDetails.role)">
                  {{ userDetails.role || 'Sin rol' }}
                </span>
              </div>
              <div class="info-item">
                <div class="info-label">Teléfono</div>
                <span>{{ userDetails.phone || 'No especificado' }}</span>
              </div>
              <div class="info-item">
                <div class="info-label">Ubicación</div>
                <span>{{ userDetails.location || 'No especificada' }}</span>
              </div>
              <div class="info-item">
                <div class="info-label">Organización</div>
                <span>{{ userDetails.organization || 'No especificada' }}</span>
              </div>
              <div class="info-item">
                <div class="info-label">Estado</div>
                <span class="badge" :class="userDetails.is_active ? 'badge-success' : 'badge-danger'">
                  {{ userDetails.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Permisos -->
          <div class="section">
            <h4>
              <i class="fas fa-shield-alt"></i>
              Permisos
            </h4>
            <div class="permissions-grid">
              <div class="permission-item">
                <i class="fas fa-user-shield" :class="userDetails.is_superuser ? 'active' : 'inactive'"></i>
                <span>Superusuario</span>
                <span class="status" :class="userDetails.is_superuser ? 'active' : 'inactive'">
                  {{ userDetails.is_superuser ? 'Sí' : 'No' }}
                </span>
              </div>
              <div class="permission-item">
                <i class="fas fa-users-cog" :class="userDetails.is_staff ? 'active' : 'inactive'"></i>
                <span>Personal Administrativo</span>
                <span class="status" :class="userDetails.is_staff ? 'active' : 'inactive'">
                  {{ userDetails.is_staff ? 'Sí' : 'No' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Información de Cuenta -->
          <div class="section">
            <h4>
              <i class="fas fa-calendar-alt"></i>
              Información de Cuenta
            </h4>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">Fecha de Registro</div>
                <span>{{ formatDateTime(userDetails.date_joined) }}</span>
              </div>
              <div class="info-item">
                <div class="info-label">Último Login</div>
                <span v-if="userDetails.last_login">
                  {{ formatDateTime(userDetails.last_login) }}
                </span>
                <span v-else class="text-muted">Nunca</span>
              </div>
              <div class="info-item">
                <div class="info-label">Última Actividad</div>
                <span v-if="userDetails.last_activity">
                  {{ formatDateTime(userDetails.last_activity) }}
                </span>
                <span v-else class="text-muted">No disponible</span>
              </div>
              <div class="info-item">
                <div class="info-label">Estado de Conexión</div>
                <span class="badge" :class="getConnectionStatusClass(userDetails)">
                  {{ getConnectionStatus(userDetails) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Estadísticas -->
          <div class="section">
            <h4>
              <i class="fas fa-chart-bar"></i>
              Estadísticas
            </h4>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-number">{{ userDetails.total_fincas || 0 }}</div>
                <div class="stat-label">Fincas</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ userDetails.total_lotes || 0 }}</div>
                <div class="stat-label">Lotes</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ userDetails.total_analyses || 0 }}</div>
                <div class="stat-label">Análisis</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ userDetails.total_reports || 0 }}</div>
                <div class="stat-label">Reportes</div>
              </div>
            </div>
          </div>

          <!-- Actividad Reciente -->
          <div class="section">
            <h4>
              <i class="fas fa-history"></i>
              Actividad Reciente
            </h4>
            <div v-if="recentActivities.length === 0" class="no-activity">
              <i class="fas fa-clock"></i>
              <p>No hay actividad reciente</p>
            </div>
            <div v-else class="activity-list">
              <div 
                v-for="activity in recentActivities" 
                :key="activity.id"
                class="activity-item"
              >
                <div class="activity-icon">
                  <i :class="getActivityIcon(activity.accion)"></i>
                </div>
                <div class="activity-content">
                  <div class="activity-description">
                    {{ activity.descripcion }}
                  </div>
                  <div class="activity-meta">
                    <span class="activity-time">{{ formatDateTime(activity.timestamp) }}</span>
                    <span class="activity-ip" v-if="activity.ip_address">
                      IP: {{ activity.ip_address }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Notas -->
          <div v-if="userDetails.notes" class="section">
            <h4>
              <i class="fas fa-sticky-note"></i>
              Notas
            </h4>
            <div class="notes-content">
              {{ userDetails.notes }}
            </div>
          </div>
        </div>
      </div>

    <template #footer>
      <div class="flex items-center justify-end gap-3">
        <button 
          type="button" 
          @click="closeModal"
          class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          Cerrar
        </button>
        <button 
          v-if="canEdit"
          type="button" 
          @click="editUser"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
        >
          <i class="fas fa-edit"></i>
          Editar Usuario
        </button>
      </div>
    </template>
  </BaseModal>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import BaseModal from '@/components/common/BaseModal.vue'

export default {
  name: 'UserDetailsModal',
  components: {
    BaseModal
  },
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'edit'],
  setup(props, { emit }) {
    const adminStore = useAdminStore()

    const loading = ref(false)
    const userDetails = ref(null)
    const recentActivities = ref([])

    // Methods
    const loadUserDetails = async () => {
      loading.value = true
      try {
        const response = await adminStore.getUserById(props.user.id)
        userDetails.value = response.data
        
        // Load recent activities
        await loadRecentActivities()
        
      } catch (error) {
        } finally {
        loading.value = false
      }
    }

    const loadRecentActivities = async () => {
      try {
        const response = await adminStore.getActivityLogs({
          user_id: props.user.id,
          limit: 10
        })
        recentActivities.value = response.data.results
      } catch (error) {
        }
    }

    const closeModal = () => {
      emit('close')
    }

    const editUser = () => {
      emit('edit', userDetails.value)
    }

    const formatDateTime = (date) => {
      return new Date(date).toLocaleString('es-ES')
    }

    const getRoleBadgeClass = (role) => {
      const classes = {
        'Administrador': 'badge-danger',
        'Agricultor': 'badge-success',
        'Técnico': 'badge-info'
      }
      return classes[role] || 'badge-secondary'
    }

    const getConnectionStatus = (user) => {
      if (!user.last_login) return 'Nunca conectado'
      
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000)
      if (new Date(user.last_login) > fiveMinutesAgo) {
        return 'En línea'
      }
      
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
      if (new Date(user.last_login) > oneHourAgo) {
        return 'Reciente'
      }
      
      return 'Desconectado'
    }

    const getConnectionStatusClass = (user) => {
      if (!user.last_login) return 'badge-secondary'
      
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000)
      if (new Date(user.last_login) > fiveMinutesAgo) {
        return 'badge-success'
      }
      
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
      if (new Date(user.last_login) > oneHourAgo) {
        return 'badge-warning'
      }
      
      return 'badge-secondary'
    }

    const getActivityIcon = (action) => {
      const icons = {
        'login': 'fas fa-sign-in-alt',
        'logout': 'fas fa-sign-out-alt',
        'create': 'fas fa-plus',
        'update': 'fas fa-edit',
        'delete': 'fas fa-trash',
        'view': 'fas fa-eye',
        'analysis': 'fas fa-microscope',
        'training': 'fas fa-brain',
        'report': 'fas fa-file-alt'
      }
      return icons[action] || 'fas fa-circle'
    }

    // Lifecycle
    onMounted(() => {
      loadUserDetails()
    })

    return {
      loading,
      userDetails,
      recentActivities,
      loadUserDetails,
      loadRecentActivities,
      closeModal,
      editUser,
      formatDateTime,
      getRoleBadgeClass,
      getConnectionStatus,
      getConnectionStatusClass,
      getActivityIcon
    }
  }
}
</script>

<style scoped>
.modal-overlay {
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
}

.modal-container {
  background: white;
  border-radius: 10px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.modal-header h3 i {
  margin-right: 10px;
  color: #3498db;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #7f8c8d;
  cursor: pointer;
  padding: 5px;
  border-radius: 3px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
}

.loading-state {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.loading-state i {
  font-size: 2rem;
  margin-bottom: 10px;
  color: #3498db;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.section h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section h4 i {
  color: #3498db;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item label,
.info-item .info-label {
  font-weight: 500;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.info-item span {
  color: #2c3e50;
  font-size: 0.95rem;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.permission-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: white;
  border-radius: 5px;
  border: 1px solid #ecf0f1;
}

.permission-item i {
  font-size: 1.2rem;
}

.permission-item i.active {
  color: #27ae60;
}

.permission-item i.inactive {
  color: #95a5a6;
}

.permission-item span:first-of-type {
  flex: 1;
  font-weight: 500;
  color: #2c3e50;
}

.status.active {
  color: #27ae60;
  font-weight: 500;
}

.status.inactive {
  color: #95a5a6;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: white;
  border-radius: 8px;
  border: 1px solid #ecf0f1;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.no-activity {
  text-align: center;
  padding: 30px;
  color: #7f8c8d;
}

.no-activity i {
  font-size: 2rem;
  margin-bottom: 10px;
  color: #bdc3c7;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #ecf0f1;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon i {
  font-size: 0.9rem;
  color: #3498db;
}

.activity-content {
  flex: 1;
}

.activity-description {
  color: #2c3e50;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.activity-meta {
  display: flex;
  gap: 15px;
  font-size: 0.8rem;
  color: #7f8c8d;
}

.notes-content {
  background: white;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #ecf0f1;
  color: #2c3e50;
  line-height: 1.5;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.badge-success {
  background-color: #d4edda;
  color: #155724;
}

.badge-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.badge-warning {
  background-color: #fff3cd;
  color: #856404;
}

.badge-info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.badge-secondary {
  background-color: #e2e3e5;
  color: #383d41;
}

.text-muted {
  color: #7f8c8d;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-secondary {
  background-color: #6b7280;
  color: #ffffff;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

.btn-primary {
  background-color: #2563eb;
  color: #ffffff;
}

.btn-primary:hover {
  background-color: #2980b9;
}

@media (max-width: 768px) {
  .modal-container {
    width: 95%;
    margin: 10px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .permissions-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
