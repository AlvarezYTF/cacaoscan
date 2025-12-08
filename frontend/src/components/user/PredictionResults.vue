<template>
  <div v-if="predictionData" class="bg-white rounded-lg shadow-md p-6">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <h3 class="text-xl font-bold text-gray-800">
          Resultados del Análisis
        </h3>
        <div class="flex items-center space-x-2">
          <!-- Indicador de confianza -->
          <div class="flex items-center">
            <div 
              class="w-3 h-3 rounded-full mr-2"
              :class="confidenceColorClass"
            ></div>
            <span class="text-sm font-medium" :class="confidenceTextClass">
              {{ confidenceLabel }}
            </span>
          </div>
          
          <!-- Botón de nuevo análisis -->
          <button
            @click="$emit('new-analysis')"
            class="text-sm text-green-600 hover:text-green-700 underline focus:outline-none"
          >
            Nuevo análisis
          </button>
        </div>
      </div>
      
      <!-- Información básica -->
      <div class="text-sm text-gray-600">
        <span>ID: #{{ predictionData.id }}</span>
        <span class="mx-2">•</span>
        <span>{{ formatDate(predictionData.created_at) }}</span>
        <span v-if="predictionData.processing_time" class="mx-2">•</span>
        <span v-if="predictionData.processing_time">
          Procesado en {{ predictionData.processing_time }}s
        </span>
      </div>
    </div>

    <!-- Imagen y resultados principales -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Imagen analizada -->
      <div class="space-y-4">
        <h4 class="font-semibold text-gray-700">Imagen Analizada</h4>
        <div class="relative">
          <img 
            v-if="predictionData.image_url"
            :src="predictionData.image_url" 
            :alt="`Grano de cacao #${predictionData.id}`"
            class="w-full h-64 object-cover rounded-lg border border-gray-200"
            @error="onImageError"
          />
          <div 
            v-else 
            class="w-full h-64 bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center"
          >
            <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          
          <!-- Overlay con información rápida -->
          <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent rounded-b-lg p-3">
            <div class="text-white text-sm">
              <div class="font-medium">{{ formatDimensions() }}</div>
              <div class="opacity-90">Peso: {{ formatWeight() }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Características físicas -->
      <div class="space-y-4">
        <h4 class="font-semibold text-gray-700">Características Físicas</h4>
        <div class="grid grid-cols-2 gap-4">
          <!-- Ancho -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-600">Ancho</span>
              <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
            </div>
            <div class="text-2xl font-bold text-gray-800">
              {{ formatNumber(predictionData.width) }}
              <span class="text-sm font-normal text-gray-500">mm</span>
            </div>
          </div>

          <!-- Alto -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-600">Alto</span>
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
              </svg>
            </div>
            <div class="text-2xl font-bold text-gray-800">
              {{ formatNumber(predictionData.height) }}
              <span class="text-sm font-normal text-gray-500">mm</span>
            </div>
          </div>

          <!-- Grosor -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-600">Grosor</span>
              <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="text-2xl font-bold text-gray-800">
              {{ formatNumber(predictionData.thickness) }}
              <span class="text-sm font-normal text-gray-500">mm</span>
            </div>
          </div>

          <!-- Peso -->
          <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-green-700">Peso Predicho</span>
              <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16l6-2m-6 2l-6-2" />
              </svg>
            </div>
            <div class="text-2xl font-bold text-green-800">
              {{ formatNumber(predictionData.predicted_weight) }}
              <span class="text-sm font-normal text-green-600">g</span>
            </div>
            <div v-if="predictionData.prediction_method" class="text-xs text-green-600 mt-1">
              Método: {{ formatPredictionMethod(predictionData.prediction_method) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Información de confianza y calidad -->
    <div class="bg-gray-50 rounded-lg p-4 mb-6">
      <h4 class="font-semibold text-gray-700 mb-3">Información de Confianza</h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Nivel de confianza -->
        <div class="text-center">
          <div class="text-sm text-gray-600 mb-1">Nivel de Confianza</div>
          <div class="text-lg font-semibold" :class="confidenceTextClass">
            {{ confidenceLabel }}
          </div>
          <div v-if="predictionData.confidence_score" class="text-sm text-gray-500">
            {{ Math.round(predictionData.confidence_score * 100) }}%
          </div>
        </div>

        <!-- Barra de confianza -->
        <div class="flex items-center">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div 
              class="h-2 rounded-full transition-all duration-500"
              :class="confidenceBarClass"
              :style="{ width: `${(predictionData.confidence_score || 0) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Recomendación -->
        <div class="text-center">
          <div class="text-sm text-gray-600 mb-1">Recomendación</div>
          <div class="text-xs" :class="confidenceTextClass">
            {{ getConfidenceRecommendation() }}
          </div>
        </div>
      </div>
    </div>

    <!-- Métricas derivadas (si están disponibles) -->
    <div 
      v-if="predictionData.derived_metrics" 
      class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6"
    >
      <div 
        v-if="predictionData.derived_metrics.volume_mm3"
        class="bg-blue-50 rounded-lg p-3 text-center"
      >
        <div class="text-xs text-blue-600 mb-1">Volumen</div>
        <div class="text-sm font-semibold text-blue-800">
          {{ formatNumber(predictionData.derived_metrics.volume_mm3) }} mm³
        </div>
      </div>
      
      <div 
        v-if="predictionData.derived_metrics.density_g_per_cm3"
        class="bg-indigo-50 rounded-lg p-3 text-center"
      >
        <div class="text-xs text-indigo-600 mb-1">Densidad</div>
        <div class="text-sm font-semibold text-indigo-800">
          {{ formatNumber(predictionData.derived_metrics.density_g_per_cm3) }} g/cm³
        </div>
      </div>
      
      <div 
        v-if="predictionData.derived_metrics.aspect_ratio"
        class="bg-purple-50 rounded-lg p-3 text-center"
      >
        <div class="text-xs text-purple-600 mb-1">Proporción</div>
        <div class="text-sm font-semibold text-purple-800">
          {{ formatNumber(predictionData.derived_metrics.aspect_ratio) }}
        </div>
      </div>
      
      <div 
        v-if="predictionData.derived_metrics.projected_area_mm2"
        class="bg-pink-50 rounded-lg p-3 text-center"
      >
        <div class="text-xs text-pink-600 mb-1">Área</div>
        <div class="text-sm font-semibold text-pink-800">
          {{ formatNumber(predictionData.derived_metrics.projected_area_mm2) }} mm²
        </div>
      </div>
    </div>

    <!-- Comparación de métodos de predicción (si está disponible) -->
    <div 
      v-if="predictionData.weight_comparison" 
      class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6"
    >
      <h4 class="font-semibold text-yellow-800 mb-3 flex items-center">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 00-2-2z" />
        </svg>
        Comparación de Métodos
      </h4>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
        <div>
          <div class="text-yellow-700 font-medium">Visión CNN</div>
          <div class="text-yellow-800">{{ formatNumber(predictionData.weight_comparison.vision_weight) }}g</div>
        </div>
        <div>
          <div class="text-yellow-700 font-medium">Regresión</div>
          <div class="text-yellow-800">{{ formatNumber(predictionData.weight_comparison.regression_weight) }}g</div>
        </div>
        <div>
          <div class="text-yellow-700 font-medium">Diferencia</div>
          <div class="text-yellow-800">{{ formatNumber(predictionData.weight_comparison.difference) }}g</div>
        </div>
        <div>
          <div class="text-yellow-700 font-medium">Acuerdo</div>
          <div class="text-yellow-800 capitalize">{{ predictionData.weight_comparison.agreement_level }}</div>
        </div>
      </div>
    </div>

    <!-- Acciones -->
    <div class="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
      <button
        @click="downloadResults"
        class="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-4-4m4 4l4-4m-6 4h8" />
        </svg>
        Descargar Resultados
      </button>
      
      <button
        @click="shareResults"
        class="flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
        </svg>
        Compartir
      </button>
      
      <button
        @click="$emit('save-analysis')"
        class="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        Guardar Análisis
      </button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';

export default {
  name: 'PredictionResults',
  props: {
    predictionData: {
      type: Object,
      required: true,
      validator(value) {
        return value && 
               value.width !== undefined && 
               value.height !== undefined && 
               value.thickness !== undefined && 
               value.predicted_weight !== undefined;
      }
    }
  },
  emits: ['new-analysis', 'save-analysis'],
  
  setup(props) {
    // Computed properties para confianza
    const confidenceLevel = computed(() => {
      return props.predictionData.confidence_level || 'unknown';
    });
    
    const confidenceScore = computed(() => {
      return props.predictionData.confidence_score || 0;
    });
    
    const confidenceLabel = computed(() => {
      const labels = {
        'very_high': 'Muy Alta',
        'high': 'Alta',
        'medium': 'Media',
        'low': 'Baja',
        'very_low': 'Muy Baja',
        'unknown': 'Desconocida'
      };
      return labels[confidenceLevel.value] || 'Desconocida';
    });
    
    const confidenceColorClass = computed(() => {
      const classes = {
        'very_high': 'bg-green-500',
        'high': 'bg-green-400',
        'medium': 'bg-yellow-400',
        'low': 'bg-orange-400',
        'very_low': 'bg-red-400',
        'unknown': 'bg-gray-400'
      };
      return classes[confidenceLevel.value] || 'bg-gray-400';
    });
    
    const confidenceTextClass = computed(() => {
      const classes = {
        'very_high': 'text-green-700',
        'high': 'text-green-600',
        'medium': 'text-yellow-600',
        'low': 'text-orange-600',
        'very_low': 'text-red-600',
        'unknown': 'text-gray-600'
      };
      return classes[confidenceLevel.value] || 'text-gray-600';
    });
    
    const confidenceBarClass = computed(() => {
      const classes = {
        'very_high': 'bg-green-500',
        'high': 'bg-green-400',
        'medium': 'bg-yellow-400',
        'low': 'bg-orange-400',
        'very_low': 'bg-red-400',
        'unknown': 'bg-gray-400'
      };
      return classes[confidenceLevel.value] || 'bg-gray-400';
    });

    // Métodos de formateo
    const formatNumber = (value) => {
      if (value === null || value === undefined) return 'N/A';
      const num = Number.parseFloat(value);
      return Number.isNaN(num) ? 'N/A' : num.toFixed(2);
    };

    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    const formatDimensions = () => {
      return `${formatNumber(props.predictionData.width)} × ${formatNumber(props.predictionData.height)} × ${formatNumber(props.predictionData.thickness)} mm`;
    };

    const formatWeight = () => {
      return `${formatNumber(props.predictionData.predicted_weight)} g`;
    };

    const formatPredictionMethod = (method) => {
      const methods = {
        'vision_cnn': 'Visión CNN',
        'regression': 'Regresión',
        'fallback': 'Estimación',
        'unknown': 'Desconocido'
      };
      return methods[method] || method;
    };

    const getConfidenceRecommendation = () => {
      const recommendations = {
        'very_high': 'Excelente precisión',
        'high': 'Buena precisión',
        'medium': 'Precisión aceptable',
        'low': 'Verificar manualmente',
        'very_low': 'Revisar imagen',
        'unknown': 'Calidad desconocida'
      };
      return recommendations[confidenceLevel.value] || 'Revisar resultados';
    };

    // Métodos de acción
    const downloadResults = () => {
      const data = {
        id: props.predictionData.id,
        fecha: new Date().toISOString(),
        dimensiones: {
          ancho: formatNumber(props.predictionData.width) + ' mm',
          alto: formatNumber(props.predictionData.height) + ' mm',
          grosor: formatNumber(props.predictionData.thickness) + ' mm'
        },
        peso_predicho: formatNumber(props.predictionData.predicted_weight) + ' g',
        confianza: confidenceLabel.value,
        metodo: formatPredictionMethod(props.predictionData.prediction_method)
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analisis_cacao_${props.predictionData.id}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    };

    const shareResults = () => {
      if (navigator.share) {
        navigator.share({
          title: 'Análisis de Grano de Cacao',
          text: `Resultados: ${formatDimensions()}, Peso: ${formatWeight()}`,
          url: globalThis.location.href
        });
      } else {
        // Fallback: copiar al portapapeles
        const text = `Análisis de Grano de Cacao #${props.predictionData.id}\nDimensiones: ${formatDimensions()}\nPeso: ${formatWeight()}\nConfianza: ${confidenceLabel.value}`;
        navigator.clipboard.writeText(text).then(() => {
          alert('Resultados copiados al portapapeles');
        });
      }
    };

    const onImageError = (event) => {
      event.target.style.display = 'none';
    };

    return {
      // Computed
      confidenceLevel,
      confidenceScore,
      confidenceLabel,
      confidenceColorClass,
      confidenceTextClass,
      confidenceBarClass,
      
      // Métodos
      formatNumber,
      formatDate,
      formatDimensions,
      formatWeight,
      formatPredictionMethod,
      getConfidenceRecommendation,
      downloadResults,
      shareResults,
      onImageError
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

/* Efectos de hover */
.hover-scale:hover {
  transform: scale(1.05);
  transition: transform 0.2s ease;
}

/* Gradientes personalizados */
.gradient-confidence {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

/* Sombras personalizadas */
.shadow-soft {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.shadow-soft:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* Animación de la barra de progreso */
.progress-bar {
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}
</style>
