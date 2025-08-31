<template>
  <div class="min-h-screen bg-gray-100 py-8">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">
          Análisis de Granos de Cacao
        </h1>
        <p class="mt-2 text-lg text-gray-600">
          Utiliza inteligencia artificial para analizar las características físicas de tus granos de cacao
        </p>
      </div>

      <!-- Content Grid -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <!-- Sección de subida -->
        <div class="space-y-6">
          <!-- Upload Component -->
          <ImageUpload 
            @prediction-result="handlePredictionResult"
            @prediction-error="handlePredictionError"
          />

          <!-- Error Display -->
          <div 
            v-if="globalError" 
            class="bg-red-50 border border-red-200 rounded-lg p-4"
          >
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 class="text-sm font-medium text-red-800">Error en el análisis</h3>
                <p class="text-sm text-red-700 mt-1">{{ globalError }}</p>
                <button
                  @click="clearError"
                  class="text-sm text-red-600 hover:text-red-500 underline mt-2"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>

          <!-- Información adicional -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-blue-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 class="text-sm font-medium text-blue-800">Consejos para mejores resultados</h3>
                <ul class="text-sm text-blue-700 mt-1 space-y-1">
                  <li>• Usa imágenes claras y bien iluminadas</li>
                  <li>• Asegúrate de que el grano esté completo en la imagen</li>
                  <li>• Evita sombras fuertes o reflejos</li>
                  <li>• Formatos recomendados: JPG o PNG</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Sección de resultados -->
        <div class="space-y-6">
          <!-- Results Component -->
          <div v-if="currentPrediction">
            <PredictionResults 
              :prediction-data="currentPrediction"
              @new-analysis="handleNewAnalysis"
              @save-analysis="handleSaveAnalysis"
            />
          </div>

          <!-- Placeholder cuando no hay resultados -->
          <div 
            v-else 
            class="bg-white rounded-lg shadow-md p-8 text-center"
          >
            <div class="text-gray-400 mb-4">
              <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 00-2-2z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-700 mb-2">
              Resultados del Análisis
            </h3>
            <p class="text-gray-500">
              Los resultados de tu análisis aparecerán aquí una vez que subas una imagen
            </p>
          </div>

          <!-- Historial reciente -->
          <div v-if="recentPredictions.length > 0" class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">
              Análisis Recientes
            </h3>
            <div class="space-y-3">
              <div
                v-for="prediction in recentPredictions"
                :key="prediction.id"
                @click="currentPrediction = prediction"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-green-600">#{{ prediction.id }}</span>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ formatDimensions(prediction) }}
                    </div>
                    <div class="text-xs text-gray-500">
                      {{ formatRelativeTime(prediction.created_at) }}
                    </div>
                  </div>
                </div>
                <div class="text-sm text-gray-600">
                  {{ formatNumber(prediction.predicted_weight) }}g
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Success Message -->
      <div 
        v-if="showSuccessMessage" 
        class="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg transition-all duration-300"
      >
        <div class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {{ successMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import ImageUpload from '@/components/user/ImageUpload.vue';
import PredictionResults from '@/components/user/PredictionResults.vue';
import { getImageHistory } from '@/services/predictionApi.js';

export default {
  name: 'PredictionView',
  components: {
    ImageUpload,
    PredictionResults
  },
  
  setup() {
    // Estado reactivo
    const currentPrediction = ref(null);
    const recentPredictions = ref([]);
    const globalError = ref('');
    const showSuccessMessage = ref(false);
    const successMessage = ref('');
    
    // Manejo de resultados de predicción
    const handlePredictionResult = (result) => {
      console.log('Predicción recibida:', result);
      
      currentPrediction.value = result;
      
      // Agregar a historial reciente (al principio)
      recentPredictions.value.unshift(result);
      
      // Mantener solo los últimos 5 análisis
      if (recentPredictions.value.length > 5) {
        recentPredictions.value = recentPredictions.value.slice(0, 5);
      }
      
      // Mostrar mensaje de éxito
      showSuccess('¡Análisis completado exitosamente!');
      
      // Limpiar errores
      globalError.value = '';
    };
    
    const handlePredictionError = (error) => {
      console.error('Error en predicción:', error);
      globalError.value = error.message || 'Error desconocido en la predicción';
      currentPrediction.value = null;
    };
    
    const handleNewAnalysis = () => {
      currentPrediction.value = null;
      globalError.value = '';
    };
    
    const handleSaveAnalysis = () => {
      // Aquí se podría implementar guardar en una base de datos local o remota
      showSuccess('Análisis guardado en el historial');
    };
    
    const clearError = () => {
      globalError.value = '';
    };
    
    const showSuccess = (message) => {
      successMessage.value = message;
      showSuccessMessage.value = true;
      
      setTimeout(() => {
        showSuccessMessage.value = false;
      }, 3000);
    };
    
    // Cargar historial reciente al montar
    const loadRecentPredictions = async () => {
      try {
        const response = await getImageHistory({ 
          processed: true,
          page: 1,
          page_size: 5 // Solo los últimos 5
        });
        
        if (response.results) {
          recentPredictions.value = response.results;
        }
      } catch (error) {
        console.warn('No se pudo cargar el historial:', error.message);
        // No mostrar error al usuario, ya que es opcional
      }
    };
    
    // Métodos de formateo
    const formatNumber = (value) => {
      if (value === null || value === undefined) return 'N/A';
      const num = parseFloat(value);
      return isNaN(num) ? 'N/A' : num.toFixed(2);
    };
    
    const formatDimensions = (prediction) => {
      return `${formatNumber(prediction.width)} × ${formatNumber(prediction.height)} × ${formatNumber(prediction.thickness)} mm`;
    };
    
    const formatRelativeTime = (dateString) => {
      if (!dateString) return '';
      
      const now = new Date();
      const date = new Date(dateString);
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);
      
      if (diffMins < 1) return 'Hace un momento';
      if (diffMins < 60) return `Hace ${diffMins} minuto${diffMins !== 1 ? 's' : ''}`;
      if (diffHours < 24) return `Hace ${diffHours} hora${diffHours !== 1 ? 's' : ''}`;
      if (diffDays < 7) return `Hace ${diffDays} día${diffDays !== 1 ? 's' : ''}`;
      
      return date.toLocaleDateString('es-ES');
    };
    
    // Lifecycle
    onMounted(() => {
      loadRecentPredictions();
    });
    
    return {
      // Estado
      currentPrediction,
      recentPredictions,
      globalError,
      showSuccessMessage,
      successMessage,
      
      // Métodos
      handlePredictionResult,
      handlePredictionError,
      handleNewAnalysis,
      handleSaveAnalysis,
      clearError,
      formatNumber,
      formatDimensions,
      formatRelativeTime
    };
  }
};
</script>

<style scoped>
/* Animaciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Efectos hover mejorados */
.recent-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Responsive adjustments */
@media (max-width: 1280px) {
  .grid-cols-1.xl\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

/* Mejoras de accesibilidad */
.focus-visible:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Animación del mensaje de éxito */
.success-message {
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
