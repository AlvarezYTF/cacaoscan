<template>
  <BaseSearchBar
    :model-value="searchQuery"
    placeholder="Buscar usuarios..."
    container-class="mb-8"
    @update:model-value="$emit('update:searchQuery', $event)"
    @clear="$emit('update:searchQuery', '')"
  >
    <template #actions>
      <div class="flex flex-wrap gap-3">
        <select 
          :value="roleFilter" 
          @change="$emit('update:roleFilter', $event.target.value)"
          class="block w-full lg:w-auto px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
        >
          <option value="">Todos los roles</option>
          <option value="Administrador">Administrador</option>
          <option value="Agricultor">Agricultor</option>
          <option value="Técnico">Técnico</option>
        </select>

        <select 
          :value="statusFilter" 
          @change="$emit('update:statusFilter', $event.target.value)"
          class="block w-full lg:w-auto px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
        >
          <option value="">Todos los estados</option>
          <option value="active">Activos</option>
          <option value="inactive">Inactivos</option>
        </select>

        <select 
          :value="sortBy" 
          @change="$emit('update:sortBy', $event.target.value)"
          class="block w-full lg:w-auto px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
        >
          <option value="-date_joined">Más recientes</option>
          <option value="date_joined">Más antiguos</option>
          <option value="username">Nombre de usuario</option>
          <option value="email">Email</option>
          <option value="last_login">Último login</option>
        </select>

        <button 
          @click="$emit('clear-filters')"
          class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
          Limpiar
        </button>
      </div>
    </template>
  </BaseSearchBar>
</template>

<script setup>
import BaseSearchBar from '@/components/common/BaseSearchBar.vue'

defineProps({
  searchQuery: {
    type: String,
    required: true
  },
  roleFilter: {
    type: String,
    required: true
  },
  statusFilter: {
    type: String,
    required: true
  },
  sortBy: {
    type: String,
    required: true
  }
})

defineEmits(['update:searchQuery', 'update:roleFilter', 'update:statusFilter', 'update:sortBy', 'clear-filters'])
</script>
