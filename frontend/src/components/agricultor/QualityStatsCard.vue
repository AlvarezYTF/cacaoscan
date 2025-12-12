<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-gray-900">Estadísticas de Calidad</h2>
        <p class="text-sm text-gray-600 mt-1">Métricas detalladas del cacao</p>
      </div>
      <div class="bg-blue-100 p-3 rounded-xl">
        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
        </svg>
      </div>
    </div>
    
    <div class="grid grid-cols-2 gap-4">
      <!-- Calidad Promedio -->
      <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-gray-600">Calidad Promedio</span>
          <div class="w-3 h-3 rounded-full" :class="qualityColorClass"></div>
        </div>
        <p class="text-3xl font-bold" :class="qualityTextClass">{{ averageQuality }}%</p>
        <p class="text-xs text-gray-500 mt-1">Basado en {{ totalAnalyses }} análisis</p>
      </div>
      
      <!-- Tasa de Procesamiento -->
      <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-gray-600">Tasa de Procesamiento</span>
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
        </div>
        <p class="text-3xl font-bold text-gray-900">{{ processingRate }}%</p>
        <p class="text-xs text-gray-500 mt-1">{{ processedImages }} de {{ totalImages }} procesadas</p>
      </div>
      
      <!-- Defectos Promedio -->
      <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-gray-600">Defectos Promedio</span>
          <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
        </div>
        <p class="text-3xl font-bold text-red-600">{{ averageDefects }}%</p>
        <p class="text-xs text-gray-500 mt-1">Granos con defectos</p>
      </div>
      
      <!-- Confianza Promedio -->
      <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-gray-600">Confianza ML</span>
          <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <p class="text-3xl font-bold text-green-600">{{ averageConfidence }}%</p>
        <p class="text-xs text-gray-500 mt-1">Precisión del modelo</p>
      </div>
    </div>
    
    <!-- Additional metrics row -->
    <div class="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-200">
      <div class="text-center">
        <p class="text-2xl font-bold text-gray-900">{{ processedToday }}</p>
        <p class="text-xs text-gray-600 mt-1">Hoy</p>
      </div>
      <div class="text-center">
        <p class="text-2xl font-bold text-gray-900">{{ processedThisWeek }}</p>
        <p class="text-xs text-gray-600 mt-1">Esta semana</p>
      </div>
      <div class="text-center">
        <p class="text-2xl font-bold text-gray-900">{{ processedThisMonth }}</p>
        <p class="text-xs text-gray-600 mt-1">Este mes</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  averageQuality: {
    type: Number,
    default: 0
  },
  totalAnalyses: {
    type: Number,
    default: 0
  },
  processingRate: {
    type: Number,
    default: 0
  },
  processedImages: {
    type: Number,
    default: 0
  },
  totalImages: {
    type: Number,
    default: 0
  },
  averageDefects: {
    type: Number,
    default: 0
  },
  averageConfidence: {
    type: Number,
    default: 0
  },
  processedToday: {
    type: Number,
    default: 0
  },
  processedThisWeek: {
    type: Number,
    default: 0
  },
  processedThisMonth: {
    type: Number,
    default: 0
  }
})

const qualityColorClass = computed(() => {
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

