<template>
  <div class="grid grid-cols-1 gap-6">
    <!-- Recent Users Table -->
    <div class="bg-white rounded-2xl border-2 border-gray-200 overflow-hidden hover:shadow-xl hover:border-green-300 transition-all duration-300">
      <div class="px-6 py-4 border-b-2 border-gray-200 bg-gray-50 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-green-100 rounded-lg">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900">{{ usersTableTitle }}</h3>
        </div>
        <router-link 
          :to="usersTableLink" 
          class="text-sm text-green-600 hover:text-green-700 font-semibold transition-colors duration-200 flex items-center gap-1 hover:gap-2"
        >
          {{ usersTableLinkText }}
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </router-link>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-gray-500">
          <thead class="text-xs text-gray-700 uppercase bg-gray-100 font-bold">
            <tr>
              <th scope="col" class="px-6 py-3">Usuario</th>
              <th scope="col" class="px-6 py-3">Email</th>
              <th scope="col" class="px-6 py-3">Rol</th>
              <th scope="col" class="px-6 py-3">Estado</th>
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
                  <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                    <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
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
                  :class="getRoleBadgeClass(user.role || 'user')"
                >
                  {{ getRoleDisplayName(user.role || 'user') }}
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
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Recent Activity Table -->
    <div class="bg-white rounded-2xl border-2 border-gray-200 overflow-hidden hover:shadow-xl hover:border-green-300 transition-all duration-300">
      <div class="px-6 py-4 border-b-2 border-gray-200 bg-gray-50 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-green-100 rounded-lg">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900">{{ activityTableTitle }}</h3>
        </div>
        <router-link 
          :to="activityTableLink" 
          class="text-sm text-green-600 hover:text-green-700 font-semibold transition-colors duration-200 flex items-center gap-1 hover:gap-2"
        >
          {{ activityTableLinkText }}
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </router-link>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-gray-500">
          <thead class="text-xs text-gray-700 uppercase bg-gray-100 font-bold">
            <tr>
              <th scope="col" class="px-6 py-3">Usuario</th>
              <th scope="col" class="px-6 py-3">Acción</th>
              <th scope="col" class="px-6 py-3">Modelo</th>
              <th scope="col" class="px-6 py-3">Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="recentActivities.length === 0">
              <td colspan="4" class="px-6 py-8 text-center text-sm text-gray-500">
                No hay actividades recientes para mostrar
              </td>
            </tr>
            <tr 
              v-for="activity in recentActivities" 
              :key="activity.id || activity.timestamp" 
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
                  {{ activity.accion_display || activity.accion || 'Desconocida' }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ activity.modelo || 'N/A' }}</td>
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

<script setup>
// 1. Vue core
import { defineProps, defineEmits } from 'vue'

// Props
const props = defineProps({
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
})

// Emits
const emit = defineEmits(['view-user', 'edit-user'])

// Functions
const handleViewUser = (userId) => {
  emit('view-user', userId)
}

const handleEditUser = (userId) => {
  emit('edit-user', userId)
}

const getRoleBadgeClass = (role) => {
  const roleClasses = {
    'admin': 'bg-green-100 text-green-800',
    'staff': 'bg-blue-100 text-blue-800',
    'analyst': 'bg-purple-100 text-purple-800',
    'farmer': 'bg-amber-100 text-amber-800',
    'user': 'bg-gray-100 text-gray-800',
    'superuser': 'bg-emerald-100 text-emerald-800'
  }
  return roleClasses[role?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

const getRoleDisplayName = (role) => {
  const roleNames = {
    'admin': 'Administrador',
    'staff': 'Personal',
    'analyst': 'Analista',
    'farmer': 'Agricultor',
    'user': 'Usuario',
    'superuser': 'Super Admin'
  }
  return roleNames[role?.toLowerCase()] || role || 'Usuario'
}

const getActionBadgeClass = (action) => {
  const actionClasses = {
    'create': 'bg-green-100 text-green-800',
    'update': 'bg-blue-100 text-blue-800',
    'delete': 'bg-red-100 text-red-800',
    'view': 'bg-gray-100 text-gray-800',
    'login': 'bg-purple-100 text-purple-800',
    'logout': 'bg-orange-100 text-orange-800'
  }
  return actionClasses[action?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

const formatDateTime = (dateString) => {
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
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>
