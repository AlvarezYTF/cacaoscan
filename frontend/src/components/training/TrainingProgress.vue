<template>
  <div class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
    <div class="px-6 py-4 border-b border-gray-200">
      <h3 class="text-xl font-bold text-gray-900">Estado del Entrenamiento</h3>
    </div>
    
    <div class="p-6">
      <!-- Not training state -->
      <div v-if="!isTraining" class="text-center py-6">
        <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <p class="text-gray-500 font-medium mb-2">No hay entrenamiento activo</p>
        <p class="text-gray-400 text-sm mb-4">Inicia un entrenamiento para ver el progreso aquí</p>
        <button
          @click="$emit('start-training')"
          class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M15 14h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Iniciar Entrenamiento
        </button>
      </div>
      
      <!-- Training in progress -->
      <div v-else class="space-y-6">
        <!-- Progress bar -->
        <div>
          <div class="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>{{ trainingStatus }}</span>
            <span>{{ Math.round(progress) }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-3">
            <div 
              class="bg-green-600 h-3 rounded-full transition-all duration-500 ease-out"
              :style="{ width: `${progress}%` }"
            ></div>
          </div>
        </div>
        
        <!-- Training details -->
        <div class="grid grid-cols-2 gap-4">
          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">{{ currentEpoch }}</div>
            <div class="text-sm text-green-700">Época Actual</div>
          </div>
          
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">{{ totalEpochs }}</div>
            <div class="text-sm text-blue-700">Total Épocas</div>
          </div>
        </div>
        
        <!-- Training metrics -->
        <div class="bg-gray-50 rounded-lg p-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-3">Métricas de Entrenamiento</h4>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Loss:</span>
              <span class="font-medium text-gray-900">0.1234</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Accuracy:</span>
              <span class="font-medium text-gray-900">95.2%</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Val Loss:</span>
              <span class="font-medium text-gray-900">0.1456</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Val Accuracy:</span>
              <span class="font-medium text-gray-900">93.8%</span>
            </div>
          </div>
        </div>
        
        <!-- Stop button -->
        <div class="pt-4 border-t border-gray-200">
          <button
            @click="$emit('stop-training')"
            class="w-full inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10h6v4H9z" />
            </svg>
            Detener Entrenamiento
          </button>
        </div>
      </div>
      
      <!-- Training completed -->
      <div v-if="!isTraining && progress === 100" class="text-center py-6">
        <svg class="w-16 h-16 text-green-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-green-600 font-medium mb-2">Entrenamiento Completado</p>
        <p class="text-gray-500 text-sm mb-4">El modelo ha sido entrenado exitosamente</p>
        <div class="flex justify-center space-x-3">
          <button
            @click="$emit('start-training')"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Reentrenar
          </button>
          <button
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 00-2-2z" />
            </svg>
            Ver Métricas
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrainingProgress',
  props: {
    isTraining: {
      type: Boolean,
      default: false
    },
    progress: {
      type: Number,
      default: 0
    },
    currentEpoch: {
      type: Number,
      default: 0
    },
    totalEpochs: {
      type: Number,
      default: 100
    },
    trainingStatus: {
      type: String,
      default: ''
    }
  },
  
  emits: ['start-training', 'stop-training']
};
</script>

<style scoped>
/* Progress bar animation */
.transition-all {
  transition: all 0.5s ease-out;
}

/* Focus states */
.focus-visible:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Button hover effects */
.hover\:bg-green-700:hover {
  background-color: #15803d;
}

.hover\:bg-red-700:hover {
  background-color: #b91c1c;
}

.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}
</style>
