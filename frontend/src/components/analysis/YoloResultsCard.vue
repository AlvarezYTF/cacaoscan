<template>
  <div class="max-w-5xl mx-auto">
    <!-- Header con método de predicción -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <div class="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900">
            {{ getMethodTitle() }}
          </h3>
          <p class="text-sm text-gray-500">
            Análisis con {{ getMethodDescription() }}
          </p>
        </div>
      </div>
      
      <!-- Indicador de confianza -->
      <div class="flex items-center space-x-2">
        <div class="text-right">
          <div class="text-sm font-medium text-gray-900">
            Confianza: {{ formatConfidence(result.nivel_confianza) }}%
          </div>
          <div class="w-20 bg-gray-200 rounded-full h-2">
            <div 
              class="h-2 rounded-full transition-all duration-300"
              :class="getConfidenceColor(result.nivel_confianza)"
              :style="{ width: `${result.nivel_confianza * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Grid de resultados -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Columna izquierda: Métricas principales -->
      <div class="space-y-4">
        <!-- Peso estimado -->
        <div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-sm font-medium text-green-800 mb-1">Peso Estimado</h4>
              <div class="text-3xl font-bold text-green-900">
                {{ result.peso_estimado }}g
              </div>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0 2l3 9m-3-9l-3 9"></path>
              </svg>
            </div>
          </div>
        </div>

        <!-- Dimensiones -->
        <div class="bg-white border border-gray-200 rounded-xl p-6">
          <h4 class="text-sm font-medium text-gray-900 mb-4">Dimensiones Físicas</h4>
          <div class="grid grid-cols-3 gap-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ result.altura_mm }}</div>
              <div class="text-xs text-gray-500 uppercase tracking-wide">Altura (mm)</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ result.ancho_mm }}</div>
              <div class="text-xs text-gray-500 uppercase tracking-wide">Ancho (mm)</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-orange-600">{{ result.grosor_mm }}</div>
              <div class="text-xs text-gray-500 uppercase tracking-wide">Grosor (mm)</div>
            </div>
          </div>
        </div>

        <!-- Información de detección -->
        <div class="bg-gray-50 border border-gray-200 rounded-xl p-6">
          <h4 class="text-sm font-medium text-gray-900 mb-3">Información de Detección</h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Método:</span>
              <span class="font-medium">{{ result.method || 'YOLOv8' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Tiempo de procesamiento:</span>
              <span class="font-medium">{{ formatProcessingTime(result.processing_time) }}</span>
            </div>
            <div v-if="result.detection_info" class="flex justify-between">
              <span class="text-gray-600">Bounding box:</span>
              <span class="font-medium text-xs">{{ formatBbox(result.detection_info.bbox_pixels) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Columna derecha: Imágenes procesadas -->
      <div class="space-y-4">
        <!-- Imagen original -->
        <div v-if="originalImage" class="bg-white border border-gray-200 rounded-xl p-4">
          <h4 class="text-sm font-medium text-gray-900 mb-3">Imagen Original</h4>
          <div class="relative">
            <img 
              :src="originalImage" 
              :alt="`Imagen original del grano ${result.id || ''}`"
              class="w-full h-48 object-cover rounded-lg"
            />
            <div v-if="result.detection_info?.bbox_pixels" class="absolute inset-0">
              <div 
                class="absolute border-2 border-blue-500 rounded"
                :style="getBboxStyle(result.detection_info.bbox_pixels)"
              ></div>
            </div>
          </div>
        </div>

        <!-- Imagen recortada -->
        <div v-if="result.cropped_image" class="bg-white border border-gray-200 rounded-xl p-4">
          <h4 class="text-sm font-medium text-gray-900 mb-3">Recorte Inteligente</h4>
          <img 
            :src="result.cropped_image" 
            alt="Grano recortado"
            class="w-full h-32 object-contain rounded-lg bg-gray-50"
          />
        </div>

        <!-- Imagen transparente -->
        <div v-if="result.transparent_image" class="bg-white border border-gray-200 rounded-xl p-4">
          <h4 class="text-sm font-medium text-gray-900 mb-3">Fondo Transparente</h4>
          <div class="relative h-32 bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg overflow-hidden">
            <img 
              :src="result.transparent_image" 
              alt="Grano con fondo transparente"
              class="absolute inset-0 w-full h-full object-contain"
            />
          </div>
        </div>

        <!-- Métricas de calidad del recorte -->
        <div v-if="result.smart_crop?.quality_metrics" class="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <h4 class="text-sm font-medium text-blue-900 mb-3">Calidad del Recorte</h4>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-blue-700">Score de calidad:</span>
              <span class="font-medium text-blue-900">{{ formatQuality(result.smart_crop.quality_metrics.quality_score) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-blue-700">Proporción de área:</span>
              <span class="font-medium text-blue-900">{{ formatPercentage(result.smart_crop.quality_metrics.area_ratio) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-blue-700">Compacidad:</span>
              <span class="font-medium text-blue-900">{{ formatCompactness(result.smart_crop.quality_metrics.compactness) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Acciones -->
    <div class="mt-6 flex justify-end space-x-3">
      <button 
        v-if="result.cropped_image || result.transparent_image"
        @click="downloadProcessedImages"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        Descargar Imágenes
      </button>
      <button 
        @click="$emit('new-analysis')"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        Nuevo Análisis
      </button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'YoloResultsCard',
  props: {
    result: {
      type: Object,
      required: true
    },
    originalImage: {
      type: String,
      default: null
    }
  },
  emits: ['new-analysis'],
  setup(props) {
    // Computed properties
    const getMethodTitle = () => {
      if (props.result.method === 'yolo_v8_smart_crop') {
        return 'Análisis con Recorte Inteligente'
      } else if (props.result.method === 'yolo_v8') {
        return 'Análisis YOLOv8'
      }
      return 'Análisis de Grano'
    }

    const getMethodDescription = () => {
      if (props.result.method === 'yolo_v8_smart_crop') {
        return 'YOLOv8 + Segmentación Avanzada'
      } else if (props.result.method === 'yolo_v8') {
        return 'Detección de Objetos YOLOv8'
      }
      return 'Visión por Computadora'
    }

    const getConfidenceColor = (confidence) => {
      if (confidence >= 0.8) return 'bg-green-500'
      if (confidence >= 0.6) return 'bg-yellow-500'
      return 'bg-red-500'
    }

    const formatConfidence = (confidence) => {
      return Math.round(confidence * 100)
    }

    const formatProcessingTime = (time) => {
      if (!time) return 'N/A'
      return `${(time * 1000).toFixed(0)}ms`
    }

    const formatBbox = (bbox) => {
      if (!bbox || !Array.isArray(bbox)) return 'N/A'
      return `[${bbox.map(Math.round).join(', ')}]`
    }

    const formatQuality = (score) => {
      if (!score) return 'N/A'
      return `${(score * 100).toFixed(1)}%`
    }

    const formatPercentage = (ratio) => {
      if (!ratio) return 'N/A'
      return `${(ratio * 100).toFixed(1)}%`
    }

    const formatCompactness = (compactness) => {
      if (!compactness) return 'N/A'
      return compactness.toFixed(2)
    }

    const getBboxStyle = (bbox) => {
      if (!bbox || !Array.isArray(bbox) || bbox.length !== 4) return {}
      
      const [x1, y1, x2, y2] = bbox
      return {
        left: `${x1}px`,
        top: `${y1}px`,
        width: `${x2 - x1}px`,
        height: `${y2 - y1}px`
      }
    }

    const downloadProcessedImages = () => {
      const images = []
      
      if (props.result.cropped_image) {
        images.push({
          name: 'grano_recortado.png',
          data: props.result.cropped_image
        })
      }
      
      if (props.result.transparent_image) {
        images.push({
          name: 'grano_transparente.png',
          data: props.result.transparent_image
        })
      }

      images.forEach(image => {
        const link = document.createElement('a')
        link.href = image.data
        link.download = image.name
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      })
    }

    return {
      getMethodTitle,
      getMethodDescription,
      getConfidenceColor,
      formatConfidence,
      formatProcessingTime,
      formatBbox,
      formatQuality,
      formatPercentage,
      formatCompactness,
      getBboxStyle,
      downloadProcessedImages
    }
  }
}
</script>

<style scoped>

/* Animaciones suaves */
.transition-all {
  transition: all 0.3s ease;
}

/* Hover effects */
.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}

.hover\:bg-blue-700:hover {
  background-color: #1d4ed8;
}

/* Focus states */
.focus\:outline-none:focus {
  outline: none;
}

.focus\:ring-2:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.focus\:ring-blue-500:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}
</style>
