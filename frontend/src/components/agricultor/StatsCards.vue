<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <!-- Card Fincas Totales -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Fincas Totales</h3>
          <p class="text-2xl font-bold text-gray-900">{{ totalFincas }}</p>
        </div>
      </div>
    </div>
    
    <!-- Card Lotes Totales -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Lotes Totales</h3>
          <p class="text-2xl font-bold text-gray-900">{{ totalLotes }}</p>
        </div>
      </div>
    </div>
    
    <!-- Card Análisis Totales -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 bg-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Análisis Totales</h3>
          <p class="text-2xl font-bold text-gray-900">{{ totalAnalyses }}</p>
        </div>
      </div>
    </div>
    
    <!-- Card Calidad Promedio -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center gap-4">
        <div 
          :class="qualityIconClass"
          class="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0"
        >
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Calidad Promedio</h3>
          <p 
            :class="qualityTextClass"
            class="text-2xl font-bold"
          >
            {{ averageQuality }}%
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  totalFincas: {
    type: Number,
    default: 0
  },
  totalLotes: {
    type: Number,
    default: 0
  },
  totalBatches: {
    type: Number,
    default: 0
  },
  totalAnalyses: {
    type: Number,
    default: 0
  },
  averageQuality: {
    type: Number,
    default: 0
  }
})

const qualityIconClass = computed(() => {
  if (props.averageQuality >= 85) return 'bg-green-500'
  if (props.averageQuality >= 70) return 'bg-yellow-500'
  return 'bg-red-500'
})

const qualityTextClass = computed(() => {
  if (props.averageQuality >= 85) return 'text-green-600'
  if (props.averageQuality >= 70) return 'text-yellow-600'
  return 'text-red-600'
})
</script>
