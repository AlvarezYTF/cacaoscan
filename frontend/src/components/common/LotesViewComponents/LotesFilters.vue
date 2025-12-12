<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
      <div class="flex items-center">
        <div class="bg-green-100 p-2 rounded-lg mr-3">
          <svg class="text-xl text-green-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-gray-900">Filtros de Búsqueda</h2>
          <p class="text-sm text-gray-600">Filtra los lotes por diferentes criterios</p>
        </div>
      </div>
    </div>
    <div class="p-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="md:col-span-2">
          <label for="lotes-filter-search" class="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
          <input
            id="lotes-filter-search"
            v-model="localSearchQuery"
            type="text"
            placeholder="Identificador, variedad, nombre..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label for="lotes-filter-estado" class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <select
            id="lotes-filter-estado"
            v-model="localFilters.estado"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
            @change="applyFilters"
          >
            <option value="">Todos</option>
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
            <option value="cosechado">Cosechado</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="clearFilters"
            class="w-full bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            Limpiar Filtros
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  filters: {
    type: Object,
    default: () => ({ estado: '' })
  }
})

const emit = defineEmits(['update:searchQuery', 'update:filters', 'apply-filters', 'clear-filters'])

const localSearchQuery = ref(props.searchQuery)
const localFilters = ref({ ...props.filters })

// Watchers para sincronizar con props
watch(() => props.searchQuery, (newVal) => {
  localSearchQuery.value = newVal
})

watch(() => props.filters, (newVal) => {
  localFilters.value = { ...newVal }
}, { deep: true })

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    emit('update:searchQuery', localSearchQuery.value)
    emit('apply-filters')
  }, 500)
}

// Métodos
const applyFilters = () => {
  emit('update:filters', { ...localFilters.value })
  emit('apply-filters')
}

const clearFilters = () => {
  localSearchQuery.value = ''
  localFilters.value = { estado: '' }
  emit('update:searchQuery', '')
  emit('update:filters', { estado: '' })
  emit('clear-filters')
}
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>

