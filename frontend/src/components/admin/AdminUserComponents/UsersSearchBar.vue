<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-8">
    <div class="flex flex-col lg:flex-row gap-4 items-start lg:items-center">
      <div class="flex-1 min-w-0">
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <input type="text" :value="searchQuery" @input="$emit('update:searchQuery', $event.target.value)"
            placeholder="Buscar usuarios..."
            class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-green-500 focus:border-green-500 text-sm">
        </div>
      </div>

      <div class="flex flex-wrap gap-3">
        <select :value="roleFilter" @change="$emit('update:roleFilter', $event.target.value)"
          class="block w-full lg:w-auto px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500">
          <option value="">Todos los roles</option>
          <option value="Administrador">Administrador</option>
          <option value="Agricultor">Agricultor</option>
          <option value="Técnico">Técnico</option>
        </select>

        <select :value="statusFilter" @change="$emit('update:statusFilter', $event.target.value)"
          class="block w-full lg:w-auto px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500">
          <option value="">Todos los estados</option>
          <option value="active">Activos</option>
          <option value="inactive">Inactivos</option>
        </select>

        <select :value="sortBy" @change="$emit('update:sortBy', $event.target.value)"
          class="block w-full lg:w-auto px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500">
          <option value="-date_joined">Más recientes</option>
          <option value="date_joined">Más antiguos</option>
          <option value="username">Nombre de usuario</option>
          <option value="email">Email</option>
          <option value="last_login">Último login</option>
        </select>

        <button @click="$emit('clear-filters')"
          class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
          Limpiar
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UsersSearchBar',
  props: {
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
  },
  emits: ['update:searchQuery', 'update:roleFilter', 'update:statusFilter', 'update:sortBy', 'clear-filters']
}
</script>

