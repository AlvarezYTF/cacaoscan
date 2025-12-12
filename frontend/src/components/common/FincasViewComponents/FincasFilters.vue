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
          <p class="text-sm text-gray-600">Filtra las fincas por diferentes criterios</p>
        </div>
      </div>
    </div>
    <div class="p-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label for="fincas-filter-search" class="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
          <input
            id="fincas-filter-search"
            v-model="localSearchQuery"
            type="text"
            placeholder="Nombre, municipio, departamento..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label for="fincas-filter-departamento" class="block text-sm font-medium text-gray-700 mb-1">Departamento</label>
          <select
            id="fincas-filter-departamento"
            v-model="localFilters.departamento"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
            @change="applyFilters"
          >
            <option value="">Todos los departamentos</option>
            <option v-for="dept in departamentos" :key="dept" :value="dept">
              {{ dept }}
            </option>
          </select>
        </div>
        <div>
          <label for="fincas-filter-estado" class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <select
            id="fincas-filter-estado"
            v-model="localFilters.activa"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
            @change="applyFilters"
          >
            <option value="">Todos</option>
            <option value="true">Activas</option>
            <option value="false">Inactivas</option>
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
import fincasApi from '@/services/fincasApi'

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  filters: {
    type: Object,
    default: () => ({ departamento: '', activa: '' })
  }
})

const emit = defineEmits(['update:searchQuery', 'update:filters', 'apply-filters', 'clear-filters'])

const localSearchQuery = ref(props.searchQuery)
const localFilters = ref({ ...props.filters })

// Computed
const departamentos = fincasApi.getDepartamentosColombia()

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
  localFilters.value = { departamento: '', activa: '' }
  emit('update:searchQuery', '')
  emit('update:filters', { departamento: '', activa: '' })
  emit('clear-filters')
}
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>