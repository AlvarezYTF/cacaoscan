<template>
  <BaseDetailView
    :loading="loading"
    :error="error"
    :title="imageData?.file_name || `Análisis #${imageId || 'Cargando...'}`"
    :subtitle="loteData ? `Lote: ${loteData.identificador || 'N/A'}` : (imageData?.lote ? `Lote ID: ${imageData.lote}` : '')"
    :icon="'fas fa-microscope'"
    :breadcrumbs="breadcrumbs"
    :statistics="statistics"
    loading-text="Cargando información del análisis..."
    @retry="loadImageData"
  >
    <template #main>
      <!-- Información del Análisis -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-info-circle me-2"></i>
            Información General
          </h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <h6 class="text-muted">ID de Imagen</h6>
              <p class="mb-3">
                <i class="fas fa-hashtag me-2"></i>
                {{ imageData?.id || 'N/A' }}
              </p>
              
              <h6 class="text-muted">Fecha de Análisis</h6>
              <p class="mb-3">
                <i class="fas fa-calendar me-2"></i>
                {{ formatDate(imageData?.created_at) }}
              </p>
              
              <h6 class="text-muted">Lote</h6>
              <p class="mb-3">
                <i class="fas fa-seedling me-2"></i>
                <router-link 
                  v-if="loteData?.id" 
                  :to="`/lotes/${loteData.id}`" 
                  class="text-decoration-none"
                >
                  {{ loteData.identificador || 'N/A' }}
                </router-link>
                <span v-else-if="imageData?.lote">{{ imageData.lote }}</span>
                <span v-else>N/A</span>
              </p>
            </div>
            <div class="col-md-6">
              <h6 class="text-muted">Finca</h6>
              <p class="mb-3">
                <i class="fas fa-map-marker-alt me-2"></i>
                <router-link 
                  v-if="fincaData?.id" 
                  :to="`/fincas/${fincaData.id}`" 
                  class="text-decoration-none"
                >
                  {{ fincaData.nombre || 'N/A' }}
                </router-link>
                <span v-else>N/A</span>
              </p>
              
              <h6 class="text-muted">Usuario</h6>
              <p class="mb-3">
                <i class="fas fa-user me-2"></i>
                {{ imageData?.user_name || imageData?.user || 'N/A' }}
              </p>
              
              <h6 class="text-muted">Estado</h6>
              <p class="mb-3">
                <span 
                  class="badge"
                  :class="imageData?.processed ? 'bg-success' : 'bg-warning'"
                >
                  {{ imageData?.processed ? 'Procesado' : 'Pendiente' }}
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Resultados de la Predicción -->
      <div v-if="predictionData" class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-chart-line me-2"></i>
            Resultados de la Predicción
          </h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <h6 class="text-muted">Dimensiones</h6>
              <div class="mb-3">
                <div class="d-flex justify-content-between mb-2">
                  <span>Alto:</span>
                  <strong>{{ (predictionData.alto_mm || 0).toFixed(2) }} mm</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span>Ancho:</span>
                  <strong>{{ (predictionData.ancho_mm || 0).toFixed(2) }} mm</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span>Grosor:</span>
                  <strong>{{ (predictionData.grosor_mm || 0).toFixed(2) }} mm</strong>
                </div>
                <div class="d-flex justify-content-between">
                  <span>Peso:</span>
                  <strong>{{ (predictionData.peso_g || 0).toFixed(2) }} g</strong>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <h6 class="text-muted">Niveles de Confianza</h6>
              <div class="mb-3">
                <div class="d-flex justify-content-between mb-2">
                  <span>Confianza Alto:</span>
                  <strong>{{ ((predictionData.confidence_alto || 0) * 100).toFixed(1) }}%</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span>Confianza Ancho:</span>
                  <strong>{{ ((predictionData.confidence_ancho || 0) * 100).toFixed(1) }}%</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span>Confianza Grosor:</span>
                  <strong>{{ ((predictionData.confidence_grosor || 0) * 100).toFixed(1) }}%</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span>Confianza Peso:</span>
                  <strong>{{ ((predictionData.confidence_peso || 0) * 100).toFixed(1) }}%</strong>
                </div>
                <div class="d-flex justify-content-between mt-3 pt-3 border-top">
                  <span><strong>Confianza Promedio:</strong></span>
                  <strong class="text-primary">{{ ((predictionData.average_confidence || 0) * 100).toFixed(1) }}%</strong>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="predictionData.crop_url" class="mt-4">
            <h6 class="text-muted mb-3">Imagen Procesada</h6>
            <img 
              :src="getImageUrl(predictionData.crop_url)" 
              alt="Imagen procesada"
              class="img-fluid rounded"
              style="max-height: 400px;"
              @error="handleImageError"
            />
          </div>
        </div>
      </div>

      <!-- Sin predicción -->
      <div v-else-if="imageData && !loading" class="card mb-4">
        <div class="card-body text-center py-5">
          <i class="fas fa-exclamation-triangle text-warning fa-3x mb-3"></i>
          <p class="text-muted">Esta imagen aún no ha sido procesada</p>
        </div>
      </div>
    </template>

    <template #sidebar>
      <!-- Información Técnica -->
      <div v-if="imageData" class="card mb-3">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="fas fa-cog me-2"></i>
            Información Técnica
          </h6>
        </div>
        <div class="card-body">
          <div class="mb-2">
            <small class="text-muted d-block">Tamaño del archivo</small>
            <strong>{{ formatFileSize(imageData.file_size) }}</strong>
          </div>
          <div class="mb-2">
            <small class="text-muted d-block">Tipo de archivo</small>
            <strong>{{ imageData.file_type || 'N/A' }}</strong>
          </div>
          <div v-if="predictionData?.processing_time_ms" class="mb-2">
            <small class="text-muted d-block">Tiempo de procesamiento</small>
            <strong>{{ (predictionData.processing_time_ms / 1000).toFixed(2) }}s</strong>
          </div>
          <div v-if="predictionData?.model_version" class="mb-2">
            <small class="text-muted d-block">Versión del modelo</small>
            <strong>{{ predictionData.model_version }}</strong>
          </div>
          <div v-if="predictionData?.device_used" class="mb-2">
            <small class="text-muted d-block">Dispositivo</small>
            <strong>{{ predictionData.device_used }}</strong>
          </div>
        </div>
      </div>

      <!-- Acciones Rápidas -->
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="fas fa-bolt me-2"></i>
            Acciones
          </h6>
        </div>
        <div class="card-body">
          <button 
            @click="goBack" 
            class="btn btn-outline-secondary btn-sm w-100 mb-2"
          >
            <i class="fas fa-arrow-left me-2"></i>
            Volver
          </button>
          <button 
            v-if="loteData?.id"
            @click="viewLote" 
            class="btn btn-outline-primary btn-sm w-100 mb-2"
          >
            <i class="fas fa-seedling me-2"></i>
            Ver Lote
          </button>
          <button 
            v-if="fincaData?.id"
            @click="viewFinca" 
            class="btn btn-outline-info btn-sm w-100"
          >
            <i class="fas fa-map-marker-alt me-2"></i>
            Ver Finca
          </button>
        </div>
      </div>
    </template>
  </BaseDetailView>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailView from '@/components/common/BaseDetailView.vue'
