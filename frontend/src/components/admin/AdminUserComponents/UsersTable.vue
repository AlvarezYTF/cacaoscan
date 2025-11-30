<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <div class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
      <h3 class="text-xl font-bold text-gray-900">Lista de Usuarios</h3>
      <div class="flex items-center space-x-3">
        <button 
          @click="handleExport" 
          :disabled="loading"
          type="button"
          class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z">
            </path>
          </svg>
          Exportar
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-12">
      <BaseSpinner size="lg" color="green" />
      <p class="mt-4 text-gray-600">Cargando usuarios...</p>
    </div>

    <div v-else-if="users.length === 0" class="flex flex-col items-center justify-center py-12">
      <svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z">
        </path>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No se encontraron usuarios</h3>
      <p class="text-gray-600 text-center">No hay usuarios que coincidan con los filtros aplicados.</p>
    </div>

    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200" aria-label="Tabla de usuarios del sistema">
        <caption class="sr-only">Tabla de usuarios mostrando información de usuario, email, rol, estado, último login, fecha de registro y acciones disponibles</caption>
        <thead class="bg-gradient-to-r from-gray-50 to-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <input 
                type="checkbox" 
                :checked="selectAll" 
                @change="handleToggleSelectAll"
                class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              >
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Último Login</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Registro</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr 
            v-for="user in users" 
            :key="user.id"
            :class="{ 'bg-green-100': selectedUsers.includes(user.id) }"
            class="hover:bg-green-50 transition-all duration-200 cursor-pointer group"
          >
            <td class="px-6 py-4 whitespace-nowrap">
              <input 
                type="checkbox" 
                :value="user.id" 
                :checked="selectedUsers.includes(user.id)" 
                @change="handleToggleUserSelect(user.id)"
                class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              >
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                  <div class="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
                    <svg class="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                        clip-rule="evenodd"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">
                    {{ user.first_name }} {{ user.last_name }}
                  </div>
                  <div class="text-sm text-gray-500">@{{ user.username }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ user.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span 
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getRoleBadgeClass(user.role)"
              >
                {{ user.role || 'Sin rol' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <button 
                @click="handleToggleStatus(user)"
                type="button"
                :class="[
                  'px-3 py-1.5 text-xs font-semibold rounded-full transition-colors duration-200 inline-flex items-center gap-1.5 hover:opacity-80',
                  user.is_active 
                    ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                    : 'bg-red-100 text-red-800 hover:bg-red-200'
                ]"
                :disabled="user.isUpdating"
                title="Click para cambiar estado"
              >
                <span v-if="!user.isUpdating" class="inline-flex items-center gap-1.5">
                  {{ user.is_active ? 'Activo' : 'Inactivo' }}
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
                  </svg>
                </span>
                <span v-else class="inline-flex items-center gap-1.5">
                  <svg class="animate-spin h-3 w-3 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Cambiando...
                </span>
              </button>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              <span v-if="user.last_login">{{ formatDateTime(user.last_login) }}</span>
              <span v-else class="text-gray-400">Nunca</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(user.date_joined) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <div class="flex items-center space-x-2">
                <button 
                  @click="handleViewUser(user)"
                  type="button"
                  class="text-green-600 hover:text-green-700 p-2 rounded-lg hover:bg-green-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                  title="Ver detalles"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z">
                    </path>
                  </svg>
                </button>
                <button 
                  @click="handleEditUser(user)"
                  type="button"
                  class="text-amber-600 hover:text-amber-700 p-2 rounded-lg hover:bg-amber-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  title="Editar"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z">
                    </path>
                  </svg>
                </button>
                <button 
                  @click="handleViewActivity(user)"
                  type="button"
                  class="text-blue-600 hover:text-blue-700 p-2 rounded-lg hover:bg-blue-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  title="Ver actividad"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </button>
                <button 
                  @click="handleDeleteUser(user)"
                  type="button"
                  class="text-red-600 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Eliminar" 
                  :disabled="user.is_superuser"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16">
                    </path>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { computed } from 'vue'

// 2. Components
import BaseSpinner from '@/components/common/BaseSpinner.vue'

// Props
const props = defineProps({
  users: {
    type: Array,
    required: true
  },
  selectedUsers: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits([
  'toggle-select-all',
  'toggle-user-select',
  'toggle-status',
  'view-user',
  'edit-user',
  'delete-user',
  'view-activity',
  'export'
])

// Computed
const selectAll = computed({
  get: () => props.selectedUsers.length === props.users.length && props.users.length > 0,
  set: (value) => emit('toggle-select-all', value)
})

// Functions
const handleToggleSelectAll = () => {
  emit('toggle-select-all', !selectAll.value)
}

const handleToggleUserSelect = (userId) => {
  emit('toggle-user-select', userId)
}

const handleToggleStatus = (user) => {
  emit('toggle-status', user)
}

const handleViewUser = (user) => {
  emit('view-user', user)
}

const handleEditUser = (user) => {
  emit('edit-user', user)
}

const handleViewActivity = (user) => {
  emit('view-activity', user)
}

const handleDeleteUser = (user) => {
  emit('delete-user', user)
}

const handleExport = () => {
  emit('export')
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('es-ES')
}

const formatDateTime = (date) => {
  return new Date(date).toLocaleString('es-ES')
}

const getRoleBadgeClass = (role) => {
  const classes = {
    'Administrador': 'bg-purple-100 text-purple-800',
    'Agricultor': 'bg-green-100 text-green-800',
    'Técnico': 'bg-blue-100 text-blue-800'
  }
  return classes[role] || 'bg-gray-100 text-gray-800'
}
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
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
