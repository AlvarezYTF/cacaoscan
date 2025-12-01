<template>
  <div class="base-finca-filters bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <!-- Header -->
    <div v-if="showHeader" class="bg-gray-50 px-6 py-4 border-b border-gray-200">
      <slot name="header">
        <div class="flex items-center">
          <div class="bg-green-100 p-2 rounded-lg mr-3">
            <slot name="header-icon">
              <svg class="text-xl text-green-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
              </svg>
            </slot>
          </div>
          <div>
            <h2 class="text-lg font-bold text-gray-900">{{ title }}</h2>
            <p class="text-sm text-gray-600">{{ subtitle }}</p>
          </div>
        </div>
      </slot>
    </div>

    <!-- Filters Content -->
    <div class="p-6">
      <div :class="['base-finca-filters-grid', gridClass]">
        <!-- Search Input -->
        <div v-if="showSearch">
          <label :for="searchInputId" class="block text-sm font-medium text-gray-700 mb-1">
            {{ searchLabel }}
          </label>
          <input
            :id="searchInputId"
            v-model="localSearchQuery"
            type="text"
            :placeholder="searchPlaceholder"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
            @input="handleSearchInput"
          />
        </div>

        <!-- Custom Filters Slot -->
        <slot name="filters" :filters="localFilters" :update-filter="updateFilter">
          <!-- Default filter fields can be provided via props -->
        </slot>

        <!-- Clear Filters Button -->
        <div v-if="showClearButton" class="flex items-end">
          <button
            @click="handleClearFilters"
            class="w-full bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            {{ clearButtonText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { generateSecureId } from '@/utils/idGenerator'

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  filters: {
    type: Object,
    default: () => ({})
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  title: {
    type: String,
    default: 'Filtros de Búsqueda'
  },
  subtitle: {
    type: String,
    default: 'Filtra los elementos por diferentes criterios'
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  searchLabel: {
    type: String,
    default: 'Buscar'
  },
  searchPlaceholder: {
    type: String,
    default: 'Buscar...'
  },
  showClearButton: {
    type: Boolean,
    default: true
  },
  clearButtonText: {
    type: String,
    default: 'Limpiar Filtros'
  },
  debounceMs: {
    type: Number,
    default: 500
  },
  gridClass: {
    type: String,
    default: 'grid grid-cols-1 md:grid-cols-4 gap-4'
  }
})

const emit = defineEmits(['update:searchQuery', 'update:filters', 'apply-filters', 'clear-filters'])

const localSearchQuery = ref(props.searchQuery)
const localFilters = ref({ ...props.filters })

// Generate unique ID for search input
const searchInputId = computed(() => {
  return generateSecureId('base-finca-filter-search')
})

// Watch for prop changes
watch(() => props.searchQuery, (newVal) => {
  localSearchQuery.value = newVal
})

watch(() => props.filters, (newVal) => {
  localFilters.value = { ...newVal }
}, { deep: true })

// Debounced search
let searchTimeout = null
const handleSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    emit('update:searchQuery', localSearchQuery.value)
    emit('apply-filters')
  }, props.debounceMs)
}

// Update filter helper
const updateFilter = (key, value) => {
  localFilters.value[key] = value
  emit('update:filters', { ...localFilters.value })
  emit('apply-filters')
}

// Clear filters
const handleClearFilters = () => {
  localSearchQuery.value = ''
  localFilters.value = {}
  emit('update:searchQuery', '')
  emit('update:filters', {})
  emit('clear-filters')
}
</script>

<style scoped>
.base-finca-filters {
  @apply w-full;
}
</style>