import { getImageDetails } from '@/services/predictionApi'
import api from '@/services/api'
import { useDateFormatting } from '@/composables/useDateFormatting'

const route = useRoute()
const router = useRouter()
const { formatDate } = useDateFormatting()

// Reactive data
const loading = ref(true)
const error = ref(null)
const imageData = ref(null)
const predictionData = ref(null)
const loteData = ref(null)
const fincaData = ref(null)

// Computed
const imageId = computed(() => route.params.id)

const breadcrumbs = computed(() => {
  const crumbs = [
    { label: 'Inicio', to: '/dashboard' },
    { label: 'Historial', to: '/historial' }
  ]
  
  if (fincaData.value?.id) {
    crumbs.push({ label: fincaData.value.nombre || 'Finca', to: `/fincas/${fincaData.value.id}` })
  }
  
  if (loteData.value?.id) {
    crumbs.push({ label: 'Lotes', to: fincaData.value?.id ? `/fincas/${fincaData.value.id}/lotes` : '/lotes' })
    crumbs.push({ label: loteData.value.identificador || 'Lote', to: `/lotes/${loteData.value.id}` })
  }
  
  crumbs.push({ label: `Análisis #${imageId.value || 'Cargando...'}`, to: null })
  
  return crumbs
})

const statistics = computed(() => {
  if (!predictionData.value) return []
  
  return [
    {
      label: 'Calidad',
      value: `${((predictionData.value.average_confidence || 0) * 100).toFixed(0)}%`,
      color: predictionData.value.average_confidence >= 0.8 ? 'success' : 
             predictionData.value.average_confidence >= 0.6 ? 'warning' : 'danger'
    },
    {
      label: 'Peso',
      value: `${(predictionData.value.peso_g || 0).toFixed(2)}g`,
      color: 'info'
    },
    {
      label: 'Tamaño',
      value: `${(predictionData.value.alto_mm || 0).toFixed(0)}mm`,
      color: 'primary'
    },
    {
      label: 'Procesado',
      value: imageData.value?.processed ? 'Sí' : 'No',
      color: imageData.value?.processed ? 'success' : 'warning'
    }
  ]
})

// Methods
const loadImageData = async () => {
  if (!imageId.value) {
    error.value = 'ID de análisis no proporcionado'
    loading.value = false
    return
  }
  
  try {
    loading.value = true
    error.value = null
    
    // Load image details
    const result = await getImageDetails(imageId.value)
    
    if (!result.success) {
      error.value = result.error || 'Error al cargar el análisis'
      loading.value = false
      return
    }
    
    imageData.value = result.data
    
    // Extract prediction data
    if (imageData.value.prediction) {
      predictionData.value = imageData.value.prediction
    }
    
    // Load lote data if available
    if (imageData.value.lote) {
      await loadLoteData(imageData.value.lote)
    }
    
  } catch (err) {
    console.error('Error loading image data:', err)
    error.value = err.response?.data?.error || err.message || 'Error al cargar el análisis'
  } finally {
    loading.value = false
  }
}

const loadLoteData = async (loteId) => {
  try {
    const response = await api.get(`/lotes/${loteId}/`)
    loteData.value = response.data
    
    // Load finca data if available
    if (loteData.value.finca) {
      await loadFincaData(loteData.value.finca)
    }
  } catch (err) {
    console.error('Error loading lote data:', err)
  }
}

const loadFincaData = async (fincaId) => {
  try {
    const response = await api.get(`/fincas/${fincaId}/`)
    fincaData.value = response.data
  } catch (err) {
    console.error('Error loading finca data:', err)
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'N/A'
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(2)} MB`
}

const getImageUrl = (url) => {
  if (!url) return null
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${apiBase}${url.startsWith('/') ? '' : '/'}${url}`
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
}

const goBack = () => {
  router.back()
}

const viewLote = () => {
  if (loteData.value?.id) {
    router.push(`/lotes/${loteData.value.id}`)
  }
}

const viewFinca = () => {
  if (fincaData.value?.id) {
    router.push(`/fincas/${fincaData.value.id}`)
  }
}

// Lifecycle
onMounted(() => {
  loadImageData()
})
</script>

<style scoped>
.card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
