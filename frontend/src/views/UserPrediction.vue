<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header Section -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              Análisis de Granos de Cacao
            </h1>
            <p class="mt-2 text-sm text-gray-600">
              Utiliza inteligencia artificial para analizar las características físicas de tus granos
            </p>
          </div>
          
          <!-- Stats Summary -->
          <div v-if="quickStats.total > 0" class="hidden lg:flex items-center space-x-6">
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">{{ quickStats.total }}</div>
              <div class="text-xs text-gray-500">Análisis realizados</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ quickStats.avgConfidence }}%</div>
              <div class="text-xs text-gray-500">Confianza promedio</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ quickStats.avgWeight }}g</div>
              <div class="text-xs text-gray-500">Peso promedio</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
        
        <!-- Left Column: Upload Section -->
        <div class="space-y-6">
          <!-- Upload Component -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="p-6">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-semibold text-gray-900">
                  Subir Nueva Imagen
                </h2>
                <div v-if="isLoading" class="flex items-center text-sm text-blue-600">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Procesando...
                </div>
              </div>
              
              <!-- Método de Predicción -->
              <div class="mb-6">
                <PredictionMethodSelector 
                  v-model="selectedMethod"
                />
              </div>
              
              <ImageUpload 
                :prediction-method="selectedMethod"
                @prediction-result="handlePredictionResult"
                @prediction-error="handlePredictionError"
              />
            </div>
          </div>

          <!-- Error Display -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="flex-1">
                <h3 class="text-sm font-medium text-red-800">Error en el análisis</h3>
                <p class="text-sm text-red-700 mt-1">{{ error }}</p>
                <button
                  @click="clearError"
                  class="text-sm text-red-600 hover:text-red-500 underline mt-2 focus:outline-none"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>

          <!-- Tips Section -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-blue-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 class="text-sm font-medium text-blue-800">Consejos para mejores resultados</h3>
                <ul class="text-sm text-blue-700 mt-2 space-y-1">
                  <li>• Usa imágenes claras y bien iluminadas</li>
                  <li>• Asegúrate de que el grano esté completo en la imagen</li>
                  <li>• Evita sombras fuertes o reflejos</li>
                  <li>• Formatos recomendados: JPG o PNG (máx. 10MB)</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Recent History (Mobile) -->
          <div v-if="hasHistory && recentPredictions.length > 0" class="xl:hidden bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">
                Análisis Recientes
              </h3>
              <div class="space-y-3">
                <div
                  v-for="prediction in recentPredictions"
                  :key="prediction.id"
                  @click="selectFromHistory(prediction.id)"
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
                    {{ formatWeight(prediction.predicted_weight) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Results Section -->
        <div class="space-y-6">
          <!-- Current Prediction Results -->
          <div v-if="hasPrediction" class="bg-white rounded-lg shadow-sm border border-gray-200">
            <!-- Mostrar resultados según el método usado -->
            <YoloResultsCard 
              v-if="isYoloMethod(currentPrediction)"
              :result="currentPrediction"
              :original-image="currentImageUrl"
              @new-analysis="startNewAnalysis"
            />
            
            <!-- Resultados tradicionales para métodos no-YOLO -->
            <PredictionResults 
              v-else
              :prediction-data="currentPrediction"
              @new-analysis="handleNewAnalysis"
              @save-analysis="handleSaveAnalysis"
            />
          </div>

          <!-- Placeholder when no results -->
          <div v-else class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div class="text-gray-400 mb-4">
              <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 00-2-2z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-700 mb-2">
              Resultados del Análisis
            </h3>
            <p class="text-gray-500 mb-4">
              Los resultados de tu análisis aparecerán aquí una vez que subas una imagen
            </p>
            
            <!-- Quick Actions -->
            <div class="flex justify-center space-x-3">
              <button
                v-if="hasHistory"
                @click="loadLatestPrediction"
                class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Ver último análisis
              </button>
            </div>
          </div>

          <!-- History Section (Desktop) -->
          <div v-if="hasHistory && recentPredictions.length > 0" class="hidden xl:block bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">
                  Análisis Recientes
                </h3>
                <router-link 
                  to="/user/history"
                  class="text-sm text-green-600 hover:text-green-700 font-medium"
                >
                  Ver todo →
                </router-link>
              </div>
              
              <div class="space-y-3">
                <div
                  v-for="prediction in recentPredictions"
                  :key="prediction.id"
                  @click="selectFromHistory(prediction.id)"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors group"
                >
                  <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center group-hover:bg-green-200 transition-colors">
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
                  <div class="flex items-center space-x-2">
                    <div class="text-sm text-gray-600">
                      {{ formatWeight(prediction.predicted_weight) }}
                    </div>
                    <div 
                      class="w-2 h-2 rounded-full"
                      :class="getConfidenceColor(prediction.confidence_level)"
                      :title="getConfidenceLabel(prediction.confidence_level)"
                    ></div>
                  </div>
                </div>
              </div>
              
              <!-- Load More Button -->
              <div v-if="predictions.length >= 5" class="mt-4 text-center">
                <button
                  @click="loadMoreHistory"
                  class="text-sm text-gray-500 hover:text-gray-700 font-medium"
                >
                  Cargar más análisis
                </button>
              </div>
            </div>
          </div>

          <!-- Statistics Card -->
          <div v-if="hasHistory" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              Estadísticas de Sesión
            </h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="text-center p-3 bg-green-50 rounded-lg">
                <div class="text-2xl font-bold text-green-600">{{ quickStats.total }}</div>
                <div class="text-sm text-green-700">Total de análisis</div>
              </div>
              <div class="text-center p-3 bg-blue-50 rounded-lg">
                <div class="text-2xl font-bold text-blue-600">{{ quickStats.highConfidenceCount }}</div>
                <div class="text-sm text-blue-700">Alta confianza</div>
              </div>
              <div class="text-center p-3 bg-purple-50 rounded-lg">
                <div class="text-2xl font-bold text-purple-600">{{ quickStats.avgWeight }}g</div>
                <div class="text-sm text-purple-700">Peso promedio</div>
              </div>
              <div class="text-center p-3 bg-orange-50 rounded-lg">
                <div class="text-2xl font-bold text-orange-600">{{ quickStats.avgConfidence }}%</div>
                <div class="text-sm text-orange-700">Confianza promedio</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <Transition name="slide-up">
      <div 
        v-if="showSuccessMessage" 
        class="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50"
      >
        <div class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {{ successMessage }}
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { usePredictionStore } from '@/stores/prediction.js';
import ImageUpload from '@/components/user/ImageUpload.vue';
import PredictionResults from '@/components/user/PredictionResults.vue';
import PredictionMethodSelector from '@/components/analysis/PredictionMethodSelector.vue';
import YoloResultsCard from '@/components/analysis/YoloResultsCard.vue';

export default {
  name: 'UserPrediction',
  components: {
    ImageUpload,
    PredictionResults,
    PredictionMethodSelector,
    YoloResultsCard
  },
  
  setup() {
    // Store
    const predictionStore = usePredictionStore();
    
    // Local reactive state
    const showSuccessMessage = ref(false);
    const successMessage = ref('');
    const selectedMethod = ref('traditional');
    const currentImageUrl = ref(null);
    
    // Computed properties from store
    const currentPrediction = computed(() => predictionStore.currentPrediction);
    const hasPrediction = computed(() => predictionStore.hasPrediction);
    const hasHistory = computed(() => predictionStore.hasHistory);
    const recentPredictions = computed(() => predictionStore.recentPredictions);
    const predictions = computed(() => predictionStore.predictions);
    const isLoading = computed(() => predictionStore.isLoading);
    const error = computed(() => predictionStore.error);
    const quickStats = computed(() => predictionStore.quickStats);
    
    // Event handlers
    const handlePredictionResult = async (result) => {
      try {
        // Update store with result (prediction is already in store from makePrediction)
        predictionStore.updateResults(result);
        
        // Show success message
        showSuccess('¡Análisis completado exitosamente!');
        
        console.log('Predicción guardada en store:', result);
        
      } catch (error) {
        console.error('Error manejando resultado:', error);
        predictionStore.setError('Error al procesar el resultado de la predicción');
      }
    };
    
    const handlePredictionError = (error) => {
      console.error('Error en predicción:', error);
      predictionStore.setError(error.message || 'Error desconocido en la predicción');
    };
    
    // Función para determinar si es un método YOLOv8
    const isYoloMethod = (prediction) => {
      if (!prediction) return false;
      return prediction.method === 'yolo_v8' || 
             prediction.method === 'yolo_v8_smart_crop' ||
             prediction.model_version === 'yolo_v8_smart_crop';
    };
    
    // Función para iniciar nuevo análisis
    const startNewAnalysis = () => {
      predictionStore.clearCurrentPrediction();
      currentImageUrl.value = null;
      showSuccess('Listo para nuevo análisis');
    };
    
    const handleNewAnalysis = () => {
      predictionStore.clearCurrentPrediction();
      showSuccess('Listo para nuevo análisis');
    };
    
    const handleSaveAnalysis = () => {
      // Esta funcionalidad se podría extender para guardar en una base de datos
      showSuccess('Análisis guardado en el historial');
    };
    
    // History management
    const selectFromHistory = (predictionId) => {
      predictionStore.selectPrediction(predictionId);
      showSuccess('Análisis cargado del historial');
    };
    
    const loadLatestPrediction = () => {
      if (recentPredictions.value.length > 0) {
        predictionStore.selectPrediction(recentPredictions.value[0].id);
        showSuccess('Último análisis cargado');
      }
    };
    
    const loadMoreHistory = async () => {
      try {
        const nextPage = predictionStore.pagination.currentPage + 1;
        await predictionStore.loadHistory(nextPage);
      } catch (error) {
        console.warn('Error cargando más historial:', error);
      }
    };
    
    // Utility functions
    const showSuccess = (message) => {
      successMessage.value = message;
      showSuccessMessage.value = true;
      
      setTimeout(() => {
        showSuccessMessage.value = false;
      }, 3000);
    };
    
    const clearError = () => {
      predictionStore.clearError();
    };
    
    // Formatting functions
    const formatDimensions = (prediction) => {
      const width = parseFloat(prediction.width).toFixed(1);
      const height = parseFloat(prediction.height).toFixed(1);
      const thickness = parseFloat(prediction.thickness).toFixed(1);
      return `${width} × ${height} × ${thickness} mm`;
    };
    
    const formatWeight = (weight) => {
      return `${parseFloat(weight).toFixed(2)}g`;
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
    
    const getConfidenceColor = (level) => {
      const colors = {
        'very_high': 'bg-green-500',
        'high': 'bg-green-400',
        'medium': 'bg-yellow-400',
        'low': 'bg-orange-400',
        'very_low': 'bg-red-400',
        'unknown': 'bg-gray-400'
      };
      return colors[level] || 'bg-gray-400';
    };
    
    const getConfidenceLabel = (level) => {
      const labels = {
        'very_high': 'Muy Alta',
        'high': 'Alta',
        'medium': 'Media',
        'low': 'Baja',
        'very_low': 'Muy Baja',
        'unknown': 'Desconocida'
      };
      return labels[level] || 'Desconocida';
    };
    
    // Auto-save scroll position
    let scrollPosition = 0;
    
    const saveScrollPosition = () => {
      scrollPosition = window.pageYOffset;
    };
    
    const restoreScrollPosition = () => {
      window.scrollTo(0, scrollPosition);
    };
    
    // Lifecycle
    onMounted(async () => {
      // Initialize store
      await predictionStore.initialize();
      
      // Add scroll listener
      window.addEventListener('scroll', saveScrollPosition);
      
      // Restore scroll position if returning to page
      setTimeout(restoreScrollPosition, 100);
    });
    
    onUnmounted(() => {
      window.removeEventListener('scroll', saveScrollPosition);
    });
    
    return {
      // Store state
      currentPrediction,
      hasPrediction,
      hasHistory,
      recentPredictions,
      predictions,
      isLoading,
      error,
      quickStats,
      
      // Local state
      showSuccessMessage,
      successMessage,
      selectedMethod,
      currentImageUrl,
      
      // Event handlers
      handlePredictionResult,
      handlePredictionError,
      handleNewAnalysis,
      handleSaveAnalysis,
      selectFromHistory,
      loadMoreHistory,
      clearError,
      showSuccess,
      
      // YOLOv8 specific functions
      isYoloMethod,
      startNewAnalysis,
      loadLatestPrediction,
      loadMoreHistory,
      
      // Utility functions
      clearError,
      formatDimensions,
      formatWeight,
      formatRelativeTime,
      getConfidenceColor,
      getConfidenceLabel
    };
  }
};
</script>

<style scoped>
/* Transiciones */
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

/* Animaciones de carga */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Efectos hover mejorados */
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
}

/* Grid responsive mejorado */
@media (max-width: 1280px) {
  .grid.xl\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

/* Scroll suave para navegación */
html {
  scroll-behavior: smooth;
}

/* Focus states mejorados */
.focus-visible:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Loading skeleton animations */
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Custom scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
