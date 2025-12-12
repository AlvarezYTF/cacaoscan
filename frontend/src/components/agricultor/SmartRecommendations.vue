<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden" data-section="recommendations">
    <div class="bg-gradient-to-r from-indigo-50 to-blue-50 px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <div class="bg-indigo-100 p-2 rounded-xl mr-3">
            <svg class="text-xl text-indigo-600 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-bold text-gray-900">Recomendaciones Inteligentes</h2>
            <p class="text-sm text-gray-600">Sugerencias basadas en IA y análisis</p>
          </div>
        </div>
        <span v-if="recommendations.length > 0" class="bg-indigo-500 text-white text-xs font-bold px-2 py-1 rounded-full">
          {{ recommendations.length }}
        </span>
      </div>
    </div>
    
    <div class="p-6">
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="text-gray-600 mt-2">Generando recomendaciones...</p>
      </div>
      
      <div v-else-if="recommendations.length === 0" class="text-center py-8">
        <div class="text-green-500 text-4xl mb-2">✓</div>
        <p class="text-gray-600 font-medium">No hay recomendaciones en este momento</p>
        <p class="text-gray-500 text-sm mt-1">Todo está funcionando correctamente</p>
      </div>
      
      <div v-else class="space-y-3">
        <div
          v-for="recommendation in recommendations"
          :key="recommendation.id"
          :class="[
            'p-4 rounded-xl border-l-4 transition-all duration-200',
            recommendation.type === 'success' ? 'bg-green-50 border-green-500' :
            recommendation.type === 'warning' ? 'bg-yellow-50 border-yellow-500' :
            'bg-blue-50 border-blue-500'
          ]"
        >
          <div class="flex items-start gap-3">
            <div :class="[
              'p-2 rounded-lg flex-shrink-0',
              recommendation.type === 'success' ? 'bg-green-100' :
              recommendation.type === 'warning' ? 'bg-yellow-100' :
              'bg-blue-100'
            ]">
              <svg
                v-if="recommendation.type === 'success'"
                class="w-5 h-5 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <svg
                v-else-if="recommendation.type === 'warning'"
                class="w-5 h-5 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
              <svg
                v-else
                class="w-5 h-5 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900 mb-1">{{ recommendation.title }}</h3>
              <p class="text-sm text-gray-700">{{ recommendation.message }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  recommendations: {
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

