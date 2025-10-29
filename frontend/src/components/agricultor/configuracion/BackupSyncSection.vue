<template>
  <div class="bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg">
    <div class="flex items-center gap-3 mb-6">
      <div class="p-2 bg-green-100 rounded-xl">
        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
        </svg>
      </div>
      <h3 class="text-2xl font-bold text-gray-900">Conectividad y Respaldo</h3>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Sincronización -->
      <div class="p-6 bg-gradient-to-br from-green-50 to-gray-50 border-2 border-green-200 rounded-xl">
        <div class="flex items-center gap-3 mb-3">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <h4 class="font-bold text-gray-900">Sincronizar</h4>
        </div>
        <p class="text-sm text-gray-600 mb-2">Última sincronización:</p>
        <p class="text-xs text-gray-500 mb-4">{{ lastSync || 'Nunca' }}</p>
        <button 
          @click="$emit('sync')"
          :disabled="isLoading"
          class="w-full py-2 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-all duration-200 disabled:opacity-50"
        >
          {{ isLoading ? 'Sincronizando...' : 'Sincronizar Ahora' }}
        </button>
      </div>

      <!-- Exportar a CSV -->
      <div class="p-6 bg-gray-50 border-2 border-gray-200 rounded-xl">
        <div class="flex items-center gap-3 mb-3">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h4 class="font-bold text-gray-900">Exportar CSV</h4>
        </div>
        <p class="text-sm text-gray-600 mb-4">Descargar reportes en CSV</p>
        <button 
          @click="$emit('export-csv')"
          class="w-full py-2 px-4 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition-all duration-200"
        >
          Descargar CSV
        </button>
      </div>

      <!-- Exportar a PDF -->
      <div class="p-6 bg-gray-50 border-2 border-gray-200 rounded-xl">
        <div class="flex items-center gap-3 mb-3">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h4 class="font-bold text-gray-900">Exportar PDF</h4>
        </div>
        <p class="text-sm text-gray-600 mb-4">Generar reporte en PDF</p>
        <button 
          @click="$emit('export-pdf')"
          class="w-full py-2 px-4 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-all duration-200"
        >
          Generar PDF
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  lastSync: {
    type: String,
    default: ''
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['sync', 'export-csv', 'export-pdf'])
</script>

