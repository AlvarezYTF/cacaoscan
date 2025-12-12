<template>
  <div 
    class="relative bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 border border-gray-200 cursor-pointer group"
    @click="$emit('view-details', lote)"
  >
    <div class="p-6">
      <!-- Header de la tarjeta -->
      <div class="flex justify-between items-start mb-4">
        <div class="flex-1">
          <h3 class="text-lg font-bold text-gray-900 mb-1">{{ lote.identificador || lote.nombre || `Lote #${lote.id}` }}</h3>
          <p class="text-sm text-gray-600 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
            </svg>
            {{ lote.variedad?.nombre || lote.variedad || 'Sin variedad' }}
          </p>
        </div>
        <span
          :class="[
            'px-3 py-1 text-xs font-semibold rounded-full flex items-center gap-1',
            getEstadoClass(lote.estado)
          ]"
        >
          <svg v-if="lote.activo" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          {{ getEstadoLabel(lote.estado) }}
        </span>
      </div>

      <!-- Información del lote -->
      <div class="space-y-3 mb-4">
        <div class="flex items-center text-sm text-gray-600">
          <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0 2v2m0 4V5m0 4H9m3 4H9"></path>
          </svg>
          {{ formatPeso(lote.peso_kg) }} kg
        </div>
        <div v-if="lote.fecha_recepcion" class="flex items-center text-sm text-gray-600">
          <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
          </svg>
          Recepción: {{ formatDate(lote.fecha_recepcion) }}
        </div>
      </div>

      <!-- Estadísticas -->
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div class="bg-blue-50 rounded-lg p-3 text-center">
          <div class="text-2xl font-bold text-blue-600">{{ lote.total_analisis || 0 }}</div>
          <div class="text-xs text-gray-600">Análisis</div>
        </div>
        <div class="bg-purple-50 rounded-lg p-3 text-center">
          <div class="text-2xl font-bold text-purple-600">{{ lote.edad_meses || 0 }}</div>
          <div class="text-xs text-gray-600">Meses</div>
        </div>
      </div>

      <!-- Acciones -->
      <div class="flex gap-2 flex-wrap">
        <button
          v-if="canEdit"
          @click.stop="$emit('edit', lote)"
          class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-sm transition-all duration-200 flex items-center justify-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
          Editar
        </button>
        <button
          @click.stop="$emit('analyze', lote)"
          class="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg text-sm transition-all duration-200 flex items-center justify-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          Analizar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  lote: {
    type: Object,
    required: true
  },
  canEdit: {
    type: Boolean,
    default: true
  }
})

defineEmits(['edit', 'analyze', 'view-details'])

const getEstadoClass = (estado) => {
  if (typeof estado === 'object' && estado?.nombre) {
    estado = estado.nombre.toLowerCase()
  } else if (typeof estado === 'string') {
    estado = estado.toLowerCase()
  } else {
    return 'bg-gray-100 text-gray-800'
  }
  
  const classes = {
    'activo': 'bg-green-100 text-green-800',
    'inactivo': 'bg-gray-100 text-gray-800',
    'cosechado': 'bg-yellow-100 text-yellow-800',
    'renovado': 'bg-blue-100 text-blue-800'
  }
  return classes[estado] || 'bg-gray-100 text-gray-800'
}

const getEstadoLabel = (estado) => {
  if (typeof estado === 'object' && estado?.nombre) {
    return estado.nombre
  } else if (typeof estado === 'string') {
    const labels = {
      'activo': 'Activo',
      'inactivo': 'Inactivo',
      'cosechado': 'Cosechado',
      'renovado': 'Renovado'
    }
    return labels[estado.toLowerCase()] || estado
  }
  return 'Sin estado'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatPeso = (peso) => {
  if (!peso) return '0'
  return parseFloat(peso).toLocaleString('es-CO', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>

