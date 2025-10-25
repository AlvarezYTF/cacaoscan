<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
    <!-- Recent Users Table -->
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900">{{ usersTableTitle }}</h3>
        <router-link 
          :to="usersTableLink" 
          class="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          {{ usersTableLinkText }}
        </router-link>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-gray-500">
          <thead class="text-xs text-gray-700 uppercase bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3">Usuario</th>
              <th scope="col" class="px-6 py-3">Email</th>
              <th scope="col" class="px-6 py-3">Rol</th>
              <th scope="col" class="px-6 py-3">Estado</th>
              <th scope="col" class="px-6 py-3">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="user in recentUsers" 
              :key="user.id" 
              class="bg-white border-b hover:bg-gray-50"
            >
              <td class="px-6 py-4">
                <div class="flex items-center">
                  <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                    <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                    </svg>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ user.first_name }} {{ user.last_name }}
                    </div>
                    <div class="text-sm text-gray-500">@{{ user.username }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ user.email }}</td>
              <td class="px-6 py-4">
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                  :class="getRoleBadgeClass(user.role)"
                >
                  {{ user.role }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                  :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ user.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center space-x-2">
                  <button 
                    @click="handleViewUser(user.id)" 
                    class="text-blue-600 hover:text-blue-800 p-1 rounded hover:bg-blue-50"
                    :title="`Ver usuario ${user.username}`"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>
                  </button>
                  <button 
                    @click="handleEditUser(user.id)" 
                    class="text-amber-600 hover:text-amber-800 p-1 rounded hover:bg-amber-50"
                    :title="`Editar usuario ${user.username}`"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Recent Activity Table -->
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900">{{ activityTableTitle }}</h3>
        <router-link 
          :to="activityTableLink" 
          class="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          {{ activityTableLinkText }}
        </router-link>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-gray-500">
          <thead class="text-xs text-gray-700 uppercase bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3">Usuario</th>
              <th scope="col" class="px-6 py-3">Acción</th>
              <th scope="col" class="px-6 py-3">Modelo</th>
              <th scope="col" class="px-6 py-3">Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="activity in recentActivities" 
              :key="activity.id" 
              class="bg-white border-b hover:bg-gray-50"
            >
              <td class="px-6 py-4 text-sm text-gray-900">
                {{ activity.usuario || 'Anónimo' }}
              </td>
              <td class="px-6 py-4">
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                  :class="getActionBadgeClass(activity.accion)"
                >
                  {{ activity.accion_display }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ activity.modelo }}</td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ formatDateTime(activity.timestamp) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardTables',
  props: {
    usersTableTitle: {
      type: String,
      default: 'Usuarios Recientes'
    },
    usersTableLink: {
      type: String,
      default: '/admin/users'
    },
    usersTableLinkText: {
      type: String,
      default: 'Ver Todos'
    },
    activityTableTitle: {
      type: String,
      default: 'Actividad Reciente'
    },
    activityTableLink: {
      type: String,
      default: '/admin/audit'
    },
    activityTableLinkText: {
      type: String,
      default: 'Ver Auditoría'
    },
    recentUsers: {
      type: Array,
      default: () => []
    },
    recentActivities: {
      type: Array,
      default: () => []
    }
  },
  emits: ['view-user', 'edit-user'],
  methods: {
    handleViewUser(userId) {
      this.$emit('view-user', userId)
    },
    
    handleEditUser(userId) {
      this.$emit('edit-user', userId)
    },
    
    getRoleBadgeClass(role) {
      const roleClasses = {
        'admin': 'bg-purple-100 text-purple-800',
        'staff': 'bg-blue-100 text-blue-800',
        'user': 'bg-gray-100 text-gray-800',
        'superuser': 'bg-red-100 text-red-800'
      }
      return roleClasses[role?.toLowerCase()] || 'bg-gray-100 text-gray-800'
    },
    
    getActionBadgeClass(action) {
      const actionClasses = {
        'create': 'bg-green-100 text-green-800',
        'update': 'bg-blue-100 text-blue-800',
        'delete': 'bg-red-100 text-red-800',
        'view': 'bg-gray-100 text-gray-800',
        'login': 'bg-purple-100 text-purple-800',
        'logout': 'bg-orange-100 text-orange-800'
      }
      return actionClasses[action?.toLowerCase()] || 'bg-gray-100 text-gray-800'
    },
    
    formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
/* Hover effects for table rows */
.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}

/* Hover effects for action buttons */
.hover\:bg-blue-50:hover {
  background-color: #eff6ff;
}

.hover\:bg-amber-50:hover {
  background-color: #fffbeb;
}

/* Table responsive adjustments */
@media (max-width: 768px) {
  .overflow-x-auto {
    -webkit-overflow-scrolling: touch;
  }
}

/* Smooth transitions */
button {
  transition: all 0.2s ease-in-out;
}

/* Focus states for accessibility */
button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
</style>
