<template>
  <div class="base-finca-list space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <slot name="loading">
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
          <div class="flex items-center gap-4">
            <BaseSpinner size="lg" color="green" />
            <div>
              <p class="text-gray-900 font-medium">{{ loadingText }}</p>
              <p class="text-gray-600 text-sm">{{ loadingSubtext }}</p>
            </div>
          </div>
        </div>
      </slot>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6">
      <slot name="error">
        <div class="flex items-center gap-3">
          <div class="bg-red-100 p-2 rounded-lg">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-red-800 font-medium">{{ errorTitle }}</h3>
            <p class="text-red-700 text-sm mt-1">{{ error }}</p>
          </div>
          <button
            v-if="showRetry"
            @click="handleRetry"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            {{ retryText }}
          </button>
        </div>
      </slot>
    </div>

    <!-- Items List -->
    <div v-else-if="items.length > 0" :class="['base-finca-list-grid', gridClass]">
      <slot name="items" :items="items">
        <component
          v-for="(item, index) in items"
          :key="getItemKey(item, index)"
          :is="itemComponent"
          v-bind="getItemProps(item, index)"
          @view-details="handleViewDetails(item, index)"
          @edit="handleEdit(item, index)"
          @delete="handleDelete(item, index)"
          @activate="handleActivate(item, index)"
        />
      </slot>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
      <slot name="empty">
        <div class="max-w-md mx-auto">
          <div class="bg-gray-100 p-4 rounded-full w-fit mx-auto mb-4">
            <slot name="empty-icon">
              <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
            </slot>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ emptyTitle }}</h3>
          <p class="text-gray-600 mb-6">{{ emptyText }}</p>
          <button
            v-if="showCreateButton"
            @click="handleCreate"
            class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-all duration-200 flex items-center gap-2 mx-auto"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            {{ createButtonText }}
          </button>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import BaseSpinner from './BaseSpinner.vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  loadingText: {
    type: String,
    default: 'Cargando...'
  },
  loadingSubtext: {
    type: String,
    default: 'Por favor espera un momento'
  },
  errorTitle: {
    type: String,
    default: 'Error al cargar los datos'
  },
  showRetry: {
    type: Boolean,
    default: true
  },
  retryText: {
    type: String,
    default: 'Reintentar'
  },
  emptyTitle: {
    type: String,
    default: 'No hay elementos'
  },
  emptyText: {
    type: String,
    default: 'No se encontraron elementos para mostrar.'
  },
  showCreateButton: {
    type: Boolean,
    default: false
  },
  createButtonText: {
    type: String,
    default: 'Crear Nuevo'
  },
  itemComponent: {
    type: [String, Object],
    default: null
  },
  itemKey: {
    type: [String, Function],
    default: 'id'
  },
  getItemProps: {
    type: Function,
    default: null
  },
  gridClass: {
    type: String,
    default: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
  }
})

const emit = defineEmits(['retry', 'create', 'view-details', 'edit', 'delete', 'activate'])

const getItemKey = (item, index) => {
  if (typeof props.itemKey === 'function') {
    return props.itemKey(item, index)
  }
  return item[props.itemKey] || index
}

const handleRetry = () => {
  emit('retry')
}

const handleCreate = () => {
  emit('create')
}

const handleViewDetails = (item, index) => {
  emit('view-details', item, index)
}

const handleEdit = (item, index) => {
  emit('edit', item, index)
}

const handleDelete = (item, index) => {
  emit('delete', item, index)
}

const handleActivate = (item, index) => {
  emit('activate', item, index)
}
</script>

<style scoped>
.base-finca-list {
  @apply w-full;
}
</style>

