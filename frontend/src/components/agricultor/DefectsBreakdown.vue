<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <div class="bg-gradient-to-r from-purple-50 to-pink-50 px-6 py-4 border-b border-gray-200">
      <div class="flex items-center">
        <div class="bg-purple-100 p-2 rounded-xl mr-3">
          <svg class="text-xl text-purple-600 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-gray-900">Distribución de Defectos</h2>
          <p class="text-sm text-gray-600">Análisis de tipos de defectos</p>
        </div>
      </div>
    </div>
    
    <div class="p-6">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="text-gray-600 mt-2">Cargando datos...</p>
      </div>
      
      <div v-else-if="!defectsData || defectsData.length === 0" class="text-center py-12">
        <div class="text-gray-400 text-4xl mb-2">🧪</div>
        <p class="text-gray-600 font-medium">No hay datos de defectos disponibles</p>
        <p class="text-gray-500 text-sm mt-1">Los datos de defectos se mostrarán cuando estén disponibles</p>
      </div>
      
      <div v-else class="space-y-4">
        <!-- Bar chart for defects -->
        <div
          v-for="defect in defectsData"
          :key="defect.type"
          class="space-y-1"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div :class="`w-3 h-3 rounded-full bg-${defect.color}-500`"></div>
              <span class="text-sm font-semibold text-gray-900">{{ defect.label }}</span>
            </div>
            <span class="text-sm font-bold text-gray-700">{{ defect.percentage }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              :class="`bg-${defect.color}-500 h-full rounded-full transition-all duration-500`"
              :style="{ width: `${defect.percentage}%` }"
            ></div>
          </div>
        </div>
        
        <!-- Summary -->
        <div class="mt-6 pt-4 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <span class="text-sm font-semibold text-gray-700">Total defectos:</span>
            <span class="text-lg font-bold text-gray-900">{{ totalDefects }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  defectsData: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const totalDefects = computed(() => {
  if (!props.defectsData || props.defectsData.length === 0) {
    return 0
  }
  return Math.round(
    props.defectsData.reduce((sum, defect) => sum + defect.percentage, 0)
  )
})
</script>

