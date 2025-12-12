<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 overflow-y-auto backdrop-blur-sm"
    aria-labelledby="modal-title"
    role="dialog"
    aria-modal="true"
    @click.self="close"
  >
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/30 backdrop-blur-sm transition-opacity" @click="close"></div>

    <!-- Modal -->
    <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
      <div
        class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-6xl"
        @click.stop
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100 sm:mx-0 sm:h-10 sm:w-10">
                <i class="fas fa-microscope text-green-600 text-xl"></i>
              </div>
              <div class="ml-4">
                <h3 class="text-lg font-medium leading-6 text-gray-900" id="modal-title">
                  Resultados del Análisis
                </h3>
                <p class="text-sm text-gray-500 mt-1">
                  <span v-if="analysisResult?.lote_name">{{ analysisResult.lote_name }}</span>
                  <span v-else-if="loading">Cargando...</span>
                </p>
              </div>
            </div>
            <button
              type="button"
              class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              @click="close"
            >
              <span class="sr-only">Cerrar</span>
              <i class="fas fa-times text-xl"></i>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 max-h-[80vh] overflow-y-auto">
          <!-- Results -->
          <div v-if="analysisResult" class="space-y-6">
            <!-- Información del Análisis -->
            <div class="bg-gray-50 rounded-xl p-4 border border-gray-200">
              <h4 class="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-3">Información del Análisis</h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p class="text-xs text-gray-500 mb-1">Lote</p>
                  <p class="text-sm font-medium text-gray-900">{{ analysisResult.lote_name || 'N/A' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500 mb-1">Imágenes Procesadas</p>
                  <p class="text-sm font-medium text-gray-900">{{ analysisResult.processed_images || 0 }}/{{ analysisResult.total_images || 0 }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500 mb-1">Confianza Promedio</p>
                  <p class="text-sm font-medium text-gray-900">{{ ((analysisResult.average_confidence || 0) * 100).toFixed(1) }}%</p>
                </div>
                <div v-if="analysisResult.processing_time_seconds">
                  <p class="text-xs text-gray-500 mb-1">Tiempo</p>
                  <p class="text-sm font-medium text-gray-900">{{ analysisResult.processing_time_seconds }}s</p>
                </div>
              </div>
            </div>

            <!-- Estadísticas Resumidas -->
            <div v-if="analysisResult.average_dimensions || analysisResult.total_weight" class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div v-if="analysisResult.average_dimensions?.alto" class="bg-blue-50 rounded-xl p-4 border border-blue-200 text-center">
                <div class="text-2xl font-bold text-blue-600 mb-1">{{ (analysisResult.average_dimensions.alto || 0).toFixed(2) }}mm</div>
                <div class="text-xs font-semibold text-gray-600 uppercase">Alto Promedio</div>
              </div>
              <div v-if="analysisResult.average_dimensions?.ancho" class="bg-green-50 rounded-xl p-4 border border-green-200 text-center">
                <div class="text-2xl font-bold text-green-600 mb-1">{{ (analysisResult.average_dimensions.ancho || 0).toFixed(2) }}mm</div>
                <div class="text-xs font-semibold text-gray-600 uppercase">Ancho Promedio</div>
              </div>
              <div v-if="analysisResult.average_dimensions?.grosor" class="bg-yellow-50 rounded-xl p-4 border border-yellow-200 text-center">
                <div class="text-2xl font-bold text-yellow-600 mb-1">{{ (analysisResult.average_dimensions.grosor || 0).toFixed(2) }}mm</div>
                <div class="text-xs font-semibold text-gray-600 uppercase">Grosor Promedio</div>
              </div>
              <div v-if="analysisResult.total_weight" class="bg-purple-50 rounded-xl p-4 border border-purple-200 text-center">
                <div class="text-2xl font-bold text-purple-600 mb-1">{{ (analysisResult.total_weight || 0).toFixed(2) }}g</div>
                <div class="text-xs font-semibold text-gray-600 uppercase">Peso Total</div>
              </div>
            </div>

            <!-- Imágenes Procesadas -->
            <div v-if="analysisResult.predictions && analysisResult.predictions.length > 0">
              <h4 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <i class="fas fa-images text-green-600"></i>
                Imágenes Procesadas ({{ analysisResult.processed_images || analysisResult.predictions.length }})
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <template
                  v-for="(prediction, index) in analysisResult.predictions"
                  :key="index"
                >
                  <div
                    v-if="prediction && prediction.success !== false && !prediction.error"
                    class="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-200"
                  >
                  <!-- Imagen -->
                  <div class="position-relative" style="height: 200px; overflow: hidden; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
                    <img
                      v-if="getImageUrl(prediction)"
                      :src="getImageUrl(prediction)"
                      :alt="`Imagen ${index + 1}`"
                      class="w-full h-full object-cover"
                      @error="handleImageError"
                    />
                    <div v-else class="flex flex-col items-center justify-center h-full text-gray-400">
                      <i class="fas fa-image fa-3x mb-2 opacity-50"></i>
                      <small>Sin imagen</small>
                    </div>
                    <!-- Badge de calidad -->
                    <div class="absolute top-2 right-2">
                      <span
                        class="badge shadow-sm text-xs px-2 py-1 bg-success"
                        v-if="prediction.prediction?.average_confidence || prediction.average_confidence"
                      >
                        <i class="fas fa-star me-1"></i>
                        {{ (((prediction.prediction?.average_confidence || prediction.average_confidence || 0)) * 100).toFixed(0) }}%
                      </span>
                    </div>
                  </div>

                  <!-- Datos del análisis -->
                  <div class="p-4">
                    <div class="flex justify-between items-center mb-3 pb-2 border-b">
                      <span class="text-xs text-gray-500">Imagen #{{ index + 1 }}</span>
                      <span v-if="prediction.model_version" class="text-xs text-gray-500">v{{ prediction.model_version }}</span>
                    </div>

                    <!-- Dimensiones -->
                    <div v-if="prediction.prediction || prediction.alto_mm" class="space-y-2">
                      <div class="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span class="text-gray-500">Alto:</span>
                          <span class="font-semibold ml-1">
                            {{ ((prediction.prediction?.alto_mm || prediction.alto_mm || 0)).toFixed(2) }} mm
                          </span>
                        </div>
                        <div>
                          <span class="text-gray-500">Ancho:</span>
                          <span class="font-semibold ml-1">
                            {{ ((prediction.prediction?.ancho_mm || prediction.ancho_mm || 0)).toFixed(2) }} mm
                          </span>
                        </div>
                        <div>
                          <span class="text-gray-500">Grosor:</span>
                          <span class="font-semibold ml-1">
                            {{ ((prediction.prediction?.grosor_mm || prediction.grosor_mm || 0)).toFixed(2) }} mm
                          </span>
                        </div>
                        <div>
                          <span class="text-gray-500">Peso:</span>
                          <span class="font-semibold ml-1">
                            {{ ((prediction.prediction?.peso_g || prediction.peso_g || 0)).toFixed(2) }} g
                          </span>
                        </div>
                      </div>

                      <!-- Confianza -->
                      <div v-if="prediction.prediction?.average_confidence || prediction.average_confidence" class="mt-3 pt-2 border-t">
                        <div class="flex justify-between items-center mb-1">
                          <span class="text-xs text-gray-500">Confianza</span>
                          <span class="text-xs font-semibold">
                            {{ (((prediction.prediction?.average_confidence || prediction.average_confidence || 0)) * 100).toFixed(1) }}%
                          </span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-1.5">
                          <div
                            class="h-1.5 rounded-full"
                            :class="{
                              'bg-success': (prediction.prediction?.average_confidence || prediction.average_confidence || 0) >= 0.8,
                              'bg-warning': (prediction.prediction?.average_confidence || prediction.average_confidence || 0) >= 0.6 && (prediction.prediction?.average_confidence || prediction.average_confidence || 0) < 0.8,
                              'bg-danger': (prediction.prediction?.average_confidence || prediction.average_confidence || 0) < 0.6
                            }"
                            :style="{ width: `${((prediction.prediction?.average_confidence || prediction.average_confidence || 0) * 100)}%` }"
                          ></div>
                        </div>
                      </div>
                    </div>

                    <!-- Sin predicción o error -->
                    <div v-else class="text-center py-2">
                      <i class="fas fa-exclamation-triangle text-warning text-xs mb-1"></i>
                      <p class="text-xs text-gray-500">{{ prediction.error || 'Sin datos de predicción' }}</p>
                    </div>
                  </div>
                  </div>
                </template>
              </div>
            </div>

            <!-- Sin análisis -->
            <div v-else class="text-center py-12">
              <i class="fas fa-microscope fa-4x text-gray-300 mb-4"></i>
              <h5 class="text-gray-600 mb-2">No hay imágenes procesadas</h5>
              <p class="text-gray-500 text-sm">No se encontraron resultados de análisis</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 border-t border-gray-200">
          <button
            type="button"
            class="inline-flex w-full justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500 sm:ml-3 sm:w-auto"
            @click="close"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '@/services/api'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  analysisResult: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const loading = ref(false)
const error = ref(null)

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
  const parent = event.target.parentElement
  if (parent) {
    parent.innerHTML = '<div class="flex flex-col items-center justify-center h-full text-gray-400"><i class="fas fa-image fa-3x mb-2 opacity-50"></i><small>Sin imagen</small></div>'
  }
}

const getImageUrl = (prediction) => {
  if (!prediction) return null
  
  // Helper to build absolute URL if needed
  const buildUrl = (url) => {
    if (!url) return null
    // If it's already an absolute URL (starts with http:// or https://), return as is
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url
    }
    // If it's a relative URL, make it absolute using the API base URL
    if (url.startsWith('/')) {
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      return `${apiBase}${url}`
    }
    // If it doesn't start with /, assume it's relative to media root
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    return `${apiBase}${url.startsWith('/') ? '' : '/'}${url}`
  }
  
  // Try crop_url first (processed image)
  const cropUrl = prediction.crop_url || prediction.prediction?.crop_url
  if (cropUrl) {
    return buildUrl(cropUrl)
  }
  
  // Try image_url (original image)
  const imageUrl = prediction.image_url || prediction.prediction?.image_url
  if (imageUrl) {
    return buildUrl(imageUrl)
  }
  
  // Try image_id to construct URL
  if (prediction.image_id) {
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    return `${apiBase}/api/v1/images/${prediction.image_id}/`
  }
  
  return null
}

// No need to load data, it's passed as prop
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
}
</style>

