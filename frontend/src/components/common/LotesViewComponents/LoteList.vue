<template>
  <div class="space-y-6">
    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
        <div class="flex items-center gap-4">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <div>
            <p class="text-gray-900 font-medium">Cargando lotes...</p>
            <p class="text-gray-600 text-sm">Por favor espera un momento</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="alert-danger bg-red-50 border border-red-200 rounded-xl p-6">
      <div class="flex items-center gap-3">
        <div class="bg-red-100 p-2 rounded-lg">
          <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
        </div>
        <div class="flex-1">
          <h3 class="text-red-800 font-medium">Error al cargar los lotes</h3>
          <p class="text-red-700 text-sm mt-1">{{ error }}</p>
        </div>
        <button
          @click="$emit('retry')"
          class="btn-outline-danger bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          <span>Intentar nuevamente</span>
        </button>
      </div>
    </div>

    <!-- Lista de lotes -->
    <div v-else-if="lotes.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <LoteCard
        v-for="lote in lotes"
        :key="lote.id"
        :lote="lote"
        :can-edit="canEdit"
        @edit="$emit('edit', $event)"
        @analyze="$emit('analyze', $event)"
        @view-details="$emit('view-details', $event)"
      />
    </div>

    <!-- Empty state -->
    <div v-else class="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
      <div class="max-w-md mx-auto">
        <div class="bg-gray-100 p-4 rounded-full w-fit mx-auto mb-4">
          <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">No hay lotes registrados</h3>
        <p class="text-gray-600 mb-6">Comienza creando tu primer lote para empezar a gestionar tu producción de cacao.</p>
        <button
          v-if="canCreate"
          @click="$emit('create')"
          class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-all duration-200 flex items-center gap-2 mx-auto"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Crear Primer Lote
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import LoteCard from './LoteCard.vue'

defineProps({
  lotes: {
    type: Array,
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
  canEdit: {
    type: Boolean,
    default: true
  },
  canCreate: {
    type: Boolean,
    default: true
  }
})

defineEmits(['edit', 'analyze', 'view-details', 'create', 'retry'])
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>

