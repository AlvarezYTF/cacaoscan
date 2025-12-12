<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <div class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-4 border-b border-gray-200">
      <div class="flex items-center">
        <div class="bg-green-100 p-2 rounded-xl mr-3">
          <svg class="text-xl text-green-600 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-gray-900">Actividad Reciente</h2>
          <p class="text-sm text-gray-600">Últimos análisis realizados</p>
        </div>
      </div>
    </div>
    <div class="p-6">
      <div class="space-y-0">
        <div 
          v-for="(analysis, index) in recentAnalyses" 
          :key="analysis.id" 
          @click="$emit('select-analysis', analysis)" 
          class="flex items-center justify-between p-4 hover:bg-green-50 transition-colors duration-200 cursor-pointer"
          :class="index < recentAnalyses.length - 1 ? 'border-b border-green-100' : ''"
        >
          <div class="flex items-center space-x-3 flex-1">
            <div class="bg-green-500 p-2 rounded-lg flex-shrink-0">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <p class="text-sm font-bold text-gray-900">Lote #{{ analysis.id }}</p>
                <span 
                  v-if="analysis.status === 'completed'"
                  class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-semibold"
                >
                  Completado
                </span>
                <span 
                  v-else
                  class="px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded text-xs font-semibold"
                >
                  Pendiente
                </span>
              </div>
              <div class="flex items-center gap-3 text-xs text-gray-600">
                <span>{{ analysis.date }}</span>
                <span v-if="analysis.defects > 0" class="text-red-600">
                  {{ analysis.defects }}% defectos
                </span>
              </div>
            </div>
          </div>
          <div class="ml-4 flex-shrink-0">
            <div class="px-3 py-1.5 bg-green-500 text-white rounded-lg text-sm font-bold shadow-sm text-center min-w-[60px]">
              {{ analysis.quality }}%
            </div>
            <p class="text-xs text-gray-500 text-center mt-1">Calidad</p>
          </div>
        </div>
        <div v-if="recentAnalyses.length === 0" class="text-center py-12">
          <div class="text-gray-400 text-4xl mb-2">📋</div>
          <p class="text-gray-600 font-medium">No hay actividad reciente</p>
          <p class="text-gray-500 text-sm mt-1">Realiza análisis para verlos aquí</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  recentAnalyses: {
    type: Array,
    required: true,
    default: () => []
  }
})

defineEmits(['select-analysis'])
</script>
