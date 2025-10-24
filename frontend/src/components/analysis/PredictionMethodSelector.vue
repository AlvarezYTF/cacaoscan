<template>
  <div class="prediction-method-selector">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Método de Análisis</h3>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Método Tradicional -->
      <div 
        class="relative cursor-pointer rounded-xl border-2 p-6 transition-all duration-200"
        :class="selectedMethod === 'traditional' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white hover:border-gray-300'"
        @click="selectMethod('traditional')"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <div v-if="selectedMethod === 'traditional'" class="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
          </div>
        </div>
        
        <h4 class="font-semibold text-gray-900 mb-2">Análisis Tradicional</h4>
        <p class="text-sm text-gray-600 mb-3">
          CNN + Regresión para predicción de peso basada en características visuales tradicionales.
        </p>
        
        <div class="space-y-1 text-xs text-gray-500">
          <div class="flex items-center">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            Rápido (~1-2s)
          </div>
          <div class="flex items-center">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            Probado y estable
          </div>
        </div>
      </div>

      <!-- YOLOv8 Básico -->
      <div 
        class="relative cursor-pointer rounded-xl border-2 p-6 transition-all duration-200"
        :class="selectedMethod === 'yolo' ? 'border-purple-500 bg-purple-50' : 'border-gray-200 bg-white hover:border-gray-300'"
        @click="selectMethod('yolo')"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
          </div>
          <div v-if="selectedMethod === 'yolo'" class="w-5 h-5 bg-purple-500 rounded-full flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
          </div>
        </div>
        
        <h4 class="font-semibold text-gray-900 mb-2">YOLOv8</h4>
        <p class="text-sm text-gray-600 mb-3">
          Detección automática del grano con YOLOv8 y estimación de dimensiones físicas.
        </p>
        
        <div class="space-y-1 text-xs text-gray-500">
          <div class="flex items-center">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            Detección automática
          </div>
          <div class="flex items-center">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            Dimensiones precisas
          </div>
        </div>
      </div>

      <!-- YOLOv8 + Recorte Inteligente -->
      <div 
        class="relative cursor-pointer rounded-xl border-2 p-6 transition-all duration-200"
        :class="selectedMethod === 'smart' ? 'border-green-500 bg-green-50' : 'border-gray-200 bg-white hover:border-gray-300'"
        @click="selectMethod('smart')"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
            </svg>
          </div>
          <div v-if="selectedMethod === 'smart'" class="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
          </div>
        </div>
        
        <h4 class="font-semibold text-gray-900 mb-2">Recorte Inteligente</h4>
        <p class="text-sm text-gray-600 mb-3">
          YOLOv8 + Segmentación avanzada con recorte estilo iPhone y fondo transparente.
        </p>
        
        <div class="space-y-1 text-xs text-gray-500">
          <div class="flex items-center">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            Máxima precisión
          </div>
          <div class="flex items-center">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            Imágenes procesadas
          </div>
        </div>
      </div>

      <!-- CacaoScan Unificado -->
      <div 
        class="relative cursor-pointer rounded-xl border-2 p-6 transition-all duration-200"
        :class="selectedMethod === 'cacaoscan' ? 'border-green-500 bg-green-50' : 'border-gray-200 bg-white hover:border-gray-300'"
        @click="selectMethod('cacaoscan')"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div v-if="selectedMethod === 'cacaoscan'" class="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
          </div>
        </div>
        
        <h4 class="font-semibold text-gray-900 mb-2">CacaoScan Unificado</h4>
        <p class="text-sm text-gray-600 mb-3">
          Sistema automático completo: YOLOv8-seg + 4 modelos de regresión + inicialización automática.
        </p>
        
        <div class="space-y-1 text-xs text-gray-500">
          <div class="flex items-center">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            Inicialización automática
          </div>
          <div class="flex items-center">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            Máxima precisión
          </div>
          <div class="flex items-center">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            Sin configuración manual
          </div>
        </div>
      </div>
    </div>

    <!-- Información adicional -->
    <div class="mt-4 p-4 bg-gray-50 rounded-lg">
      <div class="flex items-start space-x-3">
        <svg class="w-5 h-5 text-blue-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div class="text-sm text-gray-700">
          <p class="font-medium mb-1">{{ getMethodInfo().title }}</p>
          <p>{{ getMethodInfo().description }}</p>
          <p v-if="getMethodInfo().processingTime" class="mt-1 text-gray-600">
            <strong>Tiempo estimado:</strong> {{ getMethodInfo().processingTime }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'PredictionMethodSelector',
  props: {
    modelValue: {
      type: String,
      default: 'traditional'
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const selectedMethod = ref(props.modelValue)

    const selectMethod = (method) => {
      selectedMethod.value = method
      emit('update:modelValue', method)
    }

    const getMethodInfo = () => {
      switch (selectedMethod.value) {
        case 'traditional':
          return {
            title: 'Análisis Tradicional',
            description: 'Usa redes neuronales convolucionales (CNN) entrenadas específicamente para granos de cacao, combinadas con modelos de regresión para estimar el peso.',
            processingTime: '1-2 segundos'
          }
        case 'yolo':
          return {
            title: 'YOLOv8',
            description: 'Detecta automáticamente el grano en la imagen y calcula sus dimensiones físicas reales en milímetros, luego estima el peso usando fórmulas volumétricas.',
            processingTime: '2-3 segundos'
          }
        case 'smart':
          return {
            title: 'Recorte Inteligente',
            description: 'Combina YOLOv8 con segmentación avanzada para crear recortes precisos estilo iPhone, incluyendo fondo transparente y métricas de calidad.',
            processingTime: '3-5 segundos'
          }
        case 'cacaoscan':
          return {
            title: 'CacaoScan Unificado',
            description: 'Sistema automático completo que inicializa automáticamente los modelos, segmenta con YOLOv8-seg y predice dimensiones y peso con 4 modelos de regresión especializados.',
            processingTime: '2-4 segundos (primera vez: 30-60 segundos)'
          }
        default:
          return {
            title: 'Método de Análisis',
            description: 'Selecciona un método de análisis para procesar tu imagen.',
            processingTime: null
          }
      }
    }

    // Watch for external changes
    watch(() => props.modelValue, (newValue) => {
      selectedMethod.value = newValue
    })

    return {
      selectedMethod,
      selectMethod,
      getMethodInfo
    }
  }
}
</script>

<style scoped>
@reference "tailwindcss";

.prediction-method-selector {
  @apply w-full;
}

/* Transiciones suaves */
.transition-all {
  transition: all 0.2s ease-in-out;
}

/* Hover effects */
.hover\:border-gray-300:hover {
  border-color: #d1d5db;
}

/* Focus states */
.focus\:outline-none:focus {
  outline: none;
}

.focus\:ring-2:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
