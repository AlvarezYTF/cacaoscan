<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <div class="bg-gradient-to-r from-yellow-50 to-orange-50 px-6 py-4 border-b border-gray-200">
      <div class="flex items-center">
        <div class="bg-yellow-100 p-2 rounded-xl mr-3">
          <svg class="text-xl text-yellow-600 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-gray-900">Top Rendimiento</h2>
          <p class="text-sm text-gray-600">Mejores fincas y lotes</p>
        </div>
      </div>
    </div>
    
    <div class="p-6">
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="text-gray-600 mt-2">Cargando datos...</p>
      </div>
      
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Top Fincas -->
        <div>
          <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>🌱</span> Top 3 Fincas
          </h3>
          <div v-if="topFincas.length === 0" class="text-center py-4 text-gray-500 text-sm">
            No hay datos disponibles
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="(finca, index) in topFincas"
              :key="`finca-${finca.id}`"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div class="flex items-center gap-3">
                <div :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm',
                  index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : 'bg-orange-600'
                ]">
                  {{ index + 1 }}
                </div>
                <div>
                  <p class="font-semibold text-gray-900 text-sm">{{ finca.nombre }}</p>
                  <p class="text-xs text-gray-600">Calidad: {{ Math.round(finca.quality) }}%</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-xs text-gray-600">{{ Math.round(finca.defectRate) }}% defectos</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Top Lotes -->
        <div>
          <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>📦</span> Top 3 Lotes
          </h3>
          <div v-if="topLotes.length === 0" class="text-center py-4 text-gray-500 text-sm">
            No hay datos disponibles
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="(lote, index) in topLotes"
              :key="`lote-${lote.id}`"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div class="flex items-center gap-3">
                <div :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm',
                  index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : 'bg-orange-600'
                ]">
                  {{ index + 1 }}
                </div>
                <div>
                  <p class="font-semibold text-gray-900 text-sm">{{ lote.codigo }}</p>
                  <p class="text-xs text-gray-600">Calidad: {{ Math.round(lote.quality) }}%</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-xs text-gray-600">{{ lote.date }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  topFincas: {
    type: Array,
    required: true,
    default: () => []
  },
  topLotes: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})
</script>

